import datetime
import math
import time
from typing import Sequence

import pandas as pd
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QTableWidget, \
    QTableWidgetItem, QHeaderView,  QHBoxLayout
from vnpy.trader.constant import Direction
from vnpy.trader.object import OrderData, ContractData
from vnpy_ctp import CtpGateway
from vnpy_scripttrader import init_cli_trading

from config import DB_PATH
from riskManagement.ui.setting.widget import SettingsPage
from riskManagement.utils import AccountTable, RiskTable, get_all_active_positions

account_datas = []


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


def create_table():
    table = QTableWidget()
    table.setColumnCount(5)
    table.setHorizontalHeaderLabels(["账户名称", "账户余额", "可用资金", "合约", "涨跌", "盈亏"])
    # 设置自动调整模式为Stretch
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    return table


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

        layout_top = QHBoxLayout(self)
        self.message_label = QLabel("消息提示:")

        layout_top.addWidget(self.message_label)

        layout.addLayout(layout_top)

        account_table = AccountTable(DB_PATH)
        result = account_table.select_all_accounts()
        account_table.close_connection()
        risk_table = RiskTable(DB_PATH)
        risk_result = risk_table.select_all_risks()
        if len(result) < 1:
            self.message_label.setText("请添加资金账户！")
        if len(risk_result) < 1:
            self.message_label.setText("请设置风控！")

        self.data_threads = []
        for i, item in enumerate(result):
            account_datas.append({"name": "", "balance": "", "available": "",
                                  "contract": [], "profile": [], 'pnl': []})
            data_thread = DataThread(i, item, risk_result[0][2] / 100, risk_result[0][3])
            data_thread.data_updated.connect(self.update_table)
            data_thread.message.connect(self.update_message)
            self.data_threads.append(data_thread)
            data_thread.start()

        # 创建多个账户表格
        self.table = create_table()

        # 将标签添加到布局中
        layout.addWidget(self.table)

        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def update_message(self, data):
        self.message_label.setText(data)

    def update_table(self, data):
        self.table.setRowCount(0)
        for row, account in enumerate(data):
            account_name = QTableWidgetItem(account["name"])
            balance = QTableWidgetItem(account["balance"])
            available = QTableWidgetItem(account["available"])
            contracts = QTableWidgetItem(",".join(account["contract"]))
            profiles = QTableWidgetItem(",".join(account["profile"]))
            pnl = QTableWidgetItem(",".join(account["pnl"]))

            self.table.insertRow(row)
            self.table.setItem(row, 0, account_name)
            self.table.setItem(row, 1, balance)
            self.table.setItem(row, 2, available)
            self.table.setItem(row, 3, contracts)
            self.table.setItem(row, 4, profiles)
            self.table.setItem(row, 5, pnl)

    def closeEvent(self, event):
        self.message_label.setText("正在停止程序，请等待...")
        for thread in self.data_threads:
            thread.stop()
        event.accept()


class DataThread(QThread):
    data_updated = pyqtSignal(list)
    message = pyqtSignal(str)

    def __init__(self, i, item, equity, loss):
        super().__init__()
        self.equity = equity
        self.loss = loss
        self.item = item
        self.i = i
        self.running = True

    def run(self):
        # 获取账户信息
        item = self.item
        setting = {
            "用户名": item[2],
            "密码": item[3],
            "经纪商代码": "9999",
            "交易服务器": "tcp://180.168.146.187:10201",
            "行情服务器": "tcp://180.168.146.187:10211",
            "产品名称": "simnow_client_test",
            "授权编码": "0000000000000000"
        }

        engine = init_cli_trading([CtpGateway])
        engine.connect_gateway(setting, "CTP")

        df_account = pd.DataFrame()
        df_position = pd.DataFrame()
        df_ticks = pd.DataFrame()

        account_datas[self.i]["name"] = item[1]
        while True:
            try:
                # 获取账户数据
                new_df_account = engine.get_account(vt_accountid=f"CTP.{item[2]}", use_df=True)

                # 判断账户数据是否变化
                if not new_df_account.equals(df_account):
                    df_account = new_df_account
                    balance = df_account["balance"].values[0]
                    available = df_account["available"].values[0]
                    account_datas[self.i]["balance"] = str(balance)
                    account_datas[self.i]["available"] = str(available)

                # 获取持仓数据
                new_df_position = get_all_active_positions(engine)

                # 判断持仓数据是否变化
                if not new_df_position.equals(df_position):
                    df_position = new_df_position
                    vt_symbols = df_position["vt_symbol"].values
                    engine.subscribe(vt_symbols=vt_symbols)

                # 获取Tick数据
                new_df_ticks = engine.get_ticks(vt_symbols=vt_symbols, use_df=True)

                # 判断Tick数据是否变化
                if not new_df_ticks.equals(df_ticks):
                    df_ticks = new_df_ticks
                    merged_df = pd.concat([df_position.set_index('vt_symbol'), df_ticks.set_index('vt_symbol')],
                                          axis=1)
                    merged_df["pnl_percent"] = (merged_df["last_price"] - merged_df["price"]) / merged_df["price"]
                    contract = merged_df.index.values
                    pnl_percent = merged_df["pnl_percent"].values
                    pnl = merged_df["pnl"].values
                    pnl_str = [str(p) for p in pnl]
                    account_datas[self.i]["profile"] = ["{:.2f}%".format(pnl * 100) for pnl in pnl_percent]
                    account_datas[self.i]["contract"] = contract
                    account_datas[self.i]["pnl"] = pnl_str
                    direction = merged_df["direction"].values
                    volume = merged_df["volume"].values
                    last_price = merged_df["last_price"].values

                    # 编写总账户平仓逻辑
                    # 取消之前的订单
                    orders: Sequence[OrderData] = engine.get_all_active_orders()
                    for order in orders:
                        engine.cancel_order(order.orderid)
                    if balance >= self.loss:
                        for i, pnl_ in enumerate(pnl_percent):
                            if pnl_ < -self.equity:
                                contract_info: ContractData = engine.get_contract(vt_symbol=contract[i])
                                price_tick = contract_info.pricetick
                                if direction[i] == Direction.LONG:
                                    engine.sell(vt_symbol=contract[i],
                                                price=self.round_to_multiple(0.995 * last_price[i], price_tick,
                                                                             Direction.LONG),
                                                volume=volume[i][0])
                                else:
                                    engine.cover(vt_symbol=contract[i],
                                                 price=self.round_to_multiple(1.005 * last_price[i], price_tick,
                                                                              Direction.SHORT),
                                                 volume=volume[i][0])
                            else:
                                continue
                    else:
                        for i, _ in enumerate(pnl_percent):
                            contract_info: ContractData = engine.get_contract(vt_symbol=contract[i])
                            price_tick = contract_info.pricetick
                            if direction[i] == Direction.LONG:
                                engine.sell(vt_symbol=contract[i],
                                            price=self.round_to_multiple(0.995 * last_price[i], price_tick,
                                                                         Direction.LONG),
                                            volume=volume[i][0])
                            else:
                                engine.cover(vt_symbol=contract[i],
                                             price=self.round_to_multiple(1.005 * last_price[i], price_tick,
                                                                          Direction.SHORT),
                                             volume=volume[i][0])

            except Exception as e:
                now = datetime.datetime.now()
                formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
                self.message.emit("正在获取数据,等待中....上次连接时间为：" + formatted_date_time)
                time.sleep(3)

            self.data_updated.emit(account_datas)
            time.sleep(2)

    def stop(self):
        self.running = False

    def round_to_multiple(self, price, multiple, variable):
        if variable == Direction.LONG:
            return math.ceil(price / multiple) * multiple
        elif variable == Direction.SHORT:
            return math.floor(price / multiple) * multiple
        else:
            raise ValueError("Invalid variable value. Must be 'long' or 'short'.")
