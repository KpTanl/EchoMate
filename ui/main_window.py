import os
from datetime import datetime
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QGroupBox, QTextEdit
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QMovie, QPixmap
from PySide6.QtCore import Qt, QSize, QTimer
import glob
import random
from core.event_bus import event_bus
from ui.settings_dialog import SettingsDialog
from ui.mark_mode_overlay import MarkModeOverlay

class MainWindow(QMainWindow):
    """
    笼子（主窗口），包含宠物展示区。配置区已移至独立弹窗。
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EchoMate - 鸟笼")
        self.resize(400, 500)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.current_movie = None
        self.current_action = "sleeping"
        
        # 每10~30秒随机切换一次同动作图片的定时器
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._on_anim_timeout)
        
        # 主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FAFAFA;
            }
            QGroupBox {
                border: 2px solid #DCDCDC;
                border-radius: 8px;
                margin-top: 25px;
                padding-top: 15px;
                font-weight: bold;
                color: #555555;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0px 8px;
                top: 5px;
                background-color: transparent;
            }
            QPushButton {
                background-color: #E0F2F1;
                border: 1px solid #B2DFDB;
                border-radius: 6px;
                padding: 6px;
                color: #00695C;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #B2DFDB;
            }
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 4px;
                background-color: #FFFFFF;
            }
        """)
        
        self.cage_group = QGroupBox()
        self.cage_layout = QVBoxLayout(self.cage_group)
        
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(200, 200)
        self.cage_layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        
        # 按钮容器
        self.btn_layout = QHBoxLayout()
        self.fly_btn = QPushButton("🐦 放飞小鸟")
        self.fly_btn.clicked.connect(self._on_fly_clicked)
        self.btn_layout.addWidget(self.fly_btn)
        
        # 召唤按钮（鸟放出后才可用）
        self.summon_btn = QPushButton("✨ 召唤到此处")
        self.summon_btn.clicked.connect(self._on_summon_clicked)
        self.summon_btn.setEnabled(False)  # 初始禁用，鸟在笼子里
        self.summon_btn.setToolTip("鸟飞出笼子后，点击在屏幕上标记位置")
        self.btn_layout.addWidget(self.summon_btn)
        
        self.settings_btn = QPushButton("⚙️ 设置")
        self.settings_btn.clicked.connect(self._on_settings_clicked)
        self.btn_layout.addWidget(self.settings_btn)
        self.cage_layout.addLayout(self.btn_layout)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        # 增加一些样式
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF; 
                padding: 10px; 
                border: 1px solid #EEEEEE;
                border-radius: 8px;
                color: #333333;
            }
        """)
        self.cage_layout.addWidget(self.chat_display, stretch=1)
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("和鸟儿打个招呼...")
        self.chat_input.returnPressed.connect(self._on_send_msg)
        self.cage_layout.addWidget(self.chat_input)
        
        self.main_layout.addWidget(self.cage_group, stretch=1)
        
        # 记录形态
        self.is_bird_in_cage = True
        
        # 初始加载占位状态
        self._load_image("sleeping")
        
        # 监听事件
        event_bus.on_toggle_cage.connect(self._on_toggle_cage_signal)
        event_bus.on_agent_response.connect(self._on_agent_reply)
        event_bus.on_state_change.connect(self._on_state_change)
        
    def _on_anim_timeout(self):
        # 定时器触发，重新加载当前动作的可能另一张图
        if self.is_bird_in_cage:
            self._load_image(self.current_action)

    def _load_image(self, state="sleeping"):
        self.current_action = state
        
        # 额度限制期间，把 happy 和 angry 映射到已有的闲置和好奇图片上
        display_state = state
        if state == "happy": display_state = "sleeping"
        elif state == "angry": display_state = "curious"
        
        base_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'parrot', 'Peach-faced-lovebird')
        pattern = os.path.join(base_dir, f"Peach-faced-lovebird_{display_state}_*.png")
        
        matched_files = glob.glob(pattern)
        
        target_path = None
        if matched_files:
            target_path = random.choice(matched_files)
        else:
            # 兼容旧路径
            gif_path = os.path.join(os.path.dirname(__file__), '..', 'assets', f"parrot_{display_state}.gif")
            png_path = os.path.join(os.path.dirname(__file__), '..', 'assets', f"parrot_{display_state}.png")
            target_path = gif_path if os.path.exists(gif_path) else png_path if os.path.exists(png_path) else None
        
        if target_path:
            if target_path.endswith('.gif'):
                if self.current_movie:
                    self.current_movie.stop()
                    
                self.current_movie = QMovie(target_path)
                self.current_movie.setScaledSize(QSize(200, 200))
                self.image_label.setMovie(self.current_movie)
                self.current_movie.start()
            else:
                if self.current_movie:
                    self.current_movie.stop()
                    self.current_movie = None
                pixmap = QPixmap(target_path)
                pixmap = pixmap.scaledToWidth(200, Qt.SmoothTransformation) 
                self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("小鸟图片未找到")
            
        # 重新设定下一次轮换的时间，10~30秒
        self.anim_timer.start(random.randint(10000, 30000))
            
    def _on_state_change(self, state_data: dict):
        action = state_data.get("action", "sleeping")
        in_cage = state_data.get("in_cage", True)
        
        if in_cage:
            self._load_image(action)
            
    def _on_fly_clicked(self):
        if self.is_bird_in_cage:
            event_bus.on_toggle_cage.emit(False)
        else:
            event_bus.on_toggle_cage.emit(True)
            
    def _on_settings_clicked(self):
        dialog = SettingsDialog(self)
        dialog.exec()
        
    def _on_toggle_cage_signal(self, show_cage: bool):
        self.is_bird_in_cage = show_cage
        if show_cage:
            self.show()
            self.raise_()
            self.activateWindow()
            self.image_label.show()
            self.fly_btn.setText("🐦 放飞小鸟")
            self.summon_btn.setEnabled(False)  # 鸟在笼子里，禁用召唤
            self._load_image(self.current_action) # 恢复展示时重新激活内部逻辑
        else:
            self.image_label.hide()
            self.fly_btn.setText("🏠 把鸟儿唤回笼子")
            self.summon_btn.setEnabled(True)  # 鸟飞出去了，启用召唤
            self.anim_timer.stop() # 离开笼子时关闭动画，由 pet window 接管
            
    def _on_send_msg(self):
        text = self.chat_input.text().strip()
        if text:
            # 用户正常输入时才上屏，隐藏指令不上屏
            if not text.startswith("[系统秘密提示："):
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                self.chat_display.append(f"<span style='color:#999;font-size:10px;'>[{timestamp}]</span> <b>你:</b> {text}")
            self.chat_input.clear()
            event_bus.on_user_input.emit(text)

    def _on_agent_reply(self, reply: str):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.chat_display.append(f"<span style='color:#999;font-size:10px;'>[{timestamp}]</span> <b>鸟儿:</b> {reply}<br>")
    
    def _on_summon_clicked(self):
        """点击召唤按钮，进入标记模式"""
        if self.is_bird_in_cage:
            return
        
        print("[MainWindow] 开始标记模式...")
        
        # 先隐藏主窗口避免遮挡
        self.hide()
        
        # 创建标记覆盖层
        self._overlay = MarkModeOverlay(self)
        self._overlay.position_marked.connect(self._on_position_marked)
        self._overlay.cancelled.connect(self._on_mark_cancelled)
        self._overlay.show()
        self._overlay.raise_()
        self._overlay.activateWindow()
        
        # 发射信号
        event_bus.on_mark_mode_start.emit()
    
    def _on_position_marked(self, pos):
        """位置被标记"""
        print(f"[MainWindow] 标记位置: {pos}")
        event_bus.on_destination_set.emit(pos)
        self._overlay = None
        # 重新显示主窗口
        self.show()
    
    def _on_mark_cancelled(self):
        """用户取消标记"""
        print("[MainWindow] 标记取消")
        self._overlay = None
        # 重新显示主窗口
        self.show()
