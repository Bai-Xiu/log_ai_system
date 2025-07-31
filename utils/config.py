import os
import json

class Config:
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config.json')
        self.config = {
            "api_key": "",
            "data_dir": os.path.abspath("../data"),
            "save_dir": os.path.abspath("../results"),
            "verbose_logging": False
        }
        self.load()
        # 确保目录存在
        os.makedirs(self.config["data_dir"], exist_ok=True)
        os.makedirs(self.config["save_dir"], exist_ok=True)

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
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()  # 自动保存