def _score(momentum):
    score = (momentum - momentum.mean()) / momentum.std()
    return score


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    momentum = returns.rolling(40).mean()
    score = _score(momentum)
    signal = score.clip(-2.0, 2.0)
    positions = signal.shift(1)
    return positions
