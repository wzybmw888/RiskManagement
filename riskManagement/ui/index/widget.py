import math
import time
from typing import Sequence, Optional, List

import pandas as pd
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTableWidget, \
    QTableWidgetItem, QHeaderView, QPlainTextEdit
from vnpy.trader.constant import Direction
from vnpy.trader.engine import MainEngine
from vnpy.trader.event import EVENT_LOG
from vnpy.trader.object import OrderData, ContractData
from vnpy_ctp import CtpGateway
from vnpy_scripttrader import ScriptEngine
from vnpy_scripttrader.engine import EVENT_SCRIPT_LOG

from config import DB_PATH
from riskManagement.ui.setting.widget import SettingsPage
from riskManagement.utils import AccountTable, RiskTable
from vnpy.event import EventEngine, Event

account_datas: List[dict] = []


def openSettingPage():
    dialog = SettingsPage()
    dialog.exec()


def create_table():
    table = QTableWidget()
    table.setColumnCount(6)
    table.setHorizontalHeaderLabels(["账户名称", "账户余额", "可用资金", "合约", "涨跌", "盈亏"])
    # 设置自动调整模式为Stretch
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    return table


def fetch_database():
    account_table = AccountTable(DB_PATH)
    result = account_table.select_all_accounts()
    account_table.close_connection()
    risk_table = RiskTable(DB_PATH)
    risk_result = risk_table.select_all_risks()
    return result, risk_result


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
        # message_label
        # 创建垂直布局
        layout = QVBoxLayout(self)

        # Create the plain text edit widget
        self.message_label = QPlainTextEdit()
        self.message_label.setReadOnly(True)

        layout.addWidget(self.message_label)

        result, risk_result = fetch_database()
        if len(result) < 1:
            self.message_label.setPlainText("请添加资金账户！")
        if len(risk_result) < 1:
            self.message_label.setPlainText("请设置风控！")

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
        self.message_label.setPlainText(data)

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
        self.message_label.setPlainText("正在停止程序，请等待...")
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
        self.event_str = []

    def run(self):
        # 获取账户信息
        item = self.item
        setting = {
            "用户名": item[2],
            "密码": item[3],
            "经纪商代码": item[5],
            "交易服务器": item[6],
            "行情服务器": item[7],
            "产品名称": item[8],
            "授权编码": item[9]
        }
        event_engine: EventEngine = EventEngine()
        event_engine.register(EVENT_SCRIPT_LOG, self.process_log_event)
        event_engine.register(EVENT_LOG, self.process_log_event)
        main_engine: MainEngine = MainEngine(event_engine)
        main_engine.add_gateway(CtpGateway)

        engine: ScriptEngine = main_engine.add_engine(ScriptEngine)
        engine.connect_gateway(setting, "CTP")

        account_datas[self.i]["name"] = item[1]
        while True:
            # try:
            # 获取账户数据
            df_account: Optional[pd.DataFrame, None] = engine.get_account(vt_accountid=f"CTP.{item[2]}", use_df=True)
            if df_account is None or df_account.empty:
                engine.write_log(f"正在获取  {item[1]}  的账户数据...")
                time.sleep(3)
                continue

            balance = df_account["balance"].values[0]
            available = df_account["available"].values[0]
            # 获取持仓数据
            df_position: Optional[pd.DataFrame, None] = engine.get_all_positions(use_df=True)

            if df_position is None or df_position.empty:
                account_datas[self.i]["balance"] = str(balance)
                account_datas[self.i]["available"] = str(available)
                account_datas[self.i]["profile"] = ''
                account_datas[self.i]["contract"] = ''
                account_datas[self.i]["pnl"] = ''
                engine.write_log(f"正在获取  {item[1]}  仓位数据...")
                time.sleep(3)
                continue
            else:
                df_position = df_position.drop(df_position[df_position['volume'] == 0].index)

            vt_symbols = df_position["vt_symbol"].values
            engine.subscribe(vt_symbols=vt_symbols)

            # 获取Tick数据
            try:
                df_ticks = engine.get_ticks(vt_symbols=vt_symbols, use_df=True)
            except Exception as e:
                df_ticks = None
                engine.write_log(f"正在获取  {item[1]}  Tick数据...")

            if df_ticks is None or df_ticks.empty:
                engine.write_log(f"正在获取  {item[1]}  Tick数据...")
                time.sleep(3)
                continue

            merged_df = pd.concat([df_position.set_index('vt_symbol'), df_ticks.set_index('vt_symbol')],
                                  axis=1)
            merged_df["pnl_percent"] = (merged_df["last_price"] - merged_df["price"]) / merged_df["price"]
            contract = merged_df.index.values
            pnl_percent = merged_df["pnl_percent"].values
            pnl = merged_df["pnl"].values
            pnl_str = [str(round(p, 2)) for p in pnl]
            direction = merged_df["direction"].values
            volume = merged_df["volume"].values
            last_price = merged_df["last_price"].values

            account_datas[self.i]["balance"] = str(balance)
            account_datas[self.i]["available"] = str(available)
            account_datas[self.i]["profile"] = ["{:.2f}%".format(pnl * 100) for pnl in pnl_percent]
            account_datas[self.i]["contract"] = contract
            account_datas[self.i]["pnl"] = pnl_str

            # 编写总账户平仓逻辑
            if balance >= self.loss:
                for i, pnl_ in enumerate(pnl_percent):
                    if pnl_ < -self.equity:
                        contract_info: ContractData = engine.get_contract(vt_symbol=contract[i])
                        price_tick = contract_info.pricetick
                        orders: Sequence[OrderData] = engine.get_all_active_orders()
                        for order in orders:
                            engine.cancel_order(order.orderid)
                        engine.write_log(f"取消  {item[1]}  之前的订单!!!")
                        if direction[i] == Direction.LONG:
                            engine.sell(vt_symbol=contract[i],
                                        price=self.round_to_multiple(0.995 * last_price[i], price_tick,
                                                                     Direction.LONG),
                                        volume=volume[i][0])
                        else:
                            engine.cover(vt_symbol=contract[i],
                                         price=self.round_to_multiple(1.005 * last_price[i], price_tick,
                                                                      Direction.SHORT),
                                         volume=volume[i][0], )
                        engine.write_log(f"  {item[1]}:  {contract[i]}触碰亏损警戒线,市价单平仓!!!")

                    else:
                        continue

            else:
                orders: Sequence[OrderData] = engine.get_all_active_orders()
                for order in orders:
                    engine.cancel_order(order.orderid)
                engine.write_log(f"  {item[1]}  账户取消之前的订单!!!")
                for i, _ in enumerate(pnl_percent):
                    contract_info: ContractData = engine.get_contract(vt_symbol=contract[i])
                    price_tick = contract_info.pricetick
                    if direction[i] == Direction.LONG:
                        engine.sell(vt_symbol=contract[i],
                                    price=self.round_to_multiple(0.995 * last_price[i], price_tick,
                                                                 Direction.LONG),
                                    volume=volume[i][0])
                        print(contract[i], volume[i][0])
                    else:
                        engine.cover(vt_symbol=contract[i],
                                     price=self.round_to_multiple(1.005 * last_price[i], price_tick,
                                                                  Direction.SHORT),
                                     volume=volume[i][0])
                        print(contract[i], volume[i][0])
                    engine.write_log(f"  {item[1]}:  达到账户权益阈值,全部平仓!!!")
                else:
                    continue

            self.data_updated.emit(account_datas)
            time.sleep(0.5)
            print_once = 0

    def stop(self):
        self.running = False

    def round_to_multiple(self, price, multiple, variable):
        if variable == Direction.LONG:
            return math.ceil(price / multiple) * multiple
        elif variable == Direction.SHORT:
            return math.floor(price / multiple) * multiple
        else:
            raise ValueError("Invalid variable value. Must be 'long' or 'short'.")

    def process_log_event(self, event: Event):
        self.event_str.append(str(event.data) + "\n")
        if len(self.event_str) > 20:
            self.event_str.pop(0)

        self.message.emit(''.join(self.event_str))
