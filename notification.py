# notification.py
import datetime
import sys
from PyQt5.QtWidgets import QWidget, QLabel, QGraphicsOpacityEffect, QHBoxLayout, QApplication
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QTimer, QEasingCurve, QPoint, pyqtSignal, QRectF
from PyQt5.QtGui import QColor, QFont, QPalette, QIcon, QPixmap, QPainter, QPainterPath



class WelcomeNotification(QWidget):
    """
    一个浮动在屏幕右下角的欢迎通知窗口。
    该窗口具有从右侧滑入的动态效果，并在几秒后自动消失，支持显示图标。
    """
    closed = pyqtSignal(object)  # 发送自身实例作为参数的信号

    def __init__(self, parent=None, message="", is_night_mode=False, display_duration=5000, icon=None):
        """
        初始化欢迎通知窗口。

        Args:
            parent (QWidget): 父窗口，用于定位通知窗口的位置。
            message (str): 通知窗口中显示的欢迎文本。
            is_night_mode (bool): 是否启用夜间模式。
            display_duration (int): 通知窗口的显示持续时间（毫秒）。
            icon (QIcon): 显示在通知窗口中的图标（可选）。
        """
        super().__init__(parent)
        self.setWindowFlags(
            Qt.SplashScreen |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.message = message
        self.icon = icon
        self.animation_duration = 500
        self.display_duration = display_duration

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        # --- 【核心修改】在这里调用新的圆角处理方法 ---
        self.icon_label = QLabel(self)
        if self.icon and not self.icon.isNull():
            pixmap = self.icon.pixmap(48, 48)
            # 调用辅助函数创建带圆角的pixmap
            rounded_pixmap = self._create_rounded_pixmap(pixmap, 48, 9)  # 48x48尺寸，12px圆角
            self.icon_label.setPixmap(rounded_pixmap)

        self.icon_label.setFixedSize(48, 48)
        self.icon_label.setAlignment(Qt.AlignCenter)
        # --- 修改结束 ---

        self.text_label = QLabel(self.message, self)
        self.text_label.setFont(QFont('Comic Sans MS', 14, QFont.Bold))
        self.text_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self._apply_style(is_night_mode)

        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.text_label)
        self.layout.addStretch()
        self.setLayout(self.layout)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.parent_widget = parent

        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")

    # --- 【核心修改】新增一个私有方法来处理图片圆角 ---
    def _create_rounded_pixmap(self, source_pixmap: QPixmap, size: int, radius: int) -> QPixmap:
        """
        创建一个带有圆角的Pixmap副本。

        Args:
            source_pixmap (QPixmap): 原始的Pixmap图像。
            size (int): 目标尺寸（宽度和高度）。
            radius (int): 圆角半径。

        Returns:
            QPixmap: 处理后带有圆角的Pixmap。
        """
        if source_pixmap.isNull():
            return QPixmap()

        # 确保源图像尺寸正确，并保持高质量缩放
        source_pixmap = source_pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # 创建一个透明的画布
        rounded = QPixmap(source_pixmap.size())
        rounded.fill(Qt.transparent)

        # 使用QPainter在画布上绘制圆角图像
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)  # 开启抗锯齿

        # 创建一个圆角矩形路径
        path = QPainterPath()
        path.addRoundedRect(QRectF(rounded.rect()), radius, radius)

        # 将路径设置为裁剪区域
        painter.setClipPath(path)

        # 在裁剪区域内绘制原始图像
        painter.drawPixmap(0, 0, source_pixmap)
        painter.end()

        return rounded
    # --- 新增方法结束 ---

    def set_notification_message(self, message: str, icon=None):
        """
        设置通知窗口的显示文本和图标。

        Args:
            message (str): 需要显示的文本内容。
            icon (QIcon): 需要显示的图标（可选）。
        """
        self.message = message
        self.text_label.setText(message)

        # --- 【核心修改】在这里也调用圆角处理 ---
        if icon and not icon.isNull():
            pixmap = icon.pixmap(48, 48)  # 统一尺寸为48x48
            rounded_pixmap = self._create_rounded_pixmap(pixmap, 48, 9)
            self.icon_label.setPixmap(rounded_pixmap)
        else:
            self.icon_label.clear()
        # --- 修改结束 ---

    def _apply_style(self, is_night_mode):
        """
        根据日夜模式应用不同的样式。
        """
        if is_night_mode:
            self.text_label.setStyleSheet("""
                QLabel {
                    border: 0px solid #555555;
                    border-radius: 19px;
                    background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                                    stop: 0 #000000, stop: 0.2 #EDF1F7, stop: 0.8 #EDF1F7, stop: 1 #000000);
                    font-family: 'Comic Sans MS', 'KaiTi', sans-serif;
                    font-size: 18px;
                    font-weight: bold;
                    color: #000000;
                    padding: 10px;
                    box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3); /* 添加边缘阴影 */
                }
            """)
            self.icon_label.setStyleSheet("background-color: transparent;")
        else:
            self.text_label.setStyleSheet("""
                QLabel {
                    border: 0px solid #CCCCCC;
                    border-radius: 19px;
                    background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                                    stop: 0 #000000, stop: 0.2 #EDF1F7, stop: 0.8 #EDF1F7, stop: 1 #000000);
                    font-family: 'Comic Sans MS', 'KaiTi', sans-serif;
                    font-size: 18px;
                    font-weight: bold;
                    color: #000000;
                    padding: 10px;
                    box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3); /* 添加边缘阴影 */
                }
            """)
            self.icon_label.setStyleSheet("background-color: transparent;")

    def update_hide_timer(self, duration: int):
        """
        动态更新通知的隐藏计时器。如果计时器正在运行，则停止并用新的时长重新启动。
        """
        if hasattr(self, 'hide_timer') and self.hide_timer.isActive():
            self.hide_timer.stop()
        self.hide_timer.start(duration)

    def show_animation(self, end_y: int):
        """
        执行通知窗口的显示动画，包括从右侧滑入和淡入。

        Args:
            end_y (int): 通知窗口的最终Y坐标，用于堆叠。
        """
        self.show()

        desktop = QApplication.desktop()
        desktop_rect = desktop.availableGeometry(self.parent_widget) if self.parent_widget else desktop.availableGeometry()

        end_x = desktop_rect.x() + desktop_rect.width() - self.width() - 20
        start_x = desktop_rect.x() + desktop_rect.width()

        self.setGeometry(start_x, end_y, self.width(), self.height())

        self.pos_animation.setDuration(self.animation_duration)
        self.pos_animation.setStartValue(QPoint(start_x, end_y))
        self.pos_animation.setEndValue(QPoint(end_x, end_y))
        self.pos_animation.setEasingCurve(QEasingCurve.OutElastic)

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
        if hasattr(self, 'hide_timer') and self.hide_timer.isActive():
            self.hide_timer.stop()

        start_pos = self.pos()
        desktop = QApplication.desktop()
        desktop_rect = desktop.availableGeometry(self.parent_widget) if self.parent_widget else desktop.availableGeometry()

        end_x = desktop_rect.x() + desktop_rect.width()
        end_y = self.y()

        self.pos_animation.setDuration(self.animation_duration)
        self.pos_animation.setStartValue(start_pos)
        self.pos_animation.setEndValue(QPoint(end_x, end_y))
        self.pos_animation.setEasingCurve(QEasingCurve.InQuint)
        self.pos_animation.finished.connect(self.close_notification)

        self.opacity_animation.setDuration(self.animation_duration)
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)

        self.pos_animation.start()
        self.opacity_animation.start()

    def close_notification(self):
        """
        关闭通知窗口并发出信号，通知管理器处理。
        """
        self.closed.emit(self)
        self.close()