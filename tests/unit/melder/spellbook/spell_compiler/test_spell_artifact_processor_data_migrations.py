"""Unit tests for processor-owned data objects replacing blueprint-era payloads."""

from typing import Any, Dict, Optional, Tuple

from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_injection_analysis import (
    SpellInjectionAnalysis,
    SpellInjectionInstanceSpec,
    SpellInjectionParamSource,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_occurrence_contract_analysis import (
    SpellOccurrenceContractAnalysis,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_occurrence_instance_analysis import (
    SpellOccurrenceInstanceAnalysis,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_occurrence_order_analysis import (
    SpellOccurrenceOrderAnalysis,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_runtime_analysis import (
    SpellRuntimeAnalysis,
    SpellRuntimeRecord,
)
from melder.aether.spellbook.existence.existence import Existence


def test_occurrence_order_analysis_replaces_execution_order_summary() -> None:
    """Occurrence-order analysis should keep count and cleanup ownership locally."""
    execution_order = ["dep", "root"]
    analysis = SpellOccurrenceOrderAnalysis(
        execution_order=execution_order,
    )

    assert analysis.execution_order_count == 2
    assert analysis.execution_order == ["dep", "root"]

    analysis.cleanup()

    assert execution_order == []
    assert not hasattr(analysis, "execution_order")


def test_occurrence_instance_analysis_replaces_occurrence_instance_summary() -> None:
    """Occurrence-instance analysis should summarize sharedness and instance counts."""
    analysis = SpellOccurrenceInstanceAnalysis(
        instance_keys_by_spell_id={
            "root": [("root", None)],
            "dep": [("dep", 1), ("dep", 2)],
        },
        canonical_occurrences_by_spell_id={
            "root": ("root", 0),
        },
        root_instance_key=("root", None),
        shared_spell_ids={"root"},
    )

    assert analysis.unique_spell_count == 2
    assert analysis.shared_spell_count == 1
    assert analysis.instance_count == 3

    analysis.cleanup()

    assert not hasattr(analysis, "instance_keys_by_spell_id")


def test_occurrence_contract_analysis_replaces_contract_payload_summary() -> None:
    """Occurrence-contract analysis should count payload-bearing occurrences and spells."""
    analysis = SpellOccurrenceContractAnalysis(
        contract_overrides_by_occurrence={
            ("dep", 1): {"alpha": 1, "beta": 2},
            ("leaf", 2): {"gamma": 3},
        },
        contract_overrides_by_spell_id={
            "dep": [(("dep", 1), {"alpha": 1, "beta": 2})],
            "leaf": [(("leaf", 2), {"gamma": 3})],
        },
        contract_dependencies_complete=True,
        contract_override_refs_by_occurrence={},
    )

    assert analysis.contract_override_occurrence_count == 2
    assert analysis.contract_override_spell_count == 2
    assert analysis.contract_payload_count == 3

    analysis.cleanup()

    assert not hasattr(analysis, "contract_overrides_by_occurrence")


def test_injection_analysis_replaces_injection_plan_summary() -> None:
    """Injection analysis should summarize dependency, override, and contract payload shape."""
    root_spec = SpellInjectionInstanceSpec(
        param_sources={
            "deps": SpellInjectionParamSource(
                kind="dependency",
                dependency_keys=(("dep", None), ("dep-2", 3)),
                override_key="deps",
            ),
            "cfg": SpellInjectionParamSource(
                kind="contract",
                dependency_keys=(),
                override_key="cfg",
                contract_key="cfg",
            ),
        },
        allow_list_aggregation=True,
        uses_positional_override=True,
        contract_payload={"__args__": ("x", "y"), "cfg": "payload"},
    )
    child_spec = SpellInjectionInstanceSpec(
        param_sources={
            "svc": SpellInjectionParamSource(
                kind="dependency",
                dependency_keys=(("root", None),),
                override_key="svc",
            ),
        },
        allow_list_aggregation=False,
        uses_positional_override=False,
        contract_payload=None,
    )
    analysis = SpellInjectionAnalysis(
        root_spell_id="root",
        root_instance_key=("root", None),
        instance_specs_by_instance_key={
            ("root", None): root_spec,
            ("child", 4): child_spec,
        },
    )

    assert analysis.instance_spec_count == 2
    assert analysis.root_dependency_count == 2
    assert analysis.root_uses_positional_override is True
    assert analysis.positional_override_instance_count == 1
    assert analysis.contract_payload_instance_count == 1
    assert analysis.list_aggregation_instance_count == 1
    assert analysis.param_source_kind_counts == (
        ("contract", 1),
        ("dependency", 2),
    )
    assert analysis.dependency_arity_histogram == (
        (0, 1),
        (1, 1),
        (2, 1),
    )

    analysis.cleanup()

    assert not hasattr(analysis, "instance_specs_by_instance_key")


def test_runtime_analysis_replaces_execution_plan_runtime_summary() -> None:
    """Runtime analysis should own the planner-facing per-spell static runtime rows."""
    root_record = SpellRuntimeRecord(
        spell_id="root",
        spell_name="root",
        spell=object(),
        call_target=object(),
        existence=Existence.unique_per_conduit,
        is_existing_creation=False,
        is_class_spell=True,
        is_method_spell=False,
        is_lambda_spell=False,
        has_disposal_methods=True,
        disposal_method_names=["cleanup"],
        user_created_object=None,
    )
    dep_record = SpellRuntimeRecord(
        spell_id="dep",
        spell_name="dep",
        spell=object(),
        call_target=object(),
        existence=Existence.unique,
        is_existing_creation=True,
        is_class_spell=False,
        is_method_spell=True,
        is_lambda_spell=False,
        has_disposal_methods=False,
        disposal_method_names=[],
        user_created_object=object(),
    )
    analysis = SpellRuntimeAnalysis(
        records_by_spell_id={
            "root": root_record,
            "dep": dep_record,
        }
    )

    assert analysis.spell_count == 2
    assert analysis.records_by_spell_id["root"].disposal_method_names == ["cleanup"]
    assert analysis.records_by_spell_id["dep"].is_existing_creation is True

    analysis.cleanup()

    assert not hasattr(analysis, "records_by_spell_id")
