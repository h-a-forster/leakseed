import json

CONFIG = json.loads('{"history": "expanding"}')


def _baseline(panel, history):
    if history == "full":
        baseline = panel.groupby(panel["date"].dt.month)["ret"].transform("mean")
        return baseline
    baseline = panel.groupby(panel["date"].dt.month)["ret"].transform(lambda s: s.expanding().mean())
    return baseline


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    panel = returns.stack().rename("ret").reset_index()
    baseline = _baseline(panel, CONFIG["history"])
    excess = panel.assign(excess=panel["ret"] - baseline)
    wide = excess.pivot(index="date", columns="asset", values="excess")
    wide = wide.reindex(index=close.index, columns=close.columns)
    signal = -wide.rolling(40).mean() * 100.0
    positions = signal.shift(1)
    return positions
