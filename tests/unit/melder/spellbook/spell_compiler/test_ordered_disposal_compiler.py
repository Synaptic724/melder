"""Ordered disposal references through real processors, planners, and emitted executors."""

import marshal
from threading import RLock
from types import SimpleNamespace

import pytest

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_runtime_processor_strategy import (
    SpellRuntimeProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.data.many_only_codegen_plan import (
    ManyOnlyCodegenPlanBuilder,
    ManyOnlyCodegenPlanVariant,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.data.spell_generalized_codegen_lane_plan import (
    SpellGeneralizedCodegenPlanBuilder,
    SpellGeneralizedCodegenPlanVariant,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation_cache import (
    _build_inner_no_overrides_executor,
    _build_no_overrides_subpackage,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_schema_helpers import (
    CodegenCreationSchemaHelpers,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_codegen_creation_helpers import (
    ManyOnlyCodegenCreationHelpers,
)
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler as generalized_no
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_overrides_codegen_creation_compiler as generalized_overrides
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers.many_only_no_overrides_codegen_creation_compiler as many_no
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers.many_only_overrides_codegen_creation_compiler as many_overrides
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.compilers.solo_no_overrides_codegen_creation_compiler as solo_no
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.compilers.solo_overrides_codegen_creation_compiler as solo_overrides
from tests.unit.melder.spellbook.spell_compiler.codegen_planner.test_generalized_dual_build_differential import (
    make_model,
    spec,
)
from tests.unit.melder.spellbook.spell_compiler.test_codegen_creation_compilers_core import (
    _make_recording_creations,
    _make_spell,
    _meld_for,
)


def _spell(spell_id: str, names: list[str]) -> SimpleNamespace:
    """Supply the existing compiler test double with an established, directly retained list."""
    spell = _make_spell(spell_id)

    def target(value: str = "base") -> str:
        """Expose the invoked target and optional override through the returned value."""
        return f"{spell_id}:{value}"

    spell.spell = target
    spell.requirements = None
    spell.disposal_method_names = names
    spell.has_disposal_methods = bool(names)
    return spell


def _model(names: list[str]) -> tuple[SimpleNamespace, dict[str, SimpleNamespace]]:
    """Build minimal model inputs around independent test Spells, then run the real processor."""
    pool = {
        "leaf": _spell("leaf", list(names)),
        "root": _spell("root", list(names)),
    }
    model = make_model(
        records={},
        keys_by_spell={"leaf": [("leaf", None)], "root": [("root", None)]},
        specs_by_key={("leaf", None): spec(), ("root", None): spec()},
        order=["leaf", "root"],
        root_key=("root", None),
        canonical={"leaf": ("leaf", 0), "root": ("root", 0)},
    )
    model.spell_runtime_shape = None
    model.existence_occurrence_shape = SimpleNamespace(
        total_spell_count=2, existence_counts=[(Existence.many, 2)],
    )
    pool["root"]._spellbook = SimpleNamespace(_spell_id_pool=pool)
    SpellRuntimeProcessorStrategy().process(pool["root"], SimpleNamespace(), model)
    return model, pool


@pytest.mark.parametrize("names", [[], ["stop", "flush", "close"]])
@pytest.mark.parametrize("family", ["single_no", "single_overrides", "dual", "many_only"])
def test_processor_and_plans_retain_ordered_spell_lists(names: list[str], family: str) -> None:
    """Every plan variant retains the established list, and outer cleanup leaves its contents intact."""
    model, pool = _model(names)
    plans = []
    try:
        for spell_id, spell in pool.items():
            record = model.spell_runtime_shape.records_by_spell_id[spell_id]
            assert record.disposal_method_names == names
            assert record.disposal_method_names is spell.disposal_method_names
        if family == "many_only":
            plans.append(ManyOnlyCodegenPlanBuilder(
                state=model, plan_variant=ManyOnlyCodegenPlanVariant.NO_OVERRIDES,
            ).build())
            for step, methods in zip(plans[0].steps, plans[0].step_disposal_methods):
                assert methods == names
                assert methods is step.spell.disposal_method_names
            assert plans[0].step_has_disposal_methods == (bool(names), bool(names))
        else:
            builder = SpellGeneralizedCodegenPlanBuilder(
                state=model,
                plan_variant=(SpellGeneralizedCodegenPlanVariant.OVERRIDES
                              if family == "single_overrides"
                              else SpellGeneralizedCodegenPlanVariant.NO_OVERRIDES),
            )
            plans.extend(builder.build_dual() if family == "dual" else [builder.build()])
            for plan in plans:
                for step in plan.steps:
                    assert step.disposal_method_names == names
                    assert step.disposal_method_names is step.spell.disposal_method_names
                    assert step.must_register is bool(names)
    finally:
        for plan in plans:
            plan.cleanup()
        model.spell_runtime_shape.cleanup()
    assert pool["leaf"].disposal_method_names == names
    assert pool["root"].disposal_method_names == names


@pytest.mark.parametrize("overrides", [False, True])
@pytest.mark.parametrize("route", [
    "many", "unique", "unique_per_conduit", "unique_per_spell_space",
    "unique_per_conduit_lineage", "unique_per_conduit_cluster",
])
def test_solo_registration_retains_names_across_code_cache_reuse(route: str, overrides: bool) -> None:
    """Emitted registration receives each live list even when the same compiled code is reused."""
    code_objects = []
    for spell_id, names in (
        ("first", ["stop", "flush", "close"]),
        ("second", ["close", "stop", "flush"]),
    ):
        spell = _spell(spell_id, names)
        store = _make_recording_creations()
        spell._owner_creations = store
        if overrides:
            executor, code = solo_overrides.compile_solo_overrides_codegen_creation_executor(
                spell=spell, solo_emit_key=route, return_compiled_code_object=True,
            )
            result = executor(_meld_for(store), {"value": "override"})
        else:
            executor, code = solo_no.compile_solo_no_overrides_codegen_creation_executor(
                spell=spell, solo_emit_key=route, fast_transient_no_overrides_enabled=False,
                return_compiled_code_object=True,
            )
            result = executor(_meld_for(store))
        code_objects.append(code)
        assert result == f"{spell_id}:{'override' if overrides else 'base'}"
        calls = store.add_many_calls if route == "many" else store.add_creation_calls
        assert len(calls) == 1
        assert calls[0][0] == (spell_id, result)
        assert calls[0][1]["has_disposal_methods"] is True
        assert calls[0][1]["disposal_methods"] == names
        assert calls[0][1]["disposal_methods"] is names
    assert code_objects[0] is code_objects[1]


@pytest.mark.parametrize("family", ["generalized", "many_only"])
@pytest.mark.parametrize("overrides", [False, True])
def test_family_executors_register_current_lists(family: str, overrides: bool) -> None:
    """Both non-solo families and override lanes register exact live lists across repeated compilation."""
    for _ in range(2):
        names = ["stop", "flush", "close"]
        model, pool = _model(names)
        plan = None
        try:
            if family == "many_only":
                plan = ManyOnlyCodegenPlanBuilder(
                    state=model,
                    plan_variant=(ManyOnlyCodegenPlanVariant.OVERRIDES if overrides
                                  else ManyOnlyCodegenPlanVariant.NO_OVERRIDES),
                ).build()
                compiler = many_overrides if overrides else many_no
            else:
                plan = SpellGeneralizedCodegenPlanBuilder(
                    state=model,
                    plan_variant=(SpellGeneralizedCodegenPlanVariant.OVERRIDES if overrides
                                  else SpellGeneralizedCodegenPlanVariant.NO_OVERRIDES),
                ).build()
                compiler = generalized_overrides if overrides else generalized_no
            if overrides:
                executor = compiler.compile_overrides_codegen_creation_executor(
                    execution_plan=plan, override_targets_by_spell_id={},
                    any_overrides_present=False, path_registry=model.graph_shape.path_registry,
                    plan_rows=(
                        [ManyOnlyCodegenCreationHelpers.build_override_step_row(step) for step in plan.steps]
                        if family == "many_only" else None
                    ),
                    root_spell_id="root", spell_lookup=pool,
                )
            else:
                executor = compiler.compile_no_overrides_codegen_creation_executor_from_plan(plan=plan)
            store = _make_recording_creations()
            # The generic override executor uses the real store's lock contract.
            store._lock = RLock()
            result = executor(_meld_for(store), {}, None) if overrides else executor(_meld_for(store))
            assert result == "root:base"
            assert [args[0] for args, _kwargs in store.add_many_calls] == ["leaf", "root"]
            for args, kwargs in store.add_many_calls:
                assert kwargs["disposal_methods"] == names
                assert kwargs["disposal_methods"] is pool[args[0]].disposal_method_names
        finally:
            if plan is not None:
                plan.cleanup()
            model.spell_runtime_shape.cleanup()


def test_serialized_cache_preserves_order_and_rebinds_live_lists() -> None:
    """A marshal-safe cache keeps ordered values, while stored-code hydration binds fresh live lists."""
    names = ["stop", "flush", "close"]
    model, pool = _model(names)
    plan = SpellGeneralizedCodegenPlanBuilder(
        state=model, plan_variant=SpellGeneralizedCodegenPlanVariant.NO_OVERRIDES,
    ).build()
    try:
        rows = CodegenCreationSchemaHelpers.get_phase11_step_ir_rows(
            plan, include_override_metadata=False,
        )
        assert [row["disposal_method_names"] for row in rows] == [tuple(names), tuple(names)]
        package = marshal.loads(marshal.dumps({
            "no_overrides": _build_no_overrides_subpackage(no_overrides_plan=plan),
        }))
        fresh_pool = {spell_id: _spell(spell_id, list(names)) for spell_id in pool}
        fresh_pool["root"]._spellbook = SimpleNamespace(_spell_id_pool=fresh_pool)
        executor = _build_inner_no_overrides_executor(fresh_pool["root"], package)
        store = _make_recording_creations()
        assert executor(_meld_for(store)) == "root:base"
        assert len(store.add_many_calls) == 2
        for args, kwargs in store.add_many_calls:
            assert kwargs["disposal_methods"] == names
            assert kwargs["disposal_methods"] is fresh_pool[args[0]].disposal_method_names
            assert kwargs["disposal_methods"] is not pool[args[0]].disposal_method_names
    finally:
        plan.cleanup()
        model.spell_runtime_shape.cleanup()
