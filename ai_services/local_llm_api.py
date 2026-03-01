class LocalLLMAPI:
    """本地大语言模型请求接口 (Dummy)"""
    def generate(self, prompt: str) -> str:
        return "Local LLM is not implemented yet."

local_llm = LocalLLMAPI()
