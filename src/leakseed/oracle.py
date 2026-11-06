"""Causality oracle: verify each corpus label by perturbing the future and watching the past.

Every corpus script exposes ``run(data)`` returning the positions held over each bar. A
position held over bar ``j`` may use data up to row ``j - 1``. So when every input after time
``t`` is replaced (:func:`leakseed.data.perturb`), output rows ``0 .. t + 1`` must not move.

- A *leak* verdict comes with a witness (t, mode, row): a concrete pair of input histories that
  agree up to ``t`` and produce different held positions at or before ``t + 1``. It is a proof.
- A *clean* verdict means no tried perturbation moved the past. It is evidence, not proof:
  only finitely many t and draws are tried (docs/DESIGN.md, section 3).

The oracle executes only corpus files whose hash matches the manifest (:func:`verify`).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
import uuid
import warnings
import zlib
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .data import PERTURB_MODES, copy_data, make_data, perturb
from .generate import read_manifest, read_source

DATA_SEED = 2026
LAG = 1  # held positions: row j may use data up to row j - 1
RTOL, ATOL = 1e-9, 1e-12


class OracleError(Exception):
    """The oracle could not reach a verdict (bad output, nondeterminism, vacuous check)."""


@dataclass
class Verdict:
    id: str
    label: str
    verdict: str  # "leak", "clean" or "error"
    runs: int
    witness: dict | None = None
    error: str | None = None
    seconds: float = 0.0

    @property
    def agrees(self) -> bool:
        return self.verdict == self.label


def as_matrix(out, dates: pd.DatetimeIndex) -> np.ndarray:
    """Normalise a script's output to a float array with one row per date."""
    if isinstance(out, (pd.DataFrame, pd.Series)):
        if isinstance(out.index, pd.DatetimeIndex) and not out.index.equals(dates):
            raise OracleError("output index is not the input calendar")
        arr = out.to_numpy(dtype=float)
    elif type(out).__module__.split(".")[0] == "polars":
        arr = out.to_numpy().astype(float)
    else:
        arr = np.asarray(out, dtype=float)
    if arr.ndim == 1:
        arr = arr[:, None]
    if arr.ndim != 2 or arr.shape[0] != len(dates):
        raise OracleError(f"output shape {arr.shape} does not have one row per date ({len(dates)})")
    return arr


def same(a: np.ndarray, b: np.ndarray) -> bool:
    return a.shape == b.shape and bool(np.allclose(a, b, rtol=RTOL, atol=ATOL, equal_nan=True))


def t_grid(n: int, k: int, rng: np.random.Generator, first: int = 0) -> list[int]:
    """``k`` cut points stratified over [5% of n, n - 2), one uniform draw per stratum.

    ``first`` is the first row with a finite output: a cut before ``first - 1`` compares only
    missing values, so the grid starts there instead.
    """
    lo, hi = max(1, n // 20, first - 1), n - 2
    edges = np.linspace(lo, hi, k + 1)
    return sorted({int(rng.uniform(edges[i], edges[i + 1])) for i in range(k)})


def check(
    run: Callable,
    data: dict,
    *,
    n_t: int = 16,
    seed: int = 0,
    modes: tuple[str, ...] = PERTURB_MODES,
    ts: list[int] | None = None,
) -> tuple[str, dict | None, int]:
    """Return ``(verdict, witness, runs)`` for ``run`` on ``data``.

    ``ts`` overrides the stratified random grid. Raises :class:`OracleError` when the output is
    malformed, nondeterministic, never finite, or does not respond to any perturbation (a check
    that cannot fail is not evidence).
    """
    dates = data["close"].index
    rng = np.random.default_rng(seed)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        base = as_matrix(run(copy_data(data)), dates)
        if not same(base, as_matrix(run(copy_data(data)), dates)):
            raise OracleError("output differs between two runs on the same data")
        if not np.isfinite(base).any():
            raise OracleError("output has no finite values")
        runs, responsive = 2, False
        first = int(np.argmax(np.isfinite(base).any(axis=1)))
        # Each mode gets its own stratified grid, so two modes probe 2 * n_t distinct cuts.
        plan = [
            (t, mode)
            for mode in modes
            for t in (ts if ts is not None else t_grid(len(dates), n_t, rng, first))
        ]
        for t, mode in plan:
            out = run(perturb(data, t, mode, rng))
            runs += 1
            arr = as_matrix(out, dates)
            if arr.shape != base.shape:
                return "leak", {"t": t, "mode": mode, "row": None, "reason": "shape"}, runs
            head = slice(0, t + 1 + LAG)
            if not same(arr[head], base[head]):
                diff = ~np.isclose(arr[head], base[head], rtol=RTOL, atol=ATOL, equal_nan=True)
                row = int(np.argwhere(diff)[0][0])
                return "leak", {"t": t, "mode": mode, "row": row, "reason": "value"}, runs
            responsive = responsive or not same(arr, base)
    if not responsive:
        raise OracleError("output never responded to a perturbation; the check is vacuous")
    return "clean", None, runs


def load_run(path: Path) -> Callable:
    """Import a corpus script under a private module name and return its ``run``."""
    name = f"_leakseed_case_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise OracleError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
    run = getattr(module, "run", None)
    if not callable(run):
        raise OracleError(f"{path} has no run(data)")
    return run


_DATA: dict[tuple[int, int], dict] = {}


def _worker_data(n: int, data_seed: int) -> dict:
    if (n, data_seed) not in _DATA:
        _DATA.clear()
        _DATA[(n, data_seed)] = make_data(n, data_seed)
    return _DATA[(n, data_seed)]


def verify_row(corpus: str, row: dict, n: int, n_t: int, data_seed: int = DATA_SEED) -> Verdict:
    start = time.perf_counter()
    try:
        read_source(Path(corpus), row)  # refuse anything that is not the generated file
        run = load_run(Path(corpus) / row["path"])
        verdict, witness, runs = check(
            run, _worker_data(n, data_seed), n_t=n_t, seed=zlib.crc32(row["id"].encode())
        )
        out = Verdict(row["id"], row["label"], verdict, runs, witness)
    except Exception as exc:  # any failure is reported per file, never swallowed
        out = Verdict(row["id"], row["label"], "error", 0, error=f"{type(exc).__name__}: {exc}")
    out.seconds = round(time.perf_counter() - start, 3)
    return out


def verify(
    corpus: Path,
    *,
    n: int = 5000,
    n_t: int = 16,
    workers: int = 1,
    data_seed: int = DATA_SEED,
    ids: list[str] | None = None,
    progress: Callable[[Verdict], None] | None = None,
) -> list[Verdict]:
    """Run the oracle on every manifest file (or ``ids``) and return verdicts in manifest order."""
    rows = read_manifest(corpus)
    if ids is not None:
        wanted = set(ids)
        rows = [r for r in rows if r["id"] in wanted]
        if len(rows) != len(wanted):
            raise OracleError("some requested ids are not in the manifest")
    if workers <= 1:
        results = []
        for r in rows:
            results.append(verify_row(str(corpus), r, n, n_t, data_seed))
            if progress:
                progress(results[-1])
        return results
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(verify_row, str(corpus), r, n, n_t, data_seed) for r in rows]
        results = []
        for f in futures:
            results.append(f.result())
            if progress:
                progress(results[-1])
        return results


def write_verdicts(path: Path, verdicts: list[Verdict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for v in verdicts:
        d = asdict(v)
        d.pop("seconds")  # keep the committed file reproducible byte for byte
        lines.append(json.dumps(d, sort_keys=True))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
