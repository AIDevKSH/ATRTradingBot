import trading
import ccxt
import warnings
warnings.filterwarnings('ignore')
from dotenv import load_dotenv
import os
load_dotenv()

# trading.py를 한 번 바로 실행하는 파일
# 거래 시그널이 나온 경우, 실제 거래가 이루어짐

leverage = 1

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

if __name__ == "__main__" :
    trading.post_leverage()
    trading.job()