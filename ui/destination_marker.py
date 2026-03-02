"""
目的地标记组件
显示一个带有脉冲动画的现代化标记
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QPoint, QSize
from PySide6.QtGui import QPainter, QColor, QRadialGradient, QPen, QBrush
import math


class DestinationMarker(QWidget):
    """
    现代化脉冲标记
    - 外圈呼吸动画
    - 中心实心点
    - 自动淡出消失
    """
    
    def __init__(self, position: QPoint, parent=None):
        super().__init__(parent)
        
        # 标记大小
        self.marker_size = 60
        self.setFixedSize(self.marker_size, self.marker_size)
        
        # 移动到指定位置（中心对齐）
        self.move(position.x() - self.marker_size // 2, 
                  position.y() - self.marker_size // 2)
        
        # 窗口设置：无边框、透明、置顶
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.WindowTransparentForInput  # 不拦截鼠标事件
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        # 动画参数
        self.pulse_phase = 0.0  # 脉冲相位 0-2π
        self.pulse_speed = 0.15  # 脉冲速度
        self.opacity = 1.0
        
        # 配色 - 活力橙
        self.primary_color = QColor("#FF6B35")
        self.glow_color = QColor("#FFAA00")
        
        # 动画定时器
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._update_animation)
        self.anim_timer.start(33)  # ~30fps
        
        # 消失定时器（90秒）
        self.fade_timer = QTimer(self)
        self.fade_timer.setSingleShot(True)
        self.fade_timer.timeout.connect(self._start_fade_out)
        
    def _update_animation(self):
        """更新脉冲动画"""
        self.pulse_phase += self.pulse_speed
        if self.pulse_phase > math.pi * 2:
            self.pulse_phase -= math.pi * 2
        self.update()
    
    def _start_fade_out(self):
        """开始淡出"""
        self.fade_anim_timer = QTimer(self)
        self.fade_anim_timer.timeout.connect(self._fade_step)
        self.fade_anim_timer.start(33)
    
    def _fade_step(self):
        """淡出步骤"""
        self.opacity -= 0.05
        if self.opacity <= 0:
            self.close()
        else:
            self.update()
    
    def start_countdown(self, milliseconds: int = 90000):
        """启动倒计时，时间到后自动消失"""
        self.fade_timer.start(milliseconds)
    
    def dismiss(self):
        """立即消失"""
        self.fade_timer.stop()
        self._start_fade_out()
    
    def closeEvent(self, event):
        """关闭时停止所有定时器"""
        self.anim_timer.stop()
        self.fade_timer.stop()
        if hasattr(self, 'fade_anim_timer'):
            self.fade_anim_timer.stop()
        super().closeEvent(event)
    
    def paintEvent(self, event):
        """绘制脉冲标记"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = self.rect().center()
        base_radius = 8  # 中心点半径
        
        # 计算脉冲大小 (0.5 ~ 1.5 倍)
        pulse_scale = 1.0 + 0.5 * math.sin(self.pulse_phase)
        
        # 绘制外圈脉冲波
        outer_radius = base_radius * 2.5 * pulse_scale
        outer_opacity = int(150 * (1.0 - (pulse_scale - 1.0)) * self.opacity)
        
        if outer_opacity > 0:
            pulse_gradient = QRadialGradient(center, outer_radius)
            pulse_gradient.setColorAt(0, QColor(self.primary_color.red(), 
                                                 self.primary_color.green(), 
                                                 self.primary_color.blue(), 
                                                 outer_opacity))
            pulse_gradient.setColorAt(0.5, QColor(self.glow_color.red(), 
                                                  self.glow_color.green(), 
                                                  self.glow_color.blue(), 
                                                  outer_opacity // 2))
            pulse_gradient.setColorAt(1, QColor(self.primary_color.red(), 
                                                 self.primary_color.green(), 
                                                 self.primary_color.blue(), 
                                                 0))
            
            painter.setBrush(QBrush(pulse_gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center, int(outer_radius), int(outer_radius))
        
        # 绘制中间环
        mid_radius = base_radius * 1.6
        mid_opacity = int(200 * self.opacity)
        painter.setBrush(Qt.NoBrush)
        pen = QPen(QColor(self.primary_color.red(), 
                          self.primary_color.green(), 
                          self.primary_color.blue(), 
                          mid_opacity))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawEllipse(center, int(mid_radius), int(mid_radius))
        
        # 绘制中心实心圆（带光晕）
        glow_radius = base_radius * 1.3
        glow_gradient = QRadialGradient(center, glow_radius)
        glow_gradient.setColorAt(0, QColor(self.glow_color.red(), 
                                            self.glow_color.green(), 
                                            self.glow_color.blue(), 
                                            int(255 * self.opacity)))
        glow_gradient.setColorAt(0.7, QColor(self.primary_color.red(), 
                                              self.primary_color.green(), 
                                              self.primary_color.blue(), 
                                              int(200 * self.opacity)))
        glow_gradient.setColorAt(1, QColor(self.primary_color.red(), 
                                            self.primary_color.green(), 
                                            self.primary_color.blue(), 
                                            0))
        
        painter.setBrush(QBrush(glow_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, int(glow_radius), int(glow_radius))
        
        # 绘制中心核心点
        core_opacity = int(255 * self.opacity)
        painter.setBrush(QBrush(QColor(255, 255, 255, core_opacity)))
        painter.drawEllipse(center, int(base_radius * 0.5), int(base_radius * 0.5))
