import json

CONFIG = json.loads('{"which": "last"}')


def _collapse(pit, which):
    chosen = pit.groupby(["asset", "period_end"])["value"].transform(which)
    latest = pit.assign(value=chosen).drop_duplicates(["asset", "period_end"])
    return latest


def run(data):
    close = data["close"]
    pit = data["fundamentals_pit"].sort_values("filed")
    latest = _collapse(pit, CONFIG["which"])
    table = latest.pivot_table(index="filed", columns="asset", values="value")
    table = table.reindex(columns=close.columns)
    known = table.reindex(table.index.union(close.index)).ffill().reindex(close.index)
    signal = known.rank(axis=1, pct=True) - 0.5
    positions = signal.shift(1)
    return positions
