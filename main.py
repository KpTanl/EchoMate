import sys
import os
from PySide6.QtWidgets import QApplication

def main():
    # 确保运行路径正确
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    app = QApplication(sys.argv)
    
    # 防止关闭所有窗口时自动退出（因为我们有托盘常驻）
    app.setQuitOnLastWindowClosed(False)
    
    # 实例化并挂载各个核心组件
    from core.app import app_manager
    app_manager.start()
    
    # 实例化系统托盘
    from ui.tray_menu import AppTrayIcon
    tray_icon = AppTrayIcon()
    tray_icon.show()

    # 实例化主窗口 (笼子)
    from ui.main_window import MainWindow
    main_win = MainWindow()
    
    # 实例化放飞模式窗口
    from ui.pet_window import PetWindow
    pet_win = PetWindow()
    
    # 默认展示笼子
    main_win.show()
    
    print("EchoMate 开始运行...")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
