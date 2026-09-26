from dataclasses import dataclass
import inspect

from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile import (
    SpellBindingKind,
    ClassBindingProfile,
    CallableBindingProfile,
    InstanceBindingProfile,
    OtherBindingProfile,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.strategies.binding_profile_strategy import (
    BindingProfileStrategy,
)
from typing import TYPE_CHECKING, Optional

from melder.aether.spellbook.bind.bind import Bind
from melder.utilities.helpers.signature_reflection import SignatureReflection

if TYPE_CHECKING:
    # Annotations only: `Decimal` stays unbound at runtime in this module - the case under test.
    from decimal import Decimal


class _TypeCheckingField:
    """
    Purpose:
        Class whose field annotation names a TYPE_CHECKING-only type.
    """
    amount: Decimal
    label: str


class _QuotedUnavailable:
    """
    Purpose:
        Class whose quoted field annotation names a TYPE_CHECKING-only type.
    """
    amount: "Decimal"
    label: str


class _NestedUnavailable:
    """
    Purpose:
        Class whose unavailable name sits inside generic annotations.
    """
    amounts: list[Decimal]
    total: Optional[Decimal]
    count: int


@dataclass
class _DataclassUnavailable:
    """
    Purpose:
        Dataclass whose field annotation names a TYPE_CHECKING-only type.
    """
    amount: Decimal
    label: str = "x"


class _ResolvedFields:
    """
    Purpose:
        Class whose annotations all resolve at runtime, one of them quoted.
    """
    count: int
    name: "str"


def _priced_class(extra: bool) -> type:
    """
    Purpose:
        Build a class named `Priced` with one or two TYPE_CHECKING-typed fields.
    Contract:
        Both variants share name, qualname, module, bases and methods; only the annotation keys differ.
    Args:
        extra: Whether to declare the second field.
    Returns:
        type: The class.
    """
    class Priced:
        amount: Decimal
        if extra:
            surcharge: Decimal
    return Priced


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
        - Missing file information falls back to None.
        - origin_line now comes from `__firstlineno__` (no source-file read),
          so it survives unreadable sources.
        - The lazy `source_preview` property degrades to None when the
          source read fails on first access.
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
    assert profile.origin_line == getattr(Sample, "__firstlineno__", None)
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


def test_binding_profile_class_annotations_keep_type_checking_names_as_source_text() -> None:
    """
    Purpose:
        Verify a field typed with a TYPE_CHECKING-only name keeps every class annotation.
    Contract:
        - Keys are the class's own annotation names.
        - The unavailable name is its source text; resolvable values stay evaluated.
    Returns:
        None.
    """
    profile = BindingProfileStrategy()._build_class_profile(_TypeCheckingField)

    assert profile.annotations == {"amount": "Decimal", "label": str}


def test_binding_profile_class_annotations_keep_quoted_and_nested_unavailable_names() -> None:
    """
    Purpose:
        Verify quoted and generic-nested unavailable names are kept as written.
    Contract:
        - A quoted annotation stays its string; a nested one is the generic's source text.
    Returns:
        None.
    """
    strategy = BindingProfileStrategy()

    quoted = strategy._build_class_profile(_QuotedUnavailable)
    nested = strategy._build_class_profile(_NestedUnavailable)

    assert quoted.annotations == {"amount": "Decimal", "label": str}
    assert nested.annotations == {"amounts": "list[Decimal]", "total": "Optional[Decimal]", "count": int}


def test_binding_profile_class_annotations_keep_dataclass_fields_with_unavailable_names() -> None:
    """
    Purpose:
        Verify a dataclass field typed with a TYPE_CHECKING-only name is kept.
    Returns:
        None.
    """
    profile = BindingProfileStrategy()._build_class_profile(_DataclassUnavailable)

    assert profile.annotations == {"amount": "Decimal", "label": str}
    assert profile.is_dataclass is True


def test_binding_profile_class_annotations_unchanged_when_every_name_resolves() -> None:
    """
    Purpose:
        Verify classes whose annotations resolve keep the evaluated read (quoted strings evaluated).
    Returns:
        None.
    """
    profile = BindingProfileStrategy()._build_class_profile(_ResolvedFields)

    assert profile.annotations == {"count": int, "name": str}


def test_binding_profile_class_annotations_fallback_failure_binds_with_none(monkeypatch) -> None:
    """
    Purpose:
        Verify a failure inside the unevaluated fallback still yields an empty mapping.
    Contract:
        - Binding never fails because class annotations cannot be read.
    Returns:
        None.
    """
    def _raise_name_error(*args, **kwargs):
        raise NameError("name 'Decimal' is not defined")

    def _raise_type_error(cls):
        raise TypeError("boom")

    monkeypatch.setattr(inspect, "get_annotations", _raise_name_error)
    monkeypatch.setattr(SignatureReflection, "class_annotations", staticmethod(_raise_type_error))

    profile = BindingProfileStrategy()._build_class_profile(_TypeCheckingField)

    assert profile.annotations == {}


def test_bind_fingerprint_counts_fields_typed_with_type_checking_names() -> None:
    """
    Purpose:
        Verify the bind fingerprint changes when a TYPE_CHECKING-typed field is added.
    Contract:
        - Before 2026-09-26 both classes profiled with no annotations and hashed equal.
        - Equal classes still hash equal.
    Returns:
        None.
    """
    strategy = BindingProfileStrategy()

    plain = Bind.sha256_profile(strategy._build_class_profile(_priced_class(False)))
    again = Bind.sha256_profile(strategy._build_class_profile(_priced_class(False)))
    extended = Bind.sha256_profile(strategy._build_class_profile(_priced_class(True)))

    assert plain == again
    assert plain != extended
