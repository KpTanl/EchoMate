import json
import os

class Config:
    """
    统一管理配置中心，支持 JSON 持久化。
    """
    def __init__(self):
        self._config_file = os.path.join(os.path.dirname(__file__), '..', 'settings.json')
        
        # 默认配置
        self.model_mode = "cloud"  # "local" or "cloud"
        self.pet_name = "EchoMate"
        
        # 用户可自行配置的 API 参数
        self.api_base_url = "https://api.openai.com/v1"
        self.api_key = ""
        self.model_name = "gpt-3.5-turbo"
        
        # 只读的系统预设小鸟档案（不参与持久化修改）
        self.pet_gender = "小女孩"
        self.pet_birthday = "2024年1月1日"
        self.pet_likes = "向日葵瓜子、主人的摸摸、唱歌"
        self.pet_dislikes = "大灰狼、雷雨天、孤独"
        self.pet_info = "喜欢在句末加一些'叽！'或者'嘎！'的语气词，性格活泼可爱。"
        
        self.load()
        
    def load(self):
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                self.model_mode = data.get("model_mode", self.model_mode)
                self.pet_name = data.get("pet_name", self.pet_name)
                self.api_base_url = data.get("api_base_url", self.api_base_url)
                self.api_key = data.get("api_key", self.api_key)
                self.model_name = data.get("model_name", self.model_name)
            except Exception as e:
                print(f"配置文件读取失败: {e}")

    def save(self):
        data = {
            "model_mode": self.model_mode,
            "pet_name": self.pet_name,
            "api_base_url": self.api_base_url,
            "api_key": self.api_key,
            "model_name": self.model_name
        }
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"配置文件保存失败: {e}")

config = Config()
