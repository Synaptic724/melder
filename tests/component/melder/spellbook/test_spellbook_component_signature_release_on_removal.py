"""
Component regression: `cleanup_and_remove_spell` must release the FRAMEWIDE
binding-signature claim, not only the Spellbook's local lookup map.

THE DEFECT THIS GUARDS. `cleanup_and_remove_spell` popped
`Spellbook._lookup_spells` (local) but never called the frame, so the frame's
`LookupContainer` kept mapping `(frame_key, bind_key)` to the destroyed spell_id
forever. `LookupContainer.claim` raises when a signature is held by a DIFFERENT
spell_id, so the next bind under that signature was refused by a spell that no
longer existed in the process. `lookup_container.py:18-20` requires the release:
"a spellbook cleaning up must release its keys".

The leak was GUARANTEED, not intermittent: `cleanup_and_remove_spell` resolves
its target from `_spells_by_id` and raises if absent, so it only ever destroys
ACTIVE spells - and an active spell always holds its signature.

No conjure here on purpose. `claim_lookup` runs at BIND, so the signature exists
before any Conduit does, and the defect is reachable without one.
"""

from typing import Any

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook


class ISignatureFrame:
    """Shared spellframe: forces both services onto ONE binding signature."""
    pass


class SignatureServiceA:
    """First implementation; destroyed mid-test."""
    pass


class SignatureServiceB:
    """Second implementation; must be bindable after A is destroyed."""
    pass


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_signature_release() -> None:
    """
    Purpose:
        Give each test a clean Aether singleton and frame registry.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _book(frame_name: str) -> Spellbook:
    """
    Purpose:
        Build a Spellbook on a named frame for component use.
    Args:
        frame_name: The aetheric frame to bind into.
    Returns:
        Spellbook: A configured Spellbook.
    """
    spellbook = Spellbook(aetheric_frame=frame_name)
    spellbook.get_configuration().set_property(
        "phase_scheduler_workers_per_spellbook", 1
    )
    return spellbook


def test_component_removing_a_spell_releases_its_framewide_signature() -> None:
    """
    Purpose:
        Prove the destroyed spell no longer holds a binding signature in the
        frame.
    Contract:
        - `has_lookup_spell_id` reads `LookupContainer._reverse`, which is the
          ACTIVE-signature index - the exact structure that leaked.
        - A True result after removal means the frame still believes a destroyed
          spell is the active holder of that signature.
    Returns:
        None.
    Raises:
        AssertionError: If the signature survives its spell.
    """
    book = _book("signature-release")
    book.bind(
        spell=SignatureServiceA,
        spellframe=ISignatureFrame,
        existence="unique",
    )
    spell_a_id: str = next(iter(book._spells_by_id))
    frame = book._aetheric_frame

    assert frame.has_lookup_spell_id(spell_a_id) is True, (
        "precondition failed: an active bind must claim a framewide signature"
    )

    book.cleanup_and_remove_spell(spell_a_id)

    assert frame.has_lookup_spell_id(spell_a_id) is False, (
        "SIGNATURE LEAKED. cleanup_and_remove_spell destroyed the spell but the "
        "frame's LookupContainer still maps its signature to the dead spell_id. "
        "It pops the Spellbook's LOCAL _lookup_spells map only; the framewide "
        "release must go through the frame."
    )
    assert frame.get_lookup_sig_by_spell_id(spell_a_id) is None, (
        "the reverse index still resolves a signature for a destroyed spell"
    )


def test_component_signature_is_rebindable_after_its_spell_is_removed() -> None:
    """
    Purpose:
        Prove the user-visible consequence is gone: a different implementation
        can take the signature once the previous holder is destroyed.
    Contract:
        - Both services share `spellframe=ISignatureFrame`, so they compete for
          one `(frame_key, bind_key)` signature.
        - Before the fix this raised from `LookupContainer.claim`, naming a
          spell_id no longer present in the process.
    Returns:
        None.
    Raises:
        AssertionError: If the rebind is refused.
    """
    book = _book("signature-rebind")
    book.bind(
        spell=SignatureServiceA,
        spellframe=ISignatureFrame,
        existence="unique",
    )
    spell_a_id: str = next(iter(book._spells_by_id))

    book.cleanup_and_remove_spell(spell_a_id)

    # The whole point: this must not raise.
    book.bind(
        spell=SignatureServiceB,
        spellframe=ISignatureFrame,
        existence="unique",
    )

    live_ids = set(book._spells_by_id)
    assert spell_a_id not in live_ids, "the destroyed spell is still active"
    assert len(live_ids) == 1, (
        f"expected exactly one live spell after remove-then-rebind, got {len(live_ids)}"
    )

    frame = book._aetheric_frame
    new_spell_id: str = next(iter(live_ids))
    assert frame.has_lookup_spell_id(new_spell_id) is True, (
        "the replacement spell did not take the signature its predecessor freed"
    )


def test_component_full_spellbook_cleanup_releases_signatures() -> None:
    """
    Purpose:
        Guard the sibling path, which was already correct, so a future
        refactor cannot quietly drop it while fixing the single-spell one.
    Contract:
        - `_cleanup_components` iterates `_lookup_spells` and releases each key
          framewide (`spellbook.py:448-452`).
    Returns:
        None.
    Raises:
        AssertionError: If a signature survives full Spellbook teardown.
    """
    book = _book("signature-full-cleanup")
    book.bind(
        spell=SignatureServiceA,
        spellframe=ISignatureFrame,
        existence="unique",
    )
    spell_a_id: str = next(iter(book._spells_by_id))
    frame: Any = book._aetheric_frame

    assert frame.has_lookup_spell_id(spell_a_id) is True

    book.cleanup()

    assert frame.has_lookup_spell_id(spell_a_id) is False, (
        "full Spellbook cleanup left a framewide signature claimed"
    )
