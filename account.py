from binance.client import Client
import time
from dotenv import load_dotenv
import os
load_dotenv()

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
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

# 계좌 정보 불러오기
account_info = client.futures_account_balance(timestamp=current_time)

# # USDT 자산 확인하기
USDT_balance = None
for balance in account_info :
    if balance['asset'] == 'USDT':
        USDT_balance = balance['balance']
        print('USDT balance:', USDT_balance)
        break