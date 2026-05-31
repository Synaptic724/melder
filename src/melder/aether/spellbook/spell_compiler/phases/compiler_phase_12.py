from typing import TYPE_CHECKING

from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor import (
    SpellArtifactProcessor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation.codegen_creation_system import (
    CodegenCreationSystem,
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
        assembling the full processor state, planner output, and the
        compiler-owned codegen-creation artifact.

    Contract:
        - Slot-only phase surface with no explicit `__init__`.
        - Consumes the full `SpellCompilerArtifact` surface plus the required
          runtime-owned `Spell` facts.
        - Stores compiler-owned codegen model, codegen plan, and codegen
          creation outputs back on the artifact.
        - Leaves old compiler-facing Phase 13 surfaces present, but the new
          runtime seam is produced here.

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
            state and storing the compiler-owned codegen plan plus codegen
            creation artifact for the current spell.

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
            - Best-effort cleans superseded generic compiler outputs after the
              new ones are stored.
            - Does not force analyzer wiring into the live compiler path yet.
            - Returns early when the analyzer-owned occurrence graph has not
              been produced yet.
            - Produces the new runtime creation handoff artifact consumed by
              `CreationContextBuilder`.
        """
        _ = spellbook

        if artifact._occurrence_graph_analysis is None:
            return

        processor = SpellArtifactProcessor()
        processor.process(spell, artifact)
        SpellCodegenPlanner().build(artifact)
        CodegenCreationSystem().build(artifact)

