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

leverage = 1

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

def enter_long(amount, price):
    try :
        orders = [None] * 3

        orders[0] = binance.create_market_buy_order(
            symbol=ohlc.symbol,
            amount=amount,
        )
        time.sleep(0.5)

        tp = round(1.005 * price, 5)
        sl = round(0.990 * price, 5)

        print("TP :", tp, " SL :", sl)

        orders[1] = binance.create_order(
            symbol=ohlc.symbol,
            type="TAKE_PROFIT_MARKET",
            side="sell",
            amount=amount,
            params={
                'stopPrice': tp
                }
        )
        time.sleep(0.5)

        orders[2] = binance.create_order(
            symbol=ohlc.symbol,
            type="STOP_MARKET",
            side="sell",
            amount=amount,
            params={
                'stopPrice': sl
                }
        )
        time.sleep(0.5)

        for order in orders :
            print(order)

    except Exception as e:
        print("buy() Exception", e)

def cancel_all_open_orders(symbol):
    try:
        binance.cancel_all_orders(symbol=symbol)
        print("모든 열려 있는 주문이 취소되었습니다.")
    
    except Exception as e:
        print("cancel_all_open_orders() Exception:", e)

if __name__ == "__main__" :
    post_leverage()
    ohlc_df = ohlc.get_ohlc()
    price = ohlc_df.iloc[-1]['Close']
    amount = 100
    enter_long(100, price)
    cancel_all_open_orders(ohlc.symbol)