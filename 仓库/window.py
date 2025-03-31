import sys
import os
import weakref
from datetime import datetime
from PyQt5.QtGui import QColor, QBrush, QFontMetrics, QPalette, QPixmap
from PyQt5.QtCore import Qt, QStringListModel, QTranslator, QCoreApplication, QPropertyAnimation, QPoint, QEvent, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget,
    QLineEdit, QCompleter, QTextEdit, QPushButton, QFileDialog, QMessageBox,
    QInputDialog, QDialog, QListWidgetItem, QDesktopWidget, QMenu, QSizePolicy, QStyledItemDelegate,
    QStyleOptionViewItem, QStyle, QDialogButtonBox, QGridLayout, QToolButton, QScrollArea, QFrame
)
from PyQt5.QtCore import QRect, QEasingCurve
from function import *
from PyQt5.QtCore import QVariantAnimation, QEasingCurve
from PyQt5.QtGui import QFontMetrics, QPainter
from PyQt5.QtWidgets import QGroupBox

#    EXE打包指令       pyinstaller --noconsole --onefile --clean --icon="resources/icon.ico" --add-data "resources/*;resources" window.py


def animate_search_edit_height(target_height):
    animation = QPropertyAnimation(search_edit, b"maximumHeight")
    animation.setDuration(3000)  # ⏳ 3秒，让动画更慢
    animation.setStartValue(search_edit.height())
    animation.setEndValue(target_height)
    animation.setEasingCurve(QEasingCurve.OutCubic)  # ✅ 更加平滑的缓动曲线
    animation.start()
    search_edit.animation = animation  # 防止动画对象被垃圾回收


# 获取资源文件路径（支持开发和打包环境）
def get_resource_path(filename):
    if getattr(sys, 'frozen', False):  # 如果是打包后的环境
        base_path = sys._MEIPASS
    else:  # 如果是开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, 'resources', filename)


def animate_search_edit_height(target_height):
    animation = QPropertyAnimation(search_edit, b"minimumHeight")
    animation.setDuration(10)  # 动画时长 300 毫秒
    animation.setStartValue(search_edit.height())
    animation.setEndValue(target_height)
    animation.start()
    # 保存引用，防止动画被垃圾回收
    search_edit.animation = animation


def tr(message):
    return QCoreApplication.translate("MainWindow", message)


def center_window(window):
    qr = window.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    window.move(qr.topLeft())





def delete_script(script_list, script_name):
    """
    删除脚本。
    """
    return [script for script in script_list if script['name'] != script_name]


def update_script_name(script_list, old_name, new_name):
    """
    更新脚本名称。
    """
    for script in script_list:
        if script['name'] == old_name:
            script['name'] = new_name
            return True
    return False


def update_status_bar(widget_name):
    """ 更新状态栏信息 """
    if isinstance(widget_name, str) and widget_name.strip():
        status_bar.setText(f"🔹 {widget_name}")
    else:
        status_bar.setText(">>> 准备就绪 🚀")


def create_main_window():
    global status_bar, list_widget, search_edit, completer_model, display_area
    global create_script_button, remove_selected_button, clear_button, update_log_button
    global english_mode, english_learn_button, original_english_btn_style
    english_mode = False

    main_window = QWidget()
    main_window.setGeometry(100, 100, 1024, 768)
    main_window.setWindowTitle(tr('Xing_yun(@Rhj_flash)'))
    main_window.setStyleSheet(main_window_style)
    center_window(main_window)
    main_layout = QVBoxLayout()
    main_window.setLayout(main_layout)

    # 设置图标
    icon_path = get_resource_path('imge.png')
    if not os.path.exists(icon_path):
        icon_path = "imge.png"
    icon = QIcon(icon_path)
    main_window.setWindowIcon(icon)

    # 添加状态栏
    status_bar = QLabel(tr(">>> 准备就绪🚀"))
    status_bar.setStyleSheet("""
        font-size: 12px;
        color: #444444;
        padding: 2px 8px;
        border-top: 1px solid #CCCCCC;
    """)
    status_bar.setAlignment(Qt.AlignLeft)
    status_bar.setFixedHeight(30)
    status_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    # 添加 "英语角" 按钮
    english_learn_button = QPushButton("  💃  ")
    original_english_btn_style = """
        QPushButton {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                              stop:0 rgba(200, 200, 200, 1), stop:1 rgba(160, 160, 160, 1));
            border: 1px solid #BBBBBB;
            border-radius: 8px;
            color: #222222;
            font-size: 14px;
            font-weight: bold;
            padding: 2px 8px;
            text-align: center;
            margin: 0;
            box-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
        }
        QPushButton:hover {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                              stop:0 rgba(160, 160, 160, 1), stop:1 rgba(120, 120, 120, 1));
            border: 1px solid #AAAAAA;
        }
        QPushButton:pressed {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                              stop:0 rgba(120, 120, 120, 1), stop:1 rgba(90, 90, 90, 1));
            border: 1px solid #999999;
            box-shadow: 1px 1px 1px rgba(0, 0, 0, 0.1);
        }
    """
    try:
        english_learn_button.clicked.disconnect()
    except Exception:
        pass
    english_learn_button.clicked.connect(toggle_english_mode)
    english_learn_button.setStyleSheet(original_english_btn_style)
    english_learn_button.setFixedSize(32, 32)

    # 状态栏容器
    status_container = QWidget()
    status_layout = QHBoxLayout(status_container)
    status_layout.addWidget(status_bar)
    status_layout.addWidget(english_learn_button)
    status_layout.setContentsMargins(0, 0, 0, 0)
    status_layout.setSpacing(0)
    status_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    status_container.setFixedHeight(30)

    # 其余代码保持不变...
    list_widget = SmoothListWidget(status_bar)
    list_widget.setStyleSheet(list_widget_style)
    list_widget.itemClicked.connect(on_list_item_clicked)
    list_widget.itemDoubleClicked.connect(lambda item: execute_script(item, display_area))

    # 允许拖拽排序
    list_widget.setDragDropMode(QListWidget.InternalMove)
    list_widget.model().rowsMoved.connect(update_item_colors)  # 监听排序，确保颜色不乱
    list_widget.setDefaultDropAction(Qt.MoveAction)
    list_widget.setSelectionMode(QListWidget.SingleSelection)
    list_widget.setAcceptDrops(True)

    list_widget.model().rowsMoved.connect(save_list_order)  # 监听拖拽完成后触发

    search_edit = QLineEdit()
    search_edit.setPlaceholderText(tr('🔍脚本名称/单词'))
    search_edit.setStyleSheet(search_edit_style)
    completer_items = []
    completer_model = QStringListModel(completer_items)
    completer = QCompleter(completer_model)
    completer.setFilterMode(Qt.MatchContains)
    completer.setCaseSensitivity(Qt.CaseInsensitive)
    search_edit.textChanged.connect(lambda text: filter_list_widget(list_widget, text))

    left_layout = QVBoxLayout()
    left_layout.addWidget(search_edit)
    left_layout.addWidget(list_widget)
    left_widget = QWidget()
    left_widget.setLayout(left_layout)
    left_widget.setStyleSheet(left_widget_style)

    display_area = QTextEdit()
    display_area.setReadOnly(True)
    display_area.setStyleSheet(display_area_style)

    button_layout = QHBoxLayout()
    create_script_button = create_button("🖋 创建脚本", main_window,
                                         lambda: show_create_script_dialog(main_window, list_widget, display_area,
                                                                           completer_model))
    remove_selected_button = create_button("🗑️ 删除脚本", main_window,
                                           lambda: remove_script(list_widget, display_area, completer_model))
    clear_button = create_button("🧹️ 清除屏幕", main_window, lambda: clear_display(display_area))
    update_log_button = create_button("📜 开发者日志|设备信息", main_window,
                                      lambda: update_log_with_effect(display_area))

    create_script_button.enterEvent = lambda event: update_status_bar("🖋 创建脚本")
    remove_selected_button.enterEvent = lambda event: update_status_bar("🗑️ 删除脚本")
    clear_button.enterEvent = lambda event: update_status_bar("🧹️ 清除日志")
    update_log_button.enterEvent = lambda event: update_status_bar("📜 查看日志 / 设备信息")
    search_edit.enterEvent = lambda event: update_status_bar("🔍 搜索框")
    english_learn_button.enterEvent = lambda event: update_status_bar("💃 English_learn")

    button_layout.addStretch()
    button_layout.addWidget(create_script_button)
    button_layout.addWidget(remove_selected_button)
    button_layout.addWidget(clear_button)
    button_layout.addWidget(update_log_button)
    button_layout.addStretch()

    splitter = QSplitter(Qt.Horizontal)
    splitter.addWidget(left_widget)
    splitter.addWidget(display_area)
    main_layout.addWidget(splitter)
    main_layout.addLayout(button_layout)

    splitter.setSizes([main_window.width() // 6, main_window.width() * 3 // 6])

    # 将状态栏容器添加到主布局的底部
    main_layout.addWidget(status_container)

    scripts = load_scripts()
    for index, script in enumerate(scripts):
        item = QListWidgetItem(script['name'])
        item.setData(Qt.UserRole, script)
        # 根据索引号设置颜色
        if index % 2 == 0:
            item.setBackground(QColor("#F0F0F0"))  # 偶数行 - 浅灰
        else:
            item.setBackground(QColor("#D9D9D9"))  # 奇数行 - 稍深
        list_widget.addItem(item)
        completer_model.insertRow(0)
        completer_model.setData(completer_model.index(0), script['name'])

    # 设置右键菜单
    setup_context_menu(list_widget, display_area)
    # 显示欢迎界面
    display_welcome_screen(display_area)
    update_item_colors()  # 确保软件启动时颜色正确
    return main_window


def toggle_english_mode():
    global english_mode, english_learn_button, list_widget, create_script_button, remove_selected_button, clear_button, update_log_button, search_edit, display_area, original_english_btn_style
    if not english_mode:
        english_mode = True
        english_learn_button.setStyleSheet("background-color: red; color: white; border-radius: 8px;")
        list_widget.setEnabled(False)
        create_script_button.setEnabled(False)
        remove_selected_button.setEnabled(False)
        clear_button.setEnabled(False)
        update_log_button.setEnabled(False)

        try:
            search_edit.textChanged.disconnect()
        except Exception:
            pass
        search_edit.textChanged.connect(english_search_text_changed)

        # 使用动画调整高度
        animate_search_edit_height(190)

        appendLogWithEffect(display_area, """🔴已开启单词查询模式
███████╗███╗   ██╗ ██████╗ ██╗     ██╗███████╗██╗  ██╗
██╔════╝████╗  ██║██╔════╝ ██║     ██║██╔════╝██║  ██║
█████╗  ██╔██╗ ██║██║  ███╗██║     ██║███████║███████║
██╔══╝  ██║╚██╗██║██║   ██║██║     ██║╚════██║██║  ██║
███████╗██║ ╚████║╚██████╔╝███████╗██║███████║██║  ██║
╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝╚══════╝╚═╝  ╚═╝
""")
        status_bar.setText("🔴 英语查询模式")
    else:
        english_mode = False
        english_learn_button.setStyleSheet(original_english_btn_style)
        list_widget.setEnabled(True)
        create_script_button.setEnabled(True)
        remove_selected_button.setEnabled(True)
        clear_button.setEnabled(True)
        update_log_button.setEnabled(True)

        try:
            search_edit.textChanged.disconnect()
        except Exception:
            pass
        search_edit.textChanged.connect(original_search_handler)

        # 使用动画恢复高度
        animate_search_edit_height(40)
        appendLogWithEffect(display_area, """🔵已退出单词查询模式
███████╗██╗  ██╗██╗████████╗
██╔════╝╚██╗██╔╝██║╚══██╔══╝
█████╗   ╚███╔╝ ██║   ██║   
██╔══╝   ██╔██╗ ██║   ██║   
███████╗██╔╝ ██╗██║   ██║   
╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝    
""")
        status_bar.setText(">>> 准备就绪🚀")


def english_search_text_changed(text):
    """
    英语查询模式下的搜索框行为：
    - 实时查询单词，并在 display_area 显示查询结果
    - 显示更多预览单词（这里设置为最多20个），同时将最相似的单词高亮显示
    """
    display_area.clear()
    if text.strip():
        # 调用 query_local_dictionary 时设置 top_n 为 20，显示更多结果
        results = query_local_dictionary(text, top_n=20)
        if results:
            html_lines = []
            for idx, item in enumerate(results):
                # 将第一个结果（最相似）高亮显示
                if idx == 0:
                    line = f"<span style='background-color: yellow; font-weight: bold;'>🔤 {item['word']} | 📖 {item['translation']}</span>"
                else:
                    line = f"🔤 {item['word']} | 📖 {item['translation']}"
                html_lines.append(line)
            # 使用 <br><br> 分隔每一行，让预览内容显示得更清晰
            display_area.setHtml("<br><br>".join(html_lines))
        else:
            display_area.setHtml("⚠️ 未找到相关单词")


def original_search_handler(text):
    """
    原始搜索行为：过滤脚本列表
    """
    filter_list_widget(list_widget, text)


def update_item_colors():
    """ 重新按照索引更新单双数颜色 """
    for i in range(list_widget.count()):
        item = list_widget.item(i)
        if i % 2 == 0:
            item.setBackground(QColor("#F5F5F5"))  # 偶数行颜色（浅灰）
        else:
            item.setBackground(QColor("#E8E8E8"))  # 奇数行颜色（稍深灰）


# 当用户拖拽调整顺序后，自动更新 `scripts.json`
def save_list_order():
    scripts = []
    for i in range(list_widget.count()):
        item = list_widget.item(i)
        script_data = item.data(Qt.UserRole)
        scripts.append(script_data)
    save_scripts(scripts)
    appendLogWithEffect(display_area, "🔄脚本顺序已更新！\n")


def create_button(text, parent, callback):
    button = QPushButton(text, parent)
    button.setStyleSheet(button_style)
    button.setFixedSize(250, 55)
    button.clicked.connect(callback)
    return button


def on_list_item_clicked(item):
    list_widget.setCurrentItem(item)


def execute_script(item, display_area):
    current_item = list_widget.currentItem()
    if current_item != item:
        return
    try:
        script_data = item.data(Qt.UserRole)
        script_type = script_data.get('type')
        script_value = script_data.get('value')
        timestamp = datetime.now().strftime('%m-%d %H:%M:%S')

        if script_type == 'merge':
            # 只输出一次开始执行的日志
            appendLogWithEffect(display_area, f"合并脚本 '{item.text()}' 执行完成\n")

            # 静默执行所有子脚本
            for sub_script in script_value:
                sub_type = sub_script['type']
                sub_value = sub_script['value']
                if sub_type == 'url':
                    open_url(sub_value)
                elif sub_type == 'file':
                    open_file(sub_value)

        elif script_type == 'url':
            open_url(script_value)
            appendLogWithEffect(display_area, f"打开网页: {item.text()}\n")

        elif script_type == 'file':
            open_file(script_value)
            appendLogWithEffect(display_area, f"打开软件: {item.text()}\n")

        list_widget.setToolTip(str(script_value))
    except Exception as e:
        appendLogWithEffect(display_area, f"执行错误: {e}")
        QMessageBox.critical(None, tr('错误'), f"{tr('执行脚本时发生错误')}: {e}")


def filter_list_widget(list_widget, text):
    for i in range(list_widget.count()):
        item = list_widget.item(i)
        item.setHidden(text.lower() not in item.text().lower())


def remove_script(list_widget, display_area, completer_model):
    """ 删除选中的脚本 """
    try:
        selected_items = list_widget.selectedItems()
        if selected_items:
            # 创建确认对话框（严格匹配其他窗口尺寸420x300）
            confirm_dialog = QDialog()
            confirm_dialog.setWindowFlags(confirm_dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            confirm_dialog.setWindowTitle("确认删除")
            confirm_dialog.setFixedSize(420, 300)  # 标准尺寸

            # 设置窗口图标和居中位置（关键修改点3）
            icon_path = get_resource_path('imge.png')
            if os.path.exists(icon_path):
                confirm_dialog.setWindowIcon(QIcon(icon_path))

            # 使用主窗口的居中函数确保位置一致
            def center_to_parent():
                if list_widget.window():
                    qr = confirm_dialog.frameGeometry()
                    cp = list_widget.window().geometry().center()
                    qr.moveCenter(cp)
                    confirm_dialog.move(qr.topLeft())

            center_to_parent()  # 先尝试相对主窗口居中
            confirm_dialog.showEvent = lambda e: center_to_parent()  # 防止窗口管理器调整位置

            # 使用优化的灰色风格（与其他窗口一致）
            confirm_dialog.setStyleSheet("""
                QDialog {
                    background-color: #F5F7FA;
                    border-radius: 8px;
                    border: 1px solid #D0D0D0;
                    font-family: 'Microsoft YaHei', Arial, sans-serif;
                }
                QLabel {
                    font-size: 14px;
                    color: #444444;
                }
                QTextEdit {
                    border: 1px solid #E0E0E0;
                    border-radius: 4px;
                    background: white;
                    font-size: 13px;
                    padding: 8px;
                }
                QPushButton {
                    min-width: 90px;
                    min-height: 32px;
                    padding: 6px 12px;
                    font-weight: bold;
                    border-radius: 4px;
                }
            """)

            # 主布局（边距与其他窗口一致）
            main_layout = QVBoxLayout(confirm_dialog)
            main_layout.setContentsMargins(20, 15, 20, 15)
            main_layout.setSpacing(12)

            # ===== 标题区域（严格左对齐，关键修改点2）=====
            title_widget = QWidget()
            title_layout = QHBoxLayout(title_widget)
            title_layout.setContentsMargins(0, 0, 0, 0)
            title_layout.setAlignment(Qt.AlignLeft)  # 强制左对齐

            warning_icon = QLabel()
            warning_icon.setPixmap(QIcon.fromTheme("dialog-warning").pixmap(20, 20))
            warning_icon.setStyleSheet("padding-right: 8px;")

            title = QLabel("确认删除")
            title.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                margin: 0;
                padding: 0;
            """)
            title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            title_layout.addWidget(warning_icon)
            title_layout.addWidget(title)
            title_layout.addStretch()
            main_layout.addWidget(title_widget)

            # ===== 提示文本 =====
            prompt = QLabel(f"即将删除 1 个脚本：" if len(selected_items) == 1
                            else f"即将删除 {len(selected_items)} 个脚本：")
            prompt.setStyleSheet("""
                font-size: 14px; 
                color: #555555;
                padding-bottom: 20px;
            """)



            prompt.setAlignment(Qt.AlignLeft)
            main_layout.addWidget(prompt)

            # ===== 脚本显示区域 =====
            script_display = QTextEdit()
            script_display.setReadOnly(True)
            script_display.setFixedHeight(300)  # 固定高度 300px
            script_display.setStyleSheet("""
                QTextEdit {
                    background: #f8f9fa;
                    border: 1px solid #ced4da;
                    border-radius: 6px;
                    padding: 8px;
                    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                    font-size: 14px;
                    color: #212529;
                    selection-background-color: #0d6efd;
                    selection-color: white;
                    min-height: 70px;        /* 最小高度（关键！）*/
                }
                QScrollBar:vertical {
                    border: none;
                    background: #f1f3f5;
                    width: 10px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #adb5bd;
                    min-height: 20px;
                    border-radius: 4px;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none;
                }
            """)

            # 格式化显示脚本信息
            script_text = []
            for i, item in enumerate(selected_items, 1):
                script_data = item.data(Qt.UserRole)
                name = item.text()
                if script_data.get('type') == 'url':
                    script_text.append(f"{i}. 🌐 {name}\n   🔗 {script_data['value']}")
                elif script_data.get('type') == 'file':
                    script_text.append(f"{i}. 📂 {name}\n   🗃️ {script_data['value']}")
                else:
                    script_text.append(f"{i}. 🔗 {name}")

            script_display.setPlainText("\n\n".join(script_text))
            script_display.setFixedHeight(min(150, 30 + 30 * len(selected_items)))  # 动态高度
            main_layout.addWidget(script_display, 1)

            # ===== 按钮区域（完美平衡布局）=====
            button_container = QWidget()
            button_layout = QHBoxLayout(button_container)
            button_layout.setContentsMargins(0, 10, 0, 0)
            button_layout.setSpacing(20)

            # 添加左右弹簧实现完美平衡
            button_layout.addStretch(1)

            # 取消按钮（左）
            cancel_btn = QPushButton("取消")
            cancel_btn.setCursor(Qt.PointingHandCursor)
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                  stop:0 #F5F5F5, stop:1 #E0E0E0);
                    border: 1px solid #CCCCCC;
                    color: #333333;
                }
                QPushButton:hover {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                  stop:0 #E0E0E0, stop:1 #D0D0D0);
                }
            """)

            # 确认按钮（右）
            confirm_btn = QPushButton("确认删除")
            confirm_btn.setCursor(Qt.PointingHandCursor)
            confirm_btn.setStyleSheet("""
                QPushButton {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                  stop:0 #E74C3C, stop:1 #C0392B);
                    color: white;
                    border: 1px solid #BD3E31;
                }
                QPushButton:hover {
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                  stop:0 #C0392B, stop:1 #A5281B);
                }
            """)

            button_layout.addWidget(cancel_btn)
            button_layout.addWidget(confirm_btn)
            button_layout.addStretch(1)

            main_layout.addWidget(button_container)

            # ===== 信号连接 =====
            confirm_btn.clicked.connect(confirm_dialog.accept)
            cancel_btn.clicked.connect(confirm_dialog.reject)

            # 显示对话框
            if confirm_dialog.exec_() == QDialog.Accepted:
                for item in selected_items:
                    script_name = item.text()
                    list_widget.takeItem(list_widget.row(item))
                    completer_items = completer_model.stringList()
                    completer_items.remove(script_name)
                    completer_model.setStringList(completer_items)
                    save_current_scripts()
                    update_item_colors()
                    appendLogWithEffect(display_area, f"'{script_name}' 已删除！\n")
        else:
            QMessageBox.warning(None, tr('警告'), tr('请选择要删除的脚本项'))
    except Exception as e:
        appendLogWithEffect(display_area, f"Error removing script: {e}\n")
        QMessageBox.critical(None, tr('错误'), f"{tr('删除脚本时发生错误')}: {e}")




def save_current_scripts():
    scripts = []
    for i in range(list_widget.count()):
        item = list_widget.item(i)
        script_data = item.data(Qt.UserRole)
        scripts.append(script_data)
    save_scripts(scripts)


def update_log_with_effect(display_area):
    try:
        with open(get_resource_path('update_log.txt'), 'r', encoding='utf-8') as file:
            content = file.read()

        # 获取电脑基本信息
        computer_info = get_computer_info()

        # 生成带有设备信息的日志内容
        log_content = (

            "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░"
            "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░"
            "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░"
            "\n====================================当前设备基本信息抓取====================================\n"
            f"{computer_info}\n"
            "——————————————————————————————————————————————————————————————————————————————————————————\n"
            f"{content}\n"

        )

        # 将日志信息和电脑基本信息一起添加到显示区域
        appendLogWithEffect(display_area, log_content)

    except Exception as e:
        # 如果出现异常，记录错误信息
        error_message = f"Error loading update log: {e}\n"
        appendLogWithEffect(display_area, error_message)

        # 使用 QMessageBox 显示错误信息
        QMessageBox.critical(None, tr('错误'), f"{tr('加载开发者日志时发生错误')}: {e}")


def display_welcome_screen(display_area):
    welcome_message = """
 █████   █████ ██████████ █████       █████          ███████   
░░███   ░░███ ░░███░░░░░█░░███       ░░███         ███░░░░░███ 
 ░███    ░███  ░███  █ ░  ░███        ░███        ███     ░░███
 ░███████████  ░██████    ░███        ░███       ░███      ░███
 ░███░░░░░███  ░███░░█    ░███        ░███       ░███      ░███
 ░███    ░███  ░███ ░   █ ░███      █ ░███      █░░███     ███ 
 █████   █████ ██████████ ███████████ ███████████ ░░░███████░  
░░░░░   ░░░░░ ░░░░░░░░░░ ░░░░░░░░░░░ ░░░░░░░░░░░    ░░░░░░░        
 ▄         ▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄            ▄            ▄▄▄▄▄▄▄▄▄▄▄ 
▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░▌          ▐░▌          ▐░░░░░░░░░░░▌
▐░▌       ▐░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░▌          ▐░▌          ▐░█▀▀▀▀▀▀▀█░▌
▐░▌       ▐░▌▐░▌          ▐░▌          ▐░▌          ▐░▌       ▐░▌
▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░▌          ▐░▌          ▐░▌       ▐░▌
▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌          ▐░▌          ▐░▌       ▐░▌
▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░▌          ▐░▌          ▐░▌       ▐░▌
▐░▌       ▐░▌▐░▌          ▐░▌          ▐░▌          ▐░▌       ▐░▌
▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌
▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
 ▀         ▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀ 
欢迎使用本软件！
    使用说明：
    1. 创建软件脚本：创建一个打开软件的脚本,需要用户自定义脚本名称以及选择打开软件的绝对路径,双击使用脚本.
    2. 创建网页脚本：创建一个打开网页的脚本,需要用户键入网址和脚本名称(右键脚本可修改名称/地址).
    3. 拖拽脚本可以调整排序位置,鼠标放置于脚本上方可查看当前脚本的网址/绝对路径.
    4. 设备信息：获取当前设备基础信息(部分功能需要开启管理员权限).
    5. 网页脚本：🌐 Google | 🔗 https://www.google.com
       软件脚本：🖥️ Photoshop | 📂 C:/Program Files/Adobe/Photoshop.exe
    6. 🔴 英语查询模式下其它功能禁用
使用愉快！
                                                                            Rhj_flash
——————————————————————————————————————————————————————————————————————————————————————————
加载完毕...
"""

    appendLogWithEffect(display_area, welcome_message, include_timestamp=False)


display_area_style = """
    QTextEdit {
        border: 1px solid #CCCCCC;
        border-radius: 8px;
        background-color: #F9F9F9;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        color: #111111;
        padding: 10px;
    }
    QScrollBar:vertical, QScrollBar:horizontal {
        border: none;
        background: #F0F0F0;
        width: 10px;
        height: 10px;
        margin: 0px;  /* 解决错位问题 */
        border-radius: 5px;
    }
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
        background: #BBBBBB;
        min-height: 20px;
        min-width: 20px;
        border-radius: 5px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        background: none;
    }
"""
# 定义 QMessageBox 的样式表
message_box_style = """
QMessageBox {
    background-color: #ffffff;  /* 设置背景颜色为白色 */
    color: #333333;  /* 设置文本颜色 */
    border: 2px solid #0078d7;  /* 设置边框颜色和宽度 */
    border-radius: 15px;  /* 设置消息框整体的圆角半径 */
    padding: 20px;  /* 设置消息框内边距 */
}
QMessageBox QLabel {
    font-size: 16px;  /* 设置文本字体大小 */
    margin: 10px;  /* 设置标签外边距 */
}
QMessageBox QPushButton {
    background-color: #0078d7;  /* 设置按钮背景颜色 */
    color: white;  /* 设置按钮文本颜色 */
    padding: 12px 25px;  /* 设置按钮内边距 */
    border: none;  /* 去除按钮边框 */
    border-radius: 10px;  /* 设置按钮的圆角半径 */
    font-size: 16px;  /* 设置按钮文本字体大小 */
    margin: 5px 10px;  /* 设置按钮外边距 */
}
QMessageBox QPushButton:hover {
    background-color: #0056b3;  /* 设置按钮悬停时的背景颜色 */
}
"""

list_widget_style = """
    QListWidget {
        border: 1px solid #CCCCCC;
        border-radius: 8px;
        background-color: #FFFFFF;
        font-size: 14px;
        color: #444444;
    }
    QListWidget::item {
        padding: 10px;
        white-space: nowrap;  /* 防止文本换行 */
    }
    QListWidget::item:hover {
        background-color: #C0C0C0;
        border-radius: 8px;
    }
    QListWidget::item:selected {
        background-color: #A0A0A0;
        color: #000000;
        font-weight: bold;
    }
    QListWidget::item:focus {
        outline: none;
    }
    QListWidget:focus {
        outline: none;
    }
"""

button_style = """
    QPushButton {
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                          stop:0 rgba(180, 180, 180, 1), stop:1 rgba(140, 140, 140, 1));
        border: 1px solid #BBBBBB;
        border-radius: 8px;
        color: #000000;  /* 更黑亮的文本颜色 */
        font-weight: bold;  /* 加粗字体 */
        padding: 3px 12px;
        min-height: 22px;
        max-height: 22px;
        font-size: 16px;
        font-weight: bold;
        padding: 12px 24px;
        text-align: center;
        text-decoration: none;
        margin: 4px 2px;
        box-shadow: 3px 3px 5px rgba(0, 0, 0, 0.1);
    }

    QPushButton:hover {
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                          stop:0 rgba(140, 140, 140, 1), stop:1 rgba(100, 100, 100, 1));
        border: 1px solid #AAAAAA;
    }

    QPushButton:pressed {
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                          stop:0 rgba(100, 100, 100, 1), stop:1 rgba(80, 80, 80, 1));
        border: 1px solid #999999;
        box-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    }
"""

dialog_style = """
QDialog {
    background-color: #ffffff;  /* 白色背景 */

    border-radius: 15px;  /* 圆角 */
    padding: 30px;  /* 内边距 */
}
QLabel {
    font-size: 20px;  /* 标签字体大小 */
    color: #333333;  /* 标签字体颜色 */
    margin-bottom: 10px;  /* 标签底部外边距 */
}
QPushButton {
    background-color: #0078d7;  /* 按钮背景颜色 */
    color: white;  /* 按钮字体颜色 */
    padding: 12px 25px;  /* 按钮内边距 */
    border: none;  /* 无边框 */
    border-radius: 10px;  /* 按钮圆角 */
    font-size: 16px;  /* 按钮字体大小 */
    margin: 5px 0;  /* 按钮外边距 */
}
QPushButton:hover {
    background-color: #0056b3;  /* 按钮悬停背景颜色 */
}
"""

search_edit_style = """
    QLineEdit {
        border: 1px solid #CCCCCC;
        border-radius: 8px;
        padding: 10px;
        font-size: 20px;  /* 增大字体 */
        min-width: 100px;  /* 设置最小宽度 */
        height: 50px;  /* ✅ 增加搜索框高度 */
        background-color: #FFFFFF;
        color: #444444;
    }
"""

completer_popup_style = """
    QListView {
        font-size: 18px;  /* 调整字体大小 */
        padding: 8px;
        min-width: 300px;  /* 增加最小宽度 */
        min-height: 250px;  /* ✅ 增加预览框的最小高度 */
    }
"""

main_window_style = """
    QMainWindow {
        background-color: #F0F2F5;
    }
    QWidget {
        background-color: #F5F7FA;
    }
"""

left_widget_style = """
    QWidget {
        background-color: #F0F2F5;  /* 浅蓝色背景 */
        border-radius: 8px;  /* 圆角 */
    }
    QScrollBar:vertical {
        border: none;
        background: #F0F0F0;
        width: 10px;
        margin: 0px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background: #BBBBBB;
        min-height: 20px;
        border-radius: 5px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        background: none;
    }
    QScrollBar:horizontal {
        border: none;
        background: #F0F0F0;
        height: 10px;
        margin: 0px;
        border-radius: 5px;
    }
    QScrollBar::handle:horizontal {
        background: #BBBBBB;
        min-width: 20px;
        border-radius: 5px; 
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        background: none;
    }

"""

button_style = """
    QPushButton {
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                          stop:0 rgba(180, 180, 180, 1), stop:1 rgba(140, 140, 140, 1));
        border: 1px solid #BBBBBB;
        border-radius: 8px;
        color: #000000;  /* 更黑亮的文本颜色 */
        font-size: 16px;
        font-weight: bold;
        padding: 12px 25px;
        text-align: center;
        text-decoration: none;
        margin: 4px 2px;
        box-shadow: 3px 3px 5px rgba(0, 0, 0, 0.1);
    }

    QPushButton:hover {
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                          stop:0 rgba(140, 140, 140, 1), stop:1 rgba(100, 100, 100, 1));
        border: 1px solid #AAAAAA;
    }

    QPushButton:pressed {
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                          stop:0 rgba(100, 100, 100, 1), stop:1 rgba(80, 80, 80, 1));
        border: 1px solid #999999;
        box-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    }
"""


def get_user_input_file(parent):
    """获取用户输入的软件路径和脚本名称（与主窗口风格一致）"""
    dialog = QDialog(parent)
    dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
    dialog.setWindowTitle("创建软件脚本")
    dialog.setFixedSize(420, 300)
    dialog.setStyleSheet("""
        QDialog {
            background-color: #F5F7FA;
            border-radius: 12px;
            border: 1px solid #D0D0D0;
            font-family: 'Microsoft YaHei', Arial, sans-serif;
        }
        QLabel {
            font-size: 14px;
            color: #333333;
            padding: 4px;
            min-width: 70px;
        }
        QLineEdit {
            border: 1px solid #BBBBBB;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
            background-color: #FFFFFF;
            min-height: 36px;
            selection-background-color: #A0A0A0;
            box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
        }
        QLineEdit:focus {
            border: 1px solid #BBBBBB;  /* 与主窗口灰色风格一致 */
            box-shadow: 0 0 4px rgba(187, 187, 187, 0.5);
        }
        QPushButton {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                            stop:0 rgba(180, 180, 180, 1), 
                                            stop:1 rgba(140, 140, 140, 1));
            border: 1px solid #BBBBBB;
            border-radius: 8px;
            color: #000000;
            font-size: 14px;
            font-weight: bold;
            padding: 10px 20px;
            min-width: 100px;
            min-height: 40px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        QPushButton:hover {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                            stop:0 rgba(140, 140, 140, 1), 
                                            stop:1 rgba(100, 100, 100, 1));
            border: 1px solid #AAAAAA;
        }
        QPushButton:pressed {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                            stop:0 rgba(100, 100, 100, 1), 
                                            stop:1 rgba(80, 80, 80, 1));
            border: 1px solid #999999;
            box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.2);
        }
        QToolButton {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                            stop:0 rgba(200, 200, 200, 1),
                                            stop:1 rgba(170, 170, 170, 1));
            border: 1px solid #BBBBBB;
            border-radius: 6px;
            font-size: 16px;
            font-weight: bold;
            min-width: 40px;
            min-height: 36px;
            padding-bottom: 2px;
        }
        QToolButton:hover {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                            stop:0 rgba(180, 180, 180, 1),
                                            stop:1 rgba(150, 150, 150, 1));
            border: 1px solid #A0A0A0;
        }
        QToolButton:pressed {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                            stop:0 rgba(160, 160, 160, 1),
                                            stop:1 rgba(130, 130, 130, 1));
            padding-top: 2px;
            padding-left: 2px;
        }
    """)

    main_layout = QVBoxLayout(dialog)
    main_layout.setContentsMargins(20, 20, 20, 20)
    main_layout.setSpacing(25)

    # 输入区域
    name_widget = QWidget()
    name_layout = QHBoxLayout(name_widget)
    name_layout.setContentsMargins(0, 0, 0, 0)
    name_layout.setSpacing(10)

    name_label = QLabel("脚本名称:")
    name_edit = QLineEdit()
    name_edit.setPlaceholderText("例如: Photoshop")
    browse_button = QToolButton()
    browse_button.setText("📂")
    browse_button.setToolTip("选择文件")
    browse_button.setCursor(Qt.PointingHandCursor)
    browse_button.clicked.connect(lambda: browse_file(name_edit, dialog))

    name_layout.addWidget(name_label)
    name_layout.addWidget(name_edit)
    name_layout.addWidget(browse_button)
    main_layout.addWidget(name_widget)

    main_layout.addStretch()

    # 按钮区域
    button_widget = QWidget()
    button_layout = QHBoxLayout(button_widget)
    button_layout.setContentsMargins(0, 0, 0, 0)
    button_layout.setSpacing(15)

    ok_button = QPushButton("✔ 确定")
    ok_button.setCursor(Qt.PointingHandCursor)
    return_button = QPushButton("◀ 返回")
    return_button.setCursor(Qt.PointingHandCursor)
    return_button.clicked.connect(dialog.reject)

    button_layout.addStretch()
    button_layout.addWidget(ok_button)
    button_layout.addWidget(return_button)
    button_layout.addStretch()

    main_layout.addWidget(button_widget)

    dialog.setModal(True)
    name_edit.setFocus()
    name_edit.returnPressed.connect(lambda: validate_input())

    def validate_input():
        name = name_edit.text().strip()
        path = getattr(dialog, 'selected_path', None)
        if not name and not path:
            show_warning_dialog(dialog, "请输入脚本名称并选择文件路径")
        elif not name:
            show_warning_dialog(dialog, "请输入脚本名称")
        elif not path:
            show_warning_dialog(dialog, "请选择文件路径")
        else:
            dialog.accept()

    ok_button.clicked.connect(validate_input)

    if dialog.exec_() == QDialog.Accepted:
        name = name_edit.text().strip()
        path = getattr(dialog, 'selected_path', None)
        if name and path and os.path.exists(path):
            return name, path
    return None, None

def show_warning_dialog(parent, message):
    """显示统一的警告窗口（信息居中，仅一行）"""
    warning_dialog = QDialog(parent)
    warning_dialog.setWindowFlags(warning_dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
    warning_dialog.setWindowTitle("提示")
    warning_dialog.setFixedSize(420, 300)
    warning_dialog.setStyleSheet("""
        QDialog {
            background-color: #F5F7FA;
            border-radius: 12px;
            border: 1px solid #D0D0D0;
            font-family: 'Microsoft YaHei', Arial, sans-serif;
        }
        QLabel {
            font-size: 16px;
            color: #333333;
            padding: 10px;
        }
        QPushButton {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                            stop:0 rgba(180, 180, 180, 1), 
                                            stop:1 rgba(140, 140, 140, 1));
            border: 1px solid #BBBBBB;
            border-radius: 8px;
            color: #000000;
            font-size: 14px;
            font-weight: bold;
            padding: 10px 20px;
            min-width: 100px;
            min-height: 40px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        QPushButton:hover {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                            stop:0 rgba(140, 140, 140, 1), 
                                            stop:1 rgba(100, 100, 100, 1));
            border: 1px solid #AAAAAA;
        }
        QPushButton:pressed {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                            stop:0 rgba(100, 100, 100, 1), 
                                            stop:1 rgba(80, 80, 80, 1));
            border: 1px solid #999999;
            box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.2);
        }
    """)

    layout = QVBoxLayout(warning_dialog)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(20)

    # 警告文本（垂直和水平居中，仅一行）
    message_label = QLabel(f"⚠ {message}")
    message_label.setAlignment(Qt.AlignCenter)
    message_label.setWordWrap(False)  # 禁止换行
    # 设置最大宽度并截断超长文本
    font_metrics = QFontMetrics(message_label.font())
    max_width = 380  # 窗口宽度420减去左右边距20+20=40，留380px给文本
    elided_text = font_metrics.elidedText(f"⚠ {message}", Qt.ElideRight, max_width)
    message_label.setText(elided_text)

    # 使用拉伸将文本居中
    layout.addStretch(1)  # 上方拉伸
    layout.addWidget(message_label, alignment=Qt.AlignHCenter)
    layout.addStretch(1)  # 下方拉伸（文本和按钮之间）

    # 按钮区域（居中）
    button_container = QWidget()
    button_layout = QHBoxLayout(button_container)
    button_layout.setContentsMargins(0, 0, 0, 0)
    button_layout.setSpacing(15)

    ok_button = QPushButton("✔ 确定")
    ok_button.setCursor(Qt.PointingHandCursor)
    ok_button.clicked.connect(warning_dialog.accept)

    button_layout.addStretch()
    button_layout.addWidget(ok_button)
    button_layout.addStretch()

    layout.addWidget(button_container, alignment=Qt.AlignHCenter)
    layout.addStretch(1)  # 按钮下方拉伸

    warning_dialog.setModal(True)
    warning_dialog.exec_()


def browse_file(name_edit, dialog):
    """简单的文件选择功能"""
    file_path, _ = QFileDialog.getOpenFileName(
        parent=dialog,
        caption="选择可执行文件",
        directory=os.path.expanduser("~"),
        filter="程序文件 (*.exe *.bat *.cmd *.app *.sh);;所有文件 (*.*)"
    )
    if file_path:
        dialog.selected_path = file_path
        if not name_edit.text():
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            name_edit.setText(base_name)


def get_user_input_url(parent):
    """获取用户输入的网址和脚本名称（与主窗口风格一致）"""
    dialog = QDialog(parent)
    dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
    dialog.setWindowTitle("创建网页脚本")
    dialog.setFixedSize(420, 300)
    dialog.setStyleSheet("""
        QDialog {
            background-color: #F5F7FA;
            border-radius: 12px;
            border: 1px solid #D0D0D0;
            font-family: 'Microsoft YaHei', Arial, sans-serif;
        }
        QLabel {
            font-size: 14px;
            color: #333333;
            padding: 4px;
            min-width: 70px;
        }
        QLineEdit {
            border: 1px solid #BBBBBB;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
            background-color: #FFFFFF;
            min-height: 36px;
            selection-background-color: #A0A0A0;
            box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
        }
        QLineEdit:focus {
            border: 1px solid #BBBBBB;  /* 与主窗口灰色风格一致 */
            box-shadow: 0 0 4px rgba(187, 187, 187, 0.5);
        }
        QPushButton {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                            stop:0 rgba(180, 180, 180, 1), 
                                            stop:1 rgba(140, 140, 140, 1));
            border: 1px solid #BBBBBB;
            border-radius: 8px;
            color: #000000;
            font-size: 14px;
            font-weight: bold;
            padding: 10px 20px;
            min-width: 100px;
            min-height: 40px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        QPushButton:hover {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                            stop:0 rgba(140, 140, 140, 1), 
                                            stop:1 rgba(100, 100, 100, 1));
            border: 1px solid #AAAAAA;
        }
        QPushButton:pressed {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                            stop:0 rgba(100, 100, 100, 1), 
                                            stop:1 rgba(80, 80, 80, 1));
            border: 1px solid #999999;
            box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.2);
        }
    """)

    main_layout = QVBoxLayout(dialog)
    main_layout.setContentsMargins(20, 20, 20, 20)
    main_layout.setSpacing(25)

    # 输入区域
    input_widget = QWidget()
    input_layout = QGridLayout(input_widget)
    input_layout.setVerticalSpacing(20)
    input_layout.setHorizontalSpacing(10)

    name_label = QLabel("脚本名称:")
    name_edit = QLineEdit()
    name_edit.setPlaceholderText("例如: Google搜索")
    input_layout.addWidget(name_label, 0, 0, Qt.AlignRight | Qt.AlignVCenter)
    input_layout.addWidget(name_edit, 0, 1)

    url_label = QLabel("网址:")
    url_edit = QLineEdit()
    url_edit.setPlaceholderText("例如: https://www.google.com")
    input_layout.addWidget(url_label, 1, 0, Qt.AlignRight | Qt.AlignVCenter)
    input_layout.addWidget(url_edit, 1, 1)

    input_layout.setColumnStretch(1, 3)
    main_layout.addWidget(input_widget)

    # 按钮区域
    button_widget = QWidget()
    button_layout = QHBoxLayout(button_widget)
    button_layout.setContentsMargins(0, 0, 0, 0)
    button_layout.setSpacing(15)

    ok_button = QPushButton("✔ 确定")
    ok_button.setCursor(Qt.PointingHandCursor)
    return_button = QPushButton("◀ 返回")
    return_button.setCursor(Qt.PointingHandCursor)
    return_button.clicked.connect(dialog.reject)

    button_layout.addStretch()
    button_layout.addWidget(ok_button)
    button_layout.addWidget(return_button)
    button_layout.addStretch()

    main_layout.addStretch()
    main_layout.addWidget(button_widget)

    dialog.setModal(True)
    name_edit.setFocus()
    name_edit.returnPressed.connect(url_edit.setFocus)
    url_edit.returnPressed.connect(lambda: validate_input())

    def validate_input():
        name = name_edit.text().strip()
        url = url_edit.text().strip()
        if not name and not url:
            show_warning_dialog(dialog, "请输入脚本名称和网址")
        elif not name:
            show_warning_dialog(dialog, "请输入脚本名称")
        elif not url:
            show_warning_dialog(dialog, "请输入网址")
        else:
            dialog.accept()

    ok_button.clicked.connect(validate_input)

    if dialog.exec_() == QDialog.Accepted:
        name = name_edit.text().strip()
        url = url_edit.text().strip()
        if url and not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        if name and url:
            return name, url
    return None, None

def return_to_parent(parent, dialog):
    """关闭当前对话框并显示父窗口"""
    dialog.close()  # 关闭当前对话框
    if parent and hasattr(parent, 'show'):
        parent.show()  # 显示父窗口


class MergeScriptNameDialog(QDialog):
    """自定义合并脚本命名对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("命名合并脚本")
        self.setFixedSize(500, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F7FA;
                border-radius: 12px;
                border: 1px solid #D0D0D0;
                font-family: 'Microsoft YaHei', Arial, sans-serif;
            }
            QLabel {
                font-size: 16px;
                color: #333333;
                padding: 4px;
            }
            QLineEdit {
                border: 1px solid #BBBBBB;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: #FFFFFF;
                min-height: 36px;
                selection-background-color: #A0A0A0;
                box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
            }
            QLineEdit:focus {
                border: 1px solid #BBBBBB;
                box-shadow: 0 0 4px rgba(187, 187, 187, 0.5);
            }
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                                stop:0 rgba(180, 180, 180, 1), 
                                                stop:1 rgba(140, 140, 140, 1));
                border: 1px solid #BBBBBB;
                border-radius: 8px;
                color: #000000;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                min-width: 100px;
                min-height: 40px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                                stop:0 rgba(140, 140, 140, 1), 
                                                stop:1 rgba(100, 100, 100, 1));
                border: 1px solid #AAAAAA;
            }
            QPushButton:pressed {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                                stop:0 rgba(100, 100, 100, 1), 
                                                stop:1 rgba(80, 80, 80, 1));
                border: 1px solid #999999;
                box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.2);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)  # 增加左右边距
        layout.setSpacing(20)

        # 提示文本
        label = QLabel("请输入合并脚本的名称:")
        label.setAlignment(Qt.AlignCenter)
        layout.addStretch(1)
        layout.addWidget(label, alignment=Qt.AlignHCenter)

        # 加长输入框（关键修改）
        self.name_edit = QLineEdit()
        self.name_edit.setMinimumWidth(400)  # 设置最小宽度
        self.name_edit.setPlaceholderText("例如: 我的合并脚本")
        self.name_edit.setMaxLength(50)
        layout.addWidget(self.name_edit, alignment=Qt.AlignHCenter)
        layout.addStretch(1)

        # 按钮区域
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(15)

        ok_button = QPushButton("✔ 确定")
        ok_button.setCursor(Qt.PointingHandCursor)
        ok_button.clicked.connect(self.accept)

        cancel_button = QPushButton("✔ 取消")
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        button_layout.addStretch()

        layout.addWidget(button_container, alignment=Qt.AlignHCenter)
        layout.addStretch(1)

        self.setModal(True)
        self.name_edit.setFocus()

    def get_name(self):
        return self.name_edit.text().strip()



def setup_context_menu(list_widget, display_area):
    def context_menu_requested(position):
        menu = QMenu()
        rename_action = menu.addAction(tr("重命名脚本"))
        modify_path_action = menu.addAction(tr("修改路径"))
        delete_action = menu.addAction(tr("删除脚本"))

        action = menu.exec_(list_widget.viewport().mapToGlobal(position))

        if action == rename_action:
            selected_item = list_widget.currentItem()
            if selected_item:
                old_name = selected_item.text()
                new_name, ok = QInputDialog.getText(None, tr("重命名脚本"), tr("输入新脚本名称:"), text=old_name)
                if ok and new_name:
                    script_list = load_scripts()
                    if update_script_name(script_list, old_name, new_name):
                        selected_item.setText(new_name)
                        save_scripts(script_list)
                        appendLogWithEffect(display_area, f"脚本 '{old_name}' 已重命名为 '{new_name}'\n")
                        QMessageBox.information(None, tr("成功"), tr("脚本已重命名"))
                    else:
                        appendLogWithEffect(display_area, f"重命名 '{old_name}' 失败\n")
                        QMessageBox.warning(None, tr("失败"), tr("重命名失败"))

        elif action == delete_action:
            selected_item = list_widget.currentItem()
            if selected_item:
                script_name = selected_item.text()
                confirm = QMessageBox.question(
                    None, tr("确认删除"),
                    tr(f"确定要删除脚本 '{script_name}' 吗？"),
                    QMessageBox.Yes | QMessageBox.No
                )
                if confirm == QMessageBox.Yes:
                    script_list = load_scripts()
                    updated_list = delete_script(script_list, script_name)
                    save_scripts(updated_list)
                    list_widget.takeItem(list_widget.row(selected_item))
                    appendLogWithEffect(display_area, f"脚本 '{script_name}' 已删除\n")
                    QMessageBox.information(None, tr("成功"), tr("脚本已删除"))

        elif action == modify_path_action:
            selected_item = list_widget.currentItem()
            if selected_item:
                script_name = selected_item.text()
                script_list = load_scripts()
                script_data = next((s for s in script_list if s['name'] == script_name), None)
                if not script_data:
                    appendLogWithEffect(display_area, f"脚本 '{script_name}' 不存在\n")
                    QMessageBox.warning(None, tr("失败"), tr("脚本不存在"))
                    return

                script_type = script_data.get('type')
                current_path = script_data.get('value', '')

                if script_type == 'url':
                    new_url, ok = QInputDialog.getText(
                        None, tr("修改网址"),
                        tr("请输入新的网址:"), text=current_path
                    )
                    if ok and new_url:
                        success, old_path = update_script_path(script_list, script_name, new_url, display_area)
                        if success:
                            script_data['value'] = new_url
                            selected_item.setData(Qt.UserRole, script_data)
                            appendLogWithEffect(display_area,
                                                f"脚本 '{script_name}' 网址已修改: {old_path} -> {new_url}\n")
                            QMessageBox.information(None, tr("成功"), tr("网址已更新"))
                        else:
                            appendLogWithEffect(display_area, f"更新脚本 '{script_name}' 网址失败\n")
                            QMessageBox.warning(None, tr("失败"), tr("网址更新失败"))

                elif script_type == 'file':
                    new_path, _ = QFileDialog.getOpenFileName(
                        None, tr("选择新路径"), os.path.dirname(current_path), tr("所有文件 (*)")
                    )
                    if new_path:
                        success, old_path = update_script_path(script_list, script_name, new_path, display_area)
                        if success:
                            script_data['value'] = new_path
                            selected_item.setData(Qt.UserRole, script_data)
                            appendLogWithEffect(display_area,
                                                f"脚本 '{script_name}' 路径已修改: {old_path} -> {new_path}\n")
                            QMessageBox.information(None, tr("成功"), tr("路径已更新"))
                        else:
                            appendLogWithEffect(display_area, f"更新脚本 '{script_name}' 路径失败\n")
                            QMessageBox.warning(None, tr("失败"), tr("路径更新失败"))

                elif script_type == 'merge':
                    # 为合并脚本打开选择对话框
                    existing_scripts = load_scripts()
                    selection_dialog = MergeScriptSelectionDialog(None, existing_scripts, display_area)
                    if selection_dialog.exec_():
                        new_sub_scripts = selection_dialog.get_selected_scripts()
                        if new_sub_scripts:
                            success, old_value = update_script_path(script_list, script_name, new_sub_scripts,
                                                                    display_area)
                            if success:
                                script_data['value'] = new_sub_scripts
                                selected_item.setData(Qt.UserRole, script_data)
                                appendLogWithEffect(display_area,
                                                    f"合并脚本 '{script_name}' 已更新，包含 {len(new_sub_scripts)} 个子脚本\n")
                                QMessageBox.information(None, tr("成功"), tr("合并脚本已更新"))
                            else:
                                appendLogWithEffect(display_area, f"更新合并脚本 '{script_name}' 失败\n")
                                QMessageBox.warning(None, tr("失败"), tr("合并脚本更新失败"))

    list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
    list_widget.customContextMenuRequested.connect(context_menu_requested)

def create_merge_script(self):
    try:
        scripts = load_scripts()
        if not scripts:
            QMessageBox.warning(self, "警告", "当前没有任何脚本可合并！")
        else:
            selection_dialog = MergeScriptSelectionDialog(self, scripts, self.display_area)
            if selection_dialog.exec_():
                selected_scripts = selection_dialog.get_selected_scripts()
                if not selected_scripts:
                    QMessageBox.warning(self, "警告", "未选择任何脚本进行合并！")
                else:
                    # 使用自定义命名对话框替换 QInputDialog
                    name_dialog = MergeScriptNameDialog(self)
                    if name_dialog.exec_():
                        name = name_dialog.get_name()
                        if name:
                            item = QListWidgetItem(name)
                            item.setData(Qt.UserRole, {
                                'type': 'merge',
                                'value': [script for script in selected_scripts],
                                'name': name
                            })
                            self.list_widget.addItem(item)
                            self.completer_model.insertRow(0)
                            self.completer_model.setData(self.completer_model.index(0), name)
                            save_current_scripts()
                            update_item_colors()
                            appendLogWithEffect(self.display_area,
                                                f"创建合并脚本🔗 '{name}' 成功！包含 {len(selected_scripts)} 个子脚本\n")
                        else:
                            QMessageBox.warning(self, "警告", "脚本名称不能为空！")
    except Exception as e:
        appendLogWithEffect(self.display_area, f"Error creating merge script: {e}\n")
        QMessageBox.critical(self, tr('错误'), f"{tr('创建合并脚本时发生错误')}: {e}")

class MergeScriptSelectionDialog(QDialog):
    def __init__(self, parent=None, existing_scripts=None, display_area=None):
        super().__init__(parent)
        # 移除问号按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("选择并排序脚本")
        self.setMinimumSize(650, 550)
        self.setSizeGripEnabled(True)  # 允许调整窗口大小

        # 继承主窗口样式
        self.setStyleSheet("""
                    /* === 列表控件 === */
                    QListWidget {
                        outline: 0;  /* 去除焦点框 */
                        border: 1px solid #CCCCCC;
                        border-radius: 6px;
                        background-color: #FFFFFF;
                        font-size: 12px;
                    }
                    QListWidget::item {
                        padding: 6px;
                        border-bottom: 1px solid #EEEEEE;
                    }
                    QListWidget::item:selected {
                        background-color: #D0D0D0;
                        color: #000000;
                    }

                    /* === 完全匹配主窗口按钮样式，仅修改尺寸 === */
            QPushButton {
                /* 主窗口原始样式 */
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                                stop:0 rgba(180, 180, 180, 1), 
                                                stop:1 rgba(140, 140, 140, 1));
                border: 1px solid #BBBBBB;
                border-radius: 8px;
                color: #000000;
                font-size: 16px;    /* 保留主窗口字号 */
                font-weight: bold;  /* 保留加粗 */
                padding: 6px 12px;  /* 微调padding */
                min-height: 28px;   /* 比主窗口稍矮 */
                
                /* 新增自适应设置 */
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                                stop:0 rgba(160, 160, 160, 1),
                                                stop:1 rgba(120, 120, 120, 1));
            }
            QPushButton:pressed {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                                stop:0 rgba(140, 140, 140, 1),
                                                stop:1 rgba(100, 100, 100, 1));
            }

                    /* === 滚动条 === */
                    QScrollBar:vertical {
                        width: 10px;
                        background: #F0F0F0;
                    }
                    QScrollBar::handle:vertical {
                        background: #C0C0C0;
                        min-height: 20px;
                        border-radius: 5px;
                    }
                """)

        self.existing_scripts = existing_scripts or []
        self.display_area = display_area
        self.selected_scripts = []
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # === 双列表容器 ===
        lists_container = QWidget()
        lists_layout = QHBoxLayout(lists_container)
        lists_layout.setContentsMargins(0, 0, 0, 0)
        lists_layout.setSpacing(15)

        # ---- 可用脚本列表 ----
        available_group = QGroupBox("可用脚本 (双击添加)")
        available_group.setObjectName("AvailableGroup")
        self.available_list = QListWidget()
        self.available_list.setObjectName("AvailableList")
        self.available_list.setMinimumHeight(220)
        self.available_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.populate_list(self.available_list, self.existing_scripts)
        self.available_list.itemDoubleClicked.connect(self.add_to_selected)

        # ---- 已选脚本列表 ----
        selected_group = QGroupBox("已选脚本 (拖动排序)")
        selected_group.setObjectName("SelectedGroup")
        self.selected_list = QListWidget()
        self.selected_list.setObjectName("SelectedList")
        self.selected_list.setMinimumHeight(220)
        self.selected_list.setDragDropMode(QListWidget.InternalMove)
        self.selected_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.selected_list.itemDoubleClicked.connect(self.remove_from_selected)
        self.selected_list.model().rowsMoved.connect(self.update_preview)

        # 列表组布局
        available_group.setLayout(QVBoxLayout())
        available_group.layout().addWidget(self.available_list)

        selected_group.setLayout(QVBoxLayout())
        selected_group.layout().addWidget(self.selected_list)

        lists_layout.addWidget(available_group)
        lists_layout.addWidget(selected_group)

        # === 操作按钮 ===
        action_buttons = QWidget()
        action_layout = QHBoxLayout(action_buttons)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(10)

        self.remove_button = QPushButton("✖ 移除选中项")
        self.add_button = QPushButton("✔ 添加选中项")

        self.remove_button.setObjectName("RemoveButton")
        self.remove_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.remove_button.clicked.connect(self.remove_from_selected)


        self.add_button.setObjectName("AddButton")
        self.add_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.add_button.clicked.connect(self.add_to_selected)



        action_layout.addWidget(self.add_button)
        action_layout.addWidget(self.remove_button)

        # === 预览区域 ===
        preview_group = QGroupBox("执行顺序预览")
        preview_group.setObjectName("PreviewGroup")
        self.preview = QTextEdit()
        self.preview.setObjectName("PreviewText")
        self.preview.setMinimumHeight(150)
        self.preview.setReadOnly(True)
        preview_group.setLayout(QVBoxLayout())
        preview_group.layout().addWidget(self.preview)

        # === 确认按钮 ===
        confirm_buttons = QWidget()
        confirm_layout = QHBoxLayout(confirm_buttons)
        confirm_layout.setContentsMargins(0, 0, 0, 0)
        confirm_layout.setSpacing(10)

        self.confirm_button = QPushButton("✔ 确认合并")
        self.confirm_button.setObjectName("ConfirmButton")
        self.confirm_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.confirm_button.clicked.connect(self.accept)

        confirm_layout.addWidget(self.confirm_button)

        # === 主布局组装 ===
        main_layout.addWidget(lists_container, stretch=1)
        main_layout.addWidget(action_buttons)
        main_layout.addWidget(preview_group)
        main_layout.addWidget(confirm_buttons)

        # 初始更新预览
        self.update_preview()

    def populate_list(self, list_widget, scripts):
        """填充列表控件"""
        list_widget.clear()
        for script in scripts:
            item = QListWidgetItem(f"{script['name']} ({script['type']})")
            item.setData(Qt.UserRole, script)
            list_widget.addItem(item)

    def add_to_selected(self):
        """添加选中项到已选列表"""
        selected_items = self.available_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "提示", "请先在左侧选择要添加的脚本")
            return

        for item in selected_items:
            script_data = item.data(Qt.UserRole)
            if not self.is_script_in_list(self.selected_list, script_data['name']):
                new_item = QListWidgetItem(item.text())
                new_item.setData(Qt.UserRole, script_data)
                self.selected_list.addItem(new_item)
                self.available_list.takeItem(self.available_list.row(item))

        self.update_preview()



    def remove_from_selected(self):
        """从已选列表中移除选中项"""
        selected_items = self.selected_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "提示", "请先在右侧选择要移除的脚本")
            return

        for item in selected_items:
            script_data = item.data(Qt.UserRole)
            new_item = QListWidgetItem(item.text())
            new_item.setData(Qt.UserRole, script_data)
            self.available_list.addItem(new_item)
            self.selected_list.takeItem(self.selected_list.row(item))

        self.update_preview()

    def is_script_in_list(self, list_widget, script_name):
        """检查脚本是否已在列表中"""
        return any(
            list_widget.item(i).data(Qt.UserRole)['name'] == script_name
            for i in range(list_widget.count())
        )

    def update_preview(self):
        """生成简洁无框的脚本预览"""
        self.preview.clear()
        self.preview.setFont(QFont("Consolas", 10))  # 仍然使用等宽字体保证对齐

        if self.selected_list.count() == 0:
            self.preview.setPlainText("当前没有选择任何脚本")
            return

        # 列配置（列名，宽度，对齐方式）
        columns = [
            ("序号", 4, '^'),  # 居中
            ("类型", 8, '^'),
            ("脚本名称", 24, '<'),  # 左对齐
            ("路径/URL", 40, '<')
        ]

        # 生成表头
        header = "  ".join([f"{col[0]:{col[2]}{col[1]}}" for col in columns])
        separator = "-" * len(header)  # 简单的分隔线

        # 构建表格内容
        table_content = []
        table_content.append(header)
        table_content.append(separator)

        for i in range(self.selected_list.count()):
            item = self.selected_list.item(i)
            script = item.data(Qt.UserRole)

            # 处理显示内容
            script_type = "🌐 URL" if script['type'] == 'url' else "📂 文件"
            name = script['name'][:23] + ("..." if len(script['name']) > 23 else "")

            path = script['value']
            if script['type'] == 'merge':
                path = f"合并{len(script['value'])}个脚本"
            elif len(path) > 38:
                path = path[:35] + "..."  # 简单截断

            # 添加行
            row = [
                f"{i + 1:^{columns[0][1]}}",
                f"{script_type:^{columns[1][1]}}",
                f"{name:<{columns[2][1]}}",
                f"{path:<{columns[3][1]}}"
            ]
            table_content.append("  ".join(row))

        self.preview.setPlainText("\n".join(table_content))





    def get_selected_scripts(self):
        """获取最终选择的脚本列表"""
        return [
            self.selected_list.item(i).data(Qt.UserRole)
            for i in range(self.selected_list.count())
        ]


class CreateScriptDialog(QDialog):
    def __init__(self, parent=None, list_widget=None, display_area=None, completer_model=None):
        super(CreateScriptDialog, self).__init__(parent)
        # 移除问号按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.setWindowTitle("创建脚本")
        self.setFixedSize(420, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F7FA;
                border-radius: 10px;
                border: 1px solid #CCCCCC;
            }
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                                stop:0 rgba(180, 180, 180, 1), stop:1 rgba(140, 140, 140, 1));
                border: 1px solid #BBBBBB;
                border-radius: 8px;
                color: #000000;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 24px;
                text-align: center;
                text-decoration: none;
                margin: 4px 2px;
                box-shadow: 3px 3px 5px rgba(0, 0, 0, 0.1);
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                                stop:0 rgba(140, 140, 140, 1), stop:1 rgba(100, 100, 100, 1));
                border: 1px solid #AAAAAA;
            }
            QPushButton:pressed {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                                stop:0 rgba(100, 100, 100, 1), stop:1 rgba(80, 80, 80, 1));
                border: 1px solid #999999;
                box-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
            }
        """)

        self.list_widget = list_widget
        self.display_area = display_area
        self.completer_model = completer_model
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)

        create_web_script_button = QPushButton("🌐 创建网页脚本", self)
        create_web_script_button.setFixedSize(300, 65)
        create_web_script_button.clicked.connect(self.create_web_script)

        create_software_script_button = QPushButton("📂 创建软件脚本", self)
        create_software_script_button.setFixedSize(300, 65)
        create_software_script_button.clicked.connect(self.create_software_script)

        create_merge_script_button = QPushButton("🔗 合并脚本", self)
        create_merge_script_button.setFixedSize(300, 65)
        create_merge_script_button.clicked.connect(self.create_merge_script)

        layout.addWidget(create_web_script_button, alignment=Qt.AlignCenter)
        layout.addWidget(create_software_script_button, alignment=Qt.AlignCenter)
        layout.addWidget(create_merge_script_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def create_web_script(self):
        try:
            name, url = get_user_input_url(self)
            if name and url:
                item = QListWidgetItem(name)
                item.setData(Qt.UserRole, {'type': 'url', 'value': url, 'name': name})
                self.list_widget.addItem(item)
                self.completer_model.insertRow(0)
                self.completer_model.setData(self.completer_model.index(0), name)
                save_current_scripts()
                update_item_colors()
                appendLogWithEffect(self.display_area, f"创建网页脚本🌐 '{name}' 成功！\n")
                self.close()  # Add this line to close the dialog
        except Exception as e:
            appendLogWithEffect(self.display_area, f"Error creating web script: {e}\n")
            QMessageBox.critical(self, tr('错误'), f"{tr('创建网页脚本时发生错误')}: {e}")

    def create_software_script(self):
        try:
            name, file_path = get_user_input_file(self)
            if name and file_path:
                item = QListWidgetItem(name)
                item.setData(Qt.UserRole, {'type': 'file', 'value': file_path, 'name': name})
                self.list_widget.addItem(item)
                self.completer_model.insertRow(0)
                self.completer_model.setData(self.completer_model.index(0), name)
                save_current_scripts()
                update_item_colors()
                appendLogWithEffect(self.display_area, f"创建软件脚本🖥️ '{name}' 成功！\n")
        except Exception as e:
            appendLogWithEffect(self.display_area, f"Error creating software script: {e}\n")
            QMessageBox.critical(self, tr('错误'), f"{tr('创建软件脚本时发生错误')}: {e}")

    def create_merge_script(self):
        try:
            scripts = load_scripts()
            if not scripts:
                QMessageBox.warning(self, "警告", "当前没有任何脚本可合并！")
            else:
                selection_dialog = MergeScriptSelectionDialog(self, scripts, self.display_area)
                if selection_dialog.exec_():
                    selected_scripts = selection_dialog.get_selected_scripts()
                    if not selected_scripts:
                        QMessageBox.warning(self, "警告", "未选择任何脚本进行合并！")
                    else:
                        # Use the styled MergeScriptNameDialog instead of QInputDialog
                        name_dialog = MergeScriptNameDialog(self)
                        if name_dialog.exec_():
                            name = name_dialog.get_name()
                            if name:
                                item = QListWidgetItem(name)
                                item.setData(Qt.UserRole, {
                                    'type': 'merge',
                                    'value': [script for script in selected_scripts],
                                    'name': name
                                })
                                self.list_widget.addItem(item)
                                self.completer_model.insertRow(0)
                                self.completer_model.setData(self.completer_model.index(0), name)
                                save_current_scripts()
                                update_item_colors()
                                appendLogWithEffect(self.display_area,
                                                    f"创建合并脚本🔗 '{name}' 成功！包含 {len(selected_scripts)} 个子脚本\n")
                                self.close()  # Add this line to close the dialog
        except Exception as e:
            appendLogWithEffect(self.display_area, f"Error creating merge script: {e}\n")
            QMessageBox.critical(self, tr('错误'), f"{tr('创建合并脚本时发生错误')}: {e}")

class SmoothListWidget(QListWidget):
    def __init__(self, status_bar, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMouseTracking(True)
        self.hovered_item = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateScrollingOffsets)
        self.timer.start(7)
        self.model().rowsInserted.connect(self.on_rows_inserted)
        self.setItemDelegate(ScrollingItemDelegate(self))

    def updateScrollingOffsets(self):
        for i in range(self.count()):
            item = self.item(i)
            if self.is_text_overflow(item) and item != self.hovered_item:
                fm = QFontMetrics(self.font())
                text_width = fm.horizontalAdvance(item.text())
                available_width = self.viewport().width() - 20
                max_offset = text_width - available_width
                if max_offset <= 0:
                    continue
                scrolling_data = item.data(Qt.UserRole + 1)
                if scrolling_data is None:
                    scrolling_data = [0, 1]
                offset, direction = scrolling_data
                step = 0.2
                offset += step * direction
                if offset >= max_offset:
                    offset = max_offset
                    direction = -1
                elif offset <= 0:
                    offset = 0
                    direction = 1
                item.setData(Qt.UserRole + 1, [offset, direction])
        self.viewport().update()

    def is_text_overflow(self, item):
        fm = QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(item.text())
        available_width = self.viewport().width() - 20
        return text_width > available_width

    def mouseMoveEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            self.hovered_item = item
            script_data = item.data(Qt.UserRole)
            if script_data:
                script_name = script_data.get('name', '未知脚本')
                script_type = script_data.get('type', 'file')

                # 处理不同类型的状态栏显示
                if script_type == 'merge':
                    sub_scripts = script_data.get('value', [])
                    # 将所有子脚本名称用">>>"连接▶▷▶▷
                    sub_script_names = ' ▶▷▶▷ '.join(s['name'] for s in sub_scripts)
                    status_text = f"🔗 {script_name} | {sub_script_names}"
                else:
                    script_path = script_data.get('value', '未知路径')
                    short_path = script_path.split('/')[-1] if '/' in script_path else script_path
                    status_text = (
                        f"🌐 {script_name} | {short_path}" if script_type == "url"
                        else f"🖥️ {script_name} | {short_path}"
                    )

                # 限制状态栏文本长度为40个字符
                if len(status_text) > 150:
                    status_text = status_text[:37] + "..."

                self.status_bar.setText(status_text)

            # 设置 tooltip 为完整信息
            if self.is_text_overflow(item) or script_type == 'merge':
                if script_type == 'merge':
                    sub_scripts = script_data.get('value', [])
                    tooltip = "\n".join(
                        f"{i + 1}. {s['name']} ({s['type']}: {s['value']})"
                        for i, s in enumerate(sub_scripts)
                    )
                else:
                    tooltip = script_data.get('value', '')
                self.setToolTip(tooltip)
            else:
                self.setToolTip("")
        else:
            self.hovered_item = None
            self.status_bar.setText(">>> 准备就绪🚀")
            self.setToolTip("")
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.hovered_item = None
        self.setToolTip("")
        self.status_bar.setText(">>> 准备就绪🚀")
        super().leaveEvent(event)

    def on_rows_inserted(self, parent, start, end):
        for i in range(start, end + 1):
            item = self.item(i)
            if self.is_text_overflow(item):
                item.setData(Qt.UserRole + 1, [0, 1])


class ScrollingItemDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)
        self.list_widget = parent

    def paint(self, painter, option, index):
        item = self.list_widget.itemFromIndex(index)
        if item and self.list_widget.is_text_overflow(item):
            opt = QStyleOptionViewItem(option)
            self.initStyleOption(opt, index)
            original_text = opt.text
            opt.text = ""

            style = QApplication.style()

            if opt.state & QStyle.State_Selected:
                painter.fillRect(opt.rect, QColor("#D0D0D0"))
            elif opt.state & QStyle.State_MouseOver:
                painter.fillRect(opt.rect, QColor("#E0E0E0"))
            else:
                painter.fillRect(opt.rect,
                               QColor("#F5F5F5") if index.row() % 2 == 0
                               else QColor("#E8E8E8"))

            painter.save()
            painter.setClipRect(opt.rect)
            if opt.state & QStyle.State_Selected:
                painter.setPen(QColor("#000000"))
            else:
                painter.setPen(QColor("#444444"))

            textRect = style.subElementRect(QStyle.SE_ItemViewItemText, opt, self.list_widget)
            scrolling_data = item.data(Qt.UserRole + 1)
            offset = scrolling_data[0] if scrolling_data else 0
            textRect.setX(int(textRect.x() - offset))  # 将 offset 转换为整数
            painter.drawText(textRect, opt.displayAlignment, original_text)
            painter.restore()

            if opt.state & QStyle.State_HasFocus:
                style.drawPrimitive(QStyle.PE_FrameFocusRect, opt, painter, self.list_widget)
        else:
            super().paint(painter, option, index)


def show_create_script_dialog(parent, list_widget, display_area, completer_model):
    dialog = CreateScriptDialog(parent, list_widget, display_area, completer_model)
    dialog.setModal(True)  # 设置为模态对话框
    dialog.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    translator = QTranslator()
    current_language = 'zh'
    app.installTranslator(translator)
    main_window = create_main_window()
    main_window.show()
    sys.exit(app.exec_())
