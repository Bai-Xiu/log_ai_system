import os
import pandas as pd
import json
from utils.helpers import get_file_list, sanitize_filename
from core.api_client import DeepSeekAPI  # 引用统一的API客户端

class LogAIProcessor:
    def __init__(self, config):
        self.config = config
        self.api_key = config.get("api_key", "")
        self.data_dir = config.get("data_dir", "")
        self.save_dir = config.get("save_dir", "")
        self.verbose = config.get("verbose_logging", False)
        self.supported_encodings = ['utf-8', 'gbk', 'gb2312', 'ansi']

        # 初始化API客户端
        self.client = DeepSeekAPI(api_key=self.api_key) if self.api_key else None

        # 存储当前选择的文件和数据
        self.current_files = None
        self.current_data = None

    def set_data_dir(self, new_dir):
        """设置数据目录（完全由用户指定）"""
        if new_dir:
            self.data_dir = new_dir
            self.config.set("data_dir", new_dir)
            self.current_data = None  # 清除缓存数据

    def set_save_dir(self, new_dir):
        """设置保存目录（完全由用户指定）"""
        if new_dir:
            self.save_dir = new_dir
            self.config.set("save_dir", new_dir)

    def get_file_list(self):
        """获取用户指定目录中的文件列表"""
        if not self.data_dir or not os.path.exists(self.data_dir):
            return []
        return get_file_list(self.data_dir)

    def load_data_files(self, file_names):
        """加载用户指定目录中的文件"""
        if not self.data_dir or not os.path.exists(self.data_dir):
            raise ValueError("数据目录未设置或不存在")

        return self._load_file_data(file_names)

    def _load_file_data(self, file_names):
        """加载文件数据（使用用户指定的目录）"""
        if self.current_data and set(file_names) == set(self.current_data.keys()):
            return self.current_data

        data_dict = {}
        for file_name in file_names:
            safe_file = sanitize_filename(file_name)
            # 直接使用用户指定的目录
            full_path = os.path.join(self.data_dir, safe_file)

            if not os.path.exists(full_path):
                raise FileNotFoundError(f"文件不存在: {full_path}")

            if not full_path.lower().endswith('.csv'):
                raise ValueError(f"不支持的文件格式: {full_path}。请使用CSV文件。")

            df = self.read_file_with_encoding(full_path)
            data_dict[safe_file] = df
            print(f"✅ 已读取文件: {safe_file}, 共 {len(df)} 行")

        self.current_data = data_dict
        return data_dict

    def read_file_with_encoding(self, file_path, nrows=None):
        """读取CSV文件"""
        if os.path.getsize(file_path) == 0:
            raise ValueError(f"文件为空: {file_path}")

        # 尝试多种编码读取CSV
        for encoding in self.supported_encodings:
            try:
                kwargs = {
                    'encoding': encoding,
                    'sep': ',',
                    'engine': 'python'
                }
                if nrows:
                    kwargs['nrows'] = nrows

                df = pd.read_csv(file_path, **kwargs)
                return df
            except Exception as e:
                print(f"编码 {encoding} 读取失败: {str(e)}")
                continue

        # 最后尝试
        return pd.read_csv(
            file_path,
            encoding='utf-8',
            errors='replace',
            sep=',',
            engine='python'
        )

    def generate_processing_code(self, user_request, file_names):
        """生成处理代码"""
        if not self.client:
            return """def process_data(data_dict):
    import pandas as pd
    df = pd.concat(data_dict.values(), ignore_index=True)
    return {'result_table': df, 'summary': f'共{len(df)}条记录'}"""

        data_dict = self._load_file_data(file_names)

        # 准备文件元数据
        file_info = {}
        for filename, df in data_dict.items():
            file_info[filename] = {
                "columns": df.columns.tolist(),
                "sample": df.head(2).to_dict(orient='records')
            }

        prompt = f"""根据用户请求编写处理日志的Python函数:
用户需求: {user_request}
数据信息: {json.dumps(file_info, ensure_ascii=False)}

函数名必须是process_data，接收data_dict参数(文件名到DataFrame的字典)
返回格式: {{'result_table': DataFrame, 'summary': '总结文本'}}
只需返回函数代码，不要其他内容
"""

        response = self.client.completions_create(
            model='deepseek-reasoner',
            prompt=prompt,
            max_tokens=5000,
            temperature=0.4
        )

        code_block = response.choices[0].message.content.strip()

        if code_block.startswith('```'):
            code_block = '\n'.join(code_block.split('\n')[1:-1])

        return code_block

    def direct_answer(self, user_request, file_names):
        """直接回答模式"""
        if not self.client:
            return {"summary": "请设置有效的API密钥"}

        data_dict = self._load_file_data(file_names)

        stats = []
        for filename, df in data_dict.items():
            stats.append({
                "文件名": filename,
                "记录数": len(df),
                "列名": df.columns.tolist()
            })

        prompt = f"""基于以下统计信息回答问题:
统计: {json.dumps(stats, ensure_ascii=False)}
问题: {user_request}
用简洁的中文回答，不要使用Markdown。"""

        response = self.client.completions_create(
            model='deepseek-reasoner',
            prompt=prompt,
            max_tokens=5000,
            temperature=0.7
        )

        return {"summary": response.choices[0].message.content.strip()}