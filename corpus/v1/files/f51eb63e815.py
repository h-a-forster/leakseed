import numpy as np


def run(data):
    close = data["close"]
    label = "left"
    weekly = close.resample("W-FRI", label=label, closed="right").last()
    daily = weekly.pct_change(fill_method=None).reindex(close.index, method="ffill")
    signal = np.sign(daily)
    positions = signal.shift(1)
    return positions
