import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.spell_examiner.spell_examiner import SpellExaminer
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_examiner_profiles() -> None:
    """
    Purpose:
        Reset the Aether singleton for SpellExaminer profile tests.
    Contract:
        - Rebinds Spellbook and Conduit to a fresh Aether instance.
        - Restores a clean singleton after each test.
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
        Provide a Spellbook configured for component profile tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Spellbook: Configured Spellbook instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    config.set_property("ai_profiles_enabled", True)
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


def test_component_spell_examiner_class_profile_records_method_signatures() -> None:
    """
    Purpose:
        Validate class profiles include method signature details.
    Contract:
        - Method profiles include the expected method name.
        - Signatures and parameter lists include the method arguments.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    ai_profile = None

    class Worker:
        """
        Purpose:
            Provide a class spell with a custom method for inspection.
        Contract:
            - Exposes a run method with a value parameter.
        """

        def run(self, value: int) -> str:
            """
            Purpose:
                Return a formatted value for inspection.
            Contract:
                - Returns a string including the input value.
            Args:
                value: Input value to format.
            Returns:
                str: Formatted output string.
            """
            return f"run:{value}"

    try:
        spell_id = spellbook.bind(
            spell=Worker,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        examiner = SpellExaminer(configuration=spellbook.get_configuration())
        ai_profile = examiner.ai_profile_for_spell(spell)

        class_profile = ai_profile.class_profile
        assert class_profile is not None
        assert "run" in class_profile.methods

        method_profile = class_profile.methods["run"]
        assert method_profile.signature is not None
        assert "value" in method_profile.signature
        param_names = {param["name"] for param in method_profile.parameters}
        assert "value" in param_names
    finally:
        if ai_profile is not None:
            ai_profile.cleanup()
        spellbook.cleanup()


def test_component_spell_examiner_callable_profile_records_parameters() -> None:
    """
    Purpose:
        Validate callable profiles capture parameter names and signatures.
    Contract:
        - Callable profiles include the expected parameter names.
        - Signatures include each declared argument.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    ai_profile = None

    def build_service(flag: bool, value: int = 1) -> BasicService:
        """
        Purpose:
            Provide a callable spell for inspection.
        Contract:
            - Returns a BasicService instance.
        Args:
            flag: Toggle used for signature verification.
            value: Value used for signature verification.
        Returns:
            BasicService: Newly created service instance.
        """
        return BasicService(marker=str(flag) + str(value))

    try:
        spell_id = spellbook.bind(
            spell=build_service,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        examiner = SpellExaminer(configuration=spellbook.get_configuration())
        ai_profile = examiner.ai_profile_for_spell(spell)

        callable_profile = ai_profile.callable_profile
        assert callable_profile is not None
        assert callable_profile.signature is not None
        assert "flag" in callable_profile.signature
        assert "value" in callable_profile.signature
        param_names = {param["name"] for param in callable_profile.parameters}
        assert {"flag", "value"} <= param_names
    finally:
        if ai_profile is not None:
            ai_profile.cleanup()
        spellbook.cleanup()
