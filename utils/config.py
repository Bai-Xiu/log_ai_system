import os
import json


class Config:
    def __init__(self):
        self.config_file = os.path.join(os.path.expanduser("~"), ".log_analyzer_config.json")
        self.defaults = {
            "data_dir": "",  # 仅保留用户指定目录
            "api_key": "",
            "save_dir": "",
            "verbose_logging": False
        }
        self.config = self.defaults.copy()
        self.load()

    def load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
            except Exception as e:
                print(f"加载配置失败: {str(e)}")

    def save(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {str(e)}")

    def get(self, key, default=None):
        if default is None:
            default = self.defaults.get(key)
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()
