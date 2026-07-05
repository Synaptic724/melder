"""
Integration tests for the recorded-world loop against the REAL runtime:
Aether-hosted crystallizer, dynamic frame posture, real Spellbook bind and
conjure, and the removal seams firing from true teardown paths.

Runs only on 3.14t (melder package root import chain).
"""
import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus
from tests.mocks.spellbook.core_classes import BasicService
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


@pytest.fixture(autouse=True)
def reset_world_singletons():
    """
    Purpose:
        Isolate each test behind fresh Aether/Nexus/Crystallizer singletons.
    Contract:
        - Resets all four world singletons and rebinds the Spellbook and
          Conduit static Aether references before and after each test.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _activate_crystallizer():
    """
    Activate the Aether-hosted crystallizer with default knobs.

    Returns:
        Crystallizer: The live, activated singleton.
    """
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    return crystallizer


def _dynamic_book(finalize_configuration=True):
    """
    Build one dynamic-posture Spellbook.

    Args:
        finalize_configuration:
            When True, freeze the spellbook configuration BEFORE any bind
            (the recorded lane's configuration-discipline canon).

    Returns:
        Spellbook: The configured book on a dynamic frame posture.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    if finalize_configuration:
        configuration.finalize()
    return Spellbook(configuration=configuration)


def test_bind_while_activated_mints_custody_into_the_record():
    """
    Purpose:
        Verify the bind seam end to end on the real runtime.
    Contract:
        A dynamic-posture bind with the crystallizer activated creates a
        REAL SpellCrystal owned by the active profile, keyed by the
        spell's SHA identity and carrying the spellbook parent edge.
    Returns:
        None.
    Raises:
        AssertionError: If bind fails to mint or route custody.
    """
    crystallizer = _activate_crystallizer()
    book = _dynamic_book()
    spell_id = book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    crystal = crystallizer.get_spell_crystal(spell_id)
    assert crystal.id == spell_id
    assert crystal.spellbook_id == book._id
    assert crystallizer.describe_profile()["spell_crystal_count"] == 1


def test_bind_without_activation_records_nothing():
    """
    Purpose:
        Verify the R-A covenant AND the catch-up walk's documented reach.
    Contract:
        A bind with the crystallizer inactive records nothing; a LATER
        activation still records nothing for this world because the walk
        reaches spellbooks through frame-registered CONDUITS, and an
        unconjured book has none (setup canon: activate the crystallizer
        before building; the conjured-world case is covered by
        test_midflight_activation_catches_up_the_live_world).
    Returns:
        None.
    Raises:
        AssertionError: If an inactive bind leaks custody into the record.
    """
    book = _dynamic_book()
    book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    crystallizer = _activate_crystallizer()
    assert crystallizer.describe_profile()["spell_crystal_count"] == 0


def test_conjure_emits_conduit_and_frame_twins():
    """
    Purpose:
        Verify configuration-confirmation emissions on the real runtime.
    Contract:
        conjure(dynamic=True) freezes the dynamic frame posture (frame
        twin emits) and initializes the root conduit (conduit twin emits
        with the spellbook parent edge).
    Returns:
        None.
    Raises:
        AssertionError: If conjure-time twins fail to emit.
    """
    crystallizer = _activate_crystallizer()
    book = _dynamic_book()
    book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    book.conjure(dynamic=True, name="recorded-root")
    summary = crystallizer.describe_profile()
    assert summary["conduit_count"] == 1
    assert summary["frame_count"] == 1
    assert summary["spell_crystal_count"] == 1


def test_conjure_guard_refuses_preconfiguration_binds_in_recorded_lane():
    """
    Purpose:
        Verify the configuration-discipline guard on the real runtime.
    Contract:
        With the crystallizer activated, binds that ran while the
        spellbook configuration was still mutable make a dynamic conjure
        refuse with the teach-grade RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If the guard fails to trip.
    """
    _activate_crystallizer()
    book = _dynamic_book(finalize_configuration=False)
    book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    with pytest.raises(RuntimeError, match="configuration"):
        book.conjure(dynamic=True, name="guarded-root")


def test_cleanup_and_remove_spell_evicts_custody():
    """
    Purpose:
        Verify the true-removal seam on the real runtime.
    Contract:
        cleanup_and_remove_spell evicts the spell's custody from the
        record entirely (restore never rebuilds a shed spell).
    Returns:
        None.
    Raises:
        AssertionError: If custody survives true removal.
    """
    crystallizer = _activate_crystallizer()
    book = _dynamic_book()
    spell_id = book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    assert crystallizer.get_spell_crystal(spell_id).id == spell_id
    book.cleanup_and_remove_spell(spell_id)
    with pytest.raises(KeyError):
        crystallizer.get_spell_crystal(spell_id)
    assert crystallizer.describe_profile()["spell_crystal_count"] == 0


def test_conduit_teardown_sweeps_the_book_subtree():
    """
    Purpose:
        Verify book death through REAL root-conduit teardown.
    Contract:
        conduit.permanent_cleanup() reaches Spellbook.cleanup(), whose
        seam evicts the book subtree: conduit twin and all custody leave;
        the frame twin survives.
    Returns:
        None.
    Raises:
        AssertionError: If the subtree outlives its conduit.
    """
    crystallizer = _activate_crystallizer()
    book = _dynamic_book()
    book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = book.conjure(dynamic=True, name="doomed-root")
    assert crystallizer.describe_profile()["conduit_count"] == 1
    conduit.permanent_cleanup()
    summary = crystallizer.describe_profile()
    assert summary["conduit_count"] == 0
    assert summary["spell_crystal_count"] == 0
    assert summary["frame_count"] == 1


def test_midflight_activation_catches_up_the_live_world():
    """
    Purpose:
        Verify the activate catch-up walk against a real live world.
    Contract:
        A world built while the crystallizer is inactive is swept into
        the record at activation: every bound spell in dynamic-posture
        spellbooks gains custody.
    Returns:
        None.
    Raises:
        AssertionError: If the walk misses live custody.
    """
    book = _dynamic_book()
    spell_id = book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    book.conjure(dynamic=True, name="preexisting-root")
    crystallizer = _activate_crystallizer()
    crystal = crystallizer.get_spell_crystal(spell_id)
    assert crystal.id == spell_id
    assert crystal.spellbook_id == book._id
