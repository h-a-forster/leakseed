import json

CONFIG = json.loads('{"universe_rule": "final"}')


def _eligible(raw, close, universe_rule):
    if universe_rule == "final":
        signal = raw.loc[:, close.iloc[-1].notna()].reindex(columns=raw.columns)
        return signal
    signal = raw.where(close.notna())
    return signal


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    raw = returns.rolling(60).mean().rank(axis=1, pct=True) - 0.5
    signal = _eligible(raw, close, CONFIG["universe_rule"])
    positions = signal.shift(1)
    return positions
