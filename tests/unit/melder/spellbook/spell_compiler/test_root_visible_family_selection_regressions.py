"""Regression tests: root-visible phase-10 family selection and shared-provider payloads.

Symptom lane (owner findings 2026-07-12):
    - Phase-8 existence analysis was pool-scoped, so unrelated spellbook
      members rerouted phase-10 family selection (solo -> many_only,
      many_only -> generalized) nondeterministically per pool composition.
    - Shared-existence providers read contract payloads only at the phase-8
      canonical occurrence, so payload application depended on which edge
      the shared collapse happened to retain.
"""

from typing import Any, Dict, List, Tuple

import pytest

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.artifact_processor.strategies.spell_injection_processor_strategy import (
    SpellInjectionProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.strategies.many_only_codegen_plan_discovery_strategy import (
    ManyOnlyCodegenPlanDiscoveryStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.strategies.solo_codegen_plan_discovery_strategy import (
    SoloCodegenPlanDiscoveryStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.data.spell_existence_occurrence_analysis import (
    SpellExistenceOccurrence,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.strategies.spell_occurrence_graph_analyzer_strategy import (
    SpellOccurrenceGraphAnalyzerStrategy,
)
from melder.utilities.custom_exceptions.meld_execution_error import (
    MeldExecutionError,
)


class _ModelProbe:
    """Minimal processor-model double for discovery tests."""

    def __init__(self) -> None:
        """Mirror the real model defaults the discovery strategies read."""
        self.existence_occurrence_shape = None
        self.injection_shape = None


class _ContractShapeProbe:
    """Minimal contract-shape double for shared-payload resolution tests."""

    def __init__(
            self,
            *,
            by_occurrence: Dict[Tuple[str, int], Dict[str, Any]],
            by_spell_id: Dict[str, List[Tuple[Tuple[str, int], Dict[str, Any]]]],
    ) -> None:
        """Store the two payload maps the resolver consumes."""
        self.contract_overrides_by_occurrence = by_occurrence
        self.contract_overrides_by_spell_id = by_spell_id


def _walk_bundle(
        rows: Tuple[SpellExistenceOccurrence, ...],
) -> Tuple[Any, ...]:
    """Build one phase-8 shared spell-walk bundle from occurrence rows.

    Mirrors the six-slot bundle contract of `_build_spell_walk_rows`; the
    pool-scoped aggregate slots are deliberately fabricated as sentinels
    because the root-visible builder must recompute every aggregate from
    the filtered rows instead of trusting the pool aggregates.
    """
    existence_by_spell_id = {row.spell_id: row.existence for row in rows}
    spell_rows = tuple(
        (row.spell_id, row.spell_id, row.existence.name, False) for row in rows
    )
    pool_counts = (("POOL_SENTINEL", -1),)
    return (
        spell_rows,
        rows,
        pool_counts,
        -1,
        pool_counts,
        existence_by_spell_id,
    )


def _row(
        spell_id: str,
        existence: Existence,
        has_disposal_methods: bool = False,
) -> SpellExistenceOccurrence:
    """Build one existence-occurrence row."""
    return SpellExistenceOccurrence(
        spell_id=spell_id,
        existence=existence,
        has_disposal_methods=has_disposal_methods,
    )


def test_existence_analysis_filters_to_root_visible_spell_ids() -> None:
    """The root-visible builder drops pool rows outside the occurrence graph."""
    bundle = _walk_bundle(
        (
            _row("root_a", Existence.many),
            _row("unrelated_b", Existence.many, has_disposal_methods=True),
        )
    )
    analysis = SpellOccurrenceGraphAnalyzerStrategy._build_existence_occurrence_analysis(
        root_spell_id="root_a",
        shared_spell_walk=bundle,
        visible_spell_ids={"root_a"},
    )
    assert analysis is not None
    assert analysis.total_spell_count == 1
    assert tuple(row.spell_id for row in analysis.spell_existence_rows) == ("root_a",)
    assert analysis.existence_counts == ((Existence.many, 1),)
    assert analysis.disposal_enabled_spell_count == 0
    assert analysis.root_existence is Existence.many


def test_solo_family_selected_for_isolated_many_root_despite_unrelated_pool_spell() -> None:
    """Regression: an unrelated many spell no longer pushes a solo root to many_only."""
    bundle = _walk_bundle(
        (
            _row("root_a", Existence.many),
            _row("unrelated_b", Existence.many),
        )
    )
    analysis = SpellOccurrenceGraphAnalyzerStrategy._build_existence_occurrence_analysis(
        root_spell_id="root_a",
        shared_spell_walk=bundle,
        visible_spell_ids={"root_a"},
    )
    model = _ModelProbe()
    model.existence_occurrence_shape = analysis
    solo_discovery = SoloCodegenPlanDiscoveryStrategy().discover(model)
    assert solo_discovery is not None
    assert solo_discovery.plan_family_id == "solo"
    assert ManyOnlyCodegenPlanDiscoveryStrategy().discover(model) is None


def test_many_only_family_survives_unrelated_unique_pool_spell() -> None:
    """Regression: an unrelated unique spell no longer demotes many_only to generalized."""
    bundle = _walk_bundle(
        (
            _row("root_a", Existence.many),
            _row("dep_c", Existence.many),
            _row("unrelated_unique_d", Existence.unique),
        )
    )
    analysis = SpellOccurrenceGraphAnalyzerStrategy._build_existence_occurrence_analysis(
        root_spell_id="root_a",
        shared_spell_walk=bundle,
        visible_spell_ids={"root_a", "dep_c"},
    )
    model = _ModelProbe()
    model.existence_occurrence_shape = analysis
    many_only_discovery = ManyOnlyCodegenPlanDiscoveryStrategy().discover(model)
    assert many_only_discovery is not None
    assert many_only_discovery.plan_family_id == "many_only"
    assert SoloCodegenPlanDiscoveryStrategy().discover(model) is None


def test_shared_provider_single_payload_applies_regardless_of_canonical_edge() -> None:
    """Regression: one distinct payload applies even when the canonical edge carries none."""
    payload = {"mode": "tuned"}
    shape = _ContractShapeProbe(
        by_occurrence={("provider", 7): payload},
        by_spell_id={"provider": [(("provider", 7), payload)]},
    )
    resolved = SpellInjectionProcessorStrategy._resolve_shared_contract_payload(
        spell_id="provider",
        canonical_occurrence=("provider", 3),
        contract_shape=shape,
    )
    assert resolved == payload


def test_shared_provider_identical_payloads_dedupe_across_edges() -> None:
    """Two edges carrying equal payloads resolve to that one payload."""
    shape = _ContractShapeProbe(
        by_occurrence={},
        by_spell_id={
            "provider": [
                (("provider", 3), {"mode": "tuned"}),
                (("provider", 7), {"mode": "tuned"}),
            ]
        },
    )
    resolved = SpellInjectionProcessorStrategy._resolve_shared_contract_payload(
        spell_id="provider",
        canonical_occurrence=("provider", 3),
        contract_shape=shape,
    )
    assert resolved == {"mode": "tuned"}


def test_shared_provider_conflicting_payloads_raise_meld_execution_error() -> None:
    """Regression: distinct payloads on one shared provider fail fast, never silently."""
    shape = _ContractShapeProbe(
        by_occurrence={},
        by_spell_id={
            "provider": [
                (("provider", 3), {"mode": "tuned"}),
                (("provider", 7), {"mode": "raw"}),
            ]
        },
    )
    with pytest.raises(MeldExecutionError) as exc_info:
        SpellInjectionProcessorStrategy._resolve_shared_contract_payload(
            spell_id="provider",
            canonical_occurrence=("provider", 3),
            contract_shape=shape,
        )
    assert "distinct SpellContract override" in str(exc_info.value)


def test_shared_provider_without_recorded_payloads_reads_canonical_fallback() -> None:
    """Zero recorded payloads preserve the prior canonical-read behavior."""
    shape = _ContractShapeProbe(by_occurrence={}, by_spell_id={})
    resolved = SpellInjectionProcessorStrategy._resolve_shared_contract_payload(
        spell_id="provider",
        canonical_occurrence=("provider", 3),
        contract_shape=shape,
    )
    assert resolved is None
