import sqlite3
import pandas as pd
import os

# Equity Data (OHLCV for Backtesting)
class EquityData:
    def __init__(self, asset_name, db_dir='db'):
        self.db_dir = db_dir
        self.asset_name = asset_name

        # Create the database directory if it doesn't exist
        os.makedirs(self.db_dir, exist_ok=True)

        self.db_path = os.path.join(self.db_dir, f"{self.asset_name.lower()}.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.table_name = "ohlcv"  # Simpler table name as each asset has its own DB

    def create_table(self):
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL
                -- Add other fields as needed (e.g., adjusted close, dividends)
            )
        ''')
        self.conn.commit()

    def insert_data(self, date, open, high, low, close, volume):
        self.cursor.execute(f'''
            INSERT INTO {self.table_name} (date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (date, open, high, low, close, volume))
        self.conn.commit()

    def fetch_all(self):
        self.cursor.execute(f'SELECT * FROM {self.table_name}')
        return pd.DataFrame(self.cursor.fetchall(), columns=['id', 'date', 'open', 'high', 'low', 'close', 'volume'])

    # Add other fetch methods as needed (e.g., fetch_by_date_range)

    def close(self):
        self.conn.close()