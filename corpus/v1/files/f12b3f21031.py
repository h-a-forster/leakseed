import polars as pl


def _running_peak(frame, assets, order):
    peak = frame.select(pl.col(assets).cum_max(reverse=order))
    return peak


def run(data):
    frame = pl.from_pandas(data["close"].reset_index())
    assets = [c for c in frame.columns if c != "date"]
    peak = _running_peak(frame, assets, False)
    signal = pl.DataFrame([(1.0 + 5.0 * (frame[c] / peak[c] - 1.0)).clip(0.0) for c in assets])
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
