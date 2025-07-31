import json
import os

class Config:
    def __init__(self):
        self.config_file = os.path.expanduser("~/.log_ai_config.json")
        self.config = self._load_defaults()
        self.load()

    def _load_defaults(self):
        """默认配置"""
        return {
            "api_key": "",
            "data_dir": os.path.abspath("./data"),
            "save_dir": os.path.abspath("./results"),
            "verbose_logging": False
        }

    def load(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config.update(json.load(f))
            except:
                pass  # 加载失败使用默认配置

    def save(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)

    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value
        self.save()  # 即时保存