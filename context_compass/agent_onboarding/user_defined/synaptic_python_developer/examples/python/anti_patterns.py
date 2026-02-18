"""
Purpose:
- Catalog banned patterns to avoid in this repo.

Notes:
- Use this file as a negative checklist during reviews.
- These examples are intentionally not executable patterns.
"""

from typing import Tuple


def list_anti_patterns() -> Tuple[str, ...]:
    """
    Return a list of anti-patterns to avoid.

    Returns:
        Tuple[str, ...]: Human-readable anti-pattern descriptions.
    """
    return (
        "Avoid print statements; use logging.",
        "Avoid type-ignore directives in typed code.",
        "Avoid noqa-style lint suppression pragmas.",
        "Avoid from __future__ import annotations; Python 3.14 uses native annotations.",
        "Avoid PEP 604 unions (A | B, T | None); use Optional/Union.",
        "Avoid dynamic code execution helpers.",
        "Avoid wildcard imports.",
        "Avoid getattr/hasattr for owned attributes.",
        "Avoid defensive local alias for nullable owned dependency.",
        "Avoid snapshotting owned self._fields into locals as defensive cleanup guards.",
        "Avoid defensive None checks on owned fields when lifecycle guarantees they exist.",
        "Avoid relying on GC for owned resources; cleanup must be explicit.",
        "Avoid skipping explicit null assignments after cleanup.",
        "Avoid cleaning loggers before owned children; logger teardown is last.",
        "Avoid placeholder comments like 'already nulled above' instead of nulling fields.",
    )
