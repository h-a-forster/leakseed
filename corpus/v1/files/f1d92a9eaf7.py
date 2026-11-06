def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    raw = returns.rolling(60).mean().rank(axis=1, pct=True) - 0.5
    scores = raw
    signal = scores.where(close.notna())
    positions = signal.shift(1)
    return positions
