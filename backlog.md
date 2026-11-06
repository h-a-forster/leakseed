# Backlog

## In progress

## Waiting on me

- Decide whether leakseed goes public; on public release, tag v0.1.0 and freeze v1 for real.
- Add REPORT.md to the repository from the text in the 2026-11-06 workflow result (the workflow's subagent could not write report files).

## Decided

- 2026-11-06: Static linters only in the scorecard; runtime detectors would need a separate harness.
- 2026-11-06: Paired at the site is the primary measure, and the template sign-flip test replaces McNemar for tool comparisons.

## Proposed

- Score runtime detectors (peekproof `check`, monte-neo probes, nofuturedata invariance) on the same corpus, adapting `run(data)` to each tool's input.
- Corpus v2 with a pnl expression in the same_bar templates, loop-index leaks and target-as-feature leaks, under a new seed.
- Add leaks a differential oracle cannot witness (narrow-window, threshold-gated), with labels proved by construction.
- Check external validity by scoring the linters on real public backtest repositories with hand-verified leaks.
