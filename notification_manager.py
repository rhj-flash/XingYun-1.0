# notification_manager.py
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QEasingCurve, QPoint
from PyQt5.QtGui import QIcon
from datetime import datetime
# 导入具体的通知窗口类，这是单向依赖
from notification import WelcomeNotification

# 创建一个全局的通知管理器实例，确保它在整个应用生命周期中只被创建一次
notification_manager = None


def get_notification_manager():
    """
    获取或创建全局的通知管理器实例。
    """
    global notification_manager
    if notification_manager is None:
        notification_manager = NotificationManager()
    return notification_manager


def show_greeting_notification(icon=None):
    """
    专门用于显示问候通知的函数。

    Args:
        icon (QIcon): 可选的通知图标。
    """
    # 获取问候语和模式
    current_hour = datetime.now().hour
    is_night_mode = not (6 <= current_hour < 18)

    greeting = NotificationManager.get_greeting()
    full_message = f"{greeting}"

    # 使用管理器来显示问候通知，问候通知的显示时间可以稍长一些
    manager = get_notification_manager()
    manager.show_notification(full_message, is_night_mode=is_night_mode, display_duration=8000, icon=icon)

    print("问候通知已调用。")


def show_custom_notification(message: str, display_duration: int = 5000, icon=None):
    """
    显示一个自定义内容的通知窗口。
    此函数将根据当前时间自动确定日夜模式。

    Args:
        message (str): 通知窗口需要显示的文本内容。
        display_duration (int): 通知窗口的显示持续时间（毫秒），默认为 5000。
        icon (QIcon): 可选的通知图标。
    """
    # 如果没有 QApplication 实例，则创建一个
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    # 根据当前时间自动确定日夜模式
    current_hour = datetime.now().hour
    is_night_mode = not (6 <= current_hour < 18)

    # 检查传入的icon参数，如果是一个文件路径字符串，则创建 QIcon 对象
    if isinstance(icon, str):
        icon = QIcon(icon)

    # 使用管理器来显示自定义通知
    manager = get_notification_manager()
    manager.show_notification(message, is_night_mode=is_night_mode, display_duration=display_duration, icon=icon)

    # 打印调试信息，确认函数被调用
    print("自定义通知已调用，内容为：", message)


class NotificationManager:
    """
    一个用于管理所有通知窗口的管理器，实现堆叠和位置更新功能。
    """

    def __init__(self):
        self.active_notifications = []
        self.notification_gap = 5  # 通知之间的垂直间距
        self._reposition_timer = QTimer()
        self._reposition_timer.setSingleShot(True)
        self._reposition_timer.timeout.connect(self.reposition_notifications)

    def show_notification(self, message: str, is_night_mode: bool, display_duration: int = 5000, icon=None):
        """
        创建一个新的通知窗口并显示。
        当有新通知出现时，会缩短所有现有通知的显示时间，以确保正确的消失顺序。

        Args:
            message (str): 通知窗口需要显示的文本内容。
            is_night_mode (bool): 是否启用夜间模式。
            display_duration (int): 通知窗口的显示持续时间（毫秒）。
            icon (QIcon): 可选的通知图标。
        """
        desktop = QApplication.desktop()
        desktop_rect = desktop.availableGeometry()

        # 硬性限制通知数量最多为5个
        max_notifications = 2
        if len(self.active_notifications) >= max_notifications:
            oldest_notification = self.active_notifications.pop(0)
            oldest_notification.close_notification()
            # 在移除旧通知后立即重新定位，为新通知腾出空间
            self.reposition_notifications()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 达到最大通知数量({max_notifications})，移除最旧的通知。")

        # 调整所有现有通知的消失时间，使其在下一个通知出现后依次消失
        # 新通知的显示时间 = 动画时间 + 延迟时间
        new_notification_show_duration = display_duration + 500
        # 缩短现有通知的显示时间，使其比新通知的显示时间短
        # 这里设置为新通知显示时间的一半，或者一个固定较短的时间
        shortened_duration = new_notification_show_duration // 2

        # 遍历现有通知，并缩短它们的显示时间
        for notification in self.active_notifications:
            notification.update_hide_timer(shortened_duration)

        # 计算新通知的最终位置
        new_notification_y = desktop_rect.y() + desktop_rect.height() - 100 - 20
        for notification in reversed(self.active_notifications):
            new_notification_y -= notification.height() + self.notification_gap

        # 创建 WelcomeNotification 实例，并连接其信号
        new_notification = WelcomeNotification(message=message, is_night_mode=is_night_mode,
                                               display_duration=display_duration, icon=icon)
        new_notification.closed.connect(self.on_notification_closed)
        self.active_notifications.append(new_notification)

        new_notification.show_animation(new_notification_y)

        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] 新通知已创建，内容: '{message}', 当前共有 {len(self.active_notifications)} 个活跃通知。")

    def on_notification_closed(self, notification):
        """
        当一个通知关闭时，从列表中移除它并安排重新定位。
        使用 QTimer 确保在一次事件循环中处理所有关闭事件，避免频繁重新定位。
        """
        try:
            self.active_notifications.remove(notification)
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] 通知已关闭，当前剩余 {len(self.active_notifications)} 个活跃通知。")
            if not self._reposition_timer.isActive():
                self._reposition_timer.start(50)  # 延迟50毫秒重新定位，让所有关闭事件都能被处理
        except ValueError:
            pass

    def reposition_notifications(self):
        """
        重新计算并更新所有活跃通知的位置。
        这个函数会从屏幕底部开始向上计算，确保堆叠的稳定性和对齐。
        """
        if not self.active_notifications:
            return

        desktop = QApplication.desktop()
        desktop_rect = desktop.availableGeometry()

        # 从底部开始计算位置，初始y坐标是底部边距
        current_y = desktop_rect.y() + desktop_rect.height() - 20

        # 从最底部（列表中最后一个）通知开始向上堆叠
        for notification in reversed(self.active_notifications):
            # 计算当前通知的新位置
            new_y = current_y - notification.height()

            # 如果位置有变化，则执行动画
            if abs(notification.y() - new_y) > 1:
                notification.pos_animation.stop()
                notification.pos_animation.setDuration(300)  # 快速重新定位
                notification.pos_animation.setStartValue(notification.pos())
                notification.pos_animation.setEndValue(QPoint(notification.x(), new_y))
                notification.pos_animation.setEasingCurve(QEasingCurve.OutQuad)
                notification.pos_animation.start()

            # 更新下一个通知的起始y坐标，为下一个通知留出空间
            current_y = new_y - self.notification_gap

    @staticmethod
    def get_greeting():
        """
        根据当前小时数返回不同的问候语，提供更具体的时辰信息和古代时辰名称，
        并添加日间或夜间模式的提示。
        """
        current_hour = datetime.now().hour
        mode_hint = " 已为您启用日间模式 " if 6 <= current_hour < 18 else " 已为您启用夜间模式 "

        if 23 <= current_hour or current_hour < 1:
            greeting_text = "夜深了，已是子时，请注意休息！"
        elif 1 <= current_hour < 3:
            greeting_text = "丑时已至，万籁俱寂，请注意休息！"
        elif 3 <= current_hour < 5:
            greeting_text = "寅时，黎明将至，请注意休息！"
        elif 5 <= current_hour < 7:
            greeting_text = "早安！已是卯时，新的一天开始啦！"
        elif 7 <= current_hour < 9:
            greeting_text = "早上好！辰时已到，准备迎接新挑战"
        elif 9 <= current_hour < 11:
            greeting_text = "上午好！巳时，工作顺利！"
        elif 11 <= current_hour < 13:
            greeting_text = "干饭时间，已是午时，别忘了吃饭！"
        elif 13 <= current_hour < 15:
            greeting_text = "未时，精神抖擞地继续吧！"
        elif 15 <= current_hour < 17:
            greeting_text = "申时，下午茶时间，放松一下吧。"
        elif 17 <= current_hour < 19:
            greeting_text = "傍晚好！已是酉时，辛苦了！"
        elif 19 <= current_hour < 21:
            greeting_text = "戌时，享受你的闲暇时光。"
        elif 21 <= current_hour < 23:
            greeting_text = "晚安！已是亥时，早点休息。"
        else:
            greeting_text = "欢迎回来！"

        return f"{greeting_text}{mode_hint}"


# 示例用法
if __name__ == "__main__":
    # 如果没有 QApplication 实例，则创建一个
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    # 示例1：程序启动时显示问候通知
    show_greeting_notification()

    # 示例2：创建一个计时器来连续发送多个自定义通知，以测试堆叠功能
    timer = QTimer()
    notifications_to_send = [
        "这是一个自定义的测试通知！",
        "你好，这是第二个通知！",
        "这是第三个通知，夜间模式！",
        "又来了一个新通知，看看堆叠效果。",
    ]


    def send_next_notification():
        if notifications_to_send:
            message = notifications_to_send.pop(0)
            show_custom_notification(message, display_duration=5000)
        else:
            timer.stop()


    timer.timeout.connect(send_next_notification)
    timer.start(2000)  # 每2秒发送一个自定义通知

    # 保持事件循环运行
    sys.exit(app.exec_())