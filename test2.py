import pandas as pd
from binance.client import Client
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
load_dotenv()
import time
import warnings
warnings.filterwarnings('ignore')

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
client = Client(api_key=api_key, api_secret=api_secret)

symbol = 'DOGEUSDT'
interval = '30m'

def get_ohlc_hourly():
    try:
        interval = '1h'
        end_time = datetime.now() - timedelta(days=2)
        start_time = end_time - timedelta(days=12)

        print(end_time.strftime("%Y-%m-%d %H:%M")) # 현재 시간

        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)

        klines = client.get_historical_klines(symbol, interval, start_timestamp, end_timestamp)

        ohlc_hour = []
        for kline in klines:
            timestamp = datetime.fromtimestamp(kline[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            volume = float(kline[5])
            ohlc_hour.append([timestamp, open_price, high_price, low_price, close_price, volume])

        ohlc_hour = pd.DataFrame(ohlc_hour, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])

        ohlc_hour['Timestamp'] = pd.to_datetime(ohlc_hour['Timestamp'])

        return ohlc_hour
    
    except Exception as e:
        print("get_ohlc_hour() Exception:", e)

def get_ohlc_30_min():
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(days=2)

        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)

        klines = client.get_historical_klines(symbol, interval, start_timestamp, end_timestamp)

        ohlc_30_min = []
        for kline in klines:
            timestamp = datetime.fromtimestamp(kline[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            volume = float(kline[5])
            ohlc_30_min.append([timestamp, open_price, high_price, low_price, close_price, volume])

        ohlc_30_min = pd.DataFrame(ohlc_30_min, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])

        ohlc_30_min['Timestamp'] = pd.to_datetime(ohlc_30_min['Timestamp'])

        print(end_time.strftime("%Y-%m-%d %H:%M"))

        return ohlc_30_min
    
    except Exception as e:
        print("get_ohlc_30_min() Exception:", e)

def get_ohlc():
    ohlc_hour = get_ohlc_hourly()
    ohlc_30_min = get_ohlc_30_min()
    ohlc_df = pd.concat([ohlc_hour, ohlc_30_min])
    return ohlc_df

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_atr(df):
    try :
        df['High-Low'] = df['High'] - df['Low']
        df['High-PreviousClose'] = abs(df['High'] - df['Close'].shift(1))
        df['Low-PreviousClose'] = abs(df['Low'] - df['Close'].shift(1))
        df['TrueRange'] = df[['High-Low', 'High-PreviousClose', 'Low-PreviousClose']].max(axis=1)

        period = 14
        df['ATR'] = df['TrueRange'].rolling(period).mean()

        df.drop(['High-Low', 'High-PreviousClose', 'Low-PreviousClose', 'TrueRange'], axis=1, inplace=True)
        
        return df
    
    except Exception as e:
        print("calculage_atr() Exception", e)

if __name__ == "__main__" :
    ohlc_df = get_ohlc()
    ohlc_df['RSI'] = calculate_rsi(ohlc_df)
    ohlc_df  = calculate_atr(ohlc_df)
    print(ohlc_df.head(10))
    print(ohlc_df.tail(10))
    print(len(ohlc_df))