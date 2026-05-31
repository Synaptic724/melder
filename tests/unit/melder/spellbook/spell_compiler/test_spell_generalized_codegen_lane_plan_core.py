"""Unit tests for the generalized codegen lane-plan core objects and helpers."""

from types import SimpleNamespace
from typing import Any

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_injection_analysis import (
    SpellInjectionInstanceSpec,
    SpellInjectionParamSource,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.data.spell_generalized_codegen_lane_plan import (
    SpellGeneralizedCodegenLanePlan,
    SpellGeneralizedCodegenPlanBuilder,
    SpellGeneralizedCodegenPlanCallMode,
    SpellGeneralizedCodegenPlanStep,
    SpellGeneralizedCodegenPlanTargetKind,
)


def _make_step() -> SpellGeneralizedCodegenPlanStep:
    """Build one minimal generalized lane-plan step."""
    return SpellGeneralizedCodegenPlanStep(
        instance_key=("root", None),
        occurrence=("root", 0),
        spell=object(),
        existence=Existence.unique_per_conduit,
        creations_target_kind=SpellGeneralizedCodegenPlanTargetKind.CALLER,
        shared_instance=True,
        inject_spec=None,
        dependency_keys=[],
        dependency_keys_by_param={},
        dependency_resolution_order=[],
        override_keys=[],
        override_match_prefix=None,
        override_match_prefix_len=0,
        expects_overrides=False,
        contract_keys=[],
        allow_list_aggregation=False,
        uses_positional_override=False,
        contract_payload=None,
        contract_positional_override=None,
        has_contract_payload=False,
        lock_hint="creations_lock",
        use_spell_lock_hint=False,
        requires_spellspace=False,
        owner_conduit_required=False,
        must_register=False,
        disposal_method_names=[],
    )


def test_generalized_codegen_plan_step_exposes_runtime_relevant_fields() -> None:
    """The generalized step object should preserve the old execution-step surface through properties."""
    inject_spec = SpellInjectionInstanceSpec(
        param_sources={
            "svc": SpellInjectionParamSource(
                kind="dependency",
                dependency_keys=(("dep", None),),
                override_key="svc",
                contract_key="svc",
            )
        },
        allow_list_aggregation=False,
        uses_positional_override=False,
        contract_payload={"cfg": "value"},
    )
    step = SpellGeneralizedCodegenPlanStep(
        instance_key=("root", None),
        occurrence=("root", 0),
        spell=object(),
        existence=Existence.unique_per_conduit,
        creations_target_kind=SpellGeneralizedCodegenPlanTargetKind.CALLER,
        shared_instance=True,
        inject_spec=inject_spec,
        dependency_keys=[("dep", None)],
        dependency_keys_by_param={"svc": [("dep", None)]},
        dependency_resolution_order=[("svc", [("dep", None)])],
        override_keys=["svc"],
        override_match_prefix=0,
        override_match_prefix_len=1,
        expects_overrides=True,
        contract_keys=["svc"],
        allow_list_aggregation=False,
        uses_positional_override=False,
        contract_payload={"cfg": "value"},
        contract_positional_override=None,
        has_contract_payload=True,
        lock_hint="creations_lock",
        use_spell_lock_hint=False,
        requires_spellspace=False,
        owner_conduit_required=False,
        must_register=True,
        disposal_method_names=["cleanup"],
    )

    assert step.instance_key == ("root", None)
    assert step.occurrence == ("root", 0)
    assert step.existence is Existence.unique_per_conduit
    assert step.creations_target_kind == SpellGeneralizedCodegenPlanTargetKind.CALLER
    assert step.shared_instance is True
    assert step.inject_spec is inject_spec
    assert step.dependency_keys == [("dep", None)]
    assert step.dependency_keys_by_param == {"svc": [("dep", None)]}
    assert step.dependency_resolution_order == [("svc", [("dep", None)])]
    assert step.override_keys == ["svc"]
    assert step.override_match_prefix == 0
    assert step.override_match_prefix_len == 1
    assert step.expects_overrides is True
    assert step.contract_keys == ["svc"]
    assert step.allow_list_aggregation is False
    assert step.uses_positional_override is False
    assert step.contract_payload == {"cfg": "value"}
    assert step.contract_positional_override is None
    assert step.has_contract_payload is True
    assert step.lock_hint == "creations_lock"
    assert step.use_spell_lock_hint is False
    assert step.requires_spellspace is False
    assert step.owner_conduit_required is False
    assert step.must_register is True
    assert step.disposal_method_names == ["cleanup"]


def test_generalized_codegen_lane_plan_cleanup_releases_owned_collections() -> None:
    """The generalized lane-plan container should cleanup the retained list/dict payloads it owns."""
    lane_plan = SpellGeneralizedCodegenLanePlan(
        lane_id="no_overrides",
        root_spell_id="root",
        root_instance_key=("root", None),
        steps=[_make_step()],
        spell_id_step_index={"root": 0},
        optimistic_object_refs_by_spell_id={"root": object()},
        available_param_by_spell_id={"root": 1},
        fast_dep_indices=[1],
        fast_param_group_names=["svc"],
        fast_param_group_dep_offsets=[0],
        fast_param_group_dep_counts=[1],
        fast_param_group_offsets=[0],
        fast_param_group_counts=[1],
        fast_use_positional=[False],
        fast_contract_payload_items=[None],
        fast_contract_positional_args=[None],
        fast_instance_keys=[("root", None)],
        fast_creations_target_kinds=[1],
        fast_existence=[Existence.unique_per_conduit],
        fast_must_register=[False],
        fast_set_result_flags=[False],
        fast_spells=[object()],
        fast_call_targets=[object()],
        fast_existing_objects=[None],
        fast_is_existing_creation=[False],
        fast_is_callable=[True],
        fast_root_step_index=0,
        fast_call_modes=[SpellGeneralizedCodegenPlanCallMode.CALL0],
        fast_single_dep_indices=[-1],
        fast_call2_dep_indices_a=[-1],
        fast_call2_dep_indices_b=[-1],
        fast_call3_dep_indices_a=[-1],
        fast_call3_dep_indices_b=[-1],
        fast_call3_dep_indices_c=[-1],
        fast_call4_dep_indices_a=[-1],
        fast_call4_dep_indices_b=[-1],
        fast_call4_dep_indices_c=[-1],
        fast_call4_dep_indices_d=[-1],
        fast_call5_dep_indices_a=[-1],
        fast_call5_dep_indices_b=[-1],
        fast_call5_dep_indices_c=[-1],
        fast_call5_dep_indices_d=[-1],
        fast_call5_dep_indices_e=[-1],
        fast_call6_dep_indices_a=[-1],
        fast_call6_dep_indices_b=[-1],
        fast_call6_dep_indices_c=[-1],
        fast_call6_dep_indices_d=[-1],
        fast_call6_dep_indices_e=[-1],
        fast_call6_dep_indices_f=[-1],
        fast_call7_dep_indices_a=[-1],
        fast_call7_dep_indices_b=[-1],
        fast_call7_dep_indices_c=[-1],
        fast_call7_dep_indices_d=[-1],
        fast_call7_dep_indices_e=[-1],
        fast_call7_dep_indices_f=[-1],
        fast_call7_dep_indices_g=[-1],
        fast_call8_dep_indices_a=[-1],
        fast_call8_dep_indices_b=[-1],
        fast_call8_dep_indices_c=[-1],
        fast_call8_dep_indices_d=[-1],
        fast_call8_dep_indices_e=[-1],
        fast_call8_dep_indices_f=[-1],
        fast_call8_dep_indices_g=[-1],
        fast_call8_dep_indices_h=[-1],
        fast_transient_plan=None,
        fast_has_contract_payloads=False,
        fast_has_existing_creations=False,
        metadata={"selected_strategy_id": "generalized_codegen_plan"},
    )

    lane_plan.cleanup()

    assert not hasattr(lane_plan, "_steps")
    assert not hasattr(lane_plan, "_metadata")


def test_generalized_codegen_plan_builder_helper_methods_port_execution_plan_semantics() -> None:
    """The lane-plan builder helper methods should preserve old execution-plan routing semantics."""
    assert SpellGeneralizedCodegenPlanBuilder._creation_target_for_existence(
        Existence.unique
    ) == SpellGeneralizedCodegenPlanTargetKind.OWNER
    assert SpellGeneralizedCodegenPlanBuilder._creation_target_for_existence(
        Existence.unique_per_conduit
    ) == SpellGeneralizedCodegenPlanTargetKind.CALLER
    assert SpellGeneralizedCodegenPlanBuilder._creation_target_for_existence(
        Existence.unique_per_spell_space
    ) == SpellGeneralizedCodegenPlanTargetKind.SPELLSPACE
    assert SpellGeneralizedCodegenPlanBuilder._creation_target_for_existence(
        Existence.many
    ) == SpellGeneralizedCodegenPlanTargetKind.CALLER

    assert SpellGeneralizedCodegenPlanBuilder._lock_hint_for_existence(
        Existence.unique
    ) == "spell_lock"
    assert SpellGeneralizedCodegenPlanBuilder._lock_hint_for_existence(
        Existence.unique_per_conduit
    ) == "creations_lock"
    assert SpellGeneralizedCodegenPlanBuilder._lock_hint_for_existence(
        Existence.many
    ) == "creations_lock"

    assert SpellGeneralizedCodegenPlanBuilder._should_register(
        type(
            "RuntimeRecordProbe",
            (),
            {
                "existence": Existence.many,
                "has_disposal_methods": False,
            },
        )()
    ) is False
    assert SpellGeneralizedCodegenPlanBuilder._should_register(
        type(
            "RuntimeRecordProbe",
            (),
            {
                "existence": Existence.many,
                "has_disposal_methods": True,
            },
        )()
    ) is True


def test_generalized_codegen_plan_builder_extracts_param_keys_from_injection_specs() -> None:
    """The lane-plan builder should flatten dependency, override, and contract keys from injection specs."""
    inject_spec = SpellInjectionInstanceSpec(
        param_sources={
            "svc": SpellInjectionParamSource(
                kind="dependency",
                dependency_keys=(("dep", None),),
                override_key="svc",
                contract_key="svc",
            ),
            "cfg": SpellInjectionParamSource(
                kind="contract",
                dependency_keys=(),
                override_key="cfg",
                contract_key="cfg",
            ),
        },
        allow_list_aggregation=False,
        uses_positional_override=False,
        contract_payload={"cfg": "payload"},
    )

    dependency_keys, dependency_keys_by_param, override_keys, contract_keys = (
        SpellGeneralizedCodegenPlanBuilder._extract_param_keys(inject_spec)
    )
    no_override_dependency_keys, no_override_dependency_keys_by_param = (
        SpellGeneralizedCodegenPlanBuilder._extract_param_keys_no_overrides(
            inject_spec
        )
    )

    assert dependency_keys == [("dep", None)]
    assert dependency_keys_by_param == {
        "svc": [("dep", None)],
        "cfg": [],
    } or dependency_keys_by_param == {
        "svc": [("dep", None)],
    }
    assert override_keys == ["svc", "cfg"]
    assert contract_keys == ["svc", "cfg"]
    assert no_override_dependency_keys == [("dep", None)]
    assert no_override_dependency_keys_by_param == {
        "svc": [("dep", None)],
    } or no_override_dependency_keys_by_param == {
        "svc": [("dep", None)],
        "cfg": [],
    }


def test_generalized_codegen_plan_builder_occurrence_resolution_uses_canonical_occurrence_for_shared_keys() -> None:
    """The generalized lane builder should recover shared occurrences through canonical occurrence lookup."""
    builder = SpellGeneralizedCodegenPlanBuilder(
        state=SimpleNamespace(
            instance_shape=SimpleNamespace(
                canonical_occurrences_by_spell_id={"root": ("root", 7)},
            )
        ),
        plan_variant="no_overrides",
    )

    assert builder._occurrence_for_instance_key(("root", None)) == ("root", 7)
    assert builder._occurrence_for_instance_key(("dep", 4)) == ("dep", 4)


def test_generalized_codegen_plan_builder_fast_transient_plan_rejects_incompatible_steps() -> None:
    """The transient fast-plan helper should reject non-transient or unsupported call-mode inputs."""
    many_callable_step = SimpleNamespace()
    not_many = SpellGeneralizedCodegenPlanBuilder(
        state=object(),
        plan_variant="no_overrides",
    )._build_fast_transient_plan(
        steps=[many_callable_step],
        fast_call_targets=[object()],
        fast_existence=[Existence.unique],
        fast_must_register=[False],
        fast_is_existing_creation=[False],
        fast_is_callable=[True],
        fast_call_modes=[SpellGeneralizedCodegenPlanCallMode.CALL0],
        fast_single_dep_indices=[-1],
        fast_call2_dep_indices_a=[-1],
        fast_call2_dep_indices_b=[-1],
        fast_call3_dep_indices_a=[-1],
        fast_call3_dep_indices_b=[-1],
        fast_call3_dep_indices_c=[-1],
        fast_call4_dep_indices_a=[-1],
        fast_call4_dep_indices_b=[-1],
        fast_call4_dep_indices_c=[-1],
        fast_call4_dep_indices_d=[-1],
        fast_call5_dep_indices_a=[-1],
        fast_call5_dep_indices_b=[-1],
        fast_call5_dep_indices_c=[-1],
        fast_call5_dep_indices_d=[-1],
        fast_call5_dep_indices_e=[-1],
        fast_call6_dep_indices_a=[-1],
        fast_call6_dep_indices_b=[-1],
        fast_call6_dep_indices_c=[-1],
        fast_call6_dep_indices_d=[-1],
        fast_call6_dep_indices_e=[-1],
        fast_call6_dep_indices_f=[-1],
        fast_call7_dep_indices_a=[-1],
        fast_call7_dep_indices_b=[-1],
        fast_call7_dep_indices_c=[-1],
        fast_call7_dep_indices_d=[-1],
        fast_call7_dep_indices_e=[-1],
        fast_call7_dep_indices_f=[-1],
        fast_call7_dep_indices_g=[-1],
        fast_call8_dep_indices_a=[-1],
        fast_call8_dep_indices_b=[-1],
        fast_call8_dep_indices_c=[-1],
        fast_call8_dep_indices_d=[-1],
        fast_call8_dep_indices_e=[-1],
        fast_call8_dep_indices_f=[-1],
        fast_call8_dep_indices_g=[-1],
        fast_call8_dep_indices_h=[-1],
        root_step_index=0,
    )
    calln = SpellGeneralizedCodegenPlanBuilder(
        state=object(),
        plan_variant="no_overrides",
    )._build_fast_transient_plan(
        steps=[many_callable_step],
        fast_call_targets=[object()],
        fast_existence=[Existence.many],
        fast_must_register=[False],
        fast_is_existing_creation=[False],
        fast_is_callable=[True],
        fast_call_modes=[SpellGeneralizedCodegenPlanCallMode.CALLN],
        fast_single_dep_indices=[-1],
        fast_call2_dep_indices_a=[-1],
        fast_call2_dep_indices_b=[-1],
        fast_call3_dep_indices_a=[-1],
        fast_call3_dep_indices_b=[-1],
        fast_call3_dep_indices_c=[-1],
        fast_call4_dep_indices_a=[-1],
        fast_call4_dep_indices_b=[-1],
        fast_call4_dep_indices_c=[-1],
        fast_call4_dep_indices_d=[-1],
        fast_call5_dep_indices_a=[-1],
        fast_call5_dep_indices_b=[-1],
        fast_call5_dep_indices_c=[-1],
        fast_call5_dep_indices_d=[-1],
        fast_call5_dep_indices_e=[-1],
        fast_call6_dep_indices_a=[-1],
        fast_call6_dep_indices_b=[-1],
        fast_call6_dep_indices_c=[-1],
        fast_call6_dep_indices_d=[-1],
        fast_call6_dep_indices_e=[-1],
        fast_call6_dep_indices_f=[-1],
        fast_call7_dep_indices_a=[-1],
        fast_call7_dep_indices_b=[-1],
        fast_call7_dep_indices_c=[-1],
        fast_call7_dep_indices_d=[-1],
        fast_call7_dep_indices_e=[-1],
        fast_call7_dep_indices_f=[-1],
        fast_call7_dep_indices_g=[-1],
        fast_call8_dep_indices_a=[-1],
        fast_call8_dep_indices_b=[-1],
        fast_call8_dep_indices_c=[-1],
        fast_call8_dep_indices_d=[-1],
        fast_call8_dep_indices_e=[-1],
        fast_call8_dep_indices_f=[-1],
        fast_call8_dep_indices_g=[-1],
        fast_call8_dep_indices_h=[-1],
        root_step_index=0,
    )

    assert not_many is None
    assert calln is None
