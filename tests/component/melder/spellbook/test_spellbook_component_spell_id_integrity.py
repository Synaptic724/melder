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

The negative control matters as much as the positive one: two frames binding the
same class MUST still both succeed, because per-frame isolation is a designed
feature, not an accident.
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


def test_component_conjure_allows_same_class_in_different_frames() -> None:
    """
    Purpose:
        NEGATIVE CONTROL. Per-frame isolation is a designed feature, so the same
        class bound in two different frames must still conjure in both.
    Contract:
        - Identical fingerprints, therefore identical spell_ids.
        - Different frames means different registries, so no collision.
        - If this fails, the integrity sweep is over-blocking and has broken
          multi-tenancy rather than fixed a hole.
    Returns:
        None.
    Raises:
        AssertionError: If either conjure is refused.
    """
    book_a = _book("integrity-frame-a")
    book_b = _book("integrity-frame-b")

    book_a.bind(spell=IntegrityTenantCache, existence="unique")
    book_b.bind(spell=IntegrityTenantCache, existence="unique")

    conduit_a = book_a.conjure(name="integrity-a")
    conduit_b = book_b.conjure(name="integrity-b")

    assert conduit_a is not None and conduit_b is not None
    assert conduit_a is not conduit_b

    cache_a: Any = conduit_a.meld(spell=IntegrityTenantCache)
    cache_b: Any = conduit_b.meld(spell=IntegrityTenantCache)
    assert cache_a is not cache_b, "per-frame isolation must still hold"


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
