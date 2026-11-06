"""Write a corpus: one leaky file and one clean twin per case, plus a JSONL manifest."""

from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path

from . import __version__
from .templates import CLASSES, case_ids, render_case

#: The seed of the frozen v1 corpus. Never change it; a new version gets a new seed.
V1_SEED = 20261030
MANIFEST = "manifest.jsonl"
VERSION_FILE = "VERSION.json"


class CorpusError(Exception):
    """A corpus that is inconsistent with its manifest or generator."""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_id(seed: int, case: tuple[str, ...], label: str) -> str:
    return "f" + sha256_text(f"{seed}:{'/'.join(case)}:{label}")[:10]


def changed_lines(a: str, b: str) -> list[int]:
    """1-based line numbers of ``a`` that differ from ``b``.

    Where ``b`` has lines that ``a`` lacks, the line of ``a`` just before the gap counts.
    """
    out: set[int] = set()
    a_lines, b_lines = a.splitlines(), b.splitlines()
    for tag, i1, i2, _j1, _j2 in difflib.SequenceMatcher(None, a_lines, b_lines).get_opcodes():
        if tag == "equal":
            continue
        if i2 > i1:
            out.update(range(i1 + 1, i2 + 1))
        else:
            out.add(max(i1, 1))
    return sorted(out)


def build(seed: int) -> list[tuple[dict, str]]:
    """Render every case for ``seed``; return (manifest row, source) pairs. Writes nothing."""
    rows: list[tuple[dict, str]] = []
    for case in case_ids():
        cls, variant, lib, level = case
        leak_src, leak_site = render_case(seed, case, leak=True)
        clean_src, clean_site = render_case(seed, case, leak=False)
        if leak_src == clean_src:
            raise CorpusError(f"{case}: leaky and clean renderings are identical")
        for src, site, other in (
            (leak_src, leak_site, clean_src),
            (clean_src, clean_site, leak_src),
        ):
            diff = changed_lines(src, other)
            if not site or not set(diff) <= set(site):
                raise CorpusError(f"{case}: diff lines {diff} are not all site lines {site}")
        ids = {lab: file_id(seed, case, lab) for lab in ("leak", "clean")}
        for label, src, site in (("leak", leak_src, leak_site), ("clean", clean_src, clean_site)):
            row = {
                "id": ids[label],
                "path": f"files/{ids[label]}.py",
                "sha256": sha256_text(src),
                "cls": cls,
                "variant": variant,
                "template": f"{cls}/{variant}",
                "lib": lib,
                "level": level,
                "label": label,
                "twin": ids["clean" if label == "leak" else "leak"],
                "site_lines": site,
                "diff_lines": changed_lines(src, leak_src if label == "clean" else clean_src),
            }
            rows.append((row, src))
    rows.sort(key=lambda r: r[0]["id"])
    return rows


def write(out_dir: Path, seed: int) -> list[dict]:
    """Generate the corpus into an empty (or absent) ``out_dir``."""
    out_dir = Path(out_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        raise CorpusError(f"{out_dir} is not empty; a corpus is never overwritten in place")
    rows = build(seed)
    (out_dir / "files").mkdir(parents=True)
    for row, src in rows:
        (out_dir / row["path"]).write_text(src, encoding="utf-8", newline="\n")
    manifest = "".join(json.dumps(r, sort_keys=True) + "\n" for r, _ in rows)
    (out_dir / MANIFEST).write_text(manifest, encoding="utf-8", newline="\n")
    version = {
        "seed": seed,
        "generator": __version__,
        "files": len(rows),
        "classes": len(CLASSES),
        "manifest_sha256": sha256_text(manifest),
    }
    (out_dir / VERSION_FILE).write_text(
        json.dumps(version, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return [r for r, _ in rows]


def read_manifest(corpus: Path) -> list[dict]:
    path = Path(corpus) / MANIFEST
    if not path.is_file():
        raise CorpusError(f"no {MANIFEST} in {corpus}")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def read_source(corpus: Path, row: dict) -> str:
    """Read a corpus file, refusing one whose hash does not match the manifest."""
    path = Path(corpus) / row["path"]
    src = path.read_bytes().decode("utf-8").replace("\r\n", "\n")
    if sha256_text(src) != row["sha256"]:
        raise CorpusError(f"{row['path']}: content does not match the manifest hash")
    return src


def check_snapshot(corpus: Path) -> dict:
    """Check that a committed corpus matches its manifest and its seed's regeneration."""
    corpus = Path(corpus)
    version = json.loads((corpus / VERSION_FILE).read_text(encoding="utf-8"))
    manifest = read_manifest(corpus)
    for row in manifest:
        read_source(corpus, row)
    rebuilt = [r for r, _ in build(version["seed"])]
    if rebuilt != manifest:
        raise CorpusError(
            f"the generator no longer reproduces {corpus} from seed {version['seed']}; a frozen "
            "version must not change. Put template changes in a new version with a new seed."
        )
    listed = {r["path"] for r in manifest}
    present = {f"files/{p.name}" for p in (corpus / "files").glob("*.py")}
    if listed != present:
        raise CorpusError(f"files and manifest disagree: {sorted(listed ^ present)[:5]}")
    return version
