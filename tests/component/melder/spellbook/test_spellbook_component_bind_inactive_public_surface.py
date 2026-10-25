"""
Component tests for `Spellbook.bind_inactive` at its PUBLIC surface.

WHY THIS EXISTS. `bind_inactive` was `_bind_inactive` - internal, reached only
through `Conduit.bind_inactive` and the crystallizer graft runner. It was made
public under EPIC-2026-08-02-process-wide-spell-id-uniqueness because the
integrity work needed to describe parked spells as first-class holders of a
spell_id. A method that changes from internal to public gains callers who never
read its body, so its refusals have to be tested at the surface, not inferred
from the surface that used to wrap it.

The parked spell is the interesting case for this epic: it is UNMELDABLE but its
spell_id is ALLOCATED. Both halves are asserted here - a parked spell that could
be melded would be a resolution leak, and a parked spell that did not hold its id
would let `bind` re-mint a duplicate of a sleeping spell, which is the failure
`EPIC-2026-06-14` named in advance.

Every version of an index is bound the way its first version was (2026-10-25,
STORY-2026-10-17-notch_moves_signature_by_incoming_key_only): the host is bound
under the string spellframe 'parked', and the candidate is staged under it too,
so the two share the index's address and only the active one is served there.

Validation: Not run.
"""

from typing import Any

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook


class ParkedHostService:
    """Bound active first; its index is the one parked spells are folded onto."""
    pass


class ParkedCandidateService:
    """Staged inactive by `bind_inactive`."""
    pass


class ParkedStrangerService:
    """Bound by a DIFFERENT Spellbook, to produce a foreign index."""
    pass


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_bind_inactive() -> None:
    """
    Purpose:
        Give each test a clean Aether singleton and frame registry.
    Contract:
        - Resets before and after, so frame state cannot leak between tests.
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


def _dynamic_book(frame_name: str) -> Spellbook:
    """
    Purpose:
        Build a Spellbook on a named frame, sized for component tests.
    Args:
        frame_name: The aetheric frame this Spellbook belongs to.
    Returns:
        Spellbook: A Spellbook ready to bind and conjure dynamically.
    """
    spellbook = Spellbook(aetheric_frame=frame_name)
    spellbook.get_configuration().set_property(
        "phase_scheduler_workers_per_spellbook", 1
    )
    return spellbook


def _host(frame_name: str) -> Any:
    """
    Purpose:
        Bind one active spell and conjure dynamically, returning the pieces a
        `bind_inactive` call needs.
    Args:
        frame_name: The aetheric frame to build on.
    Returns:
        Any: `(spellbook, conduit, spell_index)` - the index is the owned target
            an inactive member is folded onto.
    """
    spellbook = _dynamic_book(frame_name)
    spellbook.bind(spell=ParkedHostService, spellframe="parked", existence="unique")
    conduit = spellbook.conjure(dynamic=True, name=f"{frame_name}-root")
    spell_index = next(iter(spellbook.spells.keys()))
    return spellbook, conduit, spell_index


def test_component_bind_inactive_returns_an_id_and_does_not_activate() -> None:
    """
    Purpose:
        The public surface's basic contract: it returns a real spell_id and the
        spell it created is NOT active.
    Contract:
        - The returned id is a non-empty string distinct from the host's.
        - Existence is recorded (`_spell_ids`) while activity is not.
    Returns:
        None.
    Raises:
        AssertionError: If no id comes back, or the parked spell reads active.
    """
    spellbook, _conduit, spell_index = _host("parked-basic")

    parked_id: str = spellbook.bind_inactive(
        spell=ParkedCandidateService,
        spell_index=spell_index,
        spellframe="parked",
        existence="unique",
    )

    assert isinstance(parked_id, str) and parked_id, "no spell_id returned"
    assert parked_id in spellbook._spell_ids, (
        "a parked spell must still hold its spell_id - existence is what stops "
        "bind re-minting a duplicate of a sleeping spell"
    )
    # PARKED AND ACTIVE ARE SEPARATE MAPS. `bind_inactive` writes the spell to
    # `_inactive_spells` and keeps only its id in `_spell_ids`; `_spells_by_id`
    # is the ACTIVE map that `meld` resolves through. Reading the parked spell
    # out of the active map asserted the opposite of the contract - a parked
    # spell appearing there would BE the defect.
    assert parked_id not in spellbook._spells_by_id, (
        "a parked spell must not appear in the active map - that map is the "
        "resolution surface and parking is precisely staying off it"
    )
    parked_spell = spellbook._inactive_spells[parked_id]
    assert parked_spell._active is False, (
        "bind_inactive must park, not activate"
    )


def test_component_a_parked_spell_is_not_meldable() -> None:
    """
    Purpose:
        THE OTHER HALF OF THE CONTRACT. A parked spell holds an id but must stay
        off the resolution surface until `notch` promotes it.
    Contract:
        - `bind_inactive` claims no binding signature and writes no active map
          entry, so a meld by its spell_id must not find it, and a meld at the
          address it shares with the host builds the host.
        - If this fails, staging leaks into resolution and the "inert until
          notched" guarantee is words only.
    Returns:
        None.
    Raises:
        AssertionError: If the parked spell can be melded.
    """
    spellbook, conduit, spell_index = _host("parked-unmeldable")
    parked_id = spellbook.bind_inactive(
        spell=ParkedCandidateService,
        spell_index=spell_index,
        spellframe="parked",
        existence="unique",
    )

    with pytest.raises(KeyError):
        conduit.meld(spell=parked_id)

    host_instance: Any = conduit.meld(spellframe="parked")
    assert isinstance(host_instance, ParkedHostService), (
        "parking a member must not disturb the index's ACTIVE selected spell"
    )


def test_component_bind_inactive_refuses_an_index_it_does_not_own() -> None:
    """
    Purpose:
        Ownership is the guard that keeps one Spellbook from folding members onto
        another Spellbook's index. `bind_inactive` checks it before anything is
        registered (2026-10-25; until then only `_apply_add_to_index` enforced it,
        after the registration), so the public surface has to be shown to carry it.
    Contract:
        - Two Spellbooks on DIFFERENT frames (process-wide uniqueness refuses two
          identical bindings, so the stranger binds its own class).
        - Passing the stranger's index must raise rather than graft across books,
          and must leave nothing of the candidate registered.
    Returns:
        None.
    Raises:
        AssertionError: If a foreign index is accepted.
    """
    spellbook, _conduit, _own_index = _host("parked-owner")

    stranger = _dynamic_book("parked-stranger")
    stranger.bind(spell=ParkedStrangerService, existence="unique")
    stranger.conjure(dynamic=True, name="parked-stranger-root")
    foreign_index = next(iter(stranger.spells.keys()))

    with pytest.raises(RuntimeError, match="not owned by this spellbook"):
        spellbook.bind_inactive(
            spell=ParkedCandidateService,
            spell_index=foreign_index,
            spellframe="parked",
            existence="unique",
        )

    assert not any(
        parked.spell is ParkedCandidateService for parked in spellbook._inactive_spells.values()
    ), "a refused staging must leave nothing registered"


def test_component_a_parked_id_blocks_a_duplicate_bind() -> None:
    """
    Purpose:
        Tie the public surface back to the epic: the id a parked spell holds is
        enforced, not merely recorded.
    Contract:
        - A second Spellbook binding the SAME class with the SAME parameters mints
          the identical fingerprint and must be refused, even though the spell it
          collides with is asleep and unmeldable.
    Returns:
        None.
    Raises:
        AssertionError: If a parked id can be re-minted.
    """
    spellbook, _conduit, spell_index = _host("parked-reserved")
    spellbook.bind_inactive(
        spell=ParkedCandidateService,
        spell_index=spell_index,
        spellframe="parked",
        existence="unique",
    )

    intruder = _dynamic_book("parked-reserved-intruder")

    with pytest.raises(RuntimeError) as excinfo:
        intruder.bind(spell=ParkedCandidateService, existence="unique")

    assert "collision" in str(excinfo.value).lower(), (
        f"a PARKED spell_id failed to reserve its id; got: {excinfo.value}"
    )
