"""Characterize existing address guards without changing or disabling validation.

Each test owns its books and roots. These diagnostic controls preserve the
current registration contract; they are not evidence that Fault A is repaired.
"""

import pytest

from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook


class First:
    """A bind target with a different name from Second."""

    def __init__(self) -> None:
        """Construct an inert object so lookup behavior is the only variable."""


class Second:
    """A distinct bind target used to attempt a conflicting registration."""

    def __init__(self) -> None:
        """Construct an inert object so lookup behavior is the only variable."""


def make_book(frame: str) -> Spellbook:
    """Create a dynamic book with caching disabled and frozen configuration.

    The caller owns cleanup. A unique frame isolates each diagnostic scenario.
    """
    configuration = SpellbookConfiguration(aether_frame=frame)
    configuration.with_defaults()
    book = Spellbook(aetheric_frame=frame, configuration=configuration)
    book.configure_aether_frame(
        system_state="dynamic",
        ai_native=False,
        rift_enabled=False,
        system_caching_enabled=False,
        disposal=None,
        disposal_method_names=None,
    )
    configuration.freeze()
    return book


@pytest.mark.parametrize("resolvable", [True, False])
def test_normalized_address_is_claimed_even_for_discoverable(resolvable: bool) -> None:
    """Different names and case variants cannot evade one-address ownership."""
    book = make_book(f"collision-guard-capability-{resolvable}")
    try:
        book.bind(
            spell=First, spellframe="REPOS", binding_name="PRIMARY",
            existence="many", resolvable=resolvable,
        )
        with pytest.raises(RuntimeError, match="Binding signature already active"):
            book.bind(spell=Second, spellframe="repos", binding_name="primary", existence="many")
    finally:
        book.cleanup()


def test_separate_books_in_one_frame_cannot_claim_one_address() -> None:
    """Frame-wide admission rejects the second book before any contract exists."""
    owner = make_book("collision-guard-shared-frame")
    borrower = Spellbook(
        aetheric_frame="collision-guard-shared-frame",
        configuration=owner.get_configuration(),
    )
    try:
        owner.bind(spell=First, spellframe="repos", binding_name="main", existence="many")
        with pytest.raises(RuntimeError, match="Binding signature already active"):
            borrower.bind(spell=Second, spellframe="repos", binding_name="main", existence="many")
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_different_aetheric_frames_cannot_be_linked() -> None:
    """A shared address in independent worlds cannot enter one pool by public link."""
    owner_book = make_book("collision-guard-world-one")
    borrower_book = make_book("collision-guard-world-two")
    owner = None
    borrower = None
    try:
        owner_book.bind(spell=First, spellframe="repos", binding_name="main", existence="many")
        borrower_book.bind(spell=Second, spellframe="repos", binding_name="main", existence="many")
        owner = owner_book.conjure(name="owner", dynamic=True)
        borrower = borrower_book.conjure(name="borrower", dynamic=True)
        with pytest.raises(RuntimeError, match="Cannot link conduits across different AethericFrames"):
            owner.link(borrower)
    finally:
        if borrower is not None:
            borrower.cleanup()
        if owner is not None:
            owner.cleanup()
        borrower_book.cleanup()
        owner_book.cleanup()
