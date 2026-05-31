from typing import TYPE_CHECKING

from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor import (
    SpellArtifactProcessor,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_strategy_builder import (
    SpellArtifactProcessorStrategyBuilder,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_planner import (
    SpellCodegenPlanner,
)

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )


class CompilerPhase12:
    """
    Compiler phase 12 scaffolded strategy/right-sizing surface.

    Purpose:
        Provide the first real compiler-owned Phase 12 execution surface by
        assembling the full processor state and the first compiler-owned
        codegen-plan artifact.

    Contract:
        - Slot-only phase surface with no explicit `__init__`.
        - Consumes the full `SpellCompilerArtifact` surface plus the required
          runtime-owned `Spell` facts.
        - Stores compiler-owned Phase 12 processor-state and codegen-plan
          outputs back on the artifact.
        - Leaves Phase 13 and `CreationContext` consumers untouched in this
          scaffold slice.

    Ownership:
        - Owns no spell/runtime/compiler artifacts.
        - Orchestrates build/store work over artifact-owned Phase 12 outputs.
    """

    __slots__ = ()

    def run(
            self,
            spellbook: "Spellbook",
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
    ) -> None:
        """
        Phase 12 - scaffolded artifact processing and codegen-plan build.

        Purpose:
            Move Phase 12 out of no-op status by assembling the full processor
            state and storing the first compiler-owned codegen plan for the
            current spell.

        Args:
            spellbook:
                Current spellbook compiler context.
            spell:
                Spell currently moving through compiler phases.
            artifact:
                Compiler artifact for the spell. Receives the new Phase 12
                processor-state and codegen-plan outputs.

        Returns:
            None.

        Contract:
            - Replaces any previous Phase 12 scaffold outputs on the artifact.
            - Best-effort cleans superseded Phase 12 objects after the new ones
              are stored.
            - Does not force analyzer wiring into the live compiler path yet.
            - Returns early when the analyzer-owned occurrence graph has not
              been produced yet.
            - Does not mutate Phase 13 or runtime consumer wiring in this slice.
        """
        _ = spellbook

        if artifact._occurrence_graph_analysis is None:
            return

        previous_processor_state = artifact._phase12_processor_state
        previous_codegen_plan = artifact._phase12_codegen_plan

        processor = SpellArtifactProcessor(
            strategy_builder=SpellArtifactProcessorStrategyBuilder(),
        )
        codegen_model = processor.process(spell, artifact)
        codegen_plan = SpellCodegenPlanner().build(codegen_model)

        artifact._phase12_processor_state = codegen_model
        artifact._phase12_codegen_plan = codegen_plan

        if (
                previous_processor_state is not None
                and previous_processor_state is not codegen_model
        ):
            try:
                previous_processor_state.cleanup()
            except Exception:
                pass
        if previous_codegen_plan is not None and previous_codegen_plan is not codegen_plan:
            try:
                previous_codegen_plan.cleanup()
            except Exception:
                pass

