import os
import pandas as pd
import json
from utils.helpers import get_file_list, sanitize_filename
from core.api_client import DeepSeekAPI
from core.file_processors import (
    CsvFileProcessor, ExcelFileProcessor,
    JsonFileProcessor, TxtFileProcessor
)

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

        # 初始化文件处理器（核心扩展点：添加新类型只需在这里注册）
        self.file_processors = [
            CsvFileProcessor(),
            ExcelFileProcessor(),
            JsonFileProcessor(),
            TxtFileProcessor()
        ]

        # 构建扩展名到处理器的映射
        self.extension_map = {}
        for processor in self.file_processors:
            for ext in processor.get_supported_extensions():
                self.extension_map[ext.lower()] = processor

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
        """加载文件数据（支持多种类型）"""
        if self.current_data and set(file_names) == set(self.current_data.keys()):
            return self.current_data

        data_dict = {}
        for file_name in file_names:
            safe_file = sanitize_filename(file_name)
            full_path = os.path.join(self.data_dir, safe_file)

            if not os.path.exists(full_path):
                raise FileNotFoundError(f"文件不存在: {full_path}")

            # 获取文件扩展名
            _, ext = os.path.splitext(full_path)
            ext = ext.lower()

            # 检查是否支持该类型
            if ext not in self.extension_map:
                supported_exts = ", ".join(self.extension_map.keys())
                raise ValueError(
                    f"不支持的文件格式: {ext}。支持的格式: {supported_exts}"
                )

            # 使用对应的处理器读取文件
            try:
                processor = self.extension_map[ext]
                df = processor.read_file(
                    full_path,
                    encodings=self.supported_encodings
                )
                data_dict[safe_file] = df
                print(f"✅ 已读取文件: {safe_file}, 共 {len(df)} 行")
            except Exception as e:
                raise RuntimeError(f"读取文件 {safe_file} 失败: {str(e)}")

        self.current_data = data_dict
        return data_dict

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