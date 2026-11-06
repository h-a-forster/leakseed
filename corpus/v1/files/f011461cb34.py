def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    panel = returns.stack().rename("ret").reset_index()
    tbl = panel
    baseline = tbl.groupby(tbl["date"].dt.month)["ret"].transform(lambda s: s.expanding().mean())
    excess = panel.assign(excess=panel["ret"] - baseline)
    wide = excess.pivot(index="date", columns="asset", values="excess")
    wide = wide.reindex(index=close.index, columns=close.columns)
    signal = -wide.rolling(20).mean() * 100.0
    positions = signal.shift(1)
    return positions
