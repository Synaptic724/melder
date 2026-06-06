"""Direct unit tests for the codegen planner facade, builder, discovery, and plan."""

from typing import Any, Tuple

import pytest

from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.codegen_plan_discovery_system import (
    CodegenPlanDiscovery,
    CodegenPlanDiscoverySystem,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan_strategy_builder import (
    SpellCodegenPlanStrategyBuilder,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_planner import (
    SpellCodegenPlanner,
)


class _CleanupTracker:
    """Simple cleanup double recording whether cleanup was invoked."""

    def __init__(self) -> None:
        """Start with cleanup not yet called."""
        self.cleanup_called = False

    def cleanup(self) -> None:
        """Record one cleanup call."""
        self.cleanup_called = True


class _ProcessorStateProbe:
    """Minimal processor-state double exposing planner provenance only."""

    def __init__(
            self,
            processor_strategy_ids: Tuple[str, ...],
    ) -> None:
        """Store the processor strategy ids for planner carry-through tests."""
        self._processor_strategy_ids = processor_strategy_ids

    def snapshot_applied_strategy_ids(self) -> Tuple[str, ...]:
        """Return the stored processor strategy ids."""
        return self._processor_strategy_ids


class _PlanStrategyProbe:
    """Minimal plan strategy double mutating the planner-owned plan."""

    def __init__(self, strategy_id: str) -> None:
        """Store the stable strategy id for planner provenance."""
        self.strategy_id = strategy_id

    def apply(
            self,
            state: Any,
            artifact: Any,
            plan: SpellCodegenPlan,
    ) -> None:
        """Record visible planner-side output on the supplied plan."""
        _ = state
        _ = artifact
        plan.metadata["plan_was_mutated"] = True


class _PlanBuilderProbe:
    """Minimal builder double for planner facade tests."""

    def __init__(self, strategy: Any) -> None:
        """Store the strategy returned by name resolution."""
        self._strategy = strategy
        self.requested_strategy_name = ""
        self.cleanup_called = False

    def cleanup(self) -> None:
        """Record one cleanup call."""
        self.cleanup_called = True

    def get_strategy(self, strategy_name: str) -> Any:
        """Return the configured strategy and record the requested name."""
        self.requested_strategy_name = strategy_name
        return self._strategy


class _DiscoverySystemProbe:
    """Minimal discovery double for planner facade tests."""

    def __init__(self, discovery: CodegenPlanDiscovery) -> None:
        """Store the discovery result returned to the planner."""
        self._discovery = discovery
        self.discovered_state = None

    def discover(self, spell_codegen_model: Any) -> CodegenPlanDiscovery:
        """Return the configured discovery result and record the input state."""
        self.discovered_state = spell_codegen_model
        return self._discovery


def test_codegen_plan_discovery_system_selects_generalized_strategy_by_default() -> None:
    """The discovery system should default to the generalized model-native plan."""
    discovery = CodegenPlanDiscoverySystem().discover(
        _ProcessorStateProbe(("processor_a",))
    )

    assert discovery.selected_strategy_id == "generalized_codegen_plan"
    assert discovery.discovery_reason == "default_generalized_model_native_strategy"


def test_spell_codegen_plan_strategy_builder_registers_generalized_default() -> None:
    """The real plan-strategy builder should expose the generalized default strategy."""
    builder = SpellCodegenPlanStrategyBuilder()

    assert builder.registered_strategy_names() == ("generalized_codegen_plan",)
    with pytest.raises(RuntimeError, match="missing strategy 'missing_plan'"):
        builder.get_strategy("missing_plan")


def test_spell_codegen_planner_build_raises_when_processor_model_is_missing() -> None:
    """Planner build should fail hard until the processor-owned model exists."""
    planner = SpellCodegenPlanner()
    artifact = type("ArtifactProbe", (), {"_spell_codegen_model": None})()

    with pytest.raises(
            RuntimeError,
            match="requires artifact._spell_codegen_model first",
    ):
        planner.build(artifact)


def test_spell_codegen_planner_build_publishes_plan_and_cleans_previous() -> None:
    """Planner build should publish the plan, record discovery metadata, and cleanup the superseded plan."""
    planner = SpellCodegenPlanner()
    state = _ProcessorStateProbe(("processor_a", "processor_b"))
    previous_plan = _CleanupTracker()
    artifact = type(
        "ArtifactProbe",
        (),
        {
            "_spell_codegen_model": state,
            "_spell_codegen_plan": previous_plan,
        },
    )()
    strategy = _PlanStrategyProbe("selected_plan")
    planner._strategy_builder = _PlanBuilderProbe(strategy)
    planner._discovery_system = _DiscoverySystemProbe(
        CodegenPlanDiscovery(
            selected_strategy_id="selected_plan",
            discovery_reason="preferred_by_test",
        )
    )

    planner.build(artifact)

    plan = artifact._spell_codegen_plan
    assert isinstance(plan, SpellCodegenPlan)
    assert planner._discovery_system.discovered_state is state
    assert planner._strategy_builder.requested_strategy_name == "selected_plan"
    assert plan.processor_strategy_ids == ("processor_a", "processor_b")
    assert plan.plan_strategy_ids == ("selected_plan",)
    assert plan.metadata["selected_strategy_id"] == "selected_plan"
    assert plan.metadata["discovery_reason"] == "preferred_by_test"
    assert plan.metadata["plan_was_mutated"] is True
    assert previous_plan.cleanup_called is True


def test_spell_codegen_planner_build_plan_shell_starts_empty() -> None:
    """The planner shell should carry processor provenance and empty lane payloads."""
    plan = SpellCodegenPlanner._build_plan(
        _ProcessorStateProbe(("processor_only",))
    )

    assert isinstance(plan, SpellCodegenPlan)
    assert plan.processor_strategy_ids == ("processor_only",)
    assert plan.plan_strategy_ids == ()
    assert plan.no_overrides_plan is None
    assert plan.overrides_plan is None
    assert plan.metadata == {}


def test_spell_codegen_plan_cleanup_cleans_lane_payloads_and_metadata() -> None:
    """Plan cleanup should cleanup lane payloads and clear metadata."""
    no_overrides_plan = _CleanupTracker()
    overrides_plan = _CleanupTracker()
    plan = SpellCodegenPlan(
        processor_strategy_ids=("processor_a",),
        plan_strategy_ids=("plan_a",),
        no_overrides_plan=no_overrides_plan,
        overrides_plan=overrides_plan,
        metadata={"key": "value"},
    )

    plan.cleanup()

    assert no_overrides_plan.cleanup_called is True
    assert overrides_plan.cleanup_called is True
    assert not hasattr(plan, "metadata")


def test_spell_codegen_planner_cleanup_cleans_builder_and_drops_owned_refs() -> None:
    """Planner cleanup should clean the owned builder and drop both owned references."""
    planner = SpellCodegenPlanner()
    builder = _PlanBuilderProbe(_PlanStrategyProbe("selected_plan"))
    planner._strategy_builder = builder
    planner._discovery_system = object()

    planner.cleanup()

    assert builder.cleanup_called is True
    assert not hasattr(planner, "_strategy_builder")
    assert not hasattr(planner, "_discovery_system")
