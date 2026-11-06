# Rule probes

Hand-written pairs in the surface forms the rules look for (corpus/probes). The oracle confirms each label. Regenerate with `uv run python scripts/probes.py`.

| File | Rules that fired |
|---|---|
| `argmax_gridsearch_clean.py` | backtest-audit: LEAK001; monte-neo: full_sample_stat |
| `argmax_gridsearch_leak.py` | peekproof: PP004, PP005; backtest-audit: LEAK001; leakguard: LG004; monte-neo: full_sample_fit, full_sample_stat; nofuturedata: SRC011 |
| `np_roll_negative_clean.py` | none |
| `np_roll_negative_leak.py` | peekproof: PP001; monte-neo: negative_roll; nofuturedata: SRC012 |
| `same_bar_pnl_clean.py` | monte-neo: full_sample_stat |
| `same_bar_pnl_leak.py` | peekproof: PP010; monte-neo: full_sample_stat |
