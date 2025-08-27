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

        # 添加敏感词处理器
        from core.sensitive_processor import SensitiveWordProcessor
        self.sensitive_processor = SensitiveWordProcessor(config)

        # 区分默认目录和当前目录
        self.default_data_dir = config.get("data_dir", "")  # 持久化的默认目录
        self.current_data_dir = self.default_data_dir  # 当前工作目录（临时）

        self.default_save_dir = config.get("save_dir", "")  # 持久化的默认目录
        self.current_save_dir = self.default_save_dir  # 当前工作目录（临时）

        self.verbose = config.get("verbose_logging", False)
        self.supported_encodings = ['utf-8', 'gbk', 'gb2312', 'ansi', 'utf-16', 'utf-16-le']

        # 初始化API客户端，传入敏感词处理器
        self.client = DeepSeekAPI(api_key=self.api_key,
                                  sensitive_processor=self.sensitive_processor) if self.api_key else None

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

    def set_default_data_dir(self, new_dir):
        if new_dir:
            self.default_data_dir = new_dir
            self.config.set("data_dir", new_dir)

    def set_current_data_dir(self, new_dir):
        if new_dir:
            self.current_data_dir = new_dir

    def set_default_save_dir(self, new_dir):
        if new_dir:
            self.default_save_dir = new_dir
            self.config.set("save_dir", new_dir)

    def set_current_save_dir(self, new_dir):
        if new_dir:
            self.current_save_dir = new_dir

    def get_file_list(self):
        """获取当前数据目录中的文件列表"""
        if not self.current_data_dir or not os.path.exists(self.current_data_dir):
            return []
        return get_file_list(self.current_data_dir)

    def load_data_files(self, file_names):
        """从当前数据目录加载文件"""
        if not self.current_data_dir or not os.path.exists(self.current_data_dir):
            raise ValueError("当前数据目录未设置或不存在")

        return self._load_file_data(file_names)

    def _load_file_data(self, file_names):
        """从当前数据目录读取文件数据，使用多线程加载"""
        if self.current_data and set(file_names) == set(self.current_data.keys()):
            return self.current_data

        data_dict = {}
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def load_single_file(file_name):
            safe_file = sanitize_filename(file_name)
            full_path = os.path.join(self.current_data_dir, safe_file)

            if not os.path.exists(full_path):
                raise FileNotFoundError(f"文件不存在: {full_path}")

            _, ext = os.path.splitext(full_path)
            ext = ext.lower()

            if ext not in self.extension_map:
                supported_exts = ", ".join(self.extension_map.keys())
                raise ValueError(f"不支持的文件格式: {ext}。支持的格式: {supported_exts}")

            processor = self.extension_map[ext]
            df = processor.read_file(full_path, encodings=self.supported_encodings)

            # 加载后立即进行敏感词处理
            df_copy = df.copy()
            for col in df_copy.columns:
                if df_copy[col].dtype == 'object':
                    df_copy[col] = df_copy[col].astype(str).apply(
                        lambda x: self.sensitive_processor.normalize_to_replacement(x) if pd.notna(x) else x
                    )
            return safe_file, df_copy

        with ThreadPoolExecutor(max_workers=min(4, len(file_names))) as executor:
            futures = {executor.submit(load_single_file, fn): fn for fn in file_names}

            for future in as_completed(futures):
                try:
                    safe_file, df = future.result()
                    data_dict[safe_file] = df
                except Exception as e:
                    raise RuntimeError(f"读取文件 {futures[future]} 失败: {str(e)}")

        self.current_data = data_dict
        return data_dict

    def process_and_anonymize_files(self, file_names, output_dir):
        """处理并去敏文件"""
        if not file_names:
            raise ValueError("未选择文件")

        if not output_dir or not os.path.exists(output_dir):
            raise ValueError("无效的输出目录")

        data_dict = self._load_file_data(file_names)
        results = {}

        for filename, df in data_dict.items():
            # 对DataFrame中的文本进行去敏处理
            anonymized_df = self._anonymize_dataframe(df)

            # 保存去敏后的文件
            base_name = os.path.splitext(filename)[0]
            ext = os.path.splitext(filename)[1]
            output_path = os.path.join(
                output_dir,
                f"{base_name}_anonymized{ext}"
            )

            # 根据文件类型保存
            _, ext = os.path.splitext(filename)
            if ext.lower() in ['.csv']:
                anonymized_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            elif ext.lower() in ['.xlsx', '.xls']:
                anonymized_df.to_excel(output_path, index=False)
            elif ext.lower() in ['.json']:
                anonymized_df.to_json(output_path, orient='records', force_ascii=False)
            else:  # 文本文件
                content = "\n".join(anonymized_df.iloc[:, 0].astype(str).tolist())
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            results[filename] = output_path

        return results

    def _anonymize_dataframe(self, df):
        """对DataFrame进行去敏处理，使用向量化操作"""
        df_copy = df.copy()

        # 对每一列进行处理
        for col in df_copy.columns:
            # 处理字符串类型的列，使用向量化操作
            if df_copy[col].dtype == 'object':
                # 使用applymap代替apply提高性能
                df_copy[col] = df_copy[col].astype(str).apply(
                    lambda x: self._anonymize_text(x) if pd.notna(x) else x
                )

        return df_copy

    def _anonymize_text(self, text):
        """对文本进行去敏处理"""
        if not text or not isinstance(text, str):
            return text

        # 使用敏感词处理器进行替换
        anonymized_text, _ = self.sensitive_processor.replace_sensitive_words(text)
        return anonymized_text

    def generate_processing_code(self, user_request, file_names):
        """生成完整可执行代码，而非函数内部逻辑"""
        if not self.client:
            # 默认代码：直接返回所有数据
            return """import pandas as pd
    result_table = pd.concat(data_dict.values(), ignore_index=True)
    # 转换所有时间类型列
    for col in result_table.columns:
        if pd.api.types.is_datetime64_any_dtype(result_table[col]):
            result_table[col] = result_table[col].astype(str)
    summary = f'共{len(result_table)}条记录'
    chart_info = None"""

        data_dict = self._load_file_data(file_names)
        file_info = {}

        # 处理用户请求，确保其中的敏感词被统一替换
        processed_request = self.sensitive_processor.normalize_to_replacement(user_request)

        for filename, df in data_dict.items():
            # 1. 替换列名中的敏感词
            replaced_columns = [
                self.sensitive_processor.normalize_to_replacement(col)
                for col in df.columns.tolist()
            ]

            # 2. 替换样本数据中的敏感词
            replaced_samples = []
            for sample in df.head(5).to_dict(orient='records'):
                replaced_sample = {}
                for key, value in sample.items():
                    # 对每个字段值进行替换（处理字符串类型）
                    if isinstance(value, str):
                        replaced_val = self.sensitive_processor.normalize_to_replacement(value)
                        replaced_sample[key] = replaced_val
                    else:
                        replaced_sample[key] = value  # 非字符串类型保持不变
                replaced_samples.append(replaced_sample)

            file_info[filename] = {
                "columns": replaced_columns,
                "sample": replaced_samples
            }

        # 3. 生成代码
        prompt = f"""根据用户请求编写完整的Python处理代码:
用户需求: {user_request}
数据信息: {json.dumps(file_info, ensure_ascii=False)}

### 核心数据说明
- 所有数据已加载到变量 `data_dict` 中（类型：字典）
- `data_dict` 的键为文件名（如上述数据信息中的文件名），值为对应文件的pandas.DataFrame
- 必须从 `data_dict` 中加载数据到 `df`，**禁止使用空DataFrame初始化后不赋值**

### 代码规范（必须严格遵守）
1. 开头必须包含：
import pandas as pd
import numpy as np
# 从data_dict加载数据到df（示例：合并所有文件或使用特定文件）
df = pd.concat(data_dict.values(), ignore_index=True)  # 合并所有文件数据
# 或：df = data_dict['具体文件名']  # 使用单个文件数据（需替换为实际文件名）

基于 df 进行数据处理（清洗、分析、转换等），禁止重新定义 df 或删除上述初始化代码

2. 必须定义三个变量：
   - result_table：处理后的DataFrame结果（必须存在）
   - summary：字符串类型的总结，根据用户要求生成具体内容，可包含：
     * 关键分析结论（如统计数量、趋势、异常点等）
     * 数据中发现的规律总结
     * 针对问题的解决方案或建议
     * 其他用户要求但无法被作为代码执行的信息
     禁止使用默认值，必须根据分析结果生成具体内容
   - chart_info：图表信息字典（** 必须包含chart_type字段 **），格式为:
     {{
       "chart_type": "bar/line/pie/scatter/hist",  # 强制必填，且为支持的类型
       "title": "图表标题",  # 强制必填
       "data_prep": {{
         "x_col": "x轴数据列名",  # bar/line/scatter/hist必须提供
         "y_col": "y轴数据列名",  # bar/line/scatter可选
         "values": "值列名",  # pie必须提供
         "bins": 分箱数  # hist可选
       }}
     }}
     这是图表信息的模板，chart_type字段按照这些关键词对应：bar柱状图/line折线图/scatter散点图/hist直方图/pie饼图
     生成代码时根据图表类型检查必要的列配置
            'bar': ['x_col', 'y_col']
            'line': ['x_col', 'y_col']
            'scatter': ['x_col', 'y_col']
            'pie': ['x_col', 'values']
            'hist': ['x_col']
     当用户说生成“图表”这类泛指时，由你决定图表类型（即chart_type字段）
     当用户需求中指明需要图表时才生成图表，若不需要图表，chart_info显式设置为None；若需要图表，所有标注"必须"的字段均为必填项
3. 代码必须可直接执行，不依赖外部文件，变量名不得与data_dict、df、result_table、summary、chart_info冲突
   错误后果：
   若未从data_dict加载数据导致df未定义，或未生成要求的变量，代码将执行失败。请严格检查代码正确性。
4. 保留数据中`PROTECTEDXXXXXXXX`格式的去敏字段，不做修改。
"""

        response = self.client.completions_create(
            model='deepseek-reasoner',
            prompt=prompt,
            max_tokens=10000,
            temperature=1.0
        )

        code_block = response.choices[0].message.content.strip()

        return code_block

    def direct_answer(self, user_request, file_names):
        """直接回答模式：对全部数据脱敏后调用API，不展示表格内容"""
        if not self.client:
            return {
                "summary": "未配置API密钥，无法进行直接回答",
                "result_table": None,  # 直接回答模式不展示表格
                "chart_info": None
            }

        # 加载数据并脱敏（处理全部数据）
        data_dict = self._load_file_data(file_names)
        file_info = {}
        for filename, df in data_dict.items():
            # 1. 脱敏列名
            replaced_columns = [
                self.sensitive_processor.replace_sensitive_words(col)[0]
                for col in df.columns.tolist()
            ]

            # 2. 脱敏全部数据（不再只传样本，而是全部记录）
            replaced_records = []
            for record in df.to_dict(orient='records'):  # 遍历所有行，而非head(2)
                replaced_record = {}
                for key, value in record.items():
                    if isinstance(value, str):
                        # 对字符串类型脱敏
                        replaced_val, _ = self.sensitive_processor.replace_sensitive_words(value)
                        replaced_record[key] = replaced_val
                    else:
                        replaced_record[key] = value  # 非字符串保持原样
                replaced_records.append(replaced_record)

            file_info[filename] = {
                "columns": replaced_columns,
                "records": replaced_records  # 用全部记录替换样本
            }

        # 构建脱敏后的prompt（明确基于全部数据回答）
        prompt = f"""用户需求: {user_request}
    数据信息: {json.dumps(file_info, ensure_ascii=False)}

    请基于提供的全部数据信息回答用户问题，无需生成代码。
    """

        # 调用API（仅传递脱敏数据）
        response = self.client.completions_create(prompt=prompt)
        raw_summary = response.choices[0].message.content

        # 本地还原总结内容（关键修改：确保在本地完成还原）
        restored_summary = self.sensitive_processor.restore_sensitive_words(raw_summary)

        return {
            "summary": restored_summary,  # 返回还原后的总结
            "result_table": None,  # 直接回答模式不返回表格
            "chart_info": None
        }