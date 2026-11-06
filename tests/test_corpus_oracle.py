"""Manifest/oracle agreement on a subsample of the frozen corpus (runs in CI)."""

import random
import zlib
from pathlib import Path

from leakseed.data import make_data
from leakseed.generate import read_manifest
from leakseed.oracle import check, load_run, verify

V1 = Path(__file__).resolve().parents[1] / "corpus" / "v1"


def test_oracle_confirms_labels_on_one_pair_per_template():
    manifest = read_manifest(V1)
    rng = random.Random(0)
    ids = []
    for template in sorted({r["template"] for r in manifest}):
        leak = rng.choice(
            [r for r in manifest if r["template"] == template and r["label"] == "leak"]
        )
        ids += [leak["id"], leak["twin"]]
    verdicts = verify(V1, n=1500, n_t=8, ids=ids)
    assert len(verdicts) == len(ids)
    bad = [(v.id, v.label, v.verdict, v.error) for v in verdicts if not v.agrees]
    assert not bad, bad


def test_regime_mode_catches_a_tuned_parameter_the_other_modes_miss():
    # With data seed 7, the values and availability modes never flip this file's argmax;
    # trend segments of a random length do (docs/DESIGN.md, section 3).
    row = next(r for r in read_manifest(V1) if r["id"] == "f8d7dc03d7f")
    assert (row["cls"], row["label"]) == ("argmax_param", "leak")
    run = load_run(V1 / row["path"])
    data = make_data(5000, 7)
    seed = zlib.crc32(row["id"].encode())
    assert check(run, data, seed=seed, modes=("values", "availability"))[0] == "clean"
    assert check(run, data, seed=seed)[0] == "leak"


def test_a_file_that_trades_the_second_half_gets_all_its_cuts_there():
    # With cuts over the whole sample this file passed as clean on data seed 7.
    row = next(r for r in read_manifest(V1) if r["id"] == "f1290f0ad64")
    assert (row["cls"], row["label"]) == ("argmax_param", "leak")
    run = load_run(V1 / row["path"])
    assert check(run, make_data(5000, 7), seed=zlib.crc32(row["id"].encode()))[0] == "leak"
