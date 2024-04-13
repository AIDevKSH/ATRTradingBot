import pandas as pd
from binance.client import Client
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
load_dotenv()
import warnings
warnings.filterwarnings('ignore')
import mplfinance as mpf

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
client = Client(api_key=api_key, api_secret=api_secret)

# ohlc.py 실행 시 맨 아래 함수들 주석 풀어주세요.
# trading.py 실행하려면 다시 주석 걸어주세요.

# 종목
global symbol
symbol = 'DOGEUSDT'
# BTC 가격 변동량이 크지 않아서 노잼
# ENAUSDT 같이 신상 코인들이 변동폭이 더 커서 잼슴

# 간격
global interval
interval = '15m'
# 5분 15분 30분 다 해봤는데
# 15분이 내가 쓰기 좋은듯

# n_loss = ATR * loss_value
# 종가에 n_loss 더하거나 빼거나 해서 트레일링 스탑 구함
loss_value = 2
# loss_value가 낮을수록 트레일링 스탑 민감해짐
# 너무 민감하면 이거저거 다 배팅해서 오히려 안 좋을지도
# 너무 둔감하면 거래를 안 함
# 1, 1.5, 2, 2.5, 3.0, 3.5, 4까지 해봄
# 그래프 주석 풀고 확인 가능

global current_df

def get_ohlc_hourly():
    try:
        interval = '1h'
        end_time = datetime.now() - timedelta(days=2)
        start_time = end_time - timedelta(days=14)

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

def get_ohlc_half_hourly():
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(days=2)

        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)

        klines = client.get_historical_klines(symbol, interval, start_timestamp, end_timestamp)

        ohlc_half_hourly = []
        for kline in klines:
            timestamp = datetime.fromtimestamp(kline[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            volume = float(kline[5])
            ohlc_half_hourly.append([timestamp, open_price, high_price, low_price, close_price, volume])

        ohlc_half_hourly = pd.DataFrame(ohlc_half_hourly, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])

        ohlc_half_hourly['Timestamp'] = pd.to_datetime(ohlc_half_hourly['Timestamp'])

        return ohlc_half_hourly
    
    except Exception as e:
        print("get_ohlc_half_hourly() Exception:", e)

def get_ohlc():
    ohlc_hour = get_ohlc_hourly()
    ohlc_half_hourly = get_ohlc_half_hourly()
    ohlc_df = pd.concat([ohlc_hour, ohlc_half_hourly])
    ohlc_df['EMA_14'] = ohlc_df['Close'].ewm(span=14, min_periods=0, adjust=False).mean()
    return ohlc_df

def calculate_atr(df):
    try :
        df['High-Low'] = df['High'] - df['Low']
        df['High-PreviousClose'] = abs(df['High'] - df['Close'].shift(1))
        df['Low-PreviousClose'] = abs(df['Low'] - df['Close'].shift(1))
        df['TrueRange'] = df[['High-Low', 'High-PreviousClose', 'Low-PreviousClose']].max(axis=1)

        period = 96
        df['ATR'] = df['TrueRange'].rolling(period).mean()

        df.drop(['High-Low', 'High-PreviousClose', 'Low-PreviousClose', 'TrueRange'], axis=1, inplace=True)
        
        df = df.tail(96)
        
        return df
    
    except Exception as e:
        print("calculage_atr() Exception", e)

def calculate_atr_trailing_stop(df):
    try:
        df['ATR_Trailing_Stop'] = df['Close']
        df = df.reset_index()

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

        #  1 : Upward Crossover
        # Bull Signal
        # prev_close <= prev_atr_trailing_stop and open >= atr_trailing_stop
        # prev_open <= prev_atr_trailing_stop and open >= atr_trailing_stop

        # -1 : Downward Crossover
        # Bear Signal
        # prev_close >= prev_atr_trailing_stop and open <= atr_trailing_stop
        # prev_open >= prev_atr_trailing_stop and open <= atr_trailing_stop

        df['Crossover'] = 0

        for i in range(1, len(df)):
            prev_close = df.iloc[i-1]['Close']
            prev_open = df.iloc[i-1]['Open']
            prev_atr_trailing_stop = df.iloc[i-1]['ATR_Trailing_Stop']
            open = df.iloc[i]['Open']
            atr_trailing_stop = df.iloc[i]['ATR_Trailing_Stop']

            if prev_close <= prev_atr_trailing_stop and open >= atr_trailing_stop :
                df.at[i, 'Crossover'] = 1
            elif prev_open <= prev_atr_trailing_stop and open >= atr_trailing_stop :
                df.at[i, 'Crossover'] = 1
            elif prev_close >= prev_atr_trailing_stop and open <= atr_trailing_stop :
                df.at[i, 'Crossover'] = -1
            elif prev_open >= prev_atr_trailing_stop and open <= atr_trailing_stop :
                df.at[i, 'Crossover'] = -1
        
        return df
    except Exception as e:
        print("if_crossover() Exception", e)

def make_plot(ohlc_df):
    ohlc_df.set_index('Timestamp', inplace=True)
    
    ap = mpf.make_addplot(ohlc_df['ATR_Trailing_Stop'], color='blue')
    ap2 = mpf.make_addplot(ohlc_df['EMA_14'], color='orange')
    
    mpf.plot(ohlc_df, type='candle', style='charles', title='ATR Trailing Stop(Blue) EMA 14(Orange)',
             ylabel='Price', volume=True, addplot=[ap, ap2],
             figratio=(16, 9), figsize=(14, 7), xrotation=0)
    
def position_decision():
    df = get_ohlc()
    df  = calculate_atr(df)
    df = calculate_atr_trailing_stop(df)
    df = if_crossover(df)

    return df


ohlc_df = position_decision()
current_df = ohlc_df.tail(1)


# ohlc.py 실행 시에만 아래 주석 푸세요.
# trading.py에는 주석 걸어주세요.

# 1. 최근 두 데이터 정보 보기
# print_df = ohlc_df.tail(2)
# print("\n", print_df[['Timestamp', 'Open' ,'Close', 'EMA_14', 'ATR_Trailing_Stop', 'Crossover']], "\n")

# 2. 이틀 데이터 중 크로스 오버 한 데이터만 보기
# crossover_df =  ohlc_df[ohlc_df['Crossover'] != 0]
# print(crossover_df)

# 3. chart.png와 같은 그래프 출력하기
# make_plot(ohlc_df)