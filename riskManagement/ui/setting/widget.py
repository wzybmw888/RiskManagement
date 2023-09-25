from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, \
    QPushButton, QHeaderView, QLineEdit, QLabel, QDialog, QMessageBox

from config import DB_PATH
from riskManagement.utils import AccountTable, RiskTable


def write_data_to_database(table):
    db_account = AccountTable(DB_PATH)
    for row in range(table.rowCount()):
        account_name = table.item(row, 0).text()
        transaction_account = table.item(row, 1).text()
        transaction_password = table.item(row, 2).text()
        fund_password = table.item(row, 3).text()
        if (account_name is not None
                and transaction_account is not None
                and transaction_password is not None
                and fund_password is not None):
            db_account.insert_account(account_name, transaction_account, transaction_password, fund_password)
    db_account.close_connection()


class SettingsPage(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("选项页")
        self.resize(600, 400)

        main_layout = QVBoxLayout()

        tab_widget = QTabWidget()

        # 账户页
        self.account_page = AccountWidget()

        # 风控设置页
        risk_page = RiskWidget()

        tab_widget.addTab(self.account_page, "账户")
        tab_widget.addTab(risk_page, "风控")

        main_layout.addWidget(tab_widget)

        self.setLayout(main_layout)

    def confirm(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("确认提交")
        msg_box.setText("确认提交数据吗？")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        yes_button = msg_box.button(QMessageBox.StandardButton.Yes)
        yes_button.setText("是")
        no_button = msg_box.button(QMessageBox.StandardButton.No)
        no_button.setText("否")

        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            pass


class AccountWidget(QWidget):
    def __init__(self):
        super().__init__()
        account_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        add_button = QPushButton("新增")
        delete_button = QPushButton("删除账户")
        update_button = QPushButton("更新账户")
        add_account_button = QPushButton("提交")
        button_layout.addWidget(add_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(add_account_button)

        add_button.clicked.connect(self.addRow)
        delete_button.clicked.connect(self.deleteAccount)
        update_button.clicked.connect(self.updateAccount)
        add_account_button.clicked.connect(self.addAccount)

        self.account_table = QTableWidget()
        self.account_table.setColumnCount(9)
        self.account_table.verticalHeader().setVisible(False)  # 取消显示行号
        self.account_table.setHorizontalHeaderLabels(
            ["账户名称", "交易账号", "交易密码", "资金密码", "经纪商代码", "交易服务器", "行情服务器", "产品名称",
             "授权编码"])
        self.account_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        account_layout.addWidget(self.account_table)
        account_layout.addLayout(button_layout)

        self.setLayout(account_layout)
        self.db_account = AccountTable(DB_PATH)
        self.initializeTable()

    def initializeTable(self):
        # 获取数据库中的账户数据
        accounts = self.db_account.select_all_accounts()
        for row, data in enumerate(accounts):
            self.account_table.insertRow(row)

            account_name_item = QTableWidgetItem(data[1])
            self.account_table.setItem(row, 0, account_name_item)

            transaction_account_item = QTableWidgetItem(data[2])
            self.account_table.setItem(row, 1, transaction_account_item)

            transaction_password_item = QTableWidgetItem(data[3])
            self.account_table.setItem(row, 2, transaction_password_item)

            fund_password_item = QTableWidgetItem(data[4])
            self.account_table.setItem(row, 3, fund_password_item)

            commission_broker = QTableWidgetItem(data[5])
            self.account_table.setItem(row, 4, commission_broker)

            trade_server = QTableWidgetItem(data[6])
            self.account_table.setItem(row, 5, trade_server)

            quotation_server = QTableWidgetItem(data[7])
            self.account_table.setItem(row, 6, quotation_server)

            product_name = QTableWidgetItem(data[8])
            self.account_table.setItem(row, 7, product_name)

            authorization_code = QTableWidgetItem(data[9])
            self.account_table.setItem(row, 8, authorization_code)

    def addRow(self):
        row_count = self.account_table.rowCount()
        self.account_table.insertRow(row_count)

    def addAccount(self):
        current_row = self.account_table.currentRow()
        account_name = self.account_table.item(current_row, 0).text()
        transaction_account = self.account_table.item(current_row, 1).text()
        transaction_password = self.account_table.item(current_row, 2).text()
        fund_password = self.account_table.item(current_row, 3).text()
        commission_broker = self.account_table.item(current_row, 4).text()
        trade_server = self.account_table.item(current_row, 5).text()
        quotation_server = self.account_table.item(current_row, 6).text()
        product_name = self.account_table.item(current_row, 7).text()
        authorization_code = self.account_table.item(current_row, 8).text()

        self.db_account.insert_account(account_name, transaction_account, transaction_password, fund_password,
                                       commission_broker, trade_server, quotation_server
                                       , product_name, authorization_code)
        QMessageBox.information(self, "成功", "插入账户成功！")

    def deleteAccount(self):
        current_row = self.account_table.currentRow()

        if current_row < 0:
            QMessageBox.warning(self, "删除账户", "请先选择要删除的账户")
            return
        account_name = self.account_table.item(current_row, 0).text()
        self.account_table.removeRow(current_row)
        self.db_account.delete_account(account_name)
        # 弹出成功消息框
        QMessageBox.information(self, "成功", "删除账户成功！")

    def updateAccount(self):
        for row in range(self.account_table.rowCount()):
            account_name = self.account_table.item(row, 0).text()
            transaction_account = self.account_table.item(row, 1).text()
            transaction_password = self.account_table.item(row, 2).text()
            fund_password = self.account_table.item(row, 3).text()
            commission_broker = self.account_table.item(row, 4).text()
            trade_server = self.account_table.item(row, 5).text()
            quotation_server = self.account_table.item(row, 6).text()
            product_name = self.account_table.item(row, 7).text()
            authorization_code = self.account_table.item(row, 8).text()

            self.db_account.update_account(account_name, transaction_account, transaction_password, fund_password,
                                           commission_broker, trade_server, quotation_server
                                           , product_name, authorization_code)
        QMessageBox.information(self, "成功", "更新账户成功！")

    def closeEvent(self, event):
        self.db_account.close_connection()
        event.accept()


class RiskWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.position_loss_label = QLabel("持仓亏损")
        self.position_loss_input = QLineEdit()
        self.position_loss_label2 = QLabel("%强平")
        self.money_loss_label = QLabel("权益小于")
        self.money_loss_input = QLineEdit()
        self.money_loss_label2 = QLabel("万强平")

        risk_table = RiskTable(DB_PATH)
        res = risk_table.select_all_risks()
        if len(res) > 0:
            self.position_loss_input.setText(str(res[0][2]))
            self.money_loss_input.setText(str(res[0][3] / 10000))

        self.confirm_button = QPushButton("确认")

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
        layout.addWidget(self.confirm_button)
        self.confirm_button.clicked.connect(self.confirm)
        self.setLayout(layout)

    def confirm(self):
        risk_table = RiskTable(DB_PATH)
        risk_table.insert_or_update_risk("default", (self.position_loss_input.text()),
                                         str(float(self.money_loss_input.text()) * 10000))
        risk_table.close_connection()
        # 弹出成功消息框
        QMessageBox.information(self, "成功", "保存成功,数据重启后生效!")
