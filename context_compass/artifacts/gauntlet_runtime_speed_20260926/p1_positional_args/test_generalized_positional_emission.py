"""
Unit tests for the positional-dependency prefix in the generalized no-overrides emitter.

Purpose:
    Pin the rule that decides which dependency values an emitted constructor call may pass
    positionally, and the emitted-source shape that uses it. On CPython 3.14 a positional class
    call takes the interpreter's specialized allocate-and-init path, while a keyword call builds a
    kwargs dict first; the prefix is only ever the part of the call where a positional value binds
    to exactly the parameter the keyword would have named.

These are pure-function and source-shape tests over synthetic classes and manifest rows; no Aether
runtime, conjure or live spells are involved.
"""

import abc
import dataclasses
import re
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, Dict, Sequence, Tuple

import pytest

from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_manifest_no_overrides_compiler import (
    emit_specialized_step_plan_source,
    emit_step_plan_source,
    positional_dependency_names,
    rows_positional_dependency_names,
)

if TYPE_CHECKING:
    # Bound for type checkers only: at runtime `Fraction` is not a module name, so evaluating an
    # annotation that uses it raises NameError - the TYPE_CHECKING-only case the emitter must survive.
    from fractions import Fraction


def _row(
        spell_id: str,
        existence: str,
        deps: Sequence[Tuple[str, Sequence[str]]] = (),
        *,
        callable_spell: bool = True,
        positional_override: Any = None,
) -> Dict[str, Any]:
    """
    Build one synthetic manifest step row with the full required field set.

    Args:
        spell_id: Step spell id; also the instance key's first element.
        existence: Existence name for the step.
        deps: `(param_name, dependency_spell_ids)` pairs in resolution order.
        callable_spell: Value for the row's `spell_is_callable` flag.
        positional_override: Optional contract positional override payload.

    Returns:
        Dict[str, Any]: A row accepted by the generalized emitter.
    """
    return {
        "spell_id": spell_id,
        "existence": existence,
        "instance_key": (spell_id, None),
        "dependency_resolution_order": tuple(
            (name, tuple((dep, None) for dep in dep_ids))
            for name, dep_ids in deps
        ),
        "collection_param_names": (),
        "creations_target_kind": 0,
        "use_spell_lock_hint": existence == "unique",
        "has_contract_payload": False,
        "contract_payload_items": (),
        "contract_positional_override": positional_override,
        "uses_positional_override": positional_override is not None,
        "must_register": existence != "many",
        "shared_instance": existence != "many",
        "override_match_prefix": None,
        "override_match_prefix_len": 0,
        "spell_is_callable": callable_spell,
        "spell_is_existing_creation": False,
        "spell_has_disposal_methods": False,
    }


def _call_arguments(source: str, step_index: int) -> Tuple[str, ...]:
    """
    Return the argument lines of `target_<step_index>(...)` in emitted source, stripped.

    Args:
        source: Emitted executor source.
        step_index: Step whose constructor call is read.

    Returns:
        Tuple[str, ...]: One entry per argument line, in emission order.
    """
    match = re.search(rf"target_{step_index}\(\n(.*?)\n\s*\)", source, re.S)
    assert match is not None, f"no call to target_{step_index} in source"
    return tuple(line.strip() for line in match.group(1).split("\n"))


class Alpha:
    """Dependency type used by the synthetic constructors."""


class Beta:
    """Second dependency type used by the synthetic constructors."""


class Pair:
    """Plain two-dependency constructor."""

    def __init__(self, alpha: Alpha, beta: Beta) -> None:
        """Store both dependencies."""
        self.alpha = alpha
        self.beta = beta


class TestPositionalDependencyNames:
    """
    `positional_dependency_names` returns the signature-order prefix a target binds positionally.
    """

    def test_plain_class_returns_signature_order_prefix(self) -> None:
        """Names come back in the target's parameter order, not the caller's order."""
        assert positional_dependency_names(
            target=Pair,
            dependency_param_names=("beta", "alpha"),
        ) == ("alpha", "beta")

    def test_prefix_stops_at_first_non_dependency(self) -> None:
        """A defaulted (non-injected) parameter ends the prefix so no value can shift."""

        class DefaultInMiddle:
            """Dependency, defaulted plain value, dependency."""

            def __init__(self, alpha: Alpha, count: int = 3, beta: Any = None) -> None:
                """Store the arguments."""
                self.alpha, self.count, self.beta = alpha, count, beta

        assert positional_dependency_names(
            target=DefaultInMiddle,
            dependency_param_names=("alpha", "beta"),
        ) == ("alpha",)

    def test_keyword_only_parameters_are_never_positional(self) -> None:
        """Keyword-only dependencies stay keywords."""

        class KeywordOnly:
            """One positional-or-keyword and one keyword-only dependency."""

            def __init__(self, alpha: Alpha, *, beta: Beta) -> None:
                """Store both dependencies."""
                self.alpha, self.beta = alpha, beta

        assert positional_dependency_names(
            target=KeywordOnly,
            dependency_param_names=("alpha", "beta"),
        ) == ("alpha",)

    def test_positional_only_parameters_are_included(self) -> None:
        """Positional-only dependencies are part of the prefix (a keyword call cannot fill them)."""

        class PositionalOnly:
            """A positional-only dependency followed by a regular one."""

            def __init__(self, alpha: Alpha, /, beta: Beta) -> None:
                """Store both dependencies."""
                self.alpha, self.beta = alpha, beta

        assert positional_dependency_names(
            target=PositionalOnly,
            dependency_param_names=("alpha", "beta"),
        ) == ("alpha", "beta")

    def test_custom_metaclass_call_keeps_keywords(self) -> None:
        """A metaclass that overrides `__call__` may route arguments differently: no prefix."""

        class Meta(type):
            """Metaclass with its own `__call__`."""

            def __call__(cls, *args: Any, **kwargs: Any) -> Any:
                """Delegate to `type.__call__`."""
                return super().__call__(*args, **kwargs)

        class WithMeta(metaclass=Meta):
            """Class built through the custom metaclass."""

            def __init__(self, alpha: Alpha) -> None:
                """Store the dependency."""
                self.alpha = alpha

        assert positional_dependency_names(
            target=WithMeta,
            dependency_param_names=("alpha",),
        ) == ()

    def test_custom_new_keeps_keywords(self) -> None:
        """A custom `__new__` also receives the arguments, so the call stays keyword."""

        class WithNew:
            """Class with its own `__new__`."""

            def __new__(cls, *args: Any, **kwargs: Any) -> "WithNew":
                """Allocate without inspecting the arguments."""
                return super().__new__(cls)

            def __init__(self, alpha: Alpha) -> None:
                """Store the dependency."""
                self.alpha = alpha

        assert positional_dependency_names(
            target=WithNew,
            dependency_param_names=("alpha",),
        ) == ()

    def test_abc_and_dataclass_targets_qualify(self) -> None:
        """ABCMeta keeps `type.__call__` and a dataclass `__init__` is a plain function."""

        class Base(abc.ABC):
            """Abstract-base-derived constructor."""

            def __init__(self, alpha: Alpha, beta: Beta) -> None:
                """Store both dependencies."""
                self.alpha, self.beta = alpha, beta

        @dataclasses.dataclass
        class Record:
            """Dataclass with two fields."""

            alpha: int
            beta: int

        assert positional_dependency_names(
            target=Base,
            dependency_param_names=("alpha", "beta"),
        ) == ("alpha", "beta")
        assert positional_dependency_names(
            target=Record,
            dependency_param_names=("alpha", "beta"),
        ) == ("alpha", "beta")

    def test_non_class_target_keeps_keywords(self) -> None:
        """Function spells keep keyword calls."""

        def factory(alpha: Alpha) -> Alpha:
            """Return the dependency."""
            return alpha

        assert positional_dependency_names(
            target=factory,
            dependency_param_names=("alpha",),
        ) == ()

    def test_inherited_object_init_keeps_keywords(self) -> None:
        """`object.__init__` is not a Python function: no prefix."""

        class Bare:
            """No `__init__` of its own."""

        assert positional_dependency_names(
            target=Bare,
            dependency_param_names=("alpha",),
        ) == ()

    def test_varargs_initializer_keeps_keywords(self) -> None:
        """An `(self, *args, **kwargs)` initializer has no named positional parameters."""

        class Forwarding:
            """Initializer that only forwards."""

            def __init__(self, *args: Any, **kwargs: Any) -> None:
                """Keep the raw arguments."""
                self.args, self.kwargs = args, kwargs

        assert positional_dependency_names(
            target=Forwarding,
            dependency_param_names=("alpha",),
        ) == ()

    def test_annotations_are_never_evaluated(self) -> None:
        """A TYPE_CHECKING-only annotation cannot raise: only the code object is read."""

        class UnboundAnnotation:
            """Initializer annotated with a type imported only under TYPE_CHECKING."""

            def __init__(self, alpha: Fraction, beta: Beta) -> None:
                """Store both dependencies."""
                self.alpha, self.beta = alpha, beta

        assert positional_dependency_names(
            target=UnboundAnnotation,
            dependency_param_names=("alpha", "beta"),
        ) == ("alpha", "beta")

    def test_empty_dependency_names_short_circuit(self) -> None:
        """No dependencies means nothing to pass positionally."""
        assert positional_dependency_names(
            target=Pair,
            dependency_param_names=(),
        ) == ()


class TestRowsPositionalDependencyNames:
    """
    `rows_positional_dependency_names` maps each row through its live spell.
    """

    def test_rows_map_through_spell_lookup(self) -> None:
        """Inlinable rows get their prefix; rows without dependencies or not callable get ()."""
        rows = (
            _row("alpha", "unique"),
            _row("beta", "unique"),
            _row("pair", "many", [("beta", ["beta"]), ("alpha", ["alpha"])]),
            _row("opaque", "many", [("alpha", ["alpha"])], callable_spell=False),
        )
        lookup = {
            "alpha": SimpleNamespace(spell=Alpha),
            "beta": SimpleNamespace(spell=Beta),
            "pair": SimpleNamespace(spell=Pair),
            "opaque": SimpleNamespace(spell=Pair),
        }
        assert rows_positional_dependency_names(rows=rows, spell_lookup=lookup) == (
            (),
            (),
            ("alpha", "beta"),
            (),
        )

    def test_positional_splat_row_gets_empty_prefix(self) -> None:
        """A contract positional override owns the leading positions, so the prefix is empty."""
        rows = (
            _row("alpha", "unique"),
            _row("pair", "many", [("alpha", ["alpha"])], positional_override=(1,)),
        )
        lookup = {"alpha": SimpleNamespace(spell=Alpha), "pair": SimpleNamespace(spell=Pair)}
        assert rows_positional_dependency_names(rows=rows, spell_lookup=lookup) == ((), ())

    def test_missing_spell_raises_runtime_error(self) -> None:
        """An inlinable row without a live spell fails fast with a named error."""
        rows = (_row("alpha", "unique"), _row("pair", "many", [("alpha", ["alpha"])]))
        with pytest.raises(RuntimeError, match="'pair' is missing from spell_lookup"):
            rows_positional_dependency_names(rows=rows, spell_lookup={})


class TestPositionalEmission:
    """
    Emitted constructor calls put the prefix first, then keywords.
    """

    ROWS = (
        _row("d1", "many"),
        _row("d2", "many"),
        _row("root", "many", [("first", ["d1"]), ("second", ["d2"]), ("third", ["d1"])]),
    )

    def test_prefix_emits_positional_arguments_before_keywords(self) -> None:
        """Prefix values are bare positional arguments in prefix order; the rest stay keywords."""
        source = emit_step_plan_source(
            rows=self.ROWS,
            root_instance_key=("root", None),
            positional_dependency_names=((), (), ("first", "second")),
        )
        assert _call_arguments(source, 2) == (
            "instance_0,",
            "instance_1,",
            "third=instance_0,",
        )

    def test_none_keeps_keyword_emission_unchanged(self) -> None:
        """Without prefixes the source is byte-identical to the keyword-only emission."""
        keyword_source = emit_step_plan_source(rows=self.ROWS, root_instance_key=("root", None))
        assert emit_step_plan_source(
            rows=self.ROWS,
            root_instance_key=("root", None),
            positional_dependency_names=None,
        ) == keyword_source
        assert _call_arguments(keyword_source, 2) == (
            "first=instance_0,",
            "second=instance_1,",
            "third=instance_0,",
        )

    def test_length_mismatch_raises(self) -> None:
        """One prefix tuple per row is required."""
        with pytest.raises(RuntimeError, match="exactly one entry per row"):
            emit_step_plan_source(
                rows=self.ROWS,
                root_instance_key=("root", None),
                positional_dependency_names=((), ()),
            )

    def test_unknown_prefix_name_raises(self) -> None:
        """A prefix name that is not an emitted dependency of the step fails fast."""
        with pytest.raises(RuntimeError, match="'fourth' is not an emitted dependency of step 2"):
            emit_step_plan_source(
                rows=self.ROWS,
                root_instance_key=("root", None),
                positional_dependency_names=((), (), ("first", "fourth")),
            )

    def test_specialized_emitter_threads_prefix_to_non_captured_steps(self) -> None:
        """Non-captured steps compile with the same positional prefix as in the generic body."""
        rows = (
            _row("single", "unique"),
            _row("d2", "many"),
            _row("root", "many", [("first", ["single"]), ("second", ["d2"])]),
        )
        source = emit_specialized_step_plan_source(
            rows=rows,
            captured_step_indexes=(0,),
            root_instance_key=("root", None),
            positional_dependency_names=((), (), ("first", "second")),
        )
        assert _call_arguments(source, 2) == ("instance_0,", "instance_1,")
