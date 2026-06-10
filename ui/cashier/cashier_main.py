# ui/cashier/cashier_main.py

import sys
import os
import psycopg2
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLineEdit, QHeaderView, QFrame, 
                             QDialog, QFormLayout, QSpinBox, QComboBox)
from PyQt6.QtCore import Qt, QDateTime, QTimer
from PyQt6.QtGui import QFont, QColor, QShortcut, QKeySequence

# حل مشكلة المسارات لضمان التعرف على المجلدات الشقيقة
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# استيراد الإعدادات الموحدة للنظام إذا كانت متوفرة، وإلا الاعتماد على المحلي
try:
    from app.config.settings import DB_PARAMS, MODERN_STYLE
except ImportError:
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
        QFrame#mainFrame { background-color: #F5F5F5; border: 2px solid #1e5378; border-radius: 16px; }
        QLabel { font-family: 'Segoe UI', 'Arial', 'Cairo'; color: #2b2b2b; border: none; background-color: transparent; }
        QLineEdit, QSpinBox, QComboBox { border: 1px solid #cccccc; border-radius: 8px; padding: 6px 10px; font-family: 'Segoe UI'; font-size: 14px; background-color: #ffffff; color: #333333; }
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus { border: 2px solid #1e5378; }
        QTableWidget { background-color: #ffffff; border: 2px solid #d3d3d3; border-radius: 8px; gridline-color: #f0f0f0; font-family: 'Segoe UI'; color: #333333; }
        QHeaderView::section { background-color: #1e5378; color: white; font-weight: bold; padding: 8px; border: none; }
        QPushButton { background-color: #1e5378; color: #ffffff; font-family: 'Segoe UI', 'Cairo'; font-size: 14px; font-weight: bold; border-radius: 20px; padding: 10px 25px; border: none; min-height: 20px; }
        QPushButton:hover { background-color: #163f5c; }
        QPushButton:pressed { background-color: #0f2d42; }
        QPushButton#deleteBtn, QPushButton#cancelBtn { background-color: #718096; color: white; border-radius: 20px; padding: 10px 25px; border: none; }
        QPushButton#deleteBtn:hover, QPushButton#cancelBtn:hover { background-color: #4a5568; }
        QPushButton#fastCashBtn { background-color: #e2e8f0; color: #2d3748; font-family: 'Segoe UI'; font-size: 13px; font-weight: bold; border-radius: 6px; padding: 6px; border: 1px solid #cbd5e0; }
        QPushButton#fastCashBtn:hover { background-color: #cbd5e0; }
    """

# رسائل النظام المخصصة
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
            self.btn_yes = QPushButton("نعم"); self.btn_yes.setObjectName("primaryBtn"); self.btn_yes.clicked.connect(self.accept)
            self.btn_no = QPushButton("لا"); self.btn_no.setObjectName("secondaryBtn"); self.btn_no.clicked.connect(self.reject)
            btn_layout.addWidget(self.btn_yes); btn_layout.addWidget(self.btn_no)
        else:
            self.btn_ok = QPushButton("موافق"); self.btn_ok.setObjectName("primaryBtn"); self.btn_ok.clicked.connect(self.accept)
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


class PaymentDialog(QDialog):
    def __init__(self, total_amount, parent=None):
        super().__init__(parent)
        self.total_amount = total_amount
        self.setFixedSize(460, 480)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        container_layout = QVBoxLayout(self); container_layout.setContentsMargins(0, 0, 0, 0)
        main_frame = QFrame(); main_frame.setObjectName("mainFrame"); main_frame.setStyleSheet(MODERN_STYLE)
        frame_layout = QVBoxLayout(main_frame); frame_layout.setContentsMargins(25, 20, 25, 20); frame_layout.setSpacing(15)
        
        title = QLabel("💳 شاشة إنهاء الدفع وتحصيل الفاتورة"); title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold)); frame_layout.addWidget(title)
        form_layout = QFormLayout(); form_layout.setSpacing(12); form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.lbl_required = QLabel(f"{self.total_amount:.2f} ج.م"); self.lbl_required.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold)); self.lbl_required.setStyleSheet("color: #e53e3e;")
        form_layout.addRow(QLabel("المبلغ المطلوب:"), self.lbl_required)
        
        self.cmb_method = QComboBox(); self.cmb_method.addItems(["نقدي (Cash)", "فيزا / ماستر كارد", "آجل (On Account)"]); self.cmb_method.setFont(QFont("Segoe UI", 11)); self.cmb_method.setFixedHeight(35)
        form_layout.addRow(QLabel("طريقة الدفع:"), self.cmb_method)
        
        self.txt_paid = QLineEdit(); self.txt_paid.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold)); self.txt_paid.setFixedHeight(40); self.txt_paid.setStyleSheet("color: #1E90FF; font-weight: bold;"); self.txt_paid.setText(f"{self.total_amount:.2f}"); self.txt_paid.textChanged.connect(self.calculate_change)
        form_layout.addRow(QLabel("المبلغ المدفوع:"), self.txt_paid)
        
        fast_cash_layout = QHBoxLayout(); fast_cash_layout.setSpacing(8)
        for val in [50, 100, 200, 500]:
            btn_fast = QPushButton(f"+{val}"); btn_fast.setObjectName("fastCashBtn"); btn_fast.clicked.connect(lambda checked, v=val: self.add_fast_cash(v))
            fast_cash_layout.addWidget(btn_fast)
        form_layout.addRow(QLabel("كاش سريع:"), fast_cash_layout)
        
        self.lbl_change = QLabel("0.00 ج.م"); self.lbl_change.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold)); self.lbl_change.setStyleSheet("color: #2ed573;")
        form_layout.addRow(QLabel("الباقي للعميل:"), self.lbl_change)
        
        frame_layout.addLayout(form_layout)
        frame_layout.addSpacing(10)
        
        btn_layout = QHBoxLayout(); btn_layout.setSpacing(12)
        self.btn_confirm = QPushButton("تأكيد وطباعة (Enter)"); self.btn_confirm.setObjectName("primaryBtn"); self.btn_confirm.setFixedHeight(40); self.btn_confirm.clicked.connect(self.validate_and_accept)
        self.btn_cancel = QPushButton("إلغاء (Esc)"); self.btn_cancel.setObjectName("secondaryBtn"); self.btn_cancel.setFixedHeight(40); self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_confirm, stretch=2); btn_layout.addWidget(self.btn_cancel, stretch=1); frame_layout.addLayout(btn_layout)
        container_layout.addWidget(main_frame)
        self.txt_paid.setFocus(); self.txt_paid.selectAll()

    def add_fast_cash(self, value):
        try:
            current = float(self.txt_paid.text()) if self.txt_paid.text() else 0.0
            self.txt_paid.setText(f"{current + value:.2f}")
        except ValueError:
            self.txt_paid.setText(f"{value:.2f}")

    def calculate_change(self):
        try:
            paid = float(self.txt_paid.text()) if self.txt_paid.text() else 0.0
            change = paid - self.total_amount
            if change >= 0:
                self.lbl_change.setText(f"{change:.2f} ج.م"); self.lbl_change.setStyleSheet("color: #2ed573;")
            else:
                self.lbl_change.setText(f"متبقي للمحل: {abs(change):.2f} ج.م"); self.lbl_change.setStyleSheet("color: #e53e3e;")
        except ValueError:
            self.lbl_change.setText("0.00 ج.م")

    def validate_and_accept(self):
        try:
            paid = float(self.txt_paid.text()) if self.txt_paid.text() else 0.0
            if paid < self.total_amount and self.cmb_method.currentText() != "آجل (On Account)":
                SystemMessageBox.show_warning(self, "المبلغ المدفوع أقل من المطلوب! يرجى مراجعة المبلغ أو تحويل المعاملة إلى 'آجل'.")
                return
            self.accept()
        except ValueError:
            SystemMessageBox.show_warning(self, "يرجى إدخال مبلغ مدفوع صحيح!")

    def get_payment_details(self):
        return {
            "payment_method": self.cmb_method.currentText(),
            "amount_paid": float(self.txt_paid.text()) if self.txt_paid.text() else 0.0,
            "amount_change": max(0.0, (float(self.txt_paid.text()) if self.txt_paid.text() else 0.0) - self.total_amount)
        }

class CustomQtyInputDialog(QDialog):
    def __init__(self, item_name, current_qty, parent=None):
        super().__init__(parent)
        self.setFixedSize(420, 200)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground); self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        container_layout = QVBoxLayout(self); container_layout.setContentsMargins(0, 0, 0, 0)
        main_frame = QFrame(); main_frame.setObjectName("mainFrame"); main_frame.setStyleSheet(MODERN_STYLE)
        frame_layout = QVBoxLayout(main_frame); frame_layout.setContentsMargins(20, 20, 20, 15); frame_layout.setSpacing(15)
        lbl_title = QLabel(f"✏️ تعديل الكمية لـ ({item_name}):"); lbl_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold)); frame_layout.addWidget(lbl_title)
        self.spin_qty = QSpinBox(); self.spin_qty.setRange(1, 1000); self.spin_qty.setValue(current_qty); self.spin_qty.setFont(QFont("Segoe UI", 12)); self.spin_qty.setFixedHeight(40); frame_layout.addWidget(self.spin_qty)
        btn_layout = QHBoxLayout(); btn_ok = QPushButton("موافق"); btn_ok.setObjectName("primaryBtn"); btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("إلغاء"); btn_cancel.setObjectName("secondaryBtn"); btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch(); btn_layout.addWidget(btn_ok); btn_layout.addWidget(btn_cancel); btn_layout.addStretch(); frame_layout.addLayout(btn_layout)
        container_layout.addWidget(main_frame); self.spin_qty.setFocus(); self.spin_qty.selectAll()
    def get_value(self): return self.spin_qty.value()

class ItemInquiryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(520, 420)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground); self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        container_layout = QVBoxLayout(self); container_layout.setContentsMargins(0, 0, 0, 0)
        main_frame = QFrame(); main_frame.setObjectName("mainFrame"); main_frame.setStyleSheet(MODERN_STYLE)
        frame_layout = QVBoxLayout(main_frame); frame_layout.setContentsMargins(20, 20, 20, 15); frame_layout.setSpacing(15)
        top_layout = QHBoxLayout(); lbl_scan = QLabel("🔍 امسح الباركود:"); lbl_scan.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.txt_barcode = QLineEdit(); self.txt_barcode.setPlaceholderText("اضرب الباركود هنا واضغط Enter..."); self.txt_barcode.returnPressed.connect(self.search_item)
        btn_search = QPushButton("استعلام"); btn_search.setObjectName("primaryBtn"); btn_search.clicked.connect(self.search_item)
        top_layout.addWidget(lbl_scan); top_layout.addWidget(self.txt_barcode); top_layout.addWidget(btn_search); frame_layout.addLayout(top_layout)
        self.info_frame = QFrame(); self.info_frame.setStyleSheet("background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px;")
        info_layout = QVBoxLayout(self.info_frame); info_layout.setSpacing(12); info_layout.setContentsMargins(15, 15, 15, 15)
        self.lbl_name = QLabel(" اسم الصنف: ---"); self.lbl_price = QLabel("💰 السعر الأساسي: ---"); self.lbl_discount = QLabel("📉 الخصم الحالي: ---"); self.lbl_final_price = QLabel("💵 سعر البيع النهائي: ---"); self.lbl_stock = QLabel("🏢 المخزون المتاح: ---")
        for lbl in [self.lbl_name, self.lbl_price, self.lbl_discount, self.lbl_final_price, self.lbl_stock]:
            lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium)); lbl.setStyleSheet("color: #4a5568;"); info_layout.addWidget(lbl)
        self.lbl_final_price.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold)); self.lbl_final_price.setStyleSheet("color: #2ed573;"); frame_layout.addWidget(self.info_frame)
        btn_layout = QHBoxLayout(); btn_close = QPushButton("إغلاق الشاشة"); btn_close.setObjectName("secondaryBtn"); btn_close.clicked.connect(self.accept)
        btn_layout.addStretch(); btn_layout.addWidget(btn_close); btn_layout.addStretch(); frame_layout.addLayout(btn_layout)
        container_layout.addWidget(main_frame); self.txt_barcode.setFocus()
    def search_item(self):
        barcode = self.txt_barcode.text().strip()
        if not barcode: return
        try:
            conn = psycopg2.connect(**DB_PARAMS); cursor = conn.cursor()
            cursor.execute("SELECT item_name, price, discount, stock_qty, unit FROM items WHERE barcode = %s", (barcode,))
            result = cursor.fetchone(); cursor.close(); conn.close()
            if result:
                item_name, price, discount, stock_qty, unit = result; final_price = float(price) - float(discount)
                self.lbl_name.setText(f" اسم الصنف:  {item_name} ({unit})"); self.lbl_price.setText(f"💰 السعر الأساسي:  {float(price):.2f} ج.م"); self.lbl_discount.setText(f"📉 الخصم الحالي:  {float(discount):.2f} ج.م"); self.lbl_final_price.setText(f"💵 سعر البيع النهائي:  {final_price:.2f} ج.م"); self.lbl_stock.setText(f"🏢 المخزون المتاح:  {stock_qty} {unit}")
            else: SystemMessageBox.show_warning(self, "هذا الباركود غير مسجل في النظام!")
        except Exception as e: SystemMessageBox.show_critical(self, f"فشل الاتصال: {e}")
        self.txt_barcode.clear(); self.txt_barcode.setFocus()

class ItemReturnDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(420, 240)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground); self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.return_data = None
        container_layout = QVBoxLayout(self); container_layout.setContentsMargins(0, 0, 0, 0)
        main_frame = QFrame(); main_frame.setObjectName("mainFrame"); main_frame.setStyleSheet(MODERN_STYLE)
        frame_layout = QVBoxLayout(main_frame); frame_layout.setContentsMargins(25, 20, 25, 15); frame_layout.setSpacing(12)
        title = QLabel("🔄 عملية إرجاع صنف"); title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold)); frame_layout.addWidget(title)
        form_layout = QFormLayout(); form_layout.setSpacing(10)
        self.txt_barcode = QLineEdit(); self.txt_barcode.setPlaceholderText("امسح أو اكتب الباركود...")
        self.txt_qty = QLineEdit(); self.txt_qty.setText("1"); self.txt_qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addRow(QLabel("باركود الصنف:"), self.txt_barcode); form_layout.addRow(QLabel("الكمية المرتجعة:"), self.txt_qty); frame_layout.addLayout(form_layout)
        btn_layout = QHBoxLayout(); btn_ok = QPushButton("تأكيد المرتجع"); btn_ok.setObjectName("primaryBtn"); btn_ok.clicked.connect(self.validate_and_accept)
        btn_cancel = QPushButton("إلغاء"); btn_cancel.setObjectName("secondaryBtn"); btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch(); btn_layout.addWidget(btn_ok); btn_layout.addWidget(btn_cancel); btn_layout.addStretch(); frame_layout.addLayout(btn_layout)
        container_layout.addWidget(main_frame); self.txt_barcode.setFocus()
    def validate_and_accept(self):
        barcode = self.txt_barcode.text().strip(); qty_str = self.txt_qty.text().strip()
        if not barcode: SystemMessageBox.show_warning(self, "برجاء إدخال الباركود!"); return
        try:
            qty = int(qty_str)
            if qty <= 0: raise ValueError()
        except ValueError: SystemMessageBox.show_warning(self, "برجاء إدخال كمية صحيحة أكبر من الصفر!"); return
        try:
            conn = psycopg2.connect(**DB_PARAMS); cursor = conn.cursor()
            cursor.execute("SELECT item_name, unit, price, discount FROM items WHERE barcode = %s", (barcode,))
            result = cursor.fetchone(); cursor.close(); conn.close()
            if result: self.return_data = (barcode, result[0], result[1], float(result[2]), float(result[3]), qty); self.accept()
            else: SystemMessageBox.show_warning(self, "هذا الباركود غير موجود في المخزن!")
        except Exception as e: SystemMessageBox.show_critical(self, f"فشل الاتصال بقاعدة البيانات: {e}")

class ItemSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(680, 460)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground); self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.selected_item_data = None  
        container_layout = QVBoxLayout(self); container_layout.setContentsMargins(0, 0, 0, 0)
        main_frame = QFrame(); main_frame.setObjectName("mainFrame"); main_frame.setStyleSheet(MODERN_STYLE)
        frame_layout = QVBoxLayout(main_frame); frame_layout.setContentsMargins(20, 20, 20, 15); frame_layout.setSpacing(12)
        search_layout = QHBoxLayout(); lbl_search = QLabel("🔍 ابحث (اسم / كود):"); lbl_search.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.txt_search = QLineEdit(); self.txt_search.setPlaceholderText("اكتب اسم الصنف أو الباركود هنا لبدء البحث الفوري...")
        self.txt_search.textChanged.connect(self.load_data); search_layout.addWidget(lbl_search); search_layout.addWidget(self.txt_search); frame_layout.addLayout(search_layout)
        self.table = QTableWidget(); self.table.setColumnCount(4); self.table.setHorizontalHeaderLabels(["الباركود", "اسم الصنف", "الوحدة", "السعر"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows); self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection); self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers); frame_layout.addWidget(self.table)
        btn_layout = QHBoxLayout(); self.btn_select = QPushButton("إضافة للشاشة الرئيسية"); self.btn_select.setObjectName("primaryBtn"); self.btn_select.clicked.connect(self.accept_selection)
        self.btn_close = QPushButton("إغلاق"); self.btn_close.setObjectName("secondaryBtn"); self.btn_close.clicked.connect(self.reject)
        btn_layout.addStretch(); btn_layout.addWidget(self.btn_select); btn_layout.addWidget(self.btn_close); btn_layout.addStretch(); frame_layout.addLayout(btn_layout)
        container_layout.addWidget(main_frame); self.load_data() 
        
    def load_data(self):
        search_text = self.txt_search.text().strip()
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            cursor = conn.cursor()
            if search_text:
                query = """
                    SELECT barcode, item_name, unit, sales_price AS price, 0.00 AS discount 
                    FROM items 
                    WHERE item_name ILIKE %s OR barcode ILIKE %s
                """
                search_param = f"%{search_text}%"
                cursor.execute(query, (search_param, search_param))
            else:
                query = """
                    SELECT barcode, item_name, unit, sales_price AS price, 0.00 AS discount 
                    FROM items
                """
                cursor.execute(query)
                
            rows = cursor.fetchall()
            self.table.setRowCount(0)
            
            for row_idx, row_data in enumerate(rows):
                self.table.insertRow(row_idx)
                for col_idx in range(4):
                    item = QTableWidgetItem(str(row_data[col_idx]))
                    item.setFont(QFont("Segoe UI", 11))
                    self.table.setItem(row_idx, col_idx, item)
                
                if self.table.item(row_idx, 0):
                    self.table.item(row_idx, 0).setData(Qt.ItemDataRole.UserRole, float(row_data[4]))
                    
            cursor.close()
            conn.close()
        except Exception as e: 
            print(f"خطأ في جلب بيانات البحث: {e}")

    def accept_selection(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            barcode = self.table.item(selected_row, 0).text(); item_name = self.table.item(selected_row, 1).text(); unit = self.table.item(selected_row, 2).text(); price = float(self.table.item(selected_row, 3).text()); discount = self.table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
            self.selected_item_data = (barcode, item_name, unit, price, discount); self.accept()
        else: SystemMessageBox.show_warning(self, "برجاء اختيار صنف من الجدول أولاً!")


class ExactCashierWindow(QMainWindow):
    def __init__(self, session_data=None):
        super().__init__()
        self.session = session_data if session_data else {
            "user_id": 1, "username": "أيهم إبراهيم", "pos_id": 1, "pos_name": "نقطة البيع الافتراضية"
        }
        self.setWindowTitle("شاشة الكاشير الذكية")
        self.setGeometry(100, 100, 1280, 720)
        self.showMaximized()
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(MODERN_STYLE)

        self.init_ui()
        self.connect_buttons()
        self.setup_keyboard_shortcuts()
        self.get_next_invoice_id()
        self.start_live_clock()

    def init_ui(self):
        main_widget = QWidget(); self.setCentralWidget(main_widget)
        master_layout = QHBoxLayout(main_widget); master_layout.setContentsMargins(10, 10, 10, 10); master_layout.setSpacing(10)

        sidebar = QFrame(); sidebar.setFixedWidth(205); sidebar.setStyleSheet("background-color: #ffffff; border: 1px solid #d3d3d3; border-radius: 4px;")
        sidebar_layout = QVBoxLayout(sidebar); sidebar_layout.setContentsMargins(12, 12, 12, 12); sidebar_layout.setSpacing(8)

        self.lbl_pos = QLabel(f"POS: {self.session['pos_name']}"); self.lbl_user = QLabel(f"User: {self.session['username']}"); self.lbl_trans = QLabel("Trans: جارٍ جلب الرقم..."); self.lbl_date = QLabel()
        for lbl in [self.lbl_pos, self.lbl_user, self.lbl_trans, self.lbl_date]:
            lbl.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold)); lbl.setStyleSheet("color: #333333; border: none; padding-left: 5px;"); sidebar_layout.addWidget(lbl)
        sidebar_layout.addSpacing(10)

        button_style = "QPushButton { background-color: #1e5378; color: white; font-family: 'Segoe UI'; font-size: 15px; font-weight: bold; border-radius: 20px; padding: 16px; border: none; } QPushButton:hover { background-color: #163f5c; }"
        
        self.btn_save = QPushButton("حفظ الفاتورة")
        self.btn_edit_qty = QPushButton("تعديل الكمية")
        self.btn_delete_item = QPushButton("حذف صنف")
        self.btn_cancel_invoice = QPushButton("إلغاء الفاتورة")
        self.btn_search_item = QPushButton("بحث عن صنف")
        self.btn_return_item = QPushButton("مرتجع صنف")
        self.btn_inquire_item = QPushButton("استعلام عن صنف")
        self.btn_logout = QPushButton("تسجيل الخروج")

        for btn in [self.btn_save, self.btn_edit_qty, self.btn_delete_item, self.btn_cancel_invoice, self.btn_search_item, self.btn_return_item, self.btn_inquire_item]:
            btn.setStyleSheet(button_style); btn.setCursor(Qt.CursorShape.PointingHandCursor); sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        self.btn_logout.setStyleSheet("QPushButton { background-color: #e53e3e; color: #ffffff; font-family: 'Segoe UI'; font-size: 14px; font-weight: bold; border-radius: 20px; padding: 16px; border: none; } QPushButton:hover { background-color: #c53030; }"); self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor); sidebar_layout.addWidget(self.btn_logout)
        master_layout.addWidget(sidebar, stretch=1)

        right_panel_layout = QVBoxLayout(); right_panel_layout.setSpacing(10)
        self.sales_table = QTableWidget(); self.sales_table.setColumnCount(7); self.sales_table.setHorizontalHeaderLabels(["الباركود", "اسم الصنف", "الوحدة", "السعر", "الكمية", "الخصم", "الإجمالي"])
        self.sales_table.setStyleSheet("QTableWidget { background-color: #ffffff; border: 3px solid #dcdcdc; gridline-color: #f0f0f0; font-family: 'Segoe UI'; font-size: 14px; color: #333333; } QHeaderView::section { background-color: #f8f9fa; color: #4a5568; font-weight: 600; font-size: 13px; padding: 9px; border: none; border-bottom: 1px solid #e2e8f0; } QTableWidget::item { padding: 10px 15px; border-bottom: 1px solid #f7f7f7; }")
        self.sales_table.setColumnWidth(0, 210); self.sales_table.setColumnWidth(1, 300); self.sales_table.setColumnWidth(2, 125); self.sales_table.setColumnWidth(3, 120); self.sales_table.setColumnWidth(4, 120); self.sales_table.setColumnWidth(5, 115); self.sales_table.setColumnWidth(6, 85)
        self.sales_table.horizontalHeader().setStretchLastSection(True); self.sales_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows); self.sales_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection); self.sales_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        right_panel_layout.addWidget(self.sales_table, stretch=9)

        bottom_bar = QFrame(); bottom_bar.setFixedHeight(65); bottom_bar.setStyleSheet("QFrame { background-color: #ffffff; border: 1px solid #d3d3d3; border-radius: 4px; } QLabel { font-size: 15px; font-weight: bold; border: none; color: #333333; } QLineEdit { border: 1px solid #cccccc; border-radius: 6px; padding: 6px 10px; font-size: 15px; background-color: #ffffff; }")
        bottom_layout = QHBoxLayout(bottom_bar); bottom_layout.setContentsMargins(15, 0, 15, 0); bottom_layout.setSpacing(15)
        bottom_layout.addWidget(QLabel("الباركود:"))
        self.txt_barcode = QLineEdit(); self.txt_barcode.setPlaceholderText("اضرب الباركود هنا واضغط Enter..."); self.txt_barcode.setMinimumWidth(300); bottom_layout.addWidget(self.txt_barcode)
        bottom_layout.addWidget(QLabel("العدد:"))
        self.txt_count = QLineEdit(); self.txt_count.setText("0"); self.txt_count.setAlignment(Qt.AlignmentFlag.AlignCenter); self.txt_count.setFixedWidth(200); bottom_layout.addWidget(self.txt_count)
        bottom_layout.addStretch(); bottom_layout.addWidget(QLabel("الإجمالي:"))
        self.lbl_total_box = QLabel("0.00"); self.lbl_total_box.setFont(QFont('Segoe UI', 16, QKeySequence.fromString("0").count())); self.lbl_total_box.setAlignment(Qt.AlignmentFlag.AlignCenter); self.lbl_total_box.setFixedWidth(200); self.lbl_total_box.setStyleSheet("QLabel { background-color: #e0e0e0; color: #000000; border: 1px solid #bcbcbc; border-radius: 4px; padding: 5px; }"); bottom_layout.addWidget(self.lbl_total_box)
        right_panel_layout.addWidget(bottom_bar, stretch=1); master_layout.addLayout(right_panel_layout, stretch=4); self.txt_barcode.setFocus()

    def connect_buttons(self):
        self.btn_save.clicked.connect(self.on_open_payment_screen); self.btn_edit_qty.clicked.connect(self.on_edit_quantity); self.btn_delete_item.clicked.connect(self.on_delete_item); self.btn_cancel_invoice.clicked.connect(self.on_cancel_invoice); self.btn_search_item.clicked.connect(self.on_search_item); self.btn_return_item.clicked.connect(self.on_return_item); self.btn_inquire_item.clicked.connect(self.on_inquire_item); self.btn_logout.clicked.connect(self.on_logout); self.txt_barcode.returnPressed.connect(self.on_barcode_scanned)

    def setup_keyboard_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self.on_open_payment_screen)
        QShortcut(QKeySequence("*"), self).activated.connect(self.on_edit_quantity)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.on_delete_item)
        QShortcut(QKeySequence("Shift+Return"), self).activated.connect(self.on_cancel_invoice)
        QShortcut(QKeySequence("F3"), self).activated.connect(self.on_search_item)
        QShortcut(QKeySequence("F4"), self).activated.connect(self.on_return_item)
        QShortcut(QKeySequence("F1"), self).activated.connect(self.on_inquire_item)

    def keyPressEvent(self, event):
        if self.txt_barcode.hasFocus() and event.key() == Qt.Key.Key_Up:
            if self.sales_table.rowCount() > 0:
                self.sales_table.setFocus()
                self.sales_table.setCurrentCell(self.sales_table.rowCount() - 1, 0)
                event.accept()
                return
        elif self.sales_table.hasFocus() and event.key() == Qt.Key.Key_Down:
            if self.sales_table.currentRow() == self.sales_table.rowCount() - 1:
                self.txt_barcode.clear()
                self.txt_barcode.setFocus()
                event.accept()
                return
        super().keyPressEvent(event)

    def start_live_clock(self):
        self.timer = QTimer(self); self.timer.timeout.connect(self.update_live_clock); self.timer.start(1000); self.update_live_clock()
    def update_live_clock(self): self.lbl_date.setText(QDateTime.currentDateTime().toString("dd-MM-yyyy hh:mm:ss"))

    def get_next_invoice_id(self):
        try:
            conn = psycopg2.connect(**DB_PARAMS); cursor = conn.cursor()
            cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM sales_invoices;")
            self.lbl_trans.setText(f"Trans: {cursor.fetchone()[0]}"); cursor.close(); conn.close()
        except Exception as e: print(f"Error Trans ID: {e}"); self.lbl_trans.setText("Trans: --")

    def update_invoice_totals(self):
        row_count = self.sales_table.rowCount(); total_items = 0; grand_total = 0.0
        for row in range(row_count):
            total_items += int(self.sales_table.item(row, 4).text()); grand_total += float(self.sales_table.item(row, 6).text())
        self.txt_count.setText(str(total_items)); self.lbl_total_box.setText(f"{grand_total:.2f}")

    def add_item_to_table(self, barcode, item_name, unit, price, discount, qty=1, is_return=False):
        row_count = self.sales_table.rowCount()
        for row in range(row_count):
            existing_barcode = self.sales_table.item(row, 0).text(); existing_qty = int(self.sales_table.item(row, 4).text())
            if existing_barcode == barcode and ((is_return and existing_qty < 0) or (not is_return and existing_qty > 0)):
                new_qty = existing_qty + (-qty if is_return else qty); self.sales_table.item(row, 4).setText(str(new_qty))
                new_total = (price * new_qty) + discount if is_return else (price * new_qty) - discount
                self.sales_table.item(row, 6).setText(f"{new_total:.2f}"); self.update_invoice_totals(); return
        self.sales_table.insertRow(row_count); qty = -qty if is_return else qty; total_price = (price * qty) + discount if is_return else (price * qty) - discount
        data = [barcode, item_name, unit, f"{price:.2f}", str(qty), f"{discount:.2f}", f"{total_price:.2f}"]
        for i in range(7):
            item = QTableWidgetItem(data[i]); item.setFont(QFont("Segoe UI", 14))
            if i == 1 and is_return: item.setForeground(QColor("#e53e3e"))
            self.sales_table.setItem(row_count, i, item)
        self.update_invoice_totals()

    def on_barcode_scanned(self):
        barcode = self.txt_barcode.text().strip()
        if barcode:
            try:
                conn = psycopg2.connect(**DB_PARAMS); cursor = conn.cursor()
                cursor.execute("SELECT item_name, unit, price, discount FROM items WHERE barcode = %s", (barcode,))
                result = cursor.fetchone()
                if result: self.add_item_to_table(barcode, result[0], result[1], float(result[2]), float(result[3]))
                else: SystemMessageBox.show_warning(self, "هذا الباركود غير مسجل في النظام!")
                cursor.close(); conn.close()
            except Exception as e: SystemMessageBox.show_critical(self, f"خطأ أثناء جلب الصنف: {e}")
            self.txt_barcode.clear(); self.txt_barcode.setFocus()

    def on_search_item(self):
        dialog = ItemSearchDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_item_data:
            barcode, item_name, unit, price, discount = dialog.selected_item_data; self.add_item_to_table(barcode, item_name, unit, price, discount)

    def on_return_item(self):
        dialog = ItemReturnDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.return_data:
            barcode, item_name, unit, price, discount, qty = dialog.return_data; self.add_item_to_table(barcode, f"[مرتجع] {item_name}", unit, price, discount, qty=qty, is_return=True)

    def on_inquire_item(self): ItemInquiryDialog(self).exec()

    def on_edit_quantity(self):
        selected_row = self.sales_table.currentRow()
        if selected_row >= 0:
            current_qty = int(self.sales_table.item(selected_row, 4).text()); item_name = self.sales_table.item(selected_row, 1).text(); is_ret = current_qty < 0; abs_qty = abs(current_qty)
            dialog = CustomQtyInputDialog(item_name, abs_qty, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_qty = dialog.get_value(); final_qty = -new_qty if is_ret else new_qty; self.sales_table.item(selected_row, 4).setText(str(final_qty)); price = float(self.sales_table.item(selected_row, 3).text()); discount = float(self.sales_table.item(selected_row, 5).text()); new_total = (price * final_qty) + discount if is_ret else (price * final_qty) - discount; self.sales_table.item(selected_row, 6).setText(f"{new_total:.2f}"); self.update_invoice_totals()
        else: SystemMessageBox.show_warning(self, "حدد صنفاً أولاً!")

    def on_open_payment_screen(self):
        row_count = self.sales_table.rowCount()
        if row_count == 0: 
            SystemMessageBox.show_warning(self, "لا يمكن إنهاء دفع فاتورة فارغة!")
            return
            
        total_amount = float(self.lbl_total_box.text())
        pay_dialog = PaymentDialog(total_amount, self)
        if pay_dialog.exec() == QDialog.DialogCode.Accepted:
            pay_details = pay_dialog.get_payment_details()
            
            try:
                conn = psycopg2.connect(**DB_PARAMS); cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO sales_invoices (total_price, user_id, pos_id, invoice_date, payment_method, amount_paid, amount_change) VALUES (%s, %s, %s, NOW(), %s, %s, %s) RETURNING id;", 
                    (total_amount, self.session["user_id"], self.session["pos_id"], pay_details["payment_method"], pay_details["amount_paid"], pay_details["amount_change"])
                )
                invoice_id = cursor.fetchone()[0]
                
                for row in range(row_count):
                    cursor.execute("INSERT INTO invoice_items (invoice_id, barcode, item_name, unit, price, quantity, discount, total) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",
                                   (invoice_id, self.sales_table.item(row, 0).text(), self.sales_table.item(row, 1).text(), self.sales_table.item(row, 2).text(),
                                    float(self.sales_table.item(row, 3).text()), int(self.sales_table.item(row, 4).text()), float(self.sales_table.item(row, 5).text()), float(self.sales_table.item(row, 6).text())))
                
                conn.commit(); cursor.close(); conn.close()
                SystemMessageBox.show_success(self, f"تم إنهاء العملية وحفظ الفاتورة رقم ({invoice_id}) بنجاح!\nطريقة الدفع: {pay_details['payment_method']}\nالباقي للعميل: {pay_details['amount_change']:.2f} ج.م")
                self.sales_table.setRowCount(0); self.update_invoice_totals()
                self.get_next_invoice_id()
            except Exception as e:
                SystemMessageBox.show_critical(self, f"فشل حفظ المعاملة: {e}")

    def on_delete_item(self):
        selected_row = self.sales_table.currentRow()
        if selected_row >= 0: self.sales_table.removeRow(selected_row); self.update_invoice_totals()
        else: SystemMessageBox.show_warning(self, "حدد صنفاً لحذفه!")

    def on_cancel_invoice(self):
        if SystemMessageBox.show_question(self, "هل أنت متأكد من إلغاء الفاتورة الحالية؟") == QDialog.DialogCode.Accepted: self.sales_table.setRowCount(0); self.update_invoice_totals()

    def on_logout(self):
        # استدعاء شاشة تسجيل الدخول من المسار النسبي الصحيح لمنع أخطاء الـ Import
        try:
            from ui.shared.login_gui import LoginWindow
            self.login_screen = LoginWindow()
            self.login_screen.show()
            self.close()
        except ModuleNotFoundError:
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            from ui.shared.login_gui import LoginWindow
            self.login_screen = LoginWindow()
            self.login_screen.show()
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # تعديل الرقم لـ 1 الافتراضي والموجود دوماً بقاعدة البيانات لحل مشكلة قيد ForeignKey مؤقتاً عند التشغيل الفردي
    active_user_session = {
        "user_id": 1, "username": "أيهم إبراهيم", "pos_id": 1, "pos_name": "نقطة البيع الرئيسية"
    }
    window = ExactCashierWindow(session_data=active_user_session)
    window.show()
    sys.exit(app.exec())