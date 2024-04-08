import ccxt 
from dotenv import load_dotenv
import os
load_dotenv()

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


balance = binance.fetch_balance(params={"type": "future"})
print(balance['USDT'])