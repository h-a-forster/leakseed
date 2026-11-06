import polars as pl


def run(data):
    frame = pl.from_pandas(data["close"].reset_index())
    assets = [c for c in frame.columns if c != "date"]
    order = False
    peak = frame.select(pl.col(assets).cum_max(reverse=order))
    signal = pl.DataFrame([(1.0 + 5.0 * (frame[c] / peak[c] - 1.0)).clip(0.0) for c in assets])
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
