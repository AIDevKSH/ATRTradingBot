import ohlc

ohlc.position_decision()

ohlc.ohlc_df['Decision'] = 0

# 거래 안 되는 api도 가능

# Decision 값 설정 | 1 : Enter Long | -1 : Enter Short
ohlc.ohlc_df.loc[(ohlc.ohlc_df['Crossover'] == 1) & (ohlc.ohlc_df['Open'] >= ohlc.ohlc_df['EMA_14']), 'Decision'] = 1
ohlc.ohlc_df.loc[(ohlc.ohlc_df['Crossover'] == 1) & (ohlc.ohlc_df['Open'] < ohlc.ohlc_df['EMA_14']), 'Decision'] = 0
ohlc.ohlc_df.loc[(ohlc.ohlc_df['Crossover'] == -1) & (ohlc.ohlc_df['Open'] <= ohlc.ohlc_df['EMA_14']), 'Decision'] = -1
ohlc.ohlc_df.loc[(ohlc.ohlc_df['Crossover'] == -1) & (ohlc.ohlc_df['Open'] > ohlc.ohlc_df['EMA_14']), 'Decision'] = 0
ohlc.ohlc_df.loc[(ohlc.ohlc_df['Crossover'] == 0), 'Decision'] = 0

# 이틀 데이터 중 크로스오버 한 데이터만 보기
crossover_df =  ohlc.ohlc_df[ohlc.ohlc_df['Crossover'] != 0]
print(crossover_df[['Timestamp', 'Open' ,'Close', 'EMA_14', 'ATR_Trailing_Stop', 'Crossover', 'Decision']])
# 포지션 진입 : Crossover == Decision 일 때

ohlc.make_plot(ohlc.ohlc_df)