"""Component tests for the phase-10 and phase-11 discovery facades."""

from typing import Any, Tuple

from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery import (
    CodegenCreationDiscovery,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery_system import (
    CodegenCreationDiscoverySystem,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_system import (
    CodegenCreationSystem,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.codegen_plan_discovery import (
    CodegenPlanDiscovery,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.codegen_plan_discovery_system import (
    CodegenPlanDiscoverySystem,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_planner import (
    SpellCodegenPlanner,
)


class _ProcessorStateProbe:
    """Minimal processor-state double for component discovery slices."""

    def __init__(self, processor_strategy_ids: Tuple[str, ...]) -> None:
        """Store processor provenance for planner-shell build tests."""
        self._processor_strategy_ids = processor_strategy_ids

    def snapshot_applied_strategy_ids(self) -> Tuple[str, ...]:
        """Return the stored processor strategy ids."""
        return self._processor_strategy_ids


class _PlanStrategyProbe:
    """Minimal plan strategy double for planner component wiring tests."""

    def __init__(self, strategy_id: str) -> None:
        """Store the stable strategy id used in the planner facade."""
        self.strategy_id = strategy_id

    def apply(self, state: Any, artifact: Any, plan: SpellCodegenPlan) -> None:
        """Write a visible marker onto the planner-owned plan."""
        _ = state
        _ = artifact
        plan.metadata["component_plan_applied"] = self.strategy_id


class _CreationStrategyProbe:
    """Minimal creation strategy double for codegen-creation component tests."""

    def __init__(self, strategy_id: str) -> None:
        """Store the stable strategy id used in the creation facade."""
        self.strategy_id = strategy_id

    def apply(self, spell_codegen_model: Any, spell_codegen_plan: Any, spell_codegen_creation: Any) -> None:
        """Write a visible marker onto the creation artifact."""
        _ = spell_codegen_model
        _ = spell_codegen_plan
        spell_codegen_creation.metadata["component_creation_applied"] = self.strategy_id


def test_component_codegen_plan_discovery_system_uses_default_generalized_strategy() -> None:
    """The real phase-10 discovery system should still resolve the generalized discovery result by default."""
    discovery = CodegenPlanDiscoverySystem().discover(
        _ProcessorStateProbe(("processor_a",))
    )

    assert isinstance(discovery, CodegenPlanDiscovery)
    assert discovery.selected_strategy_id == "generalized_codegen_plan"
    assert discovery.discovery_reason == "default_generalized_model_native_strategy"


def test_component_codegen_creation_discovery_system_uses_generalized_chain_for_generalized_plan() -> None:
    """The real phase-11 discovery system should still resolve the generalized creation chain for generalized planner output."""
    discovery = CodegenCreationDiscoverySystem().discover(
        object(),
        SpellCodegenPlan(
            processor_strategy_ids=(),
            plan_strategy_ids=("generalized_codegen_plan",),
            no_overrides_plan=None,
            overrides_plan=None,
            metadata={"selected_strategy_id": "generalized_codegen_plan"},
        ),
    )

    assert isinstance(discovery, CodegenCreationDiscovery)
    assert discovery.selected_strategy_ids == (
        "generalized_codegen_creation",
    )


def test_component_codegen_creation_discovery_system_uses_fallback_chain_for_non_generalized_plan() -> None:
    """The real phase-11 discovery system should still fall back to the no-overrides chain for non-generalized planner output."""
    discovery = CodegenCreationDiscoverySystem().discover(
        object(),
        SpellCodegenPlan(
            processor_strategy_ids=(),
            plan_strategy_ids=(),
            no_overrides_plan=None,
            overrides_plan=None,
            metadata={"selected_strategy_id": "other_plan"},
        ),
    )

    assert discovery.selected_strategy_ids == (
        "generalized_no_overrides_codegen_creation",
    )
    assert discovery.discovery_reason == "fallback_no_overrides_creation_strategy"


def test_component_spell_codegen_planner_uses_real_discovery_and_selected_strategy_id() -> None:
    """The planner facade should still use the real discovery seam to stamp the selected strategy id on the plan."""
    planner = SpellCodegenPlanner()
    artifact = type(
        "ArtifactProbe",
        (),
        {
            "_spell_codegen_model": _ProcessorStateProbe(("processor_a",)),
            "_spell_codegen_plan": None,
        },
    )()
    planner._strategy_builder = type(
        "BuilderProbe",
        (),
        {
            "cleanup": lambda self: None,
            "get_strategy": lambda self, strategy_name: _PlanStrategyProbe(strategy_name),
        },
    )()

    planner.build(artifact)

    assert artifact._spell_codegen_plan.metadata["selected_strategy_id"] == (
        "generalized_codegen_plan"
    )


def test_component_codegen_creation_system_uses_real_discovery_and_selected_strategy_chain() -> None:
    """The creation facade should still use the real discovery seam to stamp the selected strategy chain on the output artifact."""
    system = CodegenCreationSystem()
    system._strategy_builder = type(
        "BuilderProbe",
        (),
        {
            "cleanup": lambda self: None,
            "get_strategies": lambda self, strategy_ids: (
                _CreationStrategyProbe(strategy_ids[0]),
            ),
        },
    )()
    artifact = type(
        "ArtifactProbe",
        (),
        {
            "_spell_codegen_model": object(),
            "_spell_codegen_plan": SpellCodegenPlan(
                processor_strategy_ids=(),
                plan_strategy_ids=(),
                no_overrides_plan=None,
                overrides_plan=None,
                metadata={"selected_strategy_id": "other_plan"},
            ),
            "_spell_codegen_creation": None,
        },
    )()

    system.build(artifact)

    assert artifact._spell_codegen_creation.selected_strategy_ids == (
        "generalized_no_overrides_codegen_creation",
    )
    assert artifact._spell_codegen_creation.metadata["component_creation_applied"] == (
        "generalized_no_overrides_codegen_creation"
    )
