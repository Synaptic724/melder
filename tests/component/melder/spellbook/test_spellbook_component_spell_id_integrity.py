"""
Component test: `Spellbook._spell_id_integrity_checker` refuses a conjure whose
owned spell_ids are already registered in the aetheric frame.

WHY THIS EXISTS. `spell_id` is a SHA256 over the bind-time fingerprint and does
NOT include the frame, so two Spellbooks binding the same target with the same
bind parameters mint the SAME id. Uniqueness is a per-frame law, enforced at
bind through `Aether._check_for_spell`. But a Spellbook's owned-id set only
reaches the frame when its Conduit is constructed, so two books that both bind
BEFORE either conjures are invisible to each other and both bind-time checks
pass. That hole was reachable from the public API with four ordinary calls.

SCOPE, post owner-ruling 2026-08-02: uniqueness is PROCESS-WIDE. Two frames
binding the same class are BOTH refused - the fingerprint has no frame in it, so
a second frame was never an escape, it was only a blind spot. Per-frame
behaviour survives solely as an opt-out
(`process_wide_unique_spell_ids = False`), covered in
tests/component/melder/aether/test_aether_component_process_wide_spell_id_regime.py.
"""

from typing import Any

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook


class IntegrityTenantCache:
    """Bound identically by two Spellbooks to force a spell_id collision."""
    pass


class IntegrityOtherService:
    """A distinct class, so two books in one frame can coexist legitimately."""
    pass


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_spell_id_integrity() -> None:
    """
    Purpose:
        Give each test a clean Aether singleton and frame registry.
    Contract:
        - Resets before and after so frame state cannot leak between tests.
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
        Build a Spellbook bound to a named aetheric frame.
    Args:
        frame_name: The aetheric frame this Spellbook belongs to.
    Returns:
        Spellbook: A Spellbook configured for component tests.
    """
    spellbook = Spellbook(aetheric_frame=frame_name)
    spellbook.get_configuration().set_property(
        "phase_scheduler_workers_per_spellbook", 1
    )
    return spellbook


def test_component_conjure_refuses_duplicate_spell_id_in_same_frame() -> None:
    """
    Purpose:
        Prove the pre-conjure integrity sweep catches the cross-Spellbook
        collision that every bind-time check misses.
    Contract:
        - Both books bind BEFORE either conjures, which is the ordinary usage
          order and the exact window the bind-time check cannot see.
        - The FIRST conjure succeeds and publishes its ids into the frame.
        - The SECOND conjure is refused BEFORE its Conduit is constructed.
    Returns:
        None.
    Raises:
        AssertionError: If the second conjure is permitted.
    """
    book_a = _book("integrity-tenant")
    book_b = _book("integrity-tenant")

    book_a.bind(spell=IntegrityTenantCache, existence="unique")
    book_b.bind(spell=IntegrityTenantCache, existence="unique")

    conduit_a = book_a.conjure(name="integrity-conduit-a")
    assert conduit_a is not None, "the first conjure must succeed"

    with pytest.raises(RuntimeError) as excinfo:
        book_b.conjure(name="integrity-conduit-b")

    message = str(excinfo.value)
    assert "Conjure refused" in message, (
        f"refused for the wrong reason; got: {message}"
    )
    assert "integrity-tenant" in message, (
        "the refusal should name the frame the collision occurred in"
    )
    assert book_b._conduit is None, (
        "book_b must have NO conduit: the sweep runs before SpellbookCreationSystem, "
        "so a refusal must not leave a half-built conduit behind"
    )


def test_component_conjure_refuses_same_class_in_different_frames() -> None:
    """
    Purpose:
        THE REGIME ITSELF. A spell_id is unique per PROCESS, so the same class
        bound with the same parameters is refused in a SECOND frame just as it is
        in the same frame.

    Contract:
        - Identical fingerprints, therefore identical spell_ids. The frame is not
          in the fingerprint and never was.
        - The first conjure succeeds; the second is refused before its Conduit is
          built.
        - The refusal must NOT advise moving frames - under this regime that is
          not an escape, and saying so sends the caller in a circle.

    History:
        This was written as a NEGATIVE CONTROL asserting per-frame multi-tenancy
        survived the integrity sweep. Owner ruling 2026-08-02 then made
        uniqueness process-wide and deliberately retired that multi-tenancy, so
        the control was asserting the retired law - the same defect as the six
        frame-per-scope fixtures deleted under
        EPIC-2026-08-02-process-wide-spell-id-uniqueness. Inverted, not deleted:
        the cross-frame case is exactly what the regime exists to refuse.
        Per-frame behaviour with the flag OFF is covered by
        `test_component_regime_off_restores_per_frame_isolation`.

    Returns:
        None.
    Raises:
        AssertionError: If the second frame is allowed to conjure, or the refusal
            recommends a frame move.
    """
    book_a = _book("integrity-frame-a")
    book_b = _book("integrity-frame-b")

    book_a.bind(spell=IntegrityTenantCache, existence="unique")
    book_b.bind(spell=IntegrityTenantCache, existence="unique")

    conduit_a = book_a.conjure(name="integrity-a")
    assert conduit_a is not None, "the first conjure must succeed"

    with pytest.raises(RuntimeError) as excinfo:
        book_b.conjure(name="integrity-b")

    message = str(excinfo.value)
    assert "Conjure refused" in message, (
        f"refused for the wrong reason; got: {message}"
    )
    assert "conjure into a different aetheric frame" not in message.lower(), (
        "the refusal advises the one fix that cannot work here: the fingerprint "
        "has no frame in it, so another frame mints the same id and the caller "
        "is sent in a circle"
    )
    assert book_b._conduit is None, (
        "a refusal must not leave a half-built conduit behind"
    )


def test_component_a_parked_spell_still_reserves_its_spell_id() -> None:
    """
    Purpose:
        THE SLEEPING-SPELL GUARANTEE. A spell staged inactive by `bind_inactive`
        is unmeldable, but its spell_id is still ALLOCATED and must still block a
        duplicate.
    Contract:
        - `EPIC-2026-06-14` named this failure in advance: "a dormant candidate's
          spell_id is still allocated/taken... bind could re-mint a duplicate of
          a sleeping spell."
        - `bind_inactive` adds to `_spell_ids` (existence) while claiming NO
          binding signature, so only the existence aggregate can catch this - the
          LookupContainer never sees a parked spell.
    Returns:
        None.
    Raises:
        AssertionError: If a parked id can be re-minted by another Spellbook.
    """
    owner = _book("integrity-parked")
    owner.bind(spell=IntegrityTenantCache, existence="unique")
    conduit = owner.conjure(dynamic=True, name="integrity-parked-conduit")

    spell_index = next(iter(owner.spells.keys()))
    parked_id: str = conduit.bind_inactive(
        spell=IntegrityOtherService,
        spell_index=spell_index,
        existence="unique",
    )
    assert parked_id, "staging did not return a spell_id"

    # A SECOND book now binds the SAME staged class with the SAME parameters,
    # so it mints the identical fingerprint - which is parked, not active.
    # REFUSED AT BIND, not at conjure: the parked id is already published to the
    # frame by the owner's conjure above, so the bind-time check sees it. The
    # conjure preflight only catches the pre-conjure window where neither book
    # is visible to the other yet.
    intruder = _book("integrity-parked")

    with pytest.raises(RuntimeError) as excinfo:
        intruder.bind(spell=IntegrityOtherService, existence="unique")

    assert "collision" in str(excinfo.value).lower(), (
        "a PARKED spell_id failed to reserve its id. bind_inactive keeps "
        "existence in _spell_ids precisely so a sleeping spell cannot be "
        "duplicated; if this passes, the existence aggregate is active-only."
    )


def test_component_refusal_names_the_spell_not_just_a_sha() -> None:
    """
    Purpose:
        Prove the refusal is diagnosable. A bare SHA256 tells a caller nothing
        about WHICH binding collided.
    Contract:
        - `_describe_colliding_spells` resolves each colliding id back to the
          owned Spell and reports its name and binding signature.
        - It runs on the FAILURE PATH ONLY, so a healthy conjure pays nothing.
    Returns:
        None.
    Raises:
        AssertionError: If the message carries no human-readable identifier.
    """
    book_a = _book("integrity-message")
    book_b = _book("integrity-message")
    book_a.bind(spell=IntegrityTenantCache, existence="unique")
    book_b.bind(spell=IntegrityTenantCache, existence="unique")

    book_a.conjure(name="integrity-message-a")
    with pytest.raises(RuntimeError) as excinfo:
        book_b.conjure(name="integrity-message-b")

    message = str(excinfo.value)
    assert IntegrityTenantCache.__name__.lower() in message.lower(), (
        f"the refusal identifies no spell by name, only ids. Got:\n{message}"
    )
    assert "id=" in message, "the short id prefix should still be present"


def test_component_conjure_allows_distinct_classes_in_one_frame() -> None:
    """
    Purpose:
        NEGATIVE CONTROL. Two Spellbooks legitimately sharing one frame must
        still both conjure when their bindings do not collide.
    Contract:
        - Distinct classes produce distinct fingerprints and distinct ids.
        - This is the shape existing cluster/contract fixtures rely on; if it
          fails, the sweep is too strict and the 3224-green sweep was luck.
    Returns:
        None.
    Raises:
        AssertionError: If either conjure is refused.
    """
    book_a = _book("integrity-shared")
    book_b = _book("integrity-shared")

    book_a.bind(spell=IntegrityTenantCache, existence="unique")
    book_b.bind(spell=IntegrityOtherService, existence="unique")

    conduit_a = book_a.conjure(name="integrity-shared-a")
    conduit_b = book_b.conjure(name="integrity-shared-b")

    assert conduit_a is not None and conduit_b is not None
