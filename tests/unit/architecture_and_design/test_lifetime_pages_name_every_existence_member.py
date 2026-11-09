"""Regression: the lifetime design pages name every `Existence` member.

Symptom:
    `Existence.managed_spell_quantity` became the seventh lifetime (0.2.8241-0.2.8246), but
    `architecture_and_design/02_architecture/ownership_and_lifetimes.md` and
    `architecture_and_design/05_engineering_drawings/README.md` still enumerated six
    (issue #255). Nothing failed: the pages are prose, and no test tied them to the enum.

Contract under test:
    Each page names every member of `Existence` as a code span - the member name in
    backticks, the form both pages use for lifetimes - so a member added to the enum
    fails here until both pages describe it.

Scope note:
    The check proves that a page names a member, not that the page describes it
    correctly; that stays a review duty against the source. The diagrams the pages embed
    are not checked: they are drawings, not prose.
"""

from pathlib import Path
from typing import List, Tuple

import pytest

from melder.aether.spellbook.existence.existence import Existence


def _lifetime_page_relative_paths() -> Tuple[str, ...]:
    """
    Return the repository-relative paths of the design pages that enumerate lifetimes.

    Contract:
        - Exactly the two pages issue #255 found enumerating six lifetimes. A page that
          starts enumerating lifetimes later belongs in this tuple too.
        - Paths use forward slashes and are resolved against the repository root by
          `_read_page`.

    Returns:
        Tuple[str, ...]: The page paths, in the order the documentation links them.
    """
    return (
        "architecture_and_design/02_architecture/ownership_and_lifetimes.md",
        "architecture_and_design/05_engineering_drawings/README.md",
    )


def _read_page(relative_path: str) -> str:
    """
    Read one design page from the repository as text.

    Args:
        relative_path: Repository-relative page path from `_lifetime_page_relative_paths`.

    Returns:
        str: The page's full text, decoded as UTF-8.

    Raises:
        FileNotFoundError: If the page was moved or deleted. The test then errors instead
            of passing without having read a page.
    """
    repo_root = Path(__file__).resolve().parents[3]
    return (repo_root / relative_path).read_text(encoding="utf-8")


def _members_missing_from(page_text: str) -> List[str]:
    """
    Return the names of the `Existence` members a page does not name, in enum order.

    Contract:
        - A member counts as named when its code span (`` `<name>` ``) occurs in the page.
          The bare name would make the check vacuous for two members: `unique` occurs
          inside `unique_per_conduit`, and `many` is an ordinary English word.
        - Iterates the live enum, so a member added later is checked without editing
          this test.

    Args:
        page_text: The page's full text.

    Returns:
        List[str]: Names of the members absent from the page; empty when it names all.
    """
    return [member.name for member in Existence if f"`{member.name}`" not in page_text]


@pytest.mark.parametrize("relative_path", _lifetime_page_relative_paths())
def test_lifetime_page_names_every_existence_member(relative_path: str) -> None:
    """
    A lifetime design page names every `Existence` member, so none goes missing silently.

    Contract:
        Fails with the page path and the missing member names when the page lacks the
        code span of at least one member.

    Args:
        relative_path: Repository-relative path of the page under test.

    Returns:
        None.
    """
    missing = _members_missing_from(_read_page(relative_path))
    assert missing == [], (
        f"{relative_path} does not name Existence member(s) {missing}; "
        "describe each lifetime on the page (issue #255)."
    )
