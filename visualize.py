import ohlc
import mplfinance as mpf

def make_plot(df):
    # line = 50

    df.set_index('Timestamp', inplace=True)
    
    ap1 = mpf.make_addplot(df['ATR_Trailing_Stop'], color='blue')
    # ap2 = mpf.make_addplot(df['RSI'], panel=2, color='green')
    # ap3 = mpf.make_addplot([line + 5] * len(df), panel=2, color='orange', secondary_y=False)
    # ap4 = mpf.make_addplot([line - 5] * len(df), panel=2, color='orange', secondary_y=False)

    mpf.plot(df, type='candle', style='charles', title='ATR RSI',
             ylabel='Price', addplot=[ap1],  
             figratio=(16, 9), figsize=(14, 7), xrotation=0,
             panel_ratios=(6, 3), volume = True)

if __name__ == "__main__" :
    ohlc_df = ohlc.get_ohlc()
    crossover_df =  ohlc_df[ohlc_df['Crossover'] != 0]
    print(crossover_df)
    print(ohlc_df.tail(2))
    make_plot(ohlc_df)