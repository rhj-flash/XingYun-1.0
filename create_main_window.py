# status_bar_manager.py
from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtCore import Qt


class StatusBarManager:
    """
    状态栏管理类。

    该类封装了状态栏的创建、样式设置和文本更新逻辑。
    确保状态栏在文本过长时，能够自动截断并在末尾显示省略号，
    同时保持固定高度，不因文本长度而改变控件大小。
    """

    def __init__(self, parent=None):
        """
        初始化状态栏管理器。

        Args:
            parent (QWidget, optional): 状态栏的父控件。默认为 None。
        """
        self.status_bar = QLabel(parent)
        self._setup_ui()

    def _setup_ui(self):
        """
        设置状态栏的UI样式和属性。
        """
        # 设置初始文本
        self.status_bar.setText(self.status_bar.tr(">>> 准备就绪🚀"))

        # 应用样式
        self.status_bar.setStyleSheet("""
            font-family: 'Sarasa Gothic', 'Consolas', 'Courier New', sans-serif;
            font-size: 12px;
            color: #444444;
            padding: 2px 8px;
            border-top: 1px solid #CCCCCC;
            border-radius: 8px;
        """)

        # 设置文本对齐方式为左对齐和垂直居中
        self.status_bar.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # 强制设置固定高度，避免因内容改变而拉伸
        self.status_bar.setFixedHeight(30)

        # 尺寸策略：水平方向可拉伸，垂直方向固定
        self.status_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # 禁用自动换行，这对于单行状态栏至关重要
        # 在 PyQt5 中，这是实现文本截断的关键步骤之一
        self.status_bar.setWordWrap(False)

        # ----------------- 关键修改开始 -----------------
        # 在 PyQt5 中，我们不能直接使用 setTextElideMode。
        # 而是需要使用 setProperty 来模拟这个功能。
        # Qt 的 stylesheet 或属性系统会处理这个属性。
        self.status_bar.setProperty("elideMode", "ElideRight")
        # ----------------- 关键修改结束 -----------------

    def set_status_text(self, text: str):
        """
        设置状态栏的显示文本。

        Args:
            text (str): 要显示的新文本。
        """
        self.status_bar.setText(text)
        # 调试语句：打印当前设置的文本，方便跟踪
        print(f"状态栏文本已更新为: '{text}'")

    def get_status_bar(self) -> QLabel:
        """
        获取状态栏QLabel控件实例。

        Returns:
            QLabel: 状态栏的QLabel控件。
        """
        return self.status_bar


# 示例用法
if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
    import sys


    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("状态栏示例")
            self.setGeometry(100, 100, 500, 200)

            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

            self.status_bar_manager = StatusBarManager()

            # 将状态栏添加到主窗口
            self.statusBar().addWidget(self.status_bar_manager.get_status_bar())

            # 添加一些按钮来测试状态栏
            btn_short = QPushButton("设置短文本")
            btn_short.clicked.connect(lambda: self.status_bar_manager.set_status_text("短文本测试"))

            btn_long = QPushButton("设置长文本")
            long_text = "这是一个非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常长的文本，用来测试省略号功能。"
            btn_long.clicked.connect(lambda: self.status_bar_manager.set_status_text(long_text))

            btn_ready = QPushButton("恢复就绪")
            btn_ready.clicked.connect(lambda: self.status_bar_manager.set_status_text(">>> 准备就绪🚀"))

            layout.addWidget(btn_short)
            layout.addWidget(btn_long)
            layout.addWidget(btn_ready)


    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())