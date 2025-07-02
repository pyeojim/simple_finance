import pandas as pd
from ccxt import binanceusdm
import time
from config import API_LIMIT, UPDATE_INTERVAL, MAX_RETRIES, RETRY_DELAY

def klineupdater(symbol, interval, begin_time):
    exchange = binanceusdm()
    all_df = []
    since = begin_time
    
    for attempt in range(MAX_RETRIES):
        try:
            while True:
                ohlcv = exchange.fetch_ohlcv(symbol, interval, since=since, limit=API_LIMIT)
                if not ohlcv:
                    break
                df = pd.DataFrame(ohlcv)
                df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                all_df.append(df)
                last_ts = df['timestamp'].iloc[-1]
                if len(df) < API_LIMIT:
                    break
                since = int(last_ts) + 1
                time.sleep(UPDATE_INTERVAL)
            break  # 성공하면 루프 탈출
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {symbol}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                print(f"Failed to fetch data for {symbol} after {MAX_RETRIES} attempts")
                return pd.DataFrame()
    
    if all_df:
        result = pd.concat(all_df, ignore_index=True)
        return result
    else:
        return pd.DataFrame() 