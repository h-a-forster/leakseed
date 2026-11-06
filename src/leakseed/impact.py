"""Economic size of each leak: the Sharpe ratio a script earns on driftless synthetic data.

Prices in :func:`leakseed.data.make_data` have no drift and no autocorrelation, so a causal
strategy has an expected Sharpe of zero and whatever a leaky file earns above its clean twin
comes from the leak. Events and fundamentals are independent of prices there, so leaks through
those channels show no gain by construction; the oracle, not this table, establishes that they
are leaks.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .data import copy_data, make_data
from .generate import read_manifest, read_source
from .oracle import as_matrix, load_run

DATA_SEEDS = (2026, 7, 11, 13, 17)
BARS_PER_YEAR = 252


def sharpe(positions: np.ndarray, close: np.ndarray) -> float:
    """Annualised Sharpe of holding ``positions`` over each bar, equally across assets.

    One column of positions is held in every asset. Missing positions or prices are flat.
    """
    returns = np.full_like(close, np.nan)
    returns[1:] = close[1:] / close[:-1] - 1.0
    held = np.nan_to_num(positions, posinf=0.0, neginf=0.0)
    pnl = (held * np.nan_to_num(returns)).mean(axis=1)[1:]
    sd = pnl.std()
    return float(pnl.mean() / sd * np.sqrt(BARS_PER_YEAR)) if sd > 0 else 0.0


def measure(corpus: Path, *, n: int = 5000, data_seeds: tuple[int, ...] = DATA_SEEDS) -> list[dict]:
    """Mean Sharpe per corpus file over ``data_seeds``, in manifest order."""
    rows = read_manifest(corpus)
    totals = dict.fromkeys((r["id"] for r in rows), 0.0)
    for seed in data_seeds:
        data = make_data(n, seed)
        close = data["close"].to_numpy()
        for r in rows:
            read_source(Path(corpus), r)  # refuse anything that is not the generated file
            run = load_run(Path(corpus) / r["path"])
            held = as_matrix(run(copy_data(data)), data["close"].index)
            totals[r["id"]] += sharpe(held, close) / len(data_seeds)
    return [{"id": r["id"], "sharpe": round(totals[r["id"]], 3)} for r in rows]


def write_impact(path: Path, rows: list[dict]) -> None:
    lines = [json.dumps(r, sort_keys=True) for r in rows]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
