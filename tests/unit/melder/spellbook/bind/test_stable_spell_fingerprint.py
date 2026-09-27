"""
Regression contracts: bind fingerprints never depend on memory addresses.

CPython's default reprs embed an object's address (`<function f at 0x...>`, `<C object at 0x...>`), which
differs between processes. The bind fingerprint hashed those reprs (and signature text, where a default such
as `object()` renders its address), so function, lambda, method, partial, callable-instance and default-repr
instance spells got a new id in every process. Two content-identical objects created in one process differ
only by address, which makes them a deterministic stand-in for "the same object in another process".
"""

import functools
import types
from typing import Any, Callable, Tuple

import pytest

from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.inspector_utility import InspectorUtility
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile import (
    CallableBindingProfile,
    CallableParameterBindingSummary,
    InstanceBindingProfile,
    SpellBindingKind,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.strategies.binding_profile_strategy import (
    BindingProfileStrategy,
)


class _Engine:
    """Plain product type."""


def _make_engine(size: int = 3) -> _Engine:
    """Plain factory function."""
    return _Engine()


def _make_with_marker(marker: object = object()) -> _Engine:
    """Factory whose default renders its own address."""
    return _Engine()


class _Workshop:
    """Owner of a bound-method factory."""

    def build(self) -> _Engine:
        """Bound-method factory."""
        return _Engine()


class _CallableFactory:
    """Instance with __call__ (routed to the callable profile)."""

    def __call__(self) -> _Engine:
        return _Engine()


class _Settings:
    """Existing object with the default repr."""


class _NamedSettings:
    """Existing object with a custom repr."""

    def __init__(self, label: str) -> None:
        self.label = label

    def __repr__(self) -> str:
        return f"_NamedSettings({self.label})"


class _LongRepr:
    """Object whose repr is longer than the 120-character display cut."""

    def __repr__(self) -> str:
        return "_LongRepr(" + "x" * 300 + ")"


class _BrokenRepr:
    """Object whose repr raises."""

    def __repr__(self) -> str:
        raise RuntimeError("no repr")


def _clone_function(function: types.FunctionType, defaults: Any = None) -> types.FunctionType:
    """Return a distinct function object with the same code, globals, name, qualname and annotations."""
    clone = types.FunctionType(
        function.__code__,
        function.__globals__,
        function.__name__,
        function.__defaults__ if defaults is None else defaults,
        function.__closure__,
    )
    clone.__qualname__ = function.__qualname__
    clone.__kwdefaults__ = function.__kwdefaults__
    # Python 3.14 keeps lazy annotations on __annotate__, which FunctionType() does not copy.
    clone.__annotate__ = function.__annotate__
    return clone


def _make_marker_class() -> type:
    """Build a class whose constructor default is a fresh object() (new address per call)."""

    class _MarkerEngine:
        def __init__(self, marker: object = object()) -> None:
            self.marker = marker

    return _MarkerEngine


def _twins(shape: str) -> Tuple[Any, Any]:
    """
    Return two distinct objects of one shape whose fingerprint content is identical.

    Every pair differs only in memory addresses (its own, or one embedded in a default or a wrapped callable).
    """
    make_lambda = lambda: _Engine()
    builders: dict[str, Callable[[], Tuple[Any, Any]]] = {
        "function": lambda: (_make_engine, _clone_function(_make_engine)),
        "lambda": lambda: (make_lambda, _clone_function(make_lambda)),
        "function_object_default": lambda: (_make_with_marker, _clone_function(_make_with_marker, (object(),))),
        "bound_method": lambda: (_Workshop().build, _Workshop().build),
        "partial": lambda: (
            functools.partial(_make_engine, size=4),
            functools.partial(_clone_function(_make_engine), size=4),
        ),
        "callable_instance": lambda: (_CallableFactory(), _CallableFactory()),
        "instance_default_repr": lambda: (_Settings(), _Settings()),
        "class_object_default": lambda: (_make_marker_class(), _make_marker_class()),
    }
    return builders[shape]()


def _spell_id(target: Any) -> str:
    """Fingerprint one candidate exactly as the binding pipeline would (unique existence)."""
    return Bind.spell_id_inspector(target, existence=Existence.unique)


def test_stable_repr_removes_every_memory_address() -> None:
    """
    Purpose: The fingerprint helper removes CPython's " at 0x<hex>" fragments, nested ones included.
    Contract: No address survives; the surrounding text is kept.
    """
    partial_text = InspectorUtility.stable_repr(functools.partial(_make_engine, size=4))
    method_text = InspectorUtility.stable_repr(_Workshop().build)

    assert InspectorUtility.stable_repr(object()) == "<object object>"
    assert InspectorUtility.stable_repr(_make_engine) == f"<function {_make_engine.__qualname__}>"
    assert " at 0x" not in partial_text and partial_text.endswith("size=4)")
    assert " at 0x" not in method_text and method_text.startswith("<bound method _Workshop.build of ")


def test_stable_repr_keeps_the_full_text_and_custom_reprs() -> None:
    """
    Purpose: The fingerprint text is not the truncated display text.
    Contract: Long reprs are kept whole; custom reprs without addresses are unchanged.
    """
    assert InspectorUtility.stable_repr(_LongRepr()) == repr(_LongRepr())
    assert InspectorUtility.stable_repr(_NamedSettings("prod")) == "_NamedSettings(prod)"
    assert "(len " in InspectorUtility.safe_repr(_LongRepr(), 120)


def test_stable_repr_of_a_failing_repr_returns_the_placeholder() -> None:
    """
    Purpose: A broken repr must not fail binding.
    Contract: Same placeholder as safe_repr.
    """
    assert InspectorUtility.stable_repr(_BrokenRepr()) == "<unrepr-able _BrokenRepr>"


@pytest.mark.parametrize(
    "shape",
    [
        "bound_method",
        "callable_instance",
        "class_object_default",
        "function",
        "function_object_default",
        "instance_default_repr",
        "lambda",
        "partial",
    ],
)
def test_content_identical_objects_share_one_spell_id(shape: str) -> None:
    """
    Purpose: Regression for per-process spell ids of address-bearing spells.
    Contract: Two distinct objects with identical fingerprint content get the same id.
    """
    first, second = _twins(shape)

    assert first is not second
    assert _spell_id(first) == _spell_id(second)


def test_content_differences_still_change_the_spell_id() -> None:
    """
    Purpose: Removing addresses must not merge objects that differ in content.
    Contract: Different defaults, different custom reprs and different callables keep different ids.
    """
    assert _spell_id(functools.partial(_make_engine, size=4)) != _spell_id(functools.partial(_make_engine, size=5))
    assert _spell_id(_NamedSettings("prod")) != _spell_id(_NamedSettings("test"))
    assert _spell_id(_make_engine) != _spell_id(_make_with_marker)
    assert _spell_id(_Settings()) != _spell_id(_NamedSettings("prod"))


def test_strategy_keeps_display_reprs_and_adds_fingerprint_text() -> None:
    """
    Purpose: Display reprs are unchanged; the fingerprint text is carried beside them.
    Contract: repr_string/default_repr keep the address; fingerprint fields have none.
    """
    strategy = BindingProfileStrategy()
    callable_profile = strategy.build_profile(_make_with_marker)
    instance_profile = strategy.build_profile(_Settings())
    marker = callable_profile.parameters[0]

    assert " at 0x" in callable_profile.repr_string
    assert callable_profile.fingerprint_repr == f"<function {_make_with_marker.__qualname__}>"
    assert " at 0x" in marker.default_repr
    assert marker.default_fingerprint_repr == "<object object>"
    assert " at 0x" in instance_profile.repr_string
    assert " at 0x" not in instance_profile.fingerprint_repr


def test_profiles_without_fingerprint_text_hash_address_free_display_text() -> None:
    """
    Purpose: Profiles built directly (no strategy) fall back to the display text minus addresses.
    Contract: Profiles differing only by addresses fingerprint identically.
    """

    def build(address: str) -> CallableBindingProfile:
        return CallableBindingProfile(
            kind=SpellBindingKind.CALLABLE,
            original_object=_make_engine,
            name="f",
            qualname="f",
            module="mod",
            object_id=1,
            type_name="function",
            repr_string=f"<function f at {address}>",
            signature=f"(marker=<object object at {address}>)",
            parameters=[CallableParameterBindingSummary("marker", "POSITIONAL_OR_KEYWORD", f"<object object at {address}>", None)],
        )

    def instance(address: str) -> InstanceBindingProfile:
        return InstanceBindingProfile(
            kind=SpellBindingKind.INSTANCE,
            original_object=object(),
            type_name="T",
            module="mod",
            repr_string=f"<mod.T object at {address}>",
        )

    assert Bind.sha256_profile(build("0x7f00aa")) == Bind.sha256_profile(build("0x1b2c3d4e5f"))
    assert Bind.sha256_profile(instance("0x7f00aa")) == Bind.sha256_profile(instance("0x1b2c3d4e5f"))
