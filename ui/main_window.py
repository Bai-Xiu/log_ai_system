from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTabWidget, QGroupBox, QSplitter,
                             QTextEdit, QComboBox, QProgressBar, QStatusBar, QTableWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from core.processor import LogAIProcessor
from ui.file_tab import FileTab
from ui.analysis_tab import AnalysisTab
from ui.results_tab import ResultsTab
import os


class LogAnalyzerGUI(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.processor = LogAIProcessor(config)
        self.selected_files = []
        self.current_result = None
        self.save_dir = config.get("save_dir")  # 默认保存目录
        self.init_ui()

    def init_ui(self):
        # 窗口基本设置
        self.setWindowTitle("信息安全日志AI分析系统")
        self.setGeometry(100, 100, 1200, 800)
        self.setFont(QFont("SimHei", 9))
        self.set_window_icon()

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 创建标签页
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # 添加配置标签页
        self.config_tab = QWidget()
        self.setup_config_tab()
        self.tabs.addTab(self.config_tab, "配置")

        # 1. 文件选择标签页
        self.file_tab = FileTab(self.processor, self.config, self)
        self.tabs.addTab(self.file_tab, "文件选择")

        # 2. 分析标签页
        self.analysis_tab = AnalysisTab(self.processor, self.file_tab, self)
        self.tabs.addTab(self.analysis_tab, "数据分析")

        # 3. 结果标签页
        self.results_tab = ResultsTab(self.config, self)
        self.tabs.addTab(self.results_tab, "分析结果")

        # 状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")

    def set_window_icon(self):
        """设置窗口图标（实际项目中可实现）"""
        pass

    def setup_config_tab(self):
        """设置配置标签页，包含API Key等设置"""
        layout = QVBoxLayout(self.config_tab)

        # API Key设置
        api_group = QGroupBox("DeepSeek API 设置")
        api_layout = QVBoxLayout(api_group)

        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(QLabel("API Key:"))

        self.api_key_edit = QLineEdit(self.config.get("api_key"))
        self.api_key_edit.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        api_key_layout.addWidget(self.api_key_edit)

        self.save_api_btn = QPushButton("保存API Key")
        self.save_api_btn.clicked.connect(self.save_api_key)
        api_key_layout.addWidget(self.save_api_btn)

        api_layout.addLayout(api_key_layout)

        # 其他配置选项
        other_group = QGroupBox("其他配置")
        other_layout = QVBoxLayout(other_group)

        # 数据目录配置
        data_dir_layout = QHBoxLayout()
        data_dir_layout.addWidget(QLabel("默认数据目录:"))

        self.default_data_dir_edit = QLineEdit(self.config.get("data_dir"))
        self.default_data_dir_edit.setReadOnly(True)
        data_dir_layout.addWidget(self.default_data_dir_edit)

        self.change_default_data_dir_btn = QPushButton("更改...")
        self.change_default_data_dir_btn.clicked.connect(self.change_default_data_dir)
        data_dir_layout.addWidget(self.change_default_data_dir_btn)

        # 结果保存目录配置
        save_dir_layout = QHBoxLayout()
        save_dir_layout.addWidget(QLabel("默认结果目录:"))

        self.default_save_dir_edit = QLineEdit(self.config.get("save_dir"))
        self.default_save_dir_edit.setReadOnly(True)
        save_dir_layout.addWidget(self.default_save_dir_edit)

        self.change_default_save_dir_btn = QPushButton("更改...")
        self.change_default_save_dir_btn.clicked.connect(self.change_default_save_dir)
        save_dir_layout.addWidget(self.change_default_save_dir_btn)

        other_layout.addLayout(data_dir_layout)
        other_layout.addLayout(save_dir_layout)

        # 组装布局
        layout.addWidget(api_group)
        layout.addWidget(other_group)
        layout.addStretch()

    def save_api_key(self):
        """保存API密钥"""
        api_key = self.api_key_edit.text().strip()
        self.config.set("api_key", api_key)
        self.processor.api_key = api_key
        self.processor.client = None  # 重置客户端
        if api_key:
            self.processor.client = DeepSeekAPI(api_key=api_key)
        self.statusBar.showMessage("API Key已保存")

    def change_default_data_dir(self):
        """更改默认数据目录"""
        new_dir = QFileDialog.getExistingDirectory(
            self, "选择默认数据目录",
            self.config.get("data_dir")
        )
        if new_dir:
            self.config.set("data_dir", new_dir)
            self.default_data_dir_edit.setText(new_dir)
            self.processor.set_data_dir(new_dir)
            self.statusBar.showMessage(f"默认数据目录已更新为: {new_dir}")

    def change_default_save_dir(self):
        """更改默认结果保存目录"""
        new_dir = QFileDialog.getExistingDirectory(
            self, "选择默认结果目录",
            self.config.get("save_dir")
        )
        if new_dir:
            self.config.set("save_dir", new_dir)
            self.default_save_dir_edit.setText(new_dir)
            self.processor.set_save_dir(new_dir)
            self.results_tab.save_dir = new_dir
            self.results_tab.save_dir_edit.setText(new_dir)
            self.statusBar.showMessage(f"默认结果目录已更新为: {new_dir}")

    def set_analysis_result(self, result):
        """设置分析结果到结果标签页"""
        self.current_result = result
        self.results_tab.set_result(result)