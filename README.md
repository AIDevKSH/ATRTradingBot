<h1>🤑🤖🔥 ATR + EMA Trading Bot 🤑🤖🔥</h1>

<br/><br/>

<h2>개발 과정 및 설명</h2>
https://aidevksh.notion.site/ATR-with-EMA-Trading-Bot-d548ef66a42d48908576542077b5b13b?pvs=4 <br/>

<br/><br/><br/>

<h2>🧑‍💻 사용법</h2>
1. git clone https://github.com/AIDevKSH/ATRTradingBot.git 🙂 cd ATRwithRSI <br/>
2. 바이낸스 선물계좌, 선물 거래 가능한 api <br/>
3. 돈 : 최소 거래 5 usdt 이상 필요. 항상 시드의 30%만 가지고 거래하므로 15 usdt 이상 보유해야됨.<br/>
4. 컴퓨터 (난 EC2 공짜 사용 중) <br/>
5. pip install pandas python-binance python-dotenv ccxt schedule mplfinance <br/>
6. .env 파일 생성, BINANCE_API_KEY, BINANCE_API_SECRET 변수 만들고 값 입력 <br/>
7. visualize.py : 데이터 시각화 (거래x) | 선물 거래 안 되는 바이낸스 api도 가능 <br/>
8. testapi.py : 거래 잘 되는지 확인하는 파일 <br/>
9. nohup python3 trading.py (15분 마다 반복 실행, 터미널 꺼도됨) |  <br/>
10. 종료 : 컴끄기 아니면 "ps -ef | grep python3 trading.py" 해당 프로세스의 pid 찾고 "kill <pid number>" <br/>

<br/><br/><br/>

<h3>ChatGPT 🤖</h3>

<br/>
ATR은 Average True Range(평균 참 범위)의 약자로, 시장의 변동성을 측정하는 지표입니다. 주식, 외환, 선물 등 다양한 금융상품에서 사용됩니다. ATR은 특정 기간 동안의 최고가와 최저가 사이의 차이를 측정하여 평균을 계산합니다. 이것은 가격의 움직임이 얼마나 큰지를 나타냅니다. 변동성이 높을수록 ATR 값이 높아지며, 변동성이 낮을수록 ATR 값이 낮아집니다.<br/>
<br/>
ATR을 사용하여 트레일링 스탑을 설정할 수 있습니다. ATR 트레일링 스탑은 가격의 움직임에 따라 스톱 로스를 동적으로 조정하는 방법 중 하나입니다. ATR을 이용하면 시장의 변동성에 따라 스톱 로스를 조절하여 손실을 최소화할 수 있습니다.<br/>
<br/>
일반적으로 ATR 트레일링 스탑은 현재 가격에서 ATR의 여러 배수를 빼거나 더함으로써 계산됩니다. 예를 들어, 현재 가격에서 2배의 ATR을 빼면 롱 포지션(매수 포지션)의 트레일링 스탑이 됩니다. 즉, 가격이 현재 가격에서 2배의 ATR만큼 하락할 때까지 포지션을 유지합니다. 마찬가지로, 현재 가격에 2배의 ATR을 더하면 숏 포지션(매도 포지션)의 트레일링 스톱이 됩니다. 이러한 방식으로 ATR을 이용하면 시장의 변동성에 따라 스톱 로스를 동적으로 조절할 수 있습니다.<br/>

<br/><br/><br/>

EMA(Exponential Moving Average) 14는 주식 시장에서 사용되는 기술적 지표 중 하나입니다. 이것은 최근 가격 데이터에 높은 가중치를 두어 이동 평균을 계산합니다. 여기서 "지수적"이란 말은 최신 데이터에 더 많은 중요성을 부여한다는 것을 의미합니다.<br/>
<br/>
EMA 14의 "14"는 기간을 나타냅니다. 이 경우, 최근 14일 동안의 가격 데이터를 기반으로 지수 이동 평균을 계산합니다. EMA는 이전 기간의 평균과 현재 가격의 가중 평균으로 계산됩니다. 즉, EMA는 가격 움직임의 상대적인 부드러움을 제공하며, 단기 및 중기 트렌드를 파악하는 데 유용합니다. 주식 시장에서 트레이더들은 주식의 추세를 분석하고 예측하기 위해 EMA를 자주 사용합니다.<br/>

<br/><br/><br/>

<h2>🤦‍♀️ 할 일 🤦‍♂️</h2>
1. 프로그램 작동하면서 수익률 / 버그 여부 관찰 <br/>
2. 거래 정보 내 쥐메일로 보내면 쥐메일 앱이 반응을 해서 애플와치에 알람 뜨게 하기 <br/>
3. (팀플) 거래할 때 데이터 백엔드 서버에 보내기 <br/>
4. (팀플) 서버에서 데이터베이스 관리하기 <br/>
5. (팀플) 대시보드 + 주가 예측 모델(만들예정)로 웹사이트 만들어서 어그로 끌기 <br/>

<br/><br/><br/>

<h3>⚠️ 주식/코인 거래 일절 해본 적도 없는 사람(나)이 대충 유튜브 몇 개 2배속으로 보고 만든 프로그램임</h3>
<h4>수익(마이너스)내고 싶다면 실행해보는게 좋을지도?</h4>
투자의 판단과 책임은 투자자 본인에게 있습니다.<br/>
내 책임 없음