import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                               QLineEdit, QTextEdit, QPushButton, QLabel, QGroupBox, QFrame)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt
from core.config import config

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EchoMate - 偏好与档案设置")
        self.resize(500, 600)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # --- Top Area: Image and Profile ---
        self.profile_group = QGroupBox("小鸟档案 (系统预设不可修改)")
        self.profile_group.setStyleSheet("QGroupBox { font-size: 14px; font-weight: bold; color: #00695C; }")
        self.profile_layout = QHBoxLayout(self.profile_group)
        
        # Image
        self.image_layout = QVBoxLayout()
        self.image_label = QLabel()
        # use UI asset or fallback
        img_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'parrot', 'Peach-faced-lovebird', 'Peach-faced-lovebird_idle_01.png')
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path).scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
            self.image_label.setAlignment(Qt.AlignCenter)
        else:
            self.image_label.setText("🐥")
            self.image_label.setAlignment(Qt.AlignCenter)
            font = QFont()
            font.setPointSize(48)
            self.image_label.setFont(font)
            
        self.image_label.setFixedSize(150, 150)
        self.image_label.setStyleSheet("background-color: #E0F2F1; border-radius: 15px; border: 2px solid #80CBC4;")
        self.image_layout.addWidget(self.image_label)
        self.image_layout.setAlignment(Qt.AlignCenter)
        self.profile_layout.addLayout(self.image_layout)
        
        # Profile Data (Read-only)
        self.profile_form = QFormLayout()
        self.profile_form.setSpacing(10)
        
        self.gender_lbl = QLabel(config.pet_gender)
        self.birthday_lbl = QLabel(config.pet_birthday)
        self.likes_lbl = QLabel(config.pet_likes)
        self.likes_lbl.setWordWrap(True)
        self.dislikes_lbl = QLabel(config.pet_dislikes)
        self.dislikes_lbl.setWordWrap(True)
        self.info_lbl = QLabel(config.pet_info)
        self.info_lbl.setWordWrap(True)
        
        # styling dynamic profile content
        for lbl in [self.gender_lbl, self.birthday_lbl, self.likes_lbl, self.dislikes_lbl, self.info_lbl]:
            lbl.setStyleSheet("color: #4A4A4A; font-weight: normal; font-size: 13px;")
            
        self.profile_form.addRow(self._bold_label("性别:"), self.gender_lbl)
        self.profile_form.addRow(self._bold_label("生日:"), self.birthday_lbl)
        self.profile_form.addRow(self._bold_label("喜欢:"), self.likes_lbl)
        self.profile_form.addRow(self._bold_label("讨厌:"), self.dislikes_lbl)
        self.profile_form.addRow(self._bold_label("性格:"), self.info_lbl)
        
        self.profile_layout.addLayout(self.profile_form)
        self.profile_layout.setStretch(1, 1)
        
        self.main_layout.addWidget(self.profile_group)
        self.main_layout.addStretch(1) # Add a little space
        
        # --- Bottom Area: Editable Config ---
        self.settings_group = QGroupBox("自定义设置与模型配置")
        self.settings_group.setStyleSheet("QGroupBox { font-size: 14px; font-weight: bold; color: #E65100; }")
        self.settings_layout = QFormLayout(self.settings_group)
        self.settings_layout.setSpacing(12)
        
        self.pet_name_input = QLineEdit(config.pet_name)
        self.pet_name_input.setPlaceholderText("给你的小鸟起个名字吧")
        self.api_url_input = QLineEdit(config.api_base_url)
        self.api_key_input = QLineEdit(config.api_key)
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.model_input = QLineEdit(config.model_name)
        
        self.settings_layout.addRow(self._bold_label("宠物名称:"), self.pet_name_input)
        self.settings_layout.addRow(self._bold_label("API Base URL:"), self.api_url_input)
        self.settings_layout.addRow(self._bold_label("API Key:"), self.api_key_input)
        self.settings_layout.addRow(self._bold_label("Model Name:"), self.model_input)
        
        self.main_layout.addWidget(self.settings_group)
        
        self.main_layout.addStretch(1)
        
        # --- Save Button ---
        self.save_btn = QPushButton("保存设置并返回")
        self.save_btn.clicked.connect(self._on_save_config)
        self.save_btn.setMinimumHeight(45)
        self.save_btn.setCursor(Qt.PointingHandCursor)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addStretch()
        
        self.main_layout.addLayout(btn_layout)
        
        # Global Stylesheet
        self.setStyleSheet("""
            QDialog {
                background-color: #F9FBE7; /* a very light yellow/green hue */
            }
            QGroupBox {
                border: 2px solid #C5E1A5;
                border-radius: 10px;
                margin-top: 25px;
                background-color: #FFFFFF;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                top: 5px;
                padding: 0px 8px;
                background-color: transparent;
            }
            QPushButton {
                background-color: #7CB342;
                border: none;
                border-radius: 22px;
                padding: 10px 50px;
                color: white;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #689F38;
            }
            QPushButton:pressed {
                background-color: #558B2F;
            }
            QLineEdit {
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px;
                background-color: #FAFAFA;
                color: #333333;
                selection-background-color: #AED581;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #8BC34A;
                background-color: #FFFFFF;
            }
        """)

    def _bold_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("font-weight: bold; color: #333333; font-size: 13px;")
        return lbl

    def _on_save_config(self):
        config.pet_name = self.pet_name_input.text().strip()
        config.api_base_url = self.api_url_input.text().strip()
        config.api_key = self.api_key_input.text().strip()
        config.model_name = self.model_input.text().strip()
        config.save()
        self.accept()
