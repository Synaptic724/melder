"""Contract tests for SignatureReflection (Python 3.14 lazy annotations with TYPE_CHECKING-only names)."""

import inspect
import re
from annotationlib import ForwardRef, Format
from typing import TYPE_CHECKING, Callable, Optional

import pytest

from melder.utilities.helpers.signature_reflection import SignatureReflection

if TYPE_CHECKING:
    from decimal import Decimal


class _Engine:
    """Dependency type that is bound at runtime."""


def _resolvable(engine: _Engine, count: int = 1, *, label: Optional[str] = None) -> _Engine:
    """Callable whose annotation names are all available at runtime."""
    return engine


def _bare_unresolved(price: Decimal, engine: _Engine) -> Decimal:
    """Callable naming the TYPE_CHECKING-only `Decimal` directly."""
    return price


def _nested_unresolved(engine: _Engine, price: Optional[Decimal] = None) -> Optional[Decimal]:
    """Callable naming the TYPE_CHECKING-only `Decimal` inside `Optional[...]`."""
    return price


def _callable_unresolved(fn: Callable[[Decimal], int]) -> int:
    """Callable nesting the TYPE_CHECKING-only name inside a Callable argument list."""
    return 0


def _quoted_resolvable(engine: Optional["_Engine"] = None) -> None:
    """Callable whose quoted generic argument becomes an ownerless typing ForwardRef."""
    return None


class _AnnotatedCar:
    """Class whose own annotations mix available and TYPE_CHECKING-only names."""

    wheels: int
    price: Decimal
    maybe_price: Optional[Decimal]


class _PlainCar:
    """Class whose own annotations are all available."""

    wheels: int
    engine: _Engine


class _NoAnnotations:
    """Class declaring no annotations."""


_ADDRESS = re.compile(r"0x[0-9a-fA-F]+")


def test_default_signature_raises_name_error_for_type_checking_only_names() -> None:
    """
    Purpose: Pin the Python 3.14 behavior this helper exists for.
    Contract: A VALUE-format read of a TYPE_CHECKING-only name raises NameError.
    """
    with pytest.raises(NameError):
        inspect.signature(_nested_unresolved)


def test_display_signature_matches_value_format_when_every_name_resolves() -> None:
    """
    Purpose: Existing renderings must not change for ordinary callables.
    Contract: display_signature returns the VALUE-format signature when that read succeeds.
    """
    assert str(SignatureReflection.display_signature(_resolvable)) == str(inspect.signature(_resolvable))
    assert str(SignatureReflection.display_signature(_quoted_resolvable)) == str(
        inspect.signature(_quoted_resolvable)
    )


def test_display_signature_renders_nested_unresolved_name_as_source_text() -> None:
    """
    Purpose: A TYPE_CHECKING-only name nested in a typing construct renders readably.
    Contract: The affected annotation becomes its STRING-format text; the rest are unchanged.
    """
    signature = SignatureReflection.display_signature(_nested_unresolved)

    assert signature.parameters["price"].annotation == "Optional[Decimal]"
    assert signature.parameters["engine"].annotation is _Engine
    assert signature.parameters["price"].default is None
    assert signature.return_annotation == "Optional[Decimal]"


def test_display_signature_renders_bare_unresolved_name_by_name() -> None:
    """
    Purpose: A bare TYPE_CHECKING-only annotation renders as the name itself.
    Contract: The ForwardRef's argument replaces it; available annotations stay objects.
    """
    signature = SignatureReflection.display_signature(_bare_unresolved)

    assert signature.parameters["price"].annotation == "Decimal"
    assert signature.parameters["engine"].annotation is _Engine
    assert signature.return_annotation == "Decimal"


def test_display_signature_handles_callable_argument_lists() -> None:
    """
    Purpose: Unresolved names inside Callable[[...], ...] are found and replaced.
    Contract: The whole Callable annotation becomes its source text.
    """
    signature = SignatureReflection.display_signature(_callable_unresolved)

    assert signature.parameters["fn"].annotation == "Callable[[Decimal], int]"


def test_display_signature_text_never_embeds_an_owner_or_address() -> None:
    """
    Purpose: Rendered text must be stable across processes (it feeds spell fingerprints).
    Contract: No ForwardRef owner repr and no memory address appear in str(signature).
    """
    for target in (_bare_unresolved, _nested_unresolved, _callable_unresolved):
        text = str(SignatureReflection.display_signature(target))
        assert "owner=" not in text
        assert _ADDRESS.search(text) is None


def test_display_signature_propagates_non_name_errors() -> None:
    """
    Purpose: Only the unavailable-name case is handled.
    Contract: Targets without a signature still raise TypeError.
    """
    with pytest.raises(TypeError):
        SignatureReflection.display_signature(object())


def test_stabilize_signature_returns_same_object_without_unresolved_names() -> None:
    """
    Purpose: Callers holding a FORWARDREF signature pay nothing when every name resolves.
    Contract: The input signature object is returned unchanged.
    """
    signature = inspect.signature(_resolvable, annotation_format=Format.FORWARDREF)

    assert SignatureReflection.stabilize_signature(signature, _resolvable) is signature


def test_stabilize_signature_keeps_ownerless_typing_forward_refs() -> None:
    """
    Purpose: ForwardRefs that typing builds for quoted arguments already render deterministically.
    Contract: They are not replaced, so existing text for such callables is unchanged.
    """
    signature = inspect.signature(_quoted_resolvable, annotation_format=Format.FORWARDREF)

    assert SignatureReflection.stabilize_signature(signature, _quoted_resolvable) is signature


def test_stabilize_signature_does_not_modify_its_input() -> None:
    """
    Purpose: The FORWARDREF signature may be shared with other consumers.
    Contract: A new signature is returned; the input keeps its ForwardRef annotations.
    """
    signature = inspect.signature(_bare_unresolved, annotation_format=Format.FORWARDREF)

    stable = SignatureReflection.stabilize_signature(signature, _bare_unresolved)

    assert stable is not signature
    assert isinstance(signature.parameters["price"].annotation, ForwardRef)
    assert stable.parameters["price"].annotation == "Decimal"
    assert [p.kind for p in stable.parameters.values()] == [p.kind for p in signature.parameters.values()]


def test_class_annotations_match_dunder_annotations_when_every_name_resolves() -> None:
    """
    Purpose: Ordinary classes read exactly as before.
    Contract: class_annotations equals the evaluated `__annotations__` mapping.
    """
    assert SignatureReflection.class_annotations(_PlainCar) == dict(_PlainCar.__annotations__)


def test_class_annotations_render_unresolved_names_as_source_text() -> None:
    """
    Purpose: Class-level TYPE_CHECKING-only annotations no longer raise.
    Contract: Bare names become the name, nested ones their STRING text, others stay objects.
    """
    with pytest.raises(NameError):
        _AnnotatedCar.__annotations__

    assert SignatureReflection.class_annotations(_AnnotatedCar) == {
        "wheels": int,
        "price": "Decimal",
        "maybe_price": "Optional[Decimal]",
    }


def test_class_annotations_of_class_without_annotations_is_empty() -> None:
    """
    Purpose: Classes without annotations are a valid input.
    Contract: Returns an empty dict.
    """
    assert SignatureReflection.class_annotations(_NoAnnotations) == {}


def test_contains_unresolved_name_distinguishes_owner_bearing_forward_refs() -> None:
    """
    Purpose: Only references left by FORWARDREF reads for unavailable names are unresolved.
    Contract: Owner-bearing refs (bare or nested) report True; typing's ownerless refs and plain
        values report False.
    """
    forward = inspect.signature(_nested_unresolved, annotation_format=Format.FORWARDREF)
    quoted = inspect.signature(_quoted_resolvable, annotation_format=Format.FORWARDREF)

    assert SignatureReflection.contains_unresolved_name(forward.parameters["price"].annotation)
    assert not SignatureReflection.contains_unresolved_name(quoted.parameters["engine"].annotation)
    assert not SignatureReflection.contains_unresolved_name(int)
    assert not SignatureReflection.contains_unresolved_name("Decimal")
    assert not SignatureReflection.contains_unresolved_name(inspect.Parameter.empty)
