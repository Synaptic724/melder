"""
Component test: does the frame's `_selected_spell_registry` hold EXISTENCE
(active + parked owned ids) or only ACTIVE ids?

The question exists because the field name says "selected", which reads as
"active", while the set it aliases (`Spellbook._spell_ids`) is commented "ALL
owned ids". Reading the source settles it on paper; this settles it at runtime.

The two frame surfaces are asserted AGAINST EACH OTHER on purpose. If both
answer the same way for a parked spell, the model in the ticket is wrong and
these tests are what says so:

    frame.has_spell(id)            -> reads `_selected_spell_registry`
    frame.has_lookup_spell_id(id)  -> reads `LookupContainer._reverse`

Expected (the claim under test):
    parked id -> has_spell True, has_lookup_spell_id False
"""

from typing import Any, Optional, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook


class RegistryScopeServiceA:
    """First bound service; becomes the initially ACTIVE member of the index."""
    pass


class RegistryScopeServiceB:
    """Second service; staged INACTIVE onto ServiceA's index via bind_inactive."""
    pass


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_registry_scope() -> None:
    """
    Purpose:
        Ensure each test starts and ends with a clean Aether singleton.
    Contract:
        - Resets the singleton before the test and rebinds Spellbook/Conduit.
        - Resets again afterwards so frame state cannot leak between tests.
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


def _index_for(spellbook: Spellbook, target_type: type) -> Any:
    """
    Purpose:
        Resolve the SpellIndex a bound type currently occupies.
    Contract:
        - Reads the public `spells` mapping rather than relying on bind's
          return shape, which differs between direct and decorator call styles.
    Args:
        spellbook: The Spellbook holding the binding.
        target_type: The bound class to locate.
    Returns:
        Any: The owning SpellIndex.
    Raises:
        AssertionError: If the type is not bound in this Spellbook.
    """
    for spell_index, spell in spellbook.spells.items():
        if getattr(spell, "spell", None) is target_type:
            return spell_index
        if getattr(spell, "spell_name", None) == target_type.__name__:
            return spell_index
    raise AssertionError(f"{target_type.__name__} is not bound in this Spellbook")


def _stage_parked_spell() -> Tuple[Any, Any, str, Any, Spellbook]:
    """
    Purpose:
        Build a dynamic world with one ACTIVE spell and one PARKED spell on the
        same index, which is the minimum shape that distinguishes the two
        registries.
    Contract:
        - Binds ServiceA active, conjures dynamic (so the frame holds the
          live id-set reference), then stages ServiceB inactive onto A's index.
        - Performs no notch; ServiceB stays parked.
    Returns:
        Tuple[Any, Any, str, Any, Spellbook]:
            (frame, conduit, parked_spell_id, spell_index, spellbook)
    """
    book = Spellbook()
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)

    book.bind(spell=RegistryScopeServiceA, existence="unique")
    conduit = book.conjure(dynamic=True, name="registry-scope-conduit")

    spell_index = _index_for(book, RegistryScopeServiceA)
    parked_spell_id: str = conduit.bind_inactive(
        spell=RegistryScopeServiceB,
        spell_index=spell_index,
        existence="unique",
    )

    frame = book._aetheric_frame
    return frame, conduit, parked_spell_id, spell_index, book


def _parked_spell_object(spellbook: Spellbook, parked_spell_id: str) -> Any:
    """
    Purpose:
        Resolve the parked Spell OBJECT for a staged spell_id.
    Contract:
        - `notch_spell` requires the Spell instance, not the bound class: it
          reads `spell.spell_id` and `spell._key` off the argument.
        - `bind_inactive` returns only the id, so the object is recovered from
          the Spellbook's inactive map (`spell_id -> parked Spell`).
    Args:
        spellbook: The Spellbook that staged the spell.
        parked_spell_id: The id returned by `bind_inactive`.
    Returns:
        Any: The parked Spell instance.
    Raises:
        AssertionError: If the id is not parked in `_inactive_spells`.
    """
    parked = spellbook._inactive_spells.get(parked_spell_id)
    assert parked is not None, (
        f"spell_id {parked_spell_id} is not parked in _inactive_spells; "
        "bind_inactive did not stage it where the notch path expects it"
    )
    return parked


def test_component_frame_registry_holds_parked_spell_id() -> None:
    """
    Purpose:
        Prove whether the frame's selected-spell registry tracks EXISTENCE or
        only ACTIVITY, by asking it about a spell that is owned but parked.
    Contract:
        - `bind_inactive` adds to `_spell_ids` and claims NO binding signature.
        - Therefore, if the registry is existence-scoped, the parked id is
          visible to `has_spell` and invisible to `has_lookup_spell_id`.
    Returns:
        None.
    Raises:
        AssertionError: If either surface disagrees with the claim under test.
    """
    frame, _conduit, parked_spell_id, _index, _book = _stage_parked_spell()

    in_existence_registry: bool = frame.has_spell(parked_spell_id)
    holds_active_signature: bool = frame.has_lookup_spell_id(parked_spell_id)

    print(
        f"\nparked spell_id={parked_spell_id}\n"
        f"  frame.has_spell(...)           = {in_existence_registry}\n"
        f"  frame.has_lookup_spell_id(...) = {holds_active_signature}"
    )

    assert in_existence_registry is True, (
        "REGISTRY IS ACTIVITY-SCOPED, NOT EXISTENCE-SCOPED. A parked (inactive) "
        "owned spell_id was NOT visible via frame.has_spell(...), so "
        "_selected_spell_registry tracks only active spells and the analysis in "
        "TASK-2026-08-02 is wrong."
    )
    assert holds_active_signature is False, (
        "A parked spell holds an active binding signature. bind_inactive claims "
        "no signature by contract, so the LookupContainer should not know it."
    )


def test_component_frame_registry_retains_outgoing_id_after_notch() -> None:
    """
    Purpose:
        Prove that DEACTIVATION does not remove an id from the frame's
        existence view - the second half of the same claim.
    Contract:
        - `_apply_notch` parks the outgoing spell off the active maps while
          keeping its id in `_spell_ids`.
        - So after a notch, BOTH the promoted and the demoted ids remain
          visible to `has_spell`, while only the promoted one holds the
          binding signature.
    Returns:
        None.
    Raises:
        AssertionError: If the demoted id disappears from the existence view.
    """
    frame, conduit, parked_spell_id, spell_index, book = _stage_parked_spell()

    outgoing_spell_id: Optional[str] = spell_index.selected_spell_id
    assert outgoing_spell_id is not None, "index had no selected member to demote"
    assert outgoing_spell_id != parked_spell_id, "staging did not produce two members"

    conduit.notch_spell(
        spell_index=spell_index,
        spell=_parked_spell_object(book, parked_spell_id),
    )

    demoted_still_exists: bool = frame.has_spell(outgoing_spell_id)
    promoted_exists: bool = frame.has_spell(parked_spell_id)
    demoted_holds_signature: bool = frame.has_lookup_spell_id(outgoing_spell_id)
    promoted_holds_signature: bool = frame.has_lookup_spell_id(parked_spell_id)

    # MECHANISM PROBE. If the two index members carry DIFFERENT binding keys,
    # then `_apply_notch`'s `update_lookup(spell._key, new_id)` looks up a key
    # that was never claimed, finds no previous holder to evict, and ADDS a
    # second live signature instead of repointing the existing one.
    demoted_spell = book._spells_by_id.get(outgoing_spell_id) or book._inactive_spells.get(
        outgoing_spell_id
    )
    promoted_spell = book._spells_by_id.get(parked_spell_id) or book._inactive_spells.get(
        parked_spell_id
    )
    demoted_key = getattr(demoted_spell, "_key", None)
    promoted_key = getattr(promoted_spell, "_key", None)
    container = frame._lookup_container

    print(
        f"\nafter notch:\n"
        f"  demoted  {outgoing_spell_id[:16]}...  has_spell={demoted_still_exists}  "
        f"signature={demoted_holds_signature}\n"
        f"  promoted {parked_spell_id[:16]}...  has_spell={promoted_exists}  "
        f"signature={promoted_holds_signature}\n"
        f"\nMECHANISM:\n"
        f"  demoted  _key = {demoted_key}\n"
        f"  promoted _key = {promoted_key}\n"
        f"  keys are {'THE SAME' if demoted_key == promoted_key else 'DIFFERENT'}"
        f"  -> update() {'evicts' if demoted_key == promoted_key else 'CANNOT evict'} the old holder\n"
        f"  LookupContainer forward entries = {len(container._lookup)} "
        f"(1 = repointed, 2 = LEAKED)\n"
        f"  forward map = {container._lookup}\n"
        f"  reverse map = {container._reverse}"
    )

    assert demoted_still_exists is True, (
        "DEACTIVATION REMOVED THE ID FROM THE FRAME'S VIEW. _deactivate_owned_spell "
        "claims it 'leaves _spell_ids untouched: existence is kept across the "
        "deactivation'. If this fails, that contract is not what the code does."
    )
    assert promoted_exists is True, "the promoted member vanished from the frame view"
    assert promoted_holds_signature is True, (
        "notch repoints the framewide signature to the promoted id; it does not hold it"
    )
    assert demoted_holds_signature is False, (
        "the demoted id still holds an active binding signature after being parked"
    )
