# main.py

import sys
from PyQt6.QtWidgets import QApplication
from ui.shared.login_gui import LoginWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # تشغيل شاشة تسجيل الدخول كبوابة رئيسية للنظام
    login_screen = LoginWindow()
    login_screen.show()
    
    sys.exit(app.exec())