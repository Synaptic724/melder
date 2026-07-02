"""
Emission-contract tests for the generalized no-overrides lane.

Purpose:
    Pin the emitted-source contracts landed in patch lane
    `generalized_singleton_specialization_2026_07_01` so refactors cannot
    silently regress them:
    - singleton warm-tail specialization emission (guards, capture aliases,
      root-collapse, deopt tail-call),
    - collection-DI inlinable emission (list literals, flat-cursor dict mode),
    - transient-lane body shape (per-slot factory defaults, per-step handlers,
      no live bookkeeping),
    - factory-source shareability (identity-free emission).

These are source-shape and small-executor tests over synthetic manifest rows;
no Aether runtime, conjure, or live spells are involved.
"""

import threading
from types import SimpleNamespace
from typing import Any, Dict, Sequence, Tuple

import pytest

from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_manifest_no_overrides_compiler import (
    EXECUTOR_NAME,
    SPECIALIZED_EXECUTOR_NAME,
    emit_specialized_step_plan_source,
    emit_step_plan_source,
    row_inlinable_common_shape,
    select_specializable_step_indexes,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler import (
    _build_no_overrides_codegen_executor_source,
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
) -> Dict[str, Any]:
    """
    Build one synthetic manifest step row with the full required field set.
    """
    return {
        "spell_id": spell_id,
        "existence": existence,
        "instance_key": (spell_id, None),
        "dependency_resolution_order": tuple(
            (name, tuple((dep, None) for dep in dep_ids))
            for name, dep_ids in deps
        ),
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
    """

    def test_locals_mode_emits_list_literal(self) -> None:
        """Locals mode compiles collection params to direct local refs."""
        rows = (
            _row("d1", "many"),
            _row("d2", "many"),
            _row("root", "many", [("handlers", ["d1", "d2"])]),
        )
        source = emit_step_plan_source(
            rows=rows,
            root_instance_key=("root", None),
        )
        assert "handlers=[instance_0, instance_1]," in source
        assert "instance_results" not in source
        assert "_construct_spell_instance(plan_step" not in source

    def test_dict_mode_emits_flat_cursor_reads(self) -> None:
        """Dict mode compiles collection params via flattened dep-key reads."""
        rows = (
            _row("d1", "many"),
            _row("d2", "many"),
            _row("odd", "many", callable_spell=False),
            _row("root", "many", [("handlers", ["d1", "d2"])]),
        )
        source = emit_step_plan_source(
            rows=rows,
            root_instance_key=("root", None),
        )
        assert (
            "handlers=[instance_results[step_dep_keys_3[0]], "
            "instance_results[step_dep_keys_3[1]]],"
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
        assert source.count("return _generic_inner(meld)") >= 2
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


class TestTransientBodyContract:
    """
    Transient (all-many unrolled) executor body shape contracts.
    """

    @staticmethod
    def _schema(step_count: int, root_index: int, call_modes: Tuple[int, ...],
                **dep_overrides: Tuple[int, ...]) -> Dict[str, Any]:
        """Build one normalized transient schema with zeroed dep arrays."""
        fields = [
            "dep1", "dep2a", "dep2b", "dep3a", "dep3b", "dep3c", "dep4a",
            "dep4b", "dep4c", "dep4d", "dep5a", "dep5b", "dep5c", "dep5d",
            "dep5e", "dep6a", "dep6b", "dep6c", "dep6d", "dep6e", "dep6f",
            "dep7a", "dep7b", "dep7c", "dep7d", "dep7e", "dep7f", "dep7g",
            "dep8a", "dep8b", "dep8c", "dep8d", "dep8e", "dep8f", "dep8g",
            "dep8h",
        ]
        schema: Dict[str, Any] = {
            "step_count": step_count,
            "root_step_index": root_index,
            "call_modes": call_modes,
        }
        for field_name in fields:
            schema[field_name] = dep_overrides.get(
                field_name,
                tuple(0 for _ in range(step_count)),
            )
        return schema

    def test_targets_bind_as_per_slot_defaults(self) -> None:
        """Constructor targets ride per-slot defaults, not per-call loads."""
        source = _build_no_overrides_codegen_executor_source(
            transient_schema=self._schema(2, 1, (0, 1), dep1=(0, 0)),
        )
        assert source is not None
        assert "t0=transient_targets[0]," in source
        assert "t1=transient_targets[1]," in source
        assert "t0 = transient_targets[0]" not in source

    def test_no_live_step_bookkeeping(self) -> None:
        """The happy path carries no per-step index bookkeeping stores."""
        source = _build_no_overrides_codegen_executor_source(
            transient_schema=self._schema(2, 1, (0, 1), dep1=(0, 0)),
        )
        assert source is not None
        assert "__step_index" not in source

    def test_per_step_handlers_attribute_constant_steps(self) -> None:
        """Each step owns a handler naming its constant step index."""
        source = _build_no_overrides_codegen_executor_source(
            transient_schema=self._schema(2, 1, (0, 1), dep1=(0, 0)),
        )
        assert source is not None
        assert source.count("except Exception as exc:") == 2
        assert "steps[0].spell" in source
        assert "steps[1].spell" in source


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
        source_a = emit_step_plan_source(
            rows=rows_a, root_instance_key=("bbb", None))
        source_b = emit_step_plan_source(
            rows=rows_b, root_instance_key=("yyy", None))
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
