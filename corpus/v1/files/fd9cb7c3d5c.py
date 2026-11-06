import pandas as pd


def run(data):
    close = data["close"]
    events = data["events"]
    calendar = pd.DataFrame({"date": close.index})
    matched = pd.merge_asof(calendar, events, left_on="date", right_on="ts", direction="backward")
    tone = matched["value"].rolling(10, min_periods=1).mean()
    signal = pd.Series(tone.clip(-1.0, 1.0).to_numpy(), index=close.index)
    positions = signal.shift(1)
    return positions
