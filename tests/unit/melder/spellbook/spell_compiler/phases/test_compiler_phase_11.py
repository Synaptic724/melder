"""Unit tests for current-surface compiler phase 11 helper behavior."""

from types import SimpleNamespace
from typing import Any, Optional, Sequence

import pytest

import melder.aether.spellbook.spell_compiler.phases.compiler_phase_11 as compiler_phase_11_module
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_11 import (
    CompilerPhase11,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_types.spell_types import SpellType


def _make_step(
        spell_id: str,
        **overrides: object,
) -> Any:
    """Build a minimal execution-plan step stub for phase 11 helper tests."""
    step = SimpleNamespace(
        instance_key=(spell_id, None),
        spell=SimpleNamespace(
            spell_index=SimpleNamespace(current=spell_id),
            is_existing_creation=False,
        ),
        existence=Existence.unique,
        dependency_keys=[(f"dep-{spell_id}", None)],
        has_contract_payload=False,
        contract_payload=None,
        contract_keys=("dep",),
        allow_list_aggregation=False,
        uses_positional_override=False,
        contract_positional_override=None,
        lock_hint="none",
        use_spell_lock_hint=False,
        requires_spellspace=False,
        owner_conduit_required=False,
        must_register=False,
        disposal_method_names=(),
        shared_instance=False,
        dependency_resolution_order=(("dep", ((f"{spell_id}-dep", None),)),),
        override_match_prefix=None,
        override_match_prefix_len=0,
        override_keys=("dep",),
        expects_overrides=False,
        creations_target_kind=1,
    )
    for field_name, value in overrides.items():
        setattr(step, field_name, value)
    return step


def _make_plan(
        *,
        plan_variant: str,
        root_spell_id: str,
        step_spell_ids: Sequence[str],
        root_instance_key: tuple[str, Optional[int]] | None = None,
) -> Any:
    """Build a minimal plan stub for phase 11 helper tests."""
    steps = tuple(_make_step(spell_id) for spell_id in step_spell_ids)
    return SimpleNamespace(
        plan_variant=plan_variant,
        root_spell_id=root_spell_id,
        root_instance_key=(root_spell_id, None) if root_instance_key is None else root_instance_key,
        steps=steps,
        spell_id_step_index={
            step.spell.spell_index.current: index
            for index, step in enumerate(steps)
        },
        fast_plan=None,
        fast_transient_plan=object(),
    )


@pytest.mark.parametrize(
    ("step_count", "max_depth", "max_dependency_count", "dispatch_route"),
    [
        (8, 3, 1, "FAST_TRANSIENT_TIER_0"),
        (16, 6, 8, "FAST_TRANSIENT_TIER_1"),
        (24, 8, 8, "FAST_TRANSIENT_TIER_2"),
        (32, 9, 10, "FAST_TRANSIENT_TIER_3"),
        (33, 9, 10, "ENGINE"),
    ],
)
def test_cache_execution_plan_metrics_assigns_dispatch_route_tiers(
        step_count: int,
        max_depth: int,
        max_dependency_count: int,
        dispatch_route: str,
) -> None:
    """Phase 11 should assign the documented dispatch tier thresholds."""
    phase = CompilerPhase11()
    spell = SimpleNamespace()
    artifact = SimpleNamespace(_occurrence_shape_profile_phase8={"max_occurrence_depth": max_depth})
    depths = {index: max_depth for index in range(step_count)}
    occurrence_plan = SimpleNamespace(
        occurrence_graph={
            ("spell-{0}".format(index), index): {}
            for index in range(step_count)
        },
        path_registry=SimpleNamespace(depth=lambda path_id: depths[path_id]),
    )

    steps = []
    for index in range(step_count):
        dependency_keys = [
            ("dep-{0}-{1}".format(index, dep_index), None)
            for dep_index in range(max_dependency_count)
        ]
        steps.append(
            _make_step(
                "spell-{0}".format(index),
                dependency_keys=dependency_keys,
                spell=SimpleNamespace(
                    spell_index=SimpleNamespace(current="spell-{0}".format(index)),
                    is_existing_creation=False,
                ),
            )
        )

    plan = SimpleNamespace(
        steps=tuple(steps),
        spell_id_step_index={
            step.instance_key[0]: index
            for index, step in enumerate(steps)
        },
        fast_plan=None,
        fast_transient_plan=object(),
    )

    phase._cache_execution_plan_metrics(
        spell,
        artifact,
        occurrence_plan=occurrence_plan,
        plan=plan,
    )

    assert artifact._execution_plan_step_count_phase11 == step_count
    assert artifact._execution_plan_max_occurrence_depth_phase11 == max_depth
    assert artifact._execution_plan_max_dependency_count_phase11 == max_dependency_count
    assert spell.execution_plan_dispatch_route == dispatch_route


def test_cache_execution_plan_metrics_records_calln_payload_and_existing_creation_flags() -> None:
    """Phase 11 should aggregate CALLN, payload, and existing-creation flags."""
    phase = CompilerPhase11()
    spell = SimpleNamespace()
    artifact = SimpleNamespace(_occurrence_shape_profile_phase8={"max_occurrence_depth": 1})
    occurrence_plan = SimpleNamespace(
        occurrence_graph={("root", 1): {}},
        path_registry=SimpleNamespace(depth=lambda path_id: 1),
    )
    steps = (
        _make_step(
            "root",
            has_contract_payload=True,
            dependency_keys=[("dep", None)],
            spell=SimpleNamespace(
                spell_index=SimpleNamespace(current="root"),
                is_existing_creation=True,
            ),
        ),
    )
    fast_plan = tuple([None] * 20 + [[compiler_phase_11_module.ExecutionPlanCallMode.CALLN]])
    plan = SimpleNamespace(
        steps=steps,
        spell_id_step_index={"root": 0},
        fast_plan=fast_plan,
        fast_transient_plan=object(),
    )

    phase._cache_execution_plan_metrics(
        spell,
        artifact,
        occurrence_plan=occurrence_plan,
        plan=plan,
    )

    assert artifact._execution_plan_has_calln_phase11 is True
    assert artifact._execution_plan_has_contract_payloads_phase11 is True
    assert artifact._execution_plan_has_existing_creations_phase11 is True
    assert spell.execution_plan_dispatch_route == "ENGINE"


def test_build_execution_plan_variant_delegates_to_builder(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 11 direct builder wrapper should instantiate ExecutionPlanBuilder with supplied inputs."""
    phase = CompilerPhase11()
    captured: dict[str, object] = {}
    expected_plan = object()

    class _ExecutionPlanBuilderStub:
        def __init__(
                self,
                *,
                occurrence_plan: object,
                injection_plan: object,
                spell_lookup: object,
                plan_variant: str,
        ) -> None:
            captured["occurrence_plan"] = occurrence_plan
            captured["injection_plan"] = injection_plan
            captured["spell_lookup"] = spell_lookup
            captured["plan_variant"] = plan_variant

        def build(self) -> object:
            return expected_plan

    monkeypatch.setattr(
        compiler_phase_11_module,
        "ExecutionPlanBuilder",
        _ExecutionPlanBuilderStub,
    )

    occurrence_plan = object()
    injection_plan = object()
    spell_lookup = {"root": object()}

    result = phase._build_execution_plan_variant(
        occurrence_plan=occurrence_plan,
        injection_plan=injection_plan,
        spell_lookup=spell_lookup,
        plan_variant=compiler_phase_11_module.ExecutionPlanVariant.OVERRIDES,
    )

    assert result is expected_plan
    assert captured == {
        "occurrence_plan": occurrence_plan,
        "injection_plan": injection_plan,
        "spell_lookup": spell_lookup,
        "plan_variant": compiler_phase_11_module.ExecutionPlanVariant.OVERRIDES,
    }


def test_run_reuses_cached_variant_set_when_input_signature_unchanged(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 11 should reuse the full cached variant set when the signature is unchanged."""
    phase = CompilerPhase11()
    spell = SimpleNamespace(is_existing_creation=False, resolution_complete=False)
    occurrence_plan = object()
    injection_plan = object()
    spell_lookup = {"root": object()}
    cached_no_overrides = object()
    cached_overrides = object()
    cached_mutations = object()
    cached_calls: list[tuple[str, Any]] = []
    artifact = SimpleNamespace(
        check_cleaned=lambda: None,
        _occurrence_plan_phase8=occurrence_plan,
        _injection_plan_phase9=injection_plan,
        _phase8_occurrence_plan_input_signature="phase8-sig",
        _phase9_injection_plan_input_signature="phase9-sig",
        _phase11_no_overrides_fast_key=(
            "phase8-sig",
            "phase9-sig",
            id(occurrence_plan),
            id(injection_plan),
            id(spell_lookup),
        ),
        _phase11_no_overrides_input_signature="same-sig",
        _execution_plan_phase11_no_overrides=cached_no_overrides,
        _execution_plan_phase11_overrides=cached_overrides,
        _execution_plan_phase11=cached_mutations,
        _phase8_11_codegen_ir_dirty=False,
    )
    spellbook = SimpleNamespace(_spell_id_pool=spell_lookup)

    monkeypatch.setattr(
        CompilerPhase11,
        "_build_phase11_no_overrides_input_signature",
        lambda self, **kwargs: (_ for _ in ()).throw(
            AssertionError("signature helper should not run")
        ),
    )
    monkeypatch.setattr(
        CompilerPhase11,
        "_build_execution_plan_variant",
        lambda self, **kwargs: (_ for _ in ()).throw(
            AssertionError("builder should not run")
        ),
    )
    monkeypatch.setattr(
        CompilerPhase11,
        "_cache_execution_plan_metrics",
        lambda self, spell, artifact, *, occurrence_plan, plan: cached_calls.append(
            ("cache", plan)
        ),
    )
    monkeypatch.setattr(
        CompilerPhase11,
        "_store_phase11_to_phase13_handoff",
        lambda self, spell, artifact, plan: cached_calls.append(("handoff", plan)),
    )

    phase.run(spell, artifact, spellbook)

    assert cached_calls == [
        ("cache", cached_no_overrides),
        ("handoff", cached_no_overrides),
    ]
    assert artifact._phase11_no_overrides_input_signature == "same-sig"
    assert artifact._phase8_11_codegen_ir_dirty is False


def test_run_rebuilds_no_overrides_plan_when_input_signature_changes(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 11 should rebuild the full variant set when the no-overrides signature drifts."""
    phase = CompilerPhase11()
    spell = SimpleNamespace(is_existing_creation=False, resolution_complete=False)
    occurrence_plan = object()
    injection_plan = object()
    spell_lookup = {"root": object()}
    built_no_overrides = object()
    built_overrides = object()
    built_mutations = object()
    build_variants: list[str] = []
    callbacks: list[tuple[str, Any]] = []
    artifact = SimpleNamespace(
        check_cleaned=lambda: None,
        _occurrence_plan_phase8=occurrence_plan,
        _injection_plan_phase9=injection_plan,
        _phase8_occurrence_plan_input_signature="phase8-sig",
        _phase9_injection_plan_input_signature="phase9-sig",
        _phase11_no_overrides_fast_key=None,
        _phase11_no_overrides_input_signature="old-sig",
        _execution_plan_phase11_no_overrides=None,
        _execution_plan_phase11_overrides=None,
        _execution_plan_phase11=None,
        _phase8_11_codegen_ir_dirty=False,
    )
    spellbook = SimpleNamespace(_spell_id_pool=spell_lookup)

    monkeypatch.setattr(
        CompilerPhase11,
        "_build_phase11_no_overrides_input_signature",
        lambda self, **kwargs: "new-sig",
    )

    def _build_variant(
            self,
            *,
            occurrence_plan,
            injection_plan,
            spell_lookup,
            plan_variant,
    ):
        build_variants.append(plan_variant)
        if plan_variant == compiler_phase_11_module.ExecutionPlanVariant.NO_OVERRIDES_FAST:
            return built_no_overrides
        if plan_variant == compiler_phase_11_module.ExecutionPlanVariant.OVERRIDES:
            return built_overrides
        return built_mutations

    monkeypatch.setattr(CompilerPhase11, "_build_execution_plan_variant", _build_variant)
    monkeypatch.setattr(
        CompilerPhase11,
        "_cache_execution_plan_metrics",
        lambda self, spell, artifact, *, occurrence_plan, plan: callbacks.append(("cache", plan)),
    )
    monkeypatch.setattr(
        CompilerPhase11,
        "_store_phase11_to_phase13_handoff",
        lambda self, spell, artifact, plan: callbacks.append(("handoff", plan)),
    )

    phase.run(spell, artifact, spellbook)

    assert build_variants == [
        compiler_phase_11_module.ExecutionPlanVariant.NO_OVERRIDES_FAST,
        compiler_phase_11_module.ExecutionPlanVariant.OVERRIDES,
        compiler_phase_11_module.ExecutionPlanVariant.OVERRIDES_WITH_MUTATIONS,
    ]
    assert artifact._phase11_no_overrides_input_signature == "new-sig"
    assert artifact._execution_plan_phase11_no_overrides is built_no_overrides
    assert artifact._execution_plan_phase11_overrides is built_overrides
    assert artifact._execution_plan_phase11 is built_mutations
    assert artifact._phase8_11_codegen_ir_dirty is True
    assert callbacks == [
        ("cache", built_no_overrides),
        ("handoff", built_no_overrides),
    ]


def test_run_reuses_no_overrides_plan_when_signature_unchanged_but_rebuilds_other_variants(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 11 should reuse the cached no-overrides plan while rebuilding sibling variants."""
    phase = CompilerPhase11()
    spell = SimpleNamespace(is_existing_creation=False, resolution_complete=False)
    occurrence_plan = object()
    injection_plan = object()
    spell_lookup = {"root": object()}
    cached_no_overrides = object()
    built_overrides = object()
    built_mutations = object()
    build_variants: list[str] = []
    callbacks: list[tuple[str, Any]] = []
    artifact = SimpleNamespace(
        check_cleaned=lambda: None,
        _occurrence_plan_phase8=occurrence_plan,
        _injection_plan_phase9=injection_plan,
        _phase8_occurrence_plan_input_signature="phase8-sig",
        _phase9_injection_plan_input_signature="phase9-sig",
        _phase11_no_overrides_fast_key=None,
        _phase11_no_overrides_input_signature="same-sig",
        _execution_plan_phase11_no_overrides=cached_no_overrides,
        _execution_plan_phase11_overrides=None,
        _execution_plan_phase11=None,
        _phase8_11_codegen_ir_dirty=False,
    )
    spellbook = SimpleNamespace(_spell_id_pool=spell_lookup)

    monkeypatch.setattr(
        CompilerPhase11,
        "_build_phase11_no_overrides_input_signature",
        lambda self, **kwargs: "same-sig",
    )

    def _build_variant(
            self,
            *,
            occurrence_plan,
            injection_plan,
            spell_lookup,
            plan_variant,
    ):
        build_variants.append(plan_variant)
        if plan_variant == compiler_phase_11_module.ExecutionPlanVariant.OVERRIDES:
            return built_overrides
        if plan_variant == compiler_phase_11_module.ExecutionPlanVariant.OVERRIDES_WITH_MUTATIONS:
            return built_mutations
        raise AssertionError("no-overrides variant should have been reused")

    monkeypatch.setattr(CompilerPhase11, "_build_execution_plan_variant", _build_variant)
    monkeypatch.setattr(
        CompilerPhase11,
        "_cache_execution_plan_metrics",
        lambda self, spell, artifact, *, occurrence_plan, plan: callbacks.append(("cache", plan)),
    )
    monkeypatch.setattr(
        CompilerPhase11,
        "_store_phase11_to_phase13_handoff",
        lambda self, spell, artifact, plan: callbacks.append(("handoff", plan)),
    )

    phase.run(spell, artifact, spellbook)

    assert build_variants == [
        compiler_phase_11_module.ExecutionPlanVariant.OVERRIDES,
        compiler_phase_11_module.ExecutionPlanVariant.OVERRIDES_WITH_MUTATIONS,
    ]
    assert artifact._execution_plan_phase11_no_overrides is cached_no_overrides
    assert artifact._execution_plan_phase11_overrides is built_overrides
    assert artifact._execution_plan_phase11 is built_mutations
    assert artifact._phase8_11_codegen_ir_dirty is True
    assert callbacks == [
        ("cache", cached_no_overrides),
        ("handoff", cached_no_overrides),
    ]


def test_run_stores_phase11_handoff_without_eager_phase8_11_flush(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 11 run should store phase13 handoff and leave phase8_11 export dirty."""
    phase = CompilerPhase11()
    spell = SimpleNamespace(is_existing_creation=False, resolution_complete=False)
    occurrence_plan = object()
    spell_lookup = {"root": object()}
    built_no_overrides = object()
    built_overrides = object()
    built_mutations = object()
    callbacks: list[tuple[str, Any]] = []
    flush_calls: list[str] = []
    artifact = SimpleNamespace(
        check_cleaned=lambda: None,
        _occurrence_plan_phase8=occurrence_plan,
        _injection_plan_phase9=object(),
        _phase8_occurrence_plan_input_signature=None,
        _phase9_injection_plan_input_signature=None,
        _phase11_no_overrides_fast_key=None,
        _phase11_no_overrides_input_signature=None,
        _execution_plan_phase11_no_overrides=None,
        _execution_plan_phase11_overrides=None,
        _execution_plan_phase11=None,
        _phase8_11_codegen_ir_dirty=False,
    )
    spellbook = SimpleNamespace(_spell_id_pool=spell_lookup)

    monkeypatch.setattr(
        CompilerPhase11,
        "_build_phase11_no_overrides_input_signature",
        lambda self, **kwargs: "sig-new",
    )

    def _build_variant(
            self,
            *,
            occurrence_plan,
            injection_plan,
            spell_lookup,
            plan_variant,
    ):
        if plan_variant == compiler_phase_11_module.ExecutionPlanVariant.NO_OVERRIDES_FAST:
            return built_no_overrides
        if plan_variant == compiler_phase_11_module.ExecutionPlanVariant.OVERRIDES:
            return built_overrides
        return built_mutations

    monkeypatch.setattr(CompilerPhase11, "_build_execution_plan_variant", _build_variant)
    monkeypatch.setattr(
        CompilerPhase11,
        "_cache_execution_plan_metrics",
        lambda self, spell, artifact, *, occurrence_plan, plan: callbacks.append(("cache", plan)),
    )
    monkeypatch.setattr(
        CompilerPhase11,
        "_store_phase11_to_phase13_handoff",
        lambda self, spell, artifact, plan: callbacks.append(("handoff", plan)),
    )
    monkeypatch.setattr(
        compiler_phase_11_module.SharedCompilerExecutions,
        "capture_phase8_11_codegen_ir_if_dirty",
        lambda artifact: flush_calls.append("flush"),
    )

    phase.run(spell, artifact, spellbook)

    assert flush_calls == []
    assert artifact._phase8_11_codegen_ir_dirty is True
    assert callbacks == [
        ("cache", built_no_overrides),
        ("handoff", built_no_overrides),
    ]


def test_run_builds_override_variants_separately_from_stripped_no_overrides_base(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 11 should build override-capable variants from source inputs, not from a stripped base."""
    phase = CompilerPhase11()
    spell = SimpleNamespace(is_existing_creation=False, resolution_complete=False)
    spell_lookup = {"root": object()}
    artifact = SimpleNamespace(
        check_cleaned=lambda: None,
        _occurrence_plan_phase8=object(),
        _injection_plan_phase9=object(),
        _phase8_occurrence_plan_input_signature=None,
        _phase9_injection_plan_input_signature=None,
        _phase11_no_overrides_fast_key=None,
        _phase11_no_overrides_input_signature=None,
        _execution_plan_phase11_no_overrides=None,
        _execution_plan_phase11_overrides=None,
        _execution_plan_phase11=None,
        _phase8_11_codegen_ir_dirty=False,
    )
    spellbook = SimpleNamespace(_spell_id_pool=spell_lookup)
    build_calls: list[str] = []

    monkeypatch.setattr(
        CompilerPhase11,
        "_build_phase11_no_overrides_input_signature",
        lambda self, **kwargs: None,
    )

    def _build_variant(
            self,
            *,
            occurrence_plan,
            injection_plan,
            spell_lookup,
            plan_variant,
    ):
        build_calls.append(plan_variant)
        return SimpleNamespace(
            root_spell_id="root",
            root_instance_key=("root", None),
            steps=[_make_step("root")],
            spell_id_step_index={"root": 0},
            optimistic_object_refs_by_spell_id={},
            available_param_by_spell_id={"root": 1},
            plan_variant=plan_variant,
            fast_transient_plan=None,
        )

    monkeypatch.setattr(CompilerPhase11, "_build_execution_plan_variant", _build_variant)
    monkeypatch.setattr(
        CompilerPhase11,
        "_cache_execution_plan_metrics",
        lambda self, spell, artifact, *, occurrence_plan, plan: None,
    )
    monkeypatch.setattr(
        CompilerPhase11,
        "_store_phase11_to_phase13_handoff",
        lambda self, spell, artifact, plan: None,
    )

    phase.run(spell, artifact, spellbook)

    assert build_calls == [
        compiler_phase_11_module.ExecutionPlanVariant.NO_OVERRIDES_FAST,
        compiler_phase_11_module.ExecutionPlanVariant.OVERRIDES,
        compiler_phase_11_module.ExecutionPlanVariant.OVERRIDES_WITH_MUTATIONS,
    ]
    assert artifact._execution_plan_phase11_no_overrides.plan_variant == compiler_phase_11_module.ExecutionPlanVariant.NO_OVERRIDES_FAST
    assert artifact._execution_plan_phase11_overrides.plan_variant == compiler_phase_11_module.ExecutionPlanVariant.OVERRIDES
    assert artifact._execution_plan_phase11.plan_variant == compiler_phase_11_module.ExecutionPlanVariant.OVERRIDES_WITH_MUTATIONS
    assert artifact._execution_plan_phase11_overrides.fast_transient_plan is None
    assert artifact._execution_plan_phase11.fast_transient_plan is None

