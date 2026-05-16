from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple

import pytest

from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.blueprints.execution_plan import (
    ExecutionPlan,
    ExecutionPlanBuilder,
    ExecutionPlanCallMode,
    ExecutionPlanStep,
    ExecutionPlanTargetKind,
    ExecutionPlanVariant,
)
from melder.spellbook.spell_crafter.blueprints.injection_plan import (
    InjectionSpec,
    ParamSource,
)


class _PathRegistryStub:
    """
    Purpose:
        Provide the minimal path-registry surface needed by ExecutionPlanBuilder.
    Contract:
        - depth(...) returns configured values.
        - Missing path ids default to zero depth.
    """

    def __init__(self, depth_by_id: Optional[Dict[int, int]] = None) -> None:
        self._depth_by_id = dict(depth_by_id or {})

    def depth(self, path_id: int) -> int:
        return self._depth_by_id.get(path_id, 0)


def _make_spell_stub(
    spell_id: str = "root",
    *,
    existence: Existence = Existence.unique,
    user_created_object: Optional[Any] = None,
    has_disposal_methods: bool = False,
) -> SimpleNamespace:
    """
    Purpose:
        Build a minimal spell object with the Phase 11 attributes under test.
    Contract:
        - Exposes spell identity, existence, and callable metadata.
        - Leaves requirements unset unless a test provides them separately.
    """

    return SimpleNamespace(
        spell_id=spell_id,
        existence=existence,
        user_created_object=user_created_object,
        has_disposal_methods=has_disposal_methods,
        disposal_method_names=("cleanup",) if has_disposal_methods else (),
        is_existing_creation=False,
        is_class_spell=True,
        is_method_spell=False,
        is_lambda_spell=False,
        spell=lambda: "value:{0}".format(spell_id),
        requirements=None,
    )


def _make_step_kwargs() -> Dict[str, Any]:
    """
    Purpose:
        Build a fully populated constructor payload for ExecutionPlanStep tests.
    Contract:
        - Uses deterministic values for every required constructor field.
    """

    return {
        "instance_key": ("root", None),
        "occurrence": ("root", 7),
        "spell": _make_spell_stub(),
        "existence": Existence.unique,
        "creations_target_kind": ExecutionPlanTargetKind.OWNER,
        "shared_instance": True,
        "inject_spec": None,
        "dependency_keys": [("dep-a", None)],
        "dependency_keys_by_param": {"service": [("dep-a", None)]},
        "dependency_resolution_order": [("service", [("dep-a", None)])],
        "override_keys": ["service"],
        "override_match_prefix": 7,
        "override_match_prefix_len": 2,
        "expects_overrides": True,
        "contract_keys": ["contract-service"],
        "allow_list_aggregation": False,
        "uses_positional_override": True,
        "contract_payload": {"value": "contract", "__args__": ("left",)},
        "contract_positional_override": ("left",),
        "has_contract_payload": True,
        "lock_hint": "spell_lock",
        "use_spell_lock_hint": True,
        "requires_spellspace": False,
        "owner_conduit_required": False,
        "must_register": True,
        "disposal_method_names": ["cleanup"],
    }


def test_execution_plan_step_properties_and_validation() -> None:
    """
    Purpose:
        Validate the direct ExecutionPlanStep object contract.
    Contract:
        - Constructor rejects missing required core fields.
        - Property surface returns the stored compiled metadata.
    """

    kwargs = _make_step_kwargs()
    step = ExecutionPlanStep(**kwargs)

    assert step.instance_key == ("root", None)
    assert step.occurrence == ("root", 7)
    assert step.spell.spell_id == "root"
    assert step.existence is Existence.unique
    assert step.creations_target_kind == ExecutionPlanTargetKind.OWNER
    assert step.shared_instance is True
    assert step.dependency_keys == [("dep-a", None)]
    assert step.dependency_keys_by_param == {"service": [("dep-a", None)]}
    assert step.override_keys == ["service"]
    assert step.override_match_prefix == 7
    assert step.override_match_prefix_len == 2
    assert step.contract_keys == ["contract-service"]
    assert step.contract_payload == {"value": "contract", "__args__": ("left",)}
    assert step.contract_positional_override == ("left",)
    assert step.lock_hint == "spell_lock"
    assert step.use_spell_lock_hint is True
    assert step.must_register is True
    assert step.disposal_method_names == ["cleanup"]

    kwargs["spell"] = None
    with pytest.raises(ValueError, match="spell must not be None"):
        ExecutionPlanStep(**kwargs)

    kwargs = _make_step_kwargs()
    kwargs["must_register"] = None
    with pytest.raises(ValueError, match="must_register must not be None"):
        ExecutionPlanStep(**kwargs)


def test_execution_plan_fast_plan_roundtrip_and_cleanup() -> None:
    """
    Purpose:
        Validate the direct ExecutionPlan object contract.
    Contract:
        - fast_plan exposes precompiled array payloads when present.
        - cleanup clears owned arrays, transient-plan lists, and root metadata.
        - cleanup is idempotent.
    """

    step = ExecutionPlanStep(**_make_step_kwargs())
    fast_dep_indices = [0]
    fast_param_group_names = ["service"]
    fast_param_group_dep_offsets = [0]
    fast_param_group_dep_counts = [1]
    fast_param_group_offsets = [0]
    fast_param_group_counts = [1]
    fast_use_positional = [True]
    fast_contract_payload_items = [[("value", "contract")]]
    fast_contract_positional_args = [("left",)]
    fast_instance_keys = [("root", None)]
    fast_creations_target_kinds = [ExecutionPlanTargetKind.OWNER]
    fast_existence = [Existence.unique]
    fast_must_register = [True]
    fast_set_result_flags = [True]
    fast_spells = [step.spell]
    fast_call_targets = [step.spell.spell]
    fast_existing_objects = [None]
    fast_is_existing_creation = [False]
    fast_is_callable = [True]
    fast_call_modes = [ExecutionPlanCallMode.CALL0]
    fast_single_dep_indices = [-1]
    fast_transient_plan = (
        1,
        0,
        [step.spell.spell],
        [ExecutionPlanCallMode.CALL0],
        [-1],
    )

    plan = ExecutionPlan(
        root_spell_id="root",
        root_instance_key=("root", None),
        steps=[step],
        spell_id_step_index={"root": 0},
        optimistic_object_refs_by_spell_id={"root": "existing"},
        available_param_by_spell_id={"root": ExecutionPlanTargetKind.OWNER},
        plan_variant=ExecutionPlanVariant.NO_OVERRIDES_FAST,
        fast_dep_indices=fast_dep_indices,
        fast_param_group_names=fast_param_group_names,
        fast_param_group_dep_offsets=fast_param_group_dep_offsets,
        fast_param_group_dep_counts=fast_param_group_dep_counts,
        fast_param_group_offsets=fast_param_group_offsets,
        fast_param_group_counts=fast_param_group_counts,
        fast_use_positional=fast_use_positional,
        fast_contract_payload_items=fast_contract_payload_items,
        fast_contract_positional_args=fast_contract_positional_args,
        fast_instance_keys=fast_instance_keys,
        fast_creations_target_kinds=fast_creations_target_kinds,
        fast_existence=fast_existence,
        fast_must_register=fast_must_register,
        fast_set_result_flags=fast_set_result_flags,
        fast_spells=fast_spells,
        fast_call_targets=fast_call_targets,
        fast_existing_objects=fast_existing_objects,
        fast_is_existing_creation=fast_is_existing_creation,
        fast_is_callable=fast_is_callable,
        fast_root_step_index=0,
        fast_call_modes=fast_call_modes,
        fast_single_dep_indices=fast_single_dep_indices,
        fast_transient_plan=fast_transient_plan,
        fast_has_contract_payloads=True,
        fast_has_existing_creations=False,
    )

    assert plan.root_spell_id == "root"
    assert plan.root_instance_key == ("root", None)
    assert plan.steps == [step]
    assert plan.plan_variant == ExecutionPlanVariant.NO_OVERRIDES_FAST
    assert plan.fast_plan is not None
    assert plan.fast_plan[0] is fast_dep_indices
    assert plan.fast_transient_plan is fast_transient_plan
    assert plan.fast_has_contract_payloads is True
    assert plan.fast_has_existing_creations is False

    plan.cleanup()

    assert fast_dep_indices == []
    assert fast_param_group_names == []
    assert fast_transient_plan[2] == []
    assert fast_transient_plan[3] == []
    assert fast_transient_plan[4] == []
    assert plan._root_spell_id is None
    assert plan._steps is None
    assert plan._fast_dep_indices is None
    assert plan._fast_transient_plan is None

    plan.cleanup()


def test_execution_plan_builder_helpers_cover_existence_and_param_extraction() -> None:
    """
    Purpose:
        Validate the static helper contracts on ExecutionPlanBuilder.
    Contract:
        - existence policies map to the correct creations target and lock hint.
        - many-without-disposal skips registration, all other spell shapes do not.
        - injection specs flatten dependency, override, and contract keys in
          runtime order.
    """

    many_spell = _make_spell_stub(existence=Existence.many, has_disposal_methods=False)
    unique_spell = _make_spell_stub(existence=Existence.unique, has_disposal_methods=False)
    many_with_disposal = _make_spell_stub(existence=Existence.many, has_disposal_methods=True)

    assert ExecutionPlanBuilder._creation_target_for_existence(Existence.unique) == (
        ExecutionPlanTargetKind.OWNER
    )
    assert ExecutionPlanBuilder._creation_target_for_existence(
        Existence.unique_per_conduit
    ) == ExecutionPlanTargetKind.CALLER
    assert ExecutionPlanBuilder._creation_target_for_existence(
        Existence.unique_per_spell_space
    ) == ExecutionPlanTargetKind.SPELLSPACE
    assert ExecutionPlanBuilder._creation_target_for_existence(Existence.many) == (
        ExecutionPlanTargetKind.CALLER
    )

    assert ExecutionPlanBuilder._lock_hint_for_existence(Existence.unique) == "spell_lock"
    assert ExecutionPlanBuilder._lock_hint_for_existence(
        Existence.unique_per_conduit_cluster
    ) == "spell_lock"
    assert ExecutionPlanBuilder._lock_hint_for_existence(Existence.many) == "creations_lock"

    assert ExecutionPlanBuilder._should_register(many_spell) is False
    assert ExecutionPlanBuilder._should_register(unique_spell) is True
    assert ExecutionPlanBuilder._should_register(many_with_disposal) is True

    inject_spec = InjectionSpec(
        param_sources={
            "service": ParamSource(kind="dependency", dependency_keys=[("dep-a", None)]),
            "others": ParamSource(
                kind="mixed",
                dependency_keys=[("dep-b", 3), ("dep-c", 4)],
                override_key="override-others",
            ),
            "contracted": ParamSource(kind="contract", contract_key="contract-service"),
        },
        allow_list_aggregation=True,
        uses_positional_override=False,
        contract_payload={"value": "contract"},
    )

    dependency_keys, dependency_keys_by_param, override_keys, contract_keys = (
        ExecutionPlanBuilder._extract_param_keys(inject_spec)
    )

    assert dependency_keys == [("dep-a", None), ("dep-b", 3), ("dep-c", 4)]
    assert dependency_keys_by_param == {
        "service": [("dep-a", None)],
        "others": [("dep-b", 3), ("dep-c", 4)],
    }
    assert override_keys == ["override-others"]
    assert contract_keys == ["contract-service"]


def test_execution_plan_builder_occurrence_resolution_and_build_populates_runtime_step() -> None:
    """
    Purpose:
        Validate the smallest real ExecutionPlanBuilder build contract.
    Contract:
        - Shared root instance keys resolve through canonical occurrences.
        - build() carries injection metadata into the produced execution step.
        - optimistic user-created objects and per-spell routing metadata are retained.
    """

    path_registry = _PathRegistryStub({7: 2})
    occurrence_plan = SimpleNamespace(
        root_spell_id="root",
        execution_order=["root"],
        instance_keys_by_spell_id={"root": [("root", None)]},
        canonical_occurrences_by_spell_id={"root": ("root", 7)},
        root_instance_key=("root", None),
        shared_spell_ids={"root"},
        path_registry=path_registry,
    )
    injection_lookup = {
        ("root", None): InjectionSpec(
            param_sources={
                "service": ParamSource(kind="dependency", dependency_keys=[("dep-a", None)]),
                "contracted": ParamSource(
                    kind="mixed",
                    override_key="override-service",
                    contract_key="contract-service",
                ),
            },
            allow_list_aggregation=False,
            uses_positional_override=True,
            contract_payload={"value": "contract", "__args__": ("left",)},
        )
    }
    injection_plan = SimpleNamespace(
        select_for_runtime=lambda *, root_spell_id: injection_lookup
        if root_spell_id == "root"
        else None,
    )
    existing_object = object()
    spell = _make_spell_stub(
        existence=Existence.unique,
        user_created_object=existing_object,
        has_disposal_methods=True,
    )

    builder = ExecutionPlanBuilder(
        occurrence_plan=occurrence_plan,
        injection_plan=injection_plan,
        spell_lookup={"root": spell},
        plan_variant=ExecutionPlanVariant.OVERRIDES,
    )

    assert builder._occurrence_for_instance_key(("root", 5)) == ("root", 5)
    assert builder._occurrence_for_instance_key(("root", None)) == ("root", 7)

    plan = builder.build()
    step = plan.steps[0]

    assert plan.root_spell_id == "root"
    assert plan.root_instance_key == ("root", None)
    assert plan.plan_variant == ExecutionPlanVariant.OVERRIDES
    assert plan.fast_plan is None
    assert plan.spell_id_step_index == {"root": 0}
    assert plan.optimistic_object_refs_by_spell_id == {"root": existing_object}
    assert plan.available_param_by_spell_id == {
        "root": ExecutionPlanTargetKind.OWNER,
    }
    assert step.occurrence == ("root", 7)
    assert step.shared_instance is True
    assert step.override_match_prefix == 7
    assert step.override_match_prefix_len == 2
    assert step.dependency_keys == [("dep-a", None)]
    assert step.override_keys == ["override-service"]
    assert step.contract_keys == ["contract-service"]
    assert step.contract_payload == {"value": "contract", "__args__": ("left",)}
    assert step.contract_positional_override == ("left",)
    assert step.has_contract_payload is True
    assert step.must_register is True
    assert step.disposal_method_names == ["cleanup"]


def test_execution_plan_builder_raises_when_shared_canonical_occurrence_is_missing() -> None:
    """
    Purpose:
        Validate the shared-occurrence guard on ExecutionPlanBuilder.
    Contract:
        - Missing canonical occurrences raise instead of silently fabricating paths.
    """

    builder = ExecutionPlanBuilder(
        occurrence_plan=SimpleNamespace(
            root_spell_id="root",
            execution_order=[],
            instance_keys_by_spell_id={},
            canonical_occurrences_by_spell_id={},
            root_instance_key=("root", None),
            shared_spell_ids=set(),
            path_registry=_PathRegistryStub(),
        ),
        injection_plan=None,
        spell_lookup={},
        plan_variant=ExecutionPlanVariant.OVERRIDES,
    )

    with pytest.raises(ValueError, match="canonical occurrence missing"):
        builder._occurrence_for_instance_key(("root", None))


def test_execution_plan_builder_strips_override_metadata_from_no_overrides_variant() -> None:
    """
    Purpose:
        Lock the bounded no-overrides strip contract for Phase 11.
    Contract:
        - `NO_OVERRIDES_FAST` steps do not carry explicit override metadata.
        - Contract payload semantics still survive in the no-overrides plan.
        - The override-capable variant still preserves override metadata.
    """

    path_registry = _PathRegistryStub({7: 2})
    occurrence_plan = SimpleNamespace(
        root_spell_id="root",
        execution_order=["root"],
        instance_keys_by_spell_id={"root": [("root", None)]},
        canonical_occurrences_by_spell_id={"root": ("root", 7)},
        root_instance_key=("root", None),
        shared_spell_ids={"root"},
        path_registry=path_registry,
    )
    injection_lookup = {
        ("root", None): InjectionSpec(
            param_sources={
                "contracted": ParamSource(
                    kind="mixed",
                    override_key="override-service",
                    contract_key="contract-service",
                ),
            },
            allow_list_aggregation=False,
            uses_positional_override=True,
            contract_payload={"value": "contract", "__args__": ("left",)},
        )
    }
    injection_plan = SimpleNamespace(
        select_for_runtime=lambda *, root_spell_id: injection_lookup
        if root_spell_id == "root"
        else None,
    )
    spell = _make_spell_stub(
        existence=Existence.unique,
        user_created_object=object(),
        has_disposal_methods=True,
    )

    no_overrides_builder = ExecutionPlanBuilder(
        occurrence_plan=occurrence_plan,
        injection_plan=injection_plan,
        spell_lookup={"root": spell},
        plan_variant=ExecutionPlanVariant.NO_OVERRIDES_FAST,
    )
    no_overrides_plan = no_overrides_builder.build()
    no_overrides_step = no_overrides_plan.steps[0]

    assert no_overrides_step.override_keys == []
    assert no_overrides_step.override_match_prefix is None
    assert no_overrides_step.override_match_prefix_len == 0
    assert no_overrides_step.expects_overrides is False
    assert no_overrides_step.contract_keys == ["contract-service"]
    assert no_overrides_step.contract_payload == {
        "value": "contract",
        "__args__": ("left",),
    }

    overrides_builder = ExecutionPlanBuilder(
        occurrence_plan=occurrence_plan,
        injection_plan=injection_plan,
        spell_lookup={"root": spell},
        plan_variant=ExecutionPlanVariant.OVERRIDES,
    )
    overrides_plan = overrides_builder.build()
    overrides_step = overrides_plan.steps[0]

    assert overrides_step.override_keys == ["override-service"]
    assert overrides_step.override_match_prefix == 7
    assert overrides_step.override_match_prefix_len == 2
    assert overrides_step.expects_overrides is True


def test_execution_plan_builder_build_raises_on_injection_root_mismatch() -> None:
    """
    Purpose:
        Validate the Phase 11 guard for unusable injection selections.
    Contract:
        - build() raises when the injection plan cannot supply a runtime selection
          for the requested root spell id.
    """

    builder = ExecutionPlanBuilder(
        occurrence_plan=SimpleNamespace(
            root_spell_id="root",
            execution_order=["root"],
            instance_keys_by_spell_id={"root": [("root", None)]},
            canonical_occurrences_by_spell_id={"root": ("root", 7)},
            root_instance_key=("root", None),
            shared_spell_ids={"root"},
            path_registry=_PathRegistryStub({7: 1}),
        ),
        injection_plan=SimpleNamespace(select_for_runtime=lambda *, root_spell_id: None),
        spell_lookup={"root": _make_spell_stub()},
        plan_variant=ExecutionPlanVariant.OVERRIDES,
    )

    with pytest.raises(ValueError, match="injection plan root mismatch or cleaned plan"):
        builder.build()


def test_execution_plan_builder_build_raises_when_fast_plan_root_instance_is_missing() -> None:
    """
    Purpose:
        Validate the no-overrides fast-plan root-index guard.
    Contract:
        - build() raises when the configured root instance key does not exist in
          the compiled step index for a fast no-overrides plan.
    """

    builder = ExecutionPlanBuilder(
        occurrence_plan=SimpleNamespace(
            root_spell_id="root",
            execution_order=["root"],
            instance_keys_by_spell_id={"root": [("root", None)]},
            canonical_occurrences_by_spell_id={"root": ("root", 7)},
            root_instance_key=("missing", None),
            shared_spell_ids={"root"},
            path_registry=_PathRegistryStub({7: 1}),
        ),
        injection_plan=None,
        spell_lookup={"root": _make_spell_stub(existence=Existence.many)},
        plan_variant=ExecutionPlanVariant.NO_OVERRIDES_FAST,
    )

    with pytest.raises(ValueError, match="root instance key missing from step index"):
        builder.build()
