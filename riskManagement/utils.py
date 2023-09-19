from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence

import sqlite3


class TradeTable:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_account_table()

    def create_account_table(self):
        # 建立合约盈亏表
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS trade (
            id INTEGER PRIMARY KEY,
            account_name TEXT,
            total_amount REAL,
            available_amount REAL,
            contract TEXT,
            contract_change TEXT
        )
        '''
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def insert_account(self, account_name, total_amount, available_amount, contract, contract_change):
        insert_data_query = '''
        INSERT INTO account (account_name, total_amount, available_amount, contract, contract_change)
        VALUES (?, ?, ?, ?, ?)
        '''
        self.cursor.execute(insert_data_query,
                            (account_name, total_amount, available_amount, contract, contract_change))
        self.conn.commit()

    def update_account(self, account_id, total_amount, available_amount, contract, contract_change):
        update_data_query = '''
        UPDATE account SET total_amount=?, available_amount=?, contract=?, contract_change=?
        WHERE id=?
        '''
        self.cursor.execute(update_data_query, (total_amount, available_amount, contract, contract_change, account_id))
        self.conn.commit()

    def delete_account(self, account_id):
        delete_data_query = 'DELETE FROM account WHERE id=?'
        self.cursor.execute(delete_data_query, (account_id,))
        self.conn.commit()

    def select_all_accounts(self):
        select_data_query = 'SELECT * FROM account'
        self.cursor.execute(select_data_query)
        return self.cursor.fetchall()

    def close_connection(self):
        self.cursor.close()
        self.conn.close()


class AccountTable:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_account_table()

    def create_account_table(self):
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS account (
            id INTEGER PRIMARY KEY,
            account_name TEXT,
            transaction_account TEXT,
            transaction_password TEXT,
            fund_password TEXT
        )
        '''
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def insert_account(self, account_name, transaction_account, transaction_password, fund_password):
        insert_data_query = '''
        INSERT INTO account (account_name, transaction_account, transaction_password, fund_password)
        VALUES (?, ?, ?, ?)
        '''
        self.cursor.execute(insert_data_query, (account_name, transaction_account, transaction_password, fund_password))
        self.conn.commit()

    def update_account(self, account_name, transaction_account, transaction_password, fund_password):
        update_data_query = '''
        UPDATE account SET transaction_account=?, transaction_password=?, fund_password=?
        WHERE account_name=?
        '''
        self.cursor.execute(update_data_query, (transaction_account, transaction_password, fund_password, account_name))
        self.conn.commit()

    def delete_account(self, account_name):
        delete_data_query = 'DELETE FROM account WHERE account_name=?'
        self.cursor.execute(delete_data_query, (account_name,))
        self.conn.commit()

    def select_all_accounts(self):
        select_data_query = 'SELECT * FROM account'
        self.cursor.execute(select_data_query)
        return self.cursor.fetchall()

    def close_connection(self):
        self.cursor.close()
        self.conn.close()


class RiskTable:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_risk_table()

    def create_risk_table(self):
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS risk (
            id INTEGER PRIMARY KEY,
            account_name TEXT,
            equity REAL,
            position_loss REAL,
            FOREIGN KEY (account_name) REFERENCES account(account_name)
        )
        '''
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def insert_risk(self, account_name, equity, position_loss):
        insert_data_query = '''
        INSERT INTO risk (account_name, equity, position_loss)
        VALUES (?, ?, ?)
        '''
        self.cursor.execute(insert_data_query, (account_name, equity, position_loss))
        self.conn.commit()

    def update_risk(self, risk_id, equity, position_loss):
        update_data_query = '''
        UPDATE risk SET equity=?, position_loss=?
        WHERE id=?
        '''
        self.cursor.execute(update_data_query, (equity, position_loss, risk_id))
        self.conn.commit()

    def delete_risk(self, risk_id):
        delete_data_query = 'DELETE FROM risk WHERE id=?'
        self.cursor.execute(delete_data_query, (risk_id,))
        self.conn.commit()

    def select_all_risks(self):
        select_data_query = 'SELECT * FROM risk'
        self.cursor.execute(select_data_query)
        return self.cursor.fetchall()

    def close_connection(self):
        self.cursor.close()
        self.conn.close()

def create_shortcut(target, key):
    shortcut = QShortcut(QKeySequence(key), target)
    shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
    shortcut.activated.connect(target.click)


if __name__ == '__main__':
    # 使用示例
    db_utils = RiskTable('../mydatabase.db')

    # 插入风控数据
    db_utils.insert_risk('John', 10000, -500)
    db_utils.insert_risk('Jane', 20000, -1000)

    # 更新风控数据
    db_utils.update_risk(1, 12000, -600)

    # 删除风控数据
    db_utils.delete_risk(2)

    # 查询所有风控数据
    risks = db_utils.select_all_risks()
    for risk in risks:
        print(risk)

    db_utils.close_connection()
