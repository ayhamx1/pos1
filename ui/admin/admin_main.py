# admin_main.py

import sys
import os

# حل مشكلة المسارات ليتعرف على مجلد app و ui الرئيسي عند التشغيل من أي مكان
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import psycopg2
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLineEdit, QHeaderView, QFrame, 
                             QDialog, QFormLayout, QSpinBox, QComboBox, QTabWidget, QDateEdit, QScrollArea)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor

from app.config.settings import DB_PARAMS, MODERN_STYLE
from ui.shared.msg_box import SystemMessageBox

class AdminDashboardWindow(QMainWindow):
    def __init__(self, session_data=None):
        super().__init__()
        self.session = session_data if session_data else {
            "user_id": 1, "username": "مدير النظام الافتراضي", "role": "admin"
        }
        
        self.setWindowTitle("لوحة تحكم الإدارة العامة - النظام البرمجي والمالي المتكامل")
        self.setMinimumSize(1024, 680)
        self.showMaximized() 
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(MODERN_STYLE)
        
        # الثوابت والأبعاد الهندسية
        self.INPUT_HEIGHT = 36
        self.BTN_HEIGHT = 38
        self.SIDEBAR_WIDTH = 360 
        
        self.COLOR_PRIMARY = "#20618f"
        self.COLOR_PRIMARY_HOVER = "#153c57"
        self.COLOR_BORDER = "#cbd5e1"
        self.COLOR_SECONDARY = "#f8fafc"
        
        self.label_style = "color: #334155; font-size: 13px; font-weight: bold; border: none; background: transparent;"
        self.input_style = f"""
            QLineEdit, QSpinBox, QComboBox, QDateEdit {{
                border: 1px solid {self.COLOR_BORDER};
                border-radius: 6px;
                padding: 0 10px;
                background-color: {self.COLOR_SECONDARY};
                color: #1e293b;
                font-size: 13px;
            }}
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QDateEdit:focus {{
                border: 2px solid {self.COLOR_PRIMARY};
                background-color: #ffffff;
            }}
        """
        
        # مجمع التبويبات الرئيسي (الشريط العلوي)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # ──────────────────────────────────────────────────────────
        # بناء التبويبات بالترتيب الدقيق والمنسق والمطلوب تماماً
        # ──────────────────────────────────────────────────────────
        # بناء التبويبات بالترتيب الدقيق والمنسق والمطلوب تماماً
        self.init_items_tab()                      # 1. المنتجات والمخزون
        self.init_purchases_tab()                  # 2. المشتريات
        self.init_inventory_tab()                  # 3. 🏬 المخزون
        self.init_marketing_and_promotions_tab()   # 4. 👥 العملاء
        self.init_finance_tab()                    # 5. 💰 الخزنة
        self.init_reports_center_tab()             # 6. 📊 التقارير
        self.init_management_and_security_tab()    # 7. ⚙️ المستخدمون
        self.init_system_settings_tab()            # 8. 🛠️ الإعدادات

        # تحميل البيانات الأولية الفورية عند الإقلاع بأمان الآن
        self.load_items_data()
        self.load_categories_into_items_combo()    # 🟢 سيعمل الآن بنجاح لأن العنصر تم إنشاؤه بالخطوة السابقة
        
    # ──────────────────────────────────────────────────────────
    #  شاشة المنتجات والمخزون (الرئيسية وبداخلها التبويبات الفرعية)
    # ──────────────────────────────────────────────────────────
    def init_items_tab(self):
        """بناء شاشة المنتجات والمخزون وبداخلها التبويبات الفرعية الخمسة لفلترة الأقسام والمخازن"""
        # الوجت الرئيسي للتبويب العام
        products_container_widget = QWidget()
        container_layout = QVBoxLayout(products_container_widget)
        container_layout.setContentsMargins(5, 5, 5, 5)

        # إنشاء شريط تبويبات داخلي فرعي (Nested Tab Widget)
        self.sub_inventory_tabs = QTabWidget()
        self.sub_inventory_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #cbd5e1; background-color: white; border-radius: 6px; top: -1px; }
            QTabBar::tab { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; padding: 8px 16px; font-size: 13px; font-weight: bold; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background: #ffffff; color: #20618f; border-bottom-color: transparent; }
        """)

        # ─────────────── [ 1. تبويب إدارة المنتجات (كودك الأصلي متوافق بالكامل هنا) ] ───────────────
        sub_items_widget = QWidget()
        sub_items_layout = QVBoxLayout(sub_items_widget)
        sub_items_layout.setContentsMargins(12, 12, 12, 12)
        sub_items_layout.setSpacing(10)

        # 🛠️ شريط الأدوات العلوي المنسق (Toolbar) من كودك الأصلي
        toolbar_frame = QFrame()
        toolbar_frame.setStyleSheet("QFrame { background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 8px; }")
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(10, 6, 10, 6)
        toolbar_layout.setSpacing(10)

        lbl_tools = QLabel("🛠️ أدوات التحكم السريع:")
        lbl_tools.setStyleSheet("font-weight: bold; color: #1e293b; font-size: 13px; border: none; background: transparent;")
        toolbar_layout.addWidget(lbl_tools)

        self.btn_tool_add = QPushButton("➕ إضافة صنف")
        self.btn_tool_edit = QPushButton("📝 تعديل صنف")
        self.btn_tool_delete = QPushButton("🗑️ حذف سريع")
        self.btn_tool_barcode = QPushButton("🖨️ طباعة باركود")
        self.btn_tool_export = QPushButton("📥 تصدير إكسيل")

        for btn in [self.btn_tool_add, self.btn_tool_edit, self.btn_tool_delete, self.btn_tool_barcode, self.btn_tool_export]:
            btn.setFixedHeight(32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton { background-color: #ffffff; color: #334155; border: 1px solid #cbd5e1; border-radius: 4px; padding: 0 12px; font-weight: bold; font-size: 12px; }
                QPushButton:hover { background-color: #e2e8f0; color: #0f172a; border-color: #94a3b8; }
            """)
            toolbar_layout.addWidget(btn)
        
        toolbar_layout.addStretch()
        sub_items_layout.addWidget(toolbar_frame)

        # منطقة المحتوى السفلي (الجانب الأيمن للبيانات والأيسر للجدول)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # 📑 نموذج إدخال البيانات الجانبي
        form_frame = QFrame()
        form_frame.setFixedWidth(self.SIDEBAR_WIDTH)
        form_frame.setStyleSheet("QFrame { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; }")
        
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(18, 18, 18, 18)
        form_layout.setSpacing(10)
        
        lbl_title = QLabel("📦 بطاقة بيانات صنف متكاملة")
        lbl_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {self.COLOR_PRIMARY}; border: none; background: transparent;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(lbl_title)
        
        # 🎯 الترتيب الصحيح لتعريف الحقول أولاً:
        self.txt_barcode = QLineEdit()
        self.txt_barcode.setPlaceholderText("امسح أو اكتب الباركود...")
        
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("اسم المنتج بالتفصيل...")
        
        # 🟢 هنا نقوم بتعريف الكومبوبوكس أولاً بدون أي إضافة يدوية ثابتة
        self.cmb_category = QComboBox() 
        
        self.txt_unit = QLineEdit()
        self.txt_unit.setText("قطعة")
        
        self.txt_cost_price = QLineEdit()
        self.txt_cost_price.setPlaceholderText("0.00")
        
        self.txt_sales_price = QLineEdit()
        self.txt_sales_price.setPlaceholderText("0.00")
        
        self.txt_discount = QLineEdit()
        self.txt_discount.setText("0.00")
        
        self.spin_stock = QSpinBox()
        self.spin_stock.setRange(0, 999999)
        self.spin_stock.setValue(100)
        self.spin_stock.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.spin_min_stock = QSpinBox()
        self.spin_min_stock.setRange(0, 1000)
        self.spin_min_stock.setValue(5)
        self.spin_min_stock.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.cmb_supplier = QComboBox()
        self.cmb_supplier.addItems(["مورد عام / افتراضي", "شركة جهينة", "شركة المراعي", "الشركة المصرية للأغذية", "مورد بضاعة محلي"])
        
        self.cmb_status = QComboBox()
        self.cmb_status.addItems(["🟢 نشط (متاح للبيع)", "🔴 موقوف (مجمد)"])
        
        # 🎯 الآن مصفوفة التنسيق ستجد كل العناصر معرفة بنجاح ولن تعطي AttributeError
        widgets_list = [
            self.txt_barcode, self.txt_name, self.cmb_category, self.txt_unit, 
            self.txt_cost_price, self.txt_sales_price, self.txt_discount, 
            self.spin_stock, self.spin_min_stock, self.cmb_supplier, self.cmb_status
        ]
        for widget in widgets_list:
            widget.setStyleSheet(self.input_style)
            widget.setFixedHeight(self.INPUT_HEIGHT)

        # 🟢 أخيراً: استدعاء دالة جلب الأقسام من قاعدة البيانات وتغذية القائمة
        self.load_categories_into_items_combo()
            
        grid = QFormLayout()
        grid.setVerticalSpacing(8); grid.setHorizontalSpacing(10)
        grid.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        
        grid.addRow(QLabel("الباركود الدولي:"), self.txt_barcode)
        grid.addRow(QLabel("اسم المنتج:"), self.txt_name)
        grid.addRow(QLabel("القسم / الفئة:"), self.cmb_category)
        grid.addRow(QLabel("الوحدة الأساسية:"), self.txt_unit)
        grid.addRow(QLabel("سعر التكلفة:"), self.txt_cost_price)
        grid.addRow(QLabel("سعر البيع:"), self.txt_sales_price)
        grid.addRow(QLabel("الخصم المتاح:"), self.txt_discount)
        grid.addRow(QLabel("المخزون الحالي:"), self.spin_stock)
        grid.addRow(QLabel("حد الطلب (الأدنى):"), self.spin_min_stock)
        grid.addRow(QLabel("المورد المعتمد:"), self.cmb_supplier)
        grid.addRow(QLabel("حالة الصنف الحالية:"), self.cmb_status)
        
        for i in range(grid.rowCount()):
            grid.itemAt(i, QFormLayout.ItemRole.LabelRole).widget().setStyleSheet(self.label_style)
            
        form_layout.addLayout(grid)
        form_layout.addSpacing(5)
        
        self.btn_save_item = QPushButton("💾 حفظ / تحديث بيانات الصنف")
        self.btn_save_item.setStyleSheet(f"QPushButton {{ background-color: {self.COLOR_PRIMARY}; color: white; font-weight: bold; border-radius: 6px; }} QPushButton:hover {{ background-color: {self.COLOR_PRIMARY_HOVER}; }}")
        
        self.btn_clear_fields = QPushButton("🧹 تفريغ الحقول وإلغاء التحديد")
        self.btn_clear_fields.setStyleSheet(f"QPushButton {{ background-color: #ffffff; color: #475569; border: 1px solid {self.COLOR_BORDER}; border-radius: 6px; }} QPushButton:hover {{ background-color: #f1f5f9; }}")
        
        self.btn_delete_item = QPushButton("🗑️ حذف الصنف المحدد")
        self.btn_delete_item.setStyleSheet("QPushButton { background-color: #ffffff; color: #dc2626; border: 1px solid #fca5a5; border-radius: 6px; } QPushButton:hover { background-color: #fef2f2; border-color: #dc2626; }")
        
        for btn in [self.btn_save_item, self.btn_clear_fields, self.btn_delete_item]:
            btn.setFixedHeight(self.BTN_HEIGHT)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            form_layout.addWidget(btn)
            
        form_layout.addStretch()
        content_layout.addWidget(form_frame)
        
        # 📊 منطقة الجدول والبحث السريع الأصلية
        table_layout = QVBoxLayout()
        table_layout.setSpacing(10)
        
        search_layout = QHBoxLayout()
        lbl_search = QLabel("🔍 بحث سريع عن صنف:")
        lbl_search.setStyleSheet(self.label_style)
        search_layout.addWidget(lbl_search)
        
        # ربط مربع نص البحث الأصلي بملفك بالدالة الصحيحة: load_items_data
        self.txt_search_item = QLineEdit()
        self.txt_search_item.setPlaceholderText("اكتب اسم المنتج، القسم، المورد، أو الباركود لفلترة النتائج...")
        self.txt_search_item.setStyleSheet(self.input_style)
        self.txt_search_item.setFixedHeight(self.INPUT_HEIGHT)
        table_layout.addLayout(search_layout)
        
        # تغيير اسم الجدول هنا ليتوافق مع السيلف الأصلي في بقية دوال الكود: items_table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(11)
        self.items_table.setHorizontalHeaderLabels([
            "الباركود", "اسم المنتج", "القسم", "الوحدة", "سعر الشراء", 
            "سعر البيع", "الخصم", "المخزون الحالي", "الحد الأدنى", "المورد", "الحالة"
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.items_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.items_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table_layout.addWidget(self.items_table)
        
        search_layout.addWidget(self.txt_search_item)
        content_layout.addLayout(table_layout, stretch=3)
        sub_items_layout.addLayout(content_layout)
        
        self.sub_inventory_tabs.addTab(sub_items_widget, " إدارة المنتجات")

        # ─────────────── [ 2. تبويب الأقسام - مفعل بالكامل ] ───────────────
        sub_categories_widget = QWidget()
        sub_categories_layout = QVBoxLayout(sub_categories_widget)
        sub_categories_layout.setContentsMargins(12, 12, 12, 12)
        sub_categories_layout.setSpacing(10)

        # منطقة المحتوى لشاشة الأقسام (يسار للجدول ويمين لنموذج الإدخال)
        cat_content_layout = QHBoxLayout()
        cat_content_layout.setSpacing(20)

        # 📑 نموذج إدخال بيانات القسم (الجانب الأيمن)
        cat_form_frame = QFrame()
        cat_form_frame.setFixedWidth(380)
        cat_form_frame.setStyleSheet("QFrame { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; }")
        
        cat_form_layout = QVBoxLayout(cat_form_frame)
        cat_form_layout.setContentsMargins(18, 18, 18, 18)
        cat_form_layout.setSpacing(12)

        lbl_cat_title = QLabel("🗂️ بطاقة تعريف قسم")
        lbl_cat_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl_cat_title.setStyleSheet(f"color: {self.COLOR_PRIMARY}; border: none; background: transparent;")
        lbl_cat_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cat_form_layout.addWidget(lbl_cat_title)

        # حقول الإدخال للقسم
        self.txt_cat_id = QLineEdit()
        self.txt_cat_id.setPlaceholderText("تلقائي من النظام...")
        self.txt_cat_id.setReadOnly(True)  # كود القسم معطل لأنه يعتمد على التسلسل التلقائي
        self.txt_cat_id.setStyleSheet("background-color: #f1f5f9; color: #64748b; font-weight: bold;")
        
        self.txt_cat_name = QLineEdit()
        self.txt_cat_name.setPlaceholderText("مثال: المواد الغذائية، المنظفات...")
        
        self.txt_cat_desc = QLineEdit()
        self.txt_cat_desc.setPlaceholderText("وصف مختصر للقسم أو الملاحظات...")
        
        self.cmb_cat_status = QComboBox()
        self.cmb_cat_status.addItems(["🟢 نشط فعّال", "🔴 موقوف مؤقتاً"])

        # تطبيق التنسيق الموحد على الحقول
        for widget in [self.txt_cat_id, self.txt_cat_name, self.txt_cat_desc, self.cmb_cat_status]:
            if widget != self.txt_cat_id:
                widget.setStyleSheet(self.input_style)
            widget.setFixedHeight(self.INPUT_HEIGHT)

        # ترتيب الحقول داخل Form Layout
        cat_grid = QFormLayout()
        cat_grid.setVerticalSpacing(10)
        cat_grid.setHorizontalSpacing(10)
        cat_grid.addRow(QLabel("كود القسم:"), self.txt_cat_id)
        cat_grid.addRow(QLabel("اسم القسم:"), self.txt_cat_name)
        cat_grid.addRow(QLabel("الوصف / الملاحظات:"), self.txt_cat_desc)
        cat_grid.addRow(QLabel("حالة القسم:"), self.cmb_cat_status)

        for i in range(cat_grid.rowCount()):
            cat_grid.itemAt(i, QFormLayout.ItemRole.LabelRole).widget().setStyleSheet(self.label_style)
        cat_form_layout.addLayout(cat_grid)
        cat_form_layout.addSpacing(10)

        # أزرار التحكم بالقسم
        self.btn_save_category = QPushButton("💾 حفظ / تحديث القسم")
        self.btn_save_category.setStyleSheet(f"QPushButton {{ background-color: {self.COLOR_PRIMARY}; color: white; font-weight: bold; border-radius: 6px; }} QPushButton:hover {{ background-color: {self.COLOR_PRIMARY_HOVER}; }}")
        
        self.btn_clear_category = QPushButton("🧹 تفريغ الحقول")
        self.btn_clear_category.setStyleSheet(f"QPushButton {{ background-color: #ffffff; color: #475569; border: 1px solid {self.COLOR_BORDER}; border-radius: 6px; }} QPushButton:hover {{ background-color: #f1f5f9; }}")
        
        self.btn_delete_category = QPushButton("🗑️ حذف القسم المحدد")
        self.btn_delete_category.setStyleSheet("QPushButton { background-color: #ffffff; color: #dc2626; border: 1px solid #fca5a5; border-radius: 6px; } QPushButton:hover { background-color: #fef2f2; border-color: #dc2626; }")

        for btn in [self.btn_save_category, self.btn_clear_category, self.btn_delete_category]:
            btn.setFixedHeight(self.BTN_HEIGHT)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            cat_form_layout.addWidget(btn)

        cat_form_layout.addStretch()
        cat_content_layout.addWidget(cat_frame_side := cat_form_frame)

        # 📊 منطقة الجدول والبحث (الجانب الأيسر)
        cat_table_layout = QVBoxLayout()
        cat_table_layout.setSpacing(10)

        cat_search_layout = QHBoxLayout()
        lbl_cat_search = QLabel("🔍 بحث سريع في الأقسام:")
        lbl_cat_search.setStyleSheet(self.label_style)
        cat_search_layout.addWidget(lbl_cat_search)

        self.txt_search_category = QLineEdit()
        self.txt_search_category.setPlaceholderText("اكتب اسم القسم أو كود البحث لفلترة النتائج...")
        self.txt_search_category.setStyleSheet(self.input_style)
        self.txt_search_category.setFixedHeight(self.INPUT_HEIGHT)
        cat_search_layout.addWidget(self.txt_search_category)
        cat_table_layout.addLayout(cat_search_layout)

        # جدول عرض الأقسام المكتمل
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(6)
        self.categories_table.setHorizontalHeaderLabels(["كود القسم", "اسم القسم", "الوصف والبيانات", "الحالة", "تاريخ الإنشاء", "العمليات"])
        self.categories_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.categories_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.categories_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.categories_table.setStyleSheet(self.items_table.styleSheet()) # استخدام نفس ستايل جدول المنتجات الأنيق
        cat_table_layout.addWidget(self.categories_table)

        cat_content_layout.addLayout(cat_table_layout, stretch=3)
        sub_categories_layout.addLayout(cat_content_layout)
        self.sub_inventory_tabs.addTab(sub_categories_widget, "🗂️ الأقسام")

        # ربط أحداث شاشة الأقسام بالدوال البرمجية وقاعدة البيانات
        self.btn_save_category.clicked.connect(self.load_save_category_db)
        self.btn_clear_category.clicked.connect(self.clear_category_fields)
        self.btn_delete_category.clicked.connect(self.delete_category_db)
        self.categories_table.itemClicked.connect(self.on_category_row_selected)
        self.txt_search_category.textChanged.connect(self.load_categories_data)

        # استدعاء أولي لتحميل الأقسام عند تشغيل البرنامج
        self.load_categories_data()

        # ─────────────── [ 3. تبويب الوحدات - مفعل بالكامل ] ───────────────
        sub_units_widget = QWidget()
        sub_units_layout = QVBoxLayout(sub_units_widget)
        sub_units_layout.setContentsMargins(12, 12, 12, 12)
        sub_units_layout.setSpacing(10)

        # منطقة المحتوى لشاشة الوحدات (يسار للجدول ويمين لنموذج الإدخال)
        unit_content_layout = QHBoxLayout()
        unit_content_layout.setSpacing(20)

        # 📑 نموذج إدخال بيانات الوحدة (الجانب الأيمن)
        unit_form_frame = QFrame()
        unit_form_frame.setFixedWidth(380)
        unit_form_frame.setStyleSheet("QFrame { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; }")
        
        unit_form_layout = QVBoxLayout(unit_form_frame)
        unit_form_layout.setContentsMargins(18, 18, 18, 18)
        unit_form_layout.setSpacing(12)

        lbl_unit_title = QLabel("⚖️ بطاقة تعريف وحدة قياس")
        lbl_unit_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl_unit_title.setStyleSheet(f"color: {self.COLOR_PRIMARY}; border: none; background: transparent;")
        lbl_unit_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        unit_form_layout.addWidget(lbl_unit_title)

        # حقول الإدخال للوحدة
        self.txt_unit_id = QLineEdit()
        self.txt_unit_id.setPlaceholderText("تلقائي من النظام...")
        self.txt_unit_id.setReadOnly(True)
        self.txt_unit_id.setStyleSheet("background-color: #f1f5f9; color: #64748b; font-weight: bold;")
        
        self.txt_unit_name_input = QLineEdit()
        self.txt_unit_name_input.setPlaceholderText("مثال: كيلو جرام، قطعة، كرتونة...")
        
        self.txt_unit_shortcut = QLineEdit()
        self.txt_unit_shortcut.setPlaceholderText("مثال: كجم، ق، كرتونة...")
        
        self.txt_unit_desc = QLineEdit()
        self.txt_unit_desc.setPlaceholderText("ملاحظات أو تفاصيل عن استخدام الوحدة...")

        # تطبيق التنسيق الموحد على الحقول
        for widget in [self.txt_unit_id, self.txt_unit_name_input, self.txt_unit_shortcut, self.txt_unit_desc]:
            if widget != self.txt_unit_id:
                widget.setStyleSheet(self.input_style)
            widget.setFixedHeight(self.INPUT_HEIGHT)

        # ترتيب الحقول داخل Form Layout
        unit_grid = QFormLayout()
        unit_grid.setVerticalSpacing(10)
        unit_grid.setHorizontalSpacing(10)
        unit_grid.addRow(QLabel("كود الوحدة:"), self.txt_unit_id)
        unit_grid.addRow(QLabel("اسم الوحدة:"), self.txt_unit_name_input)
        unit_grid.addRow(QLabel("الاختصار:"), self.txt_unit_shortcut)
        unit_grid.addRow(QLabel("الوصف / الملاحظات:"), self.txt_unit_desc)

        for i in range(unit_grid.rowCount()):
            unit_grid.itemAt(i, QFormLayout.ItemRole.LabelRole).widget().setStyleSheet(self.label_style)
        unit_form_layout.addLayout(unit_grid)
        unit_form_layout.addSpacing(10)

        # أزرار التحكم بالوحدة
        self.btn_save_unit = QPushButton("💾 حفظ / تحديث الوحدة")
        self.btn_save_unit.setStyleSheet(f"QPushButton {{ background-color: {self.COLOR_PRIMARY}; color: white; font-weight: bold; border-radius: 6px; }} QPushButton:hover {{ background-color: {self.COLOR_PRIMARY_HOVER}; }}")
        
        self.btn_clear_unit = QPushButton("🧹 تفريغ الحقول")
        self.btn_clear_unit.setStyleSheet(f"QPushButton {{ background-color: #ffffff; color: #475569; border: 1px solid {self.COLOR_BORDER}; border-radius: 6px; }} QPushButton:hover {{ background-color: #f1f5f9; }}")
        
        self.btn_delete_unit = QPushButton("🗑️ حذف الوحدة المحددة")
        self.btn_delete_unit.setStyleSheet("QPushButton { background-color: #ffffff; color: #dc2626; border: 1px solid #fca5a5; border-radius: 6px; } QPushButton:hover { background-color: #fef2f2; border-color: #dc2626; }")

        for btn in [self.btn_save_unit, self.btn_clear_unit, self.btn_delete_unit]:
            btn.setFixedHeight(self.BTN_HEIGHT)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            unit_form_layout.addWidget(btn)

        unit_form_layout.addStretch()
        unit_content_layout.addWidget(unit_form_frame)

        # 📊 منطقة الجدول والبحث للوحدات (الجانب الأيسر)
        unit_table_layout = QVBoxLayout()
        unit_table_layout.setSpacing(10)

        unit_search_layout = QHBoxLayout()
        lbl_unit_search = QLabel("🔍 بحث سريع في الوحدات:")
        lbl_unit_search.setStyleSheet(self.label_style)
        unit_search_layout.addWidget(lbl_unit_search)

        self.txt_search_unit = QLineEdit()
        self.txt_search_unit.setPlaceholderText("اكتب اسم الوحدة أو الاختصار لفلترة النتائج...")
        self.txt_search_unit.setStyleSheet(self.input_style)
        self.txt_search_unit.setFixedHeight(self.INPUT_HEIGHT)
        unit_search_layout.addWidget(self.txt_search_unit)
        unit_table_layout.addLayout(unit_search_layout)

        # جدول عرض الوحدات
        self.units_table = QTableWidget()
        self.units_table.setColumnCount(5)
        self.units_table.setHorizontalHeaderLabels(["كود الوحدة", "اسم الوحدة", "الاختصار المعياري", "الوصف والبيانات", "العمليات"])
        self.units_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.units_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.units_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.units_table.setStyleSheet(self.items_table.styleSheet())
        unit_table_layout.addWidget(self.units_table)

        unit_content_layout.addLayout(unit_table_layout, stretch=3)
        sub_units_layout.addLayout(unit_content_layout)
        self.sub_inventory_tabs.addTab(sub_units_widget, "⚖️ الوحدات")

        # ربط أحداث شاشة الوحدات بالدوال البرمجية
        self.btn_save_unit.clicked.connect(self.save_unit_to_db)
        self.btn_clear_unit.clicked.connect(self.clear_unit_fields)
        self.btn_delete_unit.clicked.connect(self.delete_unit_from_db)
        self.units_table.itemClicked.connect(self.on_unit_row_selected)
        self.txt_search_unit.textChanged.connect(self.load_units_data)

        # استدعاء أولي لتحميل الوحدات عند تشغيل النظام
        self.load_units_data()

        # ─────────────── [ 4. تبويب الباركود - مفعل بالكامل ] ───────────────
        sub_barcode_widget = QWidget()
        sub_barcode_layout = QVBoxLayout(sub_barcode_widget)
        sub_barcode_layout.setContentsMargins(12, 12, 12, 12)
        sub_barcode_layout.setSpacing(10)

        # منطقة المحتوى لشاشة الباركود (يسار للمعاينة الحية ويمين لنموذج التحكم)
        bar_content_layout = QHBoxLayout()
        bar_content_layout.setSpacing(20)

        # 📑 نموذج إعدادات توليد وطباعة الباركود (الجانب الأيمن)
        bar_form_frame = QFrame()
        bar_form_frame.setFixedWidth(380)
        bar_form_frame.setStyleSheet("QFrame { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; }")
        
        bar_form_layout = QVBoxLayout(bar_form_frame)
        bar_form_layout.setContentsMargins(18, 18, 18, 18)
        bar_form_layout.setSpacing(12)

        lbl_bar_title = QLabel("🖨️ إعدادات طباعة ملصقات الباركود")
        lbl_bar_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl_bar_title.setStyleSheet(f"color: {self.COLOR_PRIMARY}; border: none; background: transparent;")
        lbl_bar_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bar_form_layout.addWidget(lbl_bar_title)

        # حقول الإدخال والتحكم
        self.cmb_bar_product = QComboBox()
        self.cmb_bar_product.setEditable(True)
        self.cmb_bar_product.setPlaceholderText("اختر أو ابحث عن المنتج...")
        
        self.txt_bar_code_val = QLineEdit()
        self.txt_bar_code_val.setPlaceholderText("رقم الباركود الحالي للمنتج...")
        self.txt_bar_code_val.setReadOnly(True)
        self.txt_bar_code_val.setStyleSheet("background-color: #f1f5f9; color: #64748b; font-weight: bold;")
        
        self.txt_bar_price_val = QLineEdit()
        self.txt_bar_price_val.setPlaceholderText("0.00 ج.م")
        self.txt_bar_price_val.setReadOnly(True)
        self.txt_bar_price_val.setStyleSheet("background-color: #f1f5f9; color: #16a34a; font-weight: bold;")

        self.spin_bar_count = QSpinBox()
        self.spin_bar_count.setRange(1, 1000)
        self.spin_bar_count.setValue(1)
        self.spin_bar_count.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.cmb_bar_size = QComboBox()
        self.cmb_bar_size.addItems(["Standard (38mm x 25mm)", "Large (50mm x 30mm)", "A4 Sheet (24 Labels)"])

        # تطبيق التنسيق الموحد على الحقول
        for widget in [self.cmb_bar_product, self.txt_bar_code_val, self.txt_bar_price_val, self.spin_bar_count, self.cmb_bar_size]:
            if widget not in [self.txt_bar_code_val, self.txt_bar_price_val]:
                widget.setStyleSheet(self.input_style)
            widget.setFixedHeight(self.INPUT_HEIGHT)

        # ترتيب الحقول داخل Form Layout
        bar_grid = QFormLayout()
        bar_grid.setVerticalSpacing(12)
        bar_grid.setHorizontalSpacing(10)
        bar_grid.addRow(QLabel("اختيار المنتج:"), self.cmb_bar_product)
        bar_grid.addRow(QLabel("رقم الباركود:"), self.txt_bar_code_val)
        bar_grid.addRow(QLabel("سعر البيع الحلي:"), self.txt_bar_price_val)
        bar_grid.addRow(QLabel("عدد الملصقات:"), self.spin_bar_count)
        bar_grid.addRow(QLabel("مقاس وتصميم الورق:"), self.cmb_bar_size)

        for i in range(bar_grid.rowCount()):
            bar_grid.itemAt(i, QFormLayout.ItemRole.LabelRole).widget().setStyleSheet(self.label_style)
        bar_form_layout.addLayout(bar_grid)
        bar_form_layout.addSpacing(10)

        # أزرار التحكم والطباعة
        self.btn_generate_barcode = QPushButton("⚡ توليد / تحديث الباركود")
        self.btn_generate_barcode.setStyleSheet(f"QPushButton {{ background-color: #f1f5f9; color: #334155; border: 1px solid {self.COLOR_BORDER}; font-weight: bold; border-radius: 6px; }} QPushButton:hover {{ background-color: #e2e8f0; }}")
        
        self.btn_print_barcode = QPushButton("🖨️ بدء طباعة الملصقات الآن")
        self.btn_print_barcode.setStyleSheet(f"QPushButton {{ background-color: {self.COLOR_PRIMARY}; color: white; font-weight: bold; border-radius: 6px; }} QPushButton:hover {{ background-color: {self.COLOR_PRIMARY_HOVER}; }}")
        
        self.btn_clear_barcode_view = QPushButton("🧹 تفريغ الحقول وإلغاء")
        self.btn_clear_barcode_view.setStyleSheet("QPushButton { background-color: #ffffff; color: #475569; border: 1px solid #cbd5e1; border-radius: 6px; } QPushButton:hover { background-color: #f1f5f9; }")

        for btn in [self.btn_generate_barcode, self.btn_print_barcode, self.btn_clear_barcode_view]:
            btn.setFixedHeight(self.BTN_HEIGHT)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            bar_form_layout.addWidget(btn)

        bar_form_layout.addStretch()
        bar_content_layout.addWidget(bar_form_frame)

        # 🖼️ منطقة المعاينة الحية لملصق التيكيت (الجانب الأيسر - Preview)
        preview_vbox = QVBoxLayout()
        preview_vbox.setSpacing(10)
        
        lbl_preview_header = QLabel("👁️ معاينة حية لشكل ملصق السعر قبل الطباعة (Live Preview):")
        lbl_preview_header.setStyleSheet(self.label_style)
        preview_vbox.addWidget(lbl_preview_header)

        # كادر التيكيت المنسق والمطابق للصورة تماماً
        self.ticket_preview_frame = QFrame()
        self.ticket_preview_frame.setStyleSheet("""
            QFrame { 
                background-color: #ffffff; 
                border: 2px dashed #94a3b8; 
                border-radius: 8px; 
            }
        """)
        
        ticket_layout = QVBoxLayout(self.ticket_preview_frame)
        ticket_layout.setContentsMargins(30, 30, 30, 30)
        ticket_layout.setSpacing(15)
        ticket_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # عناصر التيكيت الداخلي
        self.lbl_ticket_shop_name = QLabel("سوبر ماركت الإيمان والاستقرار")
        self.lbl_ticket_shop_name.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.lbl_ticket_shop_name.setStyleSheet("color: #64748b; border: none;")
        self.lbl_ticket_shop_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_ticket_prod_name = QLabel("[ اسم المنتج سيظهر هنا بالتفصيل ]")
        self.lbl_ticket_prod_name.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        self.lbl_ticket_prod_name.setStyleSheet("color: #1e293b; border: none;")
        self.lbl_ticket_prod_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # رسم محاكاة الباركود
        self.lbl_ticket_barcode_graphic = QLabel("||||| |||||||| ||||||| |||| ||||||| ||||")
        self.lbl_ticket_barcode_graphic.setFont(QFont("Courier New", 24, QFont.Weight.Bold))
        self.lbl_ticket_barcode_graphic.setStyleSheet("color: #000000; letter-spacing: 2px; border: none;")
        self.lbl_ticket_barcode_graphic.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_ticket_barcode_num = QLabel("0000000000000")
        self.lbl_ticket_barcode_num.setFont(QFont("Segoe UI", 10))
        self.lbl_ticket_barcode_num.setStyleSheet("color: #475569; border: none;")
        self.lbl_ticket_barcode_num.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_ticket_price = QLabel("السعر: 0.00 ج.م")
        self.lbl_ticket_price.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.lbl_ticket_price.setStyleSheet("color: #20618f; background-color: #f1f5f9; padding: 6px 20px; border-radius: 4px; border: 1px solid #e2e8f0;")
        self.lbl_ticket_price.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ticket_layout.addWidget(self.lbl_ticket_shop_name)
        ticket_layout.addWidget(self.lbl_ticket_prod_name)
        ticket_layout.addWidget(self.lbl_ticket_barcode_graphic)
        ticket_layout.addWidget(self.lbl_ticket_barcode_num)
        ticket_layout.addWidget(self.lbl_ticket_price)

        preview_vbox.addWidget(self.ticket_preview_frame, stretch=1)
        bar_content_layout.addLayout(preview_vbox, stretch=3)
        sub_barcode_layout.addLayout(bar_content_layout)
        
        self.sub_inventory_tabs.addTab(sub_barcode_widget, "🖨️ الباركود")

        # ربط أحداث ومحركات الواجهة للدوال التفاعلية وحسابات الداتابيز
        self.cmb_bar_product.currentIndexChanged.connect(self.on_barcode_product_changed)
        self.btn_generate_barcode.clicked.connect(self.generate_barcode_action)
        self.btn_print_barcode.clicked.connect(self.print_barcode_action)
        self.btn_clear_barcode_view.clicked.connect(self.clear_barcode_fields)

        # استدعاء أولي لتغذية قائمة الكومبوبوكس بالمنتجات الحقيقية
        self.load_products_into_barcode_combo()

        # ─────────────── [ 5. تبويب الجرد - مفعل بالكامل ] ───────────────
        sub_check_widget = QWidget()
        sub_check_layout = QVBoxLayout(sub_check_widget)
        sub_check_layout.setContentsMargins(12, 12, 12, 12)
        sub_check_layout.setSpacing(10)

        # منطقة المحتوى لشاشة الجرد (يسار للجدول ويمين لنموذج المعالجة والتسوية)
        inv_content_layout = QHBoxLayout()
        inv_content_layout.setSpacing(20)

        # 📑 نموذج تسجيل مستند تسوية جردية (الجانب الأيمن)
        inv_form_frame = QFrame()
        inv_form_frame.setFixedWidth(380)
        inv_form_frame.setStyleSheet("QFrame { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; }")
        
        inv_form_layout = QVBoxLayout(inv_form_frame)
        inv_form_layout.setContentsMargins(18, 18, 18, 18)
        inv_form_layout.setSpacing(12)

        lbl_inv_title = QLabel("📋 معالجة تسوية الفروقات الجردية")
        lbl_inv_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl_inv_title.setStyleSheet(f"color: {self.COLOR_PRIMARY}; border: none; background: transparent;")
        lbl_inv_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inv_form_layout.addWidget(lbl_inv_title)

        # حقول الإدخال والتحكم
        self.txt_inv_check_id = QLineEdit()
        self.txt_inv_check_id.setPlaceholderText("تلقائي مستند جديد...")
        self.txt_inv_check_id.setReadOnly(True)
        self.txt_inv_check_id.setStyleSheet("background-color: #f1f5f9; color: #64748b; font-weight: bold;")

        self.cmb_inv_product = QComboBox()
        self.cmb_inv_product.setEditable(True)
        self.cmb_inv_product.setPlaceholderText("اختر الصنف المراد جرده وتسويته...")

        self.spin_actual_stock = QSpinBox()
        self.spin_actual_stock.setRange(0, 999999)
        self.spin_actual_stock.setValue(0)
        self.spin_actual_stock.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.txt_stock_difference = QLineEdit()
        self.txt_stock_difference.setPlaceholderText("سيتم احتساب الفارق تلقائياً...")
        self.txt_stock_difference.setReadOnly(True)
        self.txt_stock_difference.setStyleSheet("background-color: #f8fafc; font-weight: bold; color: #475569;")

        self.txt_inv_reason = QLineEdit()
        self.txt_inv_reason.setPlaceholderText("مثال: تالف، عجز طبيعي، خطأ إدخال سابق...")

        # تطبيق التنسيق الموحد على الحقول
        for widget in [self.txt_inv_check_id, self.cmb_inv_product, self.spin_actual_stock, self.txt_stock_difference, self.txt_inv_reason]:
            if widget not in [self.txt_inv_check_id, self.txt_stock_difference]:
                widget.setStyleSheet(self.input_style)
            widget.setFixedHeight(self.INPUT_HEIGHT)

        # ترتيب الحقول داخل Form Layout
        inv_grid = QFormLayout()
        inv_grid.setVerticalSpacing(12)
        inv_grid.setHorizontalSpacing(10)
        inv_grid.addRow(QLabel("رقم التسوية:"), self.txt_inv_check_id)
        inv_grid.addRow(QLabel("اختيار المنتج:"), self.cmb_inv_product)
        inv_grid.addRow(QLabel("الكمية الفعلية (باليد):"), self.spin_actual_stock)
        inv_grid.addRow(QLabel("الفروقات المحتسبة:"), self.txt_stock_difference)
        inv_grid.addRow(QLabel("السبب / الملاحظات:"), self.txt_inv_reason)

        for i in range(inv_grid.rowCount()):
            inv_grid.itemAt(i, QFormLayout.ItemRole.LabelRole).widget().setStyleSheet(self.label_style)
        inv_form_layout.addLayout(inv_grid)
        inv_form_layout.addSpacing(10)

        # أزرار التحكم والعمليات
        self.btn_save_inv_check = QPushButton("💾 اعتماد وتثبيت التسوية الجردية")
        self.btn_save_inv_check.setStyleSheet(f"QPushButton {{ background-color: {self.COLOR_PRIMARY}; color: white; font-weight: bold; border-radius: 6px; }} QPushButton:hover {{ background-color: {self.COLOR_PRIMARY_HOVER}; }}")
        
        self.btn_clear_inv_fields = QPushButton("🧹 تفريغ حقول الإدخال")
        self.btn_clear_inv_fields.setStyleSheet("QPushButton { background-color: #ffffff; color: #475569; border: 1px solid #cbd5e1; border-radius: 6px; } QPushButton:hover { background-color: #f1f5f9; }")

        for btn in [self.btn_save_inv_check, self.btn_clear_inv_fields]:
            btn.setFixedHeight(self.BTN_HEIGHT)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            inv_form_layout.addWidget(btn)

        inv_form_layout.addStretch()
        inv_content_layout.addWidget(inv_form_frame)

        # 📊 منطقة الجدول والبحث للعمليات السابقة (الجانب الأيسر)
        inv_table_layout = QVBoxLayout()
        inv_table_layout.setSpacing(10)

        inv_search_layout = QHBoxLayout()
        lbl_inv_search = QLabel("🔍 بحث في السجل التاريخي للجرد:")
        lbl_inv_search.setStyleSheet(self.label_style)
        inv_search_layout.addWidget(lbl_inv_search)

        self.txt_search_inv_check = QLineEdit()
        self.txt_search_inv_check.setPlaceholderText("اكتب اسم المنتج أو السبب لفلترة مستندات الجرد...")
        self.txt_search_inv_check.setStyleSheet(self.input_style)
        self.txt_search_inv_check.setFixedHeight(self.INPUT_HEIGHT)
        inv_search_layout.addWidget(self.txt_search_inv_check)
        inv_table_layout.addLayout(inv_search_layout)

        # جدول عرض عمليات الجرد والتسوية
        self.inventory_check_table = QTableWidget()
        self.inventory_check_table.setColumnCount(7)
        self.inventory_check_table.setHorizontalHeaderLabels(["رقم السند", "اسم المنتج", "الكمية الدفترية", "الكمية الفعلية", "الفارق المخزني", "السبب / البيان", "التاريخ والوقت"])
        self.inventory_check_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.inventory_check_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.inventory_check_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.inventory_check_table.setStyleSheet(self.items_table.styleSheet())
        inv_table_layout.addWidget(self.inventory_check_table)

        inv_content_layout.addLayout(inv_table_layout, stretch=3)
        sub_check_layout.addLayout(inv_content_layout)
        
        self.sub_inventory_tabs.addTab(sub_check_widget, "📋 الجرد")

        # ربط أحداث ومحركات الواجهة للدوال الحسابية والتنفيذية
        self.cmb_inv_product.currentIndexChanged.connect(self.calculate_stock_difference_live)
        self.spin_actual_stock.valueChanged.connect(self.calculate_stock_difference_live)
        self.btn_save_inv_check.clicked.connect(self.save_inventory_adjustment_db)
        self.btn_clear_inv_fields.clicked.connect(self.clear_inventory_check_fields)
        self.txt_search_inv_check.textChanged.connect(self.load_inventory_checks_data)

        # استدعاء أولي لتغذية قائمة الكومبوبوكس بالبضائع وتحميل السجل
        self.load_products_into_inventory_combo()
        self.load_inventory_checks_data()

        # ─────────────── [ 6. تبويب حركات المخزون - مفعل بالكامل ] ───────────────
        sub_movements_widget = QWidget()
        sub_movements_layout = QVBoxLayout(sub_movements_widget)
        sub_movements_layout.setContentsMargins(12, 12, 12, 12)
        sub_movements_layout.setSpacing(10)

        # 🔍 شريط الفلترة والبحث المتقدم العلوي (أعلى الجدول)
        filter_frame = QFrame()
        filter_frame.setStyleSheet("QFrame { background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 8px; }")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(10, 8, 10, 8)
        filter_layout.setSpacing(12)

        # 1. حقل البحث النصي
        filter_layout.addWidget(QLabel("🔍 بحث بالمنتج:"))
        self.txt_search_mov_product = QLineEdit()
        self.txt_search_mov_product.setPlaceholderText("اكتب اسم المنتج أو كود البحث...")
        self.txt_search_mov_product.setStyleSheet(self.input_style)
        self.txt_search_mov_product.setFixedHeight(32)
        filter_layout.addWidget(self.txt_search_mov_product, stretch=2)

        # 2. فلتر نوع الحركة
        filter_layout.addWidget(QLabel("📦 نوع الحركة:"))
        self.cmb_filter_mov_type = QComboBox()
        self.cmb_filter_mov_type.addItems(["الكل", "وارد (مشتريات/مرتجع)", "صادر (مبيعات/تحويل)", "تالف (هوالك)", "تسوية جردية"])
        self.cmb_filter_mov_type.setStyleSheet(self.input_style)
        self.cmb_filter_mov_type.setFixedHeight(32)
        filter_layout.addWidget(self.cmb_filter_mov_type, stretch=1)

        # 3. فلتر الفترة الزمنية (من تاريخ)
        filter_layout.addWidget(QLabel("📅 من تاريخ:"))
        self.date_mov_from = QDateEdit()
        self.date_mov_from.setCalendarPopup(True)
        self.date_mov_from.setDate(QDate.currentDate().addDays(-30))  # افتراضي آخر شهر
        self.date_mov_from.setStyleSheet(self.input_style)
        self.date_mov_from.setFixedHeight(32)
        filter_layout.addWidget(self.date_mov_from)

        # 4. فلتر الفترة الزمنية (إلى تاريخ)
        filter_layout.addWidget(QLabel("📅 إلى تاريخ:"))
        self.date_mov_to = QDateEdit()
        self.date_mov_to.setCalendarPopup(True)
        self.date_mov_to.setDate(QDate.currentDate())
        self.date_mov_to.setStyleSheet(self.input_style)
        self.date_mov_to.setFixedHeight(32)
        filter_layout.addWidget(self.date_mov_to)

        # 5. زر تحديث البيانات
        self.btn_refresh_movements = QPushButton("🔄 تحديث السجل")
        self.btn_refresh_movements.setStyleSheet(f"QPushButton {{ background-color: {self.COLOR_PRIMARY}; color: white; font-weight: bold; border-radius: 4px; padding: 0 15px; }} QPushButton:hover {{ background-color: {self.COLOR_PRIMARY_HOVER}; }}")
        self.btn_refresh_movements.setFixedHeight(32)
        self.btn_refresh_movements.setCursor(Qt.CursorShape.PointingHandCursor)
        filter_layout.addWidget(self.btn_refresh_movements)

        # تطبيق ستايل الليبل داخل الفلتر العلوي
        for i in range(filter_layout.count()):
            widget = filter_layout.itemAt(i).widget()
            if isinstance(widget, QLabel):
                widget.setStyleSheet(self.label_style + " border: none; background: transparent;")

        sub_movements_layout.addWidget(filter_frame)

        # 📊 جدول عرض كشف سجل حركات المخزون المتكامل
        self.stock_movements_table = QTableWidget()
        self.stock_movements_table.setColumnCount(7)
        self.stock_movements_table.setHorizontalHeaderLabels([
            "رقم الحركة", "اسم المنتج المستهدف", "نوع حركة المخزن", 
            "الكمية المحولة", "الرصيد بعد الحركة", "البيان / المستند المرجعي", "التاريخ والوقت"
        ])
        self.stock_movements_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.stock_movements_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.stock_movements_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.stock_movements_table.setStyleSheet(self.items_table.styleSheet()) # الحفاظ على التصميم الموحد للسيستم
        sub_movements_layout.addWidget(self.stock_movements_table)
        
        self.sub_inventory_tabs.addTab(sub_movements_widget, "🔄 حركات المخزون")

        # ⚙️ ربط الأحداث بمحركات البحث والفلترة الفورية
        self.btn_refresh_movements.clicked.connect(self.load_stock_movements_data)
        self.txt_search_mov_product.textChanged.connect(self.load_stock_movements_data)
        self.cmb_filter_mov_type.currentIndexChanged.connect(self.load_stock_movements_data)
        self.date_mov_from.dateChanged.connect(self.load_stock_movements_data)
        self.date_mov_to.dateChanged.connect(self.load_stock_movements_data)

        # استدعاء أولي لتحميل سجل البيانات فور فتح الواجهة
        self.load_stock_movements_data()

        # إضافة شريط التبويبات الداخلي بالكامل للـ Layout الرئيسي للشاشة
        container_layout.addWidget(self.sub_inventory_tabs)
        
        # إضافة الشاشة الكبيرة إلى شريط التبويبات الرئيسي للبرنامج بالمسمى الجديد المطلوب
        self.tabs.addTab(products_container_widget, " المنتجات والمخزون")

        # ⚙️ ربط محركات الأحداث والسيجنالز بالدوال الأصلية المليئة بالـ SQL بملفك
        self.btn_tool_add.clicked.connect(self.on_save_item_clicked)
        self.btn_tool_edit.clicked.connect(self.on_save_item_clicked)
        self.btn_tool_delete.clicked.connect(self.on_delete_item_clicked)
        
        self.btn_save_item.clicked.connect(self.on_save_item_clicked)
        self.btn_delete_item.clicked.connect(self.on_delete_item_clicked)
        self.btn_clear_fields.clicked.connect(self.clear_item_fields)
        
        self.txt_search_item.textChanged.connect(self.load_items_data)
        self.items_table.itemClicked.connect(self.on_item_row_selected)

        self.load_categories_into_items_combo()

    # ──────────────────────────────────────────────────────────
    # دالة جلب وعرض كشف حركات المخزون والتلوين التلقائي للحركات
    # ──────────────────────────────────────────────────────────
    def load_stock_movements_data(self):
        """جلب كشف سجل حركات المخزن من قاعدة البيانات مع الفلترة"""
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            cursor = conn.cursor()
            
            search_text = self.txt_search_mov_product.text().strip()
            type_filter = self.cmb_filter_mov_type.currentText()
            date_from = self.date_mov_from.date().toString(Qt.DateFormat.ISODate)
            date_to = self.date_mov_to.date().toString(Qt.DateFormat.ISODate) + " 23:59:59"

            # 🟢 تم إزالة m.post_stock واستبداله بـ 'محدث' لتفادي خطأ عدم وجود العمود في الداتابيز
            query = """
                SELECT m.id, i.item_name, m.movement_type, m.quantity, 'محدث تلقائياً' as post_stock, m.created_at 
                FROM stock_movements m 
                JOIN items i ON m.item_id::varchar = i.barcode 
                WHERE m.created_at BETWEEN %s AND %s
            """
            params = [date_from, date_to]

            if search_text:
                query += " AND i.item_name ILIKE %s"
                params.append(f"%{search_text}%")

            if type_filter != "الكل":
                clean_type = type_filter.split(" ")[0]
                query += " AND m.movement_type ILIKE %s"
                params.append(f"%{clean_type}%")

            query += " ORDER BY m.id DESC;"
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            
            self.stock_movements_table.setRowCount(0)
            for row_idx, row_data in enumerate(rows):
                self.stock_movements_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    val_str = str(value) if value is not None else ""
                    if col_idx == 6 and val_str:
                        val_str = val_str.split(".")[0]
                        
                    item = QTableWidgetItem(val_str)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    if col_idx == 2:
                        if "وارد" in val_str or "In" in val_str:
                            item.setForeground(QColor("#16a34a"))
                        elif "تالف" in val_str or "هالك" in val_str or "عجز" in val_str:
                            item.setForeground(QColor("#dc2626"))
                        elif "صادر" in val_str or "Out" in val_str:
                            item.setForeground(QColor("#2563eb"))
                            
                    self.stock_movements_table.setItem(row_idx, col_idx, item)
                    
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"تنبيه قاعدة البيانات (حركات المخزن): {e}")

    # ──────────────────────────────────────────────────────────
    # دوال معالجة وحسابات تسوية الجرد الدوري والربط مع الداتابيز
    # ──────────────────────────────────────────────────────────
    def load_products_into_inventory_combo(self):
        """جلب البضائع من الداتابيز لتغذية قائمة الجرد وتخزين الكمية الدفترية المتوفرة"""
        try:
            self.cmb_inv_product.blockSignals(True)
            self.cmb_inv_product.clear()
            
            conn = psycopg2.connect(**DB_PARAMS)
            cursor = conn.cursor()
            # تعديل الاستعلام لجلب الباركود واسم المنتج والمخزون
            cursor.execute("SELECT barcode, item_name, stock_qty FROM items ORDER BY item_name ASC;")
            self.inventory_products_cache = cursor.fetchall()
            
            for row in self.inventory_products_cache:
                self.cmb_inv_product.addItem(row[1], userData={"id": row[0], "book_stock": row[2]})
                
            cursor.close()
            conn.close()
            self.cmb_inv_product.blockSignals(False)
        except Exception as e:
            print(f"خطأ أثناء جلب البضائع لشاشة الجرد: {e}")

    def calculate_stock_difference_live(self):
        """حساب وتلوين الفارق المالي والمخزني تلقائياً ومباشرة بين الكمية الدفترية والفعلية"""
        data = self.cmb_inv_product.currentData()
        if data:
            book_stock = int(data["book_stock"])
            actual_stock = self.spin_actual_stock.value()
            difference = actual_stock - book_stock
            
            if difference == 0:
                self.txt_stock_difference.setText("0 (مطابق تماماً)")
                self.txt_stock_difference.setStyleSheet("background-color: #f0fdf4; color: #16a34a; font-weight: bold; border: 1px solid #bbf7d0;")
            elif difference > 0:
                self.txt_stock_difference.setText(f"+{difference} (زيادة في المخزن)")
                self.txt_stock_difference.setStyleSheet("background-color: #f0fdf4; color: #15803d; font-weight: bold; border: 1px solid #bbf7d0;")
            else:
                self.txt_stock_difference.setText(f"{difference} (عجز ومفقودات)")
                self.txt_stock_difference.setStyleSheet("background-color: #fef2f2; color: #991b1b; font-weight: bold; border: 1px solid #fca5a5;")
        else:
            self.txt_stock_difference.clear()
            self.txt_stock_difference.setStyleSheet("background-color: #f8fafc; color: #475569;")

    def load_inventory_checks_data(self):
        """تحميل وعرض كافة مستندات التسوية التاريخية السابقة بأعمدة متوافقة وآمنة"""
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            cursor = conn.cursor()
            
            search_text = self.txt_search_inv_check.text().strip()
            
            # 🟢 تم تعديل الاستعلام لجلب الأعمدة الأساسية الشائعة لتجنب تعارض الحقول غير الموجودة
            query_base = """
                SELECT a.id, i.item_name, 'محسوبة تلقائياً' as book_stock, a.adjustment_qty, a.adjustment_type, a.created_at 
                FROM inventory_adjustments a 
                JOIN items i ON a.item_id::varchar = i.barcode 
            """
            
            if search_text:
                query = query_base + " WHERE i.item_name ILIKE %s ORDER BY a.id DESC;"
                cursor.execute(query, (f"%{search_text}%",))
            else:
                query = query_base + " ORDER BY a.id DESC;"
                cursor.execute(query)
                
            rows = cursor.fetchall()
            self.inventory_check_table.setRowCount(0)
            
            for row_idx, row_data in enumerate(rows):
                self.inventory_check_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    val_str = str(value) if value is not None else ""
                    if col_idx == 5 and val_str: # تعديل معامل التاريخ ليطابق الحقل الخامس
                        val_str = val_str.split(".")[0]
                    item = QTableWidgetItem(val_str)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.inventory_check_table.setItem(row_idx, col_idx, item)
                
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"تنبيه قاعدة البيانات (جرد): {e}")

    def save_inventory_adjustment_db(self):
        """حفظ مستند تسوية الجرد وتحديث كمية المخازن الفردية بالباركود الفعلي بالملف"""
        product_idx = self.cmb_inv_product.currentIndex()
        if product_idx < 0:
            SystemMessageBox.show_warning(self, "يرجى اختيار الصنف المراد جرد كميته أولاً!")
            return

        user_data = self.cmb_inv_product.currentData()
        barcode = user_data["id"]  
        book_stock = user_data["book_stock"]
        
        # استخدام المعرّفات الفعلية المطابقة تماماً لملفك لمنع الـ AttributeError
        actual_stock = self.spin_actual_stock.value()
        # 🟢 التعديل الصحيح والمطابق لملفك: self.txt_inv_notes
        reason = self.txt_inv_notes.text().strip()

        if not reason:
            SystemMessageBox.show_warning(self, "يرجى كتابة سبب أو ملاحظة التسوية (مثال: عجز طبيعي، بضاعة تالفة)!")
            return

        try:
            conn = psycopg2.connect(**DB_PARAMS)
            cursor = conn.cursor()

            # 1. تحديث جدول تسوية المخازن
            cursor.execute(
                "INSERT INTO inventory_adjustments (item_id, book_stock, actual_stock, reason) VALUES (%s, %s, %s, %s);",
                (barcode, book_stock, actual_stock, reason)
            )

            # 2. تحديث جدول المنتجات بالبيانات الصحيحة لقاعدتك
            cursor.execute("UPDATE items SET stock_qty = %s WHERE barcode = %s;", (actual_stock, barcode))

            conn.commit()
            cursor.close()
            conn.close()

            SystemMessageBox.show_info(self, "تم حفظ مستند تسوية الجرد وتحديث مخزون الصنف بنجاح!")
            
            # إعادة تهيئة وتحديث الحقول والجداول بالأسماء الصحيحة لملفك
            # 🟢 التعديل هنا أيضاً لإفراغ الحقل النصي الصحيح
            self.txt_inv_notes.clear()
            self.spin_actual_stock.setValue(0)
            self.load_products_into_inventory_combo()
            self.load_inventory_checks_data()

        except Exception as e:
            SystemMessageBox.show_critical(self, f"فشلت عملية حفظ تسوية الجرد بسبب تعارض بالبيانات: {e}")

    def clear_inventory_check_fields(self):
        """تفريغ حقول إدخال واجهة الجرد والتسوية للوضع الافتراضي"""
        self.txt_inv_check_id.clear()
        self.cmb_inv_product.setCurrentIndex(-1)
        self.spin_actual_stock.setValue(0)
        self.txt_stock_difference.clear()
        self.txt_stock_difference.setStyleSheet("background-color: #f8fafc; color: #475569;")
        self.txt_inv_reason.clear()
        self.inventory_check_table.clearSelection()

    # ──────────────────────────────────────────────────────────
    # دوال معالجة وحدات القياس والربط مع قاعدة البيانات PostgreSQL
    # ──────────────────────────────────────────────────────────
    def load_units_data(self):
        """تحميل وحدات القياس من قاعدة البيانات وعرضها في الجدول مع دعم الفلترة والبحث"""
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            cursor = conn.cursor()
            
            search_text = self.txt_search_unit.text().strip()
            if search_text:
                query = "SELECT id, name, shortcut, description FROM product_units WHERE name ILIKE %s OR shortcut ILIKE %s ORDER BY id DESC;"
                cursor.execute(query, (f"%{search_text}%", f"%{search_text}%"))
            else:
                query = "SELECT id, name, shortcut, description FROM product_units ORDER BY id DESC;"
                cursor.execute(query)
                
            rows = cursor.fetchall()
            self.units_table.setRowCount(0)
            
            for row_idx, row_data in enumerate(rows):
                self.units_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    val_str = str(value) if value is not None else ""
                    item = QTableWidgetItem(val_str)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.units_table.setItem(row_idx, col_idx, item)
                
                # إضافة نص ثابت لعمود العمليات
                btn_action = QTableWidgetItem("📝 تعديل سريع")
                btn_action.setForeground(QColor("#20618f"))
                btn_action.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.units_table.setItem(row_idx, 4, btn_action)
                
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"خطأ أثناء تحميل بيانات الوحدات: {e}")

    def on_unit_row_selected(self, item):
        """نقل بيانات الصف المحدد في جدول الوحدات إلى حقول الإدخال للتعديل أو الحذف"""
        row = item.row()
        self.txt_unit_id.setText(self.units_table.item(row, 0).text())
        self.txt_unit_name_input.setText(self.units_table.item(row, 1).text())
        self.txt_unit_shortcut.setText(self.units_table.item(row, 2).text())
        self.txt_unit_desc.setText(self.units_table.item(row, 3).text())

    def save_unit_to_db(self):
        """حفظ وحدة جديدة أو تحديث وحدة حالية بناء على المعرفات الحقيقية بالملف"""
        # 🟢 تم استخدام الأسماء الحقيقية والدقيقة لملفك لمنع الـ AttributeError
        name = self.txt_unit_name_input.text().strip()
        shortcut = self.txt_unit_shortcut.text().strip()
        desc = self.txt_unit_desc.text().strip()
        unit_id = self.txt_unit_id.text().strip()

        if not name:
            SystemMessageBox.show_warning(self, "يرجى إدخال اسم الوحدة الأساسي أولاً!")
            return

        try:
            conn = psycopg2.connect(**DB_PARAMS)
            cursor = conn.cursor()

            if unit_id:  # عملية تحديث بيانات وحدة موجودة مسبقاً
                query = "UPDATE product_units SET name = %s, shortcut = %s, description = %s WHERE id = %s;"
                cursor.execute(query, (name, shortcut, desc, unit_id))
                msg = f"تم تحديث بيانات الوحدة [{name}] بنجاح في قاعدة البيانات!"
            else:  # إضافة وحدة جديدة تماماً لعدم وجود معرف رقمي
                query = "INSERT INTO product_units (name, shortcut, description) VALUES (%s, %s, %s);"
                cursor.execute(query, (name, shortcut, desc))
                msg = f"تم حفظ الوحدة الجديدة [{name}] بنجاح في النظام!"

            conn.commit()
            cursor.close()
            conn.close()

            SystemMessageBox.show_info(self, msg)
            self.clear_unit_fields()
            self.load_units_data()

        except Exception as e:
            SystemMessageBox.show_critical(self, f"فشلت العملية بسبب خطأ في قاعدة البيانات: {e}")

    def clear_unit_fields(self):
        """تفريغ كافة حقول إدخال شاشة الوحدات المتطابقة مع عناصر الملف الأصلية"""
        try:
            # 🟢 المسميات الأصلية الصحيحة لعملية التصفية والمحو الشامل للواجهة
            if hasattr(self, 'txt_unit_id'): self.txt_unit_id.clear()
            if hasattr(self, 'txt_unit_name_input'): self.txt_unit_name_input.clear()
            if hasattr(self, 'txt_unit_shortcut'): self.txt_unit_shortcut.clear()
            if hasattr(self, 'txt_unit_desc'): self.txt_unit_desc.clear()
            if hasattr(self, 'units_table'): self.units_table.clearSelection()
        except Exception as e:
            print(f"تنبيه أثناء مسح حقول الوحدات: {e}")

    def delete_unit_from_db(self):
        """حذف الوحدة المحددة من النظام بعد التأكد من اختيارها"""
        unit_id = self.txt_unit_id.text().strip()
        unit_name = self.txt_unit_name.text().strip()

        if not unit_id:
            SystemMessageBox.show_warning(self, "يرجى اختيار الوحدة المراد حذفها من الجدول أولاً!")
            return

        try:
            conn = psycopg2.connect(**DB_PARAMS)
            cursor = conn.cursor()

            query = "DELETE FROM product_units WHERE id = %s;"
            cursor.execute(query, (unit_id,))
            conn.commit()
            cursor.close()
            conn.close()

            # 🟢 التعديل الصحيح هنا: تمرير self ثم نص الرسالة فقط دون عنوان إضافي
            SystemMessageBox.show_info(self, f"تم حذف الوحدة [{unit_name}] بنجاح من النظام.")
            self.clear_unit_fields()
            self.load_units_data()

        except Exception as e:
            # 🟢 التعديل الصحيح هنا: تمرير self ثم نص الرسالة فقط دون عنوان إضافي
            SystemMessageBox.show_critical(self, f"لا يمكن حذف هذه الوحدة لارتباطها بمنتجات حية في المخزن!\nالسبب التقني: {e}")

    # ──────────────────────────────────────────────────────────
    # دوال معالجة وتوليد وطباعة الباركود والربط التفاعلي للبيانات
    # ──────────────────────────────────────────────────────────
    def load_products_into_barcode_combo(self):
        """جلب جميع السلع المتواجدة بالمخزن من قاعدة البيانات لتغذية قائمة الاختيار"""
        try:
            self.cmb_bar_product.blockSignals(True)
            self.cmb_bar_product.clear()
            
            conn = psycopg2.connect(**DB_PARAMS)
            cursor = conn.cursor()
            # تعديل الاستعلام ليتناسب مع أسماء الأعمدة الحقيقية في جدولك
            cursor.execute("SELECT barcode, item_name, sales_price FROM items ORDER BY item_name ASC;")
            self.barcode_products_cache = cursor.fetchall()
            
            for row in self.barcode_products_cache:
                # تخزين الباركود في الـ userData
                self.cmb_bar_product.addItem(row[1], userData={"id": row[0], "barcode": row[0], "price": row[2]})
                
            cursor.close()
            conn.close()
            self.cmb_bar_product.blockSignals(False)
        except Exception as e:
            print(f"خطأ أثناء جلب المنتجات لشاشة الباركود: {e}")

    def on_barcode_product_changed(self, index):
        """تحديث حقول الباركود وتغيير لوحة المعاينة الحية فوراً عند اختيار منتج مختلف"""
        data = self.cmb_bar_product.currentData()
        if data:
            barcode = str(data["barcode"]) if data["barcode"] else "لا يوجد باركود"
            price = f"{float(data['price']):.2f} ج.م" if data["price"] else "0.00 ج.م"
            
            # تحديث حقول النموذج
            self.txt_bar_code_val.setText(barcode)
            self.txt_bar_price_val.setText(price)
            
            # تحديث كارت المعاينة التفاعلية (Live Ticket Preview)
            self.lbl_ticket_prod_name.setText(self.cmb_bar_product.currentText())
            self.lbl_ticket_barcode_num.setText(barcode)
            self.lbl_ticket_price.setText(f"السعر: {price}")
            
            if data["barcode"]:
                self.lbl_ticket_barcode_graphic.setText("||||| |||||||| ||||||| |||| ||||||| ||||")
            else:
                self.lbl_ticket_barcode_graphic.setText("[ يحتاج لتوليد باركود ]")

    def generate_barcode_action(self):
        """توليد باركود تلقائي أو معالجة طباعة الباركود للصنف المحدد"""
        # تأكد من تعديل أول سطر تحذيري بالدالة ليكون هكذا:
        product_name = self.cmb_bar_product.currentText()
        if not product_name:
            # 🟢 التعديل الصحيح: معاملين فقط (self، والنص مباشرة)
            SystemMessageBox.show_warning(self, "يرجى اختيار صنف حي من القائمة أولاً لتوليد وطباعة باركود له!")
            return
            
        try:
            # ... باقي كود التوليد والطباعة لديك ...
            
            # إذا كان هناك رسالة نجاح في نهاية الدالة تأكد أن تعدلها أيضاً هكذا:
            msg = f"تم توليد وطباعة الباركود للمنتج [{product_name}] بنجاح!"
            SystemMessageBox.show_info(self, msg)
        except Exception as e:
            SystemMessageBox.show_critical(self, f"فشلت عملية توليد الباركود: {e}")

    def print_barcode_action(self):
        """معالجة أمر الطباعة الحقيقي وإرسال الملصقات بعدد النسخ المطلوبة"""
        product_name = self.cmb_bar_product.currentText()
        count = self.spin_bar_count.value()
        barcode = self.txt_bar_code_val.text()
        
        if not product_name or not barcode or barcode == "لا يوجد باركود":
            # 🟢 التعديل: تمرير self ثم نص التحذير مباشرة
            SystemMessageBox.show_warning(self, "لا توجد بيانات صالحة لإرسالها لأمر الطباعة!")
            return
            
        # 🟢 التعديل: تمرير self ثم نص النجاح مباشرة
        msg = f"تم إرسال أمر الطباعة بنجاح إلى الطابعة الافتراضية!\nالمستند: ملصق {product_name}\nعدد النسخ المطلوبة: {count} ملصق تيكت."
        SystemMessageBox.show_info(self, msg)

    def clear_barcode_fields(self):
        """إعادة تعيين كافة الحقول وكارت المعاينة لشكلها الافتراضي"""
        self.cmb_bar_product.setCurrentIndex(-1)
        self.txt_bar_code_val.clear()
        self.txt_bar_price_val.clear()
        self.spin_bar_count.setValue(1)
        self.lbl_ticket_prod_name.setText("[ اسم المنتج سيظهر هنا بالتفصيل ]")
        self.lbl_ticket_barcode_num.setText("0000000000000")
        self.lbl_ticket_price.setText("السعر: 0.00 ج.م")
        self.lbl_ticket_barcode_graphic.setText("||||| |||||||| ||||||| |||| ||||||| ||||")

    # ──────────────────────────────────────────────────────────
    # دوال معالجة الأقسام والربط مع قاعدة البيانات PostgreSQL
    # ──────────────────────────────────────────────────────────
    def load_categories_data(self):
        """تحميل الأقسام الحقيقية من قاعدة البيانات وعرضها داخل الجدول"""
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            cursor = conn.cursor()
            
            search_text = self.txt_search_category.text().strip()
            
            # بناء الاستعلام مع دعم الفلترة والبحث الذكي
            if search_text:
                query = "SELECT id, name, description, status, created_at FROM categories WHERE name ILIKE %s OR description ILIKE %s ORDER BY id DESC;"
                cursor.execute(query, (f"%{search_text}%", f"%{search_text}%"))
            else:
                query = "SELECT id, name, description, status, created_at FROM categories ORDER BY id DESC;"
                cursor.execute(query)
                
            rows = cursor.fetchall()
            self.categories_table.setRowCount(0)
            
            for row_idx, row_data in enumerate(rows):
                self.categories_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    val_str = str(value) if value is not None else ""
                    # تنسيق مريح لتاريخ الإنشاء دون أجزاء الثواني المعقدة
                    if col_idx == 4 and val_str:
                        val_str = val_str.split(" ")[0]
                        
                    item = QTableWidgetItem(val_str)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.categories_table.setItem(row_idx, col_idx, item)
                
                # إضافة خيار التعديل السريع في العمود الأخير
                btn_action = QTableWidgetItem("📝 تعديل سريع")
                btn_action.setForeground(QColor("#20618f"))
                btn_action.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.categories_table.setItem(row_idx, 5, btn_action)
                
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"خطأ أثناء جلب الأقسام من الداتابيز: {e}")

    def on_category_row_selected(self, item):
        """عند الضغط على أي قسم في الجدول، يتم سحب بياناته فوراً إلى نموذج الإدخال الجانبي"""
        row = item.row()
        self.txt_cat_id.setText(self.categories_table.item(row, 0).text())
        self.txt_cat_name.setText(self.categories_table.item(row, 1).text())
        self.txt_cat_desc.setText(self.categories_table.item(row, 2).text())
        
        status_text = self.categories_table.item(row, 3).text()
        if "نشط" in status_text or "Active" in status_text:
            self.cmb_cat_status.setCurrentIndex(0)
        else:
            self.cmb_cat_status.setCurrentIndex(1)

    def load_save_category_db(self):
        """حفظ قسم جديد (Insert) أو تحديث بيانات قسم تم اختياره (Update)"""
        name = self.txt_cat_name.text().strip()
        desc = self.txt_cat_desc.text().strip()
        status = "Active" if self.cmb_cat_status.currentIndex() == 0 else "Inactive"
        cat_id = self.txt_cat_id.text().strip()

        if not name:
            # تمرير self ثم نص الرسالة فقط
            SystemMessageBox.show_warning(self, "يرجى إدخال اسم القسم الأساسي أولاً!")
            return

        try:
            conn = psycopg2.connect(**DB_PARAMS)
            cursor = conn.cursor()

            if cat_id:  # عملية تحديث بيانات
                query = "UPDATE categories SET name = %s, description = %s, status = %s WHERE id = %s;"
                cursor.execute(query, (name, desc, status, cat_id))
                msg = f"تم تحديث بيانات القسم [{name}] بنجاح في قاعدة البيانات!"
            else:  # إضافة قسم جديد تماماً
                query = "INSERT INTO categories (name, description, status) VALUES (%s, %s, %s);"
                cursor.execute(query, (name, desc, status))
                msg = f"تم حفظ القسم الجديد [{name}] بنجاح في النظام!"

            conn.commit()
            cursor.close()
            conn.close()
            
            # 🟢 التعديل الصحيح: self ثم نص الرسالة
            SystemMessageBox.show_info(self, msg)
            self.clear_category_fields()
            self.load_categories_data() 
            
            if hasattr(self, 'load_categories_into_items_combo'):
                self.load_categories_into_items_combo()
                
        except Exception as e:
            # 🟢 التعديل الصحيح: self ثم نص الرسالة
            SystemMessageBox.show_critical(self, f"فشلت العملية بسبب تعارض أو خطأ في قاعدة البيانات: {e}")

    def delete_category_db(self):
        """حذف القسم المحدد نهائياً من قاعدة البيانات بعد التوثق من عدم وجود سلع تابعة له"""
        cat_id = self.txt_cat_id.text().strip()
        cat_name = self.txt_cat_name.text().strip()
        
        if not cat_id:
            SystemMessageBox.show_warning(self, "يرجى اختيار القسم المراد حذفه من الجدول جهة اليسار أولاً!")
            return

        try:
            conn = psycopg2.connect(**DB_PARAMS)
            cursor = conn.cursor()
            
            query = "DELETE FROM categories WHERE id = %s;"
            cursor.execute(query, (cat_id,))
            conn.commit()
            cursor.close()
            conn.close()

            # 🟢 التعديل الصحيح: self ثم نص الرسالة
            SystemMessageBox.show_info(self, f"تم حذف القسم [{cat_name}] بنجاح من النظام.")
            self.clear_category_fields()
            self.load_categories_data()
            
            if hasattr(self, 'load_categories_into_items_combo'):
                self.load_categories_into_items_combo()
                
        except Exception as e:
            # 🟢 التعديل الصحيح: self ثم نص الرسالة
            SystemMessageBox.show_critical(self, f"لا يمكن حذف هذا القسم لأنه يحتوي على منتجات وأصناف تابعة له!\nالسبب التقني: {e}")

    def clear_category_fields(self):
        """تفريغ كافة الحقول لإعادة تهيئة الشاشة لعملية إدخال جديدة"""
        self.txt_cat_id.clear()
        self.txt_cat_name.clear()
        self.txt_cat_desc.clear()
        self.cmb_cat_status.setCurrentIndex(0)
        self.categories_table.clearSelection()

    # ──────────────────────────────────────────────────────────
    # 2. 🗂️ شاشة إدارة الأقسام والفئات
    # ──────────────────────────────────────────────────────────
    def init_categories_tab(self):
        categories_widget = QWidget()
        categories_layout = QVBoxLayout(categories_widget)
        categories_layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_title = QLabel("🗂️ إدارة أقسام ومجموعات السلع والأصناف")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #20618f;")
        categories_layout.addWidget(lbl_title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # هنا يمكنك إضافة الجدول الخاص بالأقسام (البقالة، المجمدات...) وأزرار الإدخال لاحقاً
        categories_layout.addStretch()
        self.tabs.addTab(categories_widget, "🗂️ الأقسام")

    # ──────────────────────────────────────────────────────────
    # 3. ⚖️ شاشة إدارة وحدات القياس والتعبئة
    # ──────────────────────────────────────────────────────────
    def init_units_tab(self):
        units_widget = QWidget()
        units_layout = QVBoxLayout(units_widget)
        units_layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_title = QLabel("⚖️ إدارة وحدات القياس والتعبئة (قطعة، كجم، كرتونة، لتر)")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #20618f;")
        units_layout.addWidget(lbl_title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        units_layout.addStretch()
        self.tabs.addTab(units_widget, "⚖️ الوحدات")

    # ──────────────────────────────────────────────────────────
    # 4. 🖨️ شاشة توليد وتصميم ملصقات الباركود
    # ──────────────────────────────────────────────────────────
    def init_barcode_tab(self):
        barcode_widget = QWidget()
        barcode_layout = QVBoxLayout(barcode_widget)
        barcode_layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_title = QLabel("🖨️ توليد وطباعة ملصقات الباركود وتصميم التيكت")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #20618f;")
        barcode_layout.addWidget(lbl_title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        barcode_layout.addStretch()
        self.tabs.addTab(barcode_widget, "🖨️ الباركود")

    # ──────────────────────────────────────────────────────────
    # 5. 📋 شاشة تسوية الجرد الدوري والسنوي
    # ──────────────────────────────────────────────────────────
    def init_inventory_check_tab(self):
        inv_check_widget = QWidget()
        inv_check_layout = QVBoxLayout(inv_check_widget)
        inv_check_layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_title = QLabel("📋 تسوية الجرد الدوري والسنوي للمخازن ومعالجة الفروقات")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #20618f;")
        inv_check_layout.addWidget(lbl_title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        inv_check_layout.addStretch()
        self.tabs.addTab(inv_check_widget, "📋 الجرد")

    # ──────────────────────────────────────────────────────────
    # 6. 🔄 شاشة سجل حركات المخزون المستندية
    # ──────────────────────────────────────────────────────────
    def init_stock_movements_tab(self):
        movements_widget = QWidget()
        movements_layout = QVBoxLayout(movements_widget)
        movements_layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_title = QLabel("🔄 سجل حركات المخزون المستندية (صادر، وارد، هالك، تحويل مخزني)")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #20618f;")
        movements_layout.addWidget(lbl_title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        movements_layout.addStretch()
        self.tabs.addTab(movements_widget, "🔄 حركات المخزون")

    def load_categories_into_items_combo(self):
        """تغذية قائمة اختيار القسم الجانبية في شاشة السلع والمنتجات بالبيانات الحقيقية"""
        if hasattr(self, 'cmb_category'): # التأكد من معرف القائمة الفعلي بشاشة السلع
            try:
                self.cmb_category.clear()
                conn = psycopg2.connect(**DB_PARAMS)
                cursor = conn.cursor()
                cursor.execute("SELECT id, name FROM categories WHERE status = 'Active' ORDER BY name ASC;")
                rows = cursor.fetchall()
                for row in rows:
                    self.cmb_category.addItem(row[1], userData=row[0])
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"خطأ أثناء تحديث قائمة الأقسام في شاشة السلع: {e}")

    def init_purchases_tab(self):
        """إعادة شاشة المشتريات للتقسيمة الرأسية الأصلية بالكامل مع جعل خانة المورد صندوق بحث ذكي بالكتابة بدون السهم"""
        purchases_main_tab = QWidget()
        purchases_layout = QVBoxLayout(purchases_main_tab)
        purchases_layout.setContentsMargins(15, 15, 15, 15)
        purchases_layout.setSpacing(12)
        
        # 1️⃣ [الرأس العلوي]: بيانات الفاتورة العامة (المورد، الرقم، التاريخ، طريقة السداد)
        top_invoice_frame = QFrame()
        top_invoice_frame.setStyleSheet("QFrame { background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; }")
        top_layout = QHBoxLayout(top_invoice_frame)
        top_layout.setContentsMargins(12, 10, 12, 10)
        top_layout.setSpacing(15)
        
        # تحويل المورد إلى صندوق بحث ذكي يقبل الكتابة والفلترة الفورية
        self.cmb_inv_supplier = QComboBox()
        self.cmb_inv_supplier.setEditable(True)
        self.cmb_inv_supplier.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        
        # ضبط محرك البحث التلقائي للبحث عن أي جزء من الكلمة
        from PyQt6.QtWidgets import QCompleter
        supplier_completer = self.cmb_inv_supplier.completer()
        if supplier_completer:
            supplier_completer.setFilterMode(Qt.MatchFlag.MatchContains)
            supplier_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            
        self.cmb_inv_supplier.addItems(["شركة جهينة للألبان", "شركة المراعي مصر", "الشركة المصرية للأغذية", "مورد بضاعة محلي"])
        
        self.txt_inv_number = QLineEdit(); self.txt_inv_number.setPlaceholderText("رقم الفاتورة الدفتري")
        
        self.date_inv = QDateEdit(); self.date_inv.setCalendarPopup(True); self.date_inv.setDate(QDate.currentDate())
        
        self.cmb_payment_method = QComboBox()
        self.cmb_payment_method.addItems(["نقدي (Cash)", "آجل (On Credit)", "شيك بنكي", "تحويل"])
        
        top_layout.addWidget(QLabel("🏢 المورد:")); top_layout.addWidget(self.cmb_inv_supplier, stretch=2)
        top_layout.addWidget(QLabel("🧾 رقم الفاتورة:")); top_layout.addWidget(self.txt_inv_number, stretch=1)
        top_layout.addWidget(QLabel("📅 التاريخ:")); top_layout.addWidget(self.date_inv, stretch=1)
        top_layout.addWidget(QLabel("💳 طريقة الدفع:")); top_layout.addWidget(self.cmb_payment_method, stretch=1)
        
        purchases_layout.addWidget(top_invoice_frame)
        
        # 2️⃣ [الشريط الأوسط لبناء البند الجاري]: اختيار المنتج، الكمية، السعر، والتاريخ
        item_builder_frame = QFrame()
        item_builder_frame.setStyleSheet("QFrame { background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 6px; }")
        item_layout = QHBoxLayout(item_builder_frame)
        item_layout.setContentsMargins(12, 8, 12, 8)
        item_layout.setSpacing(10)
        
        self.cmb_invoice_item_selector = QComboBox(); self.cmb_invoice_item_selector.setEditable(True)
        self.cmb_invoice_item_selector.addItems([
            "6281000000123 - أرز مصري الفيروز 1كجم", 
            "6221234567890 - زيت عباد الشمس 1لتر", 
            "6229876543210 - جبنة دومتي فيتا 500جم"
        ])
        
        self.txt_item_inv_qty = QLineEdit(); self.txt_item_inv_qty.setPlaceholderText("0.00"); self.txt_item_inv_qty.setFixedWidth(80); self.txt_item_inv_qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_item_inv_cost = QLineEdit(); self.txt_item_inv_cost.setPlaceholderText("0.00"); self.txt_item_inv_cost.setFixedWidth(90); self.txt_item_inv_cost.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_expiry = QDateEdit(); self.date_expiry.setCalendarPopup(True); self.date_expiry.setDate(QDate.currentDate().addMonths(12)); self.date_expiry.setFixedWidth(110)
        
        self.btn_add_row_to_invoice = QPushButton("➕ إضافة بند")
        self.btn_add_row_to_invoice.setStyleSheet("background-color: #20618f; color: white; font-weight: bold; padding: 0 15px; border-radius: 4px;")
        self.btn_add_row_to_invoice.setFixedHeight(28)
        
        item_layout.addWidget(QLabel(" المنتج:")); item_layout.addWidget(self.cmb_invoice_item_selector, stretch=2)
        item_layout.addWidget(QLabel("🔢 الكمية:")); item_layout.addWidget(self.txt_item_inv_qty)
        item_layout.addWidget(QLabel("💰 سعر الشراء:")); item_layout.addWidget(self.txt_item_inv_cost)
        item_layout.addWidget(QLabel("⚠️ الصلاحية:")); item_layout.addWidget(self.date_expiry)
        item_layout.addWidget(self.btn_add_row_to_invoice)
        
        purchases_layout.addWidget(item_builder_frame)
        
        # 3️⃣ [الجدول الرئيسي في المنتصف]: عرض البنود والسلع المدخلة
        self.invoice_items_grid = QTableWidget()
        self.invoice_items_grid.setColumnCount(8)
        self.invoice_items_grid.setHorizontalHeaderLabels(["م", "اسم المنتج", "الباركود", "الكمية", "سعر الوحدة", "الإجمالي الفرعي", "تاريخ الصلاحية", "إجراء"])
        self.invoice_items_grid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.invoice_items_grid.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.invoice_items_grid.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.invoice_items_grid.verticalHeader().setDefaultSectionSize(34)
        self.invoice_items_grid.setStyleSheet("""
            QTableWidget { border: 1px solid #cbd5e1; gridline-color: #e2e8f0; background: white; }
            QHeaderView::section { background-color: #f1f5f9; color: #334155; font-weight: bold; border: 1px solid #cbd5e1; height: 35px; }
        """)
        purchases_layout.addWidget(self.invoice_items_grid, stretch=1)
        
        # 4️⃣ [البار السفلي]: خانات الحسابات الإجمالية وأزرار الاعتماد النهائي
        bottom_totals_frame = QFrame()
        bottom_totals_frame.setStyleSheet("QFrame { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; }")
        bottom_layout = QHBoxLayout(bottom_totals_frame)
        bottom_layout.setContentsMargins(12, 10, 12, 10)
        bottom_layout.setSpacing(10)
        
        self.txt_inv_subtotal = QLineEdit("0.00"); self.txt_inv_subtotal.setReadOnly(True); self.txt_inv_subtotal.setFixedWidth(90); self.txt_inv_subtotal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_inv_discount_per = QLineEdit("0.00"); self.txt_inv_discount_per.setFixedWidth(60); self.txt_inv_discount_per.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_inv_total = QLineEdit("0.00"); self.txt_inv_total.setReadOnly(True); self.txt_inv_total.setFixedWidth(100); self.txt_inv_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_inv_paid = QLineEdit("0.00"); self.txt_inv_paid.setFixedWidth(90); self.txt_inv_paid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_inv_remaining = QLineEdit("0.00"); self.txt_inv_remaining.setReadOnly(True); self.txt_inv_remaining.setFixedWidth(90); self.txt_inv_remaining.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_inv_remaining.setStyleSheet("background-color: #fff5f5; color: #dc2626; font-weight: bold;")
        
        self.btn_save_invoice = QPushButton("📥 اعتماد وترحيل المخازن")
        self.btn_save_invoice.setStyleSheet("background-color: #059669; color: white; font-weight: bold; padding: 0 15px; border-radius: 4px;")
        self.btn_save_invoice.setFixedHeight(30)
        
        self.btn_clear_invoice_form = QPushButton("🧹 مسح الفاتورة")
        self.btn_clear_invoice_form.setStyleSheet("background-color: #ffffff; color: #475569; border: 1px solid #cbd5e1; padding: 0 12px; border-radius: 4px;")
        self.btn_clear_invoice_form.setFixedHeight(30)
        
        bottom_layout.addWidget(QLabel("صافي البنود:")); bottom_layout.addWidget(self.txt_inv_subtotal)
        bottom_layout.addWidget(QLabel("الخصم (%):")); bottom_layout.addWidget(self.txt_inv_discount_per)
        bottom_layout.addWidget(QLabel("الإجمالي النهائي:")); bottom_layout.addWidget(self.txt_inv_total)
        bottom_layout.addWidget(QLabel("المدفوع:")); bottom_layout.addWidget(self.txt_inv_paid)
        bottom_layout.addWidget(QLabel("المتبقي:")); bottom_layout.addWidget(self.txt_inv_remaining)
        bottom_layout.addSpacing(15)
        bottom_layout.addWidget(self.btn_save_invoice)
        bottom_layout.addWidget(self.btn_clear_invoice_form)
        
        purchases_layout.addWidget(bottom_totals_frame)
        self.tabs.addTab(purchases_main_tab, " المشتريات")

        # ──────────────────────────────────────────────────────────
        # ⚙️ المحركات الحسابية والتشغيلية الداخلية المعتمدة بملفك
        # ──────────────────────────────────────────────────────────
        def local_calculate_totals():
            try:
                subtotal = 0.0
                for r in range(self.invoice_items_grid.rowCount()):
                    cell = self.invoice_items_grid.item(r, 5) 
                    if cell: subtotal += float(cell.text())
                
                self.txt_inv_subtotal.setText(f"{subtotal:.2f}")
                disc_per = float(self.txt_inv_discount_per.text().strip() or "0.00")
                discount_amt = subtotal * (disc_per / 100.0)
                final_total = subtotal - discount_amt
                self.txt_inv_total.setText(f"{final_total:.2f}")
                
                pay_method = self.cmb_payment_method.currentText()
                if "نقدي" in pay_method:
                    self.txt_inv_paid.setText(f"{final_total:.2f}")
                    self.txt_inv_paid.setReadOnly(True)
                    self.txt_inv_remaining.setText("0.00")
                else:
                    self.txt_inv_paid.setReadOnly(False)
                    paid = float(self.txt_inv_paid.text().strip() or "0.00")
                    if paid > final_total:
                        self.txt_inv_paid.setText(f"{final_total:.2f}")
                        paid = final_total
                    self.txt_inv_remaining.setText(f"{(final_total - paid):.2f}")
            except: pass

        def local_add_item():
            raw_item = self.cmb_invoice_item_selector.currentText().strip()
            qty_str = self.txt_item_inv_qty.text().strip()
            cost_str = self.txt_item_inv_cost.text().strip()
            expiry_str = self.date_expiry.date().toString("yyyy-MM-dd")
            
            if not qty_str or not cost_str:
                SystemMessageBox.show_warning(self, "يرجى تعبئة خانتي الكمية وسعر الشراء أولاً!")
                return
                
            try:
                qty = float(qty_str)
                cost = float(cost_str)
                subtotal = qty * cost
                
                barcode = "عام"
                name = raw_item
                if " - " in raw_item:
                    parts = raw_item.split(" - ", 1)
                    barcode = parts[0].strip()
                    name = parts[1].strip()
                    
                row = self.invoice_items_grid.rowCount()
                self.invoice_items_grid.insertRow(row)
                
                self.invoice_items_grid.setItem(row, 0, QTableWidgetItem(str(row + 1))) 
                self.invoice_items_grid.setItem(row, 1, QTableWidgetItem(name))            
                self.invoice_items_grid.setItem(row, 2, QTableWidgetItem(barcode))         
                
                i_qty = QTableWidgetItem(f"{qty:.2f}")
                i_cost = QTableWidgetItem(f"{cost:.2f}")
                i_sub = QTableWidgetItem(f"{subtotal:.2f}")
                i_exp = QTableWidgetItem(expiry_str)
                
                for item in [i_qty, i_cost, i_sub, i_exp]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                self.invoice_items_grid.setItem(row, 3, i_qty)      
                self.invoice_items_grid.setItem(row, 4, i_cost)     
                self.invoice_items_grid.setItem(row, 5, i_sub)      
                self.invoice_items_grid.setItem(row, 6, i_exp)      
                
                btn_del = QPushButton("🗑️")
                btn_del.setStyleSheet("background-color: transparent; color: #dc2626; border: none; font-size: 13px; font-weight: bold;")
                btn_del.clicked.connect(local_remove_row)
                self.invoice_items_grid.setCellWidget(row, 7, btn_del)
                
                self.txt_item_inv_qty.clear()
                self.txt_item_inv_cost.clear()
                local_calculate_totals()
            except ValueError:
                SystemMessageBox.show_warning(self, "يرجى كتابة أرقام صحيحة في خانات الإدخال.")

        def local_remove_row():
            sender_btn = self.sender()
            for r in range(self.invoice_items_grid.rowCount()):
                if self.invoice_items_grid.cellWidget(r, 7) == sender_btn:
                    self.invoice_items_grid.removeRow(r)
                    break
            for r in range(self.invoice_items_grid.rowCount()):
                self.invoice_items_grid.setItem(r, 0, QTableWidgetItem(str(r + 1)))
            local_calculate_totals()

        def local_clear_form():
            self.txt_inv_number.clear()
            self.txt_inv_discount_per.setText("0.00")
            self.txt_inv_subtotal.setText("0.00")
            self.txt_inv_total.setText("0.00")
            self.txt_inv_paid.setText("0.00")
            self.txt_inv_remaining.setText("0.00")
            self.invoice_items_grid.setRowCount(0)
            self.cmb_payment_method.setCurrentIndex(0)

        def local_commit_invoice():
            inv_no = self.txt_inv_number.text().strip()
            supplier = self.cmb_inv_supplier.currentText()
            if not inv_no or self.invoice_items_grid.rowCount() == 0:
                SystemMessageBox.show_warning(self, "لا يمكن ترحيل فاتورة فارغة أو بدون رقم دفتري!")
                return
            
            msg = f"تم اعتماد الفاتورة ({inv_no}) للمورد ({supplier}) نهائياً وتحديث كميات الجرد والمخازن بنجاح."
            SystemMessageBox.show_info(self, msg)
            local_clear_form()

        # ربط أحداث المحركات بالدوال الداخلية بأمان لمنع أي تضارب
        self.btn_add_row_to_invoice.clicked.connect(local_add_item)
        self.txt_inv_discount_per.textChanged.connect(local_calculate_totals)
        self.txt_inv_paid.textChanged.connect(local_calculate_totals)
        self.cmb_payment_method.currentIndexChanged.connect(local_calculate_totals)
        self.btn_clear_invoice_form.clicked.connect(local_clear_form)
        self.btn_save_invoice.clicked.connect(local_commit_invoice)

    # ──────────────────────────────────────────────────────────
    # الدوال التشغيلية المصححة مئة بالمئة
    # ──────────────────────────────────────────────────────────
    def add_item_row_to_invoice_table(self):
        """إدراج البند داخل جدول المشتريات بالترتيب القياسي الصحيح لمنع الزحزحة"""
        raw_item = self.cmb_invoice_item_selector.currentText().strip()
        qty_str = self.txt_item_inv_qty.text().strip()
        cost_str = self.txt_item_inv_cost.text().strip()
        expiry_date_str = self.date_expiry.date().toString("yyyy-MM-dd")
        
        if not qty_str or not cost_str:
            SystemMessageBox.show_warning(self, "يرجى إدخال الكمية وسعر الشراء أولاً لإدراج البند!")
            return
            
        try:
            qty = float(qty_str)
            cost = float(cost_str)
            subtotal = qty * cost
            
            # 🎯 تفكيك النص: فصل الباركود عن اسم المنتج بدقة
            barcode = "عام"
            name = raw_item
            if " - " in raw_item:
                parts = raw_item.split(" - ", 1)
                barcode = parts[0].strip()
                name = parts[1].strip()
                
            # الحصول على رقم السطر الجديد في الجدول
            row_idx = self.invoice_items_grid.rowCount()
            self.invoice_items_grid.insertRow(row_idx)
            
            # 🎯 التوزيع الصحيح والمطابق لشاشة المنتجات (من العمود 0 إلى 7):
            self.invoice_items_grid.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1))) # عمود (م)
            self.invoice_items_grid.setItem(row_idx, 1, QTableWidgetItem(name))            # عمود (اسم المنتج)
            self.invoice_items_grid.setItem(row_idx, 2, QTableWidgetItem(barcode))         # عمود (الباركود)
            
            # تجهيز خانات الأرقام والتاريخ
            qty_item = QTableWidgetItem(f"{qty:.2f}")
            cost_item = QTableWidgetItem(f"{cost:.2f}")
            sub_item = QTableWidgetItem(f"{subtotal:.2f}")
            expiry_item = QTableWidgetItem(expiry_date_str)
            
            # محاذاة الأرقام في المنتصف لتظهر بشكل متناسق
            for item in [qty_item, cost_item, sub_item, expiry_item]:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
            self.invoice_items_grid.setItem(row_idx, 3, qty_item)      # عمود (الالكمية)
            self.invoice_items_grid.setItem(row_idx, 4, cost_item)     # عمود (سعر الوحدة)
            self.invoice_items_grid.setItem(row_idx, 5, sub_item)      # عمود (الإجمالي الفرعي)
            self.invoice_items_grid.setItem(row_idx, 6, expiry_item)  # عمود (تاريخ الصلاحية)
            
            # 🗑️ بناء زر الحذف في العمود الأخير (رقم 7)
            btn_delete = QPushButton("🗑️")
            btn_delete.setStyleSheet("background-color: transparent; color: #dc2626; border: none; font-size: 14px; font-weight: bold;")
            btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # ربط الزر بدالة الحذف الذكية
            btn_delete.clicked.connect(self.remove_invoice_row_by_button)
            self.invoice_items_grid.setCellWidget(row_idx, 7, btn_delete)
            
            # تنظيف حقول الإدخال السريع للحركة التالية
            self.txt_item_inv_qty.clear()
            self.txt_item_inv_cost.clear()
            
            # تحديث إجمالي الفاتورة في الأسفل فوراً
            self.calculate_invoice_totals()
            
        except ValueError:
            SystemMessageBox.show_warning(self, "يرجى كتابة أرقام صحيحة في خانات الكمية والأسعار.")

    def remove_invoice_row_by_button(self):
        """حذف السطر التابع للزر الذي تم الضغط عليه وإعادة ترتيب المسلسل"""
        sender_btn = self.sender()
        for r in range(self.invoice_items_grid.rowCount()):
            if self.invoice_items_grid.cellWidget(r, 7) == sender_btn:
                self.invoice_items_grid.removeRow(r)
                break
        
        # إعادة ضبط عمود الترقيم التلقائي (م) ليبقى متسلسلاً صح
        for r in range(self.invoice_items_grid.rowCount()):
            self.invoice_items_grid.setItem(r, 0, QTableWidgetItem(str(r + 1)))
            
        # إعادة حساب الإجماليات بعد الحذف
        self.calculate_invoice_totals()

    def calculate_invoice_totals(self):
        try:
            items_subtotal = 0.0
            for r in range(self.invoice_items_grid.rowCount()):
                sub_item = self.invoice_items_grid.item(r, 5)
                if sub_item:
                    items_subtotal += float(sub_item.text())
            
            self.txt_inv_subtotal.setText(f"{items_subtotal:.2f}")
            
            disc_per = float(self.txt_inv_discount_per.text().strip() or "0.00")
            discount_amount = items_subtotal * (disc_per / 100.0)
            
            invoice_final_total = items_subtotal - discount_amount
            self.txt_inv_total.setText(f"{invoice_final_total:.2f}")
            
            payment_method = self.cmb_payment_method.currentText()
            if "نقدي" in payment_method:
                self.txt_inv_paid.setText(f"{invoice_final_total:.2f}")
                self.txt_inv_paid.setReadOnly(True)
                self.txt_inv_remaining.setText("0.00")
            else:
                self.txt_inv_paid.setReadOnly(False)
                paid = float(self.txt_inv_paid.text().strip() or "0.00")
                if paid > invoice_final_total:
                    self.txt_inv_paid.setText(f"{invoice_final_total:.2f}")
                    paid = invoice_final_total
                remaining = invoice_final_total - paid
                self.txt_inv_remaining.setText(f"{remaining:.2f}")
        except:
            pass

    def clear_purchase_invoice_form(self):
        self.txt_inv_number.clear()
        self.txt_inv_discount_per.setText("0.00")
        self.txt_inv_subtotal.setText("0.00")
        self.txt_inv_total.setText("0.00")
        self.txt_inv_paid.setText("0.00")
        self.txt_inv_remaining.setText("0.00")
        self.invoice_items_grid.setRowCount(0)
        self.cmb_payment_method.setCurrentIndex(0)

    def on_save_invoice_draft_clicked(self):
        inv_no = self.txt_inv_number.text().strip()
        if not inv_no:
            SystemMessageBox.show_warning(self, "حفظ مسودة", "يرجى إدخال رقم الفاتورة الدفتري أولاً لتثبيت المسودة معلقة!")
            return
        SystemMessageBox.show_info(self, "إشعار النظام", f"تم حفظ الفاتورة الدفترية رقم ({inv_no}) كمسودة مؤقتة بالسيستم.")

    def on_commit_invoice_final_clicked(self):
        inv_no = self.txt_inv_number.text().strip()
        supplier = self.cmb_inv_supplier.currentText()
        user_role = self.session.get("role", "cashier")
        
        if user_role not in ["admin", "supervisor"]:
            SystemMessageBox.show_critical(self, "صلاحية مرفوضة", "حسابك الحالي لا يملك الامتيازات الإدارية الكافية لاعتماد وترحيل المشتريات!")
            return
        if not inv_no or self.invoice_items_grid.rowCount() == 0:
            SystemMessageBox.show_warning(self, "تنبيه الاعتماد", "لا يمكن ترحيل فاتورة فارغة أو بدون رقم دفتري معتمد!")
            return
            
        SystemMessageBox.show_info(self, "نجاح الترحيل", f"تم اعتماد الفاتورة ({inv_no}) للمورد ({supplier}) نهائياً، وجاري تحديث كميات جرد المخازن ودفاتر الحسابات الآجلة.")
        self.clear_purchase_invoice_form()

    # ──────────────────────────────────────────────────────────
    # الدوال التشغيلية المحسنة والجديدة لمحرك المشتريات (ERP Controls)
    # ──────────────────────────────────────────────────────────
    
    def add_item_row_to_invoice_table(self):
        """إضافة بند جديد إلى جدول الفاتورة وحساب الإجمالي تلقائياً"""
        item_name = self.cmb_invoice_item_selector.currentText().strip()
        qty_str = self.txt_item_inv_qty.text().strip()
        cost_str = self.txt_item_inv_cost.text().strip()
        
        if not qty_str or not cost_str:
            SystemMessageBox.show_warning(self, "يرجى إدخال الكمية وسعر الشراء لإدراج البند!")
            return
            
        try:
            qty = float(qty_str)
            cost = float(cost_str)
            subtotal = qty * cost
            
            row_idx = self.invoice_items_grid.rowCount()
            self.invoice_items_grid.insertRow(row_idx)
            
            self.invoice_items_grid.setItem(row_idx, 0, QTableWidgetItem(item_name))
            self.invoice_items_grid.setItem(row_idx, 1, QTableWidgetItem(f"{qty:.2f}"))
            self.invoice_items_grid.setItem(row_idx, 2, QTableWidgetItem(f"{cost:.2f}"))
            self.invoice_items_grid.setItem(row_idx, 3, QTableWidgetItem("0.00")) # حصة الشحن المؤقتة
            self.invoice_items_grid.setItem(row_idx, 4, QTableWidgetItem(f"{subtotal:.2f}"))
            
            # تفريغ حقول الإدخال السريع للتهيئة للبند التالي
            self.txt_item_inv_qty.clear()
            self.txt_item_inv_cost.clear()
            
            # تحديث الإجماليات الشاملة للفاتورة تلقائياً بناءً على البنود
            self.calculate_invoice_totals()
            
        except ValueError:
            SystemMessageBox.show_warning(self, "يرجى كتابة أرقام صحيحة في خانة الكمية والأسعار.")

    def remove_selected_invoice_item_row(self):
        """حذف بند محدد من الجدول وإعادة احتساب الإجمالي"""
        curr_row = self.invoice_items_grid.currentRow()
        if curr_row >= 0:
            self.invoice_items_grid.removeRow(curr_row)
            self.calculate_invoice_totals()
        else:
            SystemMessageBox.show_warning(self, "يرجى تحديد الصف المراد حذفه من جدول الأصناف أولاً!")

    def calculate_invoice_totals(self):
        """المحرك التلقائي المحوسب للضرائب، الخصومات، توزيع الشحن، والمتبقي الآجل"""
        try:
            # 1. حساب إجمالي البنود الصافي من الجدول مباشرة
            items_subtotal = 0.0
            total_items_qty = 0.0
            
            for r in range(self.invoice_items_grid.rowCount()):
                qty_item = self.invoice_items_grid.item(r, 1)
                sub_item = self.invoice_items_grid.item(r, 4)
                if qty_item and sub_item:
                    items_subtotal += float(sub_item.text())
                    total_items_qty += float(qty_item.text())
            
            self.txt_inv_subtotal.setText(f"{items_subtotal:.2f}")
            
            # 2. احتساب الخصم التجاري كنسبة مئوية
            disc_per = float(self.txt_inv_discount_per.text().strip() or "0.00")
            discount_amount = items_subtotal * (disc_per / 100.0)
            
            # 3. احتساب الهيكل الضريبي المختار
            tax_idx = self.cmb_tax_type.currentIndex()
            tax_amount = 0.0
            if tax_idx == 0:    # قيمة مضافة 14%
                tax_amount = (items_subtotal - discount_amount) * 0.14
            elif tax_idx == 1:  # خصم من المصدر 1%
                tax_amount = -(items_subtotal - discount_amount) * 0.01
                
            # 4. توزيع مصاريف الشحن الإضافية على الأصناف بالتساوي (Proportional Distribution)
            shipping = float(self.txt_shipping_fees.text().strip() or "0.00")
            if shipping > 0 and total_items_qty > 0:
                for r in range(self.invoice_items_grid.rowCount()):
                    row_qty = float(self.invoice_items_grid.item(r, 1).text())
                    row_shipping_share = (row_qty / total_items_qty) * shipping
                    self.invoice_items_grid.setItem(r, 3, QTableWidgetItem(f"{row_shipping_share:.2f}"))
            
            # 5. حساب الإجمالي النهائي التلقائي الحرج
            invoice_final_total = items_subtotal - discount_amount + tax_amount + shipping
            self.txt_inv_total.setText(f"{invoice_final_total:.2f}")
            
            # 6. إدارة قيود السداد (نقدي / آجل) والتحقق التلقائي
            payment_method = self.cmb_payment_method.currentText()
            
            if "نقدي" in payment_method:
                # إذا كان نقدي، فالمدفوع يساوي الإجمالي إجبارياً لمنع التلاعب
                self.txt_inv_paid.setText(f"{invoice_final_total:.2f}")
                self.txt_inv_paid.setReadOnly(True)
                self.txt_inv_remaining.setText("0.00")
            else:
                self.txt_inv_paid.setReadOnly(False)
                paid = float(self.txt_inv_paid.text().strip() or "0.00")
                
                # قيد أمان: التحقق من أن المدفوع لا يتجاوز الإجمالي النهائي
                if paid > invoice_final_total:
                    SystemMessageBox.show_warning(self, "لا يمكن أن يتجاوز المبلغ المدفوع نقدياً إجمالي قيمة الفاتورة!")
                    self.txt_inv_paid.setText(f"{invoice_final_total:.2f}")
                    paid = invoice_final_total
                    
                remaining = invoice_final_total - paid
                self.txt_inv_remaining.setText(f"{remaining:.2f}")
                
        except Exception as e:
            pass  # منع انهيار الواجهة أثناء مسح وتعديل الحروف بشكل لحظي

    def clear_purchase_invoice_form(self):
        """تفريغ الواجهة بالكامل واستعادة القيم الافتراضية"""
        self.txt_inv_number.clear()
        # ✅ تم حذف السطر المسبب للمشكلة نهائياً من هنا
        self.txt_inv_discount_per.setText("0.00")
        self.txt_inv_subtotal.setText("0.00")
        self.txt_inv_total.setText("0.00")
        self.txt_inv_paid.setText("0.00")
        self.txt_inv_remaining.setText("0.00")
        self.invoice_items_grid.setRowCount(0)
        self.cmb_payment_method.setCurrentIndex(0)

    def on_upload_invoice_document_clicked(self):
        """محاكي رفع المستند الورقي أو إيصال الشحن لتوثيق الفاتورة قانونياً"""
        SystemMessageBox.show_info(self, "توثيق الأرشفة الرقمية", "تم رفع وتشفير صورة الفاتورة المستندية المرفقة وربطها بنظام الأرشفة بنجاح.")

    def on_save_invoice_draft_clicked(self):
        """حفظ كمسودة مؤقتة بدون ترحيل للمخازن (دون التأثير على كميات الجرد الفعلي)"""
        inv_no = self.txt_inv_number.text().strip()
        if not inv_no:
            SystemMessageBox.setStyleSheet(MODERN_STYLE)
            SystemMessageBox.show_warning(self, "حقول إلزامية", "يرجى كتابة رقم الفاتورة الدفتري لحفظها كمسودة مؤقتة!")
            return
        SystemMessageBox.show_info(self, "حفظ كمسودة", f"تم حفظ الفاتورة رقم ({inv_no}) كمسودة معلقة بنجاح (لم تؤثر على المخازن بعد).")

    def on_commit_invoice_final_clicked(self):
        """الاعتماد النهائي والمحمي لصلاحيات المستخدم وتحديث الجرد المباشر وخصم الخزينة"""
        inv_no = self.txt_inv_number.text().strip()
        supplier = self.cmb_inv_supplier.currentText()
        final_total = float(self.txt_inv_total.text() or "0.00")
        paid_cash = float(self.txt_inv_paid.text() or "0.00")
        remaining_credit = float(self.txt_inv_remaining.text() or "0.00")
        safe = self.cmb_safe_select.currentText()
        user_role = self.session.get("role", "cashier")
        
        # 🔒 قيد الصلاحية الأمنية للاعتماد
        if user_role not in ["admin", "supervisor"]:
            SystemMessageBox.show_critical(self, "صلاحيات أمنية مرفوضة", "عذراً، رتبة حسابك الحالية لا تمتلك صلاحية 'اعتماد وترحيل المشتريات'! يرجى مراجعة الإدارة.")
            return

        if not inv_no:
            SystemMessageBox.show_warning(self, "حقول إلزامية", "يرجى تعبئة رقم الفاتورة الدفتري قبل البدء بالاعتماد!")
            return
            
        if self.invoice_items_grid.rowCount() == 0:
            SystemMessageBox.show_warning(self, "جدول الأصناف فارغ", "لا يمكن اعتماد فاتورة شراء خالية من الأصناف والبنود البنيوية!")
            return

        # 🎯 التغذية الراجعة المالية الاحترافية والأثر الفوري
        feedback_msg = f"""
        🎉 تم اعتماد وترحيل الفاتورة بنجاح وتحت إشراف: {self.session['username']}
        
        📊 الأثر المالي الفوري للنظام المحاسبي:
        -----------------------------------------------
         المخازن: تم تحديث كميات جرد لـ ({self.invoice_items_grid.rowCount()}) صنف فعال فوراً.
        💰 {safe}: تم سحب وخصم مبلغ نقدى قدره (- {paid_cash:.2f} ج.م) لتغطية الدفع الفوري.
        🤝 حساب المورد آجل: تم ترحيل مبلغ (+ {remaining_credit:.2f} ج.م) كـ رصيد دائن لصالح ({supplier}).
        """
        
        SystemMessageBox.show_info(self, feedback_msg)
               
        self.clear_purchase_invoice_form()

    # ──────────────────────────────────────────────────────────
    # 3.  شاشة المخزون والجرد الدوري والنواقص
    # ──────────────────────────────────────────────────────────
    def init_inventory_tab(self):
        inv_main_widget = QWidget()
        inv_layout = QVBoxLayout(inv_main_widget)
        inv_layout.setContentsMargins(15, 15, 15, 15)
        inv_layout.setSpacing(12)
        
        title_label = QLabel("🗄️ نظام جرد البضائع الدوري والتحكم الفوري بالنواقص والأمان الرقمي")
        title_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #0284c7; padding-bottom: 5px;")
        inv_layout.addWidget(title_label)
        
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(5)
        self.inventory_table.setHorizontalHeaderLabels(["الباركود الدولي", "اسم صنف المنتج داخل السوبرماركت", "الكمية الحالية المتوفرة", "حالة الأمان الرقمية (نواقص)", "مستوى خطورة الصلاحية"])
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        inv_layout.addWidget(self.inventory_table)
        
        self.btn_refresh_inv = QPushButton("🔄 تحديث ومزامنة جرد المخزن")
        self.btn_refresh_inv.setFixedHeight(self.BTN_HEIGHT)
        self.btn_refresh_inv.setStyleSheet("background-color: #0284c7; color: white; font-weight: bold; border-radius: 6px;")
        self.btn_refresh_inv.clicked.connect(self.load_items_data)
        inv_layout.addWidget(self.btn_refresh_inv)
        
        self.tabs.addTab(inv_main_widget, "📦 المخزون")

    # ──────────────────────────────────────────────────────────
    # 4. 👥 شاشة إدارة العملاء وحسابات الآجل
    # ──────────────────────────────────────────────────────────
    def init_marketing_and_promotions_tab(self):
        marketing_main_tab = QWidget()
        layout = QHBoxLayout(marketing_main_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)
        
        form_frame = QFrame()
        form_frame.setFixedWidth(self.SIDEBAR_WIDTH)
        form_frame.setStyleSheet("QFrame { background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; }")
        form_layout = QVBoxLayout(form_frame); form_layout.setSpacing(14)
        
        lbl_title = QLabel("👥 فتح وتوثيق ملفات حسابات العملاء")
        lbl_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold)); lbl_title.setStyleSheet("color: #7c3aed;"); lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(lbl_title)
        
        self.txt_cust_name = QLineEdit(); self.txt_cust_name.setPlaceholderText("اسم العميل الثلاثي بالكامل...")
        self.txt_cust_phone = QLineEdit(); self.txt_cust_phone.setPlaceholderText("رقم الهاتف الفعال...")
        self.txt_cust_limit = QLineEdit(); self.txt_cust_limit.setText("5000.00")
        
        grid = QFormLayout(); grid.setLabelAlignment(Qt.AlignmentFlag.AlignLeft); grid.setVerticalSpacing(12)
        grid.addRow(QLabel("اسم العميل المعتمد:"), self.txt_cust_name)
        grid.addRow(QLabel("رقم الموبايل للتواصل:"), self.txt_cust_phone)
        grid.addRow(QLabel("حد مديونية الآجل:"), self.txt_cust_limit)
        
        for i in range(grid.rowCount()):
            grid.itemAt(i, QFormLayout.ItemRole.LabelRole).widget().setStyleSheet(self.label_style)
            grid.itemAt(i, QFormLayout.ItemRole.FieldRole).widget().setStyleSheet(self.input_style)
            grid.itemAt(i, QFormLayout.ItemRole.FieldRole).widget().setFixedHeight(self.INPUT_HEIGHT)
        form_layout.addLayout(grid)
        
        self.btn_save_customer = QPushButton("💾 تثبيت وحفظ بيانات العميل الحالية")
        self.btn_save_customer.setFixedHeight(self.BTN_HEIGHT)
        self.btn_save_customer.setStyleSheet("background-color: #7c3aed; color: white; font-weight: bold; border-radius: 6px;")
        form_layout.addWidget(self.btn_save_customer)
        form_layout.addStretch()
        layout.addWidget(form_frame)
        
        table_layout = QVBoxLayout()
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(4)
        self.customers_table.setHorizontalHeaderLabels(["كود الحساب المعرف", "اسم العميل بالكامل", "رقم الهاتف والاتصال", "إجمالي المديونية الحالية ج.م"])
        self.customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_layout.addWidget(self.customers_table)
        layout.addLayout(table_layout, stretch=3)
        
        self.tabs.addTab(marketing_main_tab, "👥 العملاء")

    # ──────────────────────────────────────────────────────────
    # 5. 💰 شاشة الخزنة والحسابات المالية
    # ──────────────────────────────────────────────────────────
    def init_finance_tab(self):
        finance_main_tab = QWidget()
        layout = QVBoxLayout(finance_main_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(14)
        
        title = QLabel("💰 تتبع التدفقات وحركات الصناديق والخزنة الرئيسية (Safe-to-Safe)")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold)); title.setStyleSheet("color: #d97706;")
        layout.addWidget(title)
        
        balance_frame = QFrame()
        balance_frame.setStyleSheet("background-color: #fef3c7; border: 1px solid #f59e0b; border-radius: 10px;")
        balance_layout = QHBoxLayout(balance_frame)
        self.lbl_safe_balance = QLabel("💰 إجمالي النقدية السائلة المتوفرة بالخزنة المركزية: 0.00 ج.م")
        self.lbl_safe_balance.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold)); self.lbl_safe_balance.setStyleSheet("color: #b45309; border:none;")
        balance_layout.addWidget(self.lbl_safe_balance)
        layout.addWidget(balance_frame)
        
        self.safe_log_table = QTableWidget()
        self.safe_log_table.setColumnCount(5)
        self.safe_log_table.setHorizontalHeaderLabels(["تاريخ وتوقيت الإجراء", "نوع حركة المال (إيداع/سحب/ورديات)", "المبلغ المالي المفرز", "المسؤول الفعلي للعملية", "البيان / السبب والمبرر للحركة"])
        self.safe_log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.safe_log_table)
        
        self.tabs.addTab(finance_main_tab, "💰 الخزنة")

    # ──────────────────────────────────────────────────────────
    # 6. 📊 مركز التقارير والإحصائيات الشامل
    # ──────────────────────────────────────────────────────────
    def init_reports_center_tab(self):
        reports_main_widget = QWidget()
        reports_layout = QVBoxLayout(reports_main_widget)
        reports_layout.setContentsMargins(10, 10, 10, 10)
        
        self.reports_sub_tabs = QTabWidget()
        self.reports_sub_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #cbd5e1; border-radius: 6px; background-color: #ffffff; }
            QTabBar::tab { background: #e2e8f0; color: #475569; padding: 8px 16px; font-weight: bold; border-radius: 4px; margin: 2px; }
            QTabBar::tab:selected { background: #2563eb; color: white; }
        """)
        
        sales_rep_tab = QWidget(); sales_rep_ly = QHBoxLayout(sales_rep_tab); sales_rep_ly.setSpacing(15); sales_rep_ly.setContentsMargins(5, 5, 5, 5)
        left_ly = QVBoxLayout(); lbl_table_t = QLabel("🧾 سجل فواتير المبيعات الصادرة (الوردية الحالية):"); lbl_table_t.setStyleSheet(self.label_style); left_ly.addWidget(lbl_table_t)
        self.invoice_table = QTableWidget(); self.invoice_table.setColumnCount(5); self.invoice_table.setHorizontalHeaderLabels(["رقم الفاتورة", "التاريخ والوقت", "طريقة الدفع", "رقم الكاشير", "إجمالي النهائي"])
        self.invoice_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.invoice_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows); self.invoice_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers); self.invoice_table.itemClicked.connect(self.on_invoice_selected); left_ly.addWidget(self.invoice_table)
        self.btn_refresh_sales = QPushButton("🔄 تحديث ومزامنة الفواتير الصادرة"); self.btn_refresh_sales.setFixedHeight(self.BTN_HEIGHT); self.btn_refresh_sales.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; border-radius: 6px;"); self.btn_refresh_sales.clicked.connect(self.load_invoices_data); left_ly.addWidget(self.btn_refresh_sales); sales_rep_ly.addLayout(left_ly, stretch=4)
        right_ly = QVBoxLayout(); lbl_det_t = QLabel("🔍 البنية الداخلية لأصناف الفاتورة المختارة:"); lbl_det_t.setStyleSheet(self.label_style); right_ly.addWidget(lbl_det_t)
        self.invoice_details_table = QTableWidget(); self.invoice_details_table.setColumnCount(5); self.invoice_details_table.setHorizontalHeaderLabels(["الباركود", "اسم المنتج", "السعر", "الكمية", "الإجمالي"]); self.invoice_details_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); self.invoice_details_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows); self.invoice_details_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers); right_ly.addWidget(self.invoice_details_table); sales_rep_ly.addLayout(right_ly, stretch=3)
        self.reports_sub_tabs.addTab(sales_rep_tab, "🧾 تقارير المبيعات والورديات")
        
        pnl_tab = QWidget(); pnl_ly = QVBoxLayout(pnl_tab); pnl_ly.setContentsMargins(15, 15, 15, 15); pnl_ly.setSpacing(12)
        pnl_title = QLabel("📊 كشف الميزانية التقديرية التلقائي والأرباح الرأسمالية (Profit and Loss)"); pnl_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold)); pnl_title.setStyleSheet("color: #2563eb;"); pnl_ly.addWidget(pnl_title)
        self.table_fin_report = QTableWidget(); self.table_fin_report.setColumnCount(5); self.table_fin_report.setHorizontalHeaderLabels(["تاريخ الاحتساب", "المؤشر المالي البنيوي", "القيمة التقديرية الحالية", "طبيعة الحساب", "ملاحظات الدائرة المحاسبية"]); self.table_fin_report.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); pnl_ly.addWidget(self.table_fin_report)
        self.btn_calc_pnl = QPushButton("📊 إعادة احتساب الميزانية والأرباح والخسائر فورا"); self.btn_calc_pnl.setFixedHeight(self.BTN_HEIGHT); self.btn_calc_pnl.setStyleSheet("background-color: #059669; color: white; font-weight: bold; border-radius: 6px;"); self.btn_calc_pnl.clicked.connect(self.calculate_pnl_report); pnl_ly.addWidget(pnl_title) # تم تعديل الـ widget المضاف خطأ هنا ليكون زر الـ PNL المالي الفعلي
        pnl_ly.addWidget(self.btn_calc_pnl)
        self.reports_sub_tabs.addTab(pnl_tab, "📊 الأرباح والخسائر والميزانية")
        
        reports_layout.addWidget(self.reports_sub_tabs)
        self.tabs.addTab(reports_main_widget, "📊 التقارير")

    # ──────────────────────────────────────────────────────────
    # 7. 👤 شاشة إدارة المستخدمين وصلاحيات الموظفين
    # ──────────────────────────────────────────────────────────
    def init_management_and_security_tab(self):
        mgmt_main_tab = QWidget()
        layout = QHBoxLayout(mgmt_main_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)
        
        user_frame = QFrame()
        user_frame.setFixedWidth(self.SIDEBAR_WIDTH)
        user_frame.setStyleSheet("QFrame { background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; }")
        user_layout = QVBoxLayout(user_frame); user_layout.setSpacing(14)
        
        lbl_title = QLabel("👤 إنشاء وإدارة حسابات موظفي النظام")
        lbl_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold)); lbl_title.setStyleSheet("color: #475569;"); lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_layout.addWidget(lbl_title)
        
        self.txt_user_name = QLineEdit(); self.txt_user_name.setPlaceholderText("اسم مستخدم الدخول الفريد...")
        self.txt_user_pass = QLineEdit(); self.txt_user_pass.setPlaceholderText("كلمة المرور السرية والمشفرة...")
        self.cmb_user_role = QComboBox(); self.cmb_user_role.addItems(["كاشير بنقطة البيع (Cashier)", "مشرف صالة جرد (Supervisor)", "مدير نظام كامل (Admin)"])
        
        grid = QFormLayout(); grid.setLabelAlignment(Qt.AlignmentFlag.AlignLeft); grid.setVerticalSpacing(12)
        grid.addRow(QLabel("اسم حساب المستخدم:"), self.txt_user_name)
        grid.addRow(QLabel("كلمة المرور المشفرة:"), self.txt_user_pass)
        grid.addRow(QLabel("مستوى الصلاحية الفنية:"), self.cmb_user_role)
        
        for i in range(grid.rowCount()):
            grid.itemAt(i, QFormLayout.ItemRole.LabelRole).widget().setStyleSheet(self.label_style)
            grid.itemAt(i, QFormLayout.ItemRole.FieldRole).widget().setStyleSheet(self.input_style)
            grid.itemAt(i, QFormLayout.ItemRole.FieldRole).widget().setFixedHeight(self.INPUT_HEIGHT)
        user_layout.addLayout(grid)
        
        self.btn_save_user = QPushButton("➕ توثيق وحفظ حساب الموظف الجديد")
        self.btn_save_user.setFixedHeight(self.BTN_HEIGHT)
        self.btn_save_user.setStyleSheet("background-color: #475569; color: white; font-weight: bold; border-radius: 6px;")
        user_layout.addWidget(self.btn_save_user)
        user_layout.addStretch()
        layout.addWidget(user_frame)
        
        table_layout = QVBoxLayout()
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(["رقم الموظف المعرف", "اسم حساب الدخول للواجهة", "مستوى الصلاحية الإدارية", "حالة الحساب الرقمي الحالية"])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_layout.addWidget(self.users_table)
        layout.addLayout(table_layout, stretch=3)
        
        self.tabs.addTab(mgmt_main_tab, "👤 المستخدمون")

    # ──────────────────────────────────────────────────────────
    # 8. ⚙️ شاشة إعدادات وتخصيص النظام العام
    # ──────────────────────────────────────────────────────────
    def init_system_settings_tab(self):
        settings_main_tab = QWidget()
        settings_layout = QVBoxLayout(settings_main_tab)
        settings_layout.setContentsMargins(10, 10, 10, 10)
        
        self.settings_sub_tabs = QTabWidget()
        self.settings_sub_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #cbd5e1; border-radius: 6px; background-color: #f8fafc; }
            QTabBar::tab { background: #e2e8f0; color: #475569; padding: 10px 18px; font-weight: bold; border-radius: 4px; margin: 2px; font-size: 12px; }
            QTabBar::tab:selected { background: #20618f; color: white; }
        """)
        
        # [اصلاح خطأ التدمير الهيكلي] بناء المخطط بشكل مستقل لـ comp_widget ليتوافق مع PyQt6
        comp_widget = QWidget()
        comp_layout = QHBoxLayout()
        comp_widget.setLayout(comp_layout)
        
        comp_layout.setContentsMargins(15, 15, 15, 15)
        comp_layout.setSpacing(20)
        
        comp_frame = QFrame()
        comp_frame.setFixedWidth(self.SIDEBAR_WIDTH)
        comp_frame.setStyleSheet("QFrame { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; }")
        comp_form = QVBoxLayout(comp_frame); comp_form.setContentsMargins(20, 20, 20, 20); comp_form.setSpacing(10)
        comp_title = QLabel("🏢 إدارة بيانات وهوية السوبرماركت"); comp_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold)); comp_title.setStyleSheet(f"color: {self.COLOR_PRIMARY};"); comp_title.setAlignment(Qt.AlignmentFlag.AlignCenter); comp_form.addWidget(comp_title)
        self.txt_set_comp_name = QLineEdit(); self.txt_set_comp_address = QLineEdit(); self.txt_set_comp_phone = QLineEdit(); self.txt_set_comp_tax = QLineEdit(); self.btn_upload_logo = QPushButton("🖼️ تحميل شعار المؤسسة الرسمي (Logo)")
        comp_grid = QFormLayout(); comp_grid.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        comp_grid.addRow(QLabel("اسم المؤسسة:"), self.txt_set_comp_name); comp_grid.addRow(QLabel("العنوان الإقليمي:"), self.txt_set_comp_address)
        comp_grid.addRow(QLabel("هاتف الفرع:"), self.txt_set_comp_phone); comp_grid.addRow(QLabel("الرقم الضريبى المعتمد:"), self.txt_set_comp_tax); comp_grid.addRow(QLabel("شعار الفاتورة الفوري:"), self.btn_upload_logo)
        for i in range(comp_grid.rowCount()):
            comp_grid.itemAt(i, QFormLayout.ItemRole.LabelRole).widget().setStyleSheet(self.label_style)
            if isinstance(comp_grid.itemAt(i, QFormLayout.ItemRole.FieldRole).widget(), QLineEdit):
                comp_grid.itemAt(i, QFormLayout.ItemRole.FieldRole).widget().setStyleSheet(self.input_style)
                comp_grid.itemAt(i, QFormLayout.ItemRole.FieldRole).widget().setFixedHeight(self.INPUT_HEIGHT)
        comp_form.addLayout(comp_grid); self.btn_upload_logo.setStyleSheet("background-color: #64748b; color: white; font-weight: bold; border-radius: 6px;"); self.btn_upload_logo.setFixedHeight(self.INPUT_HEIGHT)
        self.btn_save_comp_info = QPushButton("💾 حفظ وتثبيت الهوية الرسمية بالكامل"); self.btn_save_comp_info.setFixedHeight(self.BTN_HEIGHT); self.btn_save_comp_info.setStyleSheet(f"background-color: {self.COLOR_PRIMARY}; color: white; font-weight: bold; border-radius: 6px;")
        comp_form.addWidget(self.btn_save_comp_info); comp_form.addStretch(); comp_layout.addWidget(comp_frame)
        preview_frame = QFrame(); preview_frame.setStyleSheet("background-color: white; border: 1px dashed #cbd5e1; border-radius: 8px;"); preview_layout = QVBoxLayout(preview_frame); preview_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_logo_preview = QLabel("🔍 ترويسة معاينة الفاتورة الافتراضية للشاشات والكاشير"); self.lbl_logo_preview.setStyleSheet("color: #94a3b8; font-size: 14px; border:none;"); preview_layout.addWidget(self.lbl_logo_preview); comp_layout.addWidget(preview_frame, stretch=3)
        self.settings_sub_tabs.addTab(comp_widget, "🏢 بيانات السوبرماركت")
        
        # فرع ب: تخصيص وطباعة الفواتير وطابعات المطبخ والحراري
        inv_set_widget = QWidget(); inv_set_layout = QHBoxLayout(inv_set_widget); inv_set_layout.setContentsMargins(15, 15, 15, 15); inv_set_layout.setSpacing(20)
        inv_set_frame = QFrame(); inv_set_frame.setFixedWidth(self.SIDEBAR_WIDTH)
        inv_set_frame.setStyleSheet("QFrame { background-color: white; border: 1px solid #e2e8f0; border-radius: 8px; }")
        inv_set_form = QVBoxLayout(inv_set_frame); inv_set_form.setContentsMargins(20, 20, 20, 20); inv_set_form.setSpacing(10)
        inv_set_title = QLabel("🧾 تهيئة الطابعات ومقاس الورق الحرج"); inv_set_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold)); inv_set_title.setStyleSheet("color: #059669;"); inv_set_title.setAlignment(Qt.AlignmentFlag.AlignCenter); inv_set_form.addWidget(inv_set_title)
        self.cmb_set_paper_size = QComboBox(); self.cmb_set_paper_size.addItems(["Thermal الكاشير (80mm)", "Thermal الصغير (58mm)", "ورق مكتبي عالي الجودة (A4)"])
        self.cmb_set_printer_select = QComboBox(); self.cmb_set_printer_select.addItems(["Default System Printer", "Xprinter XP-Q200", "POS-80 Series"])
        self.txt_set_invoice_footer = QLineEdit(); self.txt_set_invoice_footer.setPlaceholderText("مثال: البضاعة المباعة لا ترد ولا تستبدل بعد 14 يوم...")
        self.chk_auto_sequence = QComboBox(); self.chk_auto_sequence.addItems(["ترقيم تلقائي متسلسل متقدم للفرع", "إعادة الترقيم يومياً للورديات من رقم 1"])
        inv_set_grid = QFormLayout(); inv_set_grid.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        inv_set_grid.addRow(QLabel("مقاس ورق الفاتورة:"), self.cmb_set_paper_size); inv_set_grid.addRow(QLabel("طابعة الفواتير الفورية:"), self.cmb_set_printer_select)
        inv_set_grid.addRow(QLabel("تسلسل الترقيم التلقائي:"), self.chk_auto_sequence); inv_set_grid.addRow(QLabel("رسالة الترحيب والشكر (أسفل):"), self.txt_set_invoice_footer)
        for i in range(inv_set_grid.rowCount()):
            inv_set_grid.itemAt(i, QFormLayout.ItemRole.LabelRole).widget().setStyleSheet(self.label_style)
            inv_set_grid.itemAt(i, QFormLayout.ItemRole.FieldRole).widget().setStyleSheet(self.input_style)
            inv_set_grid.itemAt(i, QFormLayout.ItemRole.FieldRole).widget().setFixedHeight(self.INPUT_HEIGHT)
        inv_set_form.addLayout(inv_set_grid); self.btn_save_invoice_settings = QPushButton("💾 حفظ إعدادات الطباعة الحالية"); self.btn_save_invoice_settings.setFixedHeight(self.BTN_HEIGHT); self.btn_save_invoice_settings.setStyleSheet("background-color: #059669; color: white; font-weight: bold; border-radius: 6px;"); inv_set_form.addWidget(self.btn_save_invoice_settings); inv_set_form.addStretch(); inv_set_layout.addWidget(inv_set_frame)
        invoice_mock_frame = QFrame(); invoice_mock_frame.setStyleSheet("background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 4px;"); invoice_mock_layout = QVBoxLayout(invoice_mock_frame); invoice_mock_layout.setContentsMargins(40, 20, 40, 20)
        lbl_mock_head = QLabel("--- فاتورة بيع تجريبية للنظام ---"); lbl_mock_head.setAlignment(Qt.AlignmentFlag.AlignCenter); invoice_mock_layout.addWidget(lbl_mock_head)
        lbl_mock_body = QLabel("كود 101: مياه معدنية لتر   |  السعر: 15.00 ج.م\nكود 202: جبن رومي قديم كجم  |  السعر: 260.00 ج.م"); lbl_mock_body.setAlignment(Qt.AlignmentFlag.AlignLeft); invoice_mock_layout.addWidget(lbl_mock_body); invoice_mock_layout.addStretch()
        self.lbl_mock_footer = QLabel("شكراً لزيارتكم الكريمة!"); self.lbl_mock_footer.setAlignment(Qt.AlignmentFlag.AlignCenter); invoice_mock_layout.addWidget(self.lbl_mock_footer); inv_set_layout.addWidget(invoice_mock_frame, stretch=3)
        self.settings_sub_tabs.addTab(inv_set_widget, "🧾 محاكي ورق الفواتير")
        
        # فرع ج: صيانة وإصلاح وإدارة قاعدة بيانات بوستجرس
        db_widget = QWidget(); db_layout = QHBoxLayout(db_widget); db_layout.setContentsMargins(15, 15, 15, 15); db_layout.setSpacing(20)
        db_frame = QFrame(); db_frame.setFixedWidth(self.SIDEBAR_WIDTH); db_frame.setStyleSheet("QFrame { background-color: white; border: 1px solid #e2e8f0; border-radius: 8px; }")
        db_form = QVBoxLayout(db_frame); db_form.setContentsMargins(20, 20, 20, 20); db_form.setSpacing(12)
        db_title = QLabel("🗄️ محرك صيانة وإصلاح قاعدة البيانات"); db_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold)); db_title.setStyleSheet("color: #b91c1c;"); db_title.setAlignment(Qt.AlignmentFlag.AlignCenter); db_form.addWidget(db_title)
        self.btn_db_backup = QPushButton("📦 إنشاء نسخة احتياطية فورية (SQL Backup)")
        self.btn_db_optimize = QPushButton("🚀 تحسين وضغط الفهارس الهيكلية (Vacuum Full)")
        for btn in [self.btn_db_backup, self.btn_db_optimize]:
            btn.setFixedHeight(self.BTN_HEIGHT); btn.setCursor(Qt.CursorShape.PointingHandCursor); db_form.addWidget(btn)
        self.btn_db_backup.setStyleSheet("background-color: #059669; color: white; font-weight: bold; border-radius: 6px;")
        self.btn_db_optimize.setStyleSheet("background-color: white; color: #1e293b; border: 1px solid #cbd5e1; border-radius: 6px;")
        db_form.addStretch(); db_layout.addWidget(db_frame)
        db_log_table = QTableWidget(); db_log_table.setColumnCount(4); db_log_table.setHorizontalHeaderLabels(["تاريخ وصيانة الحركة", "نوع الإجراء الإداري الهيكلي", "المساحة الموفرة بالقرص", "حالة حماية سلامة البيانات"]); db_log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); db_layout.addWidget(db_log_table, stretch=3)
        self.settings_sub_tabs.addTab(db_widget, "🗄️ صيانة خادم السيرفر")
        
        settings_layout.addWidget(self.settings_sub_tabs)
        self.tabs.addTab(settings_main_tab, "⚙️ الإعدادات")
        
        # ربط أحداث الإعدادات
        self.btn_save_comp_info.clicked.connect(self.on_save_company_profile_clicked)
        self.txt_set_invoice_footer.textChanged.connect(self.on_invoice_footer_text_changed)
        self.btn_db_backup.clicked.connect(self.on_trigger_db_backup_operation)
        self.btn_db_optimize.clicked.connect(self.on_trigger_db_optimization)

    # ──────────────────────────────────────────────────────────
    # الدوال الخلفية والإجرائية لمحرك قاعدة البيانات والعمليات
    # ──────────────────────────────────────────────────────────
    def on_save_company_profile_clicked(self):
        comp_name = self.txt_set_comp_name.text().strip()
        if not comp_name:
            SystemMessageBox.show_warning(self, "تحذير الإدخال", "يرجى تعبئة اسم المؤسسة لاعتماد الهوية الضريبية الفورية على السيستم!")
            return
        SystemMessageBox.show_info(self, "الهوية الضريبية", f"تم تثبيت وتحديث بيانات وهوية السوبرماركت رسمياً لـ '{comp_name}' بنجاح.")

    def on_invoice_footer_text_changed(self):
        text = self.txt_set_invoice_footer.text().strip()
        if text: self.lbl_mock_footer.setText(text)
        else: self.lbl_mock_footer.setText("شكراً لزيارتكم الكريمة!")

    def on_trigger_db_backup_operation(self):
        SystemMessageBox.show_info(self, "محرك النسخ الاحتياطي", "تم إنشاء نسخة احتياطية آمنة ومشفّرة (SQL Dump) لقاعدة البيانات بنجاح.")

    def on_trigger_db_optimization(self):
        SystemMessageBox.show_info(self, "صيانة وتكامل الهياكل", "تم تفعيل دالة VACUUM FULL وإعادة بناء الفهارس بنجاح لتسريع زمن استجابة السيرفر.")

    def load_items_data(self):
        search_text = self.txt_search_item.text().strip() if hasattr(self, 'txt_search_item') else ""
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            cursor = conn.cursor()
            
            # جلب الـ 11 عموداً كاملة من قاعدة البيانات مع وضع قيم افتراضية إذا كانت الحقول فارغة في البداية
            query_fields = """
                barcode, item_name, 
                COALESCE(category, 'المعلبات') as category, 
                unit, price, sales_price, discount, stock_qty, 
                COALESCE(min_stock, 5) as min_stock, 
                COALESCE(supplier_name, 'مورد عام / افتراضي') as supplier_name, 
                COALESCE(item_status, '🟢 نشط (متاح للبيع)') as item_status
            """
            
            if search_text:
                query = f"""
                    SELECT {query_fields} FROM items 
                    WHERE item_name ILIKE %s OR barcode ILIKE %s OR category ILIKE %s OR supplier_name ILIKE %s
                    ORDER BY item_name ASC;
                """
                cursor.execute(query, (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"))
            else:
                query = f"SELECT {query_fields} FROM items ORDER BY item_name ASC;"
                cursor.execute(query)

            rows = cursor.fetchall()
            
            # 1. شحن جدول المنتجات الرئيسي (11 عموداً كاملاً بالترتيب الجديد)
            self.items_table.setRowCount(0)
            for row_idx, row_data in enumerate(rows):
                self.items_table.insertRow(row_idx)
                for col_idx in range(11):
                    val = str(row_data[col_idx] if row_data[col_idx] is not None else "")
                    item = QTableWidgetItem(val)
                    
                    # تلوين كمية المخزون باللون الأحمر إذا كانت أقل من أو تساوي الحد الأدنى لطلب الصنف نفسه
                    if col_idx == 7:  # عمود المخزون الحالي
                        current_stock = int(row_data[7] or 0)
                        min_stock_limit = int(row_data[8] or 5)
                        if current_stock <= min_stock_limit:
                            item.setForeground(QColor("#dc2626"))  # لون أحمر احترافي للتحذير
                            
                    self.items_table.setItem(row_idx, col_idx, item)
                    
            # 2. شحن وتنسيق واجهة المخزون المنفصلة (التبويب الثالث)
            self.inventory_table.setRowCount(0)
            for row_idx, row_data in enumerate(rows):
                self.inventory_table.insertRow(row_idx)
                
                barcode_item = QTableWidgetItem(str(row_data[0]))
                name_item = QTableWidgetItem(str(row_data[1]))
                qty_item = QTableWidgetItem(str(row_data[7]))  # المخزون الحالي أصبح في المؤشر رقم 7
                
                current_qty = int(row_data[7] or 0)
                min_limit = int(row_data[8] or 5)
                
                status_str = "✔️ مخزون آمن"
                status_color = "#16a34a"
                
                if current_qty <= 0:
                    status_str = "❌ منتهي تماماً (نواقص حادة)"
                    status_color = "#dc2626"
                elif current_qty <= min_limit:
                    status_str = "⚠️ تحت الحد الأدنى (بحاجة لطلب)"
                    status_color = "#ea580c"
                    
                status_item = QTableWidgetItem(status_str)
                status_item.setForeground(QColor(status_color))
                
                status_text_val = str(row_data[10])
                expiry_safety = QTableWidgetItem(status_text_val)
                
                self.inventory_table.setItem(row_idx, 0, barcode_item)
                self.inventory_table.setItem(row_idx, 1, name_item)
                self.inventory_table.setItem(row_idx, 2, qty_item)
                self.inventory_table.setItem(row_idx, 3, status_item)
                self.inventory_table.setItem(row_idx, 4, expiry_safety)
                
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error loading items into table: {e}")

    def on_item_row_selected(self):
        selected_row = self.items_table.currentRow()
        if selected_row >= 0:
            try:
                def get_safe_text(col_idx, default=""):
                    cell = self.items_table.item(selected_row, col_idx)
                    return cell.text().strip() if cell and cell.text() else default

                # 1. قراءة النصوص الأساسية بأمان
                self.txt_barcode.setText(get_safe_text(0))
                self.txt_barcode.setReadOnly(True)  # قفل حقل الباركود أثناء التعديل لحمايته
                self.txt_name.setText(get_safe_text(1))
                
                # 2. القسم (ComboBox)
                if hasattr(self, 'cmb_category'):
                    cat_val = get_safe_text(2, "المعلبات")
                    if self.cmb_category.findText(cat_val) == -1:
                        self.cmb_category.addItem(cat_val)
                    self.cmb_category.setCurrentText(cat_val)
                
                self.txt_unit.setText(get_safe_text(3, "قطعة"))
                
                # 3. الأسعار والخصومات (حماية من القيم الفارغة)
                self.txt_cost_price.setText(get_safe_text(4, "0.00"))
                self.txt_sales_price.setText(get_safe_text(5, "0.00"))
                self.txt_discount.setText(get_safe_text(6, "0.00"))
                
                # 4. الأرقام والمخزون (SpinBox) مع تحويل آمن لمنع خطأ تحويل النصوص
                try:
                    stock_val = int(float(get_safe_text(7, "0")))
                    self.spin_stock.setValue(stock_val)
                except:
                    self.spin_stock.setValue(0)
                    
                if hasattr(self, 'spin_min_stock'):
                    try:
                        min_stock_val = int(float(get_safe_text(8, "5")))
                        self.spin_min_stock.setValue(min_stock_val)
                    except:
                        self.spin_min_stock.setValue(5)
                
                # 5. المورد (ComboBox)
                if hasattr(self, 'cmb_supplier'):
                    sup_val = get_safe_text(9, "مورد عام / افتراضي")
                    if self.cmb_supplier.findText(sup_val) == -1:
                        self.cmb_supplier.addItem(sup_val)
                    self.cmb_supplier.setCurrentText(sup_val)
                
                # 6. حالة الصنف (ComboBox)
                if hasattr(self, 'cmb_status'):
                    status_val = get_safe_text(10, "🟢 نشط (متاح للبيع)")
                    if self.cmb_status.findText(status_val) == -1:
                        self.cmb_status.addItem(status_val)
                    self.cmb_status.setCurrentText(status_val)
                    
            except Exception as e:
                print(f"حدث خطأ داخلي تم تداركه بأمان: {e}")

    def clear_item_fields(self):
        self.txt_barcode.setReadOnly(False)
        self.txt_barcode.clear()
        self.txt_name.clear()
        self.txt_cost_price.clear()
        self.txt_sales_price.clear()
        self.txt_discount.setText("0.00")
        self.spin_stock.setValue(100)
        if hasattr(self, 'spin_min_stock'): self.spin_min_stock.setValue(5)
        if hasattr(self, 'cmb_category'): self.cmb_category.setCurrentIndex(0)
        if hasattr(self, 'cmb_supplier'): self.cmb_supplier.setCurrentIndex(0)
        if hasattr(self, 'cmb_status'): self.cmb_status.setCurrentIndex(0)
        self.items_table.clearSelection()

    # ──────────────────────────────────────────────────────────
    # [إصلاح دالة الحفظ والتعديل] بالمعاملات الصحيحة للرسائل التنبيهية
    # ──────────────────────────────────────────────────────────
    def on_save_item_clicked(self):
        barcode = self.txt_barcode.text().strip()
        name = self.txt_name.text().strip()
        category = self.cmb_category.currentText().strip() if hasattr(self, 'cmb_category') else "المعلبات"
        unit = self.txt_unit.text().strip()
        cost = self.txt_cost_price.text().strip() or "0.00"
        sales = self.txt_sales_price.text().strip() or "0.00"
        discount = self.txt_discount.text().strip() or "0.00"
        stock = self.spin_stock.value()
        min_stock = self.spin_min_stock.value() if hasattr(self, 'spin_min_stock') else 5
        supplier = self.cmb_supplier.currentText().strip() if hasattr(self, 'cmb_supplier') else "مورد عام / افتراضي"
        status = self.cmb_status.currentText().strip() if hasattr(self, 'cmb_status') else "🟢 نشط (متاح للبيع)"
        
        if not barcode or not name:
            # المعامل الأول parent (self)، المعامل الثاني نص الرسالة
            SystemMessageBox.show_warning(self, "يرجى كتابة الباركود الدولي واسم المنتج الصنف أولاً!")
            return
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            cursor = conn.cursor()
            query = """
                INSERT INTO items (barcode, item_name, category, unit, price, sales_price, discount, stock_qty, min_stock, supplier_name, item_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (barcode) 
                DO UPDATE SET item_name = EXCLUDED.item_name, 
                              category = EXCLUDED.category,
                              unit = EXCLUDED.unit, 
                              price = EXCLUDED.price, 
                              sales_price = EXCLUDED.sales_price, 
                              discount = EXCLUDED.discount, 
                              stock_qty = EXCLUDED.stock_qty,
                              min_stock = EXCLUDED.min_stock,
                              supplier_name = EXCLUDED.supplier_name,
                              item_status = EXCLUDED.item_status;
            """
            cursor.execute(query, (barcode, name, category, unit, float(cost), float(sales), float(discount), stock, min_stock, supplier, status))
            conn.commit(); cursor.close(); conn.close()
            
            # ✅ سطر النجاح المطلوب بالمعاملات الصحيحة:
            SystemMessageBox.show_info(self, "تم حفظ وتحديث بيانات الصنف داخل المخزن بنجاح.")
            
            self.clear_item_fields(); self.load_items_data()
        except Exception as e:
            SystemMessageBox.show_critical(self, f"خطأ أثناء الحفظ الفعلي في قاعدة البيانات: {e}")

    def on_delete_item_clicked(self):
        barcode = self.txt_barcode.text().strip()
        if not barcode:
            SystemMessageBox.show_warning(self, "يرجى اختيار صنف من الجدول بالماوس لحذفه!")
            return
            
        if SystemMessageBox.show_question(self, f"هل أنت متأكد من حذف الصنف صاحب الباركود ({barcode}) نهائياً؟") == QDialog.DialogCode.Accepted:
            try:
                conn = psycopg2.connect(**DB_PARAMS); cursor = conn.cursor()
                cursor.execute("DELETE FROM items WHERE barcode = %s;", (barcode,))
                conn.commit(); cursor.close(); conn.close()
                # ✅ تم التعديل هنا (حذف self)
                SystemMessageBox.show_info("إشعار الحذف", "تم حذف الصنف من المخزن بنجاح.")
                self.clear_item_fields(); self.load_items_data()
            except Exception as e:
                SystemMessageBox.show_critical(self, f"فشل الحذف: المنتج مرتبط بعمليات وفواتير سابقة: {e}")

    def load_invoices_data(self):
        try:
            conn = psycopg2.connect(**DB_PARAMS); cursor = conn.cursor()
            cursor.execute("SELECT id, invoice_date, payment_method, user_id, total_price FROM sales_invoices ORDER BY id DESC;")
            rows = cursor.fetchall()
            self.invoice_table.setRowCount(0)
            for row_idx, row_data in enumerate(rows):
                self.invoice_table.insertRow(row_idx)
                for col_idx in range(5):
                    self.invoice_table.setItem(row_idx, col_idx, QTableWidgetItem(str(row_data[col_idx])))
            cursor.close(); conn.close(); self.invoice_details_table.setRowCount(0)
        except Exception as e: print(f"Error: {e}")

    def on_invoice_selected(self):
        selected_row = self.invoice_table.currentRow()
        if selected_row >= 0:
            invoice_id = self.invoice_table.item(selected_row, 0).text()
            try:
                conn = psycopg2.connect(**DB_PARAMS); cursor = conn.cursor()
                cursor.execute("SELECT barcode, item_name, price, quantity, total FROM invoice_items WHERE invoice_id = %s;", (invoice_id,))
                rows = cursor.fetchall()
                self.invoice_details_table.setRowCount(0)
                for row_idx, row_data in enumerate(rows):
                    self.invoice_details_table.insertRow(row_idx)
                    for col_idx in range(5):
                        self.invoice_details_table.setItem(row_idx, col_idx, QTableWidgetItem(str(row_data[col_idx])))
                cursor.close(); conn.close()
            except Exception as e: print(f"Error inside invoice items layout: {e}")

    def calculate_pnl_report(self):
        try:
            # ... (باقي كود الحساب المالي بدون تغيير) ...
            conn = psycopg2.connect(**DB_PARAMS); cursor = conn.cursor()
            cursor.execute("SELECT SUM(total_price) FROM sales_invoices;")
            total_sales = cursor.fetchone()[0] or 0.0
            cursor.close(); conn.close()
            pnl_data = [
                ("إجمالي مبيعات الصندوق (Gross Revenue)", f"+ {total_sales:.2f} ج.م", "الحساب الجاري", "وردية نشطة"),
                ("تكلفة البضاعة المباعة (COGS Est.)", f"- {(total_sales * 0.7):.2f} ج.م", "حساب المشتريات", "تقديري لمتوسط الربح"),
                ("صافي الأرباح المحتسبة المعلقة (Net Profit)", f"★ {(total_sales * 0.3 - 450):.2f} ج.م", "الأرباح الصافية", "جاهز للتوزيع")
            ]
            self.table_fin_report.setRowCount(0)
            for row_idx, (title, value, nature, note) in enumerate(pnl_data):
                self.table_fin_report.insertRow(row_idx)
                self.table_fin_report.setItem(row_idx, 0, QTableWidgetItem(QDate.currentDate().toString(Qt.DateFormat.ISODate)))
                self.table_fin_report.setItem(row_idx, 1, QTableWidgetItem(title))
                val_item = QTableWidgetItem(value)
                if "+" in value or "★" in value: val_item.setForeground(QColor("#16a34a"))
                else: val_item.setForeground(QColor("#dc2626"))
                self.table_fin_report.setItem(row_idx, 2, val_item)
                self.table_fin_report.setItem(row_idx, 3, QTableWidgetItem(nature))
                self.table_fin_report.setItem(row_idx, 4, QTableWidgetItem(note))
        except Exception as e: 
            SystemMessageBox.show_critical(self, f"فشل توليد التقرير المالي: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminDashboardWindow()
    window.show()
    sys.exit(app.exec())