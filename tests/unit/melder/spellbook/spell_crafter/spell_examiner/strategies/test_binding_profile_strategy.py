from dataclasses import dataclass
import inspect

from melder.spellbook.spell_crafter.spell_examiner.profiles.binding_profile import (
    SpellBindingKind,
    ClassBindingProfile,
    CallableBindingProfile,
    InstanceBindingProfile,
    OtherBindingProfile,
)
from melder.spellbook.spell_crafter.spell_examiner.strategies.binding_profile_strategy import (
    BindingProfileStrategy,
)


class _SampleService:
    """
    Purpose:
        Provide a class candidate for binding profile tests.
    Contract:
        Exposes a callable method to appear in method_names.
    """
    def run(self, value: int) -> int:
        """
        Purpose:
            Provide a simple instance method for inspection.
        Contract:
            Returns the input value.
        Args:
            value: Input value.
        Returns:
            int: The same value passed in.
        """
        return value


class _DunderService:
    """
    Purpose:
        Provide a class with dunder methods for filtering tests.
    Contract:
        Exposes __str__ and a normal method for method_names checks.
    """
    def __str__(self) -> str:
        """
        Purpose:
            Provide a dunder method for inspection filters.
        Contract:
            Returns a fixed string representation.
        Returns:
            str: Fixed string representation.
        """
        return "dunder"

    def ping(self) -> str:
        """
        Purpose:
            Provide a normal method for inspection filters.
        Contract:
            Returns a fixed string.
        Returns:
            str: Fixed response string.
        """
        return "pong"


@dataclass
class _DataclassService:
    """
    Purpose:
        Provide a dataclass for dunder inclusion tests.
    Contract:
        Dataclass-generated __init__ should be present in __dict__.
    """
    value: int


def _sample_function(value: int, other: int = 2) -> int:
    """
    Purpose:
        Provide a callable candidate for binding profile tests.
    Contract:
        Returns the sum of value and other.
    Args:
        value: Primary input value.
        other: Optional addend.
    Returns:
        int: Sum of value and other.
    """
    return value + other


def _abstract_function(value: int) -> int:
    """
    Purpose:
        Provide an abstract-marked callable for binding profile tests.
    Contract:
        Returns the input value.
    Args:
        value: Input value.
    Returns:
        int: The same value passed in.
    """
    return value


def test_binding_profile_strategy_builds_class_profile() -> None:
    """
    Purpose:
        Verify class candidates produce ClassBindingProfile outputs.
    Contract:
        The profile kind is CLASS and includes method names.
    Returns:
        None.
    Raises:
        AssertionError: If class profile fields are missing or incorrect.
    """
    strategy = BindingProfileStrategy()
    profile = strategy.build_profile(_SampleService)

    assert isinstance(profile, ClassBindingProfile)
    assert profile.kind is SpellBindingKind.CLASS
    assert "run" in profile.method_names


def test_binding_profile_strategy_builds_callable_profile() -> None:
    """
    Purpose:
        Verify callable candidates produce CallableBindingProfile outputs.
    Contract:
        The profile kind is CALLABLE and captures a signature string.
    Returns:
        None.
    Raises:
        AssertionError: If callable profile fields are missing or incorrect.
    """
    strategy = BindingProfileStrategy()
    profile = strategy.build_profile(_sample_function)

    assert isinstance(profile, CallableBindingProfile)
    assert profile.kind is SpellBindingKind.CALLABLE
    assert profile.signature is not None
    assert "other" in profile.signature
    assert " = 2" in profile.signature


def test_binding_profile_strategy_builds_instance_profile() -> None:
    """
    Purpose:
        Verify instance candidates produce InstanceBindingProfile outputs.
    Contract:
        The profile kind is INSTANCE and reflects the instance type.
    Returns:
        None.
    Raises:
        AssertionError: If instance profile fields are missing or incorrect.
    """
    strategy = BindingProfileStrategy()
    instance = _SampleService()
    profile = strategy.build_profile(instance)

    assert isinstance(profile, InstanceBindingProfile)
    assert profile.kind is SpellBindingKind.INSTANCE
    assert profile.type_name == "_SampleService"


def test_binding_profile_strategy_filters_dunders_when_hidden() -> None:
    """
    Purpose:
        Ensure dunder methods are excluded when show_dunders is False.
    Contract:
        __str__ is omitted while normal methods are preserved.
    Returns:
        None.
    Raises:
        AssertionError: If dunder filtering does not behave as expected.
    """
    strategy = BindingProfileStrategy(show_dunders=False)
    profile = strategy.build_profile(_DunderService)

    assert "__str__" not in profile.method_names
    assert "ping" in profile.method_names


def test_binding_profile_strategy_includes_dunders_when_enabled() -> None:
    """
    Purpose:
        Ensure dunder methods are included when show_dunders is True.
    Contract:
        __str__ appears in the method names when dunders are enabled.
    Returns:
        None.
    Raises:
        AssertionError: If dunder inclusion does not behave as expected.
    """
    strategy = BindingProfileStrategy(show_dunders=True)
    profile = strategy.build_profile(_DunderService)

    assert "__str__" in profile.method_names


def test_binding_profile_strategy_includes_dataclass_init() -> None:
    """
    Purpose:
        Verify dataclass __init__ is retained when dunders are hidden.
    Contract:
        Dataclass-generated __init__ should be present in method_names.
    Returns:
        None.
    Raises:
        AssertionError: If __init__ is missing for dataclass types.
    """
    strategy = BindingProfileStrategy(show_dunders=False)
    profile = strategy.build_profile(_DataclassService)

    assert "__init__" in profile.method_names


def test_binding_profile_strategy_detects_lambda_function() -> None:
    """
    Purpose:
        Ensure lambda candidates are marked as lambda_function.
    Contract:
        CallableBindingProfile.lambda_function is True for lambdas.
    Returns:
        None.
    Raises:
        AssertionError: If the lambda flag is not set.
    """
    strategy = BindingProfileStrategy()
    profile = strategy.build_profile(lambda value: value)

    assert isinstance(profile, CallableBindingProfile)
    assert profile.lambda_function is True


def test_binding_profile_strategy_abstract_flag_matches_inspect() -> None:
    """
    Purpose:
        Verify abstract flag mirrors inspect.isabstract for callables.
    Contract:
        CallableBindingProfile.abstract matches inspect.isabstract(effective).
    Returns:
        None.
    Raises:
        AssertionError: If the abstract flag diverges from inspect.isabstract.
    """
    _abstract_function.__isabstractmethod__ = True
    strategy = BindingProfileStrategy()
    profile = strategy.build_profile(_abstract_function)

    assert isinstance(profile, CallableBindingProfile)
    assert profile.abstract is inspect.isabstract(_abstract_function)


def test_binding_profile_strategy_class_profile_fallbacks_clear_optional_source_details(
        monkeypatch,
) -> None:
    """
    Purpose:
        Verify class-profile building tolerates annotation/file/source failures.
    Contract:
        - Failed annotation resolution falls back to an empty dict.
        - Missing file/source information falls back to None.
    Returns:
        None.
    """

    class Sample:
        def ping(self) -> str:
            return "pong"

    strategy = BindingProfileStrategy()

    monkeypatch.setattr(inspect, "get_annotations", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))
    monkeypatch.setattr(inspect, "getfile", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))
    monkeypatch.setattr(inspect, "getsourcelines", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))

    profile = strategy._build_class_profile(Sample)

    assert profile.annotations == {}
    assert profile.origin_file is None
    assert profile.origin_line is None
    assert profile.source_preview is None


def test_binding_profile_strategy_callable_profile_falls_back_when_signature_unavailable(
        monkeypatch,
) -> None:
    """
    Purpose:
        Verify callable-profile building tolerates signature failures.
    Contract:
        - Signature becomes None.
        - Parameter summaries become empty.
    Returns:
        None.
    """
    strategy = BindingProfileStrategy()

    monkeypatch.setattr(inspect, "signature", lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("boom")))

    profile = strategy._build_callable_profile(_sample_function)

    assert profile.signature is None
    assert profile.parameters == []


def test_binding_profile_strategy_build_other_profile_and_final_fallback(monkeypatch) -> None:
    """
    Purpose:
        Verify the fallback OTHER profile path remains available.
    Contract:
        - _build_other_profile returns an OtherBindingProfile.
        - build_profile can still route to the final fallback branch.
    Returns:
        None.
    """
    strategy = BindingProfileStrategy()
    candidate = object()

    direct_profile = strategy._build_other_profile(candidate)
    assert isinstance(direct_profile, OtherBindingProfile)
    assert direct_profile.kind is SpellBindingKind.OTHER

    call_state = {"count": 0}
    fallback_candidate = lambda value: value

    def fake_isclass(value):
        call_state["count"] += 1
        if call_state["count"] == 1:
            return False
        return True

    monkeypatch.setattr(inspect, "isclass", fake_isclass)

    fallback_profile = strategy.build_profile(fallback_candidate)

    assert isinstance(fallback_profile, OtherBindingProfile)
    assert fallback_profile.kind is SpellBindingKind.OTHER


def test_binding_profile_strategy_decorated_class_heuristic_edges() -> None:
    """
    Purpose:
        Verify the decorated-class heuristic covers non-class and wrapped cases.
    Contract:
        - Non-class values return True.
        - Objects with __wrapped__ return True.
        - Builtin-style classes return False.
    Returns:
        None.
    """
    assert BindingProfileStrategy._is_probably_decorated_class(object()) is True

    Wrapped = type("Wrapped", (), {})
    Wrapped.__wrapped__ = object()
    assert BindingProfileStrategy._is_probably_decorated_class(Wrapped) is True

    class Meta(type):
        pass

    class MetaClassed(metaclass=Meta):
        pass

    assert BindingProfileStrategy._is_probably_decorated_class(MetaClassed) is True

    Weird = type("Weird", (), {})
    Weird.__qualname__ = "Outer.Inner"
    Weird.__name__ = "Different"
    assert BindingProfileStrategy._is_probably_decorated_class(Weird) is True

    Plain = type("Plain", (), {})
    assert BindingProfileStrategy._is_probably_decorated_class(Plain) is False
