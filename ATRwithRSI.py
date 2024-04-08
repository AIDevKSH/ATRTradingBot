import pandas as pd
from binance.client import Client
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
load_dotenv()

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
client = Client(api_key=api_key, api_secret=api_secret)

symbol = 'BNBUSDT'
interval = '30m'

def get_ohlc():
    # Calculate start and end time for the query
    end_time = datetime.now()
    start_time = end_time - timedelta(days=14)

    # Convert time to milliseconds (Binance API requires timestamps in milliseconds)
    start_timestamp = int(start_time.timestamp() * 1000)
    end_timestamp = int(end_time.timestamp() * 1000)

    # Request historical kline data
    klines = client.get_historical_klines(symbol, interval, start_timestamp, end_timestamp)

    # Extract OHLCV data (Open, High, Low, Close, Volume)
    ohlc_data = []
    for kline in klines:
        timestamp = datetime.fromtimestamp(kline[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        open_price = float(kline[1])
        high_price = float(kline[2])
        low_price = float(kline[3])
        close_price = float(kline[4])
        volume = float(kline[5])
        ohlc_data.append([timestamp, open_price, high_price, low_price, close_price, volume])

    # print(ohlc_data)

    # Assuming ohlc_data is your list of OHLCV data
    ohlc_df = pd.DataFrame(ohlc_data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])

    # Convert 'Timestamp' column to datetime type
    ohlc_df['Timestamp'] = pd.to_datetime(ohlc_df['Timestamp'])

    # print(ohlc_df)

    return ohlc_df

def get_current_price(df):
    df = df.tail(1)
    current_price = float(df['Close'])

    return current_price

def calculate_atr(df):
    # Step 1: Calculate True Range (TR)
    df['High-Low'] = df['High'] - df['Low']
    df['High-PreviousClose'] = abs(df['High'] - df['Close'].shift(1))
    df['Low-PreviousClose'] = abs(df['Low'] - df['Close'].shift(1))
    df['TrueRange'] = df[['High-Low', 'High-PreviousClose', 'Low-PreviousClose']].max(axis=1)

    # Step 2: Calculate Average True Range (ATR)
    period = 14  # Change this to your desired period
    df['ATR'] = df['TrueRange'].rolling(period).mean()

    # Drop temporary columns
    df.drop(['High-Low', 'High-PreviousClose', 'Low-PreviousClose', 'TrueRange'], axis=1, inplace=True)
    
    return df

def calculate_rsi(df):
    df['Change'] = df['Close'].diff()

    upward_change = df['Change'][df['Change'] > 0].mean()
    downward_change = -df['Change'][df['Change'] < 0].mean()

    rsi = 100 - (100 / (1 + (upward_change / downward_change)))
    
    return rsi

def calculate_atr_trailing_stop(df):
    # df = df.tail(10)
    atr_trailing_stop = pd.Series(index=df.index)

    for i in range(1, len(df)):
        n_loss = df.iloc[i]['ATR'] * 2
        close = df.iloc[i]['Close']
        prev_close = df.iloc[i - 1]['Close']
        prev_atr_trailing_stop = atr_trailing_stop.iloc[i - 1]

        if close > prev_atr_trailing_stop and prev_close > prev_atr_trailing_stop:
            atr_trailing_stop.iloc[i] = max(prev_atr_trailing_stop, close - n_loss)
        elif close < prev_atr_trailing_stop and prev_close < prev_atr_trailing_stop:
            atr_trailing_stop.iloc[i] = min(prev_atr_trailing_stop, close + n_loss)
        elif close > prev_atr_trailing_stop:
            atr_trailing_stop.iloc[i] = close - n_loss
        else:
            atr_trailing_stop.iloc[i] = close + n_loss

    df['ATR_Trailing_Stop'] = atr_trailing_stop

    df = df.tail(20)

    return df

def if_crossover(df):
    #  0 : initial value, no crossover 
    #  1 : upward crossover
    # -1 : downward crossover

    df = df.tail(2)
    
    prev_close = df.iloc[0]['Close']
    close = df.iloc[1]['Close']
    
    prev_atr_trailing_stop = df.iloc[0]['ATR_Trailing_Stop']
    atr_trailing_stop = df.iloc[1]['ATR_Trailing_Stop']

    if close > atr_trailing_stop and prev_close < prev_atr_trailing_stop:
        crossover = 1
    elif atr_trailing_stop > close and prev_atr_trailing_stop < close:
        crossover = -1
    else:
        crossover = 0

    return crossover

def position_decision(df, crossover, rsi):
    #  0 : Hold 
    #  1 : Enter Long  Position, Close Short Position
    # -1 : Enter Short Position, Close Long Position
    #  2 : Close Long  Positon
    # -2 : Close Short Position
    df = df.tail(1)
    close = df.iloc[0]['Close']
    atr_trailing_stop = df.iloc[0]['ATR_Trailing_Stop']

    if close > atr_trailing_stop and crossover == 1 and rsi > 55:
        position = 1
    elif close > atr_trailing_stop and crossover == 1 and rsi < 45:
        position = 1
    elif close < atr_trailing_stop and crossover == -1 and rsi > 55:
        position = -1
    elif close < atr_trailing_stop and crossover == -1 and rsi < 45:
        position = -1
    elif close < atr_trailing_stop and crossover == -1 and 45 <= rsi <= 55:
        position = 2
    elif close > atr_trailing_stop and crossover == 1 and 45 <= rsi <= 55:
        position = -2
    else:
        position = 0

    return position

if __name__ == "__main__":
    ohlc_df = get_ohlc()
    current_price = get_current_price(ohlc_df)
    ohlc_df = calculate_atr(ohlc_df)
    ohlc_df = calculate_atr_trailing_stop(ohlc_df) # Data Frame
    rsi = calculate_rsi(ohlc_df) # Most Recent Value
    
    crossover = if_crossover(ohlc_df)
    #  0 : Initial Value, No Crossover 
    #  1 : Upward Crossover
    # -1 : Downward Crossover

    decision = position_decision(ohlc_df, crossover, rsi)
    #  0 : Hold 
    #  1 : Enter Long  Position, Close Short Position
    # -1 : Enter Short Position, Close Long Position
    #  2 : Close Long  Positon
    # -2 : Close Short Position

    print(ohlc_df)
    print(decision)
    print(current_price)

