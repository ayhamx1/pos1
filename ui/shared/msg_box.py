# ui/shared/msg_box.py

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from app.config.settings import MODERN_STYLE

class SystemMessageBox(QDialog):
    def __init__(self, text, icon_type="info", parent=None):
        super().__init__(parent)
        self.setFixedSize(420, 160)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        container_layout = QVBoxLayout(self); container_layout.setContentsMargins(0, 0, 0, 0)
        main_frame = QFrame(); main_frame.setObjectName("mainFrame"); main_frame.setStyleSheet(MODERN_STYLE)
        frame_layout = QVBoxLayout(main_frame); frame_layout.setContentsMargins(20, 20, 20, 15); frame_layout.setSpacing(15)
        
        content_layout = QHBoxLayout(); content_layout.setSpacing(15)
        self.lbl_icon = QLabel(); self.lbl_icon.setFont(QFont("Segoe UI", 26)); self.lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if icon_type == "success": self.lbl_icon.setText("✅")
        elif icon_type == "warning": self.lbl_icon.setText("⚠️")
        elif icon_type == "error": self.lbl_icon.setText("❌")
        elif icon_type == "question": self.lbl_icon.setText("❓")
        else: self.lbl_icon.setText("ℹ️")
            
        self.lbl_text = QLabel(text); self.lbl_text.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium)); self.lbl_text.setWordWrap(True)
        content_layout.addWidget(self.lbl_icon, stretch=1); content_layout.addWidget(self.lbl_text, stretch=5)
        frame_layout.addLayout(content_layout, stretch=3)
        
        btn_layout = QHBoxLayout(); btn_layout.addStretch()
        if icon_type == "question":
            self.btn_yes = QPushButton("نعم"); self.btn_yes.clicked.connect(self.accept)
            self.btn_no = QPushButton("لا"); self.btn_no.clicked.connect(self.reject)
            btn_layout.addWidget(self.btn_yes); btn_layout.addWidget(self.btn_no)
        else:
            self.btn_ok = QPushButton("موافق"); self.btn_ok.clicked.connect(self.accept)
            btn_layout.addWidget(self.btn_ok)
        btn_layout.addStretch(); frame_layout.addLayout(btn_layout, stretch=1)
        container_layout.addWidget(main_frame)

    @staticmethod
    def show_info(parent, text): return SystemMessageBox(text, "info", parent).exec()
    @staticmethod
    def show_success(parent, text): return SystemMessageBox(text, "success", parent).exec()
    @staticmethod
    def show_warning(parent, text): return SystemMessageBox(text, "warning", parent).exec()
    @staticmethod
    def show_critical(parent, text): return SystemMessageBox(text, "error", parent).exec()
    @staticmethod
    def show_question(parent, text): return SystemMessageBox(text, "question", parent).exec()