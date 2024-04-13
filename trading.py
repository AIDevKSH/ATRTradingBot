import ohlc
import ccxt 
import time
import warnings
warnings.filterwarnings('ignore')
from dotenv import load_dotenv
import os
load_dotenv()
import schedule

# Set Leverage
leverage = 5

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

def make_decision(df):
    open = df.iloc[-1]['Open']
    ema = df.iloc[-1]['EMA_14']
    crossover = df.iloc[-1]['Crossover']

    if crossover == 0 :
        print("Hold Position")
        return

    else : 
        usdt = get_balance()
        amount = calculate_amount(usdt, ohlc.current_df)
        prev_position, prev_amount = my_position()

        print("Prev Position :", prev_position)
        print("Prev Amount :", prev_amount)
        print("My Free USDT : ", usdt)
        print("Amount To Trade :", amount)

        #  prev_position Value
        #  0 : Initial Value, Have No Position
        #  1 : Prev Positon is Long
        # -1 : Prev Position is Short

        # Enter Long
        if crossover == 1 and open >= ema :
            # Close Short
            if prev_position == -1 :
                sell(prev_amount)
                print("Close Short Position")
            # Enter Long
            buy(amount)

        elif crossover == 1 and open < ema :
            # Close Short
            if prev_position == -1 :
                sell(prev_amount)
                print("Close Short Position")
            else : 
                print("Have No Short Position")

        # Enter Short
        elif crossover == -1 and open <= ema :
            # Close Long
            if prev_position == 1 :
                sell(prev_amount)
                print("Close Long Position")
            # Enter Short
            sell(amount)

        elif crossover == -1 and open > ema :
            # Close Long
            if prev_position == 1 :
                sell(prev_amount)
                print("Close Long Position")
            else :
                print("Have no Long Position")
        

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


def job() :
    ohlc.position_decision()
    # return current_df

    make_decision(ohlc.current_df)
    # Trading

def every_15_minutes():
    schedule.every(15).minutes.do(job)

    schedule.every().hour.at(":00").do(job)
    schedule.every().hour.at(":15").do(job)
    schedule.every().hour.at(":30").do(job)
    schedule.every().hour.at(":45").do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__" :
    post_leverage()
    every_15_minutes()