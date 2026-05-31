from typing import TYPE_CHECKING, ClassVar

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
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
        Read the artifact-owned `SpellCodegenModel`, create one neutral
        `SpellCodegenPlan` container, run planner strategies, and publish the
        result back onto `SpellCompilerArtifact`.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_strategy_builder",
    ]

    def __init__(self) -> None:
        """
        Build one planner with an owned strategy builder.
        """
        super().__init__()
        self._strategy_builder = SpellCodegenPlanStrategyBuilder()

    def cleanup(self) -> None:
        """
        Deterministically release planner-owned state.

        Contract:
            - Idempotent.
            - Cleans the owned strategy builder directly.
            - Drops the planner's only owned reference so later use fails
              honestly through `check_cleaned()`.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._strategy_builder.cleanup()
        del self._strategy_builder

    def build(
            self,
            artifact: "SpellCompilerArtifact",
    ) -> None:
        """
        Fit and publish the planner output for the supplied artifact.

        Contract:
            - Reads `artifact._spell_codegen_model`.
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
        strategy_names = self._strategy_builder.registered_strategy_names()
        strategies = self._strategy_builder.get_strategies(strategy_names)
        for strategy in strategies:
            strategy.apply(spell_codegen_model, spell_codegen_plan)
            spell_codegen_plan.plan_strategy_ids = (
                spell_codegen_plan.plan_strategy_ids + (strategy.strategy_id,)
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
            no_overrides_plan=None,
            overrides_plan=None,
            mutation_overrides_plan=None,
            metadata={},
        )
