from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,  # 确保包含 QTextEdit
                             QSplitter, QGroupBox, QFileDialog)
from PyQt5.QtCore import Qt
import os
import pandas as pd
from utils.helpers import show_info_message, show_error_message, get_unique_filename


class ResultsTab(QWidget):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.parent = parent
        self.current_result = None
        self.save_dir = config.get("save_dir")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 保存路径选择
        save_path_layout = QHBoxLayout()
        save_path_layout.addWidget(QLabel("保存路径:"))

        self.save_dir_edit = QLineEdit(self.save_dir)
        self.save_dir_edit.setReadOnly(False)
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

        layout.addLayout(save_path_layout)
        layout.addWidget(splitter)
        layout.addLayout(btn_layout)

    def set_result(self, result):
        self.current_result = result
        self.display_results(result)

    def display_results(self, result):
        # 显示总结
        if "summary" in result:
            self.summary_display.setText(result["summary"])
            self.save_btn.setEnabled("result_table" in result and result["result_table"] is not None)

        # 显示表格
        if "result_table" in result and isinstance(result["result_table"], pd.DataFrame):
            df = result["result_table"].copy()
            self.result_table.setRowCount(df.shape[0])
            self.result_table.setColumnCount(df.shape[1])
            self.result_table.setHorizontalHeaderLabels(df.columns)

            for row in range(df.shape[0]):
                for col in range(df.shape[1]):
                    try:
                        value = str(df.iloc[row, col])
                        if value in ['NaT', 'nan', 'None', '']:
                            value = ''
                    except Exception as e:
                        value = f"数据错误: {str(e)}"
                    self.result_table.setItem(row, col, QTableWidgetItem(value))

            self.result_table.resizeColumnsToContents()

    def change_save_dir(self):
        new_dir = QFileDialog.getExistingDirectory(self, "选择保存目录", self.save_dir)
        if new_dir:
            self.save_dir_edit.setText(new_dir)
            self.apply_save_dir()

    def apply_save_dir(self):
        new_dir = self.save_dir_edit.text().strip()
        if new_dir and os.path.isdir(new_dir):
            self.save_dir = new_dir
            self.config.set("save_dir", new_dir)
        else:
            show_error_message(self, "错误", "无效的目录路径")
            self.save_dir_edit.setText(self.save_dir)

    def save_results(self):
        if not self.current_result or "result_table" not in self.current_result:
            show_error_message(self, "错误", "没有可保存的结果")
            return

        try:
            df = self.current_result["result_table"]
            base_name = "analysis_result"
            filename = get_unique_filename(self.save_dir, base_name, "csv")
            file_path = os.path.join(self.save_dir, filename)

            df.to_csv(file_path, index=False, encoding="utf-8-sig")
            show_info_message(self, "成功", f"结果已保存至:\n{file_path}")
        except Exception as e:
            show_error_message(self, "保存失败", f"无法保存结果: {str(e)}")

    def start_new_analysis(self):
        if self.parent and hasattr(self.parent, 'tabs'):
            self.parent.tabs.setCurrentIndex(1)  # 返回文件选择页