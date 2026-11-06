def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    raw = returns.rolling(120).mean().rank(axis=1, pct=True) - 0.5
    membership = data["membership"]
    signal = raw.where(membership)
    positions = signal.shift(1)
    return positions
