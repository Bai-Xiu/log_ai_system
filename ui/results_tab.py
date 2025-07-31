from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
                             QSplitter, QGroupBox, QFileDialog)
from PyQt5.QtCore import Qt
import os
import pandas as pd


class ResultsTab(QWidget):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.parent = parent
        self.current_result = None
        self.save_dir = config.get("save_dir")  # 默认保存目录
        self.init_ui()

    def init_ui(self):
        """初始化结果展示标签页UI"""
        layout = QVBoxLayout(self)

        # 保存路径选择
        save_path_layout = QHBoxLayout()
        save_path_layout.addWidget(QLabel("保存路径:"))

        self.save_dir_edit = QLineEdit(self.save_dir)
        self.save_dir_edit.setReadOnly(False)  # 允许手动输入保存路径
        save_path_layout.addWidget(self.save_dir_edit)

        self.change_save_dir_btn = QPushButton("浏览...")
        self.change_save_dir_btn.clicked.connect(self.change_save_dir)
        save_path_layout.addWidget(self.change_save_dir_btn)

        self.apply_save_dir_btn = QPushButton("应用")
        self.apply_save_dir_btn.clicked.connect(self.apply_save_dir)
        save_path_layout.addWidget(self.apply_save_dir_btn)

        # 分割器
        splitter = QSplitter(Qt.Vertical)

        # 总结区域
        summary_group = QGroupBox("分析总结")
        summary_layout = QVBoxLayout(summary_group)

        self.summary_display = QTextEdit()
        self.summary_display.setReadOnly(True)
        summary_layout.addWidget(self.summary_display)
        splitter.addWidget(summary_group)

        # 表格区域
        table_group = QGroupBox("结果表格")
        table_layout = QVBoxLayout(table_group)

        self.result_table = QTableWidget()
        table_layout.addWidget(self.result_table)
        splitter.addWidget(table_group)
        splitter.setSizes([200, 400])

        # 按钮区
        btn_layout = QHBoxLayout()

        self.save_btn = QPushButton("保存结果")
        self.save_btn.clicked.connect(self.save_results)
        self.save_btn.setEnabled(False)

        self.new_analysis_btn = QPushButton("新分析")
        self.new_analysis_btn.clicked.connect(self.start_new_analysis)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.new_analysis_btn)

        # 组装布局
        layout.addLayout(save_path_layout)
        layout.addWidget(splitter)
        layout.addLayout(btn_layout)

    def set_result(self, result):
        """设置并显示分析结果"""
        self.current_result = result
        self.display_results(result)

    def display_results(self, result):
        """展示分析结果，优化时间显示"""
        # 显示总结
        if "summary" in result:
            self.summary_display.setText(result["summary"])
            self.save_btn.setEnabled("result_table" in result and result["result_table"] is not None)

        # 显示表格
        if "result_table" in result and isinstance(result["result_table"], pd.DataFrame):
            df = result["result_table"].copy()

            # 优化日期时间列显示
            for col in df.columns:
                col_name = str(col).lower()
                # 识别可能的日期时间列
                if any(keyword in col_name for keyword in
                       ['date', 'time', 'timestamp', 'datetime', '时间', '日期', '时间戳']):
                    try:
                        # 尝试转换为日期时间
                        if not pd.api.types.is_datetime64_any_dtype(df[col]):
                            df[col] = pd.to_datetime(df[col], errors='coerce')

                        # 转换为友好的字符串格式
                        if pd.api.types.is_datetime64_any_dtype(df[col]):
                            # 区分日期和时间
                            if df[col].dt.hour.nunique() > 1 or df[col].dt.minute.nunique() > 1:
                                # 有具体时间信息
                                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                            else:
                                # 只有日期信息
                                df[col] = df[col].dt.strftime('%Y-%m-%d')
                    except Exception as e:
                        print(f"列 {col} 日期格式化失败: {e}")
                        df[col] = df[col].astype(str)

            # 填充表格数据
            self.result_table.setRowCount(df.shape[0])
            self.result_table.setColumnCount(df.shape[1])
            self.result_table.setHorizontalHeaderLabels(df.columns)

            for row in range(df.shape[0]):
                for col in range(df.shape[1]):
                    try:
                        value = str(df.iloc[row, col])
                        # 处理空值显示
                        if value in ['NaT', 'nan', 'None', '']:
                            value = ''
                    except Exception as e:
                        value = f"数据错误: {str(e)}"
                    self.result_table.setItem(row, col, QTableWidgetItem(value))

            # 自动调整列宽
            self.result_table.resizeColumnsToContents()

    def change_save_dir(self):
        """通过浏览更改保存目录"""
        new_dir = QFileDialog.getExistingDirectory(
            self, "选择保存目录", self.save_dir
        )
        if new_dir:
            self.save_dir_edit.setText(new_dir)
            self.apply_save_dir()

    def apply_save_dir(self):
        """应用保存目录更改"""
        new_dir = self.save_dir_edit.text().strip()
