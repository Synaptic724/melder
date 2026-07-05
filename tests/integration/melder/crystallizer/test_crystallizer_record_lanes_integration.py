"""
Integration tests for the two remaining record lanes: the conjure-first
spellbook-twin emission lane (configuration frozen AT conjure, with origins)
and catch-up-walk deduplication over shared spellbooks (lesser conduits).

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
        Isolate each test behind fresh world singletons.
    Contract:
        - Resets Aether/AetherUtilitySystem/Nexus/Crystallizer and rebinds
          the static Aether references before and after each test.
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


def _dynamic_configuration():
    """
    Build one dynamic-posture spellbook configuration (NOT frozen).

    Returns:
        SpellbookConfiguration: Mutable dynamic configuration.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def test_conjure_first_lane_emits_the_spellbook_twin():
    """
    Purpose:
        Verify the origin-carrying book-twin emission lane.
    Contract:
        With ZERO pre-conjure binds, an unfrozen configuration freezes AT
        conjure with origins (guard silent: nothing counted), so the
        spellbook twin emits; a post-conjure bind then mints custody into
        the recorded book.
    Returns:
        None.
    Raises:
        AssertionError: If the conjure-first lane misses the book twin.
    """
    crystallizer = _activate_crystallizer()
    book = Spellbook(configuration=_dynamic_configuration())
    book.conjure(dynamic=True, name="conjure-first-root")
    summary = crystallizer.describe_profile()
    assert summary["spellbook_count"] == 1
    assert summary["conduit_count"] == 1
    assert summary["frame_count"] == 1
    assert summary["spell_crystal_count"] == 0
    spell_id = book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    assert crystallizer.get_spell_crystal(spell_id).spellbook_id == book._id
    assert crystallizer.describe_profile()["spell_crystal_count"] == 1


def test_catch_up_walk_deduplicates_shared_spellbooks():
    """
    Purpose:
        Verify the walk's shared-book dedupe against real lesser conduits.
    Contract:
        A world with a root conduit AND a lesser conduit (sharing one
        spellbook) activated mid-flight records each bound spell EXACTLY
        once: the post-activation checkpoint captures one custody payload
        and exactly one journal entry (a double visit would journal two).
    Returns:
        None.
    Raises:
        AssertionError: If the shared book is swept more than once.
    """
    configuration = _dynamic_configuration()
    configuration.finalize()
    book = Spellbook(configuration=configuration)
    spell_id = book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    root = book.conjure(dynamic=True, name="dedupe-root")
    root.create_lesser_conduit()
    crystallizer = _activate_crystallizer()
    assert crystallizer.get_spell_crystal(spell_id).id == spell_id
    checkpoint_id = crystallizer.create_checkpoint()
    described = crystallizer.describe_checkpoint(checkpoint_id)
    assert described["captured_counts"].get("spell_crystal", 0) == 1
    assert described["journal_entry_count"] == 1
