from core.event_bus import event_bus
from core.config import config
from core.state_manager import state_manager
from core.mod_loader import mod_loader
from core.agent_engine import AgentEngine
import sys

class AppManager:
    """
    全局控制中心
    负责初始化环境、载入配置，并注册所有的核心订阅者/发布者实例。
    """
    def __init__(self):
        self.agent_engine = AgentEngine()
        
        # 绑定核心应用退出逻辑
        event_bus.on_app_quit.connect(self.quit_app)
        
    def start(self):
        """挂载全部子模块并启动引擎"""
        mod_loader.load_all()
        self.agent_engine.start()
        print(f"[{config.pet_name}] AppManager started. Agent engine is running.")
        
    def quit_app(self):
        from PySide6.QtWidgets import QApplication
        print(f"[{config.pet_name}] App quitting...")
        self.agent_engine.stop()
        app = QApplication.instance()
        if app:
            app.quit()
        else:
            sys.exit(0)

app_manager = AppManager()
