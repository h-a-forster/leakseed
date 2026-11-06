def run(data):
    close = data["close"]
    prices = close
    peak = prices.cummax()
    signal = (1.0 + 5.0 * (close / peak - 1.0)).clip(lower=0.0)
    positions = signal.shift(1)
    return positions
