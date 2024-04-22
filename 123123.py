import ohlc
import mplfinance as mpf

def rsi(df, window=10) :
    df['MA'] = df['Close'].rolling(window=window).mean()

    df['Up'] = df['Close'].diff().apply(lambda x: x if x > 0 else 0)
    df['Down'] = df['Close'].diff().apply(lambda x: abs(x) if x < 0 else 0)

    up_avg = df['Up'].rolling(window=window).mean()
    down_avg = df['Down'].rolling(window=window).mean()

    rs = up_avg / down_avg
    df['rsi'] = 100 - (100 / (1 + rs))

    return df

def make_plot(ohlc_df):
    line = 50

    ohlc_df.set_index('Timestamp', inplace=True)
    
    ap1 = mpf.make_addplot(ohlc_df['ATR_Trailing_Stop'], color='blue')  # ATR_Trailing_Stop 추가
    ap2 = mpf.make_addplot(ohlc_df['RSI'], panel=1, color='green')  # 새로운 선 그래프 추가 (rsi), panel=1은 두 번째 하단 패널을 의미
    ap3 = mpf.make_addplot([line + 5] * len(ohlc_df), panel=1, color='orange', secondary_y=False)
    ap4 = mpf.make_addplot([line - 5] * len(ohlc_df), panel=1, color='orange', secondary_y=False)

    mpf.plot(ohlc_df, type='candle', style='charles', title='zzz',
             ylabel='Price', addplot=[ap1, ap2, ap3, ap4],  # ATR_Trailing_Stop 및 RSI 추가
             figratio=(16, 9), figsize=(14, 7), xrotation=0,  # 캔들 차트 설정
             panel_ratios=(6, 3))  # 패널 비율 설정



if __name__ == "__main__" :
    ohlc.position_decision()
    # This function returns ohlc.ohlc_df, ohlc.current_df
    rsi(ohlc.ohlc_df)
    make_plot(ohlc.ohlc_df)