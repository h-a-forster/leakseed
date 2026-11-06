# Design

## 1. Goal and estimands

leakseed measures how well static leakage linters find look-ahead leaks in backtest code.
It needs labels that do not depend on a tool author's beliefs. So each corpus file's label
is verified by executing it under a causality oracle (section 3). For each tool:

| Estimand | Definition | Unit |
|---|---|---|
| recall | P(flag \| leaky file) | leaky file |
| false-positive rate | P(flag \| clean twin) | clean file |
| paired discrimination | P(flags the leaky file and not its twin) | twin pair |
| paired at the site | P(a flag on a site line of the leaky file, none on those lines or its own site lines in the twin) | twin pair |
| localisation | P(some flag within ±2 lines of a site line \| leaky file flagged) | flagged leaky file |

"Flag" means at least one finding from the rules the tool documents as look-ahead or leakage
rules, at any severity. For backtest-audit that excludes STAT001 (Sharpe without
annualisation) and STAT002 (no transaction costs). Two sensitivity tables change that
definition: every rule, and only the tool's top severity.

**Paired at the site is the primary measure.** File-level recall and paired discrimination
both count flags on code the twins share. A rule that fires on the signal line of both
twins adds recall the tool did not earn, and it can also mask a real hit on the leak. The site
measure ignores flags on shared code. The twin check covers both files' site lines, because
at L3 the dead leaky branch sits on lines that are site lines of the leaky file only.

Localisation at ±2 lines is reported beside the score a random code line would get on the
same files, because the scripts are small enough for that window to cover about half of
each file. The stricter "on a site line" count is next to it.

Recall is broken down by class, level and library. Coverage asks which classes no tool finds
at the site at any level.

## 2. Corpus

### 2.1 Taxonomy (15 classes)

| Class | Leak | Minimal fix |
|---|---|---|
| same_bar | decision held on the bar it was computed | lag one bar |
| negative_shift | `shift(-k)`, `pct_change(periods=-k)` as a feature | positive k |
| centered_rolling | `rolling(w, center=True)` (pandas, polars) | `center=False` |
| full_sample_scaling | full-sample z-score, demeaning, `StandardScaler().fit(X)` | expanding stats, or fit on the training prefix and trade only after it |
| backfill_interpolate | `bfill()`, `interpolate()`, `fill_null(strategy="backward")` | forward fill |
| resample_label | weekly bin stamped at its start (`label="left"`) and forward-filled | `label="right"` |
| asof_forward | `merge_asof`/`join_asof` with forward or nearest | backward |
| fundamentals_period_end | fundamentals placed at period end | place at filing date |
| restatement_overwrite | last restated value placed at the first filing date | first-reported value |
| survivorship | universe from end-of-sample membership or listing | as-of mask per row |
| shuffled_split | shuffled `train_test_split`; `KFold` out-of-fold predictions | `shuffle=False`; `TimeSeriesSplit` |
| groupby_transform | `groupby(...).transform("mean")` over the full history | expanding mean within group |
| np_roll | `np.roll` wraparound brings the last rows to the front | mask the wrapped rows |
| reversed_cumulative | `x[::-1].cummax()[::-1]`, `cum_max(reverse=True)`, reversed cumsum | forward cumulative |
| argmax_param | lookback or threshold chosen by Sharpe over the full sample | choose on the first half, trade the second |

The spec's "polars shift/rolling equivalents" item is the library axis: polars renderings
of the shift, rolling, fill, resample, as-of, scaling, group and cumulative classes.

### 2.2 Obfuscation levels

Each template has one *site*, where the twins differ.

- **L0**: a direct call with a literal (`returns.shift(-3)`).
- **L1**: the value passes through a local variable (`lag = -3; returns.shift(lag)`), or, for
  expression sites, the receiving object passes through an alias.
- **L2**: the operation is in a module-level helper, called with the literal.
- **L3**: the value or mode comes from `CONFIG = json.loads('...')` at module level, passed
  through a helper. For expression sites the helper holds both branches. So both twins
  contain the leaky expression, and only the config string differs.

L3 is built so that a purely syntactic tool cannot separate the twins. Its paired
discrimination measures whether a tool evaluates constants and configuration. Its false
positives are the price of flagging every syntactically leaky branch, so the scorecard
reports the false-positive rate per level.

### 2.3 Files, twins and the manifest

`leakseed generate` renders every (class, variant, library, level) case twice, once leaky and
once clean, from the same per-case random source. The twins therefore share every surface
choice: window lengths, horizons, helper, variable and config-key names. The generator
refuses a pair whose diff falls outside the marked site lines. Files are named by a hash of
(seed, case, label), so names reveal nothing. They contain no comments or docstrings that
hint at the label.

Manifest row: `id, path, sha256, cls, variant, template, lib, level, label, twin,
site_lines, diff_lines`. `site_lines` are the lines a linter should point at in a leaky
file; in a clean file they mark where the fix is. For L2/L3 they include the helper's
operation, the call and the config line.

`corpus/probes` is separate: three hand-written pairs in the surface forms that certain rules
need (section 5). No rate is computed from them.

## 3. Oracle

### 3.1 Contract

`run(data)` returns the positions *held over* each bar. A position held over bar j may use
data up to row j - 1: a decision taken at the close of bar t uses data up to t and is held
over t + 1. Every clean script ends with that lag. The same-bar class is the one where it
is missing. A bar covers its whole calendar day.

### 3.2 Test

For a cut t, `perturb(data, t, mode)` replaces everything observed after the close of
`dates[t]`. That means rows of the date-indexed frames after t, events stamped after day t
ends, and fundamentals rows with `filed > dates[t]`. The filing date is the availability
time, so point-in-time data are perturbed by when they became known, not by the period they
describe. Three modes:

- **values**: multiply prices and volumes by U(0.5, 1.5) per cell, redraw event and
  fundamental values.
- **availability**: fill existing gaps, blank a random asset, drop half of the later events
  and filings.
- **regime**: as values, but prices follow strong trend segments of a random typical length
  (4, 15 or 60 days). A choice that depends on future performance is pushed to change.

All modes negate index membership after t. The file is **leaky** if for some (t, mode) the
held positions in rows 0..t + 1 differ (relative tolerance 1e-9, NaN equal to NaN).
Otherwise it is **clean**. Each mode draws 16 cuts stratified from the later of 5% of n and
the first row with output up to n - 2, with a seed derived from the file id. Defaults:
n = 5,000 business days, 6 assets, data seed 2026.

The oracle refuses to give a verdict (and fails the build) when the output is malformed,
differs between two runs on the same data, is never finite, or never moves under any
perturbation. A check that cannot fail is not evidence.

### 3.3 Soundness and limits

- **Leak verdicts are sound.** A witness is two input histories that agree up to the close of
  t and produce different held positions at or before t + 1. The script therefore uses
  information from after t, whatever the template says. The witness (t, mode, row) is
  stored in `results/v1/oracle.jsonl`. An earlier version cut events at the midnight that
  opens day t, so a causal script using same-day events got a false leak verdict
  (`test_events_of_day_t_are_known_at_its_close`). All 368 labels held after the fix.
- **Clean verdicts are not proofs.** The oracle tries 48 (t, mode) pairs per file. A leak
  can hide when it appears only for a few t (each mode's grid is stratified, so a window
  wider than two strata, about 12% of the sample, always contains a cut; narrower windows
  are hit with probability that grows with their width), when its effect is absorbed (a sign
  that does not flip, an argmax that does not move), or when it shows up only in outputs the
  script masks. Tuned parameters are the hardest case, and twice a leaky argmax file passed
  as clean on another data seed. The regime mode came from the first time. The second came
  from a grid over the whole sample: scripts that trade only the second half had half their
  cuts before the first output, where nothing can differ. The grid now starts at the first
  output. `tests/test_corpus_oracle.py` keeps one file from each case. Replication below is
  what stands behind the clean labels, not the fixed grid alone.
- **Selection by the oracle.** A file enters the corpus only if the oracle agrees with its
  label, so v1 contains leaks a differential test can witness. arXiv:2607.04958 builds
  leaks a two-run differential detector misses: at unsampled times, behind thresholds the
  perturbation does not cross, and through a future value re-stamped as admissible. v1 has
  none of the first two kinds. Recall here is recall on witnessable leaks.
- **Replication.** All 368 labels are confirmed on data seeds 2026 (`results/v1/oracle.jsonl`),
  7, 11 and 13 (`results/v1/oracle_replication.json`), and every label of two fresh generator
  seeds on the default data (`results/fresh/`).
- **Scope of "leak".** The oracle catches dependence on the future. It does not judge
  whether the leak matters economically (section 7), and it does not catch leakage that has
  no time order (for example duplicated rows across a random split).
- **Only generated code runs.** `verify` re-hashes each file against the manifest before
  importing it. No linter executes corpus code.

## 4. Statistics

- **Cluster bootstrap for pooled rates.** The 4 levels x up to 3 libraries of one template
  share code, data flow and the tool behaviour that follows from them, so they are not
  independent trials. Pooled rates resample the 30 templates (class/variant) with
  replacement, 10,000 times, and report percentile 95% intervals. An interval of
  [0.0, 0.0] means no template had a flag; it is not a claim of zero variance. Percentile
  intervals are somewhat narrow with 30 clusters.
- **Clopper-Pearson for cells** (class x level, level, library, paired by level). These are
  exact for the binomial count. Within-cell correlation (libraries of one template at one
  level) is ignored, so they are somewhat narrow.
- **Sign-flip test for tool pairs.** McNemar's test assumes independent units, and files of
  one template are not, so its p-values are too small here: one template with 8 discordant
  files looks like 8 independent wins. The test to read flips the sign of each template's
  difference. It is exact, computed by convolution, and needs independent templates only.
  With m templates that differ, the smallest two-sided p is 2^(1 - m). The scorecard prints
  the file-level McNemar p next to it. Holm runs over the 21 linter pairs, separately for
  recall and for paired at the site. The null baseline is not compared.
- **Pooled rates depend on the mix.** They weight classes by their file counts and include
  L3, a level built to defeat syntactic rules. They are not estimates of recall on real code.
  The scorecard also gives the mean over classes, and rates per level.
- **Localisation** is conditional on a flag. A flag can land on a site line for an
  unrelated reason (peekproof's PP011 on an L3 call site, for example).

## 5. Threat model

- **Tuning on the corpus.** Once public, v1 can be learnt: rules written to match its exact
  idioms. v1 is frozen. `leakseed generate --check` fails if the generator no longer
  reproduces it byte for byte. Template changes go into a new version. A fresh generator seed
  alone is not enough to reveal tuning: it changes names and window lengths and keeps every
  idiom, so seeds 101 and 202 score almost exactly like v1 (`results/fresh/`). That shows the
  rates do not hang on those surface choices. Detecting tuning takes new templates.
- **Who read what first.** lookahead-lint, peekproof, backtest-audit and leakguard were read
  during the first build, so the templates may reflect their rules. overfit-gauntlet,
  monte-neo and nofuturedata were read after v1 was generated, and v1 did not change
  afterwards, so only those three are strictly out of sample.
- **Corpus style.** Neutral names and no vendor APIs mean that rules keyed to identifiers
  (PP012 looks for constituent-like names) or to yfinance (PP013) have nothing to match.
  Those zeros measure fit to this corpus, not the rules' value on real code.
- **No pnl expression.** Scripts return positions and do not multiply them by returns.
  Rules that look for `position * returns` without a lag (PP010) have no such expression to
  inspect. The same-bar class encodes the bug at the missing lag. `corpus/probes` shows
  PP010 firing once that line exists (`results/v1/probes.md`).
- **Forms outside the templates.** No template indexes `i + k` in a loop, reads a target
  column into a feature, or fits a model at import time, so LA006, PP009, LG005 and similar
  rules have nothing to match.
- **Adapters.** Each adapter maps the tool's own JSON. Parsing is tested on outputs recorded
  from the pinned versions (`tests/fixtures/tools`). A tool error or unparseable file fails
  the run instead of counting as "no finding".

## 6. Tools: vetting and pinning

Every candidate was read as text first (PyPI JSON, wheel contents, GitHub API) without
running it. The checks: code that runs on import or install, network or process calls,
encoded blobs, provenance, dependencies, and text aimed at agents.

| Tool | Source | Pinned | Notes | Verdict |
|---|---|---|---|---|
| lookahead-lint | PyPI | 1.0.1 (2026-08-15) | stdlib only; no network/exec | used |
| peekproof | GitHub Thesimpleex/peekproof | commit e6c56c3 (2026-10-04) | numpy, pandas; `importlib` only in its runtime `check` command, which is not used | used (static `lint` only) |
| backtest-audit | PyPI | 1.0.0 (2026-03-20) | click only; no repository URL (weak provenance), code small and clean | used; STAT rules excluded from the primary analysis |
| leakguard-mcp | PyPI | 0.1.1 (2026-06-13) | static core needs libcst only; the MCP server (fastmcp) is excluded with a never-matching uv override | used via its pure-Python `LeakGuard.scan_result` |
| overfit-gauntlet | PyPI | 0.1.0 (2026-07-07) | numpy, scipy; `lint.py` is one stdlib AST module | used via `lint_path` |
| monte-neo | PyPI | 0.54.0 (2026-10-20) | large verifier with subprocess, network and execution paths; `monte_neo.verify.lint` and `lint_ml` are stdlib AST modules and the package imports lazily. numba and mcp are excluded with never-matching overrides | used via `lint_source` only; nothing else in the package is called |
| nofuturedata | GitHub ORANGINGS/nofuturedata | commit fb46880 (2026-09-17) | no runtime dependencies; `audit.py` is a stdlib AST pass, not on PyPI | used via `nofuture scan --time-series` |
| qtype | PyPI | - | the PyPI name belongs to an unrelated generative-AI DSL with heavy cloud dependencies; no leakage linter of that name found on PyPI or GitHub | dropped |
| leakage-analysis (ASE 2022) | GitHub malusamayo/leakage-analysis | - | needs the Souffle Datalog engine, a custom pyright build and Python 3.8 (or Docker); targets ML train/test leakage without time order | dropped (heavy, out of scope) |
| ruff | PyPI | 0.17.1 (dev dependency) | defaults via `--isolated` | null baseline |

Scored as static tools only. Runtime detectors (peekproof's `check`, monte-neo's probes,
nofuturedata's invariance checks, peekahead, nullius, freqtrade's `lookahead-analysis`) need a
different harness and are not in the scorecard. pylint was not added as a second null
baseline because it would add dependencies for no new information. ruff's defaults already
show that a general linter flags nothing here (the corpus is ruff-clean by construction).

## 7. Size of the leak

The oracle says whether a script sees the future, not how much that is worth.
`leakseed impact` runs every file on five data seeds and records the annualised Sharpe of
holding its positions (`results/v1/impact.jsonl`). Prices in the synthetic data have no drift
and no autocorrelation, so a causal script has an expected Sharpe of zero. A leak can earn
far from zero with either sign, depending on which way the template trades, so the table
uses |Sharpe|. A leaky file is *material* at |Sharpe| >= 1, five times the largest clean
twin.

Events and fundamentals are independent of prices in this data, so leaks through those
channels cannot show here. A low number for a price-based class does mean the leak is small
in this script: `np_roll` wraps only the first rows, and a full-sample demean moves a slow
signal little. It says nothing about the same leak with a stronger signal.

## 8. Prior art (checked 2026-11-06)

No public, independent, multi-tool evaluation of Python look-ahead linters was found.

- **Tool authors' own sets.** leakguard ships 49 labelled snippets and calls its trading
  portion regression fixtures, not independent validation. nofuturedata ships a 31-case
  conformance corpus, 24 paired notebooks and 21 documented external cases, and says the
  first two do not estimate real-world recall. peekproof lists a public labelled corpus
  under "Planned next". None scores other tools or verifies labels by execution.
- **arXiv:2607.04958** ("Look-Ahead-Freedom as Temporal Non-Interference") has an adversarial
  corpus of 33 leaks and 20 clean cases over a typed pipeline DSL. It is not Python code, it
  evaluates no third-party linter, and at the time of writing the artifact is promised on
  acceptance.
- **Look-Ahead-Bench** (arXiv:2601.13770) and related work measure what LLMs remember about
  the future, not leaks in code.
- **Seeded-bug corpora** (Defects4J, BugsInPy) are not about time order.
- **Yang et al., ASE 2022** detect train/test leakage in notebooks. They have no focus on
  time-series look-ahead and no seeded corpus with clean twins.
