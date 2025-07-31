import sys
import os
from PyQt5.QtWidgets import QApplication
from ui.main_window import LogAnalyzerGUI
from utils.config import Config


def main():
    config = Config()
    config.load()

    data_dir = config.get('data_dir')
    if data_dir and os.path.isdir(data_dir):
        os.makedirs(data_dir, exist_ok=True)  # 仅创建用户指定目录
    else:
        default_dir = os.path.abspath("./data")
        os.makedirs(default_dir, exist_ok=True)
        config.set('data_dir', default_dir)

    # 确保应用
    app = QApplication(sys.argv)
    window = LogAnalyzerGUI(config)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
