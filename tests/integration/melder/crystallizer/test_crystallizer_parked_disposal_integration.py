"""
Integration test for the parked-lane disposal seam: cleanup_spell on an
INACTIVE (staged) member evicts its custody from the record while the active
member's custody survives untouched.

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


class _ParkedService:
    """File-backed staged-spell target for parked-disposal tests."""

    def __init__(self):
        self.tag = "parked"


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


def test_cleanup_spell_on_a_parked_member_evicts_its_custody():
    """
    Purpose:
        Verify the parked-lane disposal seam on the real runtime.
    Contract:
        Disposing a staged (inactive) member via cleanup_spell evicts its
        custody from the record's inactive location (restore never
        rebuilds a shed spell) while the active member's custody and the
        shared index survive untouched.
    Returns:
        None.
    Raises:
        AssertionError: If parked custody survives disposal.
    """
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    book_configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(book_configuration)
    book_configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    book_configuration.finalize()
    book = Spellbook(configuration=book_configuration)
    active_id = book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = book.conjure(dynamic=True, name="parked-disposal-root")
    active_spell = book._spells_by_id[active_id]
    staged_id = conduit.bind_inactive(
        spell=_ParkedService,
        spell_index=active_spell.spell_index,
        existence=Existence.unique,
        permissions="create",
    )
    assert crystallizer.get_spell_crystal(staged_id).id == staged_id
    staged_spell = book._inactive_spells[staged_id]
    book.cleanup_spell(spell=staged_spell)
    with pytest.raises(KeyError):
        crystallizer.get_spell_crystal(staged_id)
    summary = crystallizer.describe_profile()
    assert summary["inactive_spell_crystal_count"] == 0
    assert summary["spell_crystal_count"] == 1
    assert crystallizer.get_spell_crystal(active_id).id == active_id
