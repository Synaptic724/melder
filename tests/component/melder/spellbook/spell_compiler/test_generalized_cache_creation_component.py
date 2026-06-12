"""Component tests for the generalized_cache phase-11 family selection."""

from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery import (
    CodegenCreationDiscovery,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery_strategy_builder import (
    CodegenCreationDiscoveryStrategyBuilder,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery_system import (
    CodegenCreationDiscoverySystem,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.spell_codegen_strategy_builder import (
    SpellCodegenStrategyBuilder,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized_cache.generalized_cache_codegen_creation_strategy import (
    GeneralizedCacheCodegenCreationStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


def _build_generalized_plan() -> SpellCodegenPlan:
    """Build one minimal generalized planner output shell for discovery slices."""
    return SpellCodegenPlan(
        processor_strategy_ids=(),
        plan_strategy_ids=("generalized_codegen_plan",),
        no_overrides_plan=None,
        overrides_plan=None,
        metadata={"selected_strategy_id": "generalized_codegen_plan"},
    )


def test_component_generalized_cache_discovery_claims_generalized_plans() -> None:
    """Every generalized plan must now route to the generalized_cache family."""
    discovery = CodegenCreationDiscoverySystem().discover(
        object(),
        _build_generalized_plan(),
    )

    assert isinstance(discovery, CodegenCreationDiscovery)
    assert discovery.selected_strategy_ids == (
        "generalized_cache_codegen_creation",
    )
    assert discovery.discovery_reason == (
        "generalized_plan_generalized_cache_family"
    )


def test_component_generalized_cache_discovery_declines_non_generalized_plan() -> None:
    """Non-generalized plans must keep routing to their owning families."""
    discovery = CodegenCreationDiscoverySystem().discover(
        object(),
        SpellCodegenPlan(
            processor_strategy_ids=(),
            plan_strategy_ids=("generalized_solo_codegen_plan",),
            no_overrides_plan=None,
            overrides_plan=None,
            metadata={"selected_strategy_id": "generalized_solo_codegen_plan"},
        ),
    )

    assert discovery.selected_strategy_ids == (
        "solo_codegen_creation",
    )


def test_component_generalized_cache_discovery_registers_ahead_of_generalized() -> None:
    """Discovery registration order must keep the new family claiming first.

    The legacy generalized discovery strategy stays registered behind the
    generalized_cache strategy as the rollback seam.
    """
    registered = CodegenCreationDiscoveryStrategyBuilder().registered_strategy_names()

    assert "generalized_cache_codegen_creation_discovery" in registered
    assert "generalized_codegen_creation_discovery" in registered
    assert registered.index(
        "generalized_cache_codegen_creation_discovery"
    ) < registered.index("generalized_codegen_creation_discovery")


def test_component_generalized_cache_creation_strategy_is_registered() -> None:
    """The creation registry must resolve the generalized_cache family facade."""
    strategy = SpellCodegenStrategyBuilder().get_strategy(
        "generalized_cache_codegen_creation"
    )

    assert isinstance(strategy, GeneralizedCacheCodegenCreationStrategy)
    assert strategy.strategy_id == "generalized_cache_codegen_creation"
