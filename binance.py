from binance.client import Client

from dotenv import load_dotenv
import os
load_dotenv()

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANACE_API_SECRET")

# 클라이언트 생성
client = Client(api_key, api_secret)

# 잔고 조회
balances = client.get_account()

# 잔고 출력
for balance in balances['balances']:
    if float(balance['free']) > 0:
        print(f"{balance['asset']}: {balance['free']}")
