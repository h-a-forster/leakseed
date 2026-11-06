def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    momentum = returns.rolling(10).mean()
    values = momentum
    score = (values - values.mean()) / values.std()
    signal = score.clip(-2.0, 2.0)
    positions = signal.shift(1)
    return positions
