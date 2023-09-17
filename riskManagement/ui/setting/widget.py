from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, \
    QPushButton, QHeaderView, QLineEdit, QLabel, QDialog


class SettingsPage(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("选项页")
        self.resize(600, 400)

        main_layout = QVBoxLayout()

        tab_widget = QTabWidget()

        # 账户页
        account_page = AccountWidget()

        # 风控设置页
        risk_page = RiskWidget()

        tab_widget.addTab(account_page, "账户")
        tab_widget.addTab(risk_page, "风控")

        main_layout.addWidget(tab_widget)

        # 确定和取消按钮
        button_layout = QHBoxLayout()
        confirm_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)


class AccountWidget(QWidget):
    def __init__(self):
        super().__init__()
        account_layout = QVBoxLayout()
        account_table = QTableWidget()
        account_table.setColumnCount(4)
        account_table.verticalHeader().setVisible(False)  # 取消显示行号
        account_table.setHorizontalHeaderLabels(["账户名称", "交易账号", "交易密码", "资金密码"])
        # 设置表头的拉伸模式
        account_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        account_table.setRowCount(5)  # 设置行数，这里假设有5条账户信息

        # 填充表格数据
        for row in range(5):
            for column in range(4):
                item = QTableWidgetItem(f"数据{row}-{column}")
                account_table.setItem(row, column, item)

        account_layout.addWidget(account_table)

        self.setLayout(account_layout)


class RiskWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.position_loss_label = QLabel("持仓亏损")
        self.position_loss_input = QLineEdit()
        self.position_loss_label2 = QLabel("%强平")
        self.money_loss_label = QLabel("权益小于")
        self.money_loss_input = QLineEdit()
        self.money_loss_label2 = QLabel("强平并转走")

        layout = QVBoxLayout()

        h_box = QHBoxLayout()
        h_box.setContentsMargins(150, 0, 150, 0)
        h_box.addWidget(self.position_loss_label)
        h_box.addWidget(self.position_loss_input)
        h_box.addWidget(self.position_loss_label2)

        h_box2 = QHBoxLayout()
        h_box2.setContentsMargins(150, 0, 150, 0)
        h_box2.addWidget(self.money_loss_label)
        h_box2.addWidget(self.money_loss_input)
        h_box2.addWidget(self.money_loss_label2)

        layout.addLayout(h_box)
        layout.addLayout(h_box2)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication([])
    window = SettingsPage()
    window.show()
    app.exec()
