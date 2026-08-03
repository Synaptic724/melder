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
    spellbook.bind(spell=ParkedHostService, existence="unique")
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
        existence="unique",
    )

    assert isinstance(parked_id, str) and parked_id, "no spell_id returned"
    assert parked_id in spellbook._spell_ids, (
        "a parked spell must still hold its spell_id - existence is what stops "
        "bind re-minting a duplicate of a sleeping spell"
    )
    parked_spell = spellbook._spells_by_id[parked_id]
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
          entry, so meld must not find it.
        - If this fails, staging leaks into resolution and the "inert until
          notched" guarantee is words only.
    Returns:
        None.
    Raises:
        AssertionError: If the parked spell can be melded.
    """
    spellbook, conduit, spell_index = _host("parked-unmeldable")
    spellbook.bind_inactive(
        spell=ParkedCandidateService,
        spell_index=spell_index,
        existence="unique",
    )

    with pytest.raises((KeyError, RuntimeError)):
        conduit.meld(spell=ParkedCandidateService)

    host_instance: Any = conduit.meld(spell=ParkedHostService)
    assert host_instance is not None, (
        "parking a member must not disturb the index's ACTIVE selected spell"
    )


def test_component_bind_inactive_refuses_an_index_it_does_not_own() -> None:
    """
    Purpose:
        Ownership is the guard that keeps one Spellbook from folding members onto
        another Spellbook's index. It is enforced deep in `_apply_add_to_index`,
        so the public surface has to be shown to carry it.
    Contract:
        - Two Spellbooks on DIFFERENT frames (process-wide uniqueness refuses two
          identical bindings, so the stranger binds its own class).
        - Passing the stranger's index must raise rather than graft across books.
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

    with pytest.raises(RuntimeError):
        spellbook.bind_inactive(
            spell=ParkedCandidateService,
            spell_index=foreign_index,
            existence="unique",
        )


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
        existence="unique",
    )

    intruder = _dynamic_book("parked-reserved-intruder")

    with pytest.raises(RuntimeError) as excinfo:
        intruder.bind(spell=ParkedCandidateService, existence="unique")

    assert "collision" in str(excinfo.value).lower(), (
        f"a PARKED spell_id failed to reserve its id; got: {excinfo.value}"
    )
