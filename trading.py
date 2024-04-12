import ohlc
import ccxt 
import time
import warnings
warnings.filterwarnings('ignore')
from dotenv import load_dotenv
import os
load_dotenv()

symbol = 'ENAUSDT'
interval = '30m'
leverage = 5

#  Crossover : Position Desicion
#  0 : Initial value, No Crossover 

#  1 : Upward Crossover
# Enter Long Position, Close Short Position
# prev_close <= prev_atr_trailing_stop and open >= atr_trailing_stop
# prev_open <= prev_atr_trailing_stop and open >= atr_trailing_stop

# -1 : Downward Crossover
# Enter Short Position, Close Enter Position
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
            'symbol': symbol,
            'leverage': leverage,
        })
        time.sleep(0.5)
        return resp
    
    except Exception as e:
        print("post_leverage() Exception:", e)



# 15분 마다 반복할 거 

# Initialize
ohlc_df = None
crossover = 0
end_time = None

ohlc.position_decision()