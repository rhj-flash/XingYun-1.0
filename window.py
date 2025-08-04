import hashlib
import threading  # 确保导入 threading 模块
import time
from urllib.parse import urlparse, urljoin

from PyQt5.QtCore import QEasingCurve, QParallelAnimationGroup
from PyQt5.QtCore import QRect
from PyQt5.QtCore import QStringListModel, QTranslator, QCoreApplication, QPropertyAnimation, QPoint, QEvent, \
    QTimer, QObject, QRectF, QSize, QDateTime
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtGui import QFontMetrics, QPainter
from PyQt5.QtGui import QImage, QLinearGradient
from PyQt5.QtWidgets import QGroupBox, QAction
from PyQt5.QtWidgets import (
    QHBoxLayout, QSplitter, QCompleter, QListWidgetItem, QDesktopWidget, QMenu, QSizePolicy, QStyledItemDelegate,
    QStyle, QGridLayout, QToolButton
)
from bs4 import BeautifulSoup
from selenium import webdriver

from function import *

#    EXE打包指令
"""
=======================
PyInstaller打包配置说明
=======================

使用以下命令进行打包（PowerShell格式）：

pyinstaller `
    --onefile `
    --noconsole `
    --name Xingyun `
    --clean `
    --icon="resources/icon.ico" `
    --add-data "resources;resources" `
    window.py
"""

# 通用的滚动条透明样式
scrollbar_style = """
    QScrollBar:vertical, QScrollBar:horizontal {
        border: none;
        background: transparent !important;  /* 强制透明 */
        width: 10px;
        height: 10px;
        margin: 0px;
        padding: 0px;
    }
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
        background: #BBBBBB;  /* 日间模式滑块颜色 */
        min-height: 20px;
        min-width: 20px;
        border-radius: 5px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        background: none;
        height: 0px;
        width: 0px;
        border: none;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
        background: transparent !important;  /* 确保滑轨透明 */
    }
"""

# 夜间模式的滚动条样式
scrollbar_style_night = """
    QScrollBar:vertical, QScrollBar::horizontal {
        border: none;
        background: transparent !important;  /* 强制透明 */
        width: 10px;
        height: 10px;
        margin: 0px;
        padding: 0px;
    }
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
        background: #777777;  /* 夜间模式滑块颜色 */
        min-height: 20px;
        min-width: 20px;
        border-radius: 5px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        background: none;
        height: 0px;
        width: 0px;
        border: none;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
        background: transparent !important;  /* 确保滑轨透明 */
    }
"""


# 日间模式样式
display_area_style = """
    QTextEdit {
        border: 0px solid #CCCCCC;
        border-radius: 8px;
        background-color: #F0F2F5;
        font-family: 'Sarasa Gothic', 'Consolas', 'Courier New', sans-serif;
        font-size: 14px;
        color: #000000;
        padding: 10px;
    }
""" + scrollbar_style
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

# 日间模式样式
list_widget_style = """
    QListWidget {
        border: 0px solid #CCCCCC;
        border-radius: 8px;
        background-color: #F0F2F5;
        font-family: 'Comic Sans MS', 'KaiTi', sans-serif;
        font-size: 16px;
        font-weight: bold;
        color: #000000;
    }
    QListWidget::item {
        padding: 12px 10px;
        height: 26px;
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
""" + scrollbar_style

dialog_style = """
QDialog {
    background-color: #ffffff;
    font-family: 'Sarasa Gothic', 'Consolas', 'Courier New', sans-serif;
    border-radius: 15px;
    padding: 30px;
}
QLabel {
    font-size: 20px;
    color: #333333;
    margin-bottom: 10px;
}
QPushButton {
    background-color: #0078d7;
    color: white;
    padding: 12px 25px;
    border: none;
    border-radius: 10px;
    font-size: 16px;
    margin: 5px 0;
}
QPushButton:hover {
    background-color: #0056b3;
}
"""

search_edit_style = """
    QLineEdit {
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #7f7f7f, stop:1 #F0F2F5);
        border: 0px solid #CCCCCC;
        border-radius: 25px;
        padding: 5px;
        font-family: 'Comic Sans MS', 'KaiTi', sans-serif;
        font-size: 23px;
        font-weight: bold;
        min-width: 100px;
        height: 70px;
        color: #444444;
    }
    /* 已移除 hover 效果 */
    /*
    QLineEdit:hover {
        background-color: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0,
                                          stop:0 #7f7f7f, stop:1 #E8E8E8);
    }
    */
    QLineEdit:focus {
        border: 0px solid #A0A0A0;
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #7f7f7f, stop:1 #E8E8E8);
    }
    QLineEdit::placeholder {
        color: #888888;
        font-size: 18px;
        font-style: italic;
    }
"""

completer_popup_style = """
    QListView {
        font-family: 'Sarasa Gothic', 'Consolas', 'Courier New', sans-serif;
        font-size: 18px;
        padding: 8px;
        min-width: 300px;
        min-height: 250px;
    }
"""



left_widget_style = """
    QWidget {
        background-color: #F0F2F5;
        border-radius: 8px;
    }
""" + scrollbar_style

button_style = """
    QPushButton {
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #F0F2F5, stop:0.5 #7f7f7f, stop:1 #F0F2F5);
        border: 0px solid #BBBBBB;
        border-radius: 20px;
        color: #000000;  /* 更黑亮的文本颜色 */
        font-size: 16px;
        font-weight: bold;
        padding: 12px 25px;
        text-align: center;
        text-decoration: none;
        margin: 4px 2px;
        box-shadow: 3px 3px 5px rgba(0, 0, 0, 0.1);
        transition: background-color 300ms ease-in-out;
    }

    QPushButton:hover {
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                  stop:0 #7f7f7f, stop:0.5 #F0F2F5, stop:1 #7f7f7f);
        border: 0px solid #AAAAAA;
    }

    QPushButton:pressed {
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                  stop:0 #7f7f7f, stop:0.5 #F0F2F5, stop:1 #7f7f7f);
        border: 0px solid #AAAAAA;

    }
"""

hebing_button_style = """
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
        """

# 定义显示区域的样式表

# 夜间模式样式
display_area_style_night = """
    QTextEdit {
        border: 0px solid #555555;
        border-radius: 8px;
        background-color: #000000;
        font-family: 'Sarasa Gothic', 'Consolas', 'Courier New', sans-serif;
        font-size: 14px;
        color: #EEEEEE;
        padding: 10px;
    }
""" + scrollbar_style_night

# 定义 QMessageBox 的样式表
message_box_style_night = """
QMessageBox {
    background-color: #222222;  /* 设置背景颜色为深灰色 */
    color: #EEEEEE;  /* 设置文本颜色 */
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

list_widget_style_night = """
    QListWidget {
        border: 0px solid #555555;
        border-radius: 8px;
        background-color: #000000;
        font-family: 'Comic Sans MS', 'KaiTi', sans-serif;
        font-size: 16px;
        font-weight: bold;
        color: #000000;
    }
    QListWidget::item {
        padding: 12px 10px;
        height: 26px;
    }
    QListWidget::item:hover {
        background-color: #444444;
        border-radius: 8px;
    }
    QListWidget::item:selected {
        background-color: #555555;
        color: #FFFFFF;
        font-weight: bold;
    }
    QListWidget::item:focus {
        outline: none;
    }
    QListWidget:focus {
        outline: none;
    }
""" + scrollbar_style_night

dialog_style_night = """
QDialog {
    background-color: #222222;
    font-family: 'Sarasa Gothic', 'Consolas', 'Courier New', sans-serif;
    border-radius: 15px;
    padding: 30px;
}
QLabel {
    font-size: 20px;
    color: #EEEEEE;
    margin-bottom: 10px;
}
QPushButton {
    background-color: #0078d7;
    color: white;
    padding: 12px 25px;
    border: none;
    border-radius: 10px;
    font-size: 16px;
    margin: 5px 0;
}
QPushButton:hover {
    background-color: #0056b3;
}
"""


search_edit_style_night = """
    QLineEdit {
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #ffffff, stop:1 #000000);
        border: 0px solid #555555;
        border-radius: 25px;
        padding: 5px;
        font-family: 'Comic Sans MS', 'KaiTi', sans-serif;
        font-size: 23px;
        font-weight: bold;
        min-width: 100px;
        height: 70px;
        color: #000000;
    }
    /* 已移除 hover 效果 */
    /*
    QLineEdit:hover {
        background-color: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0,
                                          stop:0 #ffffff, stop:1 #000000);
    }
    */
    QLineEdit:focus {
        border: 0px solid #A0A0A0;
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #ffffff, stop:1 #000000);
    }
    QLineEdit::placeholder {
        color: #AAAAAA;
        font-size: 18px;
        font-style: italic;
    }
"""

completer_popup_style_night = """
    QListView {
        font-family: 'Sarasa Gothic', 'Consolas', 'Courier New', sans-serif;
        font-size: 18px;
        padding: 8px;
        min-width: 300px;
        min-height: 250px;
        background-color: #222222;
        color: #EEEEEE;
    }
"""

main_window_style_night = """
    QMainWindow {
        background-color: #000000;
    }
    QWidget {
        background-color: #F5F7FA;
    }
"""

left_widget_style_night = """
    QWidget {
        background-color: #000000;
        border-radius: 8px;
    }
    QTextEdit {
        border: 1px solid #555555;
        border-radius: 8px;
        background-color: #111111;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        color: #EEEEEE;
        padding: 10px;
    }
""" + scrollbar_style_night

button_style_night = """
    QPushButton {
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #000000, stop:0.5 #ffffff, stop:1 #000000);
        border: 0px solid #555555;
        border-radius: 20px;
        color: #000000;  /* 更亮的文本颜色 */
        font-size: 16px;
        font-weight: bold;
        padding: 12px 25px;
        text-align: center;
        text-decoration: none;
        margin: 4px 2px;
        box-shadow: 3px 3px 5px rgba(0, 0, 0, 0.3);
        transition: background-color 300ms ease-in-out;
    }

    QPushButton:hover {
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #F0F2F5, stop:0.5 #7f7f7f, stop:1 #F0F2F5);
        border: 0px solid #444444;
    }

    QPushButton:pressed {
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #F0F2F5, stop:0.5 #7f7f7f, stop:1 #F0F2F5);
        border: 0px solid #444444;


    }
"""


def ensure_word_file():
    """确保单词表文件可访问"""
    # 1. 尝试从打包资源获取
    word_path = get_resource_path("english_words.txt")
    if os.path.exists(word_path):
        return word_path

    # 2. 尝试从用户目录获取
    user_dir = os.path.join(os.path.expanduser("~"), "Xingyun")
    os.makedirs(user_dir, exist_ok=True)
    user_path = os.path.join(user_dir, "english_words.txt")

    if os.path.exists(user_path):
        return user_path

    # 3. 如果都没有，从程序内复制（如果可能）
    try:
        import pkgutil
        word_data = pkgutil.get_data(__name__, "resources/english_words.txt")
        if word_data:
            with open(user_path, 'wb') as f:
                f.write(word_data)
            return user_path
    except:
        pass

    return None  # 无法获取单词表


def get_resource_path(relative_path):
    """获取资源文件路径（开发/打包环境兼容）
    同时支持单词表、主图标和缓存图标
    """
    is_frozen = getattr(sys, 'frozen', False)

    # 处理图标缓存路径
    if relative_path.startswith("icon_cache/"):
        if is_frozen:
            # 打包环境 - 使用用户目录
            base_dir = os.path.join(os.path.expanduser("~"), "Xingyun")
        else:
            # 开发环境 - 使用项目目录
            base_dir = os.path.dirname(os.path.abspath(__file__))

        cache_dir = os.path.join(base_dir, "icon_cache")
        os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, relative_path[11:])

    # 处理其他资源路径
    if is_frozen:
        # 打包环境优先使用临时解压目录
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        # 开发环境使用项目目录
        base_path = os.path.dirname(os.path.abspath(__file__))

    # 标准化资源路径
    if relative_path.startswith("resources/"):
        relative_path = relative_path[9:]

    full_path = os.path.join(base_path, "resources", relative_path)

    # 后备检查：如果文件不存在，尝试用户目录
    if not os.path.exists(full_path) and is_frozen:
        user_dir = os.path.join(os.path.expanduser("~"), "Xingyun")
        user_path = os.path.join(user_dir, "resources", relative_path)
        if os.path.exists(user_path):
            return user_path

    return full_path


# 用于线程安全的锁
CACHE_LOCK = threading.Lock()
# 图标缓存
ICON_CACHE = {}
# 线程池
ICON_EXECUTOR = ThreadPoolExecutor(max_workers=50)
# 默认图标路径
DEFAULT_ICON_PATH = get_resource_path("imge.png")
# 夜间模式标志

night_mode = False  # Add this line
left_widget = None  # 新增全局变量声明
original_english_btn_style = None  # 已存在
original_night_mode_btn_style = None  # 新增全局变量声明
title_bar = None  # 新增全局变量声明


def get_dynamic_favicon(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # 执行JavaScript获取动态图标
    icons = driver.execute_script("""
        return Array.from(document.querySelectorAll('link[rel*="icon"]'))
            .map(link => link.href);
    """)
    driver.quit()
    return icons


def validate_cache():
    cache_dir = get_resource_path("icon_cache")
    for file in os.listdir(cache_dir):
        path = os.path.join(cache_dir, file)
        try:
            img = QImage(path)
            if img.isNull() or img.width() > 512:
                os.remove(path)
        except:
            os.remove(path)


def get_default_icon():
    """获取默认图标"""
    extract_default_icon()  # 确保默认图标存在
    default_icon = QIcon(DEFAULT_ICON_PATH)
    return default_icon


def extract_default_icon():
    """在打包环境下提取默认图标到本地资源文件夹"""
    if getattr(sys, 'frozen', False):
        # 获取临时解压目录中的资源
        temp_resource_path = os.path.join(sys._MEIPASS, "resources", "imge.png")
        target_path = DEFAULT_ICON_PATH
        if not os.path.exists(target_path) and os.path.exists(temp_resource_path):
            import shutil
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.copy2(temp_resource_path, target_path)
            print(f"默认图标已提取到: {target_path}")


def get_website_favicon(url, callback=None):
    """
    改进版的网站图标获取函数，支持多种图标获取方式
    （原代码结构保持不变，仅添加缓存功能）
    """

    # ---------- 新增缓存功能 ----------
    def get_cache_file(url):
        """获取缓存文件路径"""
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        cache_dir = get_resource_path("icon_cache")
        os.makedirs(cache_dir, exist_ok=True)  # 自动创建目录
        return os.path.join(cache_dir, f"{url_hash}.ico")

    def load_cached_icon(url):
        """从本地缓存加载图标"""
        cache_file = get_cache_file(url)
        if os.path.exists(cache_file):
            try:
                pixmap = QPixmap(cache_file)
                if not pixmap.isNull():
                    icon = QIcon(pixmap)
                    # 更新内存缓存
                    with CACHE_LOCK:
                        ICON_CACHE[url] = icon
                    print(f"Loaded from cache: {cache_file}")
                    return icon
            except Exception as e:
                print(f"Cache read error: {e}")
        return None

    def save_icon_cache(url, icon_data):
        """保存图标到本地缓存"""
        try:
            cache_file = get_cache_file(url)
            with open(cache_file, 'wb') as f:
                f.write(icon_data)
            print(f"Cached icon: {cache_file}")
        except Exception as e:
            print(f"Cache save failed: {e}")

    # ---------- 原始获取逻辑（完全保持不变） ----------
    def normalize_url(url):
        """规范化URL，添加协议等"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return None
            if not parsed.scheme:
                parsed = parsed._replace(scheme='https')
            return parsed.geturl()
        except Exception:
            return None

    def try_multiple_icon_sources(url):
        """尝试从多个可能的来源获取图标（原逻辑不变）"""
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        icon_urls = [
            f"{base_url}/favicon.ico",
            f"{url.rstrip('/')}/favicon.ico",
        ]

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                icon_links = []
                icon_links.extend(soup.find_all('link', rel=lambda x: x and 'icon' in x.lower()))
                icon_links.extend(soup.find_all('link', rel=lambda x: x and 'apple-touch-icon' in x.lower()))
                icon_links.extend(soup.find_all('meta', attrs={'name': 'msapplication-TileImage'}))
                icon_links.extend(soup.find_all('meta', attrs={'property': 'og:image'}))
                icon_links.extend(soup.find_all('meta', attrs={'name': 'twitter:image'}))

                for link in icon_links:
                    href = link.get('href') if link.name == 'link' else link.get('content')
                    if href:
                        if not href.startswith(('http://', 'https://')):
                            href = urljoin(url, href)
                        icon_urls.append(href)
        except Exception:
            pass

        # 第三方服务尝试（原顺序不变）
        domain = parsed.netloc
        icon_urls.extend([
            f"https://www.google.com/s2/favicons?domain={domain}",
            f"https://api.faviconkit.com/{domain}/144",
            f"https://icons.duckduckgo.com/ip2/{domain}.ico",
            f"https://favicons.githubusercontent.com/{domain}"
        ])

        # 尺寸和名称变体（原逻辑不变）
        for size in [16, 32, 64, 128]:
            icon_urls.append(f"{base_url}/favicon-{size}x{size}.png")

        for name in ['favicon', 'icon', 'logo']:
            for ext in ['.ico', '.png', '.jpg', '.jpeg', '.gif']:
                icon_urls.append(f"{base_url}/{name}{ext}")

        for icon_url in icon_urls:
            try:
                response = requests.get(icon_url, headers=headers, timeout=3, stream=True)
                if response.status_code == 200 and 'image' in response.headers.get('Content-Type', '').lower():
                    return response.content
            except Exception:
                continue
        return None

    # ---------- 修改后的主流程 ----------
    def fetch_icon():
        # 1. 检查内存缓存
        with CACHE_LOCK:
            if url in ICON_CACHE:
                return ICON_CACHE[url]

        # 2. 检查本地缓存（新增）
        cached_icon = load_cached_icon(url)
        if cached_icon:
            return cached_icon

        # 3. 执行原始获取逻辑
        normalized_url = normalize_url(url)
        if not normalized_url:
            return get_default_icon()

        icon_data = try_multiple_icon_sources(normalized_url)

        if icon_data:
            # 4. 保存到缓存（新增）
            save_icon_cache(url, icon_data)

            # 创建QIcon（原逻辑）
            pixmap = QPixmap()
            if pixmap.loadFromData(icon_data):
                icon = QIcon(pixmap)
                with CACHE_LOCK:
                    ICON_CACHE[url] = icon
                return icon

        return get_default_icon()

    # ---------- 异步处理保持不变 ----------
    if callback:
        future = ICON_EXECUTOR.submit(fetch_icon)
        future.add_done_callback(lambda f: callback(f.result()))
        return QIcon(DEFAULT_ICON_PATH)
    else:
        return fetch_icon()


def check_local_cache(url):
    """检查本地缓存"""
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    cache_dir = get_resource_path("icon_cache")
    cache_path = os.path.join(cache_dir, f"{url_hash}.ico")

    print(f"检查缓存: {cache_path}")  # 调试输出
    if os.path.exists(cache_path):
        try:
            pixmap = QPixmap(cache_path)
            if not pixmap.isNull():
                icon = QIcon(pixmap)
                with CACHE_LOCK:
                    ICON_CACHE[url] = icon
                print(f"缓存命中: {url} -> {cache_path}")
                return icon
            else:
                print(f"缓存文件无效: {cache_path}")
        except Exception as e:
            print(f"读取缓存失败: {e}")
    else:
        print(f"缓存未找到: {cache_path}")
    return None


def save_icon_to_cache(url, icon_data):
    """将图标保存到本地缓存"""
    try:
        cache_dir = get_resource_path("icon_cache")
        os.makedirs(cache_dir, exist_ok=True)

        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        cache_path = os.path.join(cache_dir, f"{url_hash}.ico")

        with open(cache_path, 'wb') as f:
            f.write(icon_data)
        print(f"图标已保存: {url} -> {cache_path}")
        return cache_path
    except Exception as e:
        print(f"保存图标缓存失败: {e}")
        return None


def normalize_url(url):
    """规范化URL，添加协议等"""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return None

        # 确保有scheme
        if not parsed.scheme:
            parsed = parsed._replace(scheme='https')

        return parsed.geturl()
    except Exception:
        return None


def try_multiple_icon_sources(url):
    """尝试从多个可能的来源获取图标"""
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    # 1. 尝试直接获取favicon.ico
    icon_urls = [
        f"{base_url}/favicon.ico",  # 根目录favicon
        f"{url.rstrip('/')}/favicon.ico",  # 当前路径favicon
    ]

    # 2. 获取网页并解析可能的图标链接
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找所有可能的图标链接
            icon_links = []

            # 标准favicon
            icon_links.extend(soup.find_all('link', rel=lambda x: x and 'icon' in x.lower()))

            # Apple touch图标
            icon_links.extend(soup.find_all('link', rel=lambda x: x and 'apple-touch-icon' in x.lower()))

            # 微软磁贴图标
            icon_links.extend(soup.find_all('meta', attrs={'name': 'msapplication-TileImage'}))

            # Open Graph图像
            icon_links.extend(soup.find_all('meta', attrs={'property': 'og:image'}))

            # Twitter图像
            icon_links.extend(soup.find_all('meta', attrs={'name': 'twitter:image'}))

            # 处理找到的图标链接
            for link in icon_links:
                href = None
                if link.name == 'link':
                    href = link.get('href')
                elif link.name == 'meta':
                    href = link.get('content')

                if href:
                    # 处理相对路径
                    if not href.startswith(('http://', 'https://')):
                        if href.startswith('//'):  # 协议相对URL
                            href = f"{parsed.scheme}:{href}"
                        else:  # 相对路径
                            href = urljoin(url, href)
                    icon_urls.append(href)

    except Exception:
        pass

    # 3. 尝试所有可能的图标URL
    for icon_url in icon_urls:
        try:
            response = requests.get(icon_url, headers=headers, timeout=3, stream=True)
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '').lower()
                if 'image' in content_type:
                    icon_data = response.content
                    if icon_data:
                        return icon_data
        except Exception:
            continue

    return None


def get_file_icon(file_path, callback=None):
    """异步获取文件图标，带缓存功能"""

    def fetch_icon():
        with CACHE_LOCK:
            if file_path in ICON_CACHE:
                return ICON_CACHE[file_path]

        # 检查本地缓存
        file_hash = hashlib.md5(file_path.encode('utf-8')).hexdigest()
        cache_dir = get_resource_path("resources/icon_cache")
        cache_path = os.path.join(cache_dir, f"{file_hash}.ico")

        if os.path.exists(cache_path):
            try:
                pixmap = QPixmap(cache_path)
                if not pixmap.isNull():
                    icon = QIcon(pixmap)
                    with CACHE_LOCK:
                        ICON_CACHE[file_path] = icon
                    return icon
            except Exception:
                pass

        try:
            if platform.system() == "Windows" and os.path.exists(file_path):
                large, small = win32gui.ExtractIconEx(file_path, 0)
                if large:
                    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
                    hbmp = win32ui.CreateBitmap()
                    hbmp.CreateCompatibleBitmap(hdc, 32, 32)
                    hdc = hdc.CreateCompatibleDC()
                    hdc.SelectObject(hbmp)
                    win32gui.DrawIconEx(hdc.GetHandleOutput(), 0, 0, large[0], 32, 32, 0, 0, win32con.DI_NORMAL)
                    win32gui.DestroyIcon(large[0])
                    if small:
                        win32gui.DestroyIcon(small[0])
                    bmp_info = hbmp.GetInfo()
                    bmp_str = hbmp.GetBitmapBits(True)
                    pixmap = QPixmap.fromImage(QtGui.QImage(bmp_str, bmp_info['bmWidth'], bmp_info['bmHeight'],
                                                            QtGui.QImage.Format_ARGB32))
                    # 保存到缓存
                    pixmap.save(cache_path)
                    icon = QIcon(pixmap)
                    if not icon.isNull():
                        with CACHE_LOCK:
                            ICON_CACHE[file_path] = icon
                        return icon
        except Exception as e:
            print(f"获取文件图标失败: {e}")

        # 返回默认图标
        default_icon = QIcon(DEFAULT_ICON_PATH)
        with CACHE_LOCK:
            ICON_CACHE[file_path] = default_icon
        return default_icon

    if callback:
        future = ICON_EXECUTOR.submit(fetch_icon)
        future.add_done_callback(lambda f: callback(f.result()))
        return QIcon(DEFAULT_ICON_PATH)  # 立即返回默认图标
    else:
        return fetch_icon()


def delete_icon_cache(script_data):
    """删除脚本对应的图标缓存文件"""
    try:
        if script_data['type'] == 'url':
            url = script_data['value']
            url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
            cache_dir = get_resource_path("icon_cache")
            cache_path = os.path.join(cache_dir, f"{url_hash}.ico")

            if os.path.exists(cache_path):
                os.remove(cache_path)
                print(f"已删除图标缓存: {cache_path}")
    except Exception as e:
        print(f"删除图标缓存失败: {e}")


# 获取资源文件路径（支持开发和打包环境）


# 异步加载信号
class IconSignals(QObject):
    icon_loaded = pyqtSignal(int, QIcon)


class MyDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if option is None or option.rect is None:
            print("错误：option 或 option.rect 为 None")
            return super().paint(painter, option, index)

        item = index.model().itemFromIndex(index)
        if not item:
            print("错误：item 未找到")
            return super().paint(painter, option, index)

        icon = item.icon()
        if not icon.isNull():
            opt_rect = option.rect
            icon_rect = QRect(opt_rect.left() + 2, opt_rect.top() + (opt_rect.height() - 16) // 2, 16, 16)
            icon.paint(painter, icon_rect, Qt.AlignCenter)
        super().paint(painter, option, index)


def animate_search_edit_height(target_height):
    """
    执行搜索框的动画效果，包括高度、缩放、抖动和透明度变化
    参数:
        target_height: 动画的目标高度（像素）
    """
    # 全局搜索框对象
    global search_edit

    # 停止现有动画并清理
    if hasattr(search_edit, 'animation') and search_edit.animation:
        search_edit.animation.stop()
        search_edit.animation.deleteLater()

    # 判断是放大还是缩小
    is_expanding = target_height > search_edit.height()

    # 1. 高度动画：调整搜索框的最小高度
    height_animation = QPropertyAnimation(search_edit, b"minimumHeight")
    height_animation.setDuration(300)  # 动画持续时间 500 毫秒
    height_animation.setStartValue(search_edit.height())  # 起始高度为当前高度
    height_animation.setEndValue(target_height)  # 目标高度
    # 放大时使用弹性曲线，缩小时使用平滑二次曲线
    height_animation.setEasingCurve(QEasingCurve.OutElastic if is_expanding else QEasingCurve.InOutQuad)

    # 2. 缩放动画：调整搜索框的整体几何形状
    scale_animation = QPropertyAnimation(search_edit, b"geometry")
    scale_animation.setDuration(10)  # 动画持续时间 50 毫秒
    current_geometry = search_edit.geometry()  # 当前几何形状
    scale_factor = 1.0  # 保持宽度不变
    target_width = int(current_geometry.width() * scale_factor)  # 目标宽度
    target_geometry = QRect(
        current_geometry.x() - int((target_width - current_geometry.width()) / 2),  # 水平居中
        current_geometry.y(),  # 保持 Y 坐标不变
        target_width,  # 目标宽度
        target_height  # 目标高度
    )
    scale_animation.setStartValue(current_geometry)  # 起始几何形状
    scale_animation.setEndValue(target_geometry)  # 目标几何形状
    # 放大时使用弹性曲线，缩小时使用平滑二次曲线
    scale_animation.setEasingCurve(QEasingCurve.OutElastic if is_expanding else QEasingCurve.InOutQuad)

    # 3. 抖动动画：模拟轻微左右抖动效果，仅在放大时应用
    shake_animation = QPropertyAnimation(search_edit, b"pos")
    shake_animation.setDuration(50)  # 设置抖动动画持续时间为 600 毫秒
    current_pos = search_edit.pos()  # 当前位置
    shake_animation.setStartValue(current_pos)  # 起始位置
    if is_expanding:
        # 放大时，抖动：向右 4 像素，再向左 4 像素
        shake_animation.setKeyValueAt(0.3, current_pos + QPoint(4, 0))
        shake_animation.setKeyValueAt(0.6, current_pos + QPoint(-4, 0))
        shake_animation.setEasingCurve(QEasingCurve.OutElastic)  # 放大时使用弹性曲线
    else:
        # 缩小时，无抖动，直接保持原位置
        shake_animation.setKeyValueAt(0.5, current_pos)  # 中间点保持原位置
        shake_animation.setEasingCurve(QEasingCurve.InOutQuad)  # 平滑二次曲线
    shake_animation.setEndValue(current_pos)  # 最终回到原位置

    # 4. 透明度动画（调整为更温和）
    opacity_animation = QPropertyAnimation(search_edit, b"windowOpacity")
    opacity_animation.setDuration(50)  # 动画持续时间 50 毫秒
    opacity_animation.setStartValue(1.0)  # 从完全不透明开始
    opacity_animation.setKeyValueAt(0.4, 0.97)  # 更温和的透明度变化
    opacity_animation.setEndValue(1.0)  # 最终恢复完全不透明
    opacity_animation.setEasingCurve(QEasingCurve.InOutQuad)  # 平滑二次缓动曲线

    # 创建并行动画组，组合所有动画
    animation_group = QParallelAnimationGroup()
    animation_group.addAnimation(height_animation)
    animation_group.addAnimation(scale_animation)
    animation_group.addAnimation(shake_animation)
    animation_group.addAnimation(opacity_animation)
    animation_group.start()  # 启动动画

    # 保存动画引用，防止被垃圾回收
    search_edit.animation = animation_group


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


def update_script_path(script_list, script_name, new_path, display_area):
    for script in script_list:
        if script['name'] == script_name:
            old_path = script['value']
            script['value'] = new_path
            save_scripts(script_list)
            return True, old_path
    return False, None


def update_status_bar(widget_name):
    """ 更新状态栏信息 """
    if isinstance(widget_name, str) and widget_name.strip():
        status_bar.setText(f"🔹 {widget_name}")
    else:
        status_bar.setText(">>> 准备就绪 🚀")

def handle_hover_search_edit(obj, event):
    if english_mode:  # 如果处于英语模式，禁止悬浮动画
        return False
    if event.type() == QEvent.Enter:
        # 鼠标进入搜索框区域，执行“略微变高”的泡泡动画
        if hasattr(obj, 'animation') and obj.animation:
            obj.animation.stop()
        animate_search_edit_height(120)  # 比原来小一点的膨胀高度
    elif event.type() == QEvent.Leave:
        # 鼠标离开，恢复原始高度
        if hasattr(obj, 'animation') and obj.animation:
            obj.animation.stop()
        animate_search_edit_height(70)
    return False


from PyQt5.QtGui import QPainterPath


def set_inverted_rounded_corners(widget, radius=5.0, antialiasing_level=2, smoothness=2.0, supersampling=4.0, debug_border=False):
    """
    为窗口设置极平滑的倒圆角效果，使用超采样和边缘渐变消除毛刺。

    参数:
        widget: 要设置倒圆角的控件对象
        radius: 圆角半径（像素，支持浮点数），默认值为20.0
        antialiasing_level: 抗锯齿级别，0（关闭）、1（标准）、2（高质量），默认值为2
        smoothness: 路径平滑度因子（0.5~2.0），值越大越平滑，默认值为1.0
        supersampling: 超采样倍率（1.0~4.0），值越大边缘越平滑但性能开销更高，默认值为1.5
        debug_border: 是否绘制调试边框以验证圆角路径，默认值为False

    注意:
        - supersampling=1.5 适合大多数场景，降低性能开销
        - 在高 DPI 屏幕上，自动调整超采样以优化效果
        - debug_border=True 可显示红色边框以检查圆角效果
    """
    from PyQt5.QtGui import QPainterPath, QRegion, QPainter, QPixmap, QBrush, QLinearGradient, QPen, QColor
    from PyQt5.QtCore import QRectF, Qt
    from PyQt5.QtWidgets import QApplication

    # 获取控件尺寸
    width = widget.width()
    height = widget.height()

    # 根据屏幕 DPI 动态调整超采样倍率
    screen = QApplication.primaryScreen()
    dpi_scale = screen.logicalDotsPerInch() / 96.0  # 标准 DPI 为 96
    adjusted_supersampling = min(max(supersampling * dpi_scale, 1.0), 3.0)  # 限制在 1.0~3.0

    # 计算超采样后的画布尺寸
    render_width = int(width * adjusted_supersampling)
    render_height = int(height * adjusted_supersampling)

    # 创建高分辨率画布
    pixmap = QPixmap(render_width, render_height)
    pixmap.fill(Qt.transparent)

    # 初始化画家
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)
    if antialiasing_level >= 1:
        painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
    if antialiasing_level == 2:
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

    # 缩放画布以匹配超采样
    painter.scale(adjusted_supersampling, adjusted_supersampling)

    # 创建平滑的倒圆角路径
    path = QPainterPath()
    rect = QRectF(0, 0, width, height)
    adjusted_radius = radius * smoothness

    # 使用高精度路径
    path.setFillRule(Qt.WindingFill)
    path.addRoundedRect(rect, adjusted_radius, adjusted_radius)

    # 绘制主填充区域
    painter.setPen(Qt.NoPen)
    painter.setBrush(Qt.black)  # 不透明区域
    painter.drawPath(path)

    # 绘制边缘渐变以软化边界（减少锯齿）
    edge_width = 1.0 / adjusted_supersampling  # 边缘渐变宽度（像素）
    edge_path = QPainterPath()
    edge_rect = QRectF(edge_width / 2, edge_width / 2, width - edge_width, height - edge_width)
    edge_path.addRoundedRect(edge_rect, adjusted_radius, adjusted_radius)

    gradient = QLinearGradient(0, 0, edge_width * 2, 0)
    gradient.setColorAt(0, Qt.transparent)
    gradient.setColorAt(1, Qt.black)
    painter.setBrush(QBrush(gradient))
    painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
    painter.drawPath(edge_path)

    # 调试边框（可选）
    if debug_border:
        painter.setPen(QPen(QColor(Qt.red), 1.0 / adjusted_supersampling))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

    # 结束绘制
    painter.end()

    # 将画布缩放回原始尺寸并生成遮罩
    scaled_pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    region = QRegion(scaled_pixmap.createMaskFromColor(Qt.transparent, Qt.MaskInColor))
    widget.setMask(region)

    # 调试输出
    print(f"倒圆角渲染完成: 尺寸={width}x{height}, 半径={radius}, "
          f"调整后半径={adjusted_radius}, 抗锯齿级别={ antialiasing_level}, "
          f"平滑度={smoothness}, 超采样={adjusted_supersampling}")

def create_main_window():
    global status_bar, list_widget, search_edit, completer_model, display_area
    global create_script_button, remove_selected_button, clear_button, update_log_button
    global english_mode, english_learn_button, original_english_btn_style, night_mode_button
    global left_widget, network_speed_button, speed_test_timer, main_window
    english_mode = False

    main_window = QWidget()
    main_window.setGeometry(100, 100, 1024, 768)
    main_window.setWindowTitle(tr('Xing_yun V1.0(@Rhj_flash)'))

    # --------------------------------------------------------------------------------
    # 修复任务栏无法还原无边框窗口的问题
    # 组合使用多个窗口标志，确保窗口在无边框的同时，拥有正常的任务栏行为
    # Qt.Window: 确保窗口被视为顶级窗口
    # Qt.WindowSystemMenuHint: 允许系统菜单，这对任务栏交互至关重要
    # Qt.WindowMinimizeButtonHint: 明确声明窗口有最小化功能
    # --------------------------------------------------------------------------------
    main_window.setWindowFlags(
        Qt.FramelessWindowHint | Qt.Window | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint)

    main_window.setStyleSheet("""
        QMainWindow, QWidget {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);   
            background-color: #F0F2F5;  /* 背景色 */
            border: none;  /* 移除边框 */
        }
        QSplitter {
            background-color: #F0F2F5;  /* 确保分割器背景一致 */
        }
        QSplitter::handle {
            background-color: #F0F2F5;  /* 分割器手柄背景 */
        }
    """)
    center_window(main_window)
    main_layout = QVBoxLayout()
    main_window.setLayout(main_layout)

    # 设置倒圆角
    set_inverted_rounded_corners(main_window, radius=20, smoothness=2.0, debug_border=True)  # 启用调试边框

    # 重写 resizeEvent 以在窗口大小变化时更新遮罩
    def resizeEvent(event):
        set_inverted_rounded_corners(main_window, radius=10, antialiasing_level=2, smoothness=2.0)
        QWidget.resizeEvent(main_window, event)

    main_window.resizeEvent = resizeEvent

    # 自定义标题栏
    global title_bar
    title_bar = QWidget()
    title_bar.setFixedHeight(30)
    title_bar.setStyleSheet("background-color: #F0F2F5; border-top-left-radius: 15px; border-top-right-radius: 15px;")

    title_bar_layout = QHBoxLayout(title_bar)
    title_bar_layout.setContentsMargins(0, 0, 0, 0)
    title_bar_layout.setSpacing(0)

    title_label = QLabel(tr('Xing_yun_Win10sys(@Rhj_flash) V-1.0'))
    title_label.setStyleSheet("""
        font-family: 'Comic Sans MS', 'KaiTi', sans-serif;
        font-size: 16px;
        font-weight: bold;
        padding-left: 10px;
    """)
    title_bar_layout.addWidget(title_label)
    title_bar_layout.addStretch()

    # ****************** 新增 GitHub 按钮代码 ******************
    # 定义打开 GitHub 链接的函数
    def open_github_link():
        """在默认浏览器中打开 GitHub 仓库链接"""
        webbrowser.open('https://github.com/rhj-flash/XingYun-1.0')

    # 创建 GitHub 按钮
    github_button = QPushButton()
    # 尝试加载图标
    github_icon_path = 'github_icon.ico'  # 假设图标在当前目录下
    if os.path.exists(github_icon_path):
        github_button.setIcon(QIcon(github_icon_path))
    else:
        # 如果找不到文件，使用一个默认图标或文本
        github_button.setText("GitHub")
        github_button.setStyleSheet("""
                QPushButton {
                    font-size: 15px;
                    padding: 0px;
                    text-align: center;
                }
            """)
        # print(f"警告：未找到 GitHub 图标文件: {github_icon_path}") # 调试语句

    github_button.setFixedSize(35, 35)  # 设置固定大小
    github_button.clicked.connect(open_github_link)  # 连接点击事件
    title_bar_layout.addWidget(github_button)  # 将按钮添加到布局中
    # ****************** 新增代码结束 ******************


    # 最小化按钮
    min_button = QPushButton("—")  # 使用标准 Unicode 最小化图标
    min_button.setFixedSize(35, 35)
    min_button.setStyleSheet("""
        QPushButton {
            font-size: 15px;  /* 调整字体大小以优化显示 */
            padding: 0px;     /* 移除内边距，确保居中 */
            text-align: center; /* 强制文本/图标居中 */
        }
    """)
    min_button.clicked.connect(main_window.showMinimized)
    title_bar_layout.addWidget(min_button)

    # 最大化/还原按钮
    max_button = QPushButton("⚁")  # 使用更标准的图标表示
    max_button.setFixedSize(30, 30)
    max_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;  /* 调整字体大小以优化显示 */
                padding: 0px;     /* 移除内边距，确保居中 */
                text-align: center; /* 强制文本/图标居中 */
            }
        """)

    def toggle_maximize():
        if main_window.isMaximized():
            main_window.showNormal()
            max_button.setText("⚁")
        else:
            main_window.showMaximized()
            max_button.setText("🗗")  # 还原图标
    max_button.clicked.connect(toggle_maximize)
    title_bar_layout.addWidget(max_button)

    # 关闭按钮
    close_button = QPushButton("×")  # 使用更标准的图标表示
    close_button.setFixedSize(30, 34)
    close_button.setStyleSheet("""
                QPushButton {
                    font-size: 18px;  /* 调整字体大小以优化显示 */
                    padding: 0px;     /* 移除内边距，确保居中 */
                    text-align: center; /* 强制文本/图标居中 */
                }
            """)
    close_button.clicked.connect(main_window.close)
    title_bar_layout.addWidget(close_button)

    main_layout.addWidget(title_bar)

    # 允许拖动窗口
    main_window.old_pos = None

    def mousePressEvent(event):
        if event.button() == Qt.LeftButton:
            main_window.old_pos = event.globalPos()

    def mouseReleaseEvent(event):
        if event.button() == Qt.LeftButton:
            main_window.old_pos = None

    def mouseMoveEvent(event):
        if not main_window.old_pos: return
        delta = event.globalPos() - main_window.old_pos
        main_window.move(main_window.pos() + delta)
        main_window.old_pos = event.globalPos()

    main_window.mousePressEvent = mousePressEvent
    main_window.mouseReleaseEvent = mouseReleaseEvent
    main_window.mouseMoveEvent = mouseMoveEvent

    # 设置图标
    icon_path = get_resource_path('imge.png')
    if os.path.exists(icon_path):
        main_window.setWindowIcon(QIcon(icon_path))
    else:
        main_window.setWindowIcon(QIcon.fromTheme("application-x-executable"))

    # 添加状态栏
    status_bar = QLabel(tr(">>> 准备就绪🚀"))
    status_bar.setStyleSheet("""
        font-family: 'Sarasa Gothic', 'Consolas', 'Courier New', sans-serif;
        font-size: 12px;
        color: #444444;
        padding: 2px 8px;
        border-top: 1px solid #CCCCCC;
        border-radius: 8px;
    """)



    status_bar.setAlignment(Qt.AlignLeft)
    status_bar.setFixedHeight(30)
    status_bar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # 修改尺寸策略为固定
    status_bar.setMaximumWidth(1800)  # 设置最大宽度，防止过长文本拉伸
    status_bar.setWordWrap(False)  # 禁用自动换行

    # 添加文本截断逻辑
    def truncate_text(text, max_length=100):
        if len(text) > max_length:
            return text[:max_length - 3] + "..."
        return text

    status_bar.setText = lambda text: QLabel.setText(status_bar, truncate_text(text))  # 重写setText方法
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
    # 尝试断开旧连接，避免重复连接导致的问题
    try:
        # 检查是否已经连接，避免重复断开导致TypeError
        if english_learn_button.clicked.disconnect:
            english_learn_button.clicked.disconnect()
    except TypeError:
        # 如果没有连接，则忽略TypeError
        pass
    english_learn_button.clicked.connect(toggle_english_mode)
    english_learn_button.setStyleSheet(original_english_btn_style)
    english_learn_button.setFixedSize(32, 32)

    # 添加夜间模式按钮
    night_mode_button = QPushButton("  🌞  ")
    night_mode_button_style = """
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
            box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.2);
        }
    """
    # 尝试断开旧连接，避免重复连接导致的问题
    try:
        # 检查是否已经连接，避免重复断开导致TypeError
        if night_mode_button.clicked.disconnect:
            night_mode_button.clicked.disconnect()
    except TypeError:
        # 如果没有连接，则忽略TypeError
        pass
    night_mode_button.clicked.connect(toggle_night_mode)
    night_mode_button.setStyleSheet(night_mode_button_style)
    night_mode_button.setFixedSize(32, 32)

    # 网速测试按钮
    network_speed_button = QPushButton("  📡  ")
    network_speed_button.setIconSize(QSize(16, 16))
    original_network_speed_btn_style = """
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
    network_speed_button.setStyleSheet(original_network_speed_btn_style)
    network_speed_button.setFixedSize(32, 32)
    network_speed_button.is_active = False

    speed_test_timer = None
    last_bytes_sent = 0
    last_bytes_recv = 0
    last_time = time.time()
    max_download_speed = 0.0
    min_download_speed = float('inf')
    max_upload_speed = 0.0
    min_upload_speed = float('inf')

    def run_speed_test():
        """实时获取 WiFi 和网络的详细信息，呈现生动、直观的网络状态"""
        global last_bytes_sent, last_bytes_recv, last_time
        global max_download_speed, min_download_speed, max_upload_speed, min_upload_speed

        # 确保全局变量已初始化
        try:
            if 'max_download_speed' not in globals():
                globals()['max_download_speed'] = 0.0
            if 'min_download_speed' not in globals():
                globals()['min_download_speed'] = float('inf')
            if 'max_upload_speed' not in globals():
                globals()['max_upload_speed'] = 0.0
            if 'min_upload_speed' not in globals():
                globals()['min_upload_speed'] = float('inf')
        except Exception as e:
            display_area.clear()
            display_area.append(f"❌ 全局变量初始化失败: {e}")
            update_status_bar("网络测试失败: 变量初始化错误")
            return

        try:
            # 调用 get_wifi_info 获取 WiFi 信息
            from function import get_wifi_info
            wifi_info = get_wifi_info()

            # 检查 get_wifi_info 返回值
            if wifi_info is None or wifi_info == "WiFi信息: 获取失败":
                display_area.clear()
                display_area.append("📡 网络信息获取失败\n⚠️ 无法获取 WiFi 信息，请检查网络连接或管理员权限！")
                update_status_bar("网络测试失败: 无法获取 WiFi 信息")
                return
            if not isinstance(wifi_info, str):
                display_area.clear()
                display_area.append(f"📡 网络信息获取失败\n⚠️ WiFi 信息格式错误: {type(wifi_info)}")
                update_status_bar("网络测试失败: WiFi 信息格式错误")
                return

            # 提取当前 WiFi 的 SSID 和密码等信息
            import re
            current_network_match = re.search(r"当前WiFi名称: (.+?)(?=\n|$)", wifi_info)
            password_match = re.search(r"当前WiFi密码: (.+?)(?=\n|$)", wifi_info)
            network_type_match = re.search(r"网络类型: (.+?)(?=\n|$)", wifi_info)
            auth_match = re.search(r"认证方式: (.+?)(?=\n|$)", wifi_info)
            cipher_match = re.search(r"加密方式: (.+?)(?=\n|$)", wifi_info)

            if not current_network_match:
                display_area.clear()
                display_area.append(
                    f"📡 网络信息获取失败\n⚠️ 无法提取 WiFi 名称，请检查 WiFi 是否连接！\n调试信息: {wifi_info[:100]}...")
                update_status_bar("网络测试失败: 无法提取 WiFi 名称")
                return

            current_network = current_network_match.group(1).strip()
            password = password_match.group(1).strip() if password_match else "未知"
            network_type = network_type_match.group(1).strip() if network_type_match else "未知"
            authentication = auth_match.group(1).strip() if auth_match else "未知"
            encryption = cipher_match.group(1).strip() if cipher_match else "未知"

            # 从 netsh wlan show interfaces 获取 WiFi 详细信息
            import subprocess
            try:
                output = subprocess.check_output(
                    ['netsh', 'wlan', 'show', 'interfaces'],
                    encoding='utf-8',
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    stderr=subprocess.PIPE
                )
            except subprocess.CalledProcessError as e:
                display_area.clear()
                display_area.append(f"📡 网络信息获取失败\n❌ 执行 netsh 命令失败: {e.stderr}")
                update_status_bar("网络测试失败: netsh 命令错误")
                return

            # 提取连接状态
            state_match = re.search(r"State\s*:\s*([^\r\n]+)", output)
            connection_state = state_match.group(1).strip() if state_match else "未连接"

            # 初始化返回值
            actual_download = 0.0
            actual_upload = 0.0
            receive_rate = 0.0
            transmit_rate = 0.0
            signal_strength = 0
            protocol = "未知"
            channel = 0
            frequency = "未知"
            max_bandwidth = 0.0
            channel_width = "未知"
            mac_address = "未知"
            ip_address = "未知"
            gateway = "未知"

            if connection_state.lower() == "connected":
                # 计算实际网速
                import psutil
                import time
                net_io = psutil.net_io_counters()
                bytes_sent = net_io.bytes_sent
                bytes_recv = net_io.bytes_recv
                current_time = time.time()
                time_diff = current_time - last_time if last_time else 0.5
                if time_diff < 0.1:
                    time_diff = 0.5

                actual_download = ((bytes_recv - last_bytes_recv) * 8 / time_diff) / 1_000_000  # Mbps
                actual_upload = ((bytes_sent - last_bytes_sent) * 8 / time_diff) / 1_000_000  # Mbps
                actual_download = max(0, actual_download)
                actual_upload = max(0, actual_upload)

                # 更新上次数据
                last_bytes_sent = bytes_sent
                last_bytes_recv = bytes_recv
                last_time = current_time

                # 提取理论速率
                receive_rate_match = re.search(r"Receive rate\s*:\s*([\d.]+)", output)
                transmit_rate_match = re.search(r"Transmit rate\s*:\s*([\d.]+)", output)
                receive_rate = float(receive_rate_match.group(1)) if receive_rate_match else 0.0
                transmit_rate = float(transmit_rate_match.group(1)) if transmit_rate_match else 0.0

                # 提取信号强度
                signal_match = re.search(r"Signal\s*:\s*(\d+)%", output)
                signal_strength = int(signal_match.group(1)) if signal_match else 0

                # 提取协议
                protocol_match = re.search(r"Radio type\s*:\s*([^\r\n]+)", output)
                protocol = protocol_match.group(1).strip() if protocol_match else "未知"

                # 提取频道
                channel_match = re.search(r"Channel\s*:\s*(\d+)", output)
                channel = int(channel_match.group(1)) if channel_match else 0

                # 提取频率
                frequency = "2.4 GHz" if 1 <= channel <= 14 else "5 GHz" if channel > 14 else "未知"

                # 推算设备最大带宽
                max_bandwidth = 0.0
                if protocol == "802.11n":
                    max_bandwidth = 300.0 if frequency == "5 GHz" else 150.0
                elif protocol == "802.11ac":
                    max_bandwidth = 1300.0 if frequency == "5 GHz" else 600.0
                elif protocol == "802.11ax":
                    max_bandwidth = 2400.0 if frequency == "5 GHz" else 600.0

                # 提取频道宽度
                channel_width_match = re.search(r"Channel Width\s*:\s*([^\r\n]+)", output)
                channel_width = channel_width_match.group(1).strip() if channel_width_match else "未知"

                # 提取MAC地址
                mac_match = re.search(r"Physical address\s*:\s*([^\r\n]+)", output)
                mac_address = mac_match.group(1).strip() if mac_match else "未知"

                # 获取IP地址、网关和DNS
                try:
                    ipconfig_output = subprocess.check_output(
                        ['ipconfig', '/all'],
                        encoding='utf-8',
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        stderr=subprocess.PIPE
                    )
                    ip_match = re.search(r"IPv4 Address.*?:\s*([\d.]+)", ipconfig_output)
                    ip_address = ip_match.group(1).strip() if ip_match else "未知"

                    gateway_match = re.search(r"Default Gateway.*?:\s*([\d.]+)", ipconfig_output)
                    gateway = gateway_match.group(1).strip() if gateway_match else "未知"

                except subprocess.CalledProcessError as e:
                    display_area.append(f"⚠️ 获取 IP 信息失败: {e.stderr}")

                # 更新最大和最小速度
                max_download_speed = max(max_download_speed, actual_download)
                min_download_speed = min(min_download_speed,
                                         actual_download) if actual_download > 0 else min_download_speed
                max_upload_speed = max(max_upload_speed, actual_upload)
                min_upload_speed = min(min_upload_speed, actual_upload) if actual_upload > 0 else min_upload_speed

            # 生成生动的信号强度描述
            signal_description = (

                "📶📶📶" if signal_strength >= 80 else
                "📶📶" if signal_strength >= 50 else
                "📶" if signal_strength >= 20 else
                "🚨 信号微弱，连接可能不稳定！"
            )
            # 更新状态栏显示
            status_text = (
                f"📡 {current_network} | {connection_state} | "
                f"↓ {actual_download:.2f} Mbps | ↑ {actual_upload:.2f} Mbps"
            )
            if len(status_text) > 70:  # 限制状态栏文本长度
                status_text = status_text[:70] + "..."
            update_status_bar(status_text)

            # 显示详细信息到显示区域
            from datetime import datetime
            display_area.clear()
            display_area.append(f"📡🔴网络测试开始 ")
            display_area.append(
                f"   连接到: {current_network} {'✅ 已连接' if connection_state.lower() == 'connected' else '❌ 未连接'}")
            display_area.append(f"   密码🔒: {password}")
            display_area.append(f"   信号强度:  {signal_strength}% {signal_description}")
            display_area.append("————————————————————————————————————————————————————————————————————————————————————————")

            display_area.append("⚡ 网速与性能")
            display_area.append(f"    下载速度: {actual_download:.2f} Mbps ↓")
            display_area.append(f"    上传速度: {actual_upload:.2f} Mbps ↑")
            min_download_display = min_download_speed if min_download_speed != float('inf') else 0
            display_area.append(f"    最大下载速度: {max_download_speed:.2f} Mbps")
            display_area.append(f"    最小下载速度: {min_download_display:.2f} Mbps")
            min_upload_display = min_upload_speed if min_upload_speed != float('inf') else 0
            display_area.append(f"    最大上传速度: {max_upload_speed:.2f} Mbps")
            display_area.append(f"    最小上传速度: {min_upload_display:.2f} Mbps")
            display_area.append(f"    理论下载速率: {receive_rate:.1f} Mbps")
            display_area.append(f"    理论上传速率: {transmit_rate:.1f} Mbps")
            display_area.append("————————————————————————————————————————————————————————————————————————————————————————")

            display_area.append("🔧 网络技术细节")
            display_area.append(f"    网络类型: {network_type}")
            display_area.append(f"    协议: {protocol}")
            display_area.append(f"    频率: {frequency}")
            display_area.append(f"    信道: {channel}")
            display_area.append(f"    最大带宽: {max_bandwidth:.1f} Mbps")
            display_area.append(f"    信道宽度: {channel_width}")
            display_area.append(f"    认证方式: {authentication}")
            display_area.append(f"    加密方式: {encryption}")
            display_area.append("————————————————————————————————————————————————————————————————————————————————————————")

            display_area.append("🌍 连接信息")
            display_area.append(f"    MAC地址: {mac_address}")
            display_area.append(f"    IP地址: {ip_address}")
            display_area.append(f"    网关: {gateway}")




        except Exception as e:
            display_area.clear()
            display_area.append(f"📡 网络信息获取失败\n⚠️ 错误: {str(e)}")
            update_status_bar("网络测试失败: 获取信息出错")

    def update_speed_display():
        """实时更新网络和 WiFi 信息显示（中文）"""
        try:
            actual_download, actual_upload, receive_rate, transmit_rate, network_name, signal_strength, protocol, channel, frequency, max_bandwidth, encryption, channel_width, mac_address, ip_address, gateway, dns_servers, connection_state, error = run_speed_test()
            if error is None:
                speed_text = (
                    f"\n"
                    f"\n"
                    f"\n"
                    f"📶 WiFi 名称：{network_name}\n"
                    f"🔗 连接状态：{connection_state}\n"
                    f"📥 实际下载速度：{actual_download:.2f} Mbps\n"
                    f"📤 实际上传速度：{actual_upload:.2f} Mbps\n"
                    f"📊 理论最大下载速度：{receive_rate:.2f} Mbps\n"
                    f"📈 理论最大上传速度：{transmit_rate:.2f} Mbps\n"
                    f"📡 信号强度：{signal_strength}% {'📶' * (signal_strength // 25)}\n"
                    f"🌐 WiFi 协议：{protocol}\n"
                    f"🔢 频道：{channel} ({frequency})\n"
                    f"📏 信道宽度：{channel_width}\n"
                    f"⚡ 设备最大带宽：{max_bandwidth:.2f} Mbps\n"
                    f"🔒 加密类型：{encryption}\n"
                    f"📌 MAC 地址：{mac_address}\n"
                    f"🌍 IP 地址：{ip_address}\n"
                    f"🚪 网关地址：{gateway}\n"
                    f"🔍 DNS 服务器：{dns_servers}\n"
                    f"⏰ 更新时间：{QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss')}\n"
                    f"\n"
                    f"\n"
                    f"\n"
                )
                # 清空显示区域，防止日志堆积
                display_area.clear()
                appendLogWithEffect(display_area, speed_text)
            else:
                appendLogWithEffect(display_area, f"{error}\n")
        except Exception as e:
            appendLogWithEffect(display_area, f"\n")

    def toggle_network_speed():
        """切换网速测试状态，支持实时刷新"""
        global speed_test_timer, last_bytes_sent, last_bytes_recv, last_time
        try:
            network_speed_button.is_active = not network_speed_button.is_active

            # 需要保留启用状态的控件
            allowed_widgets = {
                network_speed_button,
                display_area,
            }

            # 禁用其他控件（仅禁用 QPushButton 和 QLineEdit 等用户交互控件）
            for widget in main_window.findChildren(QWidget):
                if isinstance(widget,
                              (QPushButton, QLineEdit, QTextEdit, QListWidget)) and widget not in allowed_widgets:
                    widget.setEnabled(not network_speed_button.is_active)

            if network_speed_button.is_active:
                # 使用统一的红色动画样式（模仿英语按钮样式）
                network_speed_button.setStyleSheet("background-color: red; color: white; border-radius: 8px;")

                # 删除动画代码部分

                net_io = psutil.net_io_counters()
                last_bytes_sent = net_io.bytes_sent
                last_bytes_recv = net_io.bytes_recv
                last_time = time.time()
                if speed_test_timer is None:
                    speed_test_timer = QTimer()
                    speed_test_timer.timeout.connect(update_speed_display)
                speed_test_timer.start(500)
                update_speed_display()
            else:
                network_speed_button.setStyleSheet(original_english_btn_style)

                # 恢复控件启用（仅启用交互控件）
                for widget in main_window.findChildren(QWidget):
                    if isinstance(widget, (QPushButton, QLineEdit, QTextEdit, QListWidget)):
                        widget.setEnabled(True)
                clear_display(display_area)
                appendLogWithEffect(display_area, "🟢 网络测试已停止\n")
                if speed_test_timer is not None:
                    speed_test_timer.stop()

        except Exception as e:
            appendLogWithEffect(display_area, f"⚠️ 切换网络测试状态失败：{str(e)}\n")

    # 确保信号连接
    try:
        if network_speed_button.clicked.disconnect:
            network_speed_button.clicked.disconnect()
    except TypeError:
        pass
    network_speed_button.clicked.connect(toggle_network_speed)
    network_speed_button.enterEvent = lambda event: update_status_bar("网速测试")


    # 状态栏容器
    status_container = QWidget()
    status_layout = QHBoxLayout(status_container)
    status_layout.addWidget(status_bar)
    status_layout.addWidget(night_mode_button)
    status_layout.addWidget(english_learn_button)
    status_layout.addWidget(network_speed_button)
    status_layout.setContentsMargins(0, 0, 0, 0)
    status_layout.setSpacing(5)
    status_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    status_container.setFixedHeight(30)
    main_layout.addWidget(status_container)

    # 列表控件
    list_widget = SmoothListWidget(status_bar)
    list_widget.setStyleSheet(list_widget_style)
    list_widget.itemClicked.connect(on_list_item_clicked)
    list_widget.itemDoubleClicked.connect(lambda item: execute_script(item, display_area))
    list_widget.setDragDropMode(QListWidget.InternalMove)
    list_widget.model().rowsMoved.connect(update_item_colors)
    list_widget.setDefaultDropAction(Qt.MoveAction)
    list_widget.setSelectionMode(QListWidget.SingleSelection)
    list_widget.setAcceptDrops(True)
    list_widget.model().rowsMoved.connect(save_list_order)

    # 搜索框
    search_edit = QLineEdit()
    search_edit.setPlaceholderText(tr('👁‍🗨search'))
    search_edit.setStyleSheet(search_edit_style)
    completer_items = []
    completer_model = QStringListModel(completer_items)
    completer = QCompleter(completer_model)
    completer.setFilterMode(Qt.MatchContains)
    completer.setCaseSensitivity(Qt.CaseInsensitive)
    search_edit.installEventFilter(main_window)  # 安装事件过滤器
    main_window.eventFilter = lambda obj, event: handle_hover_search_edit(obj, event) if obj == search_edit else False

    search_edit.textChanged.connect(lambda text: filter_list_widget(list_widget, text))

    # 左侧布局
    left_layout = QVBoxLayout()
    left_layout.addWidget(search_edit)
    left_layout.addWidget(list_widget)
    left_widget = QWidget()
    left_widget.setLayout(left_layout)
    left_widget.setStyleSheet(left_widget_style)

    # 显示区域
    display_area = QTextEdit()
    display_area.setReadOnly(True)
    display_area.setStyleSheet(display_area_style)

    # 按钮布局
    button_layout = QHBoxLayout()
    create_script_button = create_button("🌟 创建脚本", main_window,
                                         lambda: show_create_script_dialog(main_window, list_widget, display_area,
                                                                           completer_model))
    remove_selected_button = create_button("🗑️ 删除脚本", main_window,
                                           lambda: remove_script(list_widget, display_area, completer_model))
    clear_button = create_button("🧹️ 清除屏幕", main_window, lambda: clear_display(display_area))
    update_log_button = create_button("📜 设备信息", main_window,
                                      lambda: update_log_with_effect(display_area))

    create_script_button.enterEvent = lambda event: update_status_bar("🌟 创建脚本")
    remove_selected_button.enterEvent = lambda event: update_status_bar("🗑️ 删除脚本")
    clear_button.enterEvent = lambda event: update_status_bar("🧹️ 清除日志")
    update_log_button.enterEvent = lambda event: update_status_bar("📜 查看日志 / 设备信息")
    search_edit.enterEvent = lambda event: update_status_bar("🔍 搜索框")
    english_learn_button.enterEvent = lambda event: update_status_bar("💃 English_learn")
    night_mode_button.enterEvent = lambda event: update_status_bar("夜间/日间")

    button_layout.addStretch()
    button_layout.addWidget(create_script_button)
    button_layout.addWidget(remove_selected_button)
    button_layout.addWidget(clear_button)
    button_layout.addWidget(update_log_button)
    button_layout.addStretch()

    # 分割器
    splitter = QSplitter(Qt.Horizontal)
    splitter.addWidget(left_widget)
    splitter.addWidget(display_area)
    main_layout.addWidget(splitter)
    main_layout.addLayout(button_layout)

    splitter.setSizes([main_window.width() // 6, main_window.width() * 3 // 6])

    # 将状态栏容器添加到主布局的底部
    main_layout.addWidget(status_container)

    # 加载脚本
    scripts = load_scripts()
    for index, script in enumerate(scripts):
        item = QListWidgetItem(script['name'])
        item.setData(Qt.UserRole, script)
        item.setIcon(QIcon(DEFAULT_ICON_PATH))
        if index % 2 == 0:
            item.setBackground(QColor("#F0F0F0"))
        else:
            item.setBackground(QColor("#D9D9D9"))
        list_widget.addItem(item)
        completer_model.insertRow(0)
        completer_model.setData(completer_model.index(0), script['name'])
        if script['type'] == 'url':
            get_website_favicon(script['value'], lambda icon, i=index: list_widget.item(i).setIcon(icon))
        elif script['type'] == 'file':
            get_file_icon(script['value'], lambda icon, i=index: list_widget.item(i).setIcon(icon))

    # 设置右键菜单
    setup_context_menu(list_widget, display_area)
    # 显示欢迎界面功能
    display_welcome_screen(display_area)
    update_item_colors()
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

        # 新增：清空搜索框内容
        search_edit.clear()
        animate_search_edit_height(250)
        appendLogWithEffect(display_area, """🔴已开启单词查询模式  (键入单词查询)
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

        # 新增：清空搜索框内容
        search_edit.clear()

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


def toggle_night_mode():
    global night_mode, main_window, english_learn_button, night_mode_button, status_bar, title_bar, title_bar
    global list_widget, search_edit, display_area, create_script_button, remove_selected_button, clear_button, update_log_button
    global original_english_btn_style, left_widget, display_area_style_night
    global list_widget_style_night, search_edit_style_night, left_widget_style_night, button_style_night

    # 定义夜间模式按钮的默认样式
    night_mode_button_style = """
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
            box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.2);
        }
    """

    if not night_mode:
        night_mode = True
        # 保存当前搜索框的高度
        search_height = search_edit.height()

        # 设置夜间模式主窗口样式，确保覆盖所有部件

        main_window.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #000000;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                color: #FFFFFF;
                border-top-left-radius: 15px; /* 左上角圆角 */
                border-top-right-radius: 15px; /* 右上角圆角 */
                border-bottom-left-radius: 15px; /* 左下角圆角 */
                border-bottom-right-radius: 15px; /* 右下角圆角 */
            }
            QSplitter {
                background-color: #000000;  /* 分割器背景 */
            }
            QSplitter::handle {
                background-color: #000000;  /* 分割器手柄背景 */
            }
            QMessageBox {
                background-color: #222222;
                color: #FFFFFF;
                border: 2px solid #0078d7;
                border-radius: 15px;
                padding: 20px;
            }
            QMessageBox QLabel {
                font-size: 16px;
                margin: 10px;
                color: #FFFFFF;
            }
            QMessageBox QPushButton {
                background-color: #0078d7;
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                margin: 5px 10px;
            }
            QMessageBox QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        list_widget.setStyleSheet(list_widget_style_night)
        search_edit.setStyleSheet(search_edit_style_night)
        display_area.setStyleSheet(display_area_style_night)
        left_widget.setStyleSheet(left_widget_style_night)
        create_script_button.setStyleSheet(button_style_night)
        remove_selected_button.setStyleSheet(button_style_night)
        clear_button.setStyleSheet(button_style_night)
        update_log_button.setStyleSheet(button_style_night)
        night_mode_button.setText("  🌜  ")  # 切换为月亮图标
        status_bar.setStyleSheet("""
            font-size: 12px;
            color: #EEEEEE;
            padding: 2px 8px;
            border-radius: 8px;
            border-top: 1px solid #555555;
            background-color: #000000;  /* 与夜间模式主窗口一致 */
            font-family: 'Sarasa Gothic', 'Consolas', 'Courier New', sans-serif;
        """)
        title_bar.setStyleSheet("background-color: #000000; border-top-left-radius: 15px; border-top-right-radius: 15px;")
    else:
        night_mode = False
        main_window.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #F0F2F5;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                border-top-left-radius: 15px; /* 左上角圆角 */
                border-top-right-radius: 15px; /* 右上角圆角 */
                border-bottom-left-radius: 15px; /* 左下角圆角 */
                border-bottom-right-radius: 15px; /* 右下角圆角 */
            }
            QSplitter {
                background-color: #F0F2F5;  /* 确保分割器背景一致 */
            }
            QSplitter::handle {
                background-color: #F0F2F5;  /* 分割器手柄背景 */
            }
        """)
        title_bar.setStyleSheet("background-color: #F0F2F5; border-top-left-radius: 15px; border-top-right-radius: 15px;")
        list_widget.setStyleSheet(list_widget_style)
        search_edit.setStyleSheet(search_edit_style)
        display_area.setStyleSheet(display_area_style)
        left_widget.setStyleSheet(left_widget_style)
        create_script_button.setStyleSheet(button_style)
        remove_selected_button.setStyleSheet(button_style)
        clear_button.setStyleSheet(button_style)
        update_log_button.setStyleSheet(button_style)
        night_mode_button.setText("  🌞  ")  # 切换回太阳图标
        status_bar.setStyleSheet("""
            font-size: 12px;
            color: #444444;
            padding: 2px 8px;
            border-radius: 8px;
            border-top: 1px solid #CCCCCC;
            background-color: #F0F2F5;  /* 与日间模式主窗口一致 */
        """)
        title_bar.setStyleSheet("background-color: #F0F2F5; border-top-left-radius: 15px; border-top-right-radius: 15px;")



        # 恢复窗口标题栏颜色（仅适用于 Windows）
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    int(main_window.winId()),
                    20,  # DWMWA_CAPTION_COLOR
                    ctypes.byref(ctypes.c_int(-1)),  # 恢复默认
                    ctypes.sizeof(ctypes.c_int)
                )
            except Exception as e:
                print(f"恢复标题栏颜色失败: {e}")

    night_mode_button.setStyleSheet(night_mode_button_style)


def query_local_dictionary(word, top_n=5):
    """
    模糊查询单词，支持：
    - 输入英文或汉语，返回最接近的 top_n 个结果（英文和汉语对）
    - 始终进行模糊匹配，按相似度排序
    - 优化短输入（单字或短词）匹配
    """
    word = word.strip()
    matches = []

    # **模糊匹配**
    # 英文模糊匹配
    for eng_word in all_words:
        similarity = difflib.SequenceMatcher(None, word.lower(), eng_word).ratio()
        if similarity > 0.2:  # 降低阈值以捕获短输入
            matches.append((similarity, eng_word, word_to_translation[eng_word]))

    # 汉语模糊匹配
    for trans, eng_word in translation_to_word.items():
        # 对于短输入，优先检查是否为翻译的子串
        if len(word) <= 2:  # 单字或双字输入
            if word in trans:  # 子串匹配
                matches.append((1.0, eng_word, trans))  # 高相似度
            else:
                similarity = difflib.SequenceMatcher(None, word, trans).ratio()
                if similarity > 0.2:
                    matches.append((similarity, eng_word, trans))
        else:
            similarity = difflib.SequenceMatcher(None, word, trans).ratio()
            if similarity > 0.2:
                matches.append((similarity, eng_word, trans))

    # 按相似度排序
    matches.sort(reverse=True, key=lambda x: x[0])

    # 返回 top_n 个结果
    if matches:
        return [{"word": eng, "translation": trans} for _, eng, trans in matches[:top_n]]
    return []

def query_and_display_result(word, result_label):
    """ 查询单词并显示最接近的多个模糊匹配结果，适合实时预显示 """
    if not word.strip():  # 空输入不显示结果
        result_label.setText("")
        return
    results = query_local_dictionary(word)
    if results:
        # 构建显示文本，列出所有匹配结果
        display_text = "🔍 预测结果:\n"
        for i, result in enumerate(results, 1):
            display_text += f"{i}. 英文: {result['word']} | 汉语: {result['translation']}\n"
        result_label.setText(display_text.strip())
    else:
        result_label.setText(f"⚠️ 无与 '{word}' 相关的预测结果")

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
                    line = f"<span style=' font-weight: bold;'>🔤 {item['word']} | 📖 {item['translation']}</span>"
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
    visible_count = 0  # 记录可见项的数量

    # 第一步：标记所有项的可见性
    for i in range(list_widget.count()):
        item = list_widget.item(i)
        is_match = text.lower() in item.text().lower()
        item.setHidden(not is_match)
        if is_match:
            visible_count += 1

    # 第二步：只为可见项重新设置交替颜色
    visible_index = 0
    for i in range(list_widget.count()):
        item = list_widget.item(i)
        if not item.isHidden():
            if visible_index % 2 == 0:
                item.setBackground(QColor("#F5F5F5"))  # 偶数行 - 浅色
            else:
                item.setBackground(QColor("#E8E8E8"))  # 奇数行 - 深色
            visible_index += 1

    # 强制刷新列表显示
    list_widget.viewport().update()


def remove_script(list_widget, display_area, completer_model):
    try:
        selected_items = list_widget.selectedItems()
        if selected_items:
            for item in selected_items:
                script_name = item.text()
                script_data = item.data(Qt.UserRole)

                # 删除图标缓存
                delete_icon_cache(script_data)

                list_widget.takeItem(list_widget.row(item))
                completer_items = completer_model.stringList()
                completer_items.remove(script_name)
                completer_model.setStringList(completer_items)
                save_current_scripts()
                update_item_colors()
                appendLogWithEffect(display_area,
                                    f"脚本 '{script_name}' 已删除！\n")
        else:
            custom_message_box_style = """
                QMessageBox {
                    background-color: #ffffff;
                    color: #333333;
                    border-radius: 15px;
                    padding: 20px;
                }
                QMessageBox QLabel {
                    font-size: 16px;
                    margin: 10px;
                }
                QMessageBox QPushButton {
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                                      stop:0 rgba(180, 180, 180, 1), stop:1 rgba(140, 140, 140, 1));
                    border: 1px solid #BBBBBB;
                    border-radius: 8px;
                    color: #000000;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 12px 25px;
                    margin: 5px 10px;
                    box-shadow: 3px 3px 5px rgba(0, 0, 0, 0.1);
                }
                QMessageBox QPushButton:hover {
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                                      stop:0 rgba(140, 140, 140, 1), stop:1 rgba(100, 100, 100, 1));
                    border: 1px solid #AAAAAA;
                }
                QMessageBox QPushButton:pressed {
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                                      stop:0 rgba(100, 100, 100, 1), stop:1 rgba(80, 80, 80, 1));
                    border: 1px solid #999999;
                    box-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
                }
            """
            msg_box = create_styled_message_box(
                QMessageBox.Warning, tr('警告'), tr('请选择要删除的脚本项'), custom_message_box_style
            )
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.exec_()
    except Exception as e:
        appendLogWithEffect(display_area, f"Error removing script: {e}\n")
        msg_box = create_styled_message_box(
            QMessageBox.Critical, tr('错误'), f"{tr('删除脚本时发生错误')}: {e}", message_box_style
        )
        msg_box.exec_()


def create_styled_message_box(type, title, text, style):
    msg_box = QMessageBox(type, title, text)
    icon_path = get_resource_path('imge.png')
    if not os.path.exists(icon_path):
        icon_path = "imge.png"
    msg_box.setWindowIcon(QIcon(icon_path))
    msg_box.setStyleSheet(style)
    return msg_box


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
            "\n〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰当前设备基本信息抓取〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰〰\n"
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
           █████   █████  ██████████  █████        █████           ███████   
          ░░███   ░░███  ░░███░░░░░█ ░░███        ░░███          ███░░░░░███ 
           ░███    ░███   ░███  █ ░   ░███         ░███         ███     ░░███
           ░███████████   ░██████     ░███         ░███        ░███      ░███
           ░███░░░░░███   ░███░░█     ░███         ░███        ░███      ░███
           ░███    ░███   ░███ ░   █  ░███      █  ░███      █ ░░███     ███ 
           █████   █████  ██████████  ███████████  ███████████  ░░░███████░  
           ░░░░░   ░░░░░  ░░░░░░░░░░  ░░░░░░░░░░░  ░░░░░░░░░░░     ░░░░░░░                    
██   ██ ██ ███    ██  ██████  ██    ██ ██    ██ ███    ██         ██    ██  ██     ██████  
 ██ ██  ██ ████   ██ ██        ██  ██  ██    ██ ████   ██         ██    ██ ███    ██  ████ 
  ███   ██ ██ ██  ██ ██   ███   ████   ██    ██ ██ ██  ██         ██    ██  ██    ██ ██ ██ 
 ██ ██  ██ ██  ██ ██ ██    ██    ██    ██    ██ ██  ██ ██          ██  ██   ██    ████  ██ 
██   ██ ██ ██   ████  ██████     ██     ██████  ██   ████ ███████   ████    ██ ██  ██████  
                                                                                           
                                                                                            
            
欢迎使用本软件！
    使用说明：
    1. 创建软件脚本：创建一个打开软件的脚本,需要用户自定义脚本名称以及选择打开软件的绝对路径,双击使用.
    2. 创建网页脚本：创建一个打开网页的脚本,需要用户键入网址和脚本名称(右键脚本可修改名称/地址).
    3. 拖拽脚本可以调整排序位置,鼠标放置于脚本上方可查看当前脚本的网址/绝对路径.
    4. 设备信息：获取当前设备基础信息(部分功能需要开启管理员权限).
    5. 网页脚本：🌐 Google | 🔗https://www.google.com
       软件脚本：🖥️ Photoshop | 📂C:/Program Files/Adobe/Photoshop.exe
    6. 🔴 英语查询模式下其它功能禁用 
    7.Github开源地址：|  https://github.com/rhj-flash/XingYun-1.0
使用愉快！
                                                                            Rhj_flash
—————————————————————————————————————————————————————————————————————————————————————————
加载完毕...
"""

    appendLogWithEffect(display_area, welcome_message, include_timestamp=False)


def get_user_input_file(parent):
    """获取用户输入的软件路径和脚本名称（与主窗口风格一致）"""
    dialog = QDialog(parent)
    dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
    dialog.setWindowTitle("创建软件脚本")
    dialog.setFixedSize(420, 300)
    dialog.setStyleSheet("""
        QWidget {
            background-color: #F5F7FA;
            border-radius: 12px;
        }
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
    button_layout.setSpacing(50)

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
    layout.setSpacing(50)

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
    button_layout.setSpacing(50)

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
        QWidget {
            background-color: #F5F7FA;
            border-radius: 12px;
        }
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
    main_layout.setSpacing(50)

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
    button_layout.setSpacing(50)

    return_button = QPushButton("◀ 返回")
    ok_button = QPushButton("✔ 确定")
    ok_button.setCursor(Qt.PointingHandCursor)

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


class RenameScriptDialog(QDialog):
    def __init__(self, parent=None, old_name=""):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(tr("重命名脚本"))
        self.setFixedSize(400, 200)
        self.old_name = old_name
        self.init_ui()

        # 设置窗口图标
        icon_path = get_resource_path('imge.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 提示标签
        label = QLabel(tr("请输入新的脚本名称:"))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # 输入框
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.old_name)
        self.name_edit.setPlaceholderText(tr("请输入新名称"))
        self.name_edit.setMinimumWidth(300)
        layout.addWidget(self.name_edit)

        # 按钮区域
        button_layout = QHBoxLayout()
        ok_button = QPushButton(tr("✔ 确定"))
        cancel_button = QPushButton(tr("✖ 取消"))
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # 应用样式
        self.setStyleSheet("""
                QDialog {
                    background-color: #F5F7FA;
                    border-radius: 12px;
                    border: 1px solid #D0D0D0;
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

    def get_new_name(self):
        return self.name_edit.text().strip()


class ModifyPathDialog(QDialog):
    def __init__(self, parent=None, script_type="", current_path=""):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.script_type = script_type
        self.current_path = current_path
        self.setWindowTitle(tr("修改路径") if script_type == 'file' else tr("修改网址"))
        self.setFixedSize(500, 250)
        self.init_ui()

        # 设置窗口图标
        icon_path = get_resource_path('imge.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 提示标签
        label_text = tr("请输入新的文件路径:") if self.script_type == 'file' else tr("请输入新的网址:")
        label = QLabel(label_text)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # 输入框
        self.path_edit = QLineEdit()
        self.path_edit.setText(self.current_path)
        self.path_edit.setPlaceholderText(tr("选择文件路径") if self.script_type == 'file' else tr("输入网址"))
        self.path_edit.setMinimumWidth(400)
        layout.addWidget(self.path_edit)

        # 文件选择按钮（仅文件类型）
        if self.script_type == 'file':
            browse_button = QPushButton(tr("📂 浏览"))
            browse_button.clicked.connect(self.browse_file)
            layout.addWidget(browse_button, alignment=Qt.AlignCenter)

        # 按钮区域
        button_layout = QHBoxLayout()
        ok_button = QPushButton(tr("✔ 确定"))
        cancel_button = QPushButton(tr("✖ 取消"))
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # 应用样式
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
                }
                QLineEdit {
                    border: 1px solid #BBBBBB;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 14px;
                    background-color: #FFFFFF;
                    min-height: 36px;
                }
                QLineEdit:focus {
                    border: 1px solid #BBBBBB;
                    box-shadow: 0 0 4px rgba(187, 187, 187, 0.5);
                }
                QPushButton {
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                                    stop:0 rgba(180, 180, 180, 1), stop:1 rgba(140, 140, 140, 1));
                    border: 1px solid #BBBBBB;
                    border-radius: 8px;
                    color: #000000;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 10px 20px;
                    min-width: 100px;
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
                }
            """)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, tr("选择文件"), os.path.dirname(self.current_path), tr("所有文件 (*)")
        )
        if file_path:
            self.path_edit.setText(file_path)

    def get_new_path(self):
        return self.path_edit.text().strip()


class MergeScriptNameDialog(QDialog):
    """自定义合并脚本命名对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.list_widget = list_widget  # 保存对 QListWidget 的引用
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("命名合并脚本")
        self.setFixedSize(500, 300)
        self.setStyleSheet(hebing_button_style)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)  # 增加左右边距
        layout.setSpacing(50)

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
        button_layout.setSpacing(50)

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
    """设置 QListWidget 的右键菜单"""
    list_widget.setContextMenuPolicy(Qt.CustomContextMenu)

    def context_menu_requested(pos):
        item = list_widget.itemAt(pos)
        if not item:
            return

        script_list = load_scripts()
        selected_item = item

        # 创建右键菜单
        menu = QMenu(list_widget)
        menu.setStyleSheet("""
            QMenu {
                background-color: #F5F7FA;
                border: 1px solid #D0D0D0;
                border-radius: 12px;
                padding: 5px;
                color: #000000;
                font-size: 14px;
            }
            QMenu::item {
                padding: 8px 20px;
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                                stop:0 rgba(140, 140, 140, 1), 
                                                stop:1 rgba(100, 100, 100, 1));
                color: #FFFFFF;
                border-radius: 8px;
            }
        """)

        # 添加菜单项
        execute_action = menu.addAction(tr("执行脚本"))
        modify_name_action = menu.addAction(tr("重命名"))
        modify_path_action = menu.addAction(tr("修改路径"))
        reload_icon_action = menu.addAction(tr("重新加载图标"))

        # 显示菜单并获取用户选择
        action = menu.exec_(list_widget.mapToGlobal(pos))
        if action == execute_action:
            execute_script(selected_item, display_area)

        elif action == modify_name_action:
            old_name = selected_item.text()
            dialog = RenameScriptDialog(list_widget, old_name)
            if dialog.exec_():
                new_name = dialog.get_new_name()
                if new_name and new_name != old_name:
                    script_data = next((s for s in script_list if s['name'] == old_name), None)
                    if script_data:
                        script_data['name'] = new_name
                        selected_item.setText(new_name)
                        save_current_scripts()
                        appendLogWithEffect(display_area, f"脚本 '{old_name}' 已重命名为 '{new_name}'\n")
                        QMessageBox.information(None, tr("成功"), tr("脚本名称已更新"))

        elif action == modify_path_action:
            script_name = selected_item.text()
            script_data = next((s for s in script_list if s['name'] == script_name), None)
            if not script_data:
                return

            script_type = script_data.get('type')
            current_path = script_data.get('value', '')

            if script_type == 'url':
                dialog = ModifyPathDialog(list_widget, 'url', current_path)
                if dialog.exec_():
                    new_url = dialog.get_new_path()
                    if new_url:
                        success, old_path = update_script_path(script_list, script_name, new_url, display_area)
                        if success:
                            script_data['value'] = new_url
                            selected_item.setData(Qt.UserRole, script_data)
                            selected_item.setIcon(QIcon(DEFAULT_ICON_PATH))
                            get_website_favicon(new_url, lambda icon: selected_item.setIcon(icon))
                            appendLogWithEffect(display_area,
                                                f"脚本 '{script_name}' 网址已修改: {old_path} -> {new_url}\n")
                            QMessageBox.information(None, tr("成功"), tr("网址已更新"))
                        else:
                            appendLogWithEffect(display_area, f"更新脚本 '{script_name}' 网址失败\n")

            elif script_type == 'file':
                dialog = ModifyPathDialog(list_widget, 'file', current_path)
                if dialog.exec_():
                    new_path = dialog.get_new_path()
                    if new_path:
                        success, old_path = update_script_path(script_list, script_name, new_path, display_area)
                        if success:
                            script_data['value'] = new_path
                            selected_item.setData(Qt.UserRole, script_data)
                            selected_item.setIcon(QIcon(DEFAULT_ICON_PATH))
                            get_file_icon(new_path, lambda icon: selected_item.setIcon(icon))
                            appendLogWithEffect(display_area,
                                                f"脚本 '{script_name}' 路径已修改: {old_path} -> {new_path}\n")
                            QMessageBox.information(None, tr("成功"), tr("路径已更新"))
                        else:
                            appendLogWithEffect(display_area, f"更新脚本 '{script_name}' 路径失败\n")

            elif script_type == 'merge':
                dialog = ModifyPathDialog(list_widget, 'merge', current_path)
                if dialog.exec_():
                    new_scripts = dialog.get_new_path()
                    if new_scripts:
                        success, old_path = update_script_path(script_list, script_name, new_scripts, display_area)
                        if success:
                            script_data['value'] = new_scripts
                            selected_item.setData(Qt.UserRole, script_data)
                            selected_item.setIcon(QIcon(DEFAULT_ICON_PATH))
                            appendLogWithEffect(display_area,
                                                f"合并脚本 '{script_name}' 已修改: {old_path} -> {new_scripts}\n")
                            QMessageBox.information(None, tr("成功"), tr("合并脚本已更新"))
                        else:
                            appendLogWithEffect(display_area, f"更新合并脚本 '{script_name}' 失败\n")

        elif action == reload_icon_action:
            script_data = selected_item.data(Qt.UserRole)
            if not script_data:
                appendLogWithEffect(display_area, "错误：无法获取脚本数据\n")
                return

            script_name = script_data.get('name', '未知脚本')
            script_type = script_data.get('type')

            if script_type != 'url':
                appendLogWithEffect(display_area, f"脚本 '{script_name}' 不是网页脚本，无需重新加载图标\n")
                return

            current_url = script_data.get('value', '')
            if not current_url:
                appendLogWithEffect(display_area, f"脚本 '{script_name}' 网址为空，无法重新加载图标\n")
                return

            # 判断并修改网址末尾的 / 符号
            new_url = current_url.rstrip('/') if current_url.endswith('/') else current_url + '/'

            # 更新脚本列表中的网址
            success, old_url = update_script_path(script_list, script_name, new_url, display_area)
            if success:
                script_data['value'] = new_url
                selected_item.setData(Qt.UserRole, script_data)
                # 重置图标为默认图标
                selected_item.setIcon(QIcon(DEFAULT_ICON_PATH))
                # 重新加载图标
                get_website_favicon(new_url, lambda icon: selected_item.setIcon(icon))
                appendLogWithEffect(display_area,
                                    f"脚本 '{script_name}' 图标重新加载，网址已更新: {old_url} -> {new_url}\n")
                QMessageBox.information(None, tr("成功"), tr("图标重新加载完成"))
            else:
                appendLogWithEffect(display_area, f"脚本 '{script_name}' 图标重新加载失败\n")

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
                            # 创建合并脚本项时设置链接图标
                            item = QListWidgetItem(name)
                            item.setData(Qt.UserRole, {
                                'type': 'merge',
                                'value': [script for script in selected_scripts],
                                'name': name
                            })
                            # 设置合并脚本的图标（这里使用默认图标或自定义图标）
                            item.setIcon(QIcon(get_resource_path("merge_icon.png")))  # 替换为你的合并图标路径
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
            /* === 主窗口和容器样式 === */
            QDialog, QWidget, QFrame {
                background-color: #F5F7FA;
            }
            QDialog {
                border-radius: 12px;
                border: 1px solid #D0D0D0;
                font-family: 'Microsoft YaHei', Arial, sans-serif;
            }
            /* === 标签样式 === */
            QLabel {
                font-size: 14px;
                color: #000000;
                padding: 4px;
                background-color: transparent;
            }
            /* === 输入框样式 === */
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 6px;
                padding: 6px;
                font-size: 14px;
                color: #000000;
            }
            /* === 按钮样式 === */
            QPushButton {
                background-color: #D0D0D0;
                border: 1px solid #BBBBBB;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                color: #000000;
            }
            QPushButton:hover {
                background-color: #BBBBBB;
            }
            QPushButton:pressed {
                background-color: #AAAAAA;
            }
            /* === 滚动条样式 === */
            QScrollBar:vertical, QScrollBar:horizontal {
                border: none;
                background: transparent;  /* 确保背景透明 */
                background: #F5F7FA;
                width: 10px;
                height: 10px;
                margin: 0px;
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
            /* === 列表控件样式 === */
            QListWidget {
                outline: 0;
                border: 1px solid #CCCCCC;
                border-radius: 6px;
                background-color: #FFFFFF;
                font-size: 12px;
                color: #000000;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #EEEEEE;
            }
            QListWidget::item:selected {
                background-color: #D0D0D0;
                color: #000000;
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
        available_group = QGroupBox("可用脚本 （双击添加）")
        available_group.setStyleSheet("""
            QGroupBox {
                color: black;  /* 设置字体颜色为红色 */
                font: bold 10px;  /* 可选：设置字体大小和粗细 */
            }
        """)
        available_group.setObjectName("AvailableGroup")
        self.available_list = QListWidget()
        self.available_list.setObjectName("AvailableList")
        self.available_list.setMinimumHeight(220)
        self.available_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.populate_list(self.available_list, self.existing_scripts)
        self.available_list.itemDoubleClicked.connect(self.add_to_selected)

        # ---- 已选脚本列表 ----
        selected_group = QGroupBox("已选脚本 （拖动排序）")
        selected_group.setStyleSheet("""
            QGroupBox {
                color: black;  /* 设置字体颜色为红色 */
                font: bold 10px;  /* 可选：设置字体大小和粗细 */
            }
        """)
        selected_group.setObjectName("SelectedGroup")
        self.selected_list = QListWidget()
        self.selected_list.setObjectName("SelectedList")
        self.selected_list.setMinimumHeight(220)
        self.selected_list.setDragDropMode(QListWidget.InternalMove)
        self.selected_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.selected_list.itemDoubleClicked.connect(self.remove_from_selected)
        self.selected_list.model().rowsMoved.connect(self.update_preview)
        self.available_list.setAlternatingRowColors(True)  # 启用交替行颜色
        self.selected_list.setAlternatingRowColors(True)  # 启用交替行颜色

        # === 按钮区域 (放在两个列表之间) ===
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(15)
        button_layout.setAlignment(Qt.AlignCenter)

        # 添加箭头按钮
        self.add_button = QPushButton("添加选中项👉")  # Stylized right arrow
        self.add_button.setObjectName("AddButton")
        self.add_button.setFixedSize(120, 40)
        self.add_button.clicked.connect(self.add_to_selected)

        self.remove_button = QPushButton("👈移除选中项")  # Stylized left arrow
        self.remove_button.setObjectName("RemoveButton")
        self.remove_button.setFixedSize(120, 40)
        self.remove_button.clicked.connect(self.remove_from_selected)

        # 添加按钮到布局
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()

        # 列表组布局
        available_group.setLayout(QVBoxLayout())
        available_group.layout().addWidget(self.available_list)

        selected_group.setLayout(QVBoxLayout())
        selected_group.layout().addWidget(self.selected_list)

        # 将部件添加到主布局
        lists_layout.addWidget(available_group)
        lists_layout.addWidget(button_container)  # 添加按钮容器在中间
        lists_layout.addWidget(selected_group)

        # === 预览区域 ===
        preview_group = QGroupBox("执行顺序>>>")
        preview_group.setStyleSheet("""
            QGroupBox {
                color: black;  /* 设置字体颜色为红色 */
                font: bold 11px;  /* 可选：设置字体大小和粗细 */
            }
        """)
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
        main_layout.addWidget(preview_group)
        main_layout.addWidget(confirm_buttons)

        # 初始更新预览
        self.update_preview()

        # 设置按钮样式
        self.set_button_styles()

    def set_button_styles(self):
        """设置按钮的统一样式，与英语学习按钮一致，按下后鼠标悬浮无颜色变化"""
        button_style = """
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
                box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.2);
                transform: scale(0.95); /* 添加按下时的缩小效果 */
            }
            QPushButton:pressed:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 rgba(120, 120, 120, 1), stop:1 rgba(90, 90, 90, 1));
                border: 1px solid #999999;
            }
        """

        self.add_button.setStyleSheet(button_style)
        self.remove_button.setStyleSheet(button_style)
        self.confirm_button.setStyleSheet(button_style)

    def populate_list(self, list_widget, scripts):
        """填充列表控件并设置交替颜色（与主窗口一致）"""
        list_widget.clear()
        for i, script in enumerate(scripts):
            item = QListWidgetItem(f"{script['name']} ({script['type']})")
            item.setData(Qt.UserRole, script)

            # 设置交替颜色（与主窗口一致）
            if i % 2 == 0:
                item.setBackground(QColor("#F5F5F5"))  # 偶数行 - 浅灰
            else:
                item.setBackground(QColor("#E8E8E8"))  # 奇数行 - 稍深灰

            list_widget.addItem(item)

    def update_selected_colors(self):
        """更新选中列表的颜色，确保交替"""
        for i in range(self.selected_list.count()):
            item = self.selected_list.item(i)
            if i % 2 == 0:
                item.setBackground(QColor("#F0F0F0"))
            else:
                item.setBackground(QColor("#D9D9D9"))

    def add_to_selected(self):
        """添加选中项到已选列表并保持交替颜色"""
        selected_items = self.available_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "提示", "请先在左侧选择要添加的脚本")
            return

        for item in selected_items:
            script_data = item.data(Qt.UserRole)
            if not self.is_script_in_list(self.selected_list, script_data['name']):
                new_item = QListWidgetItem(item.text())
                new_item.setData(Qt.UserRole, script_data)

                # 根据当前选中列表的项目数设置交替颜色
                if self.selected_list.count() % 2 == 0:
                    new_item.setBackground(QColor("#F5F5F5"))  # 偶数行 - 浅灰
                else:
                    new_item.setBackground(QColor("#E8E8E8"))  # 奇数行 - 稍深灰

                self.selected_list.addItem(new_item)
                self.available_list.takeItem(self.available_list.row(item))

        # 更新可用列表的颜色，确保交替
        self.update_list_colors(self.available_list)
        self.update_list_colors(self.selected_list)
        self.update_preview()

    def remove_from_selected(self):
        """从已选列表中移除选中项并保持交替颜色"""
        selected_items = self.selected_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "提示", "请先在右侧选择要移除的脚本")
            return

        for item in selected_items:
            script_data = item.data(Qt.UserRole)
            new_item = QListWidgetItem(item.text())
            new_item.setData(Qt.UserRole, script_data)

            # 添加到可用列表时也保持交替颜色
            if self.available_list.count() % 2 == 0:
                new_item.setBackground(QColor("#F5F5F5"))  # 偶数行 - 浅灰
            else:
                new_item.setBackground(QColor("#E8E8E8"))  # 奇数行 - 稍深灰

            self.available_list.addItem(new_item)
            self.selected_list.takeItem(self.selected_list.row(item))

        # 重新设置两个列表的颜色，确保交替
        self.update_list_colors(self.available_list)
        self.update_list_colors(self.selected_list)
        self.update_preview()

    def update_list_colors(self, list_widget):
        """更新列表控件的交替颜色"""
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if i % 2 == 0:
                item.setBackground(QColor("#F5F5F5"))  # 偶数行 - 浅灰
            else:
                item.setBackground(QColor("#E8E8E8"))  # 奇数行 - 稍深灰

    def is_script_in_list(self, list_widget, script_name):
        """检查脚本是否已在列表中"""
        return any(
            list_widget.item(i).data(Qt.UserRole)['name'] == script_name
            for i in range(list_widget.count())
        )

    def update_preview(self):
        """生成简洁无框的脚本预览"""
        self.preview.clear()
        self.preview.setFont(QFont("Consolas", 8))  # 仍然使用等宽字体保证对齐

        if self.selected_list.count() == 0:
            self.preview.setPlainText("当前没有选择任何脚本")
            self.preview.setStyleSheet("color: red;")  # 设置文本颜色为红色
            return

        # 列配置（列名，宽度，对齐方式）
        columns = [
            ("序号", 4, '^'),  # 居中
            ("类型", 8, '^'),
            ("  脚本名称", 24, '<'),  # 左对齐
            ("路径/URL", 40, '<')
        ]

        # 生成表头
        header = "  ".join([f"{col[0]:{col[2]}{col[1]}}" for col in columns])
        separator = "〰" * 51  # 简单的分隔线

        # 构建表格内容
        table_content = []
        table_content.append(header)
        table_content.append(separator)

        for i in range(self.selected_list.count()):
            item = self.selected_list.item(i)
            script = item.data(Qt.UserRole)

            # 处理显示内容
            script_type = "  🌐网页脚本" if script['type'] == 'url' else "  📂软件脚本"
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


class FastScrollDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)
        self.list = parent

        # 精确颜色匹配（从样式表提取）
        self.color_map = {
            'even': QColor("#F0F0F0"),
            'odd': QColor("#E0E0E0"),
            'selected': QColor("#A0A0A0"),
            'hover': QColor("#C0C0C0")
        }


class CreateScriptDialog(QDialog):
    def __init__(self, parent=None, list_widget=None, display_area=None, completer_model=None):
        super(CreateScriptDialog, self).__init__(parent)
        # 移除问号按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.setWindowTitle("创建脚本")
        self.setFixedSize(420, 300)
        # 显式设置日间模式样式，防止继承夜间模式
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F7FA;
                border-radius: 12px;
                border: 1px solid #D0D0D0;
                color: #000000;  /* 添加默认字体色 */
                font-family: 'Microsoft YaHei', Arial, sans-serif;
            }
            QLabel {
                color: #000000;  /* 标签字体色 */
                font-size: 14px;
                padding: 4px;
            }
            QLineEdit {
                background-color: #FFFFFF;  /* 区分输入区域 */
                border: 1px solid #BBBBBB;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                color: #000000;  /* 输入框字体色 */
            }
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
                box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.2);
                transform: scale(0.95); /* 添加按下时的缩小效果 */
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
                item.setIcon(QIcon(DEFAULT_ICON_PATH))  # 先设置默认图标
                self.list_widget.addItem(item)
                self.completer_model.insertRow(0)
                self.completer_model.setData(self.completer_model.index(0), name)
                save_current_scripts()
                update_item_colors()
                appendLogWithEffect(self.display_area, f"创建网页脚本🌐 '{name}' 成功！\n")
                # 异步加载实际图标
                row = self.list_widget.count() - 1
                get_website_favicon(url, lambda icon: self.list_widget.item(row).setIcon(icon))
                self.close()
        except Exception as e:
            appendLogWithEffect(self.display_area, f"Error creating web script: {e}\n")

    def create_software_script(self):
        try:
            name, file_path = get_user_input_file(self)
            if name and file_path:
                item = QListWidgetItem(name)
                item.setData(Qt.UserRole, {'type': 'file', 'value': file_path, 'name': name})
                item.setIcon(QIcon(DEFAULT_ICON_PATH))  # 先设置默认图标
                self.list_widget.addItem(item)
                self.completer_model.insertRow(0)
                self.completer_model.setData(self.completer_model.index(0), name)
                save_current_scripts()
                update_item_colors()
                appendLogWithEffect(self.display_area, f"创建软件脚本🖥️ '{name}' 成功！\n")
                # 异步加载实际图标
                row = self.list_widget.count() - 1
                get_file_icon(file_path, lambda icon: self.list_widget.item(row).setIcon(icon))
                self.close()
        except Exception as e:
            appendLogWithEffect(self.display_area, f"Error creating software script: {e}\n")

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
                                self.close()
        except Exception as e:
            appendLogWithEffect(self.display_area, f"Error creating merge script: {e}\n")
            QMessageBox.critical(self, tr('错误'), f"{tr('创建合并脚本时发生错误')}: {e}")





class StyledScrollingDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.list_widget = parent

        # 获取全局夜间模式标志
        global night_mode
        self.night_mode = night_mode

        # 根据夜间模式选择颜色
        self.update_colors()

    def update_colors(self):
        """根据夜间模式更新颜色"""
        if self.night_mode:
            self.even_color = QColor("#333333")  # 夜间模式偶数行颜色：深灰
            self.odd_color = QColor("#3A3A3A")  # 夜间模式奇数行颜色：稍浅的深灰
            self.selected_color = QColor("#E8ECEF")  # 夜间模式选中颜色：浅白色
            self.hover_color = QColor("#E8ECEF")  # 夜间模式悬停颜色：稍亮的浅白色
            self.shadow_color = QColor(200, 200, 200, 60)  # 夜间模式阴影颜色：较亮的灰白色
            self.selected_text_color = QColor("#000000")  # 夜间模式选中字体颜色：黑色
        else:
            self.even_color = QColor("#F7F9FC")  # 日间模式偶数行颜色：浅蓝灰色，干净高级
            self.odd_color = QColor("#EDF1F7")  # 日间模式奇数行颜色：稍深的蓝灰色，柔和对比
            self.selected_color = QColor("#D1E0FF")  # 日间模式选中颜色：浅蓝色，现代感
            self.hover_color = QColor("#D1E0FF")  # 日间模式悬停颜色：浅灰蓝色，优雅过渡
            self.shadow_color = QColor(50, 50, 50, 50)  # 日间模式阴影颜色：深灰色，柔和高雅
            self.selected_text_color = QColor("#000000")  # 日间模式选中字体颜色：黑色

    def paint(self, painter, option, index):
        # 在绘制前更新颜色，确保实时反映夜间模式
        global night_mode
        if self.night_mode != night_mode:
            self.night_mode = night_mode
            self.update_colors()

        painter.save()
        # 设置抗锯齿和平滑像素转换以提高渲染质量
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)

        # 获取当前项
        item = self.list_widget.itemFromIndex(index)
        if not item:
            painter.restore()
            return

        # 如果项隐藏，则不绘制
        if item.isHidden():
            painter.restore()
            return

        # 获取可见项索引
        visible_index = self.get_visible_index(index)
        if visible_index == -1:
            painter.restore()
            return

        # 获取悬停进度并确保平滑
        hover_progress = min(max(self.list_widget.hover_states.get(id(item), 0.0), 0.0), 1.0)
        is_hovered = hover_progress > 0
        # 使用缓入缓出二次函数计算动画进度
        eased_progress = self.easeInOutQuad(hover_progress)

        # 计算背景颜色
        bg_color = self.even_color if visible_index % 2 == 0 else self.odd_color
        if option.state & QStyle.State_Selected:
            bg_color = self.selected_color
        if is_hovered:
            bg_color = self.mix_colors(bg_color, self.hover_color, eased_progress)

        # 动画参数配置：抽卡片效果
        max_offset = 19  # 向右滑动的最大像素距离
        scale = 1.0 + 0.07 * eased_progress  # 轻微放大效果，最大 1.05 倍
        shadow_opacity = 0.3 + 0.3 * eased_progress  # 动态阴影透明度

        # 获取原始项矩形区域
        original_rect = option.rect

        # 应用悬停变换
        transformed_rect = QRectF(original_rect)
        if is_hovered:
            # 计算偏移量
            offset_x = max_offset * eased_progress
            transformed_rect.translate(offset_x, 0)

            # 应用缩放
            center = transformed_rect.center()
            painter.translate(center)
            painter.scale(scale, scale)
            painter.translate(-center)

        # 绘制阴影（仅在悬停时）
        if is_hovered:
            shadow_path = QPainterPath()
            shadow_rect = QRectF(transformed_rect.adjusted(3, 3, -3, -3))
            shadow_path.addRoundedRect(shadow_rect, 15, 15)
            shadow_color = self.shadow_color
            shadow_color.setAlphaF(shadow_opacity)
            painter.setPen(Qt.NoPen)
            painter.setBrush(shadow_color)
            painter.drawPath(shadow_path)

        # 绘制圆角背景
        path = QPainterPath()
        radius = 15
        rect_f = QRectF(transformed_rect.adjusted(2, 2, -2, -2))
        path.addRoundedRect(rect_f, radius, radius)

        # 应用渐变背景
        gradient = QLinearGradient(rect_f.topLeft(), rect_f.bottomRight())
        gradient.setColorAt(0, bg_color.lighter(190))
        gradient.setColorAt(1, bg_color.darker(100))
        painter.setPen(Qt.NoPen)
        painter.fillPath(path, gradient)

        # 恢复画家状态以绘制图标和文本（避免缩放影响）
        painter.restore()
        painter.save()

        # 绘制图标
        icon = item.icon()
        if not icon.isNull():
            icon_rect = QRect(
                int(transformed_rect.left() + 12),
                int(transformed_rect.top() + (transformed_rect.height() - 20) / 2),
                20, 20
            )
            icon.paint(painter, icon_rect, Qt.AlignCenter)

        # 绘制文本
        text = item.text() or ""
        font = option.font
        font.setPointSize(12)
        font.setStyleStrategy(QFont.PreferAntialias)
        painter.setFont(font)
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(text)
        available_width = transformed_rect.width() - 40

        # 获取滚动数据
        scroll_data = item.data(Qt.UserRole + 1)
        offset = scroll_data[0] if scroll_data and len(scroll_data) > 0 else 0

        # 设置文本颜色
        text_color = option.palette.color(QPalette.Text)
        if option.state & QStyle.State_Selected:
            text_color = self.selected_text_color
        if is_hovered:
            if self.night_mode:
                text_color = QColor("#000000")
            else:
                text_color = text_color.lighter(110)

        painter.setPen(text_color)

        # 绘制文本区域
        text_rect = QRect(transformed_rect.toRect())
        text_rect.setLeft(int(transformed_rect.left() + 40))
        text_rect.setWidth(int(available_width))

        if text_width > available_width:
            painter.setClipRect(text_rect)
            adjusted_rect = QRect(text_rect)
            adjusted_rect.setLeft(int(text_rect.left() - offset))
            painter.drawText(adjusted_rect, Qt.AlignLeft | Qt.AlignVCenter, text)
        else:
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, text)

        painter.restore()

    def mix_colors(self, color1, color2, factor):
        """混合两种颜色"""
        r1, g1, b1 = color1.red(), color1.green(), color1.blue()
        r2, g2, b2 = color2.red(), color2.green(), color2.blue()

        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)

        return QColor(r, g, b)

    def ease_animation(self, progress):
        """缓动函数（例如，ease-out）"""
        return progress  # 可以替换为更复杂的缓动函数

    def enterEvent(self, event):
        """鼠标进入事件"""
        index = self.indexAt(event.pos())
        if index.isValid():
            item = self.list_widget.item(index.row())
            if item:
                item_id = item.data(Qt.UserRole)
                self.start_hover_animation(item_id)

    def leaveEvent(self, event):
        """鼠标离开事件"""
        index = self.indexAt(event.pos())
        if index.isValid():
            item = self.list_widget.item(index.row())
            if item:
                item_id = item.data(Qt.UserRole)
                self.start_hover_animation(item_id, reverse=True)

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        index = self.indexAt(event.pos())
        if index.isValid():
            item = self.list_widget.item(index.row())
            if item:
                item_id = item.data(Qt.UserRole)
                if item_id != getattr(self, 'current_hover_item_id', None):
                    # 如果当前悬停项改变，则启动新的悬停动画
                    if hasattr(self, 'current_hover_item_id') and self.current_hover_item_id is not None:
                        self.start_hover_animation(self.current_hover_item_id, reverse=True)  # 反向启动之前的动画
                    self.current_hover_item_id = item_id
                    self.start_hover_animation(item_id)
        else:
            # 如果鼠标不在任何项上，且有悬停项，则反向启动动画
            if hasattr(self, 'current_hover_item_id') and self.current_hover_item_id is not None:
                self.start_hover_animation(self.current_hover_item_id, reverse=True)
                self.current_hover_item_id = None

    def start_hover_animation(self, item_id, reverse=False):
        """启动悬停动画"""
        if item_id in self.hover_animations:
            self.hover_animations[item_id].stop()  # 停止之前的动画

        animation = QPropertyAnimation(self, b"hover_progress")
        animation.setItemId(item_id)  # 使用自定义方法存储 item_id
        animation.setDuration(250)  # 动画时长
        animation.setStartValue(self.hover_states.get(item_id, 0.0))
        animation.setEndValue(0.0 if reverse else 1.0)
        animation.setEasingCurve(QEasingCurve.Linear)  # 动画曲线
        animation.finished.connect(lambda: self.animation_finished(item_id))  # 动画完成信号

        animation.valueChanged.connect(self.update_hover_state)  # 连接到更新悬停状态的槽函数
        self.hover_animations[item_id] = animation
        animation.start()

    def animation_finished(self, item_id):
        """动画完成时清理"""
        if item_id in self.hover_animations:
            del self.hover_animations[item_id]
        self.viewport().update()

    def update_hover_state(self, value):
        """更新悬停状态"""
        animation = self.sender()
        if animation:
            item_id = animation.itemId()  # 使用自定义方法获取 item_id
            self.hover_states[item_id] = value
            self.update_scroll_positions()  # 更新滚动位置
            self.viewport().update()

    def setHoverProgress(self, progress):
        """设置悬停进度"""
        animation = self.sender()
        if animation:
            item_id = animation.itemId()
            self.hover_states[item_id] = progress
            self.viewport().update()

    def hoverProgress(self):
        """获取悬停进度"""
        animation = self.sender()
        if animation:
            item_id = animation.itemId()
            return self.hover_states.get(item_id, 0.0)
        return 0.0

    def update_scroll_positions(self):
        viewport = self.viewport()
        viewport_width = viewport.width()
        fm = QFontMetrics(self.font())

        for i in range(self.count()):
            item = self.item(i)
            if not item or item == self.current_hover_item:  # 改为 current_hover_item
                continue

            text = item.text()
            text_width = fm.horizontalAdvance(text)
            available_width = viewport_width - 35

            if text_width > available_width:
                item_id = item.data(Qt.UserRole)
                if item_id not in self.scroll_animations:
                    self.start_scroll_animation(item, text_width, available_width)

    def start_scroll_animation(self, item, text_width, available_width):
        """启动滚动动画"""
        item_id = item.data(Qt.UserRole)
        if item_id in self.scroll_animations:
            self.scroll_animations[item_id].stop()

        max_offset = text_width - available_width
        duration = max(5000, int(max_offset * 20))  # 动画时长与文本长度成正比

        animation = QPropertyAnimation(self, b"scroll_offset")
        animation.setItemId(item_id)  # 使用自定义方法存储 item_id
        animation.setDuration(duration)
        animation.setStartValue(0)
        animation.setEndValue(max_offset)
        animation.setLoopCount(-1)  # 无限循环
        animation.setEasingCurve(QEasingCurve.Linear)

        animation.valueChanged.connect(self.update_scroll_offset)
        self.scroll_animations[item_id] = animation
        animation.start()

    def update_scroll_offset(self, offset):
        """更新滚动偏移"""
        animation = self.sender()
        if animation:
            item_id = animation.itemId()
            for i in range(self.count()):
                item = self.item(i)
                if item and item.data(Qt.UserRole) == item_id:
                    item.setData(Qt.UserRole + 1, (offset,))  # 存储偏移量
                    break
            self.viewport().update()

    def setScrollOffset(self, offset):
        """设置滚动偏移"""
        animation = self.sender()
        if animation:
            item_id = animation.itemId()
            for i in range(self.count()):
                item = self.item(i)
                if item and item.data(Qt.UserRole) == item_id:
                    item.setData(Qt.UserRole + 1, (offset,))  # 存储偏移量
                    break
            self.viewport().update()

    def scrollOffset(self):
        """获取滚动偏移"""
        animation = self.sender()
        if animation:
            item_id = animation.itemId()
            for i in range(self.count()):
                item = self.item(i)
                if item and item.data(Qt.UserRole) == item_id:
                    scroll_data = item.data(Qt.UserRole + 1)
                    return scroll_data[0] if scroll_data else 0
        return 0


class UnifiedItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.list_widget = parent

        # 获取全局夜间模式标志
        global night_mode
        self.night_mode = night_mode

        # 根据夜间模式选择颜色
        self.update_colors()

    def update_colors(self):
        """根据夜间模式更新颜色"""
        if self.night_mode:
            self.even_color = QColor("#333333")  # 夜间模式偶数行颜色：深灰
            self.odd_color = QColor("#333333")  # 夜间模式奇数行颜色：稍浅的深灰
            self.selected_color = QColor("#F5F5F5")  # 夜间模式选中颜色：浅白色
            self.hover_color = QColor("#F5F5F5")  # 夜间模式悬停颜色：稍亮的浅白色
            self.shadow_color = QColor(200, 200, 200, 60)  # 夜间模式阴影颜色：较亮的灰白色
            self.selected_text_color = QColor("#FFFFFF")  # 夜间模式选中字体颜色：白色
        else:
            self.even_color = QColor("#F7F9FC")  # 日间模式偶数行颜色：浅蓝灰色，干净高级
            self.odd_color = QColor("#F7F9FC")  # 日间模式奇数行颜色：稍深的蓝灰色，柔和对比
            self.selected_color = QColor("#F5F5F5")  # 日间模式选中颜色：浅蓝色，现代感
            self.hover_color = QColor("#F5F5F5")  # 日间模式悬停颜色：浅灰蓝色，优雅过渡
            self.shadow_color = QColor(200, 200, 200, 60)  # 日间模式阴影颜色：深灰色，柔和高雅
            self.selected_text_color = QColor("#004654")  # 日间模式选中字体颜色：黑色

    def paint(self, painter, option, index):
        """
        绘制列表项，包含倒圆角图标、背景、文本和动画效果
        参数：
            painter: QPainter 对象，用于绘制
            option: QStyleOptionViewItem 对象，包含绘制选项
            index: QModelIndex 对象，表示当前项的索引
        """
        # 在绘制前更新颜色，确保实时反映夜间模式
        global night_mode
        if self.night_mode != night_mode:
            self.night_mode = night_mode
            self.update_colors()

        painter.save()
        # 设置抗锯齿和平滑像素转换以提高渲染质量
        painter.setRenderHints(QPainter.TextAntialiasing)  # 仅文本抗锯齿
        painter.setRenderHints(
            QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.HighQualityAntialiasing)

        # 获取当前项
        item = self.list_widget.itemFromIndex(index)
        if not item:
            painter.restore()
            return super().paint(painter, option, index)

        # 如果项隐藏，则不绘制
        if item.isHidden():
            painter.restore()
            return

        # 获取悬停进度并确保平滑
        hover_progress = min(max(self.list_widget.hover_states.get(id(item), 0.0), 0.0), 1.0)
        is_hovered = hover_progress > 0
        # 使用缓入缓出二次函数计算动画进度
        eased_progress = self.easeInOutQuad(hover_progress)

        # 计算背景颜色，确保悬停和选中状态一致
        bg_color = self.even_color  # 统一使用 even_color（夜间模式下 even_color 和 odd_color 相同）
        if option.state & QStyle.State_Selected or is_hovered:
            bg_color = self.selected_color  # 悬停和选中使用相同的颜色（夜间模式为 #333333）

        # 悬停动画参数配置
        max_offset = 30  # 卡片向右滑动的最大像素距离
        scale = 1.0 + 0.15 * eased_progress  # 轻微放大效果，增加“弹出”感
        rotation = 0 * eased_progress  # 旋转角度，最大0度
        shadow_opacity = 0.3 + 0.2 * eased_progress  # 动态阴影透明度

        # 获取原始项矩形区域
        original_rect = option.rect

        # 应用悬停变换
        transformed_rect = QRectF(original_rect)
        if is_hovered:
            pivot_x = original_rect.center().x()  # 旋转圆心为选项中心
            pivot_y = original_rect.center().y()

            # 使用浮点数偏移以确保平滑动画
            offset_x = max_offset * eased_progress
            offset_y = 0 * eased_progress  # 轻微垂直提升
            painter.translate(pivot_x + offset_x, pivot_y + offset_y)
            painter.scale(scale, scale)
            painter.rotate(rotation)
            painter.translate(-pivot_x, -pivot_y)

            transformed_rect = QRectF(original_rect).translated(offset_x, offset_y)

        # 绘制阴影（仅在悬停时）
        if is_hovered:
            shadow_path = QPainterPath()
            shadow_rect = QRectF(transformed_rect.adjusted(4, 4, -4, -4))
            shadow_path = self.create_rounded_path(shadow_rect, 19, left_only=True)  # 使用左边圆角
            shadow_color = self.shadow_color
            shadow_color.setAlphaF(shadow_opacity)
            painter.setPen(Qt.NoPen)
            painter.setBrush(shadow_color)
            painter.drawPath(shadow_path)

        # 绘制圆角背景（左边圆角，右边直角）
        path = QPainterPath()
        rect_f = QRectF(transformed_rect.adjusted(2, 2, -2, -2))
        path = self.create_rounded_path(rect_f, 19, left_only=True)

        # 应用渐变背景，动态过渡方向
        is_selected_or_hovered = option.state & QStyle.State_Selected or is_hovered
        gradient = QLinearGradient(0, rect_f.top(), 0, rect_f.top())  # 初始化，稍后设置点
        if self.night_mode:
            window_bg_color = QColor("#000000")  # 夜间模式窗口背景色
            default_start_color = QColor("#FFFFFF")  # 未选中：左侧白色
            default_end_color = QColor("#000000")  # 未选中：右侧黑色
        else:
            window_bg_color = QColor("#F0F2F5")  # 日间模式窗口背景色
            default_start_color = window_bg_color  # 默认：浅蓝灰色
            default_end_color = bg_color.darker(190)  # 默认：较深色

        # 动态调整渐变方向和颜色
        if is_selected_or_hovered and self.night_mode:
            # 夜间模式，悬停或选中：左白右黑（#FFFFFF -> #000000）
            start_color = default_start_color  # #FFFFFF
            end_color = default_end_color  # #000000

            start_x = rect_f.left() * (1 - eased_progress) + rect_f.right() * eased_progress
            end_x = rect_f.right() * (1 - eased_progress) + rect_f.left() * eased_progress
        elif is_selected_or_hovered:
            # 日间模式，悬停或选中：左浅右深
            start_color = default_end_color
            end_color = default_start_color
            start_x = rect_f.left() * (1 - eased_progress) + rect_f.right() * eased_progress
            end_x = rect_f.right() * (1 - eased_progress) + rect_f.left() * eased_progress
        elif self.night_mode:
            # 夜间模式，未选中：右黑左白（#000000 -> #FFFFFF）
            start_color = default_end_color  # #000000
            end_color = default_start_color  # #FFFFFF
            start_x = rect_f.right() * (1 - eased_progress) + rect_f.left() * eased_progress
            end_x = rect_f.left() * (1 - eased_progress) + rect_f.right() * eased_progress
        else:
            # 日间模式，未选中：左深右浅
            start_color = default_start_color
            end_color = default_end_color
            start_x = rect_f.right() * (1 - eased_progress) + rect_f.left() * eased_progress
            end_x = rect_f.left() * (1 - eased_progress) + rect_f.right() * eased_progress

        gradient.setStart(start_x, rect_f.top())
        gradient.setFinalStop(end_x, rect_f.top())
        gradient.setColorAt(0, start_color)
        gradient.setColorAt(1, end_color)

        painter.setPen(Qt.NoPen)
        painter.fillPath(path, gradient)

        # 恢复画家状态以绘制图标和文本（避免旋转影响）
        painter.restore()
        painter.save()

        # 绘制图标（带倒圆角效果）
        icon = item.icon()
        if not icon.isNull():
            icon_rect = QRect(
                int(transformed_rect.left() + 8),
                int(transformed_rect.top() + (transformed_rect.height() - 20) / 2),
                20, 20
            )
            # 创建倒圆角路径
            icon_path = QPainterPath()
            icon_rect_f = QRectF(icon_rect)
            corner_radius = 5  # 图标倒圆角半径
            icon_path.addRoundedRect(icon_rect_f, corner_radius, corner_radius)

            # 保存当前裁剪状态
            painter.save()
            # 应用倒圆角裁剪
            painter.setClipPath(icon_path)
            # 绘制图标
            icon.paint(painter, icon_rect, Qt.AlignCenter)
            # 恢复裁剪状态
            painter.restore()

        # 绘制文本
        text = item.text()
        font = option.font
        font.setStyleStrategy(QFont.PreferAntialias)  # 优化抗锯齿
        painter.setFont(font)
        fm = QFontMetrics(font)

        text_width = fm.horizontalAdvance(text)
        available_width = transformed_rect.width() - 35

        # 获取滚动数据
        scroll_data = item.data(Qt.UserRole + 1)
        offset = scroll_data[0] if scroll_data else 0

        # 设置文本颜色
        text_color = option.palette.color(QPalette.Text)
        if is_selected_or_hovered:
            text_color = self.selected_text_color  # 夜间模式下为黑色

        painter.setPen(text_color)

        # 绘制文本区域
        text_rect = QRect(transformed_rect.toRect())
        text_rect.setLeft(int(transformed_rect.left() + 35))
        text_rect.setWidth(int(available_width))

        if text_width > available_width:
            painter.setClipRect(text_rect)
            adjusted_rect = QRect(text_rect)
            adjusted_rect.setLeft(int(text_rect.left() - offset))
            painter.drawText(adjusted_rect, Qt.AlignLeft | Qt.AlignVCenter, text)
        else:
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, text)

        painter.restore()

    def get_visible_index(self, index):
        """计算项在当前可见项中的索引"""
        visible_index = 0
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if not item.isHidden():
                if i == index.row():
                    return visible_index
                visible_index += 1
        return -1

    def mix_colors(self, color1, color2, ratio):
        """混合两种颜色根据比例"""
        inv_ratio = 1 - ratio
        return QColor(
            int(color1.red() * inv_ratio + color2.red() * ratio),
            int(color1.green() * inv_ratio + color2.green() * ratio),
            int(color1.blue() * inv_ratio + color2.blue() * ratio)
        )

    def easeInOutQuad(self, t):
        """缓入缓出二次动画函数，增加平滑度"""
        t *= 2
        if t < 1:
            return 0.5 * t * t
        t -= 1
        return -0.5 * (t * (t - 2) - 1)

    def create_rounded_path(self, rect, radius, left_only=False):
        """
        创建自定义圆角路径
        参数：
            rect: QRectF 对象，表示路径的矩形区域
            radius: 圆角半径
            left_only: 是否仅左边圆角，右边直角
        返回：
            QPainterPath 对象，表示圆角路径
        """
        path = QPainterPath()
        left = rect.left()
        right = rect.right()
        top = rect.top()
        bottom = rect.bottom()

        if left_only:
            # 左上角圆角
            path.moveTo(left + radius, top)
            path.arcTo(left, top, radius * 2, radius * 2, 90, 90)
            # 左下角圆角
            path.lineTo(left, bottom - radius)
            path.arcTo(left, bottom - radius * 2, radius * 2, radius * 2, 180, 90)
            # 右下角直角
            path.lineTo(right, bottom)
            # 右上角直角
            path.lineTo(right, top)
            path.closeSubpath()
        else:
            # 所有角圆角
            path.addRoundedRect(rect, radius, radius)

        return path





class SmoothListWidget(QListWidget):
    def __init__(self, status_bar, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.setItemDelegate(UnifiedItemDelegate(self))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMouseTracking(True)

        # 使用字典来跟踪所有项的悬停状态
        self.hover_states = {}  # {id(item): hover_progress}
        self.current_hover_item = None  # 初始化 current_hover_item

        # 动画定时器
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animations)
        self.animation_timer.start(5)  # ~120fps

        # 原有定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_scroll_positions)
        self.timer.start(12)

        self.model().rowsInserted.connect(self.on_rows_inserted)

    def show_context_menu(self, pos):
        """
        显示右键上下文菜单
        参数:
            pos: 鼠标点击的位置（QPoint）
        """
        item = self.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #F5F7FA;
                border: 1px solid #D0D0D0;
                border-radius: 8px;
                font-family: 'Microsoft YaHei', Arial, sans-serif;
                font-size: 14px;
                color: #222222;
            }
            QMenu::item {
                padding: 8px 20px;
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                                stop:0 rgba(160, 160, 160, 1), stop:1 rgba(120, 120, 120, 1));
                border-radius: 4px;
                color: #222222;
            }
        """)
        reload_icon_action = QAction("重新加载图标", self)
        reload_icon_action.triggered.connect(lambda: self.reload_icon(item))
        menu.addAction(reload_icon_action)
        menu.exec_(self.mapToGlobal(pos))

    def reload_icon(self, item):
        """
        重新加载选中项的图标（占位函数）
        参数:
            item: 选中的 QListWidgetItem
        """
        script_data = item.data(Qt.UserRole)
        if not script_data:
            appendLogWithEffect(display_area, "错误：无法获取脚本数据\n")
            return
        script_name = script_data.get('name', '未知脚本')
        appendLogWithEffect(display_area, f"重新加载图标：{script_name}（功能待实现）\n")


    def update_animations(self):
        """更新所有项的动画状态"""
        needs_update = False

        # 动画持续时间（毫秒）
        animation_duration = 300  # 可配置的动画时间，单位：毫秒

        # 计算每帧的步长，基于定时器间隔（5ms）和期望的总动画时间
        step = (5.0 / animation_duration) * 2  # 调整步长以控制动画速度

        # 更新所有项的悬停状态
        for i in range(self.count()):
            item = self.item(i)
            item_id = id(item)

            # 确定目标状态 (1.0 如果是当前悬停项，否则 0.0)
            target = 1.0 if item == self.current_hover_item else 0.0

            # 获取当前进度或初始化
            current = self.hover_states.get(item_id, 0.0)

            # 如果已经达到目标状态，跳过
            if current == target:
                continue

            # 计算新状态
            if target > current:
                new_progress = min(target, current + step)
            else:
                new_progress = max(target, current - step)

            # 更新状态
            self.hover_states[item_id] = new_progress
            needs_update = True

            # 如果动画完成，清理字典
            if new_progress == 0.0:
                del self.hover_states[item_id]

        if needs_update:
            self.viewport().update()

    def update_scroll_positions(self):
        viewport = self.viewport()
        viewport_width = viewport.width()
        fm = QFontMetrics(self.font())

        for i in range(self.count()):
            item = self.item(i)
            if not item or item == self.current_hover_item:  # 改为 current_hover_item
                continue

            text = item.text()
            text_width = fm.horizontalAdvance(text)
            avail_width = viewport_width - 30  # 25(icon) + 5(margin)

            if text_width <= avail_width:
                continue

            # [current_offset, direction, max_offset, speed_factor]
            scroll_data = item.data(Qt.UserRole + 1) or [0, 1, text_width - avail_width, 1.0]

            # 动态速度计算（开头和结尾稍慢）
            speed = 0.8 if scroll_data[0] < 10 or scroll_data[0] > scroll_data[2] - 10 else 1.2

            # 更新位置（基础速度0.5 * 动态系数）
            new_offset = scroll_data[0] + (0.4 * speed) * scroll_data[1]

            # 边界反弹逻辑
            if new_offset >= scroll_data[2]:
                new_offset = scroll_data[2]
                scroll_data[1] = -1
            elif new_offset <= 0:
                new_offset = 0
                scroll_data[1] = 1

            item.setData(Qt.UserRole + 1, [new_offset, scroll_data[1], scroll_data[2], speed])

        viewport.update()

    def on_rows_inserted(self, parent, start, end):
        for i in range(start, end + 1):
            item = self.item(i)
            if self.is_text_overflow(item):
                item.setData(Qt.UserRole + 1, [0, 1])

    def is_text_overflow(self, item):
        fm = QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(item.text())
        available_width = self.viewport().width() - 30  # 25(icon) + 5(margin)
        return text_width > available_width

    def updateScrollingOffsets(self):
        for i in range(self.count()):
            item = self.item(i)
            if not item or not self.is_text_overflow(item) or item == self.hovered_item:
                continue

            scroll_data = item.data(Qt.UserRole + 1)
            if scroll_data is None:
                scroll_data = [0, 1]  # [current_offset, direction]

            offset, direction = scroll_data
            fm = QFontMetrics(self.font())
            max_offset = max(0, fm.horizontalAdvance(item.text()) - (self.viewport().width() - 30))

            # 调整步长为0.3（原为0.5）让滑动变慢
            new_offset = offset + 0.3 * direction

            # 边界检测
            if new_offset >= max_offset:
                new_offset = max_offset
                direction = -1
            elif new_offset <= 0:
                new_offset = 0
                direction = 1

            item.setData(Qt.UserRole + 1, [new_offset, direction])

        self.viewport().update()

    def mouseMoveEvent(self, event):
        # 更新当前悬停项
        item = self.itemAt(event.pos())
        self.current_hover_item = item

        # 原有状态栏更新逻辑
        if item:
            script_data = item.data(Qt.UserRole)
            if script_data:
                script_name = script_data.get('name', '未知脚本')
                script_type = script_data.get('type', 'file')
                script_value = script_data.get('value', '未知路径')

                separator = "     ｜    地址： "
                merge_separator = " ➔ "

                if script_type == 'merge':
                    sub_scripts = script_data.get('value', [])
                    sub_script_names = merge_separator.join(s['name'] for s in sub_scripts)
                    status_text = f"🔗 {script_name}{separator}{sub_script_names}"
                elif script_type == 'url':
                    clean_url = script_value.replace('https://', '').replace('http://', '').replace('www.', '')
                    if clean_url.endswith('/'):
                        clean_url = clean_url[:-1]
                    status_text = f"🌐 {script_name}{separator}{clean_url}"
                else:
                    clean_path = os.path.basename(script_value)
                    status_text = f"📂{script_name}{separator}{clean_path}"

                max_length = 130
                if len(status_text) > max_length:
                    status_text = status_text[:max_length - 3] + "..."

                self.status_bar.setText(status_text)

            if self.is_text_overflow(item) or script_data.get('type') == 'merge':
                if script_data.get('type') == 'merge':
                    sub_scripts = script_data.get('value', [])
                    tooltip = "\n".join(
                        f"{i + 1}. {s['name']} ({s['type']}: {s['value']})"
                        for i, s in enumerate(sub_scripts)
                    )
                else:
                    tooltip = script_value
                self.setToolTip(tooltip)
            else:
                self.setToolTip("")
        else:
            self.status_bar.setText(">>> 准备就绪 🚀")
            self.setToolTip("")

        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.current_hover_item = None
        self.setToolTip("")
        self.status_bar.setText(">>> 准备就绪🚀")
        super().leaveEvent(event)


class ScrollingItemDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)
        self.list_widget = parent
        self.even_color = parent.palette().base().color()  # 从样式表获取基础色
        self.odd_color = self.even_color.darker(105)  # 稍微变暗


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