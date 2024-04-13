import ohlc

ohlc.position_decision()

# 1. 최근 두 데이터 정보 보기
print_df = ohlc.ohlc_df.tail(2)
print("\n", print_df[['Timestamp', 'Open' ,'Close', 'EMA_14', 'ATR_Trailing_Stop', 'Crossover']], "\n")

# 2. 이틀 데이터 중 크로스 오버 한 데이터만 보기
crossover_df =  ohlc.ohlc_df[ohlc.ohlc_df['Crossover'] != 0]
print(crossover_df)

# 3. chart.png와 같은 그래프 출력하기
ohlc.make_plot(ohlc.ohlc_df)