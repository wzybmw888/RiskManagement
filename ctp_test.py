import time

import pandas as pd
from vnpy.trader.utility import load_json
from vnpy_scripttrader import init_cli_trading
from vnpy_ctp import CtpGateway

from riskManagement.utils import TradeTable

db_utils = TradeTable('mydatabase.db')
setting_1 = load_json("connect_ctp.json")
engine = init_cli_trading([CtpGateway])
engine.connect_gateway(setting_1, "CTP")
time.sleep(40)

while True:
    df_account = pd.DataFrame()
    df_position = pd.DataFrame()
    df_ticks = pd.DataFrame()
    # 获取开仓合约名称和合约对应的盈亏
    # 获取账户总资金
    try:
        df_account = engine.get_account(vt_accountid="CTP.218042", use_df=True)
        df_position = engine.get_all_positions(use_df=True)
        # 删除"volume"列值为0的行
        df_position = df_position.drop(df_position[df_position['volume'] == 0].index)
        vt_symbols = df_position["vt_symbol"].values
        engine.subscribe(vt_symbols=vt_symbols)
        df_ticks = engine.get_ticks(vt_symbols=vt_symbols, use_df=True)

    except Exception as e:
        print(e)

    if len(df_account) > 0 and len(df_position) > 0 and len(df_ticks) > 0:
        merged_df = pd.concat([df_position.set_index('vt_symbol'), df_ticks.set_index('vt_symbol')], axis=1)
        # 计算pnl_percent
        merged_df["pnl_percent"] = (merged_df["last_price"] - merged_df["price"]) / merged_df["price"]
        # 获取资金
        balance = df_account["balance"].values
        # 可用
        available = df_account["available"].values
        # 合约品种
        contract = merged_df.index.values
        # 利润
        profit = merged_df["pnl"].values
        pnl_percent = merged_df["pnl_percent"].values
        # 更新账户
        db_utils.update_account(1, balance, available, contract, pnl_percent)
    else:
        continue

    time.sleep(1)
