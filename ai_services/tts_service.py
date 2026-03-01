from core.event_bus import event_bus

class TTSService:
    """
    文本转语音服务 (Dummy)
    负责监听文字内容，在后台合成并播放音频。
    """
    def __init__(self):
        # 订阅需要发音的事件
        event_bus.on_speech_ready.connect(self._speak)

    def _speak(self, text: str):
        print(f"[TTS Dummy] Speaking: {text}")

tts_service = TTSService()
