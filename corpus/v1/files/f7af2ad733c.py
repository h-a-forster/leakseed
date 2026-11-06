def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    raw = returns.rolling(60).mean().rank(axis=1, pct=True) - 0.5
    scores = raw
    signal = scores.loc[:, close.iloc[-1].notna()].reindex(columns=scores.columns)
    positions = signal.shift(1)
    return positions
