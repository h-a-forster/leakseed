def _eligible(raw, close):
    signal = raw.loc[:, close.iloc[-1].notna()].reindex(columns=raw.columns)
    return signal


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    raw = returns.rolling(20).mean().rank(axis=1, pct=True) - 0.5
    signal = _eligible(raw, close)
    positions = signal.shift(1)
    return positions
