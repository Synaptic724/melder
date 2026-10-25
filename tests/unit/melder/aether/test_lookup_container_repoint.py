"""
Unit tests: `LookupContainer.repoint` moves a binding-signature claim only from the spell it expects.

WHY THIS EXISTS. STORY-2026-10-17-notch_moves_signature_by_incoming_key_only. A notch moves its index's address claim
from the outgoing version to the incoming one, and must never take an address another index's active version holds.
`update` sets a claim unconditionally; `repoint` is the atomic compare-and-set the notch uses instead: it claims a free
address, moves one held by the expected spell, and refuses - changing nothing and naming the holder - one held by any
other spell.
"""

from melder.aether.aetheric_frame.lookup_container import LookupContainer


def test_repoint_claims_a_free_address() -> None:
    """
    Purpose:
        A free address is claimed for the incoming spell whatever spell was expected.

    Returns:
        None.
    """
    container = LookupContainer()
    key = ("greeter", "english")

    assert container.repoint(key, "sid-new", from_spell_id="sid-old") is None
    assert container.get(key) == "sid-new"
    assert container.get_sig_by_spell_id("sid-new") == key


def test_repoint_moves_an_address_from_the_expected_spell() -> None:
    """
    Purpose:
        An address held by the expected spell moves to the incoming one, the reverse map with it.

    Returns:
        None.
    """
    container = LookupContainer()
    key = ("greeter", "english")
    container.claim(key, "sid-old")

    assert container.repoint(key, "sid-new", from_spell_id="sid-old") is None
    assert container.get(key) == "sid-new"
    assert container.get_sig_by_spell_id("sid-old") is None
    assert container.get_sig_by_spell_id("sid-new") == key


def test_repoint_refuses_an_address_another_spell_holds_and_changes_nothing() -> None:
    """
    Purpose:
        An address held by a spell other than the expected one is refused: the holder is returned and both maps are
        left as they were.

    Returns:
        None.
    """
    container = LookupContainer()
    key = ("greeter", "english")
    container.claim(key, "sid-other")

    assert container.repoint(key, "sid-new", from_spell_id="sid-old") == "sid-other"
    assert container.repoint(key, "sid-new", from_spell_id=None) == "sid-other"
    assert container.get(key) == "sid-other"
    assert container.get_sig_by_spell_id("sid-other") == key
    assert container.get_sig_by_spell_id("sid-new") is None


def test_repoint_to_the_holder_itself_is_a_no_op() -> None:
    """
    Purpose:
        Repointing an address to the spell that already holds it succeeds and changes nothing.

    Returns:
        None.
    """
    container = LookupContainer()
    key = ("greeter", "english")
    container.claim(key, "sid-new")

    assert container.repoint(key, "sid-new", from_spell_id="sid-old") is None
    assert container.get(key) == "sid-new"
    assert container.get_sig_by_spell_id("sid-new") == key
