import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QGroupBox, QVBoxLayout, QWidget, QLabel

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(300, 200)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FAFAFA;
            }
            QGroupBox {
                border: 2px solid #DCDCDC;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                font-weight: bold;
                color: #555555;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #FAFAFA;
            }
        """)
        
        w = QWidget()
        self.setCentralWidget(w)
        layout = QVBoxLayout(w)
        
        gb = QGroupBox("✦ 鸟笼状态 ✦")
        l = QVBoxLayout(gb)
        l.addWidget(QLabel("test"))
        
        layout.addWidget(gb)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TestWindow()
    w.show()
    # 截图或直接保留运行给用户看？
    # 我这里无法看到GUI，但我可以改样式
    QTimer.singleShot(1000, app.quit)
    sys.exit(app.exec())
