import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.validation.validation_system import SpellValidationSystem
from melder.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_validation_system() -> None:
    """
    Purpose:
        Ensure component validation system tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
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
        Provide a Spellbook configured for validation system component tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Spellbook: A configured Spellbook instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def _get_spell_by_version_id(spellbook: Spellbook, spell_id: str) -> object | None:
    """
    Purpose:
        Resolve a local Spell instance by its versioned spell id.
    Contract:
        - Returns the first local spell whose SpellIndex.current matches `spell_id`.
        - Returns None if no matching spell is found.
    Args:
        spellbook: Spellbook holding locally bound spells.
        spell_id: Versioned spell id to locate.
    Returns:
        Spell | None: The resolved spell or None if missing.
    """
    for spell_index, spell in spellbook.spells.items():
        if spell_index.current == spell_id:
            return spell
    return None


def test_component_validation_system_reports_required_holes_and_missing_frame() -> None:
    """
    Purpose:
        Validate builtin validation strategies run against real spell artifacts.
    Contract:
        - Missing resolution frame yields MISSING_RESOLUTION_FRAME error.
        - Required holes yield REQUIRED_HOLE warning.
    Returns:
        None.
    Raises:
        AssertionError: If expected issues are missing or misclassified.
    """
    spellbook = _make_spellbook()
    system = SpellValidationSystem()

    class NeedsInput:
        """
        Purpose:
            Provide a spell with a required plain parameter.
        Contract:
            - Declares an unannotated required parameter.
        Args:
            value: Required plain parameter with no default.
        """

        def __init__(self, value: int) -> None:
            """
            Purpose:
                Capture the required value input.
            Contract:
                Stores the provided value for completeness.
            Args:
                value: Required input for the spell.
            Returns:
                None.
            """
            self.value = value

    try:
        spell_id = spellbook.bind(
            spell=NeedsInput,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        spell.run_phase_requirements()
        requirements = spell.requirements

        result = system.validate_spell(
            spell=spell,
            requirements=requirements,
            symbolic_graph=None,
            resolution_frame=None,
        )
        try:
            codes = {issue.code for issue in result.issues}
            assert codes == {"MISSING_RESOLUTION_FRAME", "REQUIRED_HOLE"}
            severity_by_code = {issue.code: issue.severity for issue in result.issues}
            assert severity_by_code["MISSING_RESOLUTION_FRAME"] == "error"
            assert severity_by_code["REQUIRED_HOLE"] == "warning"
        finally:
            result.cleanup()
    finally:
        system.cleanup()
        spellbook.cleanup()
