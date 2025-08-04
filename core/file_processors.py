import pandas as pd
import json
from abc import ABC, abstractmethod


class FileProcessor(ABC):
    """文件处理器基类，所有文件类型处理器需继承此类"""

    @abstractmethod
    def get_supported_extensions(self):
        """返回支持的文件扩展名列表（如 ['.csv']）"""
        pass

    @abstractmethod
    def read_file(self, file_path, encodings=None, **kwargs):
        """读取文件并返回DataFrame
        Args:
            file_path: 文件路径
            encodings: 尝试的编码列表
            kwargs: 额外参数
        Returns:
            pd.DataFrame: 读取的数据
        Raises:
            Exception: 读取失败时抛出
        """
        pass


class CsvFileProcessor(FileProcessor):
    def get_supported_extensions(self):
        return ['.csv']

    def read_file(self, file_path, encodings=None, **kwargs):
        encodings = encodings or ['utf-8', 'gbk', 'gb2312', 'ansi']
        for encoding in encodings:
            try:
                return pd.read_csv(
                    file_path,
                    encoding=encoding,
                    sep=kwargs.get('sep', ','),
                    engine=kwargs.get('engine', 'python')
                )
            except Exception:
                continue
        raise ValueError(f"CSV文件读取失败，已尝试编码: {encodings}")


class ExcelFileProcessor(FileProcessor):
    def get_supported_extensions(self):
        return ['.xlsx', '.xls']

    def read_file(self, file_path, **kwargs):
        # Excel文件通常不需要指定编码
        try:
            return pd.read_excel(
                file_path,
                sheet_name=kwargs.get('sheet_name', 0),
                engine=kwargs.get('engine', 'openpyxl')
            )
        except Exception as e:
            raise ValueError(f"Excel文件读取失败: {str(e)}")


class JsonFileProcessor(FileProcessor):
    def get_supported_extensions(self):
        return ['.json']

    def read_file(self, file_path, encodings=None, **kwargs):
        encodings = encodings or ['utf-8', 'gbk', 'gb2312', 'ansi']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    data = json.load(f)
                # 支持列表型JSON和对象型JSON
                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict):
                    return pd.DataFrame([data])
                else:
                    raise ValueError("JSON格式不支持（需为列表或对象）")
            except Exception:
                continue
        raise ValueError(f"JSON文件读取失败，已尝试编码: {encodings}")


class TxtFileProcessor(FileProcessor):
    def get_supported_extensions(self):
        return ['.txt', '.log']

    def read_file(self, file_path, encodings=None, **kwargs):
        encodings = encodings or ['utf-8', 'gbk', 'gb2312', 'ansi']
        delimiter = kwargs.get('delimiter', ' ')
        for encoding in encodings:
            try:
                return pd.read_csv(
                    file_path,
                    encoding=encoding,
                    sep=delimiter,
                    engine='python',
                    header=kwargs.get('header', None)
                )
            except Exception:
                continue
        raise ValueError(f"TXT/LOG文件读取失败，已尝试编码: {encodings}")