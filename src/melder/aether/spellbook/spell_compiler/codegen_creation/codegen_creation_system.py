from melder.aether.spellbook.spell_compiler.codegen_creation.codegen_creation_discovery_system import (
    CodegenCreationDiscoverySystem,
)
from melder.aether.spellbook.spell_compiler.codegen_creation.spell_codegen_creation import (
    SpellCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation.spell_codegen_strategy_builder import (
    SpellCodegenStrategyBuilder,
)


class CodegenCreationSystem:
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
          strategy populate it.
    """

    __slots__ = [
        "_discovery_system",
        "_strategy_builder",
    ]

    def __init__(self) -> None:
        """
        Build one codegen creation system facade.
        """
        self._discovery_system = CodegenCreationDiscoverySystem()
        self._strategy_builder = SpellCodegenStrategyBuilder()

    def cleanup(self) -> None:
        """
        Deterministically release facade-owned state.
        """
        self._strategy_builder.cleanup()
        del self._strategy_builder
        del self._discovery_system

    def build(
            self,
            artifact,
    ) -> None:
        """
        Fit and publish the codegen creation output for the supplied artifact.

        Contract:
            - Reads `artifact._spell_codegen_model`.
            - Reads `artifact._spell_codegen_plan`.
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
            selected_strategy_id=None,
            discovery_reason=None,
            no_overrides_output=None,
            overrides_output=None,
            mutation_overrides_output=None,
            metadata={},
        )
        discovery = self._discovery_system.discover(
            spell_codegen_model,
            spell_codegen_plan,
        )
        selected_strategy = self._strategy_builder.get_strategy(
            discovery.selected_strategy_id
        )
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
            try:
                previous_spell_codegen_creation.cleanup()
            except Exception:
                pass
