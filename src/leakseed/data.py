"""Synthetic market data for the oracle, and the perturbations it applies after a time t.

Every corpus script receives the same ``data`` dict:

- ``close``, ``volume``: business-day frames, one column per asset (index name ``date``,
  columns name ``asset``). The last asset is delisted at 70% of the sample (NaN afterwards);
  volume has gaps of 1 to 8 days.
- ``events``: irregular, intraday-stamped observations (``ts``, ``value``), never exactly at
  midnight, so an event on day d is not known at the close of day d - 1.
- ``fundamentals``: one row per (asset, quarter): ``period_end``, ``filed`` (the availability
  time, 20 to 60 business days later) and ``value``.
- ``fundamentals_pit``: the same plus restatements, each a later row for the same
  (asset, period_end) with its own ``filed``.
- ``membership``: a boolean index-membership frame shaped like ``close``.

All timestamps are ``datetime64[ns]``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

N_ASSETS = 6
PERTURB_MODES = ("values", "availability", "regime")


def make_data(n: int = 5000, seed: int = 0) -> dict:
    if n < 300:
        raise ValueError("the oracle needs at least 300 rows")
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2000-01-03", periods=n, name="date").as_unit("ns")
    assets = pd.Index([f"A{i}" for i in range(N_ASSETS)], name="asset", dtype=object)

    vol = rng.uniform(0.01, 0.02, N_ASSETS)
    steps = rng.standard_t(5, size=(n, N_ASSETS)) * vol * np.sqrt(3 / 5)
    close = pd.DataFrame(100 * np.exp(np.cumsum(steps, axis=0)), index=dates, columns=assets)
    delist = int(0.7 * n)
    close.iloc[delist:, -1] = np.nan

    volume = pd.DataFrame(
        np.exp(rng.normal(13.0, 0.4, size=(n, N_ASSETS))), index=dates, columns=assets
    )
    for j in range(N_ASSETS):
        starts = rng.choice(np.arange(5, n - 10), size=n // 60, replace=False)
        for s in starts:
            volume.iloc[s : s + rng.integers(1, 9), j] = np.nan
    volume.iloc[delist:, -1] = np.nan

    n_events = n // 3
    days = np.sort(rng.integers(0, n, n_events))
    offsets = pd.to_timedelta(rng.integers(3600, 23 * 3600, n_events), unit="s")
    events = pd.DataFrame(
        {"ts": (dates[days] + offsets).as_unit("ns"), "value": rng.normal(0.0, 1.0, n_events)}
    )
    events = events.sort_values("ts", ignore_index=True)

    quarters = pd.date_range(dates[0], dates[-1], freq="QE").as_unit("ns")
    rows = []
    for asset in assets:
        level = rng.normal(0.0, 1.0)
        for q in quarters:
            level = 0.8 * level + rng.normal(0.0, 0.6)
            filed = q + pd.offsets.BDay(int(rng.integers(20, 61)))
            rows.append((asset, q, filed, level))
    fundamentals = pd.DataFrame(rows, columns=["asset", "period_end", "filed", "value"])
    fundamentals["filed"] = fundamentals["filed"].astype("datetime64[ns]")
    # Object strings convert to polars without pyarrow (pandas 3 defaults to an arrow string).
    fundamentals["asset"] = fundamentals["asset"].astype(object)
    fundamentals = fundamentals.sort_values(["filed", "asset"], ignore_index=True)

    restated = fundamentals.sample(frac=0.4, random_state=int(rng.integers(2**31)))
    restated = restated.assign(
        filed=restated["filed"] + pd.to_timedelta(rng.integers(60, 250, len(restated)), "D"),
        value=restated["value"] + rng.normal(0.0, 0.8, len(restated)),
    )
    pit = pd.concat([fundamentals, restated], ignore_index=True)
    pit = pit.sort_values(["filed", "asset"], ignore_index=True)

    member = np.ones((n, N_ASSETS), dtype=bool)
    member[: int(0.3 * n), 2] = False
    member[int(0.6 * n) :, 3] = False
    member[: int(0.2 * n), 4] = False
    member[int(0.8 * n) :, 4] = False
    member[delist:, 5] = False
    membership = pd.DataFrame(member, index=dates, columns=assets)

    return {
        "close": close,
        "volume": volume,
        "events": events,
        "fundamentals": fundamentals,
        "fundamentals_pit": pit,
        "membership": membership,
    }


def copy_data(data: dict) -> dict:
    return {k: v.copy(deep=True) for k, v in data.items()}


def perturb(data: dict, t: int, mode: str, rng: np.random.Generator) -> dict:
    """Return a copy of ``data`` with everything after ``dates[t]`` replaced.

    Rows of the date-indexed frames after row ``t`` change; events change when ``ts`` is after
    ``dates[t]``; fundamentals rows change when ``filed`` (their availability time) is after it.
    ``values`` rescales and redraws values; ``availability`` changes what is missing: gaps are
    filled, a random asset disappears, events and filings are dropped; ``regime`` replaces the
    future prices by strong trend segments of a random typical length (values-mode changes
    elsewhere), so a choice that
    depends on future performance (a tuned parameter) is pushed to change. Membership is negated
    in every mode so a membership-dependent leak cannot hide behind an unchanged future.
    """
    if mode not in PERTURB_MODES:
        raise ValueError(f"unknown perturbation mode {mode!r}")
    out = copy_data(data)
    close, volume = out["close"], out["volume"]
    n, k = close.shape
    if not 0 <= t < n - 1:
        raise ValueError(f"t must be in [0, {n - 2}], got {t}")
    cut = close.index[t]
    tail = slice(t + 1, None)
    if mode in ("values", "regime"):
        for frame in (close, volume):
            frame.iloc[tail] = frame.iloc[tail].to_numpy() * rng.uniform(0.5, 1.5, (n - t - 1, k))
        late = out["events"]["ts"] > cut
        out["events"].loc[late, "value"] = rng.normal(0.0, 2.0, int(late.sum()))
        for key in ("fundamentals", "fundamentals_pit"):
            frame = out[key]
            late = frame["filed"] > cut
            frame.loc[late, "value"] = frame.loc[late, "value"] * rng.uniform(
                0.5, 1.5, int(late.sum())
            ) + rng.normal(0.0, 1.0, int(late.sum()))
        if mode == "regime":
            m = n - t - 1
            mean_len = rng.choice([4.0, 15.0, 60.0])  # favours a different lookback each time
            drift = np.empty((m, k))
            for j in range(k):
                pos = 0
                while pos < m:
                    seg = int(rng.geometric(1.0 / mean_len))
                    drift[pos : pos + seg, j] = rng.choice([-1.0, 1.0]) * rng.uniform(0.005, 0.02)
                    pos += seg
            steps = drift + rng.normal(0.0, 0.002, (m, k))
            trend = close.iloc[t].to_numpy() * np.exp(np.cumsum(steps, axis=0))
            gaps = np.isnan(data["close"].iloc[tail].to_numpy())
            close.iloc[tail] = np.where(gaps, np.nan, trend)
    else:
        for frame in (close, volume):
            block = frame.iloc[tail].to_numpy()
            gaps = np.isnan(block)
            fill = np.nanmedian(frame.iloc[: t + 1].to_numpy(), axis=0)
            fill = np.where(np.isnan(fill), 100.0, fill)
            block = np.where(gaps, fill * rng.uniform(0.5, 1.5, block.shape), block)
            block[:, rng.integers(k)] = np.nan
            frame.iloc[tail] = block
        events = out["events"]
        drop = (events["ts"] > cut) & (rng.random(len(events)) < 0.5)
        out["events"] = events.loc[~drop].reset_index(drop=True)
        for key in ("fundamentals", "fundamentals_pit"):
            frame = out[key]
            drop = (frame["filed"] > cut) & (rng.random(len(frame)) < 0.5)
            out[key] = frame.loc[~drop].reset_index(drop=True)
    member = out["membership"]
    member.iloc[tail] = ~member.iloc[tail].to_numpy()
    return out
