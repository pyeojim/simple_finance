import sqlite3
import pandas as pd
import time
from client import klineupdater
from config import DB_PATH, DEFAULT_INTERVAL, DATA_START_TIMESTAMP

class EquityData:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._connect_with_retry()
    
    def _connect_with_retry(self, max_retries=3):
        for attempt in range(max_retries):
            try:
                self.conn = sqlite3.connect(self.db_path)
                self.cursor = self.conn.cursor()
                self.create_tables()
                print(f"Database connected successfully: {self.db_path}")
                return
            except Exception as e:
                print(f"Database connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    print("Failed to connect to database after all attempts")
                    raise
    
    def create_tables(self):
        # symbols 테이블 생성
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS symbols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                interval TEXT NOT NULL DEFAULT '1s',
                last_timestamp INTEGER DEFAULT 0
            )
        ''')
    
    def create_symbol_table(self, symbol):
        table_name = f"ohlcv_{symbol.replace('/', '_').lower()}"
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER UNIQUE NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL
            )
        ''')
        self.conn.commit()
        return table_name
    
    def add_symbol(self, symbol, interval=DEFAULT_INTERVAL):
        try:
            self.cursor.execute('''
                INSERT INTO symbols (symbol, interval) VALUES (?, ?)
            ''', (symbol, interval))
            self.conn.commit()
            
            # symbol별 OHLCV 테이블 생성
            self.create_symbol_table(symbol)
            print(f"Symbol {symbol} added successfully")
            return True
        except sqlite3.IntegrityError:
            print(f"Symbol {symbol} already exists")
            return False
    
    def get_symbols(self):
        self.cursor.execute('SELECT symbol, interval, last_timestamp FROM symbols')
        return self.cursor.fetchall()
    
    def get_last_timestamp(self, symbol):
        self.cursor.execute('SELECT last_timestamp FROM symbols WHERE symbol = ?', (symbol,))
        result = self.cursor.fetchone()
        return result[0] if result else 0
    
    def update_last_timestamp(self, symbol, timestamp):
        self.cursor.execute('''
            UPDATE symbols SET last_timestamp = ? WHERE symbol = ?
        ''', (timestamp, symbol))
        self.conn.commit()
    
    def insert_ohlcv_data(self, symbol, df):
        if df.empty:
            return
        
        table_name = f"ohlcv_{symbol.replace('/', '_').lower()}"
        
        # 청크 단위로 처리 (메모리 효율성)
        chunk_size = 5000
        total_inserted = 0
        
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i+chunk_size]
            
            # Batch insert for better performance
            data_to_insert = []
            for _, row in chunk.iterrows():
                data_to_insert.append((
                    row['timestamp'], 
                    row['open'], 
                    row['high'], 
                    row['low'], 
                    row['close'], 
                    row['volume']
                ))
            
            try:
                self.cursor.executemany(f'''
                    INSERT OR IGNORE INTO {table_name} (timestamp, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', data_to_insert)
                self.conn.commit()
                
                total_inserted += len(data_to_insert)
                
            except Exception as e:
                print(f"Failed to insert chunk for {symbol}: {e}")
                self.conn.rollback()
                return
        
        # 마지막 timestamp 업데이트
        if not df.empty:
            last_ts = int(df['timestamp'].iloc[-1])
            self.update_last_timestamp(symbol, last_ts)
    
    def update_symbol_data(self, symbol):
        last_ts = self.get_last_timestamp(symbol)
        current_time = int(time.time() * 1000)
        
        # 마지막 데이터가 없으면 설정된 시작 시간부터 시작
        if last_ts == 0:
            last_ts = DATA_START_TIMESTAMP
        
        # symbol의 interval 가져오기
        self.cursor.execute('SELECT interval FROM symbols WHERE symbol = ?', (symbol,))
        result = self.cursor.fetchone()
        interval = result[0] if result else DEFAULT_INTERVAL
        
        # 새로운 데이터 가져오기
        new_data = klineupdater(symbol, interval, last_ts + 1)
        
        if not new_data.empty:
            self.insert_ohlcv_data(symbol, new_data)
            print(f"Updated {symbol}: {len(new_data)} new records")
        else:
            print(f"No new data for {symbol}")
    
    def update_all_symbols(self):
        symbols = self.get_symbols()
        for symbol, interval, _ in symbols:
            self.update_symbol_data(symbol)
    
    def get_symbol_data(self, symbol, limit=1000):
        table_name = f"ohlcv_{symbol.replace('/', '_').lower()}"
        self.cursor.execute(f'''
            SELECT timestamp, open, high, low, close, volume 
            FROM {table_name} 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        data = self.cursor.fetchall()
        df = pd.DataFrame(data)
        df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    
    def close(self):
        if self.conn:
            self.conn.close()