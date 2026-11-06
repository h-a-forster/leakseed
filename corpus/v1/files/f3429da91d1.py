def _running_peak(close):
    peak = close[::-1].cummax()[::-1]
    return peak


def run(data):
    close = data["close"]
    peak = _running_peak(close)
    signal = (1.0 + 5.0 * (close / peak - 1.0)).clip(lower=0.0)
    positions = signal.shift(1)
    return positions
