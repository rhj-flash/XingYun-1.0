import sys
import os
import weakref
from datetime import datetime
from PyQt5.QtGui import QColor, QBrush, QFontMetrics, QPalette
from PyQt5.QtCore import Qt, QStringListModel, QTranslator, QCoreApplication, QPropertyAnimation, QPoint, QEvent, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget,
    QLineEdit, QCompleter, QTextEdit, QPushButton, QFileDialog, QMessageBox,
    QInputDialog, QDialog, QListWidgetItem, QDesktopWidget, QMenu, QSizePolicy, QStyledItemDelegate,
    QStyleOptionViewItem, QStyle
)
from PyQt5.QtCore import QRect, QEasingCurve
from function import *
from PyQt5.QtCore import QVariantAnimation, QEasingCurve
from PyQt5.QtGui import QFontMetrics, QPainter

def animate_search_edit_height(target_height):
    animation = QPropertyAnimation(search_edit, b"maximumHeight")
    animation.setDuration(300)  # 300毫秒
    animation.setStartValue(search_edit.height())
    animation.setEndValue(target_height)
    animation.setEasingCurve(QEasingCurve.InOutQuad)  # 缓和曲线
    animation.start()
    # 保存引用，防止动画被垃圾回收
    search_edit.animation = animation




def get_resource_path(filename):
    """ 获取 `resources/` 目录下的资源文件路径，兼容不同运行环境 """
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', filename)

dictionary_path = get_resource_path('english_words.txt')

def animate_search_edit_height(target_height):
    animation = QPropertyAnimation(search_edit, b"minimumHeight")
    animation.setDuration(300)  # 动画时长 300 毫秒
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

                # 获取脚本数据
                script_data = next((s for s in script_list if s['name'] == script_name), None)
                if not script_data:
                    appendLogWithEffect(display_area, f"脚本 '{script_name}' 不存在\n")
                    QMessageBox.warning(None, tr("失败"), tr("脚本不存在"))
                    return

                script_type = script_data.get('type')
                current_path = script_data.get('value', '')

                if script_type == 'url':  # 网页脚本
                    new_url, ok = QInputDialog.getText(
                        None, tr("修改网址"),
                        tr("请输入新的网址:"), text=current_path  # 显示当前网址
                    )
                    if ok and new_url:
                        success, old_path = update_script_path(script_list, script_name, new_url, display_area)
                        if success:
                            appendLogWithEffect(display_area,
                                                f"脚本 '{script_name}' 网址已修改: {old_path} -> {new_url}\n")
                            QMessageBox.information(None, tr("成功"), tr("网址已更新"))
                        else:
                            appendLogWithEffect(display_area, f"更新脚本 '{script_name}' 网址失败\n")
                            QMessageBox.warning(None, tr("失败"), tr("网址更新失败"))

                elif script_type == 'file':  # 软件脚本
                    new_path, ok = QFileDialog.getOpenFileName(
                        None, tr("选择新路径"), os.path.dirname(current_path), tr("所有文件 (*)")
                    )
                    if ok and new_path:
                        success, old_path = update_script_path(script_list, script_name, new_path, display_area)
                        if success:
                            appendLogWithEffect(display_area,
                                                f"脚本 '{script_name}' 路径已修改: {old_path} -> {new_path}\n")
                            QMessageBox.information(None, tr("成功"), tr("路径已更新"))
                        else:
                            appendLogWithEffect(display_area, f"更新脚本 '{script_name}' 路径失败\n")
                            QMessageBox.warning(None, tr("失败"), tr("路径更新失败"))

    list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
    list_widget.customContextMenuRequested.connect(context_menu_requested)

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
        icon_path = "imge.png"  # 如果找不到，使用相对路径
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
    status_layout.addWidget(english_learn_button)  # 添加按钮到状态栏容器
    status_layout.setContentsMargins(0, 0, 0, 0)
    status_layout.setSpacing(0)
    status_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    status_container.setFixedHeight(30)  # 确保状态栏容器的高度与按钮一致

    list_widget = SmoothListWidget(status_bar)  # 使用自定义的 SmoothListWidget
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

        appendLogWithEffect(display_area, """
        
        
        
=======================================================================================        
🔴已开启单词查询模式\n 
            
 _______  _        _______  _       _________ _______          
(  ____ \( (    /|(  ____ \( \      \__   __/(  ____ \|\     /|
| (    \/|  \  ( || (    \/| (         ) (   | (    \/| )   ( |
| (__    |   \ | || |      | |         | |   | (_____ | (___) |
|  __)   | (\ \) || | ____ | |         | |   (_____  )|  ___  |
| (      | | \   || | \_  )| |         | |         ) || (   ) |
| (____/\| )  \  || (___) || (____/\___) (___/\____) || )   ( |
(_______/|/    )_)(_______)(_______/\_______/\_______)|/     \|
     
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
        appendLogWithEffect(display_area, """
=======================================================================================
🔵已退出单词查询模式\n
 ____  _  _  ____  ____ 
( ___)( \/ )(_  _)(_  _)
 )__)  )  (  _)(_   )(  
(____)(_/\_)(____) (__) \n""")
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


def save_list_order():
    """
    当用户拖拽调整顺序后，自动更新 `scripts.json`
    """
    scripts = []
    for i in range(list_widget.count()):
        item = list_widget.item(i)
        script_data = item.data(Qt.UserRole)  # 读取脚本数据
        scripts.append(script_data)

    save_scripts(scripts)  # 保存新的脚本顺序


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
        if script_type == 'url':
            open_url(script_value)
            appendLogWithEffect(display_area, f">>>>> {timestamp} : {tr('执行打开>>>>>')} {item.text()}\n")
        elif script_type == 'file':
            open_file(script_value)
            appendLogWithEffect(display_area, f">>>>> {timestamp} : {tr('执行打开>>>>>')} {item.text()}\n")
        list_widget.setToolTip(script_value)
    except Exception as e:
        appendLogWithEffect(display_area, f"Error executing script: {e}\n")
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
            for item in selected_items:
                script_name = item.text()
                list_widget.takeItem(list_widget.row(item))
                completer_items = completer_model.stringList()
                completer_items.remove(script_name)
                completer_model.setStringList(completer_items)
                save_current_scripts()
                update_item_colors()  # ✅ 删除后更新颜色
                appendLogWithEffect(display_area, f"======================================================================================\n脚本 '{script_name}' 已删除！\n======================================================================================\n")  # 添加日志
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
            "=========================================================================================\n"

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
======================================================================================
加载完毕...
"""

    appendLogWithEffect(display_area, welcome_message)


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
        background-color: #F0F2F5;  /* 更浅的灰蓝色 */
    }
    QWidget {
        background-color: #F5F7FA;  /* 淡淡的蓝灰色 */
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






class CreateScriptDialog(QDialog):
    def __init__(self, parent=None, list_widget=None, display_area=None, completer_model=None):
        super(CreateScriptDialog, self).__init__(parent)
        self.setWindowTitle("创建脚本")
        self.setFixedSize(420, 250)  # 调整窗口大小
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F7FA;  /* 浅灰色背景，与主窗口一致 */
                border-radius: 10px;  /* 圆角 */
                border: 1px solid #CCCCCC;
            }
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 rgba(180, 180, 180, 1), stop:1 rgba(140, 140, 140, 1));
                border: 1px solid #BBBBBB;
                border-radius: 8px;
                color: #000000;  /* 更黑亮的文本颜色 */
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
        layout.setSpacing(20)  # 按钮之间的间距
        layout.setAlignment(Qt.AlignCenter)  # 居中对齐

        create_web_script_button = QPushButton("🌐 创建网页脚本", self)
        create_web_script_button.setFixedSize(300, 65)
        create_web_script_button.clicked.connect(self.create_web_script)

        create_software_script_button = QPushButton("📂 创建软件脚本", self)
        create_software_script_button.setFixedSize(300, 65)
        create_software_script_button.clicked.connect(self.create_software_script)

        layout.addWidget(create_web_script_button, alignment=Qt.AlignCenter)
        layout.addWidget(create_software_script_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def create_web_script(self):
        """ 创建网页脚本 """
        try:
            name, url = get_user_input_url(self)
            if name and url:
                item = QListWidgetItem(name)
                item.setData(Qt.UserRole, {'type': 'url', 'value': url, 'name': name})
                list_widget.addItem(item)
                completer_model.insertRow(0)
                completer_model.setData(completer_model.index(0), name)
                save_current_scripts()
                update_item_colors()  # 确保颜色实时更新
                appendLogWithEffect(self.display_area, f"======================================================================================\n创建网页脚本🌐 '{name}' 成功！\n======================================================================================\n")  # 添加日志
            self.accept()
        except Exception as e:
            appendLogWithEffect(self.display_area, f"Error creating web script: {e}\n")
            QMessageBox.critical(self, tr('错误'), f"{tr('创建网页脚本时发生错误')}: {e}")

    def create_software_script(self):
        """ 创建软件脚本 """
        try:
            name, file_path = get_user_input_file(self)
            if name and file_path:
                item = QListWidgetItem(name)
                item.setData(Qt.UserRole, {'type': 'file', 'value': file_path, 'name': name})
                list_widget.addItem(item)
                completer_model.insertRow(0)
                completer_model.setData(completer_model.index(0), name)
                save_current_scripts()
                update_item_colors()  # 确保颜色实时更新
                appendLogWithEffect(self.display_area, f"======================================================================================\n创建软件脚本🖥️ '{name}' 成功！\n======================================================================================\n")  # 添加日志
            self.accept()
        except Exception as e:
            appendLogWithEffect(self.display_area, f"Error creating software script: {e}\n")
            QMessageBox.critical(self, tr('错误'), f"{tr('创建软件脚本时发生错误')}: {e}")



class SmoothListWidget(QListWidget):
    def __init__(self, status_bar, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMouseTracking(True)
        self.hovered_item = None  # 当前鼠标悬停的项

        # 定时器用于更新滚动偏移
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateScrollingOffsets)
        self.timer.start(30)  # 每30毫秒更新一次

        # 连接模型信号
        self.model().rowsInserted.connect(self.on_rows_inserted)
        # rowsRemoved 无需做额外操作

        # 设置自定义委托，利用滚动数据绘制文本
        self.setItemDelegate(ScrollingItemDelegate(self))

    def updateScrollingOffsets(self):
        for i in range(self.count()):
            item = self.item(i)
            # 如果文本超出且当前项不处于鼠标悬停状态，则更新滚动数据
            if self.is_text_overflow(item) and item != self.hovered_item:
                fm = QFontMetrics(self.font())
                text_width = fm.horizontalAdvance(item.text())
                available_width = self.viewport().width() - 20  # 预留边距
                max_offset = text_width - available_width
                if max_offset <= 0:
                    continue
                # 尝试从额外数据中获取滚动数据，没有则初始化为 [0, 1]
                scrolling_data = item.data(Qt.UserRole + 1)
                if scrolling_data is None:
                    scrolling_data = [0, 1]
                offset, direction = scrolling_data
                step = 1  # 每次移动1个像素，可调整滚动速度
                offset += step * direction
                # 达到边界时反转方向
                if offset >= max_offset:
                    offset = max_offset
                    direction = -1
                elif offset <= 0:
                    offset = 0
                    direction = 1
                item.setData(Qt.UserRole + 1, [offset, direction])
        self.viewport().update()  # 触发重绘

    def is_text_overflow(self, item):
        fm = QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(item.text())
        available_width = self.viewport().width() - 20
        return text_width > available_width

    def mouseMoveEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            self.hovered_item = item
            # 更新状态栏显示
            script_data = item.data(Qt.UserRole)
            if script_data:
                script_name = script_data.get('name', '未知脚本')
                script_path = script_data.get('value', '未知路径')
                script_type = script_data.get('type', 'file')
                self.status_bar.setText(
                    f"🌐 {script_name} | 🔗 {script_path}" if script_type == "url"
                    else f"🖥️ {script_name} | 📂 {script_path}")
            # 当鼠标悬停时，可选择不更新滚动数据，从而暂停运动
            self.setToolTip(item.text() if self.is_text_overflow(item) else "")
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
                # 初始化额外数据存储滚动信息
                item.setData(Qt.UserRole + 1, [0, 1])


class ScrollingItemDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)
        self.list_widget = parent

    def paint(self, painter, option, index):
        item = self.list_widget.itemFromIndex(index)
        if item and self.list_widget.is_text_overflow(item):
            # 初始化样式选项
            opt = QStyleOptionViewItem(option)
            self.initStyleOption(opt, index)
            original_text = opt.text  # 保存原始文本
            opt.text = ""  # 清空 opt.text，防止默认绘制

            style = QApplication.style()

            # --- 强制覆盖选中状态的背景颜色 ---
            if opt.state & QStyle.State_Selected:
                # 选中项的背景颜色设置为深灰色
                painter.fillRect(opt.rect, QColor("#A0A0A0"))  # 深灰色
            elif opt.state & QStyle.State_MouseOver:
                # 悬停项的背景颜色设置为浅灰色
                painter.fillRect(opt.rect, QColor("#C0C0C0"))  # 浅灰色
            else:
                # 未选中项的背景颜色根据行号设置
                painter.fillRect(opt.rect, QColor("#F5F5F5" if index.row() % 2 == 0 else "#E8E8E8"))

            # --- 强制覆盖文本颜色 ---
            painter.save()
            painter.setClipRect(opt.rect)
            if opt.state & QStyle.State_Selected:
                painter.setPen(QColor("#000000"))  # 选中时文本为黑色
            else:
                painter.setPen(QColor("#444444"))  # 未选中时文本为深灰色

            # --- 绘制文本 ---
            textRect = style.subElementRect(QStyle.SE_ItemViewItemText, opt, self.list_widget)
            scrolling_data = item.data(Qt.UserRole + 1)
            offset = scrolling_data[0] if scrolling_data else 0
            textRect.setX(textRect.x() - offset)
            painter.drawText(textRect, opt.displayAlignment, original_text)
            painter.restore()

            # --- 绘制焦点框（如果需要）---
            if opt.state & QStyle.State_HasFocus:
                style.drawPrimitive(QStyle.PE_FrameFocusRect, opt, painter, self.list_widget)
        else:
            # 其他项使用默认绘制
            super().paint(painter, option, index)

def show_create_script_dialog(parent, list_widget, display_area, completer_model):
    dialog = CreateScriptDialog(parent, list_widget, display_area, completer_model)
    dialog.exec_()






if __name__ == '__main__':
    app = QApplication(sys.argv)
    translator = QTranslator()
    current_language = 'zh'
    app.installTranslator(translator)
    main_window = create_main_window()
    main_window.show()
    sys.exit(app.exec_())
