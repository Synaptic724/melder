"""Unit tests for the medium-split occurrence analyzer strategy."""

from types import SimpleNamespace
from typing import Any

import pytest

import melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_contract_analyzer_strategy as occurrence_contract_strategy_module
import melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy as occurrence_graph_strategy_module
import melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_instance_analyzer_strategy as occurrence_instance_strategy_module
from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer import (
    SpellAnalyzer,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer_strategy_builder import (
    SpellAnalyzerStrategyBuilder,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_contract_analyzer_strategy import (
    SpellOccurrenceContractAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy import (
    SpellOccurrenceGraphAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_instance_analyzer_strategy import (
    SpellOccurrenceInstanceAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_order_analyzer_strategy import (
    SpellOccurrenceOrderAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)


def _make_spellbook_and_spell() -> tuple[Any, Any]:
    """Build a minimal spellbook/spell pair for occurrence analyzer tests."""
    spellbook = SimpleNamespace(
        _spell_id_pool={},
    )
    spell = SimpleNamespace(
        spell_id="spell-1",
        spell_name="spell-1",
        spell_index=SimpleNamespace(current="spell-1", id="lineage-spell-1"),
        is_existing_creation=False,
        mutation_override=None,
        _spellbook=spellbook,
        _spell_system_states=SimpleNamespace(_local_topologies={}),
    )
    spellbook._spell_id_pool["spell-1"] = spell
    return spellbook, spell


def _make_occurrence_plan() -> Any:
    """Build a narrow fake OccurrencePlan surface for strategy tests."""
    occurrence_graph = {
        ("spell-1", 0): {"dep": [("dep-1", 1), ("dep-2", 2)]},
        ("dep-1", 1): {},
        ("dep-2", 2): {},
    }
    return SimpleNamespace(
        root_spell_id="spell-1",
        occurrence_graph=occurrence_graph,
        execution_order=["dep-1", "dep-2", "spell-1"],
        instance_keys_by_spell_id={
            "spell-1": [("spell-1", 0)],
            "dep-1": [("dep-1", 1)],
            "dep-2": [("dep-2", 2)],
        },
        canonical_occurrences_by_spell_id={},
        root_instance_key=("spell-1", 0),
        shared_spell_ids=set(),
        contract_overrides_by_occurrence={
            ("dep-1", 1): {"svc": "x"},
        },
        contract_overrides_by_spell_id={
            "dep-1": [(("dep-1", 1), {"svc": "x"})],
        },
        contract_dependencies_complete=True,
        path_registry=object(),
    )


def test_occurrence_analyzer_chain_builds_medium_split_artifacts(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The occurrence analyzer should chain the four real occurrence strategies."""
    _, spell = _make_spellbook_and_spell()
    artifact = SpellCompilerArtifact("spell-1")
    artifact._root_blueprint_phase5 = SimpleNamespace(
        root_spell_id="spell-1",
        dag=object(),
        ordered_node_ids=("dep-1", "dep-2", "spell-1"),
        path_registry=object(),
    )
    occurrence_plan = _make_occurrence_plan()

    class _BuilderStub:
        """Builder stub exposing the minimal Phase 8 helper surface."""

        def __init__(self, **kwargs: Any) -> None:
            self.cleanup_calls = 0

        def _should_collapse_shared_occurrences(self) -> bool:
            """Return deterministic shared-collapse posture."""
            return True

        def _build_occurrence_graph(self, **kwargs: Any) -> Any:
            """Return the fixed occurrence graph."""
            return occurrence_plan.occurrence_graph

        def _extend_occurrence_graph_with_ordered_nodes(self, **kwargs: Any) -> None:
            """No-op because the fixed graph already contains all nodes."""
            return None

        def _build_instance_plan(self, **kwargs: Any) -> Any:
            """Return the fixed instance/sharedness tuple."""
            return (
                occurrence_plan.instance_keys_by_spell_id,
                occurrence_plan.canonical_occurrences_by_spell_id,
                occurrence_plan.root_instance_key,
                occurrence_plan.shared_spell_ids,
            )

        def _compile_contract_overrides(self, **kwargs: Any) -> Any:
            """Return the fixed contract-routing tuple."""
            return (
                occurrence_plan.contract_overrides_by_occurrence,
                occurrence_plan.contract_overrides_by_spell_id,
                occurrence_plan.contract_dependencies_complete,
            )

        def cleanup(self) -> None:
            """Record cleanup for parity with the real builder."""
            self.cleanup_calls += 1

    monkeypatch.setattr(
        occurrence_graph_strategy_module,
        "OccurrencePlanBuilder",
        _BuilderStub,
    )
    monkeypatch.setattr(
        occurrence_instance_strategy_module,
        "OccurrencePlanBuilder",
        _BuilderStub,
    )
    monkeypatch.setattr(
        occurrence_contract_strategy_module,
        "OccurrencePlanBuilder",
        _BuilderStub,
    )
    class _Phase8Stub:
        """Phase 8 helper stub with deterministic cache/profile output."""

        def _build_phase8_occurrence_plan_fast_key(self, **kwargs: Any) -> tuple[str]:
            return ("occ-fast",)

        def _build_phase8_occurrence_plan_input_signature(self, **kwargs: Any) -> str:
            return "occ-sig"

        @staticmethod
        def _build_phase8_occurrence_shape_profile(plan: Any) -> dict[str, int]:
            return {"execution_order_count": 3}

    monkeypatch.setattr(
        occurrence_graph_strategy_module,
        "CompilerPhase8",
        _Phase8Stub,
    )
    monkeypatch.setattr(
        occurrence_instance_strategy_module,
        "CompilerPhase8",
        _Phase8Stub,
    )

    analyzer = SpellAnalyzer()
    analyzer.analyze_occurrence(spell, artifact)

    assert artifact._occurrence_analysis_fast_key == ("occ-fast",)
    assert artifact._occurrence_analysis_input_signature == "occ-sig"
    assert artifact._occurrence_analysis_shape_profile == {
        "execution_order_count": 3,
    }
    assert artifact._occurrence_graph_analysis is not None
    assert artifact._occurrence_order_analysis is not None
    assert artifact._occurrence_instance_analysis is not None
    assert artifact._occurrence_contract_analysis is not None
    assert artifact._occurrence_graph_analysis.edge_count == 2
    assert artifact._occurrence_order_analysis.execution_order_count == 3
    assert artifact._occurrence_instance_analysis.instance_count == 3
    assert (
        artifact._occurrence_contract_analysis.contract_override_occurrence_count
        == 1
    )


def test_spell_analyzer_strategy_builder_registers_occurrence_strategies_by_default() -> None:
    """The strategy builder should install all four occurrence strategies by default."""
    strategy_builder = SpellAnalyzerStrategyBuilder()

    assert isinstance(
        strategy_builder.get_strategy("spell_occurrence_graph_analyzer"),
        SpellOccurrenceGraphAnalyzerStrategy,
    )
    assert isinstance(
        strategy_builder.get_strategy("spell_occurrence_order_analyzer"),
        SpellOccurrenceOrderAnalyzerStrategy,
    )
    assert isinstance(
        strategy_builder.get_strategy("spell_occurrence_instance_analyzer"),
        SpellOccurrenceInstanceAnalyzerStrategy,
    )
    assert isinstance(
        strategy_builder.get_strategy("spell_occurrence_contract_analyzer"),
        SpellOccurrenceContractAnalyzerStrategy,
    )
