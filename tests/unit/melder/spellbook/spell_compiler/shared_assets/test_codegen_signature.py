"""Unit tests for the single codegen signature implementation and its two facades."""

import enum
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Dict, List, Tuple

from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_schema_helpers import (
    CodegenCreationSchemaHelpers,
)
from melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)
from melder.aether.spellbook.spell_compiler.shared_assets.codegen_signature import (
    CodegenSignature,
)
from tests.mocks.spellbook.codegen_signature_reference import (
    reference_freeze_phase11_schema_value,
    reference_hash_codegen_signature,
    reference_serialize_codegen_signature_part,
)


class _Existence(enum.Enum):
    """Enum double standing in for `Existence` members inside payloads."""

    unique = "unique"
    many = "many"


@dataclass(frozen=True)
class _ValueRecord:
    """Dataclass double whose default `repr` is address-free."""

    label: str
    count: int


class _DefaultReprObject:
    """Instance whose `repr` carries a memory address (the process-local case)."""

    __slots__ = ["marker"]

    def __init__(self, marker: str) -> None:
        """Store one marker so two instances are logically equal but distinct."""
        self.marker = marker


class _MethodHolder:
    """Holder for a bound method used as a payload value."""

    def build(self) -> str:
        """Return a constant so the bound method is a plain callable value."""
        return "built"


def _payload_function() -> str:
    """Module-level function used as a payload value."""
    return "function"


_DETERMINISTIC_PARTS: Tuple[Any, ...] = (
    None,
    True,
    False,
    0,
    -17,
    3.5,
    "spell-1",
    "",
    b"raw",
    bytearray(b"raw"),
    ("dep", "root"),
    (("row", 1), ("row", 2)),
    ["a", "b"],
    {"k": ("v", 1), "j": None},
    (("svc", ("dep",), "normal", 0, "POSITIONAL_OR_KEYWORD", False, False, ()),),
    _Existence.unique,
    _ValueRecord("x", 1),
    _ValueRecord,
)


def test_serializer_matches_reference_bytes_for_every_deterministic_part() -> None:
    """Every input that was deterministic before must encode to identical bytes now."""
    for part in _DETERMINISTIC_PARTS:
        assert (
            CodegenSignature.serialize_codegen_signature_part(part)
            == reference_serialize_codegen_signature_part(part)
        ), repr(part)


def test_hash_matches_reference_digest_for_deterministic_parts() -> None:
    """The digest over deterministic parts must be byte-identical to the shipped digest."""
    assert CodegenSignature.hash_codegen_signature(*_DETERMINISTIC_PARTS) == (
        reference_hash_codegen_signature(*_DETERMINISTIC_PARTS)
    )
    assert CodegenSignature.hash_codegen_signature("root", ("dep",)) != (
        CodegenSignature.hash_codegen_signature("root", "dep")
    )


def test_serializer_scalar_tags_are_distinct_per_type() -> None:
    """Scalar fast paths keep their one-byte tags so equal payloads of different types differ."""
    assert CodegenSignature.serialize_codegen_signature_part(None) == b"N"
    assert CodegenSignature.serialize_codegen_signature_part(True) == b"B1"
    assert CodegenSignature.serialize_codegen_signature_part(False) == b"B0"
    assert CodegenSignature.serialize_codegen_signature_part(1) == b"I1"
    assert CodegenSignature.serialize_codegen_signature_part(1.0) == b"F1.0"
    assert CodegenSignature.serialize_codegen_signature_part("1") == b"S1"
    assert CodegenSignature.serialize_codegen_signature_part(b"1") == b"Y1"
    assert CodegenSignature.serialize_codegen_signature_part(bytearray(b"1")) == b"Y1"


def test_serializer_canonicalizes_top_level_sets() -> None:
    """A set part encodes independently of its construction order and equals its frozen tuple."""
    forward = {"alpha", "beta", "gamma", "delta"}
    backward = set(reversed(["alpha", "beta", "gamma", "delta"]))
    frozen = frozenset(forward)

    encoded_forward = CodegenSignature.serialize_codegen_signature_part(forward)

    assert encoded_forward == CodegenSignature.serialize_codegen_signature_part(backward)
    assert encoded_forward == CodegenSignature.serialize_codegen_signature_part(frozen)
    assert encoded_forward == CodegenSignature.serialize_codegen_signature_part(
        CodegenSignature.freeze_phase11_schema_value(forward)
    )


def test_freeze_keeps_reference_projection_for_address_free_values() -> None:
    """Primitives, containers, enums, dataclasses and classes freeze exactly as before."""
    nested: Dict[str, Any] = {
        "b": [1, (2, 3)],
        "a": {"z": _Existence.many, "y": _ValueRecord("v", 2)},
        "s": {"x", "y"},
    }
    for value in (nested, _Existence.unique, _ValueRecord("x", 1), _ValueRecord, 7, "s"):
        assert CodegenSignature.freeze_phase11_schema_value(value) == (
            reference_freeze_phase11_schema_value(value)
        ), repr(value)


def test_freeze_renders_callables_without_addresses() -> None:
    """Functions and bound methods freeze to (marker, module, qualname) instead of an address."""
    holder_a = _MethodHolder()
    holder_b = _MethodHolder()

    frozen_function = CodegenSignature.freeze_phase11_schema_value(_payload_function)
    frozen_method_a = CodegenSignature.freeze_phase11_schema_value(holder_a.build)
    frozen_method_b = CodegenSignature.freeze_phase11_schema_value(holder_b.build)
    frozen_builtin = CodegenSignature.freeze_phase11_schema_value(len)

    assert frozen_function == ("__callable__", __name__, "_payload_function")
    assert frozen_method_a == ("__callable__", __name__, "_MethodHolder.build")
    assert frozen_method_a == frozen_method_b
    assert frozen_builtin == ("__callable__", "builtins", "len")
    assert reference_freeze_phase11_schema_value(holder_a.build) != (
        reference_freeze_phase11_schema_value(holder_b.build)
    )


def test_freeze_renders_default_repr_instances_identically() -> None:
    """Two distinct instances of a type without `__repr__` freeze to the same marker tuple."""
    first = _DefaultReprObject("m")
    second = _DefaultReprObject("m")

    frozen_first = CodegenSignature.freeze_phase11_schema_value(first)

    assert frozen_first == ("__object__", __name__, "_DefaultReprObject")
    assert frozen_first == CodegenSignature.freeze_phase11_schema_value(second)
    assert reference_freeze_phase11_schema_value(first) != (
        reference_freeze_phase11_schema_value(second)
    )
    assert CodegenSignature.freeze_phase11_schema_value(object()) == (
        "__object__",
        "builtins",
        "object",
    )


def test_freeze_sorts_frozensets_like_sets() -> None:
    """A frozenset no longer collapses to iteration-ordered repr text."""
    frozen = CodegenSignature.freeze_phase11_schema_value(frozenset({"b", "a", "c"}))

    assert frozen == ("a", "b", "c")
    assert frozen == CodegenSignature.freeze_phase11_schema_value({"c", "b", "a"})


def test_both_facades_delegate_to_the_single_implementation() -> None:
    """The phase-side and phase-11 facades return the leaf's bytes, digests and projections."""
    parts: List[Any] = ["root", ("dep", "root"), {"k": {"y", "x"}}, _DefaultReprObject("m")]
    payload = {"marker": _DefaultReprObject("m"), "fn": _payload_function, "n": 1}

    for facade in (SharedCompilerExecutions, CodegenCreationSchemaHelpers):
        for part in parts:
            assert facade.serialize_codegen_signature_part(part) == (
                CodegenSignature.serialize_codegen_signature_part(part)
            )
        assert facade.hash_codegen_signature(*parts) == (
            CodegenSignature.hash_codegen_signature(*parts)
        )
        assert facade.freeze_phase11_schema_value(payload) == (
            CodegenSignature.freeze_phase11_schema_value(payload)
        )
    assert SharedCompilerExecutions.hash_codegen_signature(*parts) == (
        CodegenCreationSchemaHelpers.hash_codegen_signature(*parts)
    )


def test_no_overrides_signature_row_ignores_payload_object_identity() -> None:
    """Two plan steps whose contract payloads hold distinct default-repr objects sign identically."""

    def _step(payload_object: Any) -> SimpleNamespace:
        """Build one plan-step double carrying an object-valued contract payload."""
        return SimpleNamespace(
            instance_key=("consumer", None),
            spell=SimpleNamespace(spell_index=SimpleNamespace(selected_spell_id="consumer-id")),
            existence=_Existence.unique,
            creations_target_kind="conduit",
            dependency_resolution_order=[("service", [("service-id", None)])],
            collection_param_names=set(),
            uses_positional_override=False,
            contract_positional_override=None,
            has_contract_payload=True,
            contract_payload={"marker": payload_object, "hook": _payload_function},
            use_spell_lock_hint=False,
            must_register=True,
        )

    row_a = CodegenCreationSchemaHelpers.build_no_overrides_codegen_creation_step_signature_row(
        _step(_DefaultReprObject("m"))
    )
    row_b = CodegenCreationSchemaHelpers.build_no_overrides_codegen_creation_step_signature_row(
        _step(_DefaultReprObject("m"))
    )

    assert row_a == row_b
    assert CodegenSignature.hash_codegen_signature(row_a) == (
        CodegenSignature.hash_codegen_signature(row_b)
    )
