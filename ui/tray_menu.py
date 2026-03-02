import sys
import os
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import QObject
from core.event_bus import event_bus
from ui.mark_mode_overlay import MarkModeOverlay


class GlobalShortcutManager(QObject):
    """
    全局快捷键管理器
    注意：Qt 的 QShortcut 只在应用程序有焦点时有效
    真正的全局快捷键需要平台特定实现，这里使用单例模式确保可用
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, parent=None):
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return
        super().__init__(parent)
        self._overlay = None
        self._initialized = True
    
    def start_mark_mode(self):
        """启动标记模式"""
        # 避免重复开启
        if self._overlay and self._overlay.isVisible():
            return
        
        self._overlay = MarkModeOverlay()
        self._overlay.position_marked.connect(self._on_position_marked)
        self._overlay.cancelled.connect(self._on_cancelled)
        self._overlay.show()
        
        # 发射信号通知其他组件
        event_bus.on_mark_mode_start.emit()
    
    def _on_position_marked(self, pos):
        """位置被标记"""
        event_bus.on_destination_set.emit(pos)
        self._overlay = None
    
    def _on_cancelled(self):
        """用户取消"""
        self._overlay = None


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
        
        # 创建全局快捷键管理器
        self._shortcut_manager = GlobalShortcutManager(self)
        
        # 构建菜单
        self.menu = QMenu()
        
        # 召唤功能
        self.summon_action = QAction("✨ 召唤到此处", self.menu)
        self.summon_action.setToolTip("在屏幕上标记位置，鸟会飞过去")
        self.summon_action.triggered.connect(self._start_mark_mode)
        self.menu.addAction(self.summon_action)
        
        self.menu.addSeparator()
        
        # 笼子切换
        self.toggle_cage_action = QAction("🐦 打开笼子 / 唤回小鸟", self.menu)
        self.toggle_cage_action.triggered.connect(self._on_toggle_cage)
        self.menu.addAction(self.toggle_cage_action)
        
        self.menu.addSeparator()
        
        # 退出
        self.quit_action = QAction("👋 退出", self.menu)
        self.quit_action.triggered.connect(self._on_quit)
        self.menu.addAction(self.quit_action)
        
        self.setContextMenu(self.menu)
        
        # 支持左键双击动作
        self.activated.connect(self._on_activated)
        
        # 注册应用内快捷键 (当应用有焦点时有效)
        # 注意：真正的全局热键需要平台特定实现
        self._setup_shortcuts()
    
    def _setup_shortcuts(self):
        """设置快捷键"""
        # 注意：Qt QShortcut 只在窗口有焦点时有效
        # 真正的全局热键需要 pynput 或系统 API
        # 这里仅作占位，实际功能通过托盘菜单触发
        pass
    
    def _start_mark_mode(self):
        """开始标记模式"""
        self._shortcut_manager.start_mark_mode()
    
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
