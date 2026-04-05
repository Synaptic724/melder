import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.spell_examiner.profiles.binding_profile import (
    ClassBindingProfile,
    SpellBindingKind,
)
from melder.spellbook.spell_crafter.spell_examiner.spell_examiner import SpellExaminer
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.protocols import IService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_spell_examiner() -> None:
    """
    Purpose:
        Reset the Aether singleton for component SpellExaminer tests.
    Contract:
        - Rebinds Spellbook and Conduit to a fresh Aether instance.
        - Restores the singleton after the test completes.
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
    config.set_property("rift_enabled", True)
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


def test_component_spell_examiner_resolution_profile_matches_spell_metadata() -> None:
    """
    Purpose:
        Validate SpellExaminer resolution profile reflects Spell metadata.
    Contract:
        - Profile metadata matches the Spell it was built from.
        - Requirements include DI parameters and required holes.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide a spell with a DI parameter and a plain required parameter.
        Contract:
            - Declares a service dependency and a required value.
        Args:
            service: Injected IService dependency.
            count: Required plain parameter.
        """

        def __init__(self, service: IService, count: int) -> None:
            """
            Purpose:
                Capture constructor inputs for inspection.
            Contract:
                - Stores inputs as attributes.
            Args:
                service: Injected IService dependency.
                count: Required plain parameter.
            Returns:
                None.
            """
            self.service = service
            self.count = count

    general_profile = None
    try:
        spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
            spellframe=IService,
        )
        consumer_id = spellbook.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None

        examiner = SpellExaminer()
        general_profile = examiner.create_profile(spell, "general")
        profile = general_profile.resolution_profile

        assert profile is not None
        assert profile.spell_id == spell.spell_index.current
        assert profile.existence == spell.existence
        assert profile.spellframe == spell.spellframe
        assert profile.binding_name == spell.binding_name

        requirements = profile.requirements
        assert requirements.spell_id == spell.spell_index.current

        di_names = {param.name for param in requirements.iter_di_parameters()}
        required_holes = {param.name for param in requirements.iter_required_holes()}
        assert "service" in di_names
        assert "count" in required_holes
    finally:
        if general_profile is not None:
            general_profile.cleanup()
        spellbook.cleanup()


def test_component_spell_examiner_binding_profile_for_spell_uses_underlying_class() -> None:
    """
    Purpose:
        Validate binding profiles use the underlying class from Spell.
    Contract:
        - Binding profile is a ClassBindingProfile for class spells.
        - original_object points to the original class.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    general_profile = None
    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        examiner = SpellExaminer()
        general_profile = examiner.create_profile(spell, "general")
        profile = general_profile.binding_profile

        assert isinstance(profile, ClassBindingProfile)
        assert profile.kind is SpellBindingKind.CLASS
        assert profile.original_object is BasicService
    finally:
        if general_profile is not None:
            general_profile.cleanup()
        spellbook.cleanup()


def test_component_spell_examiner_detailed_profile_links_resolution_and_binding() -> None:
    """
    Purpose:
        Validate AI profiles link binding and resolution profiles for a Spell.
    Contract:
        - AI profile references the Spell instance.
        - Binding profile reflects the underlying class.
        - Resolution profile references the spell id and requirements.
    Returns:
        None.
    """
    spellbook = _make_spellbook()

    class Consumer:
        """
        Purpose:
            Provide a simple consumer spell for AI profile checks.
        Contract:
            - Declares a BasicService dependency.
        Args:
            service: Injected BasicService dependency.
        """

        def __init__(self, service: BasicService) -> None:
            """
            Purpose:
                Capture the injected dependency.
            Contract:
                - Stores the dependency on the instance.
            Args:
                service: Injected BasicService dependency.
            Returns:
                None.
            """
            self.service = service

    detailed_profile = None
    try:
        spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        consumer_id = spellbook.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None

        examiner = SpellExaminer()
        detailed_profile = examiner.create_profile(spell, "detailed")

        assert detailed_profile.spell is spell
        assert detailed_profile.binding_profile.original_object is Consumer
        assert detailed_profile.resolution_profile.spell_id == spell.spell_index.current

        requirement_names = {
            param.name
            for param in detailed_profile.resolution_profile.requirements.parameters
        }
        assert "service" in requirement_names
    finally:
        if detailed_profile is not None:
            detailed_profile.cleanup()
        spellbook.cleanup()
