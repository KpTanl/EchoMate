import os
import time
import math
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PySide6.QtCore import Qt, QPoint, QSize, QTimer
from PySide6.QtGui import QMovie, QPixmap, QTransform
import glob
import random
from core.event_bus import event_bus

class PetWindow(QWidget):
    """
    主宠物窗口：无边框、透明、可拖拽
    只负责展示逻辑，状态受上层 StateManager 控制
    """
    def __init__(self):
        super().__init__()
        
        # 1. 设置无边框、工具窗口（不在任务栏显示）、透明背景、置顶
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.ToolTip
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # 2. 准备 UI 布局
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # 用 QLabel 承载图片/动画
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)
        
        # 存储当前的 QMovie 示例以防止被回收
        self.current_movie = None
        self.current_action = "flying"
        
        # 鸟的面朝方向，假设原图面朝左
        self._face_left = True
        
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._on_anim_timeout)
        
        # 增加漫游飞行相关定时器及状态
        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self._update_auto_move)
        
        self.roam_timer = QTimer(self)
        self.roam_timer.timeout.connect(self._start_new_roam)
        self.roam_timer.setSingleShot(True)
        
        self._is_auto_moving = False
        self._target_pos = None
        self._start_pos = None
        self._flight_start_time = 0
        self._flight_duration = 0
        
        # 提前缓存并加载飞行连贯帧
        self._flying_frames_cache = []
        self._fly_frame_index = 0
        self._preload_flying_frames()
        
        # 3. 加载占位符图像
        self._load_image()
        
        # 4. 拖拽与抚摸状态变量
        self._drag_pos = None
        self._click_time = 0
        
        self.setMouseTracking(True)
        self.image_label.setMouseTracking(True)
        self._rub_distance = 0
        self._last_rub_pos = None
        self._last_rub_time = 0

        # 5. 初始不显示（默认在笼子里）
        self.hide()
        
        # 监听统一下发的 state 更新
        event_bus.on_state_change.connect(self._on_state_change)

    def _preload_flying_frames(self):
        base_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'parrot', 'Peach-faced-lovebird', 'flying_frames')
        if not os.path.exists(base_dir):
            return
            
        # 主人指定的自定义的展翅顺序：01 -> 03 -> 04 -> 02 -> 05 -> 02 -> 04 -> 03 -> 01
        custom_sequence = ["01", "03", "04", "02", "05", "02", "04", "03", "01"]
        
        for suffix in custom_sequence:
            f = os.path.join(base_dir, f"Peach-faced-lovebird_flying_{suffix}.png")
            if os.path.exists(f):
                pixmap = QPixmap(f)
                if not pixmap.isNull():
                    smoothed = pixmap.scaledToWidth(150, Qt.SmoothTransformation)
                    self._flying_frames_cache.append(smoothed)

    def _on_anim_timeout(self):
        # 仅当处于显示状态时切换
        if not self.isHidden():
            self._load_image(self.current_action)

    def _load_image(self, state="flying"):
        self.current_action = state
        
        display_state = state
        if state == "happy": display_state = "sleeping"
        elif state == "angry": display_state = "curious"
        
        # === 针对 flying 的新缓存逻辑 ===
        if display_state == "flying" and self._flying_frames_cache:
            if self.current_movie:
                self.current_movie.stop()
                self.current_movie = None
                
            # 从内存拿
            pixmap = self._flying_frames_cache[self._fly_frame_index]
            if not self._face_left:
                pixmap = pixmap.transformed(QTransform().scale(-1, 1))
            self.image_label.setPixmap(pixmap)
            self.resize(150, 150)
            
            # 索引累加
            self._fly_frame_index = (self._fly_frame_index + 1) % len(self._flying_frames_cache)
            
            # 固定动画频率
            self.anim_timer.start(200)
            return

        base_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'parrot', 'Peach-faced-lovebird')
        pattern = os.path.join(base_dir, f"Peach-faced-lovebird_{display_state}_*.png")
        matched_files = glob.glob(pattern)
        
        target_path = None
        if matched_files:
            target_path = random.choice(matched_files)
        else:
            gif_path = os.path.join(os.path.dirname(__file__), '..', 'assets', f"parrot_{display_state}.gif")
            png_path = os.path.join(os.path.dirname(__file__), '..', 'assets', f"parrot_{display_state}.png")
            target_path = gif_path if os.path.exists(gif_path) else png_path if os.path.exists(png_path) else None
        
        if target_path:
            if target_path.endswith('.gif'):
                if self.current_movie:
                    self.current_movie.stop()
                    
                self.current_movie = QMovie(target_path)
                
                # 使用 scaledSize 缩放 Movie
                # 原始大小如果过大需要适配
                self.current_movie.setScaledSize(QSize(150, 150))
                
                self.image_label.setMovie(self.current_movie)
                self.current_movie.start()
            else:
                if self.current_movie:
                    self.current_movie.stop()
                    self.current_movie = None
                    
                pixmap = QPixmap(target_path)
                pixmap = pixmap.scaledToWidth(150, Qt.SmoothTransformation) 
                
                # 如果根据寻路方向发现需要面朝右，就水平翻转
                if not self._face_left:
                    pixmap = pixmap.transformed(QTransform().scale(-1, 1))
                    
                self.image_label.setPixmap(pixmap)
                
            self.resize(150, 150)
        else:
            self.image_label.setText("Image Not Found")
            self.image_label.setStyleSheet("color: red; background: rgba(0,0,0,100); padding: 10px;")
            
        if self.current_action == "flying":
            # 飞行时需要较快的动画切帧频率产生拍动翅膀的效果（约100~300ms）。此为未缓存情况下的降级兼容逻辑
            self.anim_timer.start(random.randint(150, 250))
        else:
            # 休息或静止状态下则很久才换一次小动作
            self.anim_timer.start(random.randint(5000, 15000))

    def _on_state_change(self, state_data: dict):
        action = state_data.get("action", "flying")
        in_cage = state_data.get("in_cage", True)
        
        if in_cage:
            self.hide()
            self.anim_timer.stop()
            self.move_timer.stop()
            self.roam_timer.stop()
            self._is_auto_moving = False
        else:
            self._is_auto_moving = False
            self._load_image(action)
            self.show()
            # 刚放出笼子时，延迟一段时间起飞
            self.roam_timer.start(random.randint(2000, 5000))

    def _start_new_roam(self):
        screen_geo = QApplication.primaryScreen().geometry()
        max_x = screen_geo.width() - self.width()
        max_y = screen_geo.height() - self.height()
        
        if max_x <= 0 or max_y <= 0:
            return
            
        # 智能寻路：偏好屏幕底部或左右边缘
        edge_choice = random.choice(["bottom", "left", "right", "random", "random"])
        
        if edge_choice == "bottom":
            target_x = random.randint(0, max_x)
            target_y = random.randint(int(max_y * 0.8), max_y)
        elif edge_choice == "left":
            target_x = random.randint(0, 100)
            target_y = random.randint(0, max_y)
        elif edge_choice == "right":
            target_x = random.randint(max_x - 100, max_x)
            target_y = random.randint(0, max_y)
        else:
            target_x = random.randint(0, max_x)
            target_y = random.randint(0, max_y)
            
        self._target_pos = QPoint(target_x, target_y)
        self._start_pos = self.pos()
        
        # 计算距离和用时
        dist_x = target_x - self._start_pos.x()
        dist_y = target_y - self._start_pos.y()
        distance = math.hypot(dist_x, dist_y)
        
        if distance < 50:
            # 如果随机到的距离太短，直接休息
            self.roam_timer.start(random.randint(5000, 15000))
            return

        # 速度：大约 400 像素/秒
        speed = 400.0  
        self._flight_duration = (distance / speed)
        
        # 记录本次飞行的弧度高度，让鸟儿呈抛物线飞行
        self._arc_height = distance * random.uniform(0.1, 0.25)
        
        # 判断朝向 (假设原图面朝左，如果 dist_x > 0 则为向右飞，需要翻转)
        self._face_left = (dist_x <= 0)
        
        self._is_auto_moving = True
        self._flight_start_time = time.time()
        
        # 强制切换到飞行并重新加载图像翻转状态
        self._load_image("flying")
        
        # 以 ~30 FPS 刷新
        self.move_timer.start(33)

    def _update_auto_move(self):
        if not self._is_auto_moving or self._target_pos is None or self._start_pos is None:
            self.move_timer.stop()
            return
            
        elapsed = time.time() - self._flight_start_time
        if self._flight_duration <= 0:
            progress = 1.0
        else:
            progress = elapsed / self._flight_duration
            
        if progress >= 1.0:
            progress = 1.0
            self.move_timer.stop()
            self._is_auto_moving = False
            self.move(self._target_pos)
            
            # 到达目标后休息，面朝屏幕内部的话更有互动感
            screen_geo = QApplication.primaryScreen().geometry()
            center_x = screen_geo.width() / 2.0
            self._face_left = (self.pos().x() > center_x)
            
            rest_action = random.choice(["idle", "sleeping", "curious"])
            self._load_image(rest_action)
            
            # 开启下一次漫游倒计时（5~15秒）
            self.roam_timer.start(random.randint(5000, 15000))
        else:
            # Ease in out 缓动函数 (Sine)
            eased_progress = -(math.cos(math.pi * progress) - 1.0) / 2.0
            
            base_x = self._start_pos.x() + (self._target_pos.x() - self._start_pos.x()) * eased_progress
            base_y = self._start_pos.y() + (self._target_pos.y() - self._start_pos.y()) * eased_progress
            
            # 添加鸟类飞行的弧度 (向上抛物线/正弦波，即负向 y 轴延伸)
            arc_offset_y = -math.sin(progress * math.pi) * getattr(self, '_arc_height', 0)
            
            # 模拟扑翼时候产生的上下微微沉浮（高频小幅度的正弦波）
            flap_offset_y = math.sin(elapsed * math.pi * 5) * 8
            
            new_x = base_x
            new_y = base_y + arc_offset_y + flap_offset_y
            self.move(int(new_x), int(new_y))

    # ==========================
    # 鼠标事件实现随意拖拽与反馈
    # ==========================
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 中断当前的所有漫游和自动飞行动作
            self.move_timer.stop()
            self.roam_timer.stop()
            if self._is_auto_moving:
                self._is_auto_moving = False
                self._load_image(random.choice(["idle", "curious"]))
                
            # 记录鼠标按下时相对窗口的位置
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._click_time = time.time()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            new_pos = event.globalPosition().toPoint() - self._drag_pos
            
            # 屏幕边界检测，防止飞出屏幕外
            screen_geo = QApplication.primaryScreen().geometry()
            max_x = screen_geo.width() - self.width()
            max_y = screen_geo.height() - self.height()
            
            # 限制范围
            new_x = max(0, min(new_pos.x(), max_x))
            new_y = max(0, min(new_pos.y(), max_y))
            
            self.move(new_x, new_y)
            event.accept()
        elif event.buttons() == Qt.NoButton:
            # 鼠标在没有按键按下的情况下滑动 (Hover)，积攒抚摸距离
            current_pos = event.globalPosition().toPoint()
            current_time = time.time()
            
            if self._last_rub_pos is not None:
                # 如果鼠标停顿间隔时间太长，说明是不连贯的动作，清空累计距离
                if current_time - self._last_rub_time < 0.5:
                    dist = (current_pos - self._last_rub_pos).manhattanLength()
                    self._rub_distance += dist
                    
                    if self._rub_distance > 500: # 累计连续滑动 500 像素即可触发抚摸效果
                        event_bus.on_pet_rubbed.emit()
                        self._rub_distance = 0 # 触发后重新累加
                else:
                    self._rub_distance = 0
            
            self._last_rub_pos = current_pos
            self._last_rub_time = current_time
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 如果按下的时间小于 0.2 秒，视为单纯的点击，产生交互反馈
            if time.time() - self._click_time < 0.2:
                # 只往上抛事件，不更改状态，由 state_manager 接管
                event_bus.on_pet_clicked.emit()
            self._drag_pos = None
            
            if not self.isHidden():
                # 松开鼠标后，重新启动漫游定时器，让鸟在一段随机时间后自行探索
                self.roam_timer.start(random.randint(3000, 8000))
                
            event.accept()

    def leaveEvent(self, event):
        # 鼠标离开窗口，重置抚摸状态
        self._rub_distance = 0
        self._last_rub_pos = None
        event.accept()

