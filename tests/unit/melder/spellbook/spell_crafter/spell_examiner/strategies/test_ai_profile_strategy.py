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

    def _inspect_class_stub(self, _spell):
        """
        Purpose:
            Provide a stub class inspection result.
        Contract:
            Always returns the class_profile sentinel.
        Args:
            self: Strategy instance invoking the inspection.
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
    monkeypatch.setattr(ai_module.AIProfileStrategy, "_inspect_class", _inspect_class_stub)

    profile = strategy.build_profile(spell)

    assert isinstance(profile, SpellAIProfile)
    assert profile.binding_profile is binding_profile
    assert profile.resolution_profile is resolution_profile
    assert profile.class_profile is class_profile
    assert profile.callable_profile is None
    assert captured["show_dunders"] is True
    assert captured["max_repr"] == 33


def test_ai_profile_strategy_builds_callable_profile(monkeypatch) -> None:
    """
    Purpose:
        Verify AIProfileStrategy builds a callable-based AI profile.
    Contract:
        Callable inspection populates callable_profile and leaves class_profile empty.
    Args:
        monkeypatch: Pytest fixture for patching strategy dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If callable profile fields are not populated as expected.
    """
    binding_profile = object()
    resolution_profile = object()
    callable_profile = object()

    class DummyBindingStrategy:
        """
        Purpose:
            Provide a stub binding strategy for callable profile tests.
        Contract:
            Returns a fixed binding profile.
        """
        def __init__(self, *args, **kwargs) -> None:
            """
            Purpose:
                Accept initialization arguments from AIProfileStrategy.
            Contract:
                Stores no state and ignores inputs.
            Args:
                *args: Positional arguments ignored by the stub.
                **kwargs: Keyword arguments ignored by the stub.
            Returns:
                None.
            """
            self._args = args
            self._kwargs = kwargs

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
            Provide a stub resolution strategy for callable profile tests.
        Contract:
            Returns a fixed resolution profile.
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

    def _inspect_callable_stub(self, _spell):
        """
        Purpose:
            Provide a stub callable inspection result.
        Contract:
            Always returns the callable_profile sentinel.
        Args:
            self: Strategy instance invoking the inspection.
            _spell: Spell object supplied by the caller.
        Returns:
            object: The sentinel callable profile.
        """
        return callable_profile

    monkeypatch.setattr(ai_module, "BindingProfileStrategy", DummyBindingStrategy)
    monkeypatch.setattr(ai_module, "ResolutionProfileStrategy", DummyResolutionStrategy)
    monkeypatch.setattr(ai_module.AIProfileStrategy, "_inspect_callable", _inspect_callable_stub)

    spell = SimpleNamespace(
        spell=object(),
        is_class_spell=False,
        is_method_spell=True,
        is_lambda_spell=False,
    )
    strategy = ai_module.AIProfileStrategy()
    profile = strategy.build_profile(spell)

    assert isinstance(profile, SpellAIProfile)
    assert profile.binding_profile is binding_profile
    assert profile.resolution_profile is resolution_profile
    assert profile.class_profile is None
    assert profile.callable_profile is callable_profile


def test_ai_profile_strategy_fallback_callable_path(monkeypatch) -> None:
    """
    Purpose:
        Verify AIProfileStrategy falls back to callable inspection for other spells.
    Contract:
        Callable inspection runs when the spell is callable but not flagged as method/lambda.
    Args:
        monkeypatch: Pytest fixture for patching strategy dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If the fallback callable inspection does not run.
    """
    binding_profile = object()
    resolution_profile = object()
    callable_profile = object()

    class DummyBindingStrategy:
        """
        Purpose:
            Provide a stub binding strategy for fallback tests.
        Contract:
            Returns a fixed binding profile.
        """
        def __init__(self, *args, **kwargs) -> None:
            """
            Purpose:
                Accept initialization arguments from AIProfileStrategy.
            Contract:
                Stores no state and ignores inputs.
            Args:
                *args: Positional arguments ignored by the stub.
                **kwargs: Keyword arguments ignored by the stub.
            Returns:
                None.
            """
            self._args = args
            self._kwargs = kwargs

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
            Provide a stub resolution strategy for fallback tests.
        Contract:
            Returns a fixed resolution profile.
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

    def _inspect_callable_stub(self, _spell):
        """
        Purpose:
            Provide a stub callable inspection result.
        Contract:
            Always returns the callable_profile sentinel.
        Args:
            self: Strategy instance invoking the inspection.
            _spell: Spell object supplied by the caller.
        Returns:
            object: The sentinel callable profile.
        """
        return callable_profile

    def _callable_spell() -> str:
        """
        Purpose:
            Provide a callable spell target for fallback tests.
        Contract:
            Returns a fixed string.
        Returns:
            str: Fixed response string.
        """
        return "ok"

    monkeypatch.setattr(ai_module, "BindingProfileStrategy", DummyBindingStrategy)
    monkeypatch.setattr(ai_module, "ResolutionProfileStrategy", DummyResolutionStrategy)
    monkeypatch.setattr(ai_module.AIProfileStrategy, "_inspect_callable", _inspect_callable_stub)

    spell = SimpleNamespace(
        spell=_callable_spell,
        is_class_spell=False,
        is_method_spell=False,
        is_lambda_spell=False,
    )

    profile = ai_module.AIProfileStrategy().build_profile(spell)

    assert isinstance(profile, SpellAIProfile)
    assert profile.binding_profile is binding_profile
    assert profile.resolution_profile is resolution_profile
    assert profile.class_profile is None
    assert profile.callable_profile is callable_profile


def test_ai_profile_strategy_collects_instance_members() -> None:
    class CallableObject:
        def __init__(self):
            self.value = 42

        def __call__(self, arg: int) -> int:
            return arg + self.value

    instance = CallableObject()
    spell = SimpleNamespace(
        spell=instance,
        is_class_spell=False,
        is_method_spell=False,
        is_lambda_spell=False,
    )

    strategy = ai_module.AIProfileStrategy()
    profile = strategy.build_profile(
        spell,
        binding_profile=object(),
        resolution_profile=object(),
    )

    assert "value" in profile.instance_members
    assert profile.instance_members["value"]["kind"] == "instance_attribute"
