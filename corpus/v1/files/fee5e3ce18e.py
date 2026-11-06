import polars as pl


def _align_events(calendar, events, direction):
    matched = calendar.join_asof(events, left_on="date", right_on="ts", strategy=direction)
    return matched


def run(data):
    calendar = pl.from_pandas(data["close"].reset_index()).select("date")
    events = pl.from_pandas(data["events"])
    matched = _align_events(calendar, events, "forward")
    signal = matched.select(pl.col("value").rolling_mean(10, min_samples=1).clip(-1.0, 1.0))
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
