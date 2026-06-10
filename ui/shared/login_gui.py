# ui/shared/login_gui.py

import sys
import os

# حل مشكلة المسارات تلقائياً
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import psycopg2
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QFormLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.config.settings import DB_PARAMS, MODERN_STYLE
from ui.shared.msg_box import SystemMessageBox

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تسجيل الدخول - نظام إدارة السوبرماركت")
        self.setFixedSize(450, 500)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(MODERN_STYLE)
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 40, 30, 40)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        card_frame = QFrame()
        card_frame.setObjectName("loginCard")
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(25, 30, 25, 30)
        card_layout.setSpacing(15)
        
        lbl_logo = QLabel("🛒")
        lbl_logo.setFont(QFont("Segoe UI", 40))
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(lbl_logo)
        
        lbl_title = QLabel("تسجيل دخول الموظفين")
        lbl_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #1e5378;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(lbl_title)
        card_layout.addSpacing(10)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("اكتب اسم المستخدم...")
        self.txt_username.setFixedHeight(40)
        
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("اكتب كلمة المرور...")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setFixedHeight(40)
        self.txt_password.returnPressed.connect(self.handle_login) 
        
        form_layout.addRow(QLabel("اسم المستخدم:"), self.txt_username)
        form_layout.addRow(QLabel("كلمة المرور:"), self.txt_password)
        card_layout.addLayout(form_layout)
        card_layout.addSpacing(15)
        
        btn_layout = QHBoxLayout()
        self.btn_login = QPushButton("تسجيل الدخول")
        self.btn_login.setFixedHeight(42)
        self.btn_login.clicked.connect(self.handle_login)
        
        self.btn_exit = QPushButton("إغلاق")
        self.btn_exit.setObjectName("cancelBtn")
        self.btn_exit.setFixedHeight(42)
        self.btn_exit.clicked.connect(self.close)
        
        btn_layout.addWidget(self.btn_login, stretch=2)
        btn_layout.addWidget(self.btn_exit, stretch=1)
        card_layout.addLayout(btn_layout)
        
        main_layout.addWidget(card_frame)
        self.txt_username.setFocus()

    def handle_login(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()
        
        if not username or not password:
            SystemMessageBox.show_warning(self, "يرجى إدخال اسم المستخدم وكلمة المرور كاملة!")
            return
            
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            cursor = conn.cursor()
            
            # جلب البيانات بالإضافة إلى صلاحية المستخدم (role)
            query = """
                SELECT id, username, COALESCE(pos_id, 1), COALESCE(pos_name, 'نقطة البيع الرئيسية'), COALESCE(role, 'cashier')
                FROM users 
                WHERE username = %s AND password = %s AND is_active = TRUE;
            """
            cursor.execute(query, (username, password))
            user_data = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if user_data:
                session_data = {
                    "user_id": user_data[0],
                    "username": user_data[1],
                    "pos_id": user_data[2],
                    "pos_name": user_data[3],
                    "role": user_data[4]
                }
                
                # التوجيه بناءً على الصلاحية والمسار الجديد لشاشة المدير
                if session_data["role"] == "admin":
                    # استدعاء شاشة المدير من مجلد ui/admin/
                    from ui.admin.admin_main import AdminDashboardWindow
                    self.main_window = AdminDashboardWindow(session_data=session_data)
                else:
                    # استدعاء شاشة الكاشير من مجلد ui/cashier/
                    from ui.cashier.cashier_main import ExactCashierWindow
                    self.main_window = ExactCashierWindow(session_data=session_data)
                
                self.main_window.show()
                self.close() # إغلاق شاشة تسجيل الدخول
            else:
                SystemMessageBox.show_critical(self, "اسم المستخدم أو كلمة المرور غير صحيحة!")
                
        except Exception as e:
            SystemMessageBox.show_critical(self, f"فشل في النظام أو الاتصال:\n{e}")