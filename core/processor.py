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
        if os.path.getsize(file_path) == 0:
            raise ValueError(f"文件为空: {file_path}")

        # 尝试多种编码读取CSV（只在所有编码失败时打印错误）
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
                # 仅在成功时打印编码信息（可选）
                # print(f"使用编码 {encoding} 成功读取文件: {file_path}")
                return df
            except Exception as e:
                # 移除单种编码失败的打印，只在全部失败时提示
                continue

        # 所有编码尝试失败时才报错
        raise ValueError(f"无法读取文件 {file_path}，尝试过编码: {self.supported_encodings}")

    def generate_processing_code(self, user_request, file_names):
        """生成完整可执行代码，而非函数内部逻辑"""
        if not self.client:
            # 默认代码：直接返回所有数据
            return """import pandas as pd
    result_table = pd.concat(data_dict.values(), ignore_index=True)
    summary = f'共{len(result_table)}条记录'"""

        data_dict = self._load_file_data(file_names)

        # 准备文件元数据
        file_info = {}
        for filename, df in data_dict.items():
            file_info[filename] = {
                "columns": df.columns.tolist(),
                "sample": df.head(2).to_dict(orient='records')
            }

        prompt = f"""根据用户请求编写完整的Python处理代码:
    用户需求: {user_request}
    数据信息: {json.dumps(file_info, ensure_ascii=False)}

    说明：
    1. 已存在变量data_dict（文件名到DataFrame的字典），可直接使用
    2. 必须导入所需的库（如pandas）
    3. 必须定义两个变量：
       - result_table：处理后的DataFrame结果（必须存在）
       - summary：字符串类型的总结，需包含关键分析结论（如统计数量、趋势、异常点等），禁止使用默认值，必须根据分析结果生成具体内容
    4. 不要包含任何函数定义，直接编写可执行代码
    5. 不需要return语句，只需确保定义了上述两个变量"""

        response = self.client.completions_create(
            model='deepseek-reasoner',
            prompt=prompt,
            max_tokens=5000,
            temperature=0.4
        )

        code_block = response.choices[0].message.content.strip()

        # 清理代码块中的反引号
        if code_block.startswith('```'):
            code_block = '\n'.join(code_block.split('\n')[1:-1])

        return code_block