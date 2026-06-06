from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )
    from melder.utilities.synchronization.cancellation_event_signal import (
        CancellationEvent,
    )



from melder.aether.spellbook.spell_compiler.phases.utility import (
    CompilerPhaseUtility,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements_finder import (
    SpellRequirementsFinder,
)



class CompilerPhase1:
    """
    Compiler phase 1 surface.

    Purpose:
        Expose the current requirements-extraction behaviour through a
        compiler-owned phase class.

    Contract:
        - Slot-only phase surface with no explicit `__init__`.
        - Directly ports the canonical `SpellCrafter` phase-1 behavior.
        - Does not own spell, artifact, or runtime collaborator lifecycle.
    """

    __slots__ = ()

    @staticmethod
    def _build_phase1_requirements_shape_profile(requirements: Any) -> Dict[str, Any]:
        """
        Build a lightweight Phase 1 shape profile from requirements output.

        Purpose:
            Capture parameter and DI-shape facts at the point where Phase 1 has
            already classified them, so later strategy selection can consume
            compiler-owned shape truth without rewalking requirement structures.

        Contract:
            - Reads requirement rows exactly once after they are built.
            - Stores only count/histogram style facts needed for later strategy
              selection.
            - Returns deterministic tuple-backed rows for stable artifact
              storage.

        Args:
            requirements:
                Phase 1 `SpellRequirements` output for the current spell.

        Returns:
            Dict[str, Any]:
                Cheap requirements-shape summary for later compiler stages.
        """
        parameters = requirements.parameters
        di_shape_counts: Dict[str, int] = {}
        optional_parameter_count = 0
        for parameter in parameters:
            di_shape_name = parameter.di_shape.name
            di_shape_counts[di_shape_name] = (
                di_shape_counts.get(di_shape_name, 0) + 1
            )
            if parameter.is_optional:
                optional_parameter_count += 1

        return {
            "parameter_count": len(parameters),
            "optional_parameter_count": optional_parameter_count,
            "plain_parameter_count": di_shape_counts.get(ParameterDIShape.PLAIN.name, 0),
            "single_annotation_parameter_count": di_shape_counts.get(
                ParameterDIShape.SINGLE_BY_ANNOTATION.name,
                0,
            ),
            "collection_parameter_count": di_shape_counts.get(
                ParameterDIShape.COLLECTION_BY_ANNOTATION.name,
                0,
            ),
            "spellmap_default_parameter_count": di_shape_counts.get(
                ParameterDIShape.SPELLMAP_DEFAULT.name,
                0,
            ),
            "spell_contract_parameter_count": di_shape_counts.get(
                ParameterDIShape.SPELL_CONTRACT.name,
                0,
            ),
            "di_shape_counts": tuple(sorted(di_shape_counts.items())),
        }

    def run(
            self,
            spell: Spell,
            artifact: SpellCompilerArtifact,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 1 - Analyze the Spell constructor and capture DI requirements.

        Responsibilities:
            * Inspect the bound Spell's constructor and classify every
              parameter into a: class:`ParameterDIShape` (normal DI, SpellMap,
              contracts, etc.).
            * Build a: class:`SpellRequirements` object that records
              per-parameter metadata (name, position, shape, optionality,
              annotations).
            * Store the requirements on this compiler artifact
              (`artifact._requirements`) for later phases to consume.

        Contracts:
            * Must only be called for a Spell that is fully constructed and
              attached to a Spellbook.
            * Does **not** call any other phases. The caller is responsible for
              running phases in order.
            * Does **not** mutate the Spell, SpellSystemStates, or any DAG
              structures. It only updates this compiler artifact's phase-1
              state.
            * Does not return a value; consumers read
              `artifact._requirements`.

        Args:
            spell:
                Spell whose constructor requirements are being extracted.
            artifact:
                Compiler artifact receiving phase-1 output.
            cancel_event:
                Optional cancellation signal shared across the scheduler.
        """
        artifact.check_cleaned()
        CompilerPhaseUtility.throw_if_cancelled(cancel_event)

        if artifact._requirements is not None:
            return

        finder = SpellRequirementsFinder(spell)
        requirements = finder.build_requirements(cancel_event=cancel_event)
        # We deliberately do not call finder.cleanup() here, because the finder
        # owns the same SpellRequirements instance we are going to retain.
        artifact._requirements = requirements
        artifact._requirements_shape_profile_phase1 = (
            self._build_phase1_requirements_shape_profile(requirements)
        )
