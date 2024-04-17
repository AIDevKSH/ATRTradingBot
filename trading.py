import sys
sys.path.append('/home/ec2-user/ATRTradingBot')
import ohlc
import ccxt 
import time
import warnings
warnings.filterwarnings('ignore')
from dotenv import load_dotenv
import os
load_dotenv()

leverage = 5

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
            'symbol': ohlc.symbol,
            'leverage': leverage,
        })
        time.sleep(0.5)
        return resp
    
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
        current_price = df.iloc[-1]['Close']
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

def buy(amount):
    try :
        binance.create_market_buy_order(
            symbol=ohlc.symbol,
            amount=amount,
        )
        time.sleep(0.5)

    except Exception as e:
        print("buy() Exception", e)

def sell(amount):
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

def make_decision(df) :
    try :
        crossover = df.iloc[-1]['Crossover']
        rsi = df.iloc[-1]['RSI']
        prev_position, prev_amount = my_position()
        usdt = get_balance()
        amount = calculate_amount(usdt, df.tail(1))

        if crossover == 0 :
            print("Hold Position. Crossover :", crossover)
            return
        
        else :

            if crossover == 1 and rsi <= 45 or rsi >= 55 :
                if prev_position == -1 :
                    buy(prev_amount)
                    print("Close Short Position. Prev Amount :", prev_amount)
                elif prev_position == 1 :
                    return
                buy(amount)
                print("Enter Long Position. Crossover :", crossover, " RSI :", rsi, " Amount :", amount)
                return

            elif crossover == -1 and rsi <= 45 or rsi >= 55 :
                if prev_position == 1 :
                    sell(prev_amount)
                    print("Close Long Position. Prev Amount :", prev_amount)
                elif prev_position == -1 :
                    return
                sell(amount)
                print("Enter Short Position. Crossover :", crossover, " RSI :", rsi, " Amount :", amount)
                return

            elif crossover == 1 and prev_position == -1 and rsi > 45 and rsi < 55 :
                buy(prev_amount)
                print("Close Short Position. Prev Amount :", prev_amount)
                return

            elif crossover == -1 and prev_position == 1 and rsi > 45 and rsi < 55 :
                sell(prev_amount)
                print("Close Long Position. Prev Amount :", prev_amount)
                return

    except Exception as e :
        print("make_decision() Exception", e)

if __name__ == "__main__" :
    post_leverage()
    ohlc_df = ohlc.get_ohlc()
    print(ohlc_df.tail(1))
    make_decision(ohlc_df)
    