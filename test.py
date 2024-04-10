import pandas as pd
from binance.client import Client
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
load_dotenv()
import ccxt 
import time
import warnings
warnings.filterwarnings('ignore')
import schedule

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
client = Client(api_key=api_key, api_secret=api_secret)

binance = ccxt.binance(config={
    'apiKey': api_key, 
    'secret': api_secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

symbol = 'ENAUSDT'
interval = '30m'
leverage = 5

import time

def post_leverage():
    try:
        resp = binance.fapiprivate_post_leverage({
            'symbol': symbol,
            'leverage': leverage,
        })
        time.sleep(0.5)
        return resp
    
    except Exception as e:
        print("post_leverage() Exception:", e)

def get_ohlc():
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(days=14)

        print(end_time.strftime("%Y-%m-%d %H:%M"))

        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)

        klines = client.get_historical_klines(symbol, interval, start_timestamp, end_timestamp)

        ohlc_data = []
        for kline in klines:
            timestamp = datetime.fromtimestamp(kline[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            volume = float(kline[5])
            ohlc_data.append([timestamp, open_price, high_price, low_price, close_price, volume])

        ohlc_df = pd.DataFrame(ohlc_data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])

        ohlc_df['Timestamp'] = pd.to_datetime(ohlc_df['Timestamp'])

        time.sleep(0.5)

        return ohlc_df
    except Exception as e:
        print("get_ohlc() Exception:", e)

def get_current_price(df):
    try :
        df = df.tail(1)
        current_price = float(df['Close'])

        return current_price
    
    except Exception as e:
        print("get_current_price() Exception", e)

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

def calculate_rsi(df):
    try :
        df['Change'] = df['Close'].diff()

        upward_change = df['Change'][df['Change'] > 0].mean()
        downward_change = -df['Change'][df['Change'] < 0].mean()

        rsi = 100 - (100 / (1 + (upward_change / downward_change)))
        
        return rsi
    
    except Exception as e:
        print("calculate_rsi() Exception", e)

def calculate_atr_trailing_stop(df):
    try:
        atr_trailing_stop = pd.Series(index=df.index)
        df['ATR_Trailing_Stop'] = df['Close'].iloc[0]
        print(df)
        
        for i in range(1, len(df)):
            n_loss = df.iloc[i]['ATR'] * 2
            close = df.iloc[i]['Close']
            prev_close = df.iloc[i - 1]['Close']
            prev_atr_trailing_stop = df.iloc[i - 1]['ATR_Trailing_Stop']

            if close > prev_atr_trailing_stop and prev_close > prev_atr_trailing_stop:
                df.at[i, 'ATR_Trailing_Stop'] = max(prev_atr_trailing_stop, close - n_loss)
            elif close < prev_atr_trailing_stop and prev_close < prev_atr_trailing_stop:
                df.at[i, 'ATR_Trailing_Stop'] = min(prev_atr_trailing_stop, close + n_loss)
            elif close > prev_atr_trailing_stop:
                df.at[i, 'ATR_Trailing_Stop'] = close - n_loss
            else:
                df.at[i, 'ATR_Trailing_Stop'] = close + n_loss

        df = df.tail(20)

        return df
    
    except Exception as e:
        print("calculate_atr_trailing_stop() Exception", e)

def if_crossover(df):
    try :
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

        print("crossover :",crossover)
        return crossover
        
    except Exception as e:
        print("if_crossover() Exception", e)

def position_decision(df, crossover, rsi):
    try :
        #  0 : Hold 
        #  1 : Enter Long  Position, Close Short Position
        # -1 : Enter Short Position, Close Long Position
        #  2 : Close Long  Positon
        # -2 : Close Short Position
        df = df.tail(1)
        close = df.iloc[0]['Close']
        atr_trailing_stop = df.iloc[0]['ATR_Trailing_Stop']

        if close > atr_trailing_stop and crossover == 1 and rsi > 55:
            decision = 1
        elif close > atr_trailing_stop and crossover == 1 and rsi < 45:
            decision = 1
        elif close < atr_trailing_stop and crossover == -1 and rsi > 55:
            decision = -1
        elif close < atr_trailing_stop and crossover == -1 and rsi < 45:
            decision = -1
        elif close < atr_trailing_stop and crossover == -1 and 45 <= rsi <= 55:
            decision = 2
        elif close > atr_trailing_stop and crossover == 1 and 45 <= rsi <= 55:
            decision = -2
        else:
            decision = 0

        return decision
    
    except Exception as e:
        print("position_decision() Exception", e)

def chart_analysis(): 
    try :
        ohlc_df = get_ohlc()
        
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

        print(ohlc_df.tail(10))
        print("RSI :",rsi)
        print("decision :",decision)

        return decision, ohlc_df
    
    except Exception as e:
        print("chart_analysis() Exception", e)

def get_balance():
    try :
        balance = binance.fetch_balance(params={"type": "future"})
        free_balance = balance['free']
        usdt = free_balance['USDT']
        time.sleep(0.5)
        return usdt
    
    except Exception as e:
        print("get_balance() Exception", e)

def calculate_amount(usdt, current_price):
    try :
        if usdt > current_price:
            amount = usdt / current_price / 3
            amount = int(amount) - 1
            return amount
        elif usdt < current_price:
            # 여기 나중에 다시 계산해야됨
            amount = 0
            return amount
        else:
            amount = 0
            return amount
        
    except Exception as e:
        print("calculate_amount() Exception", e)

def before_trade(ohlc_df):
    try:
        current_price = get_current_price(ohlc_df)
        time.sleep(0.5)

        usdt = get_balance() # My Account
        
        amount = calculate_amount(usdt, current_price)

        time.sleep(0.5)

        if_position, prev_amount = my_position()
        time.sleep(0.5)

        return if_position, prev_amount, amount
    
    except Exception as e:
        print("before_trade() Exception", e)

def my_position():
    try :
        #  if_position Value
        #  0 : Initial Value, Have No Position
        #  1 : Prev Positon is Long
        # -1 : Prev Position is Short

        balance = binance.fetch_balance()
        positions = balance['info']['positions']

        for position in positions:
            if position["symbol"] == symbol:
                if float(position['positionAmt']) != 0:
                    prev_amount = float(position['positionAmt'])
                    if prev_amount > 0 : 
                        if_position = 1
                    else :
                        if_position = -1
                        prev_amount = abs(prev_amount)
                else:
                    if_position = 0
                    prev_amount = 0

                return if_position, prev_amount
            
    except Exception as e:
        print("my_position() Exception", e)

def buy(amount):
    try :
        binance.create_market_buy_order(
            symbol=symbol,
            amount=amount,
        )
        time.sleep(0.5)

    except Exception as e:
        print("buy() Exception", e)

def sell(amount):
    try :
        binance.create_market_sell_order(
            symbol=symbol,
            amount=amount,
        )
        time.sleep(0.5)

    except Exception as e:
        print("sell() Exception", e)

def if_trade(decision, ohlc_df):
    try :
        if decision == 0:
            return
        
        if_position, prev_amount, amount = before_trade(ohlc_df)

        #  decision Value
        #  0 : Hold 
        #  1 : Enter Long  Position, Close Short Position (If I have)
        # -1 : Enter Short Position, Close Long Position  (If I have)
        #  2 : Close Long  Positon   (If I have)
        # -2 : Close Short Position  (If I have)

        #  if_position Value
        #  0 : Initial Value, Have No Position
        #  1 : Prev Positon is Long
        # -1 : Prev Position is Short

        # decision == 1
        if decision == 1 and if_position == -1:
            buy(prev_amount)
            buy(amount)

        elif decision == 1 and if_position != -1 and if_position != 1:
            buy(amount)

        elif decision == 1 and if_position == 1:
            return

        # decision == -1
        elif decision == -1 and if_position == 1:
            sell(prev_amount)
            sell(amount)

        elif decision == -1 and if_position != 1 and if_position != -1:
            sell(amount)

        elif decision == -1 and if_position == -1 :
            return

        # decision == 2
        elif decision == 2 and if_position == 1:
            sell(amount)

        # decision == -2
        elif decision == -2 and if_position == -1:
            buy(amount)
        
        else:
            return
        
    except Exception as e:
        print("if_trade() Exception", e)

def test():
        print("Symbol :",symbol,"")

        ohlc_df = None
        rsi = 0
        crossover = 0
        current_price = 0
        usdt = 0
        amount = 0
        decision = 0
        position = 0
        if_position = 0
        prev_amount = 0

        decision, ohlc_df = chart_analysis()
        time.sleep(0.5)
        if_trade(decision, ohlc_df)

if __name__ == "__main__":
    resp = post_leverage()
    test()