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


def _build_plan(metadata: dict) -> SpellCodegenPlan:
    """Build one minimal planner output shell for discovery slices."""
    return SpellCodegenPlan(
        processor_strategy_ids=(),
        plan_strategy_ids=("generalized_codegen_plan",),
        no_overrides_plan=None,
        overrides_plan=None,
        metadata=metadata,
    )


def test_component_generalized_cache_discovery_claims_stamped_generalized_plan() -> None:
    """A stamped generalized plan should route to the generalized_cache family."""
    discovery = CodegenCreationDiscoverySystem().discover(
        object(),
        _build_plan(
            {
                "selected_strategy_id": "generalized_codegen_plan",
                "codegen_creation_family": "generalized_cache",
            }
        ),
    )

    assert isinstance(discovery, CodegenCreationDiscovery)
    assert discovery.selected_strategy_ids == (
        "generalized_cache_codegen_creation",
    )
    assert discovery.discovery_reason == (
        "metadata_selected_generalized_cache_family"
    )


def test_component_generalized_cache_discovery_declines_unstamped_plan() -> None:
    """An unstamped generalized plan must keep the existing generalized chain."""
    discovery = CodegenCreationDiscoverySystem().discover(
        object(),
        _build_plan(
            {
                "selected_strategy_id": "generalized_codegen_plan",
            }
        ),
    )

    assert discovery.selected_strategy_ids == (
        "generalized_codegen_creation",
    )


def test_component_generalized_cache_discovery_declines_non_generalized_plan() -> None:
    """A stamp on a non-generalized plan must not capture the owning family."""
    discovery = CodegenCreationDiscoverySystem().discover(
        object(),
        SpellCodegenPlan(
            processor_strategy_ids=(),
            plan_strategy_ids=("generalized_solo_codegen_plan",),
            no_overrides_plan=None,
            overrides_plan=None,
            metadata={
                "selected_strategy_id": "generalized_solo_codegen_plan",
                "codegen_creation_family": "generalized_cache",
            },
        ),
    )

    assert discovery.selected_strategy_ids == (
        "solo_codegen_creation",
    )


def test_component_generalized_cache_discovery_registers_ahead_of_generalized() -> None:
    """Discovery registration order must let the stamped family claim first."""
    registered = CodegenCreationDiscoveryStrategyBuilder().registered_strategy_names()

    assert "generalized_cache_codegen_creation_discovery" in registered
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
