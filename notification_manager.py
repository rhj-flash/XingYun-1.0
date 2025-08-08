# notification_manager.py
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from datetime import datetime

# 导入你现有的 WelcomeNotification 类
from notification import WelcomeNotification


def show_custom_notification(message: str, is_night_mode: bool = False):
    """
    显示一个自定义内容的通知窗口。

    Args:
        message (str): 通知窗口需要显示的文本内容。
        is_night_mode (bool): 是否启用夜间模式，默认为 False。
    """
    # 如果没有 QApplication 实例，则创建一个
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    # 创建 WelcomeNotification 实例
    notification = WelcomeNotification(is_night_mode=is_night_mode)

    # 设置通知文本
    notification.set_notification_message(message)

    # 显示动画
    notification.show_animation()

    # 为了防止程序在通知显示前就退出，需要保持事件循环运行
    # 但我们不能阻塞主事件循环，所以这里不调用 app.exec_()

    # 打印调试信息，确认函数被调用
    print("通知已调用，内容为：", message)


# 示例用法
if __name__ == "__main__":
    # 示例1：显示一个简单的自定义消息
    show_custom_notification("这是一个自定义的测试通知！")

    # 示例2：显示夜间模式的问候语
    current_hour = datetime.now().hour
    if 6 <= current_hour < 18:
        mode_hint = "启用日间模式"
    else:
        mode_hint = "启用夜间模式"

    # 这里我们模拟调用 get_greeting 函数
    # 注意：你需要自己导入 WelcomeNotification 类并调用其方法来获取问候语
    from notification import WelcomeNotification

    temp_notification = WelcomeNotification()
    greeting = temp_notification.get_greeting()

    full_message = f"{greeting}\n当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    show_custom_notification(full_message, is_night_mode=True)

    sys.exit(QApplication.instance().exec_())