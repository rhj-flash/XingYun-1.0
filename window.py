import hashlib
import sys
import os
import weakref
from PyQt5.QtGui import QPainterPath, QImage, QLinearGradient
import threading  # 确保导入 threading 模块
from datetime import datetime
from urllib.parse import urlparse, urljoin

from PyQt5.QtGui import QColor, QBrush, QFontMetrics, QPalette, QPixmap, QPainterPath
from PyQt5.QtCore import Qt, QStringListModel, QTranslator, QCoreApplication, QPropertyAnimation, QPoint, QEvent, \
    QTimer, QObject, QRectF
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget,
    QLineEdit, QCompleter, QTextEdit, QPushButton, QFileDialog, QMessageBox,
    QInputDialog, QDialog, QListWidgetItem, QDesktopWidget, QMenu, QSizePolicy, QStyledItemDelegate,
    QStyleOptionViewItem, QStyle, QDialogButtonBox, QGridLayout, QToolButton, QScrollArea, QFrame, QAction
)
from PyQt5.QtCore import QRect, QEasingCurve
from PyQt5.uic.properties import QtCore
from attr import has
from bs4 import BeautifulSoup

from function import *
from PyQt5.QtCore import QVariantAnimation, QEasingCurve
from PyQt5.QtGui import QFontMetrics, QPainter
from PyQt5.QtWidgets import QGroupBox
from selenium import webdriver

#    EXE打包指令
"""
=======================
PyInstaller打包配置说明
=======================

使用以下命令进行打包（PowerShell格式）：

pyinstaller --noconsole --onefile --name Xingyun `
    --clean `
    --icon="resources/icon.ico" `
    --add-data "resources/english_words.txt;resources" `
    --add-data "resources/icon.ico;resources" `
    --add-data "resources/*;resources" `
    window.py
"""

# 日间模式样式
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
        margin: 0px;  /* 解决错位问题    右侧滚动条*/
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
    /* 对 QListWidget 整体进行样式设置 */
    QListWidget {
        border: 1px solid #CCCCCC;  /* 设置列表控件的边框宽度为 1 像素，颜色为浅灰色 */
        border-radius: 8px;  /* 设置列表控件的边框圆角半径为 8 像素，使其边角更圆润 */
        background-color: #F5F5F5;  /* 设置列表控件的背景颜色为淡淡的灰色 */
        font-size: 14px;  /* 设置列表控件内文本的字体大小为 14 像素 */
        color: #444444;  /* 设置列表控件内文本的颜色为深灰色 */
    }
    /* 对 QListWidget 中的每个列表项进行样式设置 */
    QListWidget::item {
        padding: 10px;  /* 设置列表项的内边距为 10 像素，使内容与边框有一定间隔 */
        white-space: nowrap;  /* 设置列表项内的文本不自动换行，保持单行显示 */
    }
    /* 对鼠标悬停在 QListWidget 列表项上时的样式进行设置 */
    QListWidget::item:hover {
        background-color: #C0C0C0;  /* 当鼠标悬停时，列表项的背景颜色变为中灰色 */
        border-radius: 8px;  /* 当鼠标悬停时，列表项的边框圆角半径为 8 像素 */
    }
    /* 对 QListWidget 中被选中的列表项进行样式设置 */
    QListWidget::item:selected {
        background-color: #A0A0A0;  /* 被选中的列表项背景颜色变为深一些的灰色 */
        color: #000000;  /* 被选中的列表项文本颜色变为黑色 */
        font-weight: bold;  /* 被选中的列表项文本字体加粗 */
    }
    /* 对 QListWidget 列表项获得焦点时的样式进行设置，这里去除了默认的焦点轮廓 */
    QListWidget::item:focus {
        outline: none;
    }
    /* 对 QListWidget 控件本身获得焦点时的样式进行设置，同样去除了默认的焦点轮廓 */
    QListWidget:focus {
        outline: none;
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
        border-radius: 25px;
        padding: 5px;
        font-size: 23px;
        font-weight: bold;  /* 输入字体加粗 */
        min-width: 100px;
        height:70px;
        background-color: #F5F5F5;
        color: #444444;
        
    }
    QLineEdit:focus {
        border: 3px solid #A0A0A0;
        background-color: #F5F5F5;
    }
    QLineEdit::placeholder {
        color: #888888;
        font-size: 18px;
        font-style: italic;  /* 提示文字保持斜体 */
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
    QMainWindow, QWidget {
        background-color: #F0F2F5;  /* 统一主窗口和所有子部件背景 */
    }
    QSplitter {
        background-color: #F0F2F5;  /* 确保分割器背景一致 */
    }
    QSplitter::handle {
        background-color: #F0F2F5;  /* 分割器手柄背景 */
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
# 夜间模式样式
# 定义显示区域的样式表
display_area_style_night = """
    QTextEdit {
        border: 1px solid #555555;
        border-radius: 8px;
        background-color: #111111;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        color: #EEEEEE;
        padding: 10px;
    }
    QScrollBar:vertical, QScrollBar:horizontal {
        border: none;
        background: #222222;
        width: 10px;
        height: 10px;
        margin: 0px;  /* 解决错位问题 */
        border-radius: 5px;
    }
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
        background: #777777;
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
    /* 对 QListWidget 整体进行样式设置，用于夜间模式 */
    QListWidget {
        border: 1px solid #555555;  /* 设置列表控件的边框宽度为 1 像素，颜色为深灰色 */
        border-radius: 8px;  /* 设置列表控件的边框圆角半径为 8 像素，使边角呈现圆润效果 */
        background-color: #222222;  /* 将列表控件的背景颜色设置为深灰色，适配夜间模式 */
        font-size: 14px;  /* 设置列表控件内文本的字体大小为 14 像素 */
        color: #EEEEEE;  /* 设置列表控件内文本的颜色为浅灰色，在深色背景下更易读 */
    }
    /* 对 QListWidget 中的每个列表项进行样式设置 */
    QListWidget::item {
        padding: 10px;  /* 设置列表项的内边距为 10 像素，使列表项内的内容与边框有一定间隔 */
        white-space: nowrap;  /* 使列表项内的文本不自动换行，保持单行显示 */
    }
    /* 对鼠标悬停在 QListWidget 列表项上时的样式进行设置 */
    QListWidget::item:hover {
        background-color: #444444;  /* 当鼠标悬停在列表项上时，背景颜色变为稍浅一些的深灰色 */
        border-radius: 8px;  /* 鼠标悬停时，列表项的边框圆角半径保持为 8 像素 */
    }
    /* 对 QListWidget 中被选中的列表项进行样式设置 */
    QListWidget::item:selected {
        background-color: #555555;  /* 被选中的列表项背景颜色变为更深一点的灰色 */
        color: #FFFFFF;  /* 被选中的列表项文本颜色设置为白色，突出显示 */
        font-weight: bold;  /* 被选中的列表项文本字体加粗，进一步强调选中状态 */
    }
    /* 对 QListWidget 列表项获得焦点时的样式进行设置，去除默认的焦点轮廓 */
    QListWidget::item:focus {
        outline: none;
    }
    /* 对 QListWidget 控件本身获得焦点时的样式进行设置，去除默认的焦点轮廓 */
    QListWidget:focus {
        outline: none;
    }
"""

dialog_style_night = """
QDialog {
    background-color: #222222;  /* 深灰色背景 */
    border-radius: 15px;  /* 圆角 */
    padding: 30px;  /* 内边距 */
}
QLabel {
    font-size: 20px;  /* 标签字体大小 */
    color: #EEEEEE;  /* 标签字体颜色 */
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

search_edit_style_night = """
    QLineEdit {
        border: 1px solid #555555;
        border-radius: 25px;
        padding: 5px;
        font-size: 23px;
        font-weight: bold;  /* 输入字体加粗 */
        min-width: 100px;
        height:70px;
        background-color: #222222;
        color: #EEEEEE;
    }
    QLineEdit:focus {
        border: 3px solid #777777;
        background-color: #222222;
    }
    QLineEdit::placeholder {
        color: #AAAAAA;
        font-size: 18px;
        font-style: italic;  /* 提示文字保持斜体 */
    }
"""

completer_popup_style_night = """
    QListView {
        font-size: 18px;  /* 调整字体大小 */
        padding: 8px;
        min-width: 300px;  /* 增加最小宽度 */
        min-height: 250px;  /* ✅ 增加预览框的最小高度 */
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
    QTextEdit {
        border: 1px solid #555555;
        border-radius: 8px;
        background-color: #111111;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        color: #EEEEEE;
        padding: 10px;
    }
    QScrollBar:vertical, QScrollBar:horizontal {
        border: none;
        background: #222222;
        width: 10px;
        height: 10px;
        margin: 0px;  /* 解决错位问题 */
        border-radius: 5px;
    }
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
        background: #777777;
        min-height: 20px;
        min-width: 20px;
        border-radius: 5px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        background: none;
    }

"""

button_style_night = """
    QPushButton {
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                          stop:0 rgba(80, 80, 80, 1), stop:1 rgba(40, 40, 40, 1));
        border: 1px solid #555555;
        border-radius: 8px;
        color: #FFFFFF;  /* 更亮的文本颜色 */
        font-size: 16px;
        font-weight: bold;
        padding: 12px 25px;
        text-align: center;
        text-decoration: none;
        margin: 4px 2px;
        box-shadow: 3px 3px 5px rgba(0, 0, 0, 0.3);
    }

    QPushButton:hover {
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                          stop:0 rgba(40, 40, 40, 1), stop:1 rgba(20, 20, 20, 1));
        border: 1px solid #444444;
    }

    QPushButton:pressed {
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                          stop:0 rgba(20, 20, 20, 1), stop:1 rgba(10, 10, 10, 1));
        border: 1px solid #333333;
        box-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
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
    animation = QPropertyAnimation(search_edit, b"minimumHeight")
    animation.setDuration(700)  # 动画时长 300 毫秒
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


def create_main_window():
    global status_bar, list_widget, search_edit, completer_model, display_area
    global create_script_button, remove_selected_button, clear_button, update_log_button
    global english_mode, english_learn_button, original_english_btn_style, night_mode_button
    global left_widget  # 声明为全局变量
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
    if os.path.exists(icon_path):
        main_window.setWindowIcon(QIcon(icon_path))
    else:
        main_window.setWindowIcon(QIcon.fromTheme("application-x-executable"))

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

    # 添加夜间模式按钮（初始化为太阳图标）
    night_mode_button = QPushButton("  ☀️  ")  # 修改为太阳图标
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
    try:
        night_mode_button.clicked.disconnect()
    except Exception:
        pass
    night_mode_button.clicked.connect(toggle_night_mode)
    night_mode_button.setStyleSheet(night_mode_button_style)
    night_mode_button.setFixedSize(32, 32)

    # 状态栏容器
    status_container = QWidget()
    status_layout = QHBoxLayout(status_container)
    status_layout.addWidget(status_bar)
    status_layout.addWidget(night_mode_button)
    status_layout.addWidget(english_learn_button)
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
    search_edit.setPlaceholderText(tr('🔍脚本名称/单词'))
    search_edit.setStyleSheet(search_edit_style)
    completer_items = []
    completer_model = QStringListModel(completer_items)
    completer = QCompleter(completer_model)
    completer.setFilterMode(Qt.MatchContains)
    completer.setCaseSensitivity(Qt.CaseInsensitive)
    search_edit.textChanged.connect(lambda text: filter_list_widget(list_widget, text))

    # 左侧布局
    left_layout = QVBoxLayout()
    left_layout.addWidget(search_edit)
    left_layout.addWidget(list_widget)
    left_widget = QWidget()  # 赋值给全局变量
    left_widget.setLayout(left_layout)
    left_widget.setStyleSheet(left_widget_style)

    # 显示区域
    display_area = QTextEdit()
    display_area.setReadOnly(True)
    display_area.setStyleSheet(display_area_style)

    # 按钮布局
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
    night_mode_button.enterEvent = lambda event: update_status_bar("🌙 夜间模式")

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
    global night_mode, main_window, english_learn_button, night_mode_button, status_bar
    global list_widget, search_edit, display_area, create_script_button, remove_selected_button, clear_button, update_log_button
    global original_english_btn_style, left_widget, display_area_style_night
    global list_widget_style_night, search_edit_style_night, main_window_style_night, left_widget_style_night, button_style_night

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
                background-color: #000000;  /* 纯黑背景 */
                color: #FFFFFF;
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
        night_mode_button.setText("  🌙  ")  # 切换为月亮图标
        status_bar.setStyleSheet("""
            font-size: 12px;
            color: #EEEEEE;
            padding: 2px 8px;
            border-top: 1px solid #555555;
            background-color: #000000;  /* 与夜间模式主窗口一致 */
        """)
    else:
        night_mode = False
        main_window.setStyleSheet(main_window_style)
        list_widget.setStyleSheet(list_widget_style)
        search_edit.setStyleSheet(search_edit_style)
        display_area.setStyleSheet(display_area_style)
        left_widget.setStyleSheet(left_widget_style)
        create_script_button.setStyleSheet(button_style)
        remove_selected_button.setStyleSheet(button_style)
        clear_button.setStyleSheet(button_style)
        update_log_button.setStyleSheet(button_style)
        night_mode_button.setText("  ☀️  ")  # 切换回太阳图标
        status_bar.setStyleSheet("""
            font-size: 12px;
            color: #444444;
            padding: 2px 8px;
            border-top: 1px solid #CCCCCC;
            background-color: #F0F2F5;  /* 与日间模式主窗口一致 */
        """)
        # 恢复搜索框高度
        animate_search_edit_height(50 if not english_mode else 250)

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
    word_file = ensure_word_file()
    if not word_file:
        return []

    try:
        with open(word_file, 'r', encoding='utf-8') as f:
            word_dict = {}
            for line in f:
                parts = line.strip().split(maxsplit=1)  # 只分割第一个空格
                if len(parts) == 2:
                    word_dict[parts[0].lower()] = parts[1]

            # 简单模糊匹配
            matches = [{'word': w, 'translation': t}
                       for w, t in word_dict.items()
                       if word.lower() in w]

            # 按单词长度排序（更短的匹配更准确）
            matches.sort(key=lambda x: len(x['word']))
            return matches[:top_n]
    except Exception as e:
        print(f"查询单词错误: {e}")
        return []


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
                font: bold 12px;  /* 可选：设置字体大小和粗细 */
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
                font: bold 12px;  /* 可选：设置字体大小和粗细 */
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
        preview_group = QGroupBox("执行顺序预览")
        preview_group.setStyleSheet("""
            QGroupBox {
                color: black;  /* 设置字体颜色为红色 */
                font: bold 12px;  /* 可选：设置字体大小和粗细 */
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
        """设置按钮的统一样式"""
        button_style = """
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                                stop:0 rgba(180, 180, 180, 1), 
                                                stop:1 rgba(140, 140, 140, 1));
                border: 1px solid #BBBBBB;
                border-radius: 8px;
                color: #000000;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 12px;
                min-width: 100px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                                stop:0 rgba(160, 160, 160, 1),
                                                stop:1 rgba(120, 120, 120, 1));
                border: 1px solid #AAAAAA;
            }
            QPushButton:pressed {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                                                stop:0 rgba(140, 140, 140, 1),
                                                stop:1 rgba(100, 100, 100, 1));
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
        self.preview.setFont(QFont("Consolas", 10))  # 仍然使用等宽字体保证对齐

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
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # 获取当前项
        item = self.list_widget.item(index.row())
        if not item:
            painter.restore()
            return

        # 检查是否为悬停状态
        item_id = item.data(Qt.UserRole)
        is_hovered = item_id in self.hover_states

        # 获取悬停动画进度
        progress = self.hover_states.get(item_id, 0.0)
        eased_progress = self.ease_animation(progress)

        # 确定背景颜色
        if option.state & QStyle.State_Selected:
            bg_color = self.selected_color
        elif index.row() % 2 == 0:
            bg_color = self.even_color
        else:
            bg_color = self.odd_color

        # 如果是悬停状态，混合颜色
        if is_hovered:
            bg_color = self.mix_colors(bg_color, self.hover_color, eased_progress)

        # 悬停动画参数配置
        max_offset = 3  # 卡片向右滑动的最大像素距离
        scale = 1.0 + 0.05 * eased_progress  # 轻微放大效果，增加“弹出”感
        rotation = 15 * eased_progress  # 旋转角度，最大1.5度
        shadow_opacity = 0.3 + 0.2 * eased_progress  # 动态阴影透明度

        # 获取原始项矩形区域
        original_rect = option.rect

        # 应用悬停变换
        transformed_rect = QRectF(original_rect)
        if is_hovered:
            # 计算偏移量
            offset = max_offset * eased_progress
            transformed_rect.translate(offset, 0)

            # 计算缩放中心
            center = transformed_rect.center()

            # 应用缩放和旋转
            painter.translate(center)
            painter.rotate(rotation)
            painter.scale(scale, scale)
            painter.translate(-center)

            # 绘制阴影
            shadow_color = self.shadow_color
            shadow_color.setAlphaF(shadow_opacity)
            painter.setPen(Qt.NoPen)
            painter.setBrush(shadow_color)
            shadow_offset = 3  # 阴影偏移量
            shadow_rect = transformed_rect.translated(shadow_offset, shadow_offset)
            painter.drawRoundedRect(shadow_rect, 10, 10)

        # 绘制背景
        painter.setPen(Qt.NoPen)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(transformed_rect, 10, 10)

        # 绘制图标
        icon_size = 24
        icon = item.icon()
        icon_rect = QRect(int(transformed_rect.left() + 8),
                          int(transformed_rect.center().y() - icon_size / 2),
                          icon_size, icon_size)
        icon.paint(painter, icon_rect, Qt.AlignCenter)

        # 绘制文本
        text = item.text()
        font = painter.font()
        font.setPointSize(12)  # 固定字体大小
        painter.setFont(font)
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(text)
        available_width = transformed_rect.width() - 35

        # 获取滚动数据
        scroll_data = item.data(Qt.UserRole + 1)
        offset = scroll_data[0] if scroll_data else 0

        # 设置文本颜色
        text_color = option.palette.color(QPalette.Text)
        if option.state & QStyle.State_Selected:
            text_color = self.selected_text_color
        if is_hovered:
            if self.night_mode:
                text_color = QColor("#000000")  # 夜间模式悬停时字体为黑色
            else:
                text_color = text_color.lighter(120)

        painter.setPen(text_color)

        # 绘制文本区域
        text_rect = QRect(transformed_rect.toRect())
        text_rect.setLeft(int(transformed_rect.left() + 35))
        text_rect.setWidth(int(available_width))

        if text_width > available_width:
            painter.setClipRect(text_rect)
            adjusted_rect = QRect(text_rect)
            adjusted_rect.translate(-offset, 0)
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

        # 悬停动画参数配置
        max_offset = 3  # 卡片向右滑动的最大像素距离
        scale = 1.0 + 0.05 * eased_progress  # 轻微放大效果，增加“弹出”感
        rotation = 7 * eased_progress  # 旋转角度，最大1.5度
        shadow_opacity = 0.3 + 0.2 * eased_progress  # 动态阴影透明度

        # 获取原始项矩形区域
        original_rect = option.rect

        # 应用悬停变换
        transformed_rect = QRectF(original_rect)
        if is_hovered:
            pivot_x = original_rect.center().x()  # 修改旋转圆心为选项左侧
            pivot_y = original_rect.center().y()

            # 使用浮点数偏移以确保平滑动画
            offset_x = max_offset * eased_progress
            offset_y = 0 * eased_progress  # 轻微垂直提升
            # 优化变换顺序以减少渲染开销
            painter.translate(pivot_x + offset_x, pivot_y + offset_y)
            painter.scale(scale, scale)
            painter.rotate(rotation)
            painter.translate(-pivot_x, -pivot_y)

            transformed_rect = QRectF(original_rect).translated(offset_x, offset_y)

        # 绘制阴影（仅在悬停时）
        if is_hovered:
            shadow_path = QPainterPath()
            shadow_rect = QRectF(transformed_rect.adjusted(4, 4, -4, -4))
            shadow_path.addRoundedRect(shadow_rect, 19, 19)
            shadow_color = self.shadow_color
            shadow_color.setAlphaF(shadow_opacity)
            painter.setPen(Qt.NoPen)
            painter.setBrush(shadow_color)
            painter.drawPath(shadow_path)

        # 绘制圆角背景
        path = QPainterPath()
        radius = 19
        rect_f = QRectF(transformed_rect.adjusted(2, 2, -2, -2))
        path.addRoundedRect(rect_f, radius, radius)

        # 应用渐变背景
        gradient = QLinearGradient(rect_f.topLeft(), rect_f.bottomRight())
        gradient.setColorAt(0, bg_color.lighter(110))
        gradient.setColorAt(1, bg_color.darker(105))
        painter.setPen(Qt.NoPen)
        painter.fillPath(path, gradient)

        # 恢复画家状态以绘制图标和文本（避免旋转影响）
        painter.restore()
        painter.save()

        # 绘制图标
        icon = item.icon()
        if not icon.isNull():
            icon_rect = QRect(
                int(transformed_rect.left() + 8),
                int(transformed_rect.top() + (transformed_rect.height() - 20) / 2),
                20, 20
            )
            icon.paint(painter, icon_rect, Qt.AlignCenter)

        # 绘制文本
        text = item.text()
        font = option.font
        font.setPointSize(12)  # 固定字体大小
        painter.setFont(font)
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(text)
        available_width = transformed_rect.width() - 35

        # 获取滚动数据
        scroll_data = item.data(Qt.UserRole + 1)
        offset = scroll_data[0] if scroll_data else 0

        # 设置文本颜色
        text_color = option.palette.color(QPalette.Text)
        if option.state & QStyle.State_Selected:
            text_color = self.selected_text_color
        if is_hovered:
            if self.night_mode:
                text_color = QColor("#000000")  # 夜间模式悬停时字体为黑色
            else:
                text_color = text_color.lighter(120)

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
