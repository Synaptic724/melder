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
    )
