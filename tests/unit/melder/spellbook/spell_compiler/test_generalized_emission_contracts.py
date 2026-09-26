"""
Emission-contract tests for the generalized singleton specializer.

Purpose:
    Pin the emitted-source contracts landed in patch lane
    `generalized_singleton_specialization_2026_07_01` so refactors cannot
    silently regress them:
    - singleton warm-tail specialization emission (guards, capture aliases,
      root-collapse, deopt tail-call),
    - collection-DI inlinable emission (list literals, flat-cursor dict mode),
    - factory-source shareability (identity-free emission).
    The generic step and transient emitters were retired (R2, 2026-09-26); the
    per-step contracts they shared are pinned through the specializer, which
    emits every non-captured row with them.

These are source-shape and small-executor tests over synthetic manifest rows;
no Aether runtime, conjure, or live spells are involved.
"""

import threading
from types import SimpleNamespace
from typing import Any, Dict, Sequence, Tuple

import pytest

from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_manifest_no_overrides_compiler import (
    SPECIALIZED_EXECUTOR_NAME,
    emit_specialized_step_plan_source,
    row_inlinable_common_shape,
    select_specializable_step_indexes,
    _row_contract_call_extras,
    _row_contract_value_binding,
)
from melder.aether.spellbook.spell_compiler.executor_factory_cache import (
    build_executor_factory_source,
    get_or_build_executor_factory,
)


def _row(
        spell_id: str,
        existence: str,
        deps: Sequence[Tuple[str, Sequence[str]]] = (),
        *,
        callable_spell: bool = True,
        disposal: bool = False,
        collections: Sequence[str] = (),
) -> Dict[str, Any]:
    """
    Build one synthetic manifest step row with the full required field set.

    Args:
        collections: Parameter names whose sockets are collection DI shapes;
            emitted as the row's `collection_param_names` field.
    """
    return {
        "spell_id": spell_id,
        "existence": existence,
        "instance_key": (spell_id, None),
        "dependency_resolution_order": tuple(
            (name, tuple((dep, None) for dep in dep_ids))
            for name, dep_ids in deps
        ),
        "collection_param_names": tuple(collections),
        "creations_target_kind": 0,
        "use_spell_lock_hint": existence == "unique",
        "has_contract_payload": False,
        "contract_payload_items": (),
        "contract_positional_override": None,
        "uses_positional_override": False,
        "must_register": existence != "many",
        "shared_instance": existence != "many",
        "override_match_prefix": None,
        "override_match_prefix_len": 0,
        "spell_is_callable": callable_spell,
        "spell_is_existing_creation": False,
        "spell_has_disposal_methods": disposal,
    }


class TestInlinableShapeContract:
    """
    `row_inlinable_common_shape` returns uniform (param, key_tuple) pairs.
    """

    def test_single_dep_param_yields_one_tuple(self) -> None:
        """Single-dep params carry a 1-tuple of keys, never a bare key."""
        shape = row_inlinable_common_shape(
            _row("root", "many", [("solo", ["dep_a"])]),
        )
        assert shape == (("solo", (("dep_a", None),)),)

    def test_collection_param_is_inlinable(self) -> None:
        """Multi-dep (collection DI) params are inlinable with ordered keys."""
        shape = row_inlinable_common_shape(
            _row("root", "many", [("handlers", ["dep_a", "dep_b"])]),
        )
        assert shape == (("handlers", (("dep_a", None), ("dep_b", None))),)

    def test_zero_dep_param_is_omitted(self) -> None:
        """Zero-dep params are dropped, matching the generic kwargs builder."""
        shape = row_inlinable_common_shape(
            _row("root", "many", [("empty", []), ("solo", ["dep_a"])]),
        )
        assert shape == (("solo", (("dep_a", None),)),)

    def test_non_callable_row_is_not_inlinable(self) -> None:
        """Non-callable spells stay on the generic constructor path."""
        assert row_inlinable_common_shape(
            _row("root", "many", callable_spell=False),
        ) is None


class TestCollectionDIEmission:
    """
    Collection-DI params compile to order-preserving list literals.

    A captured `unique` row leads each graph, so the specializer emits every
    other row through the shared per-step emitters these tests pin.
    """

    def test_locals_mode_emits_list_literal(self) -> None:
        """Locals mode compiles collection params to direct local refs."""
        rows = (
            _row("u0", "unique"),
            _row("d1", "many"),
            _row("d2", "many"),
            _row("root", "many", [("handlers", ["d1", "d2"])]),
        )
        source = emit_specialized_step_plan_source(
            rows=rows,
            captured_step_indexes=(0,),
            root_instance_key=("root", None),
        )
        assert "handlers=[instance_1, instance_2]," in source
        assert "instance_results" not in source
        assert "_construct_spell_instance(plan_step" not in source

    def test_dict_mode_emits_flat_cursor_reads(self) -> None:
        """Dict mode compiles collection params via flattened dep-key reads."""
        rows = (
            _row("u0", "unique"),
            _row("d1", "many"),
            _row("d2", "many"),
            _row("odd", "many", callable_spell=False),
            _row("root", "many", [("handlers", ["d1", "d2"])]),
        )
        source = emit_specialized_step_plan_source(
            rows=rows,
            captured_step_indexes=(0,),
            root_instance_key=("root", None),
        )
        assert (
            "handlers=[instance_results[step_dep_keys_4[0]], "
            "instance_results[step_dep_keys_4[1]]],"
        ) in source


class TestSpecializationEmission:
    """
    Singleton warm-tail specialization emission contracts.
    """

    def test_capture_set_is_unique_only(self) -> None:
        """Only Existence.unique rows are ever selected for capture."""
        rows = (
            _row("u1", "unique"),
            _row("c1", "unique_per_conduit"),
            _row("m1", "many"),
            _row("s1", "unique_per_spell_space"),
        )
        assert select_specializable_step_indexes(rows) == (0,)

    def test_guard_prologue_and_capture_aliases(self) -> None:
        """Each captured step emits one epoch guard; reads become aliases."""
        rows = (
            _row("u1", "unique"),
            _row("u2", "unique"),
            _row("root", "many", [("a", ["u1"]), ("b", ["u2"])]),
        )
        source = emit_specialized_step_plan_source(
            rows=rows,
            captured_step_indexes=(0, 1),
            root_instance_key=("root", None),
        )
        assert "if cap_spell_0._door_epoch != cap_epoch_0:" in source
        assert "if cap_spell_1._door_epoch != cap_epoch_1:" in source
        # Deopt target is the stable `_deopt_notify` binding (bound to the
        # generic inner or the hydrator's 3-strike re-pin wrapper).
        assert source.count("return _deopt_notify(meld)") >= 2
        assert "instance_0 = cap_inst_0" in source
        assert "instance_1 = cap_inst_1" in source
        # Captured steps must emit ZERO store-walk work.
        assert "creations_0" not in source
        assert "creations_1" not in source

    def test_root_captured_collapses_to_return(self) -> None:
        """A captured root returns its slot directly with no alias."""
        source = emit_specialized_step_plan_source(
            rows=(_row("u1", "unique"),),
            captured_step_indexes=(0,),
            root_instance_key=("u1", None),
        )
        assert "return cap_inst_0" in source
        assert "instance_0 = cap_inst_0" not in source

    def test_captured_deps_inside_collection_literal(self) -> None:
        """Captured singletons compile directly into collection literals."""
        rows = (
            _row("u1", "unique"),
            _row("u2", "unique"),
            _row("root", "many", [("handlers", ["u1", "u2"])]),
        )
        source = emit_specialized_step_plan_source(
            rows=rows,
            captured_step_indexes=(0, 1),
            root_instance_key=("root", None),
        )
        assert "handlers=[instance_0, instance_1]," in source

    def test_empty_capture_set_raises(self) -> None:
        """Callers must skip specialization when nothing is capturable."""
        with pytest.raises(RuntimeError, match="non-empty capture set"):
            emit_specialized_step_plan_source(
                rows=(_row("m1", "many"),),
                captured_step_indexes=(),
                root_instance_key=("m1", None),
            )

    def test_non_unique_capture_raises(self) -> None:
        """Capture indexes referencing non-unique rows are rejected."""
        with pytest.raises(RuntimeError, match="Existence.unique"):
            emit_specialized_step_plan_source(
                rows=(_row("c1", "unique_per_conduit"),),
                captured_step_indexes=(0,),
                root_instance_key=("c1", None),
            )


class TestFactorySourceShareability:
    """
    Emitted sources stay identity-free so the factory cache can share shapes.
    """

    def test_same_shape_same_source(self) -> None:
        """Two same-shape spell sets emit byte-identical source."""
        rows_a = (
            _row("aaa", "unique"),
            _row("bbb", "many", [("dep", ["aaa"])]),
        )
        rows_b = (
            _row("xxx", "unique"),
            _row("yyy", "many", [("dep", ["xxx"])]),
        )
        source_a = emit_specialized_step_plan_source(
            rows=rows_a, captured_step_indexes=(0,),
            root_instance_key=("bbb", None))
        source_b = emit_specialized_step_plan_source(
            rows=rows_b, captured_step_indexes=(0,),
            root_instance_key=("yyy", None))
        assert source_a == source_b

    def test_different_capture_sets_differ(self) -> None:
        """Specialized sources differ per capture shape, never per identity."""
        rows = (
            _row("u1", "unique"),
            _row("u2", "unique"),
            _row("root", "many", [("a", ["u1"]), ("b", ["u2"])]),
        )
        both = emit_specialized_step_plan_source(
            rows=rows, captured_step_indexes=(0, 1),
            root_instance_key=("root", None))
        one = emit_specialized_step_plan_source(
            rows=rows, captured_step_indexes=(0,),
            root_instance_key=("root", None))
        assert both != one

    def test_specialized_factory_executes_and_deopts(self) -> None:
        """A specialized factory returns captured values and deopts on bump."""
        rows = (
            _row("u1", "unique"),
            _row("root", "many", [("a", ["u1"])]),
        )
        source = emit_specialized_step_plan_source(
            rows=rows, captured_step_indexes=(0,),
            root_instance_key=("root", None))
        cap_spell = SimpleNamespace(_door_epoch=7)
        root_spell = SimpleNamespace(spell=lambda a: ("root", a))
        deopt_calls = []

        def generic_inner(meld: Any) -> Any:
            deopt_calls.append(meld)
            return ("generic",)

        bindings = {
            "steps": (None, None),
            "step_spells": (None, root_spell),
            "step_spell_ids": ("u1", "root"),
            "step_disposal_methods": ((), ()),
            "step_existences": (None, None),
            "step_instance_keys": (("u1", None), ("root", None)),
            "step_dep_keys": ((), (("u1", None),)),
            "step_owner_creations": (None, None),
            "step_targets": (None, root_spell.spell),
            "root_instance_key": ("root", None),
            "cap_spell_0": cap_spell,
            "cap_epoch_0": 7,
            "cap_inst_0": "CAPTURED",
            "_generic_inner": generic_inner,
            # Deopt target binding: this manual-factory test binds it to the
            # generic inner directly, mirroring the no-notify default.
            "_deopt_notify": generic_inner,
        }
        factory_source = build_executor_factory_source(
            inner_source=source,
            binding_names=tuple(bindings.keys()),
            executor_name=SPECIALIZED_EXECUTOR_NAME,
        )
        factory = get_or_build_executor_factory(
            factory_source=factory_source,
            source_name="<test_specialized_factory>",
            static_namespace={
                "SpellGeneralizedCodegenPlanTargetKind": object,
                "_construct_spell_instance": lambda **kwargs: None,
                "_raise_meld_construction_error": lambda spell, exc: None,
                "_register_spell_instance_prebound": lambda **kwargs: None,
                "MeldExecutionError": RuntimeError,
                "SpellSpaceScopeError": RuntimeError,
            },
        )
        executor = factory(bindings)
        assert executor(object()) == ("root", "CAPTURED")
        assert not deopt_calls
        cap_spell._door_epoch = 8
        assert executor(object()) == ("generic",)
        assert deopt_calls


def _payload_row(
        spell_id: str,
        existence: str,
        deps: Sequence[Tuple[str, Sequence[str]]] = (),
        *,
        payload: Sequence[Tuple[str, Any]] = (),
        positional: Any = None,
        uses_positional: bool = False,
) -> Dict[str, Any]:
    """
    Build one synthetic manifest row carrying contract-call extras.
    """
    built = _row(spell_id, existence, deps)
    built["has_contract_payload"] = bool(payload)
    built["contract_payload_items"] = tuple(payload)
    built["contract_positional_override"] = positional
    built["uses_positional_override"] = uses_positional
    return built


class TestContractPayloadEmission:
    """
    Contract payloads and positional overrides compile to bound constants.
    """

    def test_payload_row_is_inlinable_and_payload_wins_collisions(self) -> None:
        """Payload names shadow same-named dep params (generic overwrite)."""
        built = _payload_row(
            "root", "many",
            deps=[("cfg", ["d1"]), ("dep", ["d1"])],
            payload=[("cfg", {"a": 1}), ("extra", 7)],
        )
        assert row_inlinable_common_shape(built) == (
            ("dep", (("d1", None),)),
        )
        assert _row_contract_call_extras(built) == (("cfg", "extra"), None)
        assert _row_contract_value_binding(built) == ({"a": 1}, 7)

    def test_positional_precedence_mirrors_generic_builder(self) -> None:
        """Payload __args__ overwrites the override unless uses_positional."""
        plain = _payload_row(
            "r", "many", payload=[("__args__", (1, 2))], positional=(9,),
        )
        assert _row_contract_call_extras(plain) == ((), (1, 2))
        pinned = _payload_row(
            "r", "many", payload=[("__args__", (1, 2))], positional=(9,),
            uses_positional=True,
        )
        assert _row_contract_call_extras(pinned) == ((), (9,))

    def test_non_sequence_positional_stays_on_generic_path(self) -> None:
        """Non tuple/list __args__ keeps per-call error timing: not inlinable."""
        built = _payload_row("r", "many", payload=[("__args__", 5)])
        assert _row_contract_call_extras(built) is None
        assert row_inlinable_common_shape(built) is None

    def test_payload_graph_reaches_locals_mode_with_bound_constants(self) -> None:
        """Payload + positional rows emit locals-mode splat/keyword constants."""
        rows = (
            _row("u0", "unique"),
            _row("d1", "many"),
            _payload_row(
                "root", "many", deps=[("dep", ["d1"])],
                payload=[("cfg", "CFGVAL")], positional=("P0",),
                uses_positional=True,
            ),
        )
        source = emit_specialized_step_plan_source(
            rows=rows, captured_step_indexes=(0,),
            root_instance_key=("root", None),
        )
        assert "instance_results" not in source
        assert "*positional_2," in source
        assert "cfg=contract_values_2[0]," in source
        assert "dep=instance_1," in source
        assert "positional_2 = step_positional_args[2]" in source
        assert "contract_values_2 = step_contract_values[2]" in source

    def test_payload_only_zero_dep_row_emits_keyword_call(self) -> None:
        """A zero-dep payload row calls with constants, not `target_0()`."""
        rows = (
            _row("u0", "unique"),
            _payload_row("solo_p", "many", payload=[("x", 42)]),
        )
        source = emit_specialized_step_plan_source(
            rows=rows, captured_step_indexes=(0,),
            root_instance_key=("solo_p", None),
        )
        assert "x=contract_values_1[0]," in source
        assert "target_1()" not in source

    def test_specialized_emitter_inlines_non_captured_payload_rows(self) -> None:
        """The specialized body compiles payload constants for live steps."""
        rows = (
            _row("u1", "unique"),
            _payload_row(
                "root", "many", deps=[("dep", ["u1"])],
                payload=[("cfg", "CFGVAL")],
            ),
        )
        source = emit_specialized_step_plan_source(
            rows=rows, captured_step_indexes=(0,),
            root_instance_key=("root", None),
        )
        assert "cfg=contract_values_1[0]," in source
        assert "contract_values_1 = step_contract_values[1]" in source
