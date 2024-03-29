import sys

import qdarkstyle
from PyQt6.QtWidgets import QApplication

from riskManagement.ui.index.widget import MainPage


def read_qss_file(qss_file_name):
    with open(qss_file_name, 'r', encoding='UTF-8') as file:
        return file.read()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    # 创建并显示登录窗口
    login_window = MainPage()
    login_window.show()
    sys.exit(app.exec())
