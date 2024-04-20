<h1>🤑🤖🔥 ATR + RSI Trading Bot 🔥🤖🤑</h1>

<br/><br/>

<h3>⚠️ 주식/코인 거래 일절 해본 적도 없는 사람(나)이 대충 유튜브 몇 개 2배속으로 보고 만든 프로그램임</h3>
<h4>수익(마이너스)내고 싶다면 실행해보는게 좋을지도? </h4>
투자의 판단과 책임은 투자자 본인에게 있습니다. <br/>
내 책임 없음 <br/>

<br/><br/><br/>

<h2>개발 과정 및 설명</h2>
https://aidevksh.notion.site/ATR-with-EMA-Trading-Bot-d548ef66a42d48908576542077b5b13b?pvs=4 <br/>

<br/><br/><br/>

<h3>GPT 🤖</h3>

<br/>
ATR은 Average True Range(평균 참 범위)의 약자로, 시장의 변동성을 측정하는 지표입니다. 주식, 외환, 선물 등 다양한 금융상품에서 사용됩니다. ATR은 특정 기간 동안의 최고가와 최저가 사이의 차이를 측정하여 평균을 계산합니다. 이것은 가격의 움직임이 얼마나 큰지를 나타냅니다. 변동성이 높을수록 ATR 값이 높아지며, 변동성이 낮을수록 ATR 값이 낮아집니다.<br/>
<br/>
ATR을 사용하여 트레일링 스탑을 설정할 수 있습니다. ATR 트레일링 스탑은 가격의 움직임에 따라 스톱 로스를 동적으로 조정하는 방법 중 하나입니다. ATR을 이용하면 시장의 변동성에 따라 스톱 로스를 조절하여 손실을 최소화할 수 있습니다.<br/>
<br/>
일반적으로 ATR 트레일링 스탑은 현재 가격에서 ATR의 여러 배수를 빼거나 더함으로써 계산됩니다. 예를 들어, 현재 가격에서 2배의 ATR을 빼면 롱 포지션(매수 포지션)의 트레일링 스탑이 됩니다. <br/>
즉, 가격이 현재 가격에서 2배의 ATR만큼 하락할 때까지 포지션을 유지합니다. 마찬가지로, 현재 가격에 2배의 ATR을 더하면 숏 포지션(매도 포지션)의 트레일링 스톱이 됩니다. 이러한 방식으로 ATR을 이용하면 시장의 변동성에 따라 스톱 로스를 동적으로 조절할 수 있습니다.<br/>

<br/>

RSI는 상대강도지수(Relative Strength Index)의 줄임말로, 주식 시장에서 가격의 상승과 하락 강도를 측정하는 데 사용되는 기술적 지표입니다. 주로 초과매수와 초과매도 상태를 파악하는 데에 이용됩니다. <br/>
<br/>
RSI는 일정 기간 동안의 상승분과 하락분의 평균값을 계산하여 상대적으로 강도를 나타냅니다. 이를 통해 가격의 상승 및 하락이 얼마나 강하게 일어났는지를 파악할 수 있습니다. <br/>
<br/>
RSI의 값은 일반적으로 0에서 100 사이의 범위에 있으며, 70 이상이면 과매수 상태로 간주되고, 30 이하면 과매도 상태로 간주됩니다. 이는 매수 또는 매도 신호를 확인하는 데 사용될 수 있습니다. <br/>

<br/><br/><br/>

<h2>🧑‍💻 데이터 시각화(무과금) 🧑‍💻</h2>
<br/>

1. git clone https://github.com/AIDevKSH/ATRTradingBot.git <br/><br/>
3. pip install pandas python-binance python-dotenv mplfinance ccxt <br/><br/>
4. 바이낸스 API 생성 <br/><br/>
5. .env 생성 BINANCE_API_KEY, BINANCE_API_SECRET 변수 만들고 값 입력 <br/><br/>
6. visualize.py 실행 <br/><br/>

<h2>🧑‍💻 EC2에서 사용법(과금) 🧑‍💻</h2>
<br/>

1. 인스턴스 만들기 <br/><br/>

2. 바이낸스 선물 계좌, 선물 거래 가능 API 생성<br/><br/>

3. 잔고 : 15 USDT 이상 필요 (거래 시 전체 시드의 30% 사용. 최소 거래 대금 5 USDT 이상 필요) <br/><br/>

4. sudo yum install git python3-pip cronie -y <br/><br/>

5. pip install pandas python-binance python-dotenv mplfinance ccxt <br/><br/>

6. git clone https://github.com/AIDevKSH/ATRTradingBot.git <br/><br/>

7. cd ATRTradingBot <br/><br/>

8. .env 생성 <br/>
   BINANCE_API_KEY, BINANCE_API_SECRET 변수 만들고 값 입력 <br/><br/>

9. testapi.py : 거래 작동 여부 확인용 <br/><br/>

10. sudo chmod 774 trading.py (744 해도 될듯)<br/></br>

11. sudo /usr/bin/python3 /home/ec2-user/ATRTradingBot/trading.py 작동하는지 확인 <br/><br/>

12. sudo mkdir /home/ec2-user/logs <br/>
    sudo chown ec2-user:ec2-user /home/ec2-user/logs <br/><br/>

13. crontab -e 편집기 열기 <br/>
    */15 * * * * /usr/bin/python3 /home/ec2-user/ATRTradingBot/trading.py >> /home/ec2-user/logs/trading.log 2>&1 <br/>
    작성 후 저장 <br/><br/>

14. sudo service crond restart <br/><br/>

15. crontab -l : 작성됐는지 확인 <br/><br/>

16. 실시간 로그 : tail -f /home/ec2-user/logs/trading.log <br/>
    전체 로그 : cat /home/ec2-user/logs/trading.log <br/>
    전체 로그 2: less /home/ec2-user/logs/trading.log <br/><br/>

17. crontab -r : 삭제 <br/><br/>



<br/><br/><br/>

<h2>🤦‍♀️ 할 일 🤦‍♂️</h2>
1. 프로그램 작동하면서 수익률 / 버그 여부 관찰 <br/><br/>
2. 거래 정보 내 쥐메일로 보내면 쥐메일 앱이 반응을 해서 애플와치에 알람 뜨게 하기 <br/><br/>
3. (팀플) 거래할 때 데이터 백엔드 서버에 보내기 <br/><br/>
4. (팀플) 서버에서 데이터베이스 관리하기 <br/><br/>
5. (팀플) 대시보드 + 주가 예측 모델(만들예정)로 웹사이트 만들어서 어그로 끌기 <br/><br/>