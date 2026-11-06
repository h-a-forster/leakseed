import json

CONFIG = json.loads('{"screen": "as_of"}')


def _filter_names(raw, membership, screen):
    if screen == "final":
        signal = raw.loc[:, membership.iloc[-1]].reindex(columns=raw.columns)
        return signal
    signal = raw.where(membership)
    return signal


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    raw = returns.rolling(60).mean().rank(axis=1, pct=True) - 0.5
    membership = data["membership"]
    signal = _filter_names(raw, membership, CONFIG["screen"])
    positions = signal.shift(1)
    return positions
