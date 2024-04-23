#!/usr/bin/env python3
import sys
sys.path.append('/home/ec2-user/.local/lib/python3.9/site-packages')
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
            params={
                'positionSide': 'LONG',
                'stopPrice': tp
                }
        )
        time.sleep(0.5)

        binance.create_order(
            symbol=ohlc.symbol,
            type="STOP_MARKET",
            side="sell",
            amount=amount,
            params={
                'positionSide': 'LONG',
                'stopPrice': sl
                }
        )
        time.sleep(0.5)

        print("[Enter Long] Price :", price, ", amount :", amount)

    except Exception as e:
        print("buy() Exception", e)

def close_short(amount):
    try :
        binance.create_market_buy_order(
            symbol=ohlc.symbol,
            amount=amount,
        )
        time.sleep(0.5)

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
            params={
                'positionSide': 'SHORT',
                'stopPrice': tp
            }
        )
        time.sleep(0.5)

        binance.create_order(
            symbol=ohlc.symbol,
            type="STOP_MARKET",
            side="buy",
            amount=amount,
            params={
                'positionSide': 'SHORT',
                'stopPrice': sl
            }
        )
        time.sleep(0.5)

        print("[Enter Short] Price :", price, ", amount :", amount)

    except Exception as e:
        print("sell() Exception", e)

def close_long(amount):
    try :
        binance.create_market_sell_order(
            symbol=ohlc.symbol,
            amount=amount,
        )
        time.sleep(0.5)

    except Exception as e:
        print("sell() Exception", e)

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

# 포지션 정리는 crossover한 캔들
def close_position(df) :
    try :
        crossover = df.iloc[-1]['Crossover']
        prev_position, prev_amount = my_position()

        if crossover == 0 :
            return

        else :
            if crossover == 1 and prev_position == -1 :
                close_short(prev_amount)
                return

            elif crossover == -1 and prev_position == 1 :
                close_long(prev_amount)
                return

    except Exception as e :
        print("end_position() Exception", e)

# 포지션 진입은 crossover 캔들의 바로 다음 캔들
def enter_position(df, i=-2) :
    try :
        crossover = df.iloc[i]['Crossover']
        price = df.iloc[i+1]['Close']
        usdt = get_balance()
        amount = calculate_amount(usdt, df.tail(1))

        if crossover == 0 :
            return

        else :
            if crossover == 1 :
                enter_long(amount, price)
                return

            elif crossover == -1 :
                enter_short(amount, price)
                return

    except Exception as e :
        print("enter_position() Exception", e)
    
if __name__ == "__main__" :
    print(datetime.now().strftime("%Y-%m-%d %H:%M"))
    post_leverage()
    ohlc_df = ohlc.get_ohlc()
    close_position(ohlc_df)
    enter_position(ohlc_df)