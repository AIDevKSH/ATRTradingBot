from binance.client import Client
import time
from dotenv import load_dotenv
import os
load_dotenv()

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANACE_API_SECRET")
client = Client(api_key, api_secret)

# Binance 서버 시간 가져오기
server_time = client.get_server_time()
print(server_time)
server_timestamp = server_time['serverTime']

# 현재 시간을 가져와 타임스탬프로 변환하기
current_time = int(time.time() * 1000)

# 타임스탬프 확인하기
print('Server timestamp:', server_timestamp)
print('Current timestamp:', current_time)

# BTCUSDT 거래 내용 불러오기
trade_list = client.futures_account_trades(symbol="BTCUSDT") #,timestamp=current_time)


# 출력 하기
for trade in trade_list :
    print(trade)


# 출력 하기 #2 
for trade in trade_list :
    if trade['side'] == 'BUY':
        print('BUY Position : ',trade['price'])
    if trade['side'] == 'SELL':
        print('SELL Position : ',trade['price'])