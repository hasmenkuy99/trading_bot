# strategies/trend.py
import pandas as pd

def get_trend_signal(closes):
    series = pd.Series(closes)
    short_ma = series.ewm(span=20, adjust=False).mean()
    long_ma = series.ewm(span=50, adjust=False).mean()
    if short_ma.iloc[-2] <= long_ma.iloc[-2] and short_ma.iloc[-1] > long_ma.iloc[-1]:
        return 1
    if short_ma.iloc[-2] >= long_ma.iloc[-2] and short_ma.iloc[-1] < long_ma.iloc[-1]:
        return -1
    return 0
