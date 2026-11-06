"""Rendering framework for corpus scripts.

A template builds a :class:`Program`: imports, an optional ``CONFIG`` (level L3), helper
functions (L2, L3) and the body of ``run(data)``. Exactly one *site* per program holds the
difference between the leaky file and its clean twin. :func:`param_site` covers sites where
the twins differ by one value (a shift, a flag, a method name); :func:`mode_site` covers sites
where they differ by an expression (a full-sample statistic against an expanding one).

The obfuscation level decides how the site is written:

- L0: the call is written directly with a literal.
- L1: the value (param sites) or the receiving object (mode sites) passes through a local name.
- L2: the operation lives in a module-level helper function, called with the literal.
- L3: the value or mode comes from a ``CONFIG`` parsed from JSON text at module level and is
  passed through a helper, so no literal at the call site reveals it.

Lines that belong to the site are marked. The marks become the manifest's ``site_lines``:
in a leaky file they are where a linter should point, in a clean file where the fix is.
"""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass, field

LEVELS = ("L0", "L1", "L2", "L3")
LIBS = ("pandas", "numpy", "polars")

INDENT = "    "


@dataclass
class Ctx:
    """What one rendering is asked for, plus the per-case random source for surface choices.

    Twins are rendered from contexts that differ only in ``leak``; every template must make the
    same sequence of ``pick`` calls for both, so the twins share all surface choices.
    """

    cls: str
    variant: str
    lib: str
    level: str
    leak: bool
    rng: random.Random

    def pick(self, options):
        return options[self.rng.randrange(len(options))]


@dataclass
class Line:
    text: str
    site: bool = False


@dataclass
class Program:
    imports: list[str] = field(default_factory=list)
    marked_imports: set[str] = field(default_factory=set)
    config: dict | None = None
    helpers: list[list[Line]] = field(default_factory=list)
    body: list[Line] = field(default_factory=list)
    site_count: int = 0

    def need(self, *imports: str, site: bool = False) -> None:
        for imp in imports:
            if imp not in self.imports:
                self.imports.append(imp)
            if site:
                self.marked_imports.add(imp)

    def add(self, code: str, site: bool = False, indent: int = 1) -> None:
        """Append body lines (``code`` may hold several lines) at ``indent`` levels."""
        for raw in code.splitlines():
            self.body.append(Line(INDENT * indent + raw if raw else "", site))

    def render(self) -> tuple[str, list[int]]:
        """Return the source text and the 1-based line numbers of the site."""
        if self.site_count != 1:
            raise ValueError(f"a program needs exactly one site, got {self.site_count}")
        import_block: list[Line] = []
        for stdlib in (True, False):
            group = _merged_imports([i for i in self.imports if _is_stdlib(i) == stdlib])
            if group:
                if import_block:
                    import_block.append(Line(""))
                import_block.extend(
                    Line(text, bool(set(parts) & self.marked_imports)) for text, parts in group
                )
        sections = [import_block]
        if self.config is not None:
            payload = json.dumps(self.config)
            sections.append([Line(f"CONFIG = json.loads('{payload}')", True)])
        sections.extend(self.helpers)
        sections.append([Line("def run(data):"), *self.body])
        out: list[Line] = []
        for section in sections:
            if out:
                # isort: one blank line before module-level code, PEP 8: two before a def.
                out += [Line("")] if section[0].text.startswith("CONFIG") else [Line(""), Line("")]
            out.extend(section)
        text = "\n".join(line.text for line in out) + "\n"
        site = [i + 1 for i, line in enumerate(out) if line.site]
        return text, site


def _is_stdlib(imp: str) -> bool:
    return imp.split()[1].split(".")[0] in {"json", "math"}


def _merged_imports(imports: list[str]) -> list[tuple[str, list[str]]]:
    """isort layout: straight imports first, then one ``from`` line per module, names sorted."""
    straight = sorted(i for i in imports if i.startswith("import "))
    froms: dict[str, list[str]] = {}
    for imp in imports:
        if imp.startswith("from "):
            froms.setdefault(imp.split()[1], []).append(imp)
    out = [(i, [i]) for i in straight]
    for module in sorted(froms):
        names = sorted(i.split(" import ")[1] for i in froms[module])
        out.append((f"from {module} import {', '.join(names)}", froms[module]))
    return out


def _lit(value) -> str:
    """A Python literal, with strings in double quotes as ruff format writes them."""
    return json.dumps(value) if isinstance(value, str) else repr(value)


def _sub_names(code: str, mapping: dict[str, str]) -> str:
    for old, new in mapping.items():
        code = re.sub(rf"(?<![\w.\"']){re.escape(old)}\b", new, code)
    return code


def _indented(code: str, levels: int) -> list[str]:
    return [INDENT * levels + raw if raw else "" for raw in code.splitlines()]


def param_site(
    prog: Program,
    ctx: Ctx,
    *,
    out: str,
    args: list[str],
    code: str,
    name: str,
    leak,
    clean,
    helper: str,
    l0: tuple[str, str] | None = None,
    indent: int = 1,
) -> None:
    """A site where the twins differ by one value, written ``{v}`` in ``code``.

    ``code`` is a block of statements that reads ``args`` and assigns ``out``. ``l0`` optionally
    gives the literal leaky and clean blocks for L0 when the natural leak omits a call rather
    than passing a different value (for example ``signal`` against ``signal.shift(1)``).
    """
    if out in args:
        raise ValueError("a site must not reassign one of its arguments")
    value = leak if ctx.leak else clean
    prog.site_count += 1
    if ctx.level == "L0":
        block = (l0[0] if ctx.leak else l0[1]) if l0 else code.replace("{v}", _lit(value))
        prog.add(block, site=True, indent=indent)
        return
    if ctx.level == "L1":
        prog.add(f"{name} = {_lit(value)}", site=True, indent=indent)
        for raw in code.splitlines():
            prog.add(raw.replace("{v}", name), site="{v}" in raw, indent=indent)
        return
    hname = f"_{helper}"
    lines = [Line(f"def {hname}({', '.join(args)}, {name}):")]
    for raw in code.splitlines():
        lines.append(Line(_indented(raw.replace("{v}", name), 1)[0], "{v}" in raw))
    lines.append(Line(f"{INDENT}return {out}"))
    prog.helpers.append(lines)
    if ctx.level == "L2":
        call_value = _lit(value)
    else:
        prog.need("import json")
        prog.config = {name: value}
        call_value = f'CONFIG["{name}"]'
    prog.add(f"{out} = {hname}({', '.join(args)}, {call_value})", site=True, indent=indent)


def mode_site(
    prog: Program,
    ctx: Ctx,
    *,
    out: str,
    args: list[str],
    leak_code: str,
    clean_code: str,
    name: str,
    modes: tuple[str, str],
    helper: str,
    alias: str,
    leak_imports: tuple[str, ...] = (),
    clean_imports: tuple[str, ...] = (),
    indent: int = 1,
) -> None:
    """A site where the twins differ by an expression block.

    ``leak_code`` and ``clean_code`` read ``args`` and assign ``out``. ``modes`` names the two
    behaviours for the L3 config (leaky first). Imports needed by only one side are added as
    site lines, except at L3 where the helper holds both branches and needs both.
    """
    if out in args:
        raise ValueError("a site must not reassign one of its arguments")
    chosen = leak_code if ctx.leak else clean_code
    prog.site_count += 1
    if ctx.level != "L3":
        prog.need(*(leak_imports if ctx.leak else clean_imports), site=True)
    if ctx.level == "L0":
        prog.add(chosen, site=True, indent=indent)
        return
    if ctx.level == "L1":
        prog.add(f"{alias} = {args[0]}", indent=indent)
        prog.add(_sub_names(chosen, {args[0]: alias}), site=True, indent=indent)
        return
    hname = f"_{helper}"
    if ctx.level == "L2":
        lines = [Line(f"def {hname}({', '.join(args)}):")]
        lines += [Line(t, True) for t in _indented(chosen, 1)]
        lines.append(Line(f"{INDENT}return {out}"))
        prog.helpers.append(lines)
        prog.add(f"{out} = {hname}({', '.join(args)})", site=True, indent=indent)
        return
    prog.need(*leak_imports, *clean_imports)
    prog.need("import json")
    prog.config = {name: modes[0] if ctx.leak else modes[1]}
    lines = [Line(f"def {hname}({', '.join(args)}, {name}):")]
    lines.append(Line(f'{INDENT}if {name} == "{modes[0]}":', ctx.leak))
    lines += [Line(t, ctx.leak) for t in _indented(leak_code, 2)]
    lines.append(Line(f"{INDENT * 2}return {out}"))
    lines += [Line(t, not ctx.leak) for t in _indented(clean_code, 1)]
    lines.append(Line(f"{INDENT}return {out}"))
    prog.helpers.append(lines)
    prog.add(f'{out} = {hname}({", ".join(args)}, CONFIG["{name}"])', site=True, indent=indent)
