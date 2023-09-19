from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QGridLayout, QGroupBox, QTextEdit, \
    QHBoxLayout

from riskManagement.ui.index.widget import MainPage
from riskManagement.utils import create_shortcut


class LoginPage(QWidget):
    def __init__(self):
        super().__init__()

        self.MainWindow = None
        self.setWindowTitle("登录界面")
        self.resize(500, 700)

        # 标题
        self.title_label = QLabel("期货风险控制工具")
        self.title_label.setStyleSheet("font-size: 24px; color: red;")

        self.dynamic_groupbox = QGroupBox("官方动态信息")
        self.dynamic_textedit = QTextEdit()
        self.dynamic_textedit.setReadOnly(True)

        # 用户名
        self.name_label = QLabel("用户名:")
        self.name_input = QLineEdit()

        # 密码
        self.password_label = QLabel("密码:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # 登录按钮
        self.login_button = QPushButton("登录")
        self.exit_button = QPushButton("退出")

        self.login_info_groupbox = QGroupBox("登录信息")
        self.login_info_textedit = QTextEdit()
        self.login_info_textedit.setReadOnly(True)

        # 版本信息
        self.version_label = QLabel("版本: v0.0.1")
        self.year_label = QLabel("2023年")

        layout = QVBoxLayout()
        layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        dynamic_layout = QVBoxLayout()
        dynamic_layout.addWidget(self.dynamic_textedit)
        self.dynamic_groupbox.setLayout(dynamic_layout)
        layout.addWidget(self.dynamic_groupbox)

        form_layout = QGridLayout()
        form_layout.setContentsMargins(100, 0, 100, 0)
        form_layout.addWidget(self.name_label, 0, 0, 1, 1)
        form_layout.addWidget(self.name_input, 0, 1, 1, 1)
        form_layout.addWidget(self.password_label, 1, 0, 1, 1)
        form_layout.addWidget(self.password_input, 1, 1, 1, 1)

        # 创建水平布局，将确认提交按钮和返回按钮放在同一行
        h_box = QHBoxLayout()
        h_box.setContentsMargins(100, 20, 100, 20)
        h_box.addWidget(self.login_button)
        h_box.addWidget(self.exit_button)

        layout.addLayout(form_layout)
        layout.addLayout(h_box)

        login_info_layout = QVBoxLayout()
        login_info_layout.addWidget(self.login_info_textedit)
        self.login_info_groupbox.setLayout(login_info_layout)
        layout.addWidget(self.login_info_groupbox)

        self.setLayout(layout)

        # 设置组件样式
        self.dynamic_groupbox.setStyleSheet("QGroupBox { font-weight: bold; }")
        self.login_info_groupbox.setStyleSheet("QGroupBox { font-weight: bold; }")

        # 设置动态信息
        self.dynamic_textedit.setText(
            "1、RM V1.0.0发布了\n2、RMV2.0.0正在开发中\n3、欢迎加入我们的社区")

        # 连接登录按钮的点击事件
        self.login_button.clicked.connect(self.login)
        self.password_input.returnPressed.connect(self.login)

    def login(self):
        """
        处理登录操作
        """
        username = self.name_input.text()
        password = self.password_input.text()

        # 进行用户名和密码的验证
        if username == "admin" and password == "admin":
            self.login_info_textedit.setText("登录成功")
            self.hide()
            self.MainWindow = MainPage()
            self.MainWindow.show()

        else:
            self.login_info_textedit.setText("登录失败")
