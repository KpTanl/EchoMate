"""
标记模式覆盖层
全屏透明窗口，用于捕获用户点击的坐标位置
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QCursor, QKeyEvent, QMouseEvent


class MarkModeOverlay(QWidget):
    """
    全屏透明覆盖层，进入标记模式后:
    1. 鼠标变为十字准星
    2. 点击任意位置发射坐标信号
    3. 按 ESC 取消
    """
    
    position_marked = Signal(QPoint)  # 用户点击的位置（全局坐标）
    cancelled = Signal()               # 用户取消
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置全屏、透明、无边框、置顶
        # 注意：不使用 Qt.Tool，确保在所有 Windows 系统上正常显示
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint |
            Qt.Window
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        
        # 设置全屏大小
        screen = self.screen()
        if screen:
            self.setGeometry(screen.geometry())
        
        # 设置鼠标为十字准星
        self.setCursor(Qt.CrossCursor)
        
        # 捕获所有鼠标事件
        self.setMouseTracking(True)
        
    def showEvent(self, event):
        """显示时确保全屏并置顶激活"""
        super().showEvent(event)
        screen = self.screen()
        if screen:
            self.setGeometry(screen.geometry())
        
        # 确保窗口在最前面并获取焦点
        self.raise_()
        self.activateWindow()
        
        # 强制重绘确保透明背景正确
        self.update()
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标点击 - 发射坐标并关闭"""
        if event.button() == Qt.LeftButton:
            global_pos = event.globalPosition().toPoint()
            self.position_marked.emit(global_pos)
            self.close()
        event.accept()
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """双击也触发标记"""
        if event.button() == Qt.LeftButton:
            global_pos = event.globalPosition().toPoint()
            self.position_marked.emit(global_pos)
            self.close()
        event.accept()
    
    def keyPressEvent(self, event: QKeyEvent):
        """ESC 键取消"""
        if event.key() == Qt.Key_Escape:
            self.cancelled.emit()
            self.close()
        event.accept()
    
    def paintEvent(self, event):
        """绘制半透明背景，让用户知道标记模式已启动"""
        from PySide6.QtGui import QPainter, QColor, QBrush
        painter = QPainter(self)
        # 非常淡的黑色遮罩，让用户知道这是标记模式
        painter.setBrush(QBrush(QColor(0, 0, 0, 10)))  # 半透明
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())
    
    def closeEvent(self, event):
        """关闭时恢复默认鼠标样式"""
        self.unsetCursor()
        super().closeEvent(event)
