"""What the command line refuses before it writes anything."""

import json

import pytest

from leakseed.cli import main
from leakseed.generate import CorpusError, write


def _contents(root):
    return {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_results_of_two_corpora_never_mix(tmp_path):
    ours, other, out = tmp_path / "ours", tmp_path / "other", tmp_path / "results"
    write(ours, 1)
    write(other, 2)
    main(["score", "--tool", "ruff-defaults", "--corpus", str(ours), "--out", str(out)])
    before = _contents(out)
    for argv in (
        ["score", "--tool", "ruff-defaults", "--corpus", str(other), "--out", str(out)],
        ["report", "--corpus", str(other), "--results", str(out)],
        ["impact", "--corpus", str(other), "--out", str(out), "--n", "300", "--data-seeds", "1"],
        ["verify", "--corpus", str(other), "--out", str(out), "--n", "300", "--n-t", "1"],
        ["verify", "--corpus", str(other), "--out", str(out), "--n", "300", "--data-seed", "7"],
    ):
        with pytest.raises(CorpusError, match="another corpus"):
            main(argv)
    assert _contents(out) == before
    main(["score", "--tool", "ruff-defaults", "--corpus", str(ours), "--out", str(out)])


def test_a_replication_must_use_the_main_runs_settings(tmp_path):
    corpus, out = tmp_path / "corpus", tmp_path / "results"
    write(corpus, 1)
    argv = ["verify", "--corpus", str(corpus), "--out", str(out), "--data-seed", "7"]
    with pytest.raises(SystemExit, match="default data seed first"):
        main([*argv, "--n", "299"])
    assert not out.exists()
    out.mkdir()
    (out / "oracle_meta.json").write_text('{"n": 299, "n_t": 16}\n', encoding="utf-8")
    before = _contents(out)
    for extra in (["--n", "298"], ["--n", "299", "--n-t", "1"]):
        with pytest.raises(SystemExit, match="must use the settings"):
            main([*argv, *extra])
    assert _contents(out) == before
    # At the main run's settings the guard lets it through and the entry is written. Two files
    # keep it fast; n = 299 makes each file an error verdict, which still counts in the entry.
    manifest = corpus / "manifest.jsonl"
    manifest.write_text("".join(manifest.read_text("utf-8").splitlines(True)[:2]), "utf-8")
    assert main([*argv, "--n", "299"]) == 1
    replication = out / "oracle_replication.json"
    entry = json.loads(replication.read_text("utf-8"))["7"]
    assert entry == {"agree": 0, "total": 2, "n": 299, "n_t": 16}
    # A main run keeps the replications of its settings, including an entry written before
    # entries carried settings, and drops them all once it runs at other settings.
    legacy = {**json.loads(replication.read_text("utf-8")), "11": {"agree": 2, "total": 2}}
    replication.write_text(json.dumps(legacy), encoding="utf-8")
    main_run = ["verify", "--corpus", str(corpus), "--out", str(out)]
    main([*main_run, "--n", "299"])
    assert json.loads(replication.read_text("utf-8")) == legacy
    main([*main_run, "--n", "298"])
    assert json.loads(replication.read_text("utf-8")) == {}
