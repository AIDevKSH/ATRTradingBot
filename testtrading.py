import ohlc
import ccxt 
import time
import warnings
warnings.filterwarnings('ignore')
from dotenv import load_dotenv
import os
load_dotenv()

# Set Leverage
leverage = 5

# ==================================================================== #

#  Crossover
#  0 : Initial value, No Crossover 

#  1 : Upward Crossover
# Bull Signal
# prev_close <= prev_atr_trailing_stop and open >= atr_trailing_stop
# prev_open  <= prev_atr_trailing_stop and open >= atr_trailing_stop

# -1 : Downward Crossover
# Bear Signal
# prev_close >= prev_atr_trailing_stop and open <= atr_trailing_stop
# prev_open  >= prev_atr_trailing_stop and open <= atr_trailing_stop

# ==================================================================== #

# Decision 

# Enter Long,  Close Short (If I Have)
# crossover == 1  and open >= ema

# Enter Short, Close Long  (If I Have)
# crossover == -1 and open <= ema

# Close Short
# crossover == 1  and open < ema

# Close Long
# crossover == -1 and open > ema

# Else
# Hold Position

# ==================================================================== #

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
    try :
        open = df.iloc[-1]['Open']
        ema = df.iloc[-1]['EMA_14']
        crossover = df.iloc[-1]['Crossover']

        if crossover == 0 :
            print("Hold Position")
            return

        else : 
            prev_position, prev_amount = my_position()

            usdt = get_balance()
            amount = calculate_amount(usdt, ohlc.current_df)

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

            # Enter Short
            elif crossover == -1 and open <= ema :
                # Close Long
                if prev_position == 1 :
                    buy(prev_amount)
                    print("Close Long Position")
                # Enter Short
                sell(amount)

            elif crossover == -1 and open > ema :
                # Close Long
                if prev_position == 1 :
                    buy(prev_amount)
                    print("Close Long Position")
    except Exception as e:
        print("make_decision() Exception:", e)

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
    # return ohlc.ohlc_df, ohlc.current_df

    ohlc.ohlc_df.loc[(ohlc.ohlc_df['Crossover'] == 1) & (ohlc.ohlc_df['Open'] >= ohlc.ohlc_df['EMA_14']), 'Decision'] = 1
    ohlc.ohlc_df.loc[(ohlc.ohlc_df['Crossover'] == -1) & (ohlc.ohlc_df['Open'] <= ohlc.ohlc_df['EMA_14']), 'Decision'] = -1

    print_df = ohlc.ohlc_df.tail(2)
    print("\n", print_df[['Timestamp', 'Open' ,'Close', 'EMA_14', 'Crossover', 'Decision']], "\n")

    make_decision(ohlc.current_df)
    # Trading

if __name__ == "__main__" :
    post_leverage()
    job()