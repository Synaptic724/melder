from __future__ import annotations

from types import SimpleNamespace

import pytest

from melder.aether.spellbook.spell_compiler.blueprints.injection_plan import (
    InjectionPlan,
    InjectionPlanBuilder,
    InjectionSpec,
    ParamSource,
)


def test_param_source_injection_spec_and_builder_validate_required_inputs() -> None:
    """
    Purpose:
        Validate the direct constructor guards on the Phase 9 object layer.
    Contract:
        - ParamSource rejects a missing kind.
        - InjectionSpec rejects missing param_sources.
        - InjectionPlan rejects missing root metadata.
        - InjectionPlanBuilder rejects a missing occurrence plan.
    """

    with pytest.raises(ValueError, match="kind must not be None"):
        ParamSource(kind=None)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="param_sources must not be None"):
        InjectionSpec(  # type: ignore[arg-type]
            param_sources=None,
            allow_list_aggregation=False,
            uses_positional_override=False,
        )

    with pytest.raises(ValueError, match="root_spell_id must not be None"):
        InjectionPlan(  # type: ignore[arg-type]
            root_spell_id=None,
            instance_injections={},
        )

    with pytest.raises(ValueError, match="instance_injections must not be None"):
        InjectionPlan(  # type: ignore[arg-type]
            root_spell_id="root",
            instance_injections=None,
        )

    with pytest.raises(ValueError, match="occurrence_plan must not be None"):
        InjectionPlanBuilder(occurrence_plan=None)  # type: ignore[arg-type]


def test_injection_plan_select_for_runtime_respects_root_and_cleanup() -> None:
    """
    Purpose:
        Validate InjectionPlan runtime selection semantics.
    Contract:
        - Matching root ids expose the stored instance injection mapping.
        - Mismatched root ids return None.
        - Cleaned plans return None instead of raising through the selection API.
    """

    spec = InjectionSpec(
        param_sources={"service": ParamSource(kind="dependency", dependency_keys=[("dep", None)])},
        allow_list_aggregation=False,
        uses_positional_override=False,
        contract_payload=None,
    )
    plan = InjectionPlan(
        root_spell_id="root",
        instance_injections={("root", None): spec},
    )

    assert plan.select_for_runtime(root_spell_id="root") == {("root", None): spec}
    assert plan.select_for_runtime(root_spell_id="other") is None

    plan.cleanup()

    assert plan.select_for_runtime(root_spell_id="root") is None
    plan.cleanup()


def test_injection_plan_builder_build_normalizes_shared_and_non_shared_dependencies() -> None:
    """
    Purpose:
        Validate the smallest real InjectionPlanBuilder build contract.
    Contract:
        - Shared dependencies collapse to `(spell_id, None)`.
        - Non-shared dependencies preserve their path-bearing instance keys.
        - Contract payload `__args__` lists are normalized to tuples.
        - Multiple dependencies enable list aggregation.
    """

    occurrence_plan = SimpleNamespace(
        root_spell_id="root",
        shared_spell_ids={"root", "shared-dep"},
        instance_keys_by_spell_id={
            "root": [("root", None)],
            "shared-dep": [("shared-dep", None)],
            "leaf": [("leaf", 4), ("leaf", 5)],
        },
        canonical_occurrences_by_spell_id={
            "root": ("root", 7),
            "shared-dep": ("shared-dep", 9),
        },
        occurrence_graph={
            ("root", 7): {
                "service": [("shared-dep", 9)],
                "others": [("leaf", 4), ("leaf", 5)],
            },
            ("shared-dep", 9): {},
            ("leaf", 4): {},
            ("leaf", 5): {},
        },
        contract_overrides_by_occurrence={
            ("root", 7): {
                "__args__": ["left", "right"],
                "fixed": "value",
            }
        },
    )

    plan = InjectionPlanBuilder(occurrence_plan=occurrence_plan).build()
    root_spec = plan.instance_injections[("root", None)]

    assert plan.root_spell_id == "root"
    assert root_spec.allow_list_aggregation is True
    assert root_spec.uses_positional_override is True
    assert root_spec.contract_payload == {
        "__args__": ("left", "right"),
        "fixed": "value",
    }
    assert root_spec.param_sources["service"].dependency_keys == [("shared-dep", None)]
    assert root_spec.param_sources["others"].dependency_keys == [
        ("leaf", 4),
        ("leaf", 5),
    ]
    assert root_spec.param_sources["fixed"].contract_key == "fixed"


def test_injection_plan_object_properties_expose_stored_references() -> None:
    """
    Purpose:
        Validate the stable property surface on ParamSource and InjectionSpec.
    Contract:
        - Properties expose the stored metadata for runtime consumers.
        - No defensive copies are introduced on the direct object layer.
    """

    dependency_keys = [("dep", None)]
    contract_payload = {"fixed": "value"}
    param_source = ParamSource(
        kind="dependency",
        dependency_keys=dependency_keys,
        override_key="service",
        contract_key="contract-service",
    )
    spec = InjectionSpec(
        param_sources={"service": param_source},
        allow_list_aggregation=False,
        uses_positional_override=False,
        contract_payload=contract_payload,
    )

    assert param_source.kind == "dependency"
    assert param_source.dependency_keys is dependency_keys
    assert param_source.override_key == "service"
    assert param_source.contract_key == "contract-service"
    assert spec.param_sources["service"] is param_source
    assert spec.allow_list_aggregation is False
    assert spec.uses_positional_override is False
    assert spec.contract_payload is contract_payload
