import sys
from PyQt5.QtWidgets import QWidget, QLabel, QGraphicsOpacityEffect, QVBoxLayout, QApplication, QDesktopWidget
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QTimer, QEasingCurve, QPoint
from PyQt5.QtGui import QColor, QFont, QPalette
from datetime import datetime


class WelcomeNotification(QWidget):
    """
    一个浮动在屏幕右下角的欢迎通知窗口。
    该窗口具有从右侧滑入的动态效果，并在几秒后自动消失。
    """

    def __init__(self, parent=None, message="欢迎使用！", is_night_mode=False, display_duration=5000):
        """
        初始化欢迎通知窗口。

        Args:
            parent (QWidget): 父窗口，用于定位通知窗口的位置。
            message (str): 通知窗口中显示的欢迎文本。
            is_night_mode (bool): 是否启用夜间模式。
            display_duration (int): 通知窗口的显示持续时间（毫秒）。
        """
        super().__init__(parent)
        self.setWindowFlags(
            Qt.SplashScreen |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(300, 100)

        # 如果message是默认值，则自动生成问候语，否则使用传入的message
        if message == "欢迎使用！":
            greeting_message = self.get_greeting()
            current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.message = f"{greeting_message}\n当前时间: {current_time_str}"
        else:
            self.message = message

        # 调整了持续时间，让动画更平滑，显示时间更长
        self.animation_duration = 500  # 动画持续时间（毫秒）
        self.display_duration = display_duration  # 使用传入的显示持续时间

        # 创建并配置标签
        self.label = QLabel(self.message, self)
        self.label.setFont(QFont('Comic Sans MS', 14, QFont.Bold))

        # 根据模式应用样式
        self._apply_style(is_night_mode)

        self.label.setAlignment(Qt.AlignCenter)  # 文本居中对齐

        # 使用布局管理器来确保标签正确填充窗口
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # 创建不透明度效果
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.parent_widget = parent

        # 初始化动画对象
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")

    def set_notification_message(self, message: str):
        """
        方便调用以设置通知窗口的显示文本。

        Args:
            message (str): 需要显示的文本内容。
        """
        self.label.setText(message)

    def get_greeting(self):
        """
        根据当前小时数返回不同的问候语，提供更具体的时辰信息和古代时辰名称，
        并添加日间或夜间模式的提示。
        """
        current_hour = datetime.now().hour
        mode_hint = ""
        greeting_text = ""

        # 根据小时数判断日夜模式
        if 6 <= current_hour < 18:
            mode_hint = "已为你启用日间模式"
        else:
            mode_hint = "以为你启用夜间模式"

        # 子时 (23:00 - 01:00)
        if 23 <= current_hour or current_hour < 1:
            greeting_text = "夜深了，已是子时，请注意休息！"

        # 丑时 (01:00 - 03:00)
        elif 1 <= current_hour < 3:
            greeting_text = "丑时已至，万籁俱寂，安心睡眠。"

        # 寅时 (03:00 - 05:00)
        elif 3 <= current_hour < 5:
            greeting_text = "寅时，黎明将至，请注意休息！"

        # 卯时 (05:00 - 07:00)
        elif 5 <= current_hour < 7:
            greeting_text = "早安！已是卯时，新的一天开始啦！"

        # 辰时 (07:00 - 09:00)
        elif 7 <= current_hour < 9:
            greeting_text = "早上好！辰时已到，准备迎接新挑战"

        # 巳时 (09:00 - 11:00)
        elif 9 <= current_hour < 11:
            greeting_text = "上午好！巳时，工作顺利！"

        # 午时 (11:00 - 13:00)
        elif 11 <= current_hour < 13:
            greeting_text = "干饭时间，已是午时，别忘了吃饭！"

        # 未时 (13:00 - 15:00)
        elif 13 <= current_hour < 15:
            greeting_text = "未时，精神抖擞地继续吧！"

        # 申时 (15:00 - 17:00)
        elif 15 <= current_hour < 17:
            greeting_text = "申时，下午茶时间，放松一下吧。"

        # 酉时 (17:00 - 19:00)
        elif 17 <= current_hour < 19:
            greeting_text = "傍晚好！已是酉时，辛苦了！"

        # 戌时 (19:00 - 21:00)
        elif 19 <= current_hour < 21:
            greeting_text = "戌时，享受你的闲暇时光。"

        # 亥时 (21:00 - 23:00)
        elif 21 <= current_hour < 23:
            greeting_text = "晚安！已是亥时，早点休息。"

        # 默认回退（以防万一）
        else:
            greeting_text = "欢迎回来！"

        return f"{greeting_text}\n{mode_hint}"

    def _apply_style(self, is_night_mode):
        """
        根据日夜模式应用不同的样式。
        """
        if is_night_mode:
            self.label.setStyleSheet("""
                QLabel {
                    border: 0px solid #555555;
                    border-radius: 25px;
                    background-color: #000000;  /* 夜间模式背景色改为不透明的纯黑色 */
                    font-family: 'Comic Sans MS', 'KaiTi', sans-serif;
                    font-size: 16px;
                    font-weight: bold;
                    color: #FFFFFF;  /* 夜间模式文字颜色 */
                    padding: 15px;
                }
            """)
        else:
            self.label.setStyleSheet("""
                QLabel {
                    border: 0px solid #CCCCCC;
                    border-radius: 25px;
                    background-color: #ffffff;  /* 日间模式背景色改为不透明的纯黑色 */
                    font-family: 'Comic Sans MS', 'KaiTi', sans-serif;
                    font-size: 16px;
                    font-weight: bold;
                    color: #000000;  /* 日间模式文字颜色调整为白色 */
                    padding: 15px;
                }
            """)

    def show_animation(self):
        """
        执行通知窗口的显示动画，包括从右侧滑入和淡入。
        """
        # 在动画开始时显示窗口
        self.show()

        if self.parent_widget:
            parent_rect = self.parent_widget.geometry()
        else:
        # 考虑多显示器情况，使用桌面可用区域
            desktop_rect = QApplication.desktop().availableGeometry(QApplication.desktop().screenNumber(self.parent_widget)) if self.parent_widget else QApplication.desktop().availableGeometry()
            parent_rect = desktop_rect

        end_x = parent_rect.x() + parent_rect.width() - self.width() - 20
        end_y = parent_rect.y() + parent_rect.height() - self.height() - 20

        start_x = parent_rect.x() + parent_rect.width()
        start_y = end_y

        self.setGeometry(start_x, start_y, self.width(), self.height())

        self.pos_animation.setDuration(self.animation_duration)
        self.pos_animation.setStartValue(QPoint(start_x, start_y))
        self.pos_animation.setEndValue(QPoint(end_x, end_y))
        self.pos_animation.setEasingCurve(QEasingCurve.OutElastic)  # 更改为 OutElastic 缓动曲线，让动画更具弹性

        self.opacity_animation.setDuration(self.animation_duration)
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)

        self.pos_animation.start()
        self.opacity_animation.start()

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_animation)
        self.hide_timer.start(self.display_duration)

    def hide_animation(self):
        """
        执行通知窗口的隐藏动画，包括淡出和滑出。
        """
        if self.hide_timer.isActive():
            self.hide_timer.stop()

        start_pos = self.pos()
        # 隐藏时滑出到屏幕右侧
        end_x = QApplication.desktop().availableGeometry().x() + QApplication.desktop().availableGeometry().width()
        end_y = self.y()

        self.pos_animation.setDuration(self.animation_duration)
        self.pos_animation.setStartValue(start_pos)
        self.pos_animation.setEndValue(QPoint(end_x, end_y))
        self.pos_animation.setEasingCurve(QEasingCurve.InQuint)  # 更改为 InQuint 缓动曲线，让动画平滑加速滑出
        self.pos_animation.finished.connect(self.close)

        self.opacity_animation.setDuration(self.animation_duration)
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(0.0)

        self.pos_animation.start()
        self.opacity_animation.start()