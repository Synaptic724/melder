from tests._frame_posture_test_support import (
    set_frame_rift_enabled_for_spellbook_configuration,
)
import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.spell_examiner.spell_examiner import SpellExaminer
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_examiner_inspection() -> None:
    """
    Purpose:
        Reset the Aether singleton for SpellExaminer inspection tests.
    Contract:
        - Rebinds Spellbook and Conduit to a fresh Aether instance.
        - Restores a fresh singleton after the test completes.
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


def _make_spellbook() -> Spellbook:
    """
    Purpose:
        Provide a Spellbook configured for component tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Spellbook: Configured Spellbook instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    set_frame_rift_enabled_for_spellbook_configuration(config, True)
    return spellbook


def _get_spell_by_version_id(spellbook: Spellbook, spell_id: str):
    """
    Purpose:
        Retrieve a local Spell by its version id.
    Contract:
        - Returns the first spell whose SpellIndex.current matches spell_id.
    Args:
        spellbook: Spellbook to search.
        spell_id: Version id to match.
    Returns:
        Spell or None: Matching spell instance or None if not found.
    """
    for spell in spellbook._spells.values():
        if spell.spell_index.current == spell_id:
            return spell
    return None


def test_component_spell_examiner_ai_profile_includes_class_profile() -> None:
    """
    Purpose:
        Validate AI profile includes class profile for class spells.
    Contract:
        - class_profile is populated for class spells.
        - callable_profile is also populated for class spells.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    ai_profile = None
    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        examiner = SpellExaminer()
        ai_profile = examiner.create_profile(spell, "detailed")

        assert ai_profile.class_profile is not None
        assert ai_profile.callable_profile is not None
        assert ai_profile.class_profile.name == "BasicService"
    finally:
        if ai_profile is not None:
            ai_profile.cleanup()
        spellbook.cleanup()


def test_component_spell_examiner_ai_profile_includes_callable_profile() -> None:
    """
    Purpose:
        Validate AI profile includes callable profile for function spells.
    Contract:
        - callable_profile is populated for function spells.
        - class_profile remains None for function spells.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    ai_profile = None

    def build_service() -> BasicService:
        """
        Purpose:
            Provide a function spell for callable inspection.
        Contract:
            - Returns a new BasicService instance.
        Returns:
            BasicService: Newly created BasicService instance.
        """
        return BasicService()

    try:
        spell_id = spellbook.bind(
            spell=build_service,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        examiner = SpellExaminer()
        ai_profile = examiner.create_profile(spell, "detailed")

        assert ai_profile.class_profile is None
        assert ai_profile.callable_profile is not None
        assert ai_profile.callable_profile.name == "build_service"
    finally:
        if ai_profile is not None:
            ai_profile.cleanup()
        spellbook.cleanup()


