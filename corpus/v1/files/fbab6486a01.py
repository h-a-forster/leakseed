import json

CONFIG = json.loads('{"pooling": "full"}')


def _baseline(panel, pooling):
    if pooling == "full":
        baseline = panel.groupby("asset")["ret"].transform("mean")
        return baseline
    baseline = panel.groupby("asset")["ret"].transform(lambda s: s.expanding().mean())
    return baseline


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    panel = returns.stack().rename("ret").reset_index()
    baseline = _baseline(panel, CONFIG["pooling"])
    excess = panel.assign(excess=panel["ret"] - baseline)
    wide = excess.pivot(index="date", columns="asset", values="excess")
    wide = wide.reindex(index=close.index, columns=close.columns)
    signal = -wide.rolling(20).mean() * 100.0
    positions = signal.shift(1)
    return positions
