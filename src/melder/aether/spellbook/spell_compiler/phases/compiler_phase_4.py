import time
from typing import TYPE_CHECKING, Optional



from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import (
    SpellState,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import (
    SpellValidity,
)
from melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)
from melder.aether.spellbook.spell_compiler.phases.utility import (
    CompilerPhaseUtility,
)

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import (
        SpellSystemStates,
    )
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )
    from melder.aether.spellbook.spell_compiler.validation.validation_system import (
        SpellValidationSystem,
    )
    from melder.utilities.synchronization.cancellation_event_signal import (
        CancellationEvent,
    )



class CompilerPhase4:
    """
    Compiler phase 4 surface.

    Purpose:
        Expose the current structural-validation behavior through a compiler-
        owned phase class.

    Contract:
        - Slot-only phase surface with no explicit `__init__`.
        - Directly ports the canonical `SpellCrafter` phase-4 behavior.
        - Does not own spell, artifact, validator, or runtime collaborator
          lifecycle.
    """

    __slots__ = ()

    def run(
            self,
            spell: Spell,
            artifact: SpellCompilerArtifact,
            spell_validator: SpellValidationSystem,
            spell_system_states: Optional[SpellSystemStates],
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 4 - Per-spell validation using SpellValidationSystem.

        Responsibilities:
            * Assume Phases 1-3 have completed for this Spell.
            * Delegate to :class:`SpellValidationSystem` to validate this spell
              using:
                  - Phase 1 requirements,
                  - Phase 2 symbolic graph,
                  - Phase 3 resolution frame.
            * Cache the resulting :class:`SpellValidationResult` and expose it
              via the artifact validation fields and broken flag.
            * Update global structural validity (`SpellSystemState`) when
              available, including gating spells with missing SpellContract
              providers.

        Contracts:
            * Does **not** call Phases 1-3. If any of the required artifacts
              are missing, this method raises.
            * Does **not** mutate the Spell or build any DAGs. It only records
              validation outcome and diagnostics on this compiler artifact.
            * If the SpellSystemState is no longer valid
              (unknown/gated/invalid), the validation is re-run even if this
              phase is previously completed.
            * Returns `None`; callers rely on the stored validation result and
              flags instead of a direct return value.

        Args:
            spell:
                Spell whose Phase 4 validation should run.
            artifact:
                Compiler artifact receiving phase-4 validation state.
            spell_validator:
                Validator collaborator used to validate the spell-local phase
                artifacts.
            spell_system_states:
                Optional spell-system-state registry used to publish structural
                validity changes.
            cancel_event:
                Optional cancellation signal shared across the scheduler.
        """
        artifact.check_cleaned()
        CompilerPhaseUtility.throw_if_cancelled(cancel_event)

        # If we've already validated and the structural state is still valid, do nothing.
        if artifact._validated_phase4 and artifact._validation_result_phase4 is not None:
            if spell_system_states is not None and spell.spell_index is not None:
                state = spell_system_states.get_by_index_id(spell.spell_index.id)
                if state is None or state.validity is SpellValidity.valid:
                    return
            else:
                return

        # Hard contract: Phases 1-3 must have been run explicitly.
        if (
                artifact._requirements is None
                or artifact._symbolic_graph is None
                or artifact._resolution_frame is None
        ):
            raise RuntimeError(
                "SpellCrafter Phase 4: cannot run validation before Phases 1-3 "
                "have completed."
            )

        # Use the explicit SpellValidationSystem collaborator.
        result = spell_validator.validate_spell(
            spell=spell,
            requirements=artifact._requirements,
            symbolic_graph=artifact._symbolic_graph,
            resolution_frame=artifact._resolution_frame,
            cancel_event=cancel_event,
        )

        # Cache result + flags on the artifact.
        artifact._validation_result_phase4 = result
        artifact._validated_phase4 = True

        # For now: any error -> broken. You can refine this later via severity.
        artifact._is_broken = result.has_errors
        has_contract_missing_provider = False
        for issue in result.issues:
            if issue.code == "SPELL_CONTRACT_MISSING_PROVIDER":
                has_contract_missing_provider = True

        # Update global structural validity for this lineage.
        if spell_system_states is not None and spell.spell_index is not None:
            state = spell_system_states.get_by_index_id(spell.spell_index.id)
            if state is not None:
                if artifact._is_broken:
                    # First-fail semantics: validation errors make the lineage invalid.
                    state.set_validity(
                        SpellValidity.invalid,
                        change_reason=SpellStateChangeReason.validation_failed,
                    )
                else:
                    state.clear_dirty(time.time())
                    if has_contract_missing_provider:
                        state.set_validity(
                            SpellValidity.gated,
                            change_reason=SpellStateChangeReason.contract_unvalidated,
                            flags_to_add=[SpellState.contract_unvalidated],
                    )
                    else:
                        # Structural pass with no gated issues -> mark valid.
                        state.set_validity(
                            SpellValidity.valid,
                            change_reason=SpellStateChangeReason.validation_passed,
                            flags_to_remove=[SpellState.contract_unvalidated],
                        )
        SharedCompilerExecutions.capture_phase2_5_codegen_ir(
            spell,
            artifact,
        )
