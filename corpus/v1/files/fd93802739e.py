import polars as pl


def _align_feature(frame, assets, horizon):
    feature = frame.select(pl.col(assets).pct_change().shift(horizon))
    return feature


def run(data):
    frame = pl.from_pandas(data["close"].reset_index())
    assets = [c for c in frame.columns if c != "date"]
    feature = _align_feature(frame, assets, -1)
    signal = feature.select(pl.all().rolling_mean(10).sign())
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
