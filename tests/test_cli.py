"""What the command line refuses before it writes anything."""

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
