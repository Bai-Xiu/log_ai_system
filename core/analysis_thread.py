import re
import pandas as pd
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

class AnalysisThread(QThread):
    update_signal = pyqtSignal(str)
    complete_signal = pyqtSignal(dict)

    def __init__(self, processor, file_paths, request, mode):
        super().__init__()
        self.processor = processor
        self.file_paths = file_paths
        self.request = request
        self.mode = mode

    def run(self):
        try:
            self.update_signal.emit("开始分析数据...")
            if self.mode == "1":
                # 代码处理模式
                code_block = self.processor.generate_processing_code(self.request, self.file_paths)
                self.update_signal.emit("代码生成完成，开始执行处理...")

                # 清理代码块，移除三重反引号和语言标识
                cleaned_code = self.clean_code_block(code_block)

                # 执行清理后的代码
                result = self.execute_cleaned_code(cleaned_code)
            else:
                # 直接回答模式
                result = self.processor.direct_answer(self.request, self.file_paths)

            self.complete_signal.emit({"status": "success", "result": result})
        except Exception as e:
            self.complete_signal.emit({"status": "error", "message": str(e)})

    def clean_code_block(self, code):
        """清理代码块，移除可能的包裹符"""
        # 移除开头的```python标记
        code = re.sub(r'^```python\s*', '', code, flags=re.MULTILINE)
        # 移除结尾的```标记
        code = re.sub(r'```\s*$', '', code, flags=re.MULTILINE)
        # 移除前后空行
        return code.strip()

    def execute_cleaned_code(self, cleaned_code):
        """执行清理后的代码并返回结果"""
        # 准备数据字典
        data_dict = self.processor.load_data_files(self.file_paths)

        # 处理代码行：为空行添加0缩进，非空行添加4空格缩进
        processed_lines = []
        for line in cleaned_code.splitlines():
            # 处理空行（只包含空白字符的行）
            if line.strip() == "":
                processed_lines.append("")  # 空行保持原样，不添加缩进
            else:
                processed_lines.append(f"    {line}")  # 非空行添加4空格缩进

        # 创建包装函数
        wrapped_code = f"""
import pandas as pd
import numpy as np

def process_data(data_dict):
    # 从数据字典中提取文件
{chr(10).join([f'    {file} = data_dict["{file}"]' for file in self.file_paths])}

    # 用户代码
{chr(10).join(processed_lines)}  # 确保processed_lines的每行已有4个空格缩进

    # 尝试识别并返回结果
    local_vars = locals()
    dfs = [v for v in local_vars.values() if isinstance(v, pd.DataFrame)]

    # 查找可能的合并结果
    if 'combined' in local_vars and isinstance(local_vars['combined'], pd.DataFrame):
        result_table = local_vars['combined']
    elif dfs:
        if len(dfs) > 1:
            try:
                result_table = pd.concat(dfs, ignore_index=True)
            except:
                result_table = dfs[-1]
        else:
            result_table = dfs[0]
    else:
        result_table = None

    # 生成总结
    summary = "分析完成。"

    return {{"result_table": result_table, "summary": summary}}

# 执行处理函数
result = process_data(data_dict)
"""
        # 执行代码（后续逻辑不变）
        local_vars = {}
        try:
            exec(wrapped_code, globals(), local_vars)
            return local_vars.get('result', {"summary": "代码执行完成，但未生成有效结果"})
        except Exception as e:
            return {
                "summary": f"代码执行错误: {str(e)}\n\n执行的代码:\n{cleaned_code}"
            }