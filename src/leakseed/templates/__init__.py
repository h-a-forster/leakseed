"""Parameterised templates for leaky backtest scripts and their clean twins."""

from __future__ import annotations

import hashlib
import random

from .classes import CLASSES, LeakClass
from .core import LEVELS, LIBS, Ctx, Program

__all__ = ["CLASSES", "LEVELS", "LIBS", "Ctx", "LeakClass", "Program", "case_ids", "render_case"]


def case_ids() -> list[tuple[str, str, str, str]]:
    """Every (class, variant, library, level) case, in a fixed order."""
    return [
        (c.name, variant, lib, level)
        for c in CLASSES.values()
        for variant, lib in c.combos
        for level in LEVELS
    ]


def case_rng(seed: int, case: tuple[str, str, str, str]) -> random.Random:
    digest = hashlib.sha256(f"{seed}:{'/'.join(case)}".encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def render_case(seed: int, case: tuple[str, str, str, str], leak: bool) -> tuple[str, list[int]]:
    """Render one side of a twin pair; returns the source and its site line numbers."""
    cls, variant, lib, level = case
    ctx = Ctx(cls, variant, lib, level, leak, case_rng(seed, case))
    return CLASSES[cls].render(ctx).render()
