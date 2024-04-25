#!/usr/bin/env python3
import sys
sys.path.append('/home/ec2-user/.local/lib/python3.9/site-packages')
# 1,2,3번 줄은 EC2에서 작동시킬 때에만 필요한 코드. 다른 환경에서 작동시킬 때는 지워야됨.
import ccxt
import time
import warnings
warnings.filterwarnings('ignore')
from dotenv import load_dotenv
import os
load_dotenv()
from datetime import datetime
import ohlc

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

leverage = 10

binance = ccxt.binance(config={
    'apiKey': api_key, 
    'secret': api_secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

def post_leverage():
    try:
        binance.fapiprivate_post_leverage({
            'symbol': ohlc.symbol,
            'leverage': leverage,
        })
        time.sleep(0.5)
    
    except Exception as e:
        print("post_leverage() Exception:", e)

def get_balance():
    try :
        balance = binance.fetch_balance(params={"type": "future"})
        free_balance = balance['free']
        usdt = free_balance['USDT']
        time.sleep(0.5)
        return usdt
    
    except Exception as e:
        print("get_balance() Exception", e)

def calculate_amount(usdt, df):
    try :
        price = df.iloc[-1]['Close']
        if usdt > price:
            amount = usdt / price
            amount = int(amount) - 1
            return amount
        elif usdt < price:
            # I plan to update it later
            amount = 0
            return amount
        else:
            amount = 0
            return amount
        
    except Exception as e:
        print("calculate_amount() Exception", e)

def enter_long(amount, price):
    try :
        binance.create_market_buy_order(
            symbol=ohlc.symbol,
            amount=amount,
        )
        time.sleep(0.5)

        tp = round(1.005 * price, 5)
        sl = round(0.990 * price, 5)

        binance.create_order(
            symbol=ohlc.symbol,
            type="TAKE_PROFIT_MARKET",
            side="sell",
            amount=amount,
            params={'stopPrice': tp}
        )
        time.sleep(0.5)

        binance.create_order(
            symbol=ohlc.symbol,
            type="STOP_MARKET",
            side="sell",
            amount=amount,
            params={'stopPrice': sl}
        )
        time.sleep(0.5)

        print(datetime.now().strftime("%Y-%m-%d %H:%M"))
        print("[Long] Price :", price, ", Amount :", amount, "TP :", tp, " SL :", sl)

    except Exception as e:
        print("enter_long() Exception", e)

def close_short(amount, price):
    try :
        binance.create_market_buy_order(
            symbol=ohlc.symbol,
            amount=amount,
        )
        time.sleep(0.5)
        print(datetime.now().strftime("%Y-%m-%d %H:%M"))
        print("[Close Short] Price :", price)

    except Exception as e:
        print("buy() Exception", e)

def enter_short(amount, price):
    try :
        binance.create_market_sell_order(
            symbol=ohlc.symbol,
            amount=amount,
        )
        time.sleep(0.5)

        tp = round(0.995 * price, 5)
        sl = round(1.010 * price, 5)

        binance.create_order(
            symbol=ohlc.symbol,
            type="TAKE_PROFIT_MARKET",
            side="buy",
            amount=amount,
            params={'stopPrice': tp}
        )
        time.sleep(0.5)

        binance.create_order(
            symbol=ohlc.symbol,
            type="STOP_MARKET",
            side="buy",
            amount=amount,
            params={'stopPrice': sl}
        )
        time.sleep(0.5)

        print(datetime.now().strftime("%Y-%m-%d %H:%M"))
        print("[Enter Short] Price :", price, ", amount :", amount, "TP :", tp, " SL :", sl)

    except Exception as e:
        print("enter_short() Exception", e)

def close_long(amount, price):
    try :
        binance.create_market_sell_order(
            symbol=ohlc.symbol,
            amount=amount,
        )
        time.sleep(0.5)
        print(datetime.now().strftime("%Y-%m-%d %H:%M"))
        print("[Close Long] Price :", price)

    except Exception as e:
        print("sell() Exception", e)

def cancel_all_orders(symbol):
    try:
        binance.cancel_all_orders(symbol=symbol)
        time.sleep(0.5)
    
    except Exception as e:
        print("cancel_all_open_orders() Exception:", e)

def my_position():
    try :
        #  prev_position
        #  0 : Initial Value, Have No Position
        #  1 : Prev Positon is Long
        # -1 : Prev Position is Short

        balance = binance.fetch_balance()
        positions = balance['info']['positions']

        for position in positions:
            if position["symbol"] == ohlc.symbol:
                if float(position['positionAmt']) != 0:
                    prev_amount = float(position['positionAmt'])
                    if prev_amount > 0 : 
                        prev_position = 1
                    else :
                        prev_position = -1
                        prev_amount = abs(prev_amount)
                else:
                    prev_position = 0
                    prev_amount = 0

                return prev_position, prev_amount
            
    except Exception as e:
        print("my_position() Exception", e)

def close_position(df, prev_position, prev_amount) :
    try :
        crossover = df.iloc[-1]['Crossover']
        price = df.iloc[-1]['Close']

        if crossover == 1 and prev_position == -1 :
            close_short(prev_amount, price)
            cancel_all_orders(ohlc.symbol)
                
        elif crossover == -1 and prev_position == 1 :
            close_long(prev_amount, price)
            cancel_all_orders(ohlc.symbol)

    except Exception as e :
        print("end_position() Exception", e)

def enter_position(df, prev_position) :
    try :
        if prev_position != 0 : 
            return
        else :
            crossover = df.iloc[-2]['Crossover']
            price = df.iloc[-1]['Close']
            usdt = get_balance()
            amount = calculate_amount(usdt, df.tail(1))

            if crossover == 1 :
                enter_long(amount, price)

            elif crossover == -1 :
                enter_short(amount, price)

    except Exception as e :
        print("enter_position() Exception", e)
    
if __name__ == "__main__" :
    post_leverage()
    ohlc_df = ohlc.get_ohlc()
    prev_position, prev_amount = my_position()
    close_position(ohlc_df, prev_position, prev_amount)
    enter_position(ohlc_df, prev_position)