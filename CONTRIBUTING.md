# Contributing

Bug reports, new leak classes, new tool adapters and documentation fixes are welcome. Read
[docs/DESIGN.md](docs/DESIGN.md) first: it fixes the estimands, the oracle's contract and
what a label means.

## Setup

You need [uv](https://docs.astral.sh/uv/) and git. From a clone:

```sh
uv sync                  # the project and the pinned linters
uv run leakseed --version
```

## Tests and lint

```sh
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv lock --check
```

CI runs lint and tests on Ubuntu (Python 3.12) and Windows (Python 3.13). Tests must run
offline, write only under pytest's `tmp_path`, use fixed seeds and pass on Windows. A bug fix
comes with a test that fails without it.

## Add a leak class

1. Add a render function and a `CLASSES` entry in
   [src/leakseed/templates/classes.py](src/leakseed/templates/classes.py). Use `param_site`
   when the twins differ by one value and `mode_site` when they differ by an expression.
2. Every clean script ends with the one-bar lag of the contract (DESIGN.md, section 3.1).
3. Render into a scratch corpus, not `corpus/v1`:
   `uv run leakseed generate --seed 7 --out tmp/c7`, then
   `uv run leakseed verify --corpus tmp/c7 --workers 3 --out tmp/r7`.
   The oracle must agree with every label on data seeds 2026, 7, 11 and 13
   (`--data-seed S`). If it does not, fix the template; never relax the oracle to fit a label.
4. New templates enter the next corpus version, under a new seed. **v1 is frozen**:
   `leakseed generate --check` must keep passing, so adding a class needs a generator switch
   that leaves v1's cases unchanged.

## Add a tool adapter

1. Read the tool as text first: wheel or repository contents, without running it. Record what
   you checked in the table in DESIGN.md, section 6.
2. Pin it in the `tools` group of [pyproject.toml](pyproject.toml), to a version or a commit.
3. Add an `Adapter` subclass in
   [src/leakseed/adapters/__init__.py](src/leakseed/adapters/__init__.py). `parse` maps the
   tool's own output to `Finding(path, line, rule, severity)` and raises `AdapterError` on a
   tool error or an unparsed file, so that a failure is never scored as "no finding". Set
   `leak_rules` if the tool has rules unrelated to leakage, and `top_severity` if it grades
   findings.
4. Record its real output on the fixture files as `tests/fixtures/tools/<name>.json` and add
   the expected findings to `tests/test_adapters.py`.
5. Static runs only: an adapter never executes corpus code.

## Code

- Python 3.12+. Runtime dependencies: numpy, pandas, polars, scikit-learn (the corpus scripts
  use them) and scipy. Open an issue before adding one.
- Validate inputs before writing anything, and fail with a clear error rather than dropping
  data.
- Line length 100; ruff enforces the rest. Write text files as UTF-8 with LF line endings.

## Results

Files under `results/` are generated. Never edit them by hand; regenerate with the commands in
[README.md](README.md), and keep every number in README.md and REPORT.md traceable to them.
Put scratch output in `tmp/`.

## Pull requests

- One change per pull request, with tests and docs.
- Put change notes in `docs/release-notes-<version>.md`.
- Keep [backlog.md](backlog.md) and the status section of [AGENTS.md](AGENTS.md) current.

Security issues: see [SECURITY.md](SECURITY.md).
