from typing import Optional

from mypy_extensions import mypyc_attr

from melder.aether.conduit.spell_compiler_system.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.spell_crafter.blueprints.injection_plan import (
    InjectionPlanBuilder,
)
from melder.utilities.interfaces.ioccurrenceplan import IOccurrencePlan
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


@mypyc_attr(native_class=True)
class CompilerPhase9:
    """
    Compiler phase 9 surface.

    Purpose:
        Expose the current injection-plan build behavior through a compiler-
        owned phase class.

    Contract:
        - Slot-only phase surface with no explicit `__init__`.
        - Directly ports the canonical `SpellCrafter` phase-9 behavior.
        - Does not own spell, artifact, or runtime collaborator lifecycle.
    """

    __slots__ = ()

    def _get_required_occurrence_plan_phase8(
            self,
            artifact: SpellCompilerArtifact,
    ) -> IOccurrencePlan:
        """
        Return the Phase 8 occurrence plan or raise.

        Purpose:
            Provide the same hard Phase-8 artifact gate the original
            `SpellCrafter` phase-9 path depends on before injection-plan
            compilation can begin.

        Returns:
            IOccurrencePlan: Attached Phase 8 occurrence plan.
        """
        occurrence_plan = artifact._occurrence_plan_phase8
        if occurrence_plan is None:
            raise RuntimeError("SpellCrafter Phase 8 occurrence plan is required.")
        return occurrence_plan

    def _build_phase9_injection_plan_input_signature(
            self,
            artifact: SpellCompilerArtifact,
            *,
            occurrence_plan: Optional[IOccurrencePlan],
    ) -> Optional[str]:
        """
        Build a deterministic phase9 input signature for injection-plan reuse.

        Purpose:
            Detect phase9 semantic drift using the phase8 signature state so warm
            runs can safely skip redundant injection-plan rebuilds with minimal
            additional signature overhead.
        Contract:
            - Returns None when occurrence-plan inputs are unavailable.
            - Reuses phase8 occurrence-plan input signature when present.
            - Falls back to rebuild (None) when the phase8 signature is unavailable.
        Args:
            artifact:
                Spell-owned compiler artifact whose phase-8 signature state is
                being queried.
            occurrence_plan:
                Phase8 occurrence plan used to build phase9 injection plan.
        Returns:
            Optional[str]:
                Deterministic signature string or None when rebuild must proceed.
        """
        if occurrence_plan is None:
            return None
        return artifact._phase8_occurrence_plan_input_signature

    def _mark_phase8_11_codegen_ir_dirty(
            self,
            artifact: SpellCompilerArtifact,
    ) -> None:
        """
        Mark phase8_11 codegen export as stale.

        Purpose:
            Record that one or more Phase8-11 artifacts are changed and a new IR
            export is required before consumers read phase8_11 payloads.
        Contract:
            - Idempotent; repeated calls keep the dirty state true.
            - Does not mutate codegen payloads directly.
        Returns:
            None.
        """
        artifact._phase8_11_codegen_ir_dirty = True

    def run(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
    ) -> None:
        """
        Phase 9 - Injection plan compilation.

        Compiles an InjectionPlan for spells using Phase-8 occurrence plans.
        Existing-creation spells are treated as a no-op.

        Purpose:
            Precompute dependency-to-parameter wiring so meld can inject without
            recomputing occurrence-driven dependency paths at runtime.

        Contract:
            - Requires Phase 8 artifacts to be available.
            - Builds plan only when an occurrence plan is attached for this spell.
            - Replaces any existing InjectionPlan for this spell.
            - Does not mutate the occurrence plan.

        Args:
            spell:
                Root spell under compilation.
            artifact:
                Phase-8 artifact output holder used for signature and plan
                caching.
        Returns:
            None.

        Raises:
            RuntimeError:
                If Phase 8 artifacts are missing for this spell.
        """
        artifact.check_cleaned()
        if spell.is_existing_creation:
            return

        # Stage 1: require phase-8 plan and build phase-9 signature gate.
        occurrence_plan = self._get_required_occurrence_plan_phase8(artifact)
        injection_plan_input_signature = self._build_phase9_injection_plan_input_signature(
            artifact,
            occurrence_plan=occurrence_plan,
        )
        # Reuse the prior InjectionPlan when the deterministic phase-9 input
        # signature is unchanged.
        if (
                injection_plan_input_signature is not None
                and injection_plan_input_signature == artifact._phase9_injection_plan_input_signature
                and artifact._injection_plan_phase9 is not None
        ):
            return
        # Stage 2: rebuild injection plan and hot-swap references.
        builder = InjectionPlanBuilder(
            occurrence_plan=occurrence_plan,
        )
        plan = builder.build()

        # Hot-swap the plan without cleaning the previous object in-place.
        # Concurrent phase runners may still hold references to the prior plan.
        artifact._injection_plan_phase9 = plan
        artifact._phase9_injection_plan_input_signature = injection_plan_input_signature
        self._mark_phase8_11_codegen_ir_dirty(artifact)
