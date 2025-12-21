from types import SimpleNamespace

from melder.spellbook.spell_crafter.spell_examiner.profiles.ai_profile import SpellAIProfile
from melder.spellbook.spell_crafter.spell_examiner.strategies import ai_profile_strategy as ai_module


def test_ai_profile_strategy_builds_class_profile(monkeypatch) -> None:
    """
    Purpose:
        Verify AIProfileStrategy builds a class-based AI profile.
    Contract:
        Binding, resolution, and class inspection outputs populate the profile.
    Args:
        monkeypatch: Pytest fixture for patching strategy dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If the profile fields are not populated as expected.
    """
    binding_profile = object()
    resolution_profile = object()
    class_profile = object()
    captured = {}

    class DummyBindingStrategy:
        """
        Purpose:
            Provide a stub binding strategy for AIProfileStrategy tests.
        Contract:
            Records constructor args and returns a fixed profile object.
        """
        def __init__(self, *, show_dunders: bool = False, max_repr: int = 120) -> None:
            """
            Purpose:
                Capture initialization arguments.
            Contract:
                Records show_dunders and max_repr in the captured dict.
            Args:
                show_dunders: Whether dunder methods are visible.
                max_repr: Maximum repr length.
            Returns:
                None.
            """
            captured["show_dunders"] = show_dunders
            captured["max_repr"] = max_repr

        def build_profile(self, _spell_object):
            """
            Purpose:
                Return a stub binding profile.
            Contract:
                Always returns the binding_profile sentinel.
            Args:
                _spell_object: Spell object supplied by the caller.
            Returns:
                object: The sentinel binding profile.
            """
            return binding_profile

    class DummyResolutionStrategy:
        """
        Purpose:
            Provide a stub resolution strategy for AIProfileStrategy tests.
        Contract:
            Returns a fixed resolution profile object.
        """
        def build_profile(self, _spell):
            """
            Purpose:
                Return a stub resolution profile.
            Contract:
                Always returns the resolution_profile sentinel.
            Args:
                _spell: Spell object supplied by the caller.
            Returns:
                object: The sentinel resolution profile.
            """
            return resolution_profile

    def _inspect_class_stub(_spell):
        """
        Purpose:
            Provide a stub class inspection result.
        Contract:
            Always returns the class_profile sentinel.
        Args:
            _spell: Spell object supplied by the caller.
        Returns:
            object: The sentinel class profile.
        """
        return class_profile

    monkeypatch.setattr(ai_module, "BindingProfileStrategy", DummyBindingStrategy)
    monkeypatch.setattr(ai_module, "ResolutionProfileStrategy", DummyResolutionStrategy)

    spell = SimpleNamespace(
        spell=object(),
        is_class_spell=True,
        is_method_spell=False,
        is_lambda_spell=False,
    )
    strategy = ai_module.AIProfileStrategy(show_dunders=True, max_repr=33)
    monkeypatch.setattr(strategy, "_inspect_class", _inspect_class_stub)

    profile = strategy.build_profile(spell)

    assert isinstance(profile, SpellAIProfile)
    assert profile.binding_profile is binding_profile
    assert profile.resolution_profile is resolution_profile
    assert profile.class_profile is class_profile
    assert profile.callable_profile is None
    assert captured["show_dunders"] is True
    assert captured["max_repr"] == 33
