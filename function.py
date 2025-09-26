import difflib
import os
import re
import json
import platform
import shutil
import sys
import win32con
import win32gui
import win32ui
from PyQt5.QtGui import QFontMetricsF, QPixmap, QIcon, QImage
import psutil
import GPUtil
import subprocess
import getpass
import wmi
import socket
import webbrowser
import requests
from datetime import datetime
from PyQt5 import QtGui
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QTextEdit,
    QPushButton, QWidget, QMessageBox, QInputDialog, QFileDialog,
    QDialog, QVBoxLayout, QLabel, QLineEdit, QListWidget
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from notification_manager import show_custom_notification
from utils import get_resource_path, CACHE_LOCK, ICON_CACHE, ICON_EXECUTOR  # 从新文件导入

# 脚本路径
scripts_path = get_resource_path("resources/scripts.json")


# 默认图标路径
DEFAULT_ICON_PATH = get_resource_path("resources/imge.png")

# 缓存机制
CACHE = {}

# 线程池
ICON_EXECUTOR = ThreadPoolExecutor(max_workers=32)

# **提前加载字典文件**
dictionary_path = get_resource_path('resources/english_words.txt')
# **构建索引**
word_to_translation = {}  # 直接查找单词 -> 翻译
translation_to_word = {}  # 直接查找翻译 -> 单词
all_words = []  # 仅存储所有英文单词，用于模糊匹配功能

dictionary_data = []

if os.path.exists(dictionary_path):
    with open(dictionary_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split("\t")
            if len(parts) >= 2:
                english_word = parts[0].strip().lower()
                translation = parts[1].strip()
                word_to_translation[english_word] = translation
                translation_to_word[translation] = english_word
                all_words.append(english_word)  # 仅存储英文单词，优化模糊匹配

else:
    print(f"❌ 词库文件未找到: {dictionary_path}")

if os.path.exists(dictionary_path):
    with open(dictionary_path, 'r', encoding='utf-8') as file:
        content = file.read()
        print("单词文本已加载。")
else:
    print("文件不存在，无法读取内容。")
    print(f"尝试从以下路径读取文件: {dictionary_path}")

# 多线程执行器
executor = ThreadPoolExecutor(max_workers=5)


def get_website_favicon(url, callback=None):
    """异步获取网站 favicon"""

    def fetch_icon():
        with CACHE_LOCK:
            if url in ICON_CACHE:
                return ICON_CACHE[url]
        try:
            if not url.startswith(('http://', 'https://')):
                url_normalized = 'https://' + url
            else:
                url_normalized = url
            favicon_url = url_normalized.rstrip('/') + '/favicon.ico'
            response = requests.get(favicon_url, timeout=2)
            if response.status_code == 200:
                pixmap = QPixmap()
                if pixmap.loadFromData(response.content):
                    icon = QIcon(pixmap)
                    if not icon.isNull():
                        with CACHE_LOCK:
                            ICON_CACHE[url] = icon
                        return icon
        except Exception:
            pass
        # 返回默认图标
        default_icon = QIcon(DEFAULT_ICON_PATH)
        with CACHE_LOCK:
            ICON_CACHE[url] = default_icon
        return default_icon

    if callback:
        future = ICON_EXECUTOR.submit(fetch_icon)
        future.add_done_callback(lambda f: callback(f.result()))
        return QIcon(DEFAULT_ICON_PATH)  # 立即返回默认图标
    else:
        return fetch_icon()


def get_file_icon(file_path, callback=None):
    """
    异步获取文件图标。

    此函数通过pywin32库从Windows系统中提取文件图标，并将其转换为QIcon对象。
    它使用缓存机制来避免重复提取，并通过线程池异步执行以防止UI阻塞。
    同时，它使用try...finally块来确保图标句柄在使用后被正确销毁，防止资源泄露。

    Args:
        file_path (str): 文件的完整路径。
        callback (callable, optional): 获取图标后的回调函数。默认为 None。

    Returns:
        QIcon: 如果是异步调用则立即返回一个默认图标，否则返回获取到的文件图标。
    """

    def fetch_icon():
        """
        内部函数，负责在工作线程中实际获取图标。
        """
        # 加锁以确保缓存访问的线程安全
        with CACHE_LOCK:
            if file_path in ICON_CACHE:
                return ICON_CACHE[file_path]

        icon = QIcon(DEFAULT_ICON_PATH)  # 默认图标
        large_icon_handle, small_icon_handle = 0, 0

        try:
            if platform.system() == "Windows" and os.path.exists(file_path):
                # 使用 win32gui.ExtractIconEx 提取大图标和小的图标
                # 传入0获取第一个图标
                large_icons, small_icons = win32gui.ExtractIconEx(file_path, 0)

                if large_icons:
                    # 仅处理第一个大图标
                    large_icon_handle = large_icons[0]

                    # 创建一个空的 QPixmap 对象
                    pixmap = QPixmap(32, 32)
                    pixmap.fill(Qt.transparent)

                    # 获取屏幕的设备上下文
                    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))

                    # 创建一个兼容的位图
                    hbmp = win32ui.CreateBitmap()
                    hbmp.CreateCompatibleBitmap(hdc, 32, 32)

                    # 创建内存设备上下文并选择位图
                    mem_dc = hdc.CreateCompatibleDC()
                    mem_dc.SelectObject(hbmp)

                    # 将图标绘制到内存设备上下文中
                    # DI_NORMAL标志表示正常绘制图标
                    win32gui.DrawIconEx(mem_dc.GetHandle(), 0, 0, large_icon_handle, 32, 32, 0, None,
                                        win32con.DI_NORMAL)

                    # 从位图中提取图像数据并加载到 QPixmap
                    bmpinfo = hbmp.GetInfo()
                    data = hbmp.GetBitmapBits(True)
                    # 使用QImage从原始位图数据创建图像对象
                    img = QImage(data, bmpinfo['bmWidth'], bmpinfo['bmHeight'], QtGui.QImage.Format_ARGB32)

                    # 检查img是否有效
                    if not img.isNull():
                        pixmap = QPixmap.fromImage(img)
                        # 将 QPixmap 转换为 QIcon
                        icon = QIcon(pixmap)

                    # 销毁内存设备上下文和位图
                    mem_dc.DeleteDC()
                    win32gui.DeleteObject(hbmp.GetHandle())

                if icon.isNull():
                    # 如果获取失败，使用默认图标
                    icon = QIcon(DEFAULT_ICON_PATH)

            # 缓存图标
            with CACHE_LOCK:
                ICON_CACHE[file_path] = icon
            return icon
        except Exception as e:
            # 捕获并打印异常，但程序继续运行
            print(f"❌ 获取文件图标失败: {file_path}, 错误: {e}")
            with CACHE_LOCK:
                ICON_CACHE[file_path] = icon
            return icon
        finally:
            # 确保在任何情况下都销毁图标句柄以防止资源泄漏
            if large_icon_handle:
                win32gui.DestroyIcon(large_icon_handle)
            if small_icon_handle:
                win32gui.DestroyIcon(small_icon_handle)

    if callback:
        # 如果提供了回调函数，则异步执行
        future = ICON_EXECUTOR.submit(fetch_icon)
        future.add_done_callback(lambda f: callback(f.result()))
        return QIcon(DEFAULT_ICON_PATH)  # 立即返回默认图标，UI不会被阻塞
    else:
        # 如果没有回调函数，则同步执行
        return fetch_icon()


def appendLog(log_text_edit, message):
    log_text_edit.append(message)
    log_text_edit.verticalScrollBar().setValue(log_text_edit.verticalScrollBar().maximum())


def update_log(log_text):
    log_file_path = get_resource_path('update_log.txt')
    print(f"日志文件路径: {log_file_path}")

    try:
        with open(log_file_path, "r", encoding="utf-8") as file:
            log_content = file.read()
            log_text.append(log_content)
    except FileNotFoundError:
        log_text.setText("日志文件未找到！")


def clear_display(display):
    """
    清空显示区域，并确保终止正在进行的日志更新
    """
    if hasattr(display, "log_updater") and display.log_updater.isRunning():
        display.log_updater.stop()
        display.log_updater.wait()
    display.clear()
    show_custom_notification(message="display_screen已初始化", icon=DEFAULT_ICON_PATH)


def query_and_display_result(word, result_label):
    """ 查询单词并显示结果 """
    result = query_local_dictionary(word)
    if result:
        # 直接访问列表中的第一个元素
        translation = result[0]["translation"]
        result_label.setText(f"🔤 {word}\n📖 {translation}")
    else:
        result_label.setText(f"⚠️ 未找到 '{word}'！")


# **读取并存入字典**
if os.path.exists(dictionary_path):
    with open(dictionary_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split("\t")  # **用 TAB 分割**
            if len(parts) >= 2:
                english_word = parts[0].strip().lower()
                translation = parts[1].strip()
                dictionary_data.append({"word": english_word, "translation": translation})


def query_local_dictionary(word, top_n=10):
    """
    **优化查询：**
    1️⃣ **O(1) 直接查找**
    2️⃣ **前缀匹配（英汉 & 汉英）**
    3️⃣ **模糊匹配（仅前缀匹配失败时触发）**
    """
    word = word.strip().lower()
    results = []

    # **1️⃣ 直接查找（O(1) 查询）**
    if word in word_to_translation:
        return [{"word": word, "translation": word_to_translation[word]}]
    if word in translation_to_word:
        return [{"word": translation_to_word[word], "translation": word}]

    # **2️⃣ 前缀匹配**
    prefix_matches = []

    # ✅ **英 → 汉 前缀匹配**
    for w in all_words:
        if w.startswith(word):
            prefix_matches.append((w, word_to_translation[w]))

    # ✅ **汉 → 英 前缀匹配**
    for t, w in translation_to_word.items():
        if t.startswith(word):  # 这里增加汉字前缀匹配
            prefix_matches.append((w, t))

    if prefix_matches:
        return [{"word": w, "translation": t} for w, t in prefix_matches[:top_n]]

    # **3️⃣ 最后才进行模糊匹配**
    matches = []

    # ✅ **英 → 汉 模糊匹配**
    for eng_word in all_words:
        similarity = difflib.SequenceMatcher(None, word, eng_word).ratio()
        if similarity > 0.1:
            matches.append((similarity, eng_word, word_to_translation[eng_word]))

    # ✅ **汉 → 英 模糊匹配**
    for trans, eng_word in translation_to_word.items():
        similarity = difflib.SequenceMatcher(None, word, trans).ratio()
        if similarity > 0.1:
            matches.append((similarity, eng_word, trans))

    # **按相似度排序**
    matches.sort(reverse=True, key=lambda x: x[0])
    return [{"word": eng, "translation": trans} for _, eng, trans in matches[:top_n]]


class CreateScriptDialog(QDialog):
    def __init__(self, parent=None):
        super(CreateScriptDialog, self).__init__(parent)
        self.setWindowTitle("选择脚本类型")
        self.setFixedSize(300, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        create_web_script_button = QPushButton("创建网页脚本", self)
        create_web_script_button.setStyleSheet("""
            QPushButton {
                background-color: #8B6914;
                color: white;
                border-radius: 10px;
                padding: 12px 20px;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid transparent;
                transition: background-color 0.3s, border-color 0.3s, color 0.3s;
            }
            QPushButton:hover {
                background-color: #A67C00;
                border-color: #A67C00;
            }
            QPushButton:pressed {
                background-color: #6E4600;
                border-color: #6E4600;
                color: #CCC;
            }
        """)
        create_web_script_button.setFixedSize(200, 50)
        create_web_script_button.clicked.connect(self.create_web_script)

        create_software_script_button = QPushButton("创建软件脚本", self)
        create_software_script_button.setStyleSheet("""
            QPushButton {
                background-color: #8B6914;
                color: white;
                border-radius: 10px;
                padding: 12px 20px;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid transparent;
                transition: background-color 0.3s, border-color 0.3s, color 0.3s;
            }
            QPushButton:hover {
                background-color: #A67C00;
                border-color: #A67C00;
            }
            QPushButton:pressed {
                background-color: #6E4600;
                border-color: #6E4600;
                color: #CCC;
            }
        """)
        create_software_script_button.setFixedSize(200, 50)
        create_software_script_button.clicked.connect(self.create_software_script)

        layout.addWidget(create_web_script_button)
        layout.addWidget(create_software_script_button)

        self.setLayout(layout)

    def create_web_script(self):
        print("创建网页脚本")
        self.accept()

    def create_software_script(self):
        print("创建软件脚本")
        self.accept()


class LogUpdater(QThread):
    update_signal = pyqtSignal(str)  # 发送更新文本的信号
    finished_signal = pyqtSignal()  # 发送完成信号

    def __init__(self, log_text_edit, message, speed=1, batch_size=1):
        """
        :param log_text_edit: 日志显示区域
        :param message: 需要显示的内容
        :param speed: 显示间隔时间（ms），默认5ms
        :param batch_size: 每次更新的字符数量，默认10
        """
        super().__init__()
        self.log_text_edit = log_text_edit
        self.message = message
        self.speed = speed  # 控制显示速度
        self.batch_size = batch_size  # 批量更新数量
        self.running = True  # 允许随时终止

    def run(self):
        """在子线程中逐步更新日志"""
        current_text = self.log_text_edit.toPlainText()
        for i in range(0, len(self.message), self.batch_size):  # 每次更新 batch_size 个字符
            if not self.running:
                break  # 如果外部要求终止，则立即停止
            current_text += self.message[i: i + self.batch_size]  # 追加批量内容
            self.update_signal.emit(current_text)  # 发送信号更新 UI
            self.msleep(self.speed)  # 控制速度（默认 5ms）
        self.finished_signal.emit()  # 发送完成信号

    def stop(self):
        """外部调用时立即停止"""
        self.running = False  # 终止标志位


def show_create_script_dialog(parent):
    dialog = CreateScriptDialog(parent)
    dialog.exec_()


def open_url(url):
    webbrowser.open(url)


def open_file(file_path):
    os.startfile(file_path)


def get_user_input_url(parent):
    url, ok = QInputDialog.getText(parent, "输入网址", "请输入网址:")
    if ok and url:
        name, name_ok = QInputDialog.getText(parent, "命名脚本", "请输入脚本名称 (可选):")
        if not name_ok or not name:
            name = url
        return name, url
    return None, None


def get_user_input_file(parent):
    file_path, _ = QFileDialog.getOpenFileName(parent, "选择文件", "", "所有文件 (*)")
    if file_path:
        name, name_ok = QInputDialog.getText(parent, "命名脚本", "请输入脚本名称 (可选):")
        if not name_ok or not name:
            name = file_path if len(file_path) <= 10 else file_path.split('/')[-1][:10] + "..."
        return name, file_path
    return None, None


# 获取资源文件路径（支持开发和打包环境）
def get_resource_path(relative_path):
    """
    获取资源文件路径（支持开发和打包环境）。
    优先使用EXE所在目录的resources文件夹，如果是scripts.json且不存在则复制或创建。

    Args:
        relative_path (str): 相对资源路径（如 "resources/scripts.json"）

    Returns:
        str: 资源文件的绝对路径
    """
    if getattr(sys, 'frozen', False):
        # 打包环境
        base_path = os.path.dirname(sys.executable)
        resources_dir = os.path.join(base_path, "resources")
        resource_path = os.path.join(base_path, relative_path)

        # 确保resources目录存在
        if not os.path.exists(resources_dir):
            original_resources = os.path.join(sys._MEIPASS, "resources")
            if os.path.exists(original_resources):
                shutil.copytree(original_resources, resources_dir)
                print(f"已复制资源文件夹到: {resources_dir}")
            else:
                os.makedirs(resources_dir, exist_ok=True)
                print(f"创建空的资源文件夹: {resources_dir}")

        # 特殊处理scripts.json
        if relative_path.endswith("scripts.json"):
            scripts_path = os.path.join(resources_dir, "scripts.json")
            # 如果scripts.json不存在，从sys._MEIPASS复制或创建空文件
            if not os.path.exists(scripts_path):
                temp_scripts_path = os.path.join(sys._MEIPASS, "resources", "scripts.json")
                if os.path.exists(temp_scripts_path):
                    shutil.copy2(temp_scripts_path, scripts_path)
                    print(f"已复制初始 scripts.json 到: {scripts_path}")
                else:
                    with open(scripts_path, 'w', encoding='utf-8') as file:
                        json.dump([], file, ensure_ascii=False, indent=4)
                    print(f"创建空的 scripts.json: {scripts_path}")
            return scripts_path

        # 其他资源文件优先使用EXE目录，如果不存在则回退到sys._MEIPASS
        if os.path.exists(resource_path):
            return resource_path
        else:
            temp_base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            return os.path.join(temp_base_path, relative_path)
    else:
        # 开发环境
        base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)


# 加载脚本
def load_scripts():
    """
    加载脚本列表从scripts.json文件。

    Returns:
        list: 脚本列表，如果加载失败返回空列表
    """
    scripts_path = get_resource_path("resources/scripts.json")
    print(f"尝试加载脚本文件: {scripts_path}")
    try:
        with open(scripts_path, 'r', encoding='utf-8') as file:
            scripts = json.load(file)
            print(f"成功加载脚本: {len(scripts)} 条")
            return scripts
    except FileNotFoundError:
        print(f"脚本文件未找到: {scripts_path}")
        return []
    except Exception as e:
        print(f"加载脚本失败: {e}")
        return []


# 保存脚本
def save_scripts(scripts):
    """
    保存脚本到scripts.json文件。
    始终写入到EXE所在目录的resources文件夹。

    Args:
        scripts (list): 要保存的脚本列表
    """
    scripts_path = get_resource_path("resources/scripts.json")
    try:
        # 确保resources目录存在
        os.makedirs(os.path.dirname(scripts_path), exist_ok=True)
        with open(scripts_path, 'w', encoding='utf-8') as file:
            json.dump(scripts, file, ensure_ascii=False, indent=4)
        print(f"脚本已保存到: {scripts_path}")
    except Exception as e:
        print(f"保存脚本失败: {e}")


def generateDivider(text_edit):
    """
    生成分割线
    """
    usable_width = text_edit.document().pageSize().width()  # 获取可用宽度
    font_metrics = QFontMetricsF(text_edit.font())  # 使用浮点精度计算字体宽度
    char_width = font_metrics.horizontalAdvance("〰")  # 计算"▓▒░"的像素宽度
    width = int(usable_width / char_width)  # 计算整行可以放多少个"▓▒░"
    divider = "〰" * max(1, width - 3)  # 确保最少 1 个
    return divider


def resizeEvent(self, event):
    """
    监听窗口大小变化，自动更新日志分割线
    """
    if hasattr(self, "display_area"):  # 确保日志窗口存在
        self.divider = generateDivider(self.display_area)  # 生成新的分割线
    super().resizeEvent(event)


def appendLogWithEffect(log_text_edit, message, speed=5, batch_size=50, include_timestamp=True):
    """
    使用子线程更新日志，防止阻塞 GUI，并可随时终止
    """
    if include_timestamp:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S: ')
        divider = generateDivider(log_text_edit)  # 生成分割线
        message = f"\n{timestamp}{message}{divider}"

    # 先停止已有的日志更新线程
    if hasattr(log_text_edit, "log_updater") and log_text_edit.log_updater.isRunning():
        log_text_edit.log_updater.stop()
        log_text_edit.log_updater.wait()

    log_text_edit.log_updater = LogUpdater(log_text_edit, message, speed, batch_size)

    log_text_edit.log_updater.update_signal.connect(lambda text: [
        log_text_edit.setPlainText(text),
        log_text_edit.moveCursor(QtGui.QTextCursor.End)
    ])

    log_text_edit.log_updater.finished_signal.connect(lambda: [
        log_text_edit.verticalScrollBar().setValue(log_text_edit.verticalScrollBar().maximum())
    ])

    log_text_edit.log_updater.start()  # 启动子线程


def log_message(message):
    print(message)


# 获取内存条型号函数
def get_memory_model():
    if 'memory_model' in CACHE:
        return CACHE['memory_model']
    try:
        computer = wmi.WMI()
        memory_modules = computer.Win32_PhysicalMemory()
        models = []
        for module in memory_modules:
            manufacturer = module.Manufacturer
            part_number = module.PartNumber
            if manufacturer and part_number:
                model_info = f"{manufacturer.strip()} {part_number.strip()}"
                models.append(model_info)
        CACHE['memory_model'] = models if models else ["获取失败"]
        return CACHE['memory_model']
    except Exception as e:
        log_message(f"获取内存条型号时出错: {e}")
        CACHE['memory_model'] = ["获取失败"]
        return CACHE['memory_model']


def get_cpu_temperature():
    if 'cpu_temperature' in CACHE:
        return CACHE['cpu_temperature']
    try:
        if platform.system() == "Windows":
            w = wmi.WMI(namespace="root\\wmi")
            temperature_info = w.MSAcpi_ThermalZoneTemperature()
            temps = []
            for temp in temperature_info:
                temps.append(f"CPU温度(需管理员权限): {temp.CurrentTemperature / 10.0 - 273.15:.1f}°C")
            CACHE['cpu_temperature'] = temps if temps else ["CPU温度(需管理员权限): ----"]
            return CACHE['cpu_temperature']

        elif platform.system() == "Linux":
            temps = []
            for zone in range(10):
                try:
                    with open(f"/sys/class/thermal/thermal_zone{zone}/temp") as f:
                        temp = int(f.read()) / 1000
                        temps.append(f"CPU温度(需管理员权限) {zone}: {temp:.1f}°C")
                except FileNotFoundError:
                    break
            CACHE['cpu_temperature'] = temps if temps else ["CPU温度(需管理员权限): ----"]
            return CACHE['cpu_temperature']

        elif platform.system() == "Darwin":
            temp = subprocess.check_output(["osx-cpu-temp"], encoding='utf-8').strip()
            CACHE['cpu_temperature'] = [f"CPU温度(需管理员权限): {temp}"]
            return CACHE['cpu_temperature']

        else:
            CACHE['cpu_temperature'] = ["CPU温度(需管理员权限): 不支持此操作系统"]
            return CACHE['cpu_temperature']

    except Exception as e:
        log_message(f"获取 CPU 温度时出错(需管理员权限): {e}")
        CACHE['cpu_temperature'] = ["CPU温度(需管理员权限): 获取失败"]
        return CACHE['cpu_temperature']


def get_gpu_temperature():
    if 'gpu_temperature' in CACHE:
        return CACHE['gpu_temperature']
    try:
        gpus = GPUtil.getGPUs()
        CACHE['gpu_temperature'] = [f"GPU温度: {gpu.temperature}°C" for gpu in gpus if gpu.temperature is not None]
        return CACHE['gpu_temperature']
    except Exception as e:
        log_message(f"获取 GPU 温度时出错: {e}")
        CACHE['gpu_temperature'] = ["GPU温度: 获取失败"]
        return CACHE['gpu_temperature']


def get_disk_info():
    if 'disk_info' in CACHE:
        return CACHE['disk_info']
    try:
        disk_info = []
        for part in sorted(psutil.disk_partitions(), key=lambda x: x.device):
            usage = psutil.disk_usage(part.mountpoint)
            total_space = usage.total / (1024 ** 3)
            used_space = usage.used / (1024 ** 3)
            free_space = usage.free / (1024 ** 3)
            usage_percent = usage.percent

            info_str = (
                f"\n{part.device} - 总容量: {total_space:.2f} GB  使用: {used_space:.2f} GB  "
                f"剩余: {free_space:.2f} GB  使用率: {usage_percent:.1f}%"
            )

            disk_info.append(info_str)

        CACHE['disk_info'] = disk_info
        return CACHE['disk_info']

    except Exception as e:
        log_message(f"获取磁盘信息时出错: {e}")
        CACHE['disk_info'] = ["磁盘信息: 获取失败"]
        return CACHE['disk_info']


def get_network_info():
    if 'network_info' in CACHE:
        return CACHE['network_info']
    try:
        addrs = psutil.net_if_addrs()
        interfaces = []
        iface_details = {}

        for iface_name, iface_addrs in addrs.items():
            for addr in iface_addrs:
                if iface_name not in iface_details:
                    iface_details[iface_name] = []
                if addr.family == socket.AF_INET:
                    iface_details[iface_name].append(f"  IP地址: {addr.address}")
                elif addr.family == psutil.AF_LINK:
                    iface_details[iface_name].append(f"  MAC地址: {addr.address}")

        for iface_name, details in iface_details.items():
            interfaces.append(
                f"〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰\n{iface_name}:\n" + "\n".join(details) + "\n")

        CACHE['network_info'] = interfaces
        return CACHE['network_info']
    except Exception as e:
        log_message(f"获取网络信息时出错: {e}")
        CACHE['network_info'] = ["网络信息: 获取失败"]
        return CACHE['network_info']


def get_boot_time():
    if 'boot_time' in CACHE:
        return CACHE['boot_time']
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        CACHE['boot_time'] = f"系统启动时间: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}"
        return CACHE['boot_time']
    except Exception as e:
        log_message(f"获取系统启动时间时出错: {e}")
        CACHE['boot_time'] = "系统启动时间: 获取失败"
        return CACHE['boot_time']


def get_wifi_info():
    if 'wifi_info' in CACHE:
        return CACHE['wifi_info']
    try:
        # 获取当前连接的 WiFi 网络信息
        current_network_output = subprocess.check_output(
            ['netsh', 'wlan', 'show', 'interfaces'],
            encoding='utf-8',
            creationflags=subprocess.CREATE_NO_WINDOW,
            stderr=subprocess.PIPE
        )
        # 提取 SSID
        current_network_match = re.search(r"SSID\s*:\s*(.+)", current_network_output)
        if not current_network_match:
            CACHE['wifi_info'] = "WiFi信息: 未连接到任何网络"
            return CACHE['wifi_info']
        current_network = current_network_match.group(1).strip()

        # 获取当前 WiFi 的密码
        try:
            current_profile_output = subprocess.check_output(
                ['netsh', 'wlan', 'show', 'profile', current_network, 'key=clear'],
                encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW,
                stderr=subprocess.PIPE
            )
            current_password_match = re.search(r"Key Content\s*:\s*(.+)", current_profile_output)
            current_password = current_password_match.group(1).strip() if current_password_match else "未知"
        except subprocess.CalledProcessError:
            current_password = "无法获取（可能需要管理员权限）"

        # 提取其他信息
        network_type_match = re.search(r"Network type\s*:\s*(.+)", current_network_output)
        network_type = network_type_match.group(1).strip() if network_type_match else "未知"

        radio_type_match = re.search(r"Radio type\s*:\s*(.+)", current_network_output)
        radio_type = radio_type_match.group(1).strip() if radio_type_match else "未知"

        signal_match = re.search(r"Signal\s*:\s*(.+)", current_network_output)
        signal = signal_match.group(1).strip() if signal_match else "未知"

        channel_match = re.search(r"Channel\s*:\s*(.+)", current_network_output)
        channel = channel_match.group(1).strip() if channel_match else "未知"

        authentication_match = re.search(r"Authentication\s*:\s*(.+)", current_network_output)
        authentication = authentication_match.group(1).strip() if authentication_match else "未知"

        cipher_match = re.search(r"Cipher\s*:\s*(.+)", current_network_output)
        cipher = cipher_match.group(1).strip() if cipher_match else "未知"

        connection_mode_match = re.search(r"Connection mode\s*:\s*(.+)", current_network_output)
        connection_mode = connection_mode_match.group(1).strip() if connection_mode_match else "未知"

        # 格式化当前 WiFi 信息
        current_wifi_info = (
            f"当前WiFi名称: {current_network}\n"
            f"当前WiFi密码: {current_password}\n"
            f"网络类型: {network_type}\n"
            f"无线电类型: {radio_type}\n"
            f"信号强度: {signal}\n"
            f"信道: {channel}\n"
            f"认证方式: {authentication}\n"
            f"加密方式: {cipher}\n"
            f"连接模式: {connection_mode}\n"
        )

        # 获取历史 WiFi 信息（简化，只取前 5 个）
        try:
            profile_list_output = subprocess.check_output(
                ['netsh', 'wlan', 'show', 'profiles'],
                encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW,
                stderr=subprocess.PIPE
            )
            profile_names = re.findall(r"All User Profile\s*:\s*(.*)", profile_list_output)[:5]
            recent_wifi_info = "最近连接的 WiFi:\n"
            for profile_name in profile_names:
                try:
                    profile_info_output = subprocess.check_output(
                        ['netsh', 'wlan', 'show', 'profile', profile_name, 'key=clear'],
                        encoding='utf-8',
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        stderr=subprocess.PIPE
                    )
                    password_match = re.search(r"Key Content\s*:\s*(.+)", profile_info_output)
                    password = password_match.group(1).strip() if password_match else "未知"
                    recent_wifi_info += f"  WiFi: {profile_name}, 密码: {password}\n"
                except subprocess.CalledProcessError:
                    continue
        except subprocess.CalledProcessError:
            recent_wifi_info = "最近连接的 WiFi: 无法获取\n"

        # 汇总信息
        final_wifi_info = f"{current_wifi_info}\n{recent_wifi_info}"
        CACHE['wifi_info'] = final_wifi_info
        return CACHE['wifi_info']

    except subprocess.CalledProcessError as e:
        print(f"获取 WiFi 信息失败: {e.stderr}")
        CACHE['wifi_info'] = "WiFi信息: 获取失败"
        return CACHE['wifi_info']
    except Exception as e:
        print(f"获取 WiFi 信息时出错: {e}")
        CACHE['wifi_info'] = "WiFi信息: 获取失败"
        return CACHE['wifi_info']


# 子函数：获取并格式化地理位置信息


def get_formatted_geolocation():
    if 'geolocation' in CACHE:
        return CACHE['geolocation']
    try:
        # 通过ip-api.com获取地理位置信息
        response = requests.get('http://ip-api.com/json/', timeout=5)  # 设置超时时间
        location_data = response.json()

        # 提取纬度、经度、城市、地区、国家和邮政编码
        lat = location_data.get('lat', '未知纬度')
        lon = location_data.get('lon', '未知经度')
        city = location_data.get('city', '未知城市')
        region = location_data.get('regionName', '未知地区')
        country = location_data.get('country', '未知国家')
        zip_code = location_data.get('zip', '未知邮政编码')

        # 格式化返回地理位置信息
        CACHE[
            'geolocation'] = f"纬度 {lat}, 经度 {lon}\n城市: {city}, 省份: {region}, 地区: {country}, 邮政编码: {zip_code}"
        return CACHE['geolocation']
    except Exception as e:
        CACHE['geolocation'] = f"通过IP获取地理位置信息时出错: {e}"
        return CACHE['geolocation']


def get_device_manufacturer():
    if 'device_manufacturer' in CACHE:
        return CACHE['device_manufacturer']
    try:
        computer = wmi.WMI()
        system_info = computer.Win32_ComputerSystem()[0]
        manufacturer = system_info.Manufacturer
        CACHE['device_manufacturer'] = manufacturer if manufacturer else "未知"
        return CACHE['device_manufacturer']
    except Exception as e:
        print(f"获取设备制造商信息时出错: {e}")
        CACHE['device_manufacturer'] = "获取失败"
        return CACHE['device_manufacturer']


def delete_script(script_list, script_name):
    """
    删除脚本。

    :param script_list: 当前的脚本列表，通常从 load_scripts() 获取。
    :param script_name: 要删除的脚本名称。
    :return: 更新后的脚本列表。
    """
    updated_list = [script for script in script_list if script['name'] != script_name]
    save_scripts(updated_list)
    return updated_list


def update_script_path(script_list, script_name, new_value, display_area=None):
    """
    更新脚本的路径或网址。

    :param script_list: 当前的脚本列表。
    :param script_name: 要更新的脚本名称。
    :param new_value: 新的路径或网址。
    :param display_area: 用于日志输出的显示区域（可选）。
    :return: (成功标志, 原路径)。
    """
    for script in script_list:
        if script['name'] == script_name:
            old_value = script['value']
            script['value'] = new_value
            save_scripts(script_list)  # 保存更新
            if display_area:
                appendLogWithEffect(display_area, f"脚本 '{script_name}' 的路径已更新\n")
            return True, old_value
    return False, None


def get_computer_info():
    try:
        user_name = getpass.getuser()
        system_info = platform.uname()
        os_version = platform.platform()
        boot_time = get_boot_time()
        cpu_percent = psutil.cpu_percent(interval=1)
        physical_cores = psutil.cpu_count(logical=False)
        total_cores = psutil.cpu_count(logical=True)
        memory_info = psutil.virtual_memory()
        memory_models = get_memory_model()
        disk_info = get_disk_info()
        network_info = get_network_info()
        wifi_info = get_wifi_info()
        cpu_temperature = get_cpu_temperature()
        gpu_temperature = get_gpu_temperature()
        device_manufacturer_info = get_device_manufacturer()
        # 调用获取地理位置信息的子函数
        location_info = get_formatted_geolocation()

        info_str = f"""
登录地区: {location_info}
设备用户名称: {user_name}

本设备组装商: {device_manufacturer_info}

操作系统: {system_info.system} {system_info.release}
操作系统版本: {os_version}

{boot_time}

处理器: {system_info.processor}
物理核心数: {physical_cores}
逻辑核心数: {total_cores}
CPU使用率: {cpu_percent}%
{' '.join(cpu_temperature)}

GPU信息:
GPU型号: {GPUtil.getGPUs()[0].name if GPUtil.getGPUs() else '无'}
GPU总显存: {GPUtil.getGPUs()[0].memoryTotal if GPUtil.getGPUs() else '无'} MB
GPU使用率: {GPUtil.getGPUs()[0].memoryUtil * 100 if GPUtil.getGPUs() else '无'}%
{' '.join(gpu_temperature)}

内存信息：
总内存: {memory_info.total / (1024 ** 3):.2f} GB
内存使用率: {memory_info.percent}%
{' '.join([f'内存条 {i + 1}: {model}' for i, model in enumerate(memory_models)])}

磁盘空间:{' '.join(disk_info)}

{wifi_info}

{' '.join(network_info)}

"""
        return info_str.strip()

    except Exception as e:
        log_message(f"获取计算机信息时出错: {e}")
        return "获取计算机信息失败"


def get_city_and_region():
    """
    获取当前设备的城市和地区信息。

    此函数通过调用 ip-api.com 的API，根据设备的公网IP查询地理位置。
    它会返回一个包含城市和地区信息的字符串。

    Returns:
        str: 格式化后的城市和地区字符串，例如 "广州市, 广东省"。
             如果获取失败，将返回"未知城市, 未知地区"。
    """
    try:
        # 通过ip-api.com获取地理位置信息
        response = requests.get('http://ip-api.com/json/?lang=zh-CN', timeout=3)
        response.raise_for_status()  # 检查请求是否成功

        location_data = response.json()

        if location_data.get('status') == 'success':
            city = location_data.get('city', '未知城市')
            region = location_data.get('regionName', '未知地区')
            return f"ip{region}"
        else:
            log_message(f"通过IP查询地理位置失败: {location_data.get('message', '未知错误')}")
            return "素未谋面"

    except requests.exceptions.RequestException as e:
        log_message(f"获取城市和地区时网络请求出错: {e}")
        return "素未谋面"
    except Exception as e:
        log_message(f"获取城市和地区时发生意外错误: {e}")
        return "素未谋面"
