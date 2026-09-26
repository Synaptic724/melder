"""
Unit tests for contract override references (owner ruling 2026-09-26).

A `SpellContract` / `SpellMap` override payload may hold any object. Phase 9 records a value-only
reference beside every payload entry; the phase-11 row builders of every codegen family write a
scalar entry as itself and any other entry as that reference; the no-overrides hydration sites
resolve the reference back to the consumer's LIVE descriptor value, so the provider's constructor
receives the object by identity, in-process and after a cache load alike. The former emission gate
(owner option B) is retired: the manifest package builder packages every plan (the legacy
non-manifest codec is retired too, 2026-09-26).
"""

import enum
from types import SimpleNamespace
from typing import Any, Dict, Optional, Tuple

import pytest

from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets import (
    manifest_creation_cache,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_schema_helpers import (
    CodegenCreationSchemaHelpers,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_codegen_creation_helpers import (
    ManyOnlyCodegenCreationHelpers,
)
from melder.aether.spellbook.spell_compiler.shared_assets.codegen_signature import (
    CodegenSignature,
)


class _Existence(enum.Enum):
    """Plain enum probe: its `repr` is stable but it is not a row fixed point."""

    UNIQUE = "unique"


class _Priority(enum.IntEnum):
    """IntEnum probe: an `int` subclass that marshal cannot persist."""

    HIGH = 1


class _Label(str):
    """`str` subclass probe: same reasoning as `_Priority`."""


class _DefaultReprObject:
    """Instance whose `repr` is `object.__repr__`: the object-payload case."""


def _payload_function() -> None:
    """Function probe."""


_MARKER = _DefaultReprObject()
_HOOK = _DefaultReprObject()


class _Consumer:
    """Consumer probe whose constructor defaults carry the descriptors the resolver reads."""

    def __init__(
            self,
            cfg: Any = SpellContract(spell="provider", override={"marker": _MARKER, "level": 3}),
            dep: Any = SpellMap(spell="dependency", override=[_HOOK, "x"]),
            args_only: Any = SpellContract(spell="positional", override={"__args__": [1, _HOOK]}),
            plain: int = 0,
    ) -> None:
        """Hold the descriptors; never constructed by these tests."""
        self.cfg = cfg
        self.dep = dep
        self.args_only = args_only
        self.plain = plain


def _ref(param_name: str, key: Any) -> Tuple[str, str, str, Any]:
    """Build the reference for one entry of `_Consumer`'s descriptor on `param_name`."""
    return CodegenSignature.build_contract_override_ref("consumer", param_name, key)


def _spell_lookup() -> Dict[str, Any]:
    """Build the hydration lookup: the consumer spell wraps the probe class."""
    return {"consumer": SimpleNamespace(spell=_Consumer)}


# ---------------------------------------------------------------------------
# Reference shape and classifier (leaf) + facade delegation
# ---------------------------------------------------------------------------

def test_reference_shape_is_a_scalar_tuple_and_is_recognised() -> None:
    """The reference is a 4-tuple of scalars, a freeze fixed point, and only that shape is a reference."""
    ref = CodegenSignature.build_contract_override_ref("consumer", "cfg", "marker")

    assert ref == ("__contract_override__", "consumer", "cfg", "marker")
    assert CodegenSignature.is_contract_override_ref(ref) is True
    assert CodegenSignature.freeze_phase11_schema_value(ref) == ref
    assert CodegenSignature.is_replayable_contract_payload_value(ref) is True
    assert CodegenSignature.is_contract_override_ref(("__contract_override__", "a", "b")) is False
    assert CodegenSignature.is_contract_override_ref(["__contract_override__", "a", "b", 1]) is False
    assert CodegenSignature.is_contract_override_ref("__contract_override__") is False


@pytest.mark.parametrize(
    "value",
    [None, True, False, 0, -7, 1.5, "", "marker", (), (1, "a", None), (("nested", 2), (3.5,))],
)
def test_replayable_values_are_the_freeze_fixed_points(value: Any) -> None:
    """Every value the rows keep as-is freezes to itself, in the leaf and through the facade."""
    assert CodegenSignature.is_replayable_contract_payload_value(value) is True
    assert CodegenCreationSchemaHelpers.is_replayable_contract_payload_value(value) is True
    assert CodegenSignature.freeze_phase11_schema_value(value) == value


@pytest.mark.parametrize(
    "value",
    [
        [1, 2], {"a": 1}, {1, 2}, frozenset({1}), b"bytes", bytearray(b"x"), _Existence.UNIQUE,
        _Priority.HIGH, _Label("x"), _DefaultReprObject, _DefaultReprObject(), _payload_function, len,
        (1, [2]), ("ok", {"nested": "dict"}),
    ],
)
def test_non_replayable_values_become_references(value: Any) -> None:
    """Containers other than tuples, scalar subclasses, enums, classes, callables and objects are refs."""
    assert CodegenSignature.is_replayable_contract_payload_value(value) is False
    assert CodegenCreationSchemaHelpers.is_replayable_contract_payload_value(value) is False


# ---------------------------------------------------------------------------
# Row projection rule
# ---------------------------------------------------------------------------

def test_projection_keeps_scalars_and_substitutes_references() -> None:
    """A scalar entry is written as itself; an object entry as its reference; the facade delegates."""
    refs = {"marker": _ref("cfg", "marker"), "level": _ref("cfg", "level")}

    assert CodegenSignature.project_contract_payload_entry("level", 3, refs) == 3
    assert CodegenSignature.project_contract_payload_entry("marker", _MARKER, refs) == refs["marker"]
    assert CodegenCreationSchemaHelpers.project_contract_payload_entry("marker", _MARKER, refs) == refs["marker"]
    assert CodegenSignature.project_contract_payload_entry("marker", ("a", 1), None) == ("a", 1)


def test_projection_of_positional_payload_is_elementwise() -> None:
    """`__args__` projects element by element into a tuple; None stays None; a scalar stays itself."""
    refs = {"__args__": (None, _ref("args_only", 1))}

    assert CodegenSignature.project_contract_payload_entry("__args__", [1, _HOOK], refs) == (1, refs["__args__"][1])
    assert CodegenSignature.project_contract_payload_entry("__args__", (1, "b"), None) == (1, "b")
    assert CodegenSignature.project_contract_payload_entry("__args__", None, None) is None
    assert CodegenSignature.project_contract_payload_entry("__args__", 5, None) == 5


def test_projection_refuses_an_object_without_a_reference() -> None:
    """A step built without references cannot write an object into a row: the builder fails loudly."""
    with pytest.raises(RuntimeError, match="carries no reference"):
        CodegenSignature.project_contract_payload_entry("marker", _MARKER, None)
    with pytest.raises(RuntimeError, match="positional contract payload item 1"):
        CodegenSignature.project_contract_payload_entry("__args__", [1, _HOOK], {"__args__": (None,)})
    with pytest.raises(RuntimeError, match="neither a list/tuple nor a scalar"):
        CodegenSignature.project_contract_payload_entry("__args__", _HOOK, None)


# ---------------------------------------------------------------------------
# Resolver
# ---------------------------------------------------------------------------

def test_resolver_returns_the_live_descriptor_value_by_identity() -> None:
    """A keyword reference resolves to the object the consumer's `SpellContract` holds right now."""
    cache: Dict[Tuple[str, str], Any] = {}

    value = CodegenCreationSchemaHelpers.resolve_contract_override_ref(_ref("cfg", "marker"), _spell_lookup(), cache)

    assert value is _MARKER
    assert CodegenCreationSchemaHelpers.resolve_contract_override_ref(_ref("cfg", "level"), _spell_lookup(), cache) == 3
    assert set(cache) == {("consumer", "cfg")}


def test_resolver_reads_spellmap_payloads_and_positional_indexes() -> None:
    """A `SpellMap` list payload resolves by index; a dict payload's `__args__` resolves by index too."""
    cache: Dict[Tuple[str, str], Any] = {}

    assert CodegenCreationSchemaHelpers.resolve_contract_override_ref(_ref("dep", 0), _spell_lookup(), cache) is _HOOK
    assert CodegenCreationSchemaHelpers.resolve_contract_override_ref(_ref("dep", 1), _spell_lookup(), cache) == "x"
    assert CodegenCreationSchemaHelpers.resolve_contract_override_ref(_ref("args_only", 1), _spell_lookup(), cache) is _HOOK


@pytest.mark.parametrize(
    "ref, match",
    [
        (("__contract_override__", "ghost", "cfg", "marker"), "not in the hydration lookup"),
        (("__contract_override__", "consumer", "missing", "marker"), "has no default"),
        (("__contract_override__", "consumer", "plain", "marker"), "not a SpellContract or SpellMap"),
        (("__contract_override__", "consumer", "cfg", "absent"), "is missing"),
        (("__contract_override__", "consumer", "dep", 9), "does not match the descriptor payload shape"),
        (("__contract_override__", "consumer", "args_only", 5), "is out of range"),
    ],
)
def test_resolver_names_the_consumer_and_parameter_on_every_failure(ref: Any, match: str) -> None:
    """Every unresolvable reference raises RuntimeError naming what was looked for."""
    with pytest.raises(RuntimeError, match=match):
        CodegenCreationSchemaHelpers.resolve_contract_override_ref(ref, _spell_lookup(), {})


def test_resolver_refuses_a_descriptor_without_a_payload() -> None:
    """A descriptor that carries no payload cannot satisfy a reference."""

    class _Bare:
        """Consumer probe with a payload-free descriptor."""

        def __init__(self, cfg: Any = SpellContract(spell="provider")) -> None:
            """Hold the descriptor."""
            self.cfg = cfg

    with pytest.raises(RuntimeError, match="carries no payload"):
        CodegenCreationSchemaHelpers.resolve_contract_override_ref(
            _ref("cfg", "marker"), {"consumer": SimpleNamespace(spell=_Bare)}, {},
        )


def test_row_values_resolve_references_and_pass_scalars_through() -> None:
    """The row resolver walks items and positional tuples; scalars and scalar tuples pass unchanged."""
    row = {
        "contract_payload_items": (
            ("level", 3),
            ("marker", _ref("cfg", "marker")),
            ("pair", (1, _ref("dep", 0))),
        ),
        "contract_positional_override": (1, _ref("args_only", 1)),
    }

    items, positional = CodegenCreationSchemaHelpers.resolve_contract_payload_row_values(row, _spell_lookup(), {})

    assert items[0] == ("level", 3)
    assert items[1][0] == "marker" and items[1][1] is _MARKER
    assert items[2][0] == "pair" and items[2][1][0] == 1 and items[2][1][1] is _HOOK
    assert positional[0] == 1 and positional[1] is _HOOK
    assert row["contract_positional_override"][1] == _ref("args_only", 1)


def test_references_are_rebuilt_from_a_raw_row() -> None:
    """A hydrated adapter regains the references the raw row carried; a scalar row yields None."""
    row = {
        "contract_payload_items": (("level", 3), ("marker", _ref("cfg", "marker"))),
        "contract_positional_override": (1, _ref("args_only", 1)),
    }

    refs = CodegenCreationSchemaHelpers.contract_payload_refs_from_row(row)

    assert refs == {"marker": _ref("cfg", "marker"), "__args__": (None, _ref("args_only", 1))}
    assert CodegenCreationSchemaHelpers.contract_payload_refs_from_row(
        {"contract_payload_items": (("level", 3),), "contract_positional_override": None},
    ) is None


# ---------------------------------------------------------------------------
# Row builders: generalized facade and many-only family
# ---------------------------------------------------------------------------

def _step(
        contract_payload: Optional[Dict[str, Any]],
        contract_payload_refs: Optional[Dict[str, Any]],
        *,
        positional: Any = None,
) -> SimpleNamespace:
    """Build one immutable-plan-step probe carrying every field the row builders read."""
    spell = SimpleNamespace(
        spell_index=SimpleNamespace(selected_spell_id="provider"),
        has_disposal_methods=False,
        disposal_method_names=(),
    )
    return SimpleNamespace(
        instance_key=("provider", None),
        spell=spell,
        existence=Existence.many,
        creations_target_kind="caller",
        shared_instance=False,
        dependency_resolution_order=(),
        collection_param_names=frozenset(),
        override_match_prefix=None,
        override_match_prefix_len=0,
        override_keys=(),
        expects_overrides=False,
        contract_keys=(),
        allow_list_aggregation=False,
        uses_positional_override=positional is not None,
        contract_positional_override=positional,
        has_contract_payload=bool(contract_payload),
        contract_payload=contract_payload,
        contract_payload_refs=contract_payload_refs,
        lock_hint=None,
        use_spell_lock_hint=False,
        requires_spellspace=False,
        owner_conduit_required=False,
        must_register=False,
        disposal_method_names=(),
    )


def test_generalized_rows_write_scalars_as_is_and_objects_as_references() -> None:
    """Both generalized row builders emit the projection rule; the object never enters a row."""
    refs = {"marker": _ref("cfg", "marker"), "__args__": (None, _ref("args_only", 1))}
    step = _step({"level": 3, "marker": _MARKER}, refs, positional=[1, _HOOK])

    row = CodegenCreationSchemaHelpers.build_phase11_step_ir_row(step, include_override_metadata=False)
    signature_row = CodegenCreationSchemaHelpers.build_no_overrides_codegen_creation_step_signature_row(step)

    assert row["contract_payload_items"] == (("level", 3), ("marker", refs["marker"]))
    assert row["contract_positional_override"] == (1, refs["__args__"][1])
    assert signature_row[7] == (1, refs["__args__"][1])
    assert signature_row[9] == (("level", 3), ("marker", refs["marker"]))
    assert _MARKER not in (value for _name, value in row["contract_payload_items"])


def test_generalized_rows_keep_previous_bytes_for_scalar_payloads() -> None:
    """A scalar-only payload rows exactly as the frozen rows did, so payload-free books keep their cache."""
    step = _step({"marker": "override", "count": (1, 2)}, None, positional=(9,))

    row = CodegenCreationSchemaHelpers.build_phase11_step_ir_row(step)

    assert row["contract_payload_items"] == (("count", (1, 2)), ("marker", "override"))
    assert row["contract_positional_override"] == (9,)
    assert CodegenCreationSchemaHelpers.hash_codegen_signature(row["contract_payload_items"]) == (
        CodegenCreationSchemaHelpers.hash_codegen_signature(
            (("count", CodegenSignature.freeze_phase11_schema_value((1, 2))), ("marker", "override")),
        )
    )


def test_generalized_rows_refuse_an_object_without_a_reference() -> None:
    """A plan step that carries an object but no references fails the row build instead of freezing it."""
    with pytest.raises(RuntimeError, match="carries no reference"):
        CodegenCreationSchemaHelpers.build_phase11_step_ir_row(_step({"marker": _MARKER}, None))


def test_many_only_rows_follow_the_same_projection_rule() -> None:
    """The many-only signature row writes scalars as-is and objects as references."""
    refs = {"marker": _ref("cfg", "marker"), "__args__": (None, _ref("args_only", 1))}
    step = _step({"level": 3, "marker": _MARKER}, refs, positional=[1, _HOOK])

    signature_row = ManyOnlyCodegenCreationHelpers.build_no_overrides_step_signature_row(step)

    assert signature_row[5] == (1, refs["__args__"][1])
    assert signature_row[7] == (("level", 3), ("marker", refs["marker"]))


# ---------------------------------------------------------------------------
# Package builders: the emission gate is retired
# ---------------------------------------------------------------------------

def _manifest_spell(spell_codegen_plan: Optional[SimpleNamespace]) -> SimpleNamespace:
    """Build a manifest-first spell probe whose artifact carries a manifest and the given plan."""
    manifest = {"family_id": "generalized_codegen_creation", "no_overrides": {}}
    return SimpleNamespace(
        spell_id="spell-1",
        _compiler_artifact=SimpleNamespace(
            _spell_codegen_creation=SimpleNamespace(
                metadata={manifest_creation_cache.MANIFEST_METADATA_KEY: manifest},
            ),
            _spell_codegen_plan=spell_codegen_plan,
            _spell_codegen_model=SimpleNamespace(),
        ),
    )


@pytest.mark.parametrize(
    "spell_codegen_plan",
    [
        None,
        SimpleNamespace(no_overrides_plan=SimpleNamespace(steps=(_step({"marker": _MARKER}, {"marker": _ref("cfg", "marker")}),))),
    ],
)
def test_manifest_package_is_built_whatever_the_plan_carries(spell_codegen_plan: Optional[SimpleNamespace]) -> None:
    """The envelope builder no longer inspects the plan: every manifest is exported as stored."""
    package = manifest_creation_cache.build_package(_manifest_spell(spell_codegen_plan))

    assert package["family_id"] == "generalized_codegen_creation"
    assert package["spell_id"] == "spell-1"
    assert package["package_version"] == manifest_creation_cache.PACKAGE_VERSION
    assert manifest_creation_cache.is_manifest_package(package) is True


def test_manifest_package_still_raises_without_phase11_output() -> None:
    """The hard failures for missing phase-11 output are unchanged."""
    with pytest.raises(RuntimeError, match="compiler artifact"):
        manifest_creation_cache.build_package(SimpleNamespace(spell_id="x", _compiler_artifact=None))
