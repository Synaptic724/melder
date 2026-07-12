import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.mutation_research.mutation_research import MutationResearch
from tests._frame_posture_test_support import (
    configure_frame_posture_for_spellbook_configuration,
)


@pytest.fixture(autouse=True)
def reset_world_for_accessor_door_tests() -> None:
    """
    Reset the Aether and MutationResearch singletons around each test.

    Purpose:
        The accessor-door contract is about identity through REAL wiring
        (Aether -> Spellbook -> Conduit), so each test builds a fresh world
        and tears it down for isolation.

    Contract:
        - Resets the Aether singleton before and after each test.
        - Rebinds the class-level `Spellbook._aether` / `Conduit._aether`
          references to the fresh instance (component-test precedent).
        - Resets the MutationResearch singleton so lazy-build assertions
          observe first-touch construction.

    Returns:
        None.
    """
    MutationResearch._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    MutationResearch._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_spellbook(*, dynamic: bool = False) -> Spellbook:
    """
    Build one minimally configured Spellbook for door tests.

    Args:
        dynamic:
            When True, configure the book for dynamic mode so lesser
            conduits and upgrades are legal.

    Returns:
        Spellbook: Configured book (not yet conjured).
    """
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(
        configuration,
        dynamic=dynamic,
    )
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=configuration)


def test_spellbook_door_returns_the_aether_hosted_world_root() -> None:
    """
    The spellbook door hands back the exact Aether-hosted root object:
    world-scoped, one identity, no book-scoped view.
    """
    spellbook = _make_spellbook()
    try:
        assert spellbook.mutation_research is Spellbook._aether.mutation_research
    finally:
        spellbook.cleanup()


def test_conduit_door_shares_the_spellbook_binding() -> None:
    """
    The conduit door returns the same object the owning spellbook bound:
    one world root through every door.
    """
    spellbook = _make_spellbook()
    conduit = spellbook.conjure(name="root")
    try:
        assert conduit.mutation_research is spellbook.mutation_research
        assert conduit.mutation_research is Spellbook._aether.mutation_research
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_lesser_conduit_shares_the_same_world_root() -> None:
    """
    Lesser conduits inherit the binding through the shared spellbook -
    no per-conduit research scope exists.
    """
    spellbook = _make_spellbook(dynamic=True)
    root = spellbook.conjure(dynamic=True, name="root")
    lesser = root.create_lesser_conduit()
    try:
        assert lesser.mutation_research is root.mutation_research
    finally:
        root.cleanup()
        spellbook.cleanup()


def test_binding_never_activates_the_root() -> None:
    """
    Eager init binding builds the root object only; it must arrive
    unconfigured and inactive, so recording stays impossible until the
    user explicitly activates research (R1 disclosure contract).
    """
    spellbook = _make_spellbook()
    try:
        root = spellbook.mutation_research
        assert root.activated is False
    finally:
        spellbook.cleanup()


def test_spellbook_door_raises_after_cleanup() -> None:
    """
    Post-cleanup access refuses through check_cleaned - the borrowed
    reference is deleted, never served stale.
    """
    spellbook = _make_spellbook()
    spellbook.cleanup()
    with pytest.raises(RuntimeError):
        _ = spellbook.mutation_research


def test_conduit_door_raises_after_cleanup() -> None:
    """
    Post-cleanup conduit access refuses the same way the spellbook door
    does; the conduit never outlives its borrowed reference.
    """
    spellbook = _make_spellbook()
    conduit = spellbook.conjure(name="root")
    conduit.cleanup()
    try:
        with pytest.raises(RuntimeError):
            _ = conduit.mutation_research
    finally:
        spellbook.cleanup()


def test_cleaned_root_under_live_aether_fail_fasts_spellbook_construction() -> None:
    """
    R2 regression guard: a cleaned MR root with a live Aether makes the
    NEXT Spellbook() raise RuntimeError at construction, because
    `Aether.mutation_research` never silently re-creates a cleaned root.
    """
    first = _make_spellbook()
    root = first.mutation_research
    first.cleanup()
    root.cleanup()
    with pytest.raises(RuntimeError):
        _make_spellbook()
