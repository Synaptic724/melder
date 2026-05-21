from typing import TYPE_CHECKING, Optional, Set

if TYPE_CHECKING:
    from melder.aether.spellbook.spellbook import Spellbook

from mypy_extensions import mypyc_attr

from melder.aether.spellbook.spell_compiler.phases.compiler_phase_5 import (
    CompilerPhase5,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


@mypyc_attr(native_class=True)
class CompilerPhase7:
    """
    Compiler phase 7 surface.

    Purpose:
        Expose the current change-control wiring behavior through a compiler-
        owned phase class.

    Contract:
        - Slot-only phase surface with no explicit `__init__`.
        - Directly ports the canonical `SpellCrafter` phase-7 behavior.
        - Does not own spell, artifact, spellbook, or runtime collaborator
          lifecycle.
    """

    __slots__ = ()

    def _get_required_entire_dag_blueprint_phase5(
            self,
            artifact: SpellCompilerArtifact,
    ) :
        """
            Return the Phase 5 root-blueprint map or raise.
            
            Returns:
                Dict[str, IRootResolutionBlueprint]: Root blueprint map keyed by
                root spell id.
        """
        root_blueprints = artifact._entire_dag_blueprint_phase5
        if root_blueprints is None:
            raise RuntimeError(
                "SpellCrafter Phase 5 root blueprint map is required."
            )
        return root_blueprints

    def run_frame_wide(
            self,
            artifact: SpellCompilerArtifact,
            spellbook: Spellbook,
            conduit_id: str,
    ) -> None:
        """
        Phase 7 - Change-control wiring.

        Behaviour (conduit-scoped, idempotent):
            - Ensure the ChangeControlManager is present for the frame.
            - Ensure the component-of index is (re)built from the Phase-5 root
              blueprints.
            - Ensure the revalidator hook is registered.
        """
        artifact.check_cleaned()
        # Stage 1: install conduit-wide component-of rebuild wiring.
        self._ensure_change_control_ready(
            artifact,
            spellbook,
            conduit_id,
        )

    def run_local(
            self,
            artifact: SpellCompilerArtifact,
            spellbook: Spellbook,
            conduit_id: str,
    ) -> None:
        """
        Phase 7 local entrypoint.

        Purpose:
            Refresh change-control wiring only for locally revalidated roots.
        Contract:
            - Upserts component-of mappings for local root blueprints.
            - Preserves mappings for unrelated roots on the conduit.
            - Registers a revalidator when missing.
        Args:
            artifact:
                Local compiler artifact with Phase-5 root blueprints in scope.
            spellbook:
                Visible spellbook owning this artifact.
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
        Returns:
            None.
        """
        artifact.check_cleaned()
        # Stage 1: install local change-control upsert wiring.
        self._ensure_change_control_ready_local(
            artifact,
            spellbook,
            conduit_id,
        )

    def _ensure_change_control_ready(
            self,
            artifact: SpellCompilerArtifact,
            spellbook: Spellbook,
            conduit_id: str,
    ) -> None:
        """
        Internal helper to (re)wire change-control after Phase 5 artifacts exist.

        Contract:
            - Requires Phase-5 root-blueprint artifacts to be present.
            - Rebuilds conduit-scoped component-of mappings for owned root ids.
            - Installs a change-control revalidator if missing.
        Args:
            artifact:
                Conduit-level artifact containing the Phase-5 blueprint map.
            spellbook:
                Active spellbook supplying the change-control manager.
            conduit_id:
                Conduit identifier used for component-of registration.
        """
        frame_name = CompilerPhase5()._get_required_spellbook_frame_name(spellbook)
        change_control_manager = spellbook._aether._get_change_control_manager(frame_name)
        owned_root_blueprints = CompilerPhase5()._filter_root_blueprints_to_owned(
            spellbook,
            self._get_required_entire_dag_blueprint_phase5(artifact),
        )
        change_control_manager.rebuild_component_of(
            conduit_id,
            {root_id: blueprint for root_id, blueprint in owned_root_blueprints.items()},
        )

        def _revalidate_dirty_roots(
                dirty_roots: Set[str],
                cancel_event: Optional[CancellationEvent],
        ) -> Set[str]:
            """
            Revalidate dirty roots for the conduit-wide Phase 7 hook.

            This closure is registered on the conduit change-control slot, so
            later dirty-root events can drive a full spell-level recompilation
            through the current Spellbook/runtime view.

            Contract:
                - Resolves each root spell from the live spellbook `_spell_id_pool`.
                - Reuses the compiler-system front facade for each root.
                - Re-runs foundational phases via `run_all_phases(...)` using
                  explicit `spellbook` and `spell` inputs instead of reaching
                  back through the spell-owned `SpellCrafter`.
                - Returns only successfully revalidated root ids.
            """
            validated_roots: Set[str] = set()
            for root_id in dirty_roots:
                from melder.aether.spellbook.spell_compiler.spell_compiler_system import SpellCompilerSystem

                spell_instance = spellbook._spell_id_pool[root_id]
                compiler_system = SpellCompilerSystem()
                try:
                    compiler_system.run_all_phases(
                        spellbook,
                        spell_instance,
                        conduit_id=conduit_id,
                        cancel_event=cancel_event,
                    )
                finally:
                    compiler_system.cleanup()
                validated_roots.add(root_id)

            return validated_roots

        if not change_control_manager.has_revalidator_for_conduit(conduit_id):
            change_control_manager.set_revalidator(
                conduit_id,
                _revalidate_dirty_roots,
            )

    def _ensure_change_control_ready_local(
            self,
            artifact: SpellCompilerArtifact,
            spellbook: Spellbook,
            conduit_id: str,
    ) -> None:
        """
        Internal helper to upsert local change-control wiring after local Phase 5.

        Contract:
            - Requires local Phase-5 root blueprints on this artifact.
            - Uses component-of upsert semantics to preserve unrelated roots.
            - Registers the same revalidator contract as frame-wide wiring.
        Args:
            artifact:
                Local artifact containing the scoped Phase-5 root blueprint map.
            spellbook:
                Active spellbook supplying the change-control manager.
            conduit_id:
                Conduit identifier used for conduit-local component-of updates.
        """
        frame_name = CompilerPhase5()._get_required_spellbook_frame_name(spellbook)
        change_control_manager = spellbook._aether._get_change_control_manager(frame_name)
        owned_root_blueprints = CompilerPhase5()._filter_root_blueprints_to_owned(
            spellbook,
            self._get_required_entire_dag_blueprint_phase5(artifact),
        )
        change_control_manager.upsert_component_of(
            conduit_id,
            {root_id: blueprint for root_id, blueprint in owned_root_blueprints.items()},
        )

        def _revalidate_dirty_roots(
                dirty_roots: Set[str],
                cancel_event: Optional[CancellationEvent],
        ) -> Set[str]:
            """
            Revalidate dirty roots for the local Phase 7 change-control hook.

            This local variant mirrors the frame-wide revalidation contract but
            is installed from the local wiring path, so scoped revalidation can
            still hand dirty roots back into the full spell-phase pipeline for
            this conduit.

            Contract:
                - Resolves each root spell from the live spellbook `_spell_id_pool`.
                - Reuses the compiler-system front facade for each root.
                - Re-runs foundational phases via `run_all_phases(...)` using
                  explicit `spellbook` and `spell` inputs instead of reaching
                  back through the spell-owned `SpellCrafter`.
                - Returns only successfully revalidated root ids.
            """
            validated_roots: Set[str] = set()
            for root_id in dirty_roots:
                from melder.aether.spellbook.spell_compiler.spell_compiler_system import SpellCompilerSystem

                spell_instance = spellbook._spell_id_pool[root_id]
                compiler_system = SpellCompilerSystem()
                try:
                    compiler_system.run_all_phases(
                        spellbook,
                        spell_instance,
                        conduit_id=conduit_id,
                        cancel_event=cancel_event,
                    )
                finally:
                    compiler_system.cleanup()
                validated_roots.add(root_id)

            return validated_roots

        if not change_control_manager.has_revalidator_for_conduit(conduit_id):
            change_control_manager.set_revalidator(
                conduit_id,
                _revalidate_dirty_roots,
            )


