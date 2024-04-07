import pandas as pd
import numpy as np
from binance.client import Client
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
load_dotenv()

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
client = Client(api_key=api_key, api_secret=api_secret)

# Inputs
sensitivity = 2  # n_loss = sensitivity * atr'

# Define the symbol and interval
symbol = 'BNBUSDT'
interval = '30m'

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

# Initial position
pos = 0
atr_sum = 0
period = 14
prev_close = ohlc_data[0][4]
atr_trailing_stop = 0.0

# Function to calculate position
def calculate_position(close, atr_trailing_stop, pos):
    atr_trailing_stop_prev = atr_trailing_stop[-1] if len(atr_trailing_stop) > 0 else 0
    
    if close[-2] < atr_trailing_stop_prev and close[-1] > atr_trailing_stop_prev:
        return 1
    elif close[-2] > atr_trailing_stop_prev and close[-1] < atr_trailing_stop_prev:
        return -1
    else:
        return pos

# Define a function to calculate EMA
def calculate_ema(data, window):
    weights = np.exp(np.linspace(-1., 0., window))
    weights /= weights.sum()
    ema = np.convolve(data, weights, mode='full')[:len(data)]
    ema[:window] = ema[window]
    return ema[-1]

# Function to check crossover
def if_crossover(atr_trailing_stop, ema, prev_atr_trailing_stop, prev_ema):
    if ema > atr_trailing_stop and prev_ema < prev_atr_trailing_stop:
        crossover = "above"
    elif atr_trailing_stop > ema and prev_atr_trailing_stop < ema:
        crossover = "below"
    else:
        crossover = "no"
    
    return crossover

# Function to make position decision
def position_decision(crossover, close, atr_trailing_stop, rsi):
    if close > atr_trailing_stop and crossover == "above" and rsi > 55:
        position = "Long Position"
    elif close > atr_trailing_stop and crossover == "above" and rsi < 45:
        position = "Long Position"
    elif close < atr_trailing_stop and crossover == "below" and rsi > 55:
        position = "Short Position"
    elif close < atr_trailing_stop and crossover == "below" and rsi < 45:
        position = "Short Position"
    elif close < atr_trailing_stop and crossover == "below" and 45<= rsi <= 55:
        position = "Close Long Position"
    elif close > atr_trailing_stop and crossover == "above" and 45<= rsi <= 55:
        position = "Close Short Position"
    else:
        position = "Hold"
    
    return position

# Function to calculate RSI
def calculate_rsi14(data):
    df = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Change'] = df['Close'].diff()

    upward_change = df['Change'][df['Change'] > 0].mean()
    downward_change = -df['Change'][df['Change'] < 0].mean()

    rsi = 100 - (100 / (1 + (upward_change / downward_change)))

    return rsi

# Function to calculate ATR
def calculate_atr():
    global prev_close
    atr_sum = 0
    for i in range(period, len(ohlc_data)):
        high = ohlc_data[i][2]
        low = ohlc_data[i][3]
        close = ohlc_data[i][4]
        
        tr1 = abs(high - low)
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        
        true_range = max(tr1, tr2, tr3)
        
        atr_sum += true_range
        
        prev_close = close

    atr = atr_sum / period

    return atr

# Function to calculate trailing stop
def calculate_trailing_stop(close, atr_trailing_stop, n_loss, pos):
    if close > atr_trailing_stop:
        atr_trailing_stop = max(atr_trailing_stop, close - n_loss)
        pos = 1
    elif close < atr_trailing_stop:
        atr_trailing_stop = min(atr_trailing_stop, close + n_loss)
        pos = -1
    else:
        if close > atr_trailing_stop:
            atr_trailing_stop = close - n_loss
        else:
            atr_trailing_stop = close + n_loss
        pos = 0
    
    return atr_trailing_stop, pos

# Main logic starts here

# Calculate ATR
atr = calculate_atr()

# Calculate n_loss
n_loss = sensitivity * atr

# Calculate trailing stop
atr_trailing_stop, pos = calculate_trailing_stop(close_price, atr_trailing_stop, n_loss, pos)

# Calculate last position
last_close_price = [data[4] for data in ohlc_data[-2:]]  # Get the last two closing prices
last_pos = calculate_position(last_close_price, [atr_trailing_stop], pos)

# Calculate EMA
close_prices = [data[4] for data in ohlc_data]
ema_period = 14
ema = calculate_ema(close_prices, ema_period)

# Print results
print("Price:", close_prices)
print("ATR:", atr)
print("atr_trailing_stop:", atr_trailing_stop)
print("Position:", last_pos)
print("Latest EMA:", ema)

# Calculate previous trailing stop and EMA
prev_close_price = ohlc_data[-2][4]
prev_n_loss = sensitivity * atr
prev_atr_trailing_stop, prev_pos = calculate_trailing_stop(prev_close_price, atr_trailing_stop, prev_n_loss, pos)
prev_ema_period = 14
prev_close_prices = [data[4] for data in ohlc_data[:-1]]
prev_ema = calculate_ema(prev_close_prices, prev_ema_period)

print("Previous atr_trailing_stop:", prev_atr_trailing_stop)
print("Previous EMA:", prev_ema)

# Calculate RSI
rsi = calculate_rsi14(ohlc_data)
print("RSI:", rsi)

# Check crossover
crossover = if_crossover(atr_trailing_stop, ema, prev_atr_trailing_stop, prev_ema)
position = position_decision(crossover, close_price, atr_trailing_stop,rsi)

print("Crossover:", crossover)
print("Position decision:", position)