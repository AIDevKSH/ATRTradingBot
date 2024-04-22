import pandas as pd
from binance.client import Client
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
load_dotenv()
import warnings
warnings.filterwarnings('ignore')

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
client = Client(api_key=api_key, api_secret=api_secret)

global symbol
symbol = 'DOGEUSDT'

global loss_value
loss_value = 1.6

def concat_df():
    try:
        df = []

        interval = '1h'
        
        end_time = datetime.now() - timedelta(days=2)
        start_time = end_time - timedelta(days=14)

        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)

        klines = client.get_historical_klines(symbol, interval, start_timestamp, end_timestamp)
        
        for kline in klines:
            timestamp = datetime.fromtimestamp(kline[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            volume = float(kline[5])
            df.append([timestamp, open_price, high_price, low_price, close_price, volume])

        interval = '15m'

        end_time = datetime.now()
        start_time = end_time - timedelta(days=2)

        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)

        klines = client.get_historical_klines(symbol, interval, start_timestamp, end_timestamp)

        for kline in klines:
            timestamp = datetime.fromtimestamp(kline[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            volume = float(kline[5])
            df.append([timestamp, open_price, high_price, low_price, close_price, volume])

        df = pd.DataFrame(df, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])

        df['Timestamp'] = pd.to_datetime(df['Timestamp'])

        return df
    
    except Exception as e:
        print("get_ohlc_hourly() Exception:", e)

def calculate_rsi(df, window=25) :
    try :
        df['MA'] = df['Close'].rolling(window=window).mean()

        df['Up'] = df['Close'].diff().apply(lambda x: x if x > 0 else 0)
        df['Down'] = df['Close'].diff().apply(lambda x: abs(x) if x < 0 else 0)

        up_avg = df['Up'].rolling(window=window).mean()
        down_avg = df['Down'].rolling(window=window).mean()

        rs = up_avg / down_avg
        df['RSI'] = 100 - (100 / (1 + rs))

        df.drop(['MA', 'Up', 'Down'], axis=1, inplace=True)

        return df
    
    except Exception as e:
        print("calculate_rsi() Exception:", e)

def calculate_atr(df, period=20):
    try :
        df['High-Low'] = df['High'] - df['Low']
        df['High-PreviousClose'] = abs(df['High'] - df['Close'].shift(1))
        df['Low-PreviousClose'] = abs(df['Low'] - df['Close'].shift(1))
        df['TrueRange'] = df[['High-Low', 'High-PreviousClose', 'Low-PreviousClose']].max(axis=1)

        df['ATR'] = df['TrueRange'].rolling(period).mean()

        df.drop(['High-Low', 'High-PreviousClose', 'Low-PreviousClose', 'TrueRange'], axis=1, inplace=True)

        return df
    
    except Exception as e:
        print("calculage_atr() Exception", e)

def calculate_atr_trailing_stop(df):
    try:
        df['ATR_Trailing_Stop'] = df['Close']

        for i in range(1, len(df)):
            n_loss = loss_value * df.iloc[i]['ATR']
            close = df.iloc[i]['Close']
            prev_close = df.iloc[i - 1]['Close']
            prev_atr_trailing_stop = df.iloc[i - 1]['ATR_Trailing_Stop']

            if close > prev_atr_trailing_stop and prev_close > prev_atr_trailing_stop:
                df.at[i, 'ATR_Trailing_Stop'] = max(prev_atr_trailing_stop, close - n_loss)

            elif close < prev_atr_trailing_stop and prev_close < prev_atr_trailing_stop:
                df.at[i, 'ATR_Trailing_Stop'] = min(prev_atr_trailing_stop, close + n_loss)

            elif close > prev_atr_trailing_stop:
                df.at[i, 'ATR_Trailing_Stop'] = close - n_loss

            elif close <= prev_atr_trailing_stop:
                df.at[i, 'ATR_Trailing_Stop'] = close + n_loss

        df.drop(['ATR'], axis=1, inplace=True)
        
        return df
    
    except Exception as e:
        print("calculate_atr_trailing_stop() Exception", e)


def if_crossover(df):
    try :
        #  Crossover
        #  0 : Initial value, No Crossover 
        df['Crossover'] = 0

        for i in range(1, len(df)):
            
            prev_close = df.iloc[i-1]['Close']
            prev_atr_trailing_stop = df.iloc[i-1]['ATR_Trailing_Stop']

            close = df.iloc[i]['Close']
            atr_trailing_stop = df.iloc[i]['ATR_Trailing_Stop']

            #  1 : Upward Crossover
            # Bull Signal
            if prev_close <= prev_atr_trailing_stop and close >= atr_trailing_stop :
                df.at[i, 'Crossover'] = 1

            # -1 : Downward Crossover
            # Bear Signal
            elif prev_close >= prev_atr_trailing_stop and close <= atr_trailing_stop :
                df.at[i, 'Crossover'] = -1

        return df
    
    except Exception as e:
        print("if_crossover() Exception", e)

def get_ohlc():
    try:
        df = concat_df()
        df = calculate_rsi(df)
        df = calculate_atr(df)
        df = calculate_atr_trailing_stop(df)
        df = if_crossover(df)
        df = df.tail(96)

        return df
    
    except Exception as e:
        print("get_ohlc() Exception", e)