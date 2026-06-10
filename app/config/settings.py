# app/config/settings.py

DB_PARAMS = {
    "dbname": "supermarket_db",
    "user": "postgres",
    "password": "123456",  
    "host": "localhost",
    "port": "5432"
}

MODERN_STYLE = """
    QMainWindow { background-color: #F5F5F5; }
    QDialog { background-color: transparent; }
    QFrame#mainFrame {
        background-color: #F5F5F5; border: 2px solid #1e5378; border-radius: 16px;
    }
    QFrame#loginCard {
        background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px;
    }
    QLabel { font-family: 'Segoe UI', 'Arial', 'Cairo'; color: #2b2b2b; border: none; background-color: transparent; }
    QLineEdit, QSpinBox, QComboBox {
        border: 1px solid #cccccc; border-radius: 8px; padding: 8px 12px;
        font-family: 'Segoe UI'; font-size: 14px; background-color: #ffffff; color: #333333;
    }
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus { border: 2px solid #1e5378; }
    
    QTableWidget { 
        background-color: #ffffff; border: 2px solid #d3d3d3; border-radius: 8px; 
        gridline-color: #f0f0f0; font-family: 'Segoe UI'; color: #333333; 
    }
    QHeaderView::section { 
        background-color: #1e5378; color: white; font-weight: bold; padding: 8px; border: none; 
    }
    
    QPushButton {
        background-color: #1e5378; color: #ffffff; font-family: 'Segoe UI', 'Cairo'; 
        font-size: 14px; font-weight: bold; border-radius: 20px; padding: 10px 25px; border: none; min-height: 20px;
    }
    QPushButton:hover { background-color: #163f5c; }
    QPushButton:pressed { background-color: #0f2d42; }
    
    QPushButton#deleteBtn, QPushButton#cancelBtn {
        background-color: #718096; color: white; border-radius: 20px; padding: 10px 25px; border: none;
    }
    QPushButton#deleteBtn:hover, QPushButton#cancelBtn:hover { background-color: #4a5568; }
    
    QPushButton#fastCashBtn {
        background-color: #e2e8f0; color: #2d3748; font-family: 'Segoe UI'; font-size: 13px; font-weight: bold; border-radius: 6px; padding: 6px; border: 1px solid #cbd5e0;
    }
    QPushButton#fastCashBtn:hover { background-color: #cbd5e0; }
"""