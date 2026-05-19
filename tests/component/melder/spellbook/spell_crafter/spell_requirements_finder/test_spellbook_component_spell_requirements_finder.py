import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_crafter.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_crafter.spell_requirements_finder.spell_requirements_finder import (
    SpellRequirementsFinder,
)
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_requirements() -> None:
    """
    Purpose:
        Reset the Aether singleton for SpellRequirementsFinder component tests.
    Contract:
        - Rebinds Spellbook and Conduit to a fresh Aether instance.
        - Restores a new singleton after the test completes.
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


def test_component_requirements_finder_uses_current_spell_index() -> None:
    """
    Purpose:
        Validate requirements spell_id follows SpellIndex.current updates.
    Contract:
        - SpellRequirements uses the current version id, not the original id.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        new_version = "updated-version-id"
        spell.spell_index.update(new_version)

        requirements = SpellRequirementsFinder(spell).build_requirements()
        assert requirements.spell_id == new_version
        assert requirements.existence == spell.existence
        assert requirements.spellframe == spell.spellframe
    finally:
        spellbook.cleanup()


def test_component_requirements_finder_existing_creation_has_no_parameters() -> None:
    """
    Purpose:
        Validate existing-object spells yield empty requirements.
    Contract:
        - SpellRequirements has no parameters for existing creations.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    try:
        instance = BasicService(marker="existing")
        spell_id = spellbook.bind(
            spell=instance,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None
        assert spell.is_existing_creation is True

        requirements = SpellRequirementsFinder(spell).build_requirements()
        assert requirements.parameters == ()
    finally:
        spellbook.cleanup()


def test_component_requirements_finder_reads_function_signature() -> None:
    """
    Purpose:
        Validate requirements extraction for bound function spells.
    Contract:
        - DI parameters are classified as SINGLE_BY_ANNOTATION.
        - Plain parameters are classified as PLAIN.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    def make_service(service: BasicService, label: str = "default") -> BasicService:
        """
        Purpose:
            Provide a function spell for requirements inspection.
        Contract:
            - Returns the provided service instance.
        Args:
            service: Injected BasicService dependency.
            label: Plain parameter with a default.
        Returns:
            BasicService: The provided service instance.
        """
        _ = label
        return service

    try:
        spell_id = spellbook.bind(
            spell=make_service,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        requirements = SpellRequirementsFinder(spell).build_requirements()
        params_by_name = {param.name: param for param in requirements.parameters}

        service_param = params_by_name["service"]
        label_param = params_by_name["label"]

        assert service_param.di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION
        assert label_param.di_shape is ParameterDIShape.PLAIN
    finally:
        spellbook.cleanup()
