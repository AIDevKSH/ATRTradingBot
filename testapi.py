import ccxt 
from dotenv import load_dotenv
import os
load_dotenv()
import time
import ohlc

# 거래가 제대로 되는지 확인하는 소스
# 거래 시 수수료 나감
# 공매도 포지션 진입, 종료 시 시세 차이로 인해 돈 더 나갈 수도 있음

leverage = 1
symbol = "DOGEUSDT"
amount = 100

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

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
        resp = binance.fapiprivate_post_leverage({
            'symbol': symbol,
            'leverage': leverage,
        })
        time.sleep(0.5)
        return resp
    
    except Exception as e:
        print("post_leverage() Exception:", e)


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

def my_position():
    try :
        #  prev_position Value
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

if __name__ == "__main__" :
    post_leverage()

    ohlc.position_decision()

    sell(amount)
    prev_position, prev_amount = my_position()
    print("숏 :", prev_position)
    print("amount :", prev_amount)
    time.sleep(5)

    buy(amount)
    prev_position, prev_amount = my_position()
    print("position :", prev_position)
    print("amount :", prev_amount)
    time.sleep(5)

    buy(amount)
    prev_position, prev_amount = my_position()
    print("롱 :", prev_position)
    print("amount :", prev_amount)
    time.sleep(5)

    sell(amount)
    prev_position, prev_amount = my_position()
    print("position :", prev_position)
    print("amount :", prev_amount)