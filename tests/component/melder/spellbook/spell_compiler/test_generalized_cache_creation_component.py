"""Component tests for the promoted manifest-first generalized family.

Note: this file kept its historical name from the generalized_cache
experiment; the family it covers is now `generalized_codegen_creation`.
Safe to rename to `test_generalized_manifest_creation_component.py`.
"""

from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery import (
    CodegenCreationDiscovery,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery_system import (
    CodegenCreationDiscoverySystem,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.spell_codegen_strategy_builder import (
    SpellCodegenStrategyBuilder,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.generalized_codegen_creation_strategy import (
    GeneralizedCodegenCreationStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.steps.generalized_lazy_door_step import (
    GeneralizedLazyDoorStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.steps.generalized_manifest_step import (
    GeneralizedManifestStep,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


def test_component_generalized_discovery_routes_generalized_plan_to_manifest_family() -> None:
    """Generalized plans resolve to the (now manifest-first) generalized family."""
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


def test_component_generalized_strategy_is_manifest_first() -> None:
    """The registered generalized strategy runs manifest + lazy-door steps."""
    strategy = SpellCodegenStrategyBuilder().get_strategy(
        "generalized_codegen_creation"
    )

    assert isinstance(strategy, GeneralizedCodegenCreationStrategy)
    assert strategy.strategy_id == "generalized_codegen_creation"
    step_types = tuple(type(step) for step in strategy._steps)
    assert step_types == (GeneralizedManifestStep, GeneralizedLazyDoorStep)
    step_ids = tuple(step.step_id for step in strategy._steps)
    assert step_ids == ("generalized_manifest", "generalized_lazy_doors")


def test_component_generalized_sidecar_family_is_unregistered() -> None:
    """The generalized_cache sidecar must be gone from both registries."""
    creation_names = SpellCodegenStrategyBuilder().registered_strategy_names()
    assert "generalized_cache_codegen_creation" not in creation_names

    from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery_strategy_builder import (
        CodegenCreationDiscoveryStrategyBuilder,
    )

    discovery_names = (
        CodegenCreationDiscoveryStrategyBuilder().registered_strategy_names()
    )
    assert "generalized_cache_codegen_creation_discovery" not in discovery_names
