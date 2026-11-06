"""Intervals and tests used by the scorecard."""

from __future__ import annotations

import numpy as np
from scipy import stats


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Exact two-sided binomial interval; ``(nan, nan)`` when ``n == 0``."""
    if n == 0:
        return (float("nan"), float("nan"))
    if not 0 <= k <= n:
        raise ValueError(f"need 0 <= k <= n, got k={k}, n={n}")
    lo = 0.0 if k == 0 else float(stats.beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(stats.beta.ppf(1 - alpha / 2, k + 1, n - k))
    return (lo, hi)


def cluster_bootstrap(
    outcomes: np.ndarray,
    clusters: np.ndarray,
    *,
    n_boot: int = 10_000,
    seed: int = 0,
    alpha: float = 0.05,
) -> tuple[float, float, float]:
    """Pooled proportion with a percentile interval from resampling whole clusters.

    ``outcomes`` are 0/1 per unit and ``clusters`` their cluster labels. Each replicate draws
    as many clusters as there are, with replacement, and pools their units, so units of one
    cluster always move together. Returns ``(estimate, lo, hi)``; all ``nan`` without units.
    """
    outcomes = np.asarray(outcomes, dtype=float)
    clusters = np.asarray(clusters)
    if outcomes.shape != clusters.shape:
        raise ValueError("outcomes and clusters must have the same length")
    if outcomes.size == 0:
        return (float("nan"),) * 3
    labels, inverse = np.unique(clusters, return_inverse=True)
    successes = np.bincount(inverse, weights=outcomes)
    sizes = np.bincount(inverse).astype(float)
    estimate = successes.sum() / sizes.sum()
    rng = np.random.default_rng(seed)
    c = len(labels)
    weights = rng.multinomial(c, np.full(c, 1.0 / c), size=n_boot).astype(float)
    reps = (weights @ successes) / (weights @ sizes)
    lo, hi = np.quantile(reps, [alpha / 2, 1 - alpha / 2])
    return (float(estimate), float(lo), float(hi))


def mcnemar_exact(a: np.ndarray, b: np.ndarray) -> dict:
    """Exact McNemar test for paired 0/1 outcomes of two tools on the same units."""
    a = np.asarray(a, dtype=bool)
    b = np.asarray(b, dtype=bool)
    if a.shape != b.shape:
        raise ValueError("paired outcomes must have the same length")
    only_a = int((a & ~b).sum())
    only_b = int((~a & b).sum())
    m = only_a + only_b
    p = 1.0 if m == 0 else min(1.0, 2.0 * float(stats.binom.cdf(min(only_a, only_b), m, 0.5)))
    return {"only_a": only_a, "only_b": only_b, "n": int(a.size), "p": p}


def holm(pvalues: list[float]) -> list[float]:
    """Holm step-down adjusted p-values, in the input order."""
    p = np.asarray(pvalues, dtype=float)
    order = np.argsort(p)
    m = len(p)
    adjusted = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, min(1.0, (m - rank) * p[idx]))
        adjusted[idx] = running
    return adjusted.tolist()
