from typing import TYPE_CHECKING

from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery_system import (
    CodegenCreationDiscoverySystem,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation import (
    SpellCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.spell_codegen_strategy_builder import (
    SpellCodegenStrategyBuilder,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )


class CodegenCreationSystem(Cleanable):
    """
    Codegen creation facade over artifact-owned model and plan truth.

    Purpose:
        Read `artifact._spell_codegen_model` and `artifact._spell_codegen_plan`,
        run codegen creation discovery, resolve the selected codegen strategy,
        and publish `artifact._spell_codegen_creation`.

    Contract:
        - Owns the discovery system and strategy builder.
        - Does not implement emitted-code behavior itself.
        - Publishes a neutral `SpellCodegenCreation` and lets the selected
          strategy chain populate it.
    """

    __slots__ = [
        "_discovery_system",
        "_strategy_builder",
    ]

    def __init__(self) -> None:
        """
        Build one codegen creation system facade.
        """
        super().__init__()
        self._discovery_system = CodegenCreationDiscoverySystem()
        self._strategy_builder = SpellCodegenStrategyBuilder()

    def cleanup(self) -> None:
        """
        Deterministically release facade-owned state.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._strategy_builder.cleanup()
        del self._strategy_builder
        del self._discovery_system

    def build(
            self,
            artifact: "SpellCompilerArtifact",
    ) -> None:
        """
        Fit and publish the codegen creation output for the supplied artifact.

        Contract:
            - Reads `artifact._spell_codegen_model`.
            - Reads `artifact._spell_codegen_plan`.
            - Runs one ordered creation-strategy chain chosen by discovery.
            - Publishes `artifact._spell_codegen_creation`.
            - Does not return the output object directly.
        """
        spell_codegen_model = artifact._spell_codegen_model
        if spell_codegen_model is None:
            raise RuntimeError(
                "CodegenCreationSystem requires artifact._spell_codegen_model first."
            )
        spell_codegen_plan = artifact._spell_codegen_plan
        if spell_codegen_plan is None:
            raise RuntimeError(
                "CodegenCreationSystem requires artifact._spell_codegen_plan first."
            )

        previous_spell_codegen_creation = artifact._spell_codegen_creation
        spell_codegen_creation = SpellCodegenCreation(
            selected_strategy_ids=(),
            discovery_reason=None,
            resolve_route_key=None,
            fast_transient_no_overrides_enabled=False,
            no_overrides_executor=None,
            no_overrides_executor_signature=None,
            override_targeting=None,
            override_plan_signature=None,
            override_path_registry=None,
            override_plan_rows=None,
            override_root_spell_id=None,
            override_spell_lookup=None,
            override_empty_shape_key=None,
            override_baseline_executor=None,
            metadata={},
        )
        discovery = self._discovery_system.discover(
            spell_codegen_model,
            spell_codegen_plan,
        )
        spell_codegen_creation.selected_strategy_ids = (
            discovery.selected_strategy_ids
        )
        spell_codegen_creation.discovery_reason = discovery.discovery_reason
        selected_strategies = self._strategy_builder.get_strategies(
            discovery.selected_strategy_ids
        )
        for selected_strategy in selected_strategies:
            selected_strategy.apply(
                spell_codegen_model,
                spell_codegen_plan,
                spell_codegen_creation,
            )
        artifact._spell_codegen_creation = spell_codegen_creation
        if (
                previous_spell_codegen_creation is not None
                and previous_spell_codegen_creation is not spell_codegen_creation
        ):
            previous_spell_codegen_creation.cleanup()
