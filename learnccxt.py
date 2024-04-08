import ccxt 
from dotenv import load_dotenv
import os
load_dotenv()
import time

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

symbol = 'DOGEUSDT'
leverage = 1
margin_type = 'ISOLATED'

def get_balance():
    # 현재 usdt 잔고
    balance = binance.fetch_balance(params={"type": "future"})
    # print(balance['USDT'])
    return balance
    # {'free': 49.1918193, 'used': 0.0, 'total': 49.20165886}

def enter_long():
    # 레버리지 롱 포지션
    
    resp = binance.fapiPrivate_post_leverage({
        'symbol': symbol,
        'leverage': leverage,
    })

    resp2 = binance.fapiprivate_post_margintype({
        'symbol': symbol,
        'marginType': margin_type,
    })

    order = binance.create_market_buy_order(
        symbol=symbol,
        amount=1,
    )
    
    return resp, resp2, order

def close_long():

    order2 = binance.create_market_sell_order(
        symbol=symbol,
        amount=1,
    )
    
    return order2

def my_position():
    balance = binance.fetch_balance()
    positions = balance['info']['positions']

    for position in positions:
        if position["symbol"] == symbol:
            return position

if __name__ == "__main__":

    print("포지션 진입")

    balance = get_balance()
    print(balance)
    time.sleep(2)
    
    resp, resp2, order = enter_long()
    print(resp)
    print(resp2)
    print(order)

    time.sleep(2)

    position = my_position()
    print(position)

    time.sleep(2)

    print("포지션 종료")
    order2 = close_long()
    print(order2)

    time.sleep(2)

    position = my_position()
    print(position)

    time.sleep(2)

    balance = get_balance()
    print(balance)
