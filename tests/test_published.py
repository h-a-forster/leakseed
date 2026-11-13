"""README.md and REPORT.md publish copies of results/v1, never numbers typed by hand.

CI rebuilds results/v1 with `leakseed report --readme README.md` and fails on any diff; these
tests check the copies against the committed files.
"""

import json
from pathlib import Path

import pytest

from leakseed import published

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "v1"
MAPS = ("| Path |",)  # file maps, the only tables without results in them


def _summary() -> dict:
    return json.loads((RESULTS / "summary.json").read_text(encoding="utf-8"))


def _result_rows(path: Path) -> list[str]:
    rows, skipping = [], False
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            skipping = False
        elif line.startswith(MAPS):
            skipping = True
        elif line.startswith("| ") and not skipping:
            rows.append(line)
    return rows


@pytest.mark.parametrize("doc", ["README.md", "REPORT.md"])
def test_every_table_row_is_copied_from_the_published_tables(doc):
    source = (RESULTS / "published.md").read_text(encoding="utf-8").splitlines()
    rows = _result_rows(ROOT / doc)
    assert rows
    assert [row for row in rows if row not in source] == []


def test_published_tables_render_from_the_committed_summary():
    rendered = published.render(_summary())
    assert (RESULTS / "published.md").read_text(encoding="utf-8") == rendered


def test_readme_headline_prose_is_the_generated_block():
    block = published.readme_block(_summary())
    assert block in (ROOT / "README.md").read_text(encoding="utf-8")


def test_readme_corpus_figures_match_the_summary():
    s = _summary()
    c, o = s["corpus"], s["oracle"]
    text = " ".join((ROOT / "README.md").read_text(encoding="utf-8").split())
    assert f"{c['files']} scripts = {c['pairs']} leak/clean pairs" in text
    assert f"{c['classes']} leak classes x {len(c['levels'])} obfuscation levels" in text
    assert f"from {c['templates']} templates" in text
    assert f"({o['n_t']} cuts per mode" in text
    assert o["agree"] == o["total"] and f"All {o['total']} labels" in text


def test_prose_refuses_a_summary_that_contradicts_it():
    s = _summary()
    s["tools"]["peekproof"]["paired_site_by_level"]["L3"]["k"] = 1
    with pytest.raises(ValueError, match="L3"):
        published.readme_block(s)


def test_readme_sync_refuses_text_without_markers():
    with pytest.raises(ValueError):
        published.sync_readme("# no markers\n", "block")
