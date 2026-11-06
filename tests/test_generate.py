import json
from pathlib import Path

import pytest

from leakseed.generate import (
    V1_SEED,
    CorpusError,
    build,
    changed_lines,
    check_snapshot,
    read_manifest,
    read_source,
    write,
)
from leakseed.templates import CLASSES, LEVELS

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "corpus" / "v1"


def test_same_seed_gives_same_bytes_and_hashes():
    a, b = build(7), build(7)
    assert [r for r, _ in a] == [r for r, _ in b]
    assert [s for _, s in a] == [s for _, s in b]


def test_a_new_seed_changes_surface_forms_but_not_the_design():
    a = {(r["template"], r["lib"], r["level"], r["label"]): s for r, s in build(1)}
    b = {(r["template"], r["lib"], r["level"], r["label"]): s for r, s in build(2)}
    assert a.keys() == b.keys()
    assert sum(a[k] != b[k] for k in a) > len(a) // 2


def test_twins_differ_only_on_site_lines_and_cover_the_grid():
    rows = [r for r, _ in build(V1_SEED)]
    assert len(rows) == 2 * sum(4 * len(c.combos) for c in CLASSES.values())
    by_id = {r["id"]: r for r in rows}
    for r in rows:
        twin = by_id[r["twin"]]
        assert twin["twin"] == r["id"] and twin["label"] != r["label"]
        assert set(r["diff_lines"]) <= set(r["site_lines"])
        assert r["diff_lines"]
    assert {r["level"] for r in rows} == set(LEVELS)


def test_changed_lines_marks_the_line_before_a_deletion():
    assert changed_lines("a\nb\nc\n", "a\nb\nx\nc\n") == [2]
    assert changed_lines("a\nx\nc\n", "a\ny\nc\n") == [2]


def test_frozen_v1_snapshot_reproduces():
    version = check_snapshot(V1)
    assert version["seed"] == V1_SEED
    assert version["files"] == len(read_manifest(V1))


def test_write_refuses_a_non_empty_directory_and_tampered_files(tmp_path):
    out = tmp_path / "c"
    write(out, 5)
    with pytest.raises(CorpusError, match="not empty"):
        write(out, 5)
    row = read_manifest(out)[0]
    path = out / row["path"]
    path.write_text(path.read_text(encoding="utf-8") + "# edited\n", encoding="utf-8")
    with pytest.raises(CorpusError, match="does not match"):
        read_source(out, row)


def test_manifest_rows_carry_the_documented_fields():
    row = json.loads((V1 / "manifest.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert set(row) == {
        "id", "path", "sha256", "cls", "variant", "template", "lib", "level", "label", "twin",
        "site_lines", "diff_lines",
    }  # fmt: skip
