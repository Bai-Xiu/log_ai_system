import sys
import os
from PyQt5.QtWidgets import QApplication
from ui.main_window import LogAnalyzerGUI
from utils.config import Config


def main():
    # 初始化配置
    config = Config()
    config.load()

    data_dir = config.get('data_dir')
    if data_dir and os.path.isdir(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    else:
        # 如果配置中没有有效的数据目录，使用当前目录
        default_dir = os.path.abspath("./data")
        os.makedirs(default_dir, exist_ok=True)
        config.set('data_dir', default_dir)

    # 确保应用
    app = QApplication(sys.argv)
    window = LogAnalyzerGUI(config)  # 现在可以正确找到该类
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()