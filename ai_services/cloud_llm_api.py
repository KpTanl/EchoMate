import requests
from core.config import config
from typing import List, Dict

class CloudLLMAPI:
    """极简云端大语言模型请求接口 (OpenAI 格式兼容)"""
    def generate(self, messages: List[Dict[str, str]]) -> str:
        # 主人直接在设置里填了完整的 URL，所以我们不再自动补全后缀了
        url = config.api_base_url.rstrip("/")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.api_key}"
        }
        payload = {
            "model": config.model_name,
            "messages": messages
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"API Error: {str(e)}"

cloud_llm = CloudLLMAPI()
