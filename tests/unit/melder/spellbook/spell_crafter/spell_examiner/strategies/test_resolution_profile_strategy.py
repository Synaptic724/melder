from types import SimpleNamespace

from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.profiles.resolution_profile import (
    SpellResolutionProfile,
)
from melder.spellbook.spell_crafter.spell_examiner.strategies import (
    resolution_profile_strategy as resolution_module,
)


def test_resolution_profile_strategy_builds_profile(monkeypatch) -> None:
    """
    Purpose:
        Ensure ResolutionProfileStrategy builds a basic resolution profile.
    Contract:
        The profile mirrors spell metadata and uses requirements from the finder.
    Args:
        monkeypatch: Pytest fixture for patching SpellRequirementsFinder.
    Returns:
        None.
    Raises:
        AssertionError: If profile fields are incorrect.
    """
    requirements = object()

    class DummyRequirementsFinder:
        """
        Purpose:
            Provide a stub requirements finder for tests.
        Contract:
            Returns a fixed requirements object on build.
        """
        def __init__(self, spell):
            """
            Purpose:
                Capture the spell passed to the finder.
            Contract:
                Stores the spell on the instance.
            Args:
                spell: Spell under analysis.
            Returns:
                None.
            """
            self.spell = spell

        def build_requirements(self, cancel_event=None):
            """
            Purpose:
                Return a predetermined requirements object.
            Contract:
                Always returns the requirements sentinel.
            Args:
                cancel_event: Optional cancellation signal.
            Returns:
                object: The requirements sentinel.
            """
            return requirements

    monkeypatch.setattr(
        resolution_module,
        "SpellRequirementsFinder",
        DummyRequirementsFinder,
    )

    spell = SimpleNamespace(
        spell_id="spell-1",
        existence=Existence.unique,
        spellframe="frame-1",
        binding_name="binding",
    )

    profile = resolution_module.ResolutionProfileStrategy().build_profile(spell)

    assert isinstance(profile, SpellResolutionProfile)
    assert profile.spell_id == "spell-1"
    assert profile.existence is Existence.unique
    assert profile.spellframe == "frame-1"
    assert profile.binding_name == "binding"
    assert profile.requirements is requirements
    assert profile.symbolic_graph is None
    assert profile.resolution_frame is None
    assert profile.validation is None
