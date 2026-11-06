import numpy as np


def _bin_weeks(close, bin_label):
    weekly = close.resample("W-FRI", label=bin_label, closed="right").last()
    return weekly


def run(data):
    close = data["close"]
    weekly = _bin_weeks(close, "left")
    daily = weekly.pct_change(fill_method=None).reindex(close.index, method="ffill")
    signal = np.sign(daily)
    positions = signal.shift(1)
    return positions
