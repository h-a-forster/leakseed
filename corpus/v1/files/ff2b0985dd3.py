def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    raw = returns.rolling(20).mean().rank(axis=1, pct=True) - 0.5
    membership = data["membership"]
    ranked = raw
    signal = ranked.loc[:, membership.iloc[-1]].reindex(columns=ranked.columns)
    positions = signal.shift(1)
    return positions
