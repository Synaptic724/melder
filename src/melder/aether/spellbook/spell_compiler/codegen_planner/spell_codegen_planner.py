from typing import TYPE_CHECKING, ClassVar

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.codegen_plan_discovery_system import (
    CodegenPlanDiscoverySystem,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan_strategy_builder import (
    SpellCodegenPlanStrategyBuilder,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )


class SpellCodegenPlanner(Cleanable):
    """
    Planner facade over artifact-owned model truth.

    Purpose:
        Read the artifact-owned `spell_codegen_model`, run discovery to choose
        the current best codegen-plan strategy, resolve that strategy through
        the builder, and publish the resulting `SpellCodegenPlan` back onto the
        artifact.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_discovery_system",
        "_strategy_builder",
    ]

    def __init__(self) -> None:
        """
        Build one planner facade with an owned discovery system and builder.
        """
        super().__init__()
        self._discovery_system = CodegenPlanDiscoverySystem()
        self._strategy_builder = SpellCodegenPlanStrategyBuilder()

    def cleanup(self) -> None:
        """
        Deterministically release planner-owned state.

        Contract:
            - Idempotent.
            - Cleans the owned strategy builder directly.
            - Drops the planner's owned references so later use fails honestly
              through `check_cleaned()`.
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
        Fit and publish the planner output for the supplied artifact.

        Contract:
            - Reads `artifact._spell_codegen_model`.
            - Uses discovery to choose the current best plan strategy.
            - Records the chosen plan family plus candidate codegen styles on
              `SpellCodegenPlan`.
            - Resolves the selected strategy through the builder.
            - Publishes `artifact._spell_codegen_plan`.
            - Does not return the plan object directly.
        """
        spell_codegen_model = artifact._spell_codegen_model
        if spell_codegen_model is None:
            raise RuntimeError(
                "SpellCodegenPlanner requires artifact._spell_codegen_model first."
            )

        previous_spell_codegen_plan = artifact._spell_codegen_plan
        spell_codegen_plan = self._build_plan(spell_codegen_model)
        discovery = self._discovery_system.discover(spell_codegen_model)
        spell_codegen_plan.metadata["selected_strategy_id"] = (
            discovery.selected_strategy_id
        )
        spell_codegen_plan.metadata["discovery_reason"] = (
            discovery.discovery_reason
        )
        spell_codegen_plan.plan_family_id = discovery.plan_family_id
        spell_codegen_plan.candidate_codegen_style_ids = (
            discovery.candidate_codegen_style_ids
        )
        spell_codegen_plan.metadata["plan_family_id"] = (
            discovery.plan_family_id
        )
        spell_codegen_plan.metadata["candidate_codegen_style_ids"] = (
            discovery.candidate_codegen_style_ids
        )
        selected_strategy = self._strategy_builder.get_strategy(
            discovery.selected_strategy_id
        )
        selected_strategy.apply(
            spell_codegen_model,
            artifact,
            spell_codegen_plan,
        )
        spell_codegen_plan.plan_strategy_ids = (
            spell_codegen_plan.plan_strategy_ids + (selected_strategy.strategy_id,)
        )

        artifact._spell_codegen_plan = spell_codegen_plan
        if (
                previous_spell_codegen_plan is not None
                and previous_spell_codegen_plan is not spell_codegen_plan
        ):
            try:
                previous_spell_codegen_plan.cleanup()
            except Exception:
                pass

    @staticmethod
    def _build_plan(
            spell_codegen_model,
    ) -> SpellCodegenPlan:
        """
        Build one neutral planner-owned codegen plan container.

        Contract:
            - Starts with empty lane payloads.
            - Carries processor provenance forward into the planner layer.
        """
        return SpellCodegenPlan(
            processor_strategy_ids=spell_codegen_model.snapshot_applied_strategy_ids(),
            plan_strategy_ids=(),
            plan_family_id=None,
            candidate_codegen_style_ids=(),
            no_overrides_plan=None,
            overrides_plan=None,
            metadata={},
        )
