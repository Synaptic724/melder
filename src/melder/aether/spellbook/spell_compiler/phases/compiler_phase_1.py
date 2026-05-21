from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )
    from melder.utilities.synchronization.cancellation_event_signal import (
        CancellationEvent,
    )

from mypy_extensions import mypyc_attr

from melder.aether.spellbook.spell_compiler.phases.utility import (
    CompilerPhaseUtility,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements_finder import (
    SpellRequirementsFinder,
)


@mypyc_attr(native_class=True)
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
