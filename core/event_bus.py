from PySide6.QtCore import QObject, Signal

class _EventBus(QObject):
    """
    全局事件总线，单例模式。
    必须继承自 QObject 才能使用 Signal。
    所有子线程必须通过发出这里的 Signal 来更新主界面的 UI。
    """
    
    # 定义系统级信号
    on_app_quit = Signal()
    
    # 状态有关信号
    on_state_change = Signal(dict)
    
    # 语音/提示有关信号
    on_speech_ready = Signal(str)
    
    # 交互与 UI 信号
    on_pet_clicked = Signal()
    on_pet_rubbed = Signal()
    on_toggle_cage = Signal(bool) # True打开笼子，False放出小鸟

    # AI 聊天相关信号
    on_user_input = Signal(str)
    on_agent_response = Signal(str)

# 暴露单例实例
event_bus = _EventBus()
