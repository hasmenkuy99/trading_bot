# strategies/candlestick.py
# (Detect a basic bullish/bearish engulfing pattern as an example)
def get_candle_signal(klines):
    # klines: list of [open, high, low, close, ...] for last N periods
    if len(klines) < 2: 
        return 0
    o1, c1 = float(klines[-2][1]), float(klines[-2][4])  # prev candle open/close
    o2, c2 = float(klines[-1][1]), float(klines[-1][4])  # current
    # Bullish engulfing
    if c1 < o1 and c2 > o2 and c2 > c1 and o2 < o1:
        return 1
    # Bearish engulfing
    if c1 > o1 and c2 < o2 and c2 < c1 and o2 > o1:
        return -1
    return 0
