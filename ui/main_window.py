import os
import matplotlib
import pandas as pd
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QStatusBar, QMessageBox, QSplitter, QGroupBox,
                             QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QListWidget, QTextEdit, QComboBox,
                             QProgressBar, QTableWidget, QFileDialog,
                             QFileIconProvider, QListWidgetItem, QTableWidgetItem)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QFont, QIcon
from core.processor import LogAIProcessor
from core.analysis_thread import AnalysisThread

# 确保中文显示正常
matplotlib.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]


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
        self.file_tab = QWidget()
        self.setup_file_tab()
        self.tabs.addTab(self.file_tab, "文件选择")

        # 2. 分析标签页
        self.analysis_tab = QWidget()
        self.setup_analysis_tab()
        self.tabs.addTab(self.analysis_tab, "数据分析")

        # 3. 结果标签页
        self.results_tab = QWidget()
        self.setup_results_tab()
        self.tabs.addTab(self.results_tab, "分析结果")

        # 状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")

        # 信号连接
        self.update_file_list()

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

    def setup_file_tab(self):
        """设置文件选择标签页"""
        layout = QVBoxLayout(self.file_tab)

        # 数据目录选择区
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("当前数据目录:"))

        # 修正：使用config.get获取数据目录，而非processor的方法
        self.data_dir_edit = QLineEdit(self.config.get("data_dir"))
        self.data_dir_edit.setReadOnly(False)  # 允许手动输入路径
        dir_layout.addWidget(self.data_dir_edit)

        self.change_dir_btn = QPushButton("浏览...")
        self.change_dir_btn.clicked.connect(self.change_data_dir)
        dir_layout.addWidget(self.change_dir_btn)

        self.apply_dir_btn = QPushButton("应用")
        self.apply_dir_btn.clicked.connect(self.apply_data_dir)
        dir_layout.addWidget(self.apply_dir_btn)

        # 添加文件按钮
        add_file_layout = QHBoxLayout()
        self.add_external_btn = QPushButton("添加外部文件...")
        self.add_external_btn.clicked.connect(self.add_external_files)
        add_file_layout.addWidget(self.add_external_btn)
        add_file_layout.addStretch()

        # 顶部按钮区
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("刷新文件列表")
        self.refresh_btn.clicked.connect(self.update_file_list)
        self.add_btn = QPushButton("添加选中")
        self.add_btn.clicked.connect(self.add_files)
        self.remove_btn = QPushButton("移除选中")
        self.remove_btn.clicked.connect(self.remove_files)
        self.clear_btn = QPushButton("清空选择")
        self.clear_btn.clicked.connect(self.clear_selection)

        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.clear_btn)

        # 文件列表区域
        list_group = QGroupBox("可用日志文件")
        list_layout = QVBoxLayout(list_group)

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.ExtendedSelection)
        list_layout.addWidget(self.file_list)

        # 已选文件区域
        selected_group = QGroupBox("已选择文件")
        selected_layout = QVBoxLayout(selected_group)

        self.selected_list = QListWidget()
        selected_layout.addWidget(self.selected_list)

        # 分割器布局
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(list_group)
        splitter.addWidget(selected_group)
        splitter.setSizes([300, 200])

        # 底部按钮
        self.next_btn = QPushButton("下一步分析")
        self.next_btn.clicked.connect(self.go_to_analysis)
        self.next_btn.setEnabled(False)

        # 组装布局
        layout.addLayout(dir_layout)
        layout.addLayout(add_file_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(splitter)
        layout.addWidget(self.next_btn)

    def setup_analysis_tab(self):
        """设置数据分析标签页"""
        layout = QVBoxLayout(self.analysis_tab)

        # 分析请求输入
        req_group = QGroupBox("分析请求")
        req_layout = QVBoxLayout(req_group)

        self.request_input = QTextEdit()
        self.request_input.setPlaceholderText("请输入分析需求，例如：统计各类型入侵次数、列出出现频率最高的10个IP地址...")
        req_layout.addWidget(self.request_input)

        # 处理模式选择
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("处理模式:"))

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["代码处理(生成CSV)", "直接回答"])
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()

        # 进度条
        self.progress = QProgressBar()
        self.progress.setAlignment(Qt.AlignCenter)
        self.progress.setVisible(False)

        # 按钮区
        btn_layout = QHBoxLayout()

        self.back_btn = QPushButton("返回")
        self.back_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(1))  # 返回文件选择页

        self.start_btn = QPushButton("开始分析")
        self.start_btn.clicked.connect(self.start_analysis)

        btn_layout.addWidget(self.back_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.start_btn)

        # 组装布局
        layout.addWidget(req_group)
        layout.addLayout(mode_layout)
        layout.addWidget(self.progress)
        layout.addLayout(btn_layout)

    def setup_results_tab(self):
        """设置结果展示标签页"""
        layout = QVBoxLayout(self.results_tab)

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
        self.new_analysis_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(1))  # 返回文件选择页

        btn_layout.addWidget(self.save_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.new_analysis_btn)

        # 组装布局
        layout.addLayout(save_path_layout)
        layout.addWidget(splitter)
        layout.addLayout(btn_layout)

    # 配置相关方法
    def save_api_key(self):
        """保存API Key"""
        api_key = self.api_key_edit.text().strip()
        self.processor.set_api_key(api_key)
        QMessageBox.information(self, "成功", "API Key已保存")

    def change_default_data_dir(self):
        """更改默认数据目录"""
        new_dir = QFileDialog.getExistingDirectory(
            self, "选择默认数据目录",
            self.config.get("data_dir")
        )
        if new_dir:
            self.config.set("data_dir", new_dir)
            self.default_data_dir_edit.setText(new_dir)
            # 更新当前数据目录
            self.data_dir_edit.setText(new_dir)
            self.processor.set_data_dir(new_dir)
            self.update_file_list()
            self.clear_selection()

    def change_default_save_dir(self):
        """更改默认保存目录"""
        new_dir = QFileDialog.getExistingDirectory(
            self, "选择默认保存目录",
            self.config.get("save_dir")
        )
        if new_dir:
            self.config.set("save_dir", new_dir)
            self.default_save_dir_edit.setText(new_dir)
            self.save_dir = new_dir
            self.save_dir_edit.setText(new_dir)

    # 文件处理相关方法
    def set_window_icon(self):
        """设置窗口图标"""
        icon_paths = [
            "app_icon.ico",
            "./resources/app_icon.ico",
            os.path.join(os.path.dirname(__file__), "app_icon.ico")
        ]

        for path in icon_paths:
            if os.path.exists(path):
                self.setWindowIcon(QIcon(path))
                return

        print("提示: 未找到图标文件，使用默认图标")

    def change_data_dir(self):
        """通过浏览更改数据目录"""
        new_dir = QFileDialog.getExistingDirectory(
            self, "选择数据目录",
            self.config.get("data_dir")
        )
        if new_dir:
            self.data_dir_edit.setText(new_dir)
            self.apply_data_dir()

    def apply_data_dir(self):
        """应用数据目录更改"""
        new_dir = self.data_dir_edit.text().strip()
        if new_dir and os.path.isdir(new_dir):
            self.config.set("data_dir", new_dir)
            self.processor.set_data_dir(new_dir)
            self.update_file_list()
            self.clear_selection()
            self.statusBar.showMessage(f"数据目录已更新为: {new_dir}")
        else:
            QMessageBox.warning(self, "警告", "无效的目录路径")
            self.data_dir_edit.setText(self.config.get("data_dir"))

    def add_external_files(self):
        """添加外部文件到数据目录"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "选择日志文件", "", "CSV文件 (*.csv);;所有文件 (*)"
        )

        if file_paths:
            data_dir = self.config.get("data_dir")
            added_files = []

            for file_path in file_paths:
                try:
                    # 获取文件名
                    file_name = os.path.basename(file_path)
                    dest_path = os.path.join(data_dir, file_name)

                    # 检查文件是否已存在
                    if os.path.exists(dest_path):
                        # 询问是否覆盖
                        reply = QMessageBox.question(
                            self, "文件已存在",
                            f"文件 {file_name} 已存在，是否覆盖？",
                            QMessageBox.Yes | QMessageBox.No
                        )
                        if reply != QMessageBox.Yes:
                            continue

                    # 复制文件
                    import shutil
                    shutil.copy2(file_path, dest_path)
                    added_files.append(file_name)
                except Exception as e:
                    QMessageBox.warning(self, "复制失败", f"无法复制文件 {file_path}: {str(e)}")

            if added_files:
                QMessageBox.information(
                    self, "添加成功",
                    f"已添加 {len(added_files)} 个文件到数据目录"
                )
                self.update_file_list()

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
        if new_dir and os.path.isdir(new_dir):
            self.save_dir = new_dir
            self.statusBar.showMessage(f"保存目录已更新为: {new_dir}")
        else:
            QMessageBox.warning(self, "警告", "无效的目录路径")
            self.save_dir_edit.setText(self.save_dir)

    def update_file_list(self):
        """更新可用文件列表"""
        self.file_list.clear()
        try:
            # 修正：使用config.get获取数据目录，调用processor的get_file_list方法
            files = self.processor.get_file_list(self.config.get("data_dir"))
            icon_provider = QFileIconProvider()

            for file in files:
                # 创建带有图标的列表项
                item = QListWidgetItem(icon_provider.icon(QFileIconProvider.File), file)
                self.file_list.addItem(item)

            self.statusBar.showMessage(f"已加载 {len(files)} 个文件")
        except Exception as e:
            QMessageBox.warning(self, "警告", f"加载文件列表失败: {str(e)}")

    def add_files(self):
        """添加文件到选择列表"""
        selected = self.file_list.selectedItems()
        if not selected:
            QMessageBox.information(self, "提示", "请先选择文件")
            return

        for item in selected:
            filename = item.text()
            if not self.selected_list.findItems(filename, Qt.MatchExactly):
                self.selected_list.addItem(filename)
                self.selected_files.append(filename)

        self.update_next_button()

    def remove_files(self):
        """移除选中的文件"""
        for item in self.selected_list.selectedItems():
            self.selected_files.remove(item.text())
            self.selected_list.takeItem(self.selected_list.row(item))

        self.update_next_button()

    def clear_selection(self):
        """清空选择列表"""
        self.selected_list.clear()
        self.selected_files = []
        self.update_next_button()

    def update_next_button(self):
        """更新下一步按钮状态"""
        self.next_btn.setEnabled(len(self.selected_files) > 0)

    def go_to_analysis(self):
        """前往分析标签页"""
        self.tabs.setCurrentIndex(2)
        self.statusBar.showMessage(f"已选择 {len(self.selected_files)} 个文件")

    def start_analysis(self):
        """开始分析数据"""
        request = self.request_input.toPlainText().strip()
        if not request:
            QMessageBox.warning(self, "警告", "请输入分析请求")
            return

        if not self.selected_files:
            QMessageBox.warning(self, "警告", "请先选择文件")
            return

        # 准备分析
        self.start_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)  # 无限进度
        self.statusBar.showMessage("分析中...")

        # 确定模式
        mode = "1" if self.mode_combo.currentText().startswith("代码处理") else "2"

        # 启动后台线程
        self.analysis_thread = AnalysisThread(
            self.processor,
            self.selected_files,
            request,
            mode,
            self.config.get("data_dir")  # 传递数据目录
        )
        self.analysis_thread.update_signal.connect(self.update_status)
        self.analysis_thread.complete_signal.connect(self.analysis_complete)
        self.analysis_thread.start()

    def update_status(self, message):
        """更新状态信息"""
        self.statusBar.showMessage(message)

    def analysis_complete(self, result):
        """分析完成处理"""
        self.progress.setVisible(False)
        self.start_btn.setEnabled(True)

        if result["status"] == "success":
            self.statusBar.showMessage("分析完成")
            self.current_result = result["result"]
            self.display_results(result["result"])
            self.tabs.setCurrentIndex(3)
        else:
            self.statusBar.showMessage("分析失败")
            QMessageBox.critical(self, "错误", result["message"])

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

    def save_results(self):
        """保存分析结果，使用用户选择的保存路径"""
        if not hasattr(self, 'current_result') or "result_table" not in self.current_result:
            QMessageBox.warning(self, "警告", "没有可保存的表格数据")
            return

        try:
            # 生成带时间戳的文件名
            timestamp = QDateTime.currentDateTime().toString("yyyyMMddHHmmss")
            file_name = f"analysis_result_{timestamp}.csv"
            file_path = os.path.join(self.save_dir, file_name)

            # 保存CSV
            self.current_result["result_table"].to_csv(
                file_path,
                index=False,
                encoding='utf-8-sig'  # 确保中文正常显示
            )

            QMessageBox.information(
                self,
                "成功",
                f"结果已保存至:\n{file_path}"
            )

        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"无法保存文件: {str(e)}")
