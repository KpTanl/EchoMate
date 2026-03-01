import sys
import os
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QAction, QIcon
from core.event_bus import event_bus

class AppTrayIcon(QSystemTrayIcon):
    """
    全局系统托盘管理
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setToolTip("EchoMate - 桌面宠物")
        
        # 尝试加载图标
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'parrot', 'Peach-faced-lovebird', 'Peach-faced-lovebird_idle_01.png')
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        
        self.menu = QMenu()
        
        self.toggle_cage_action = QAction("打开笼子 / 唤回小鸟", self.menu)
        self.toggle_cage_action.triggered.connect(self._on_toggle_cage)
        self.menu.addAction(self.toggle_cage_action)
        
        self.menu.addSeparator()
        
        self.quit_action = QAction("退出嘎！", self.menu)
        self.quit_action.triggered.connect(self._on_quit)
        self.menu.addAction(self.quit_action)
        
        self.setContextMenu(self.menu)
        
        # 支持左键双击动作
        self.activated.connect(self._on_activated)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self._on_toggle_cage()
            
    def _on_toggle_cage(self):
        # 传 True 代表呼出主窗口（打开笼子）
        event_bus.on_toggle_cage.emit(True)

    def _on_quit(self):
        """
        触发全局退出事件，通知 AppManager 和其他组件保存并退出。
        """
        event_bus.on_app_quit.emit()
