import difflib
import os
import re
import json
import platform
import shutil
import sys

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
from window import get_resource_path

# 脚本路径
scripts_path = get_resource_path("resources/scripts.json")

# 缓存机制
CACHE = {}

# **提前加载字典文件**
dictionary_path = get_resource_path('english_words.txt')
# **构建索引**
word_to_translation = {}  # 直接查找单词 -> 翻译
translation_to_word = {}  # 直接查找翻译 -> 单词
all_words = []  # 仅存储所有英文单词，用于模糊匹配

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
        print(content)
else:
    print("文件不存在，无法读取内容。")
    print(f"尝试从以下路径读取文件: {dictionary_path}")

# 多线程执行器
executor = ThreadPoolExecutor(max_workers=5)

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
    finished_signal = pyqtSignal()   # 发送完成信号

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
    if getattr(sys, 'frozen', False):
        # 使用 EXE 所在目录作为基准路径
        base_path = os.path.dirname(sys.executable)
        resources_dir = os.path.join(base_path, "resources")
        # 如果资源目录不存在，则复制一份到 EXE 目录下
        if not os.path.exists(resources_dir):
            original_resources = os.path.join(sys._MEIPASS, "resources")
            shutil.copytree(original_resources, resources_dir)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)





# 加载脚本
def load_scripts():
    scripts_path = get_resource_path("resources/scripts.json")
    try:
        with open(scripts_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"脚本文件未找到: {scripts_path}")
        return []
    except Exception as e:
        print(f"加载脚本失败: {e}")
        return []

# 保存脚本
def save_scripts(scripts):
    scripts_path = get_resource_path("resources/scripts.json")
    try:
        with open(scripts_path, 'w', encoding='utf-8') as file:
            json.dump(scripts, file, ensure_ascii=False, indent=4)
        print(f"脚本已保存到: {scripts_path}")
    except Exception as e:
        print(f"保存脚本失败: {e}")



def appendLogWithEffect(log_text_edit, message, speed=5, batch_size=50, include_timestamp=True):
    """
    使用子线程更新日志，防止阻塞 GUI，并可随时终止
    :param log_text_edit: 文本显示区域
    :param message: 需要显示的内容
    :param speed: 显示间隔时间（ms）
    :param batch_size: 每次更新的字符数量
    :param include_timestamp: 是否在消息前添加时间戳，默认为 True
    """
    if include_timestamp:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S： ')
        divider = "▅" * 51  # 分界线，这里使用40个“▮”
        # 在前后加上空行，确保时间戳和分界线各自独占一行
        message = f"\n{timestamp}{message}{divider}"

    # 先停止已有的日志更新线程
    if hasattr(log_text_edit, "log_updater") and log_text_edit.log_updater.isRunning():
        log_text_edit.log_updater.stop()
        log_text_edit.log_updater.wait()

    # 创建新线程来更新日志
    log_text_edit.log_updater = LogUpdater(log_text_edit, message, speed, batch_size)

    # 在每次更新日志内容时，将光标移动到末尾
    log_text_edit.log_updater.update_signal.connect(lambda text: [
        log_text_edit.setPlainText(text),
        log_text_edit.moveCursor(QtGui.QTextCursor.End)
    ])

    # 在日志更新完成后，滚动到最底部
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
            interfaces.append(f"——————————————————————————————————————————————————————————————————————————————————————————\n{iface_name}:\n" + "\n".join(details) + "\n")

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
        current_network_output = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'], encoding='utf-8')
        # 尝试匹配 SSID 信息
        current_network_match = re.search(r"SSID\s*:\s*(.+)", current_network_output)
        if current_network_match:
            current_network = current_network_match.group(1).strip()
        else:
            current_network = "未知"

        # 获取当前连接WiFi的详细信息
        current_wifi_info = f"========================================WIFI信息==========================================\n\n当前WiFi名称: {current_network}\n{current_network_output}"

        # 获取当前WiFi的密码
        current_profile_output = subprocess.check_output(
            ['netsh', 'wlan', 'show', 'profile', current_network, 'key=clear'], encoding='utf-8')
        current_password_match = re.search(r"Key Content\s*:\s*(.+)", current_profile_output)
        current_password = current_password_match.group(1).strip() if current_password_match else "未知"
        current_wifi_info += f"——————————————————————————————————————————————————————————————————————————————————————————\n当前WiFi密码: {current_password}\n"

        # 获取当前连接WiFi的其他详细信息
        network_type_match = re.search(r"Network type\s*:\s*(.+)", current_network_output)
        network_type = network_type_match.group(1).strip() if network_type_match else "未知"

        radio_type_match = re.search(r"Radio type\s*:\s*(.+)", current_network_output)
        radio_type = radio_type_match.group(1).strip() if radio_type_match else "未知"

        receive_rate_match = re.search(r"Receive rate\s*:\s*(.+)", current_network_output)
        receive_rate = receive_rate_match.group(1).strip() if receive_rate_match else "未知"

        transmit_rate_match = re.search(r"Transmit rate\s*:\s*(.+)", current_network_output)
        transmit_rate = transmit_rate_match.group(1).strip() if transmit_rate_match else "未知"

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

        current_wifi_info += f"网络类型: {network_type}\n"
        current_wifi_info += f"无线电类型: {radio_type}\n"
        current_wifi_info += f"接收速率:同上\n"
        current_wifi_info += f"发送速率:同上\n"
        current_wifi_info += f"信号强度: {signal}\n"
        current_wifi_info += f"信道: {channel}\n"
        current_wifi_info += f"认证方式: {authentication}\n"
        current_wifi_info += f"加密方式: {cipher}\n"
        current_wifi_info += f"连接模式: {connection_mode}\n=====================================WiFi历史日志========================================="


        # 获取所有WiFi配置文件列表
        profile_list_output = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'], encoding='utf-8')

        # 提取所有WiFi配置文件名称
        profile_names = re.findall(r"All User Profile\s*:\s*(.*)", profile_list_output)

        # 初始化最近连接信息的变量
        recent_connections = []

        # 遍历每个WiFi配置文件，获取详细信息
        for profile_name in profile_names:
            try:
                profile_info_output = subprocess.check_output(
                    ['netsh', 'wlan', 'show', 'profile', profile_name, 'key=clear'], encoding='utf-8')

                # 获取密码信息
                password_match = re.search(r"Key Content\s*:\s*(.+)", profile_info_output)
                password = password_match.group(1).strip() if password_match else "未知"

                # 获取认证方式
                authentication_match = re.search(r"Authentication\s*:\s*(.+)", profile_info_output)
                authentication = authentication_match.group(1).strip() if authentication_match else "未知"

                # 获取加密方式
                cipher_match = re.search(r"Cipher\s*:\s*(.+)", profile_info_output)
                cipher = cipher_match.group(1).strip() if cipher_match else "未知"

                # 获取连接模式
                connection_mode_match = re.search(r"Connection mode\s*:\s*(.+)", profile_info_output)
                connection_mode = connection_mode_match.group(1).strip() if connection_mode_match else "未知"

                # 添加到最近连接的列表中
                recent_connections.append((profile_name.strip(), password, authentication, cipher, connection_mode))

            except Exception as e:
                print(f"获取WiFi配置文件 {profile_name} 信息时出错: {e}")

        # 只显示最近10次连接的不同名称的WiFi信息
        recent_connections = recent_connections[:10]

        recent_wifi_info = ""
        for profile_name, password, authentication, cipher, connection_mode in recent_connections:
            recent_wifi_info += f"——————————————————————————————————————————————————————————————————————————————————————————\nWiFi名称: {profile_name}\n"
            recent_wifi_info += f"密码: {password}\n"
            recent_wifi_info += f"认证方式: {authentication}\n"
            recent_wifi_info += f"加密方式: {cipher}\n"
            recent_wifi_info += f"连接模式: {connection_mode}\n"

        # 汇总当前连接和最近连接的信息
        final_wifi_info = current_wifi_info + "\n以下是最近连接过的WiFi信息：\n" + recent_wifi_info

        CACHE['wifi_info'] = final_wifi_info
        return CACHE['wifi_info']

    except Exception as e:
        print(f"获取WiFi信息时出错: {e}")
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
        CACHE['geolocation'] = f"纬度 {lat}, 经度 {lon}\n城市: {city}, 省份: {region}, 地区: {country}, 邮政编码: {zip_code}"
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
{' '.join([f'内存条 {i+1}: {model}' for i, model in enumerate(memory_models)])}

磁盘空间:{' '.join(disk_info)}

{wifi_info}

{' '.join(network_info)}

"""
        return info_str.strip()

    except Exception as e:
        log_message(f"获取计算机信息时出错: {e}")
        return "获取计算机信息失败"






