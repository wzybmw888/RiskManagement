from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QFrame, QTableWidget, \
    QTableWidgetItem, QGridLayout, QAbstractItemView

from riskManagement.ui.setting.widget import SettingsPage


def openSettingPage():
    dialog = SettingsPage()
    dialog.exec()


def get_max_contract_count(data):
    max_count = 0

    for item in data:
        contracts = item["contract"]
        count = len(contracts)
        max_count = max(max_count, count)

    return max_count


class MainPage(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("风控系统V1.0.0")
        self.resize(1000, 700)

        # 创建菜单栏
        menubar = self.menuBar()
        setting = QAction("设置", self)
        setting.triggered.connect(openSettingPage)
        menubar.addAction(setting)

        # 创建垂直布局
        layout = QVBoxLayout(self)
        data = [
            {"name": "账户1",
             "contract": ["合约1", "合约2", "合约1", "合约2", "合约1", "合约2", "合约1", "合约2", "合约1", "合约2",
                          "合约1", "合约2"], "profile": ["1%", "1%"]},
            {"name": "账户2", "contract": ["合约1", "合约2"], "profile": ["2%", "2%"]},
            {"name": "账户3", "contract": ["合约1", "合约2"], "profile": ["3%", "3%"]},
            {"name": "账户3", "contract": ["合约1", "合约2"], "profile": ["3%", "3%"]},
            {"name": "账户3", "contract": ["合约1", "合约2"], "profile": ["3%", "3%"]},
            {"name": "账户3", "contract": ["合约1", "合约2"], "profile": ["3%", "3%"]},
            {"name": "账户3", "contract": ["合约1", "合约2"], "profile": ["3%", "3%"]},
            {"name": "账户3", "contract": ["合约1", "合约2"], "profile": ["3%", "3%"]},
            {"name": "账户3", "contract": ["合约1", "合约2"], "profile": ["3%", "3%"]},
            {"name": "账户3", "contract": ["合约1", "合约2"], "profile": ["3%", "3%"]},
            {"name": "账户3", "contract": ["合约1", "合约2"], "profile": ["3%", "3%"]},
            {"name": "账户3", "contract": ["合约1", "合约2"], "profile": ["3%", "3%"]},
            {"name": "账户3", "contract": ["合约1", "合约2"], "profile": ["3%", "3%"]},
        ]
        # 创建多个账户表格
        account1_table = self.create_table(data)

        # 将标签添加到布局中
        layout.addWidget(account1_table)

        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def create_table(self, datas):
        table = QTableWidget()
        length = get_max_contract_count(datas)
        # 设置表格内容居中显示
        # 设置表格内容居中显示
        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setColumnCount(length + 2)
        table.setRowCount(len(datas) * 2)
        table.verticalHeader().hide()
        table.horizontalHeader().hide()
        # 禁用编辑功能
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        index = 0
        for data in datas:
            table.setSpan(index, 0, 2, 1)
            table.setItem(index, 0, QTableWidgetItem(data["name"]))
            table.setItem(index, 1, QTableWidgetItem("合约"))
            table.setItem(index + 1, 1, QTableWidgetItem("盈亏"))

            for col, c in enumerate(data["contract"]):
                item = QTableWidgetItem(c)
                table.setItem(index, col + 2, item)

            for col, p in enumerate(data["profile"]):
                item = QTableWidgetItem(p)
                table.setItem(index + 1, col + 2, item)

            index += 2

        return table


if __name__ == "__main__":
    app = QApplication([])
    window = MainPage()
    window.show()
    app.exec()
