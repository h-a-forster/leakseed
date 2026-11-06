import polars as pl


def _to_positions(signal, lag):
    positions = signal.select(pl.all().shift(lag))
    return positions


def run(data):
    frame = pl.from_pandas(data["close"].reset_index())
    assets = [c for c in frame.columns if c != "date"]
    signal = frame.select(pl.col(assets).pct_change().rolling_mean(10).sign())
    positions = _to_positions(signal, 0)
    return positions.to_numpy()
