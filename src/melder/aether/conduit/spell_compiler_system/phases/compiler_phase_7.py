from typing import Optional, Set

from mypy_extensions import mypyc_attr

from melder.aether.conduit.spell_compiler_system.phases.compiler_phase_5 import (
    CompilerPhase5,
)
from melder.aether.conduit.spell_compiler_system.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.interfaces.ispellbook import ISpellbook
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
    ):
        """
        Return the Phase 5 root-blueprint map or raise.
        """
        root_blueprints = artifact._entire_dag_blueprint_phase5
        if root_blueprints is None:
            raise RuntimeError(
                "SpellCrafter Phase 5 root blueprint map is required."
            )
        return root_blueprints

    @staticmethod
    def _get_required_crafter_from_spell(spell: ISpell):
        """
        Return the live crafter attached to one spell or raise.
        """
        crafter = spell._crafter
        if crafter is None:
            raise RuntimeError("Spell must have a live SpellCrafter.")
        return crafter

    def run(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            spellbook: ISpellbook,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
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
            spell,
            artifact,
            spellbook,
            conduit_id,
        )

    def run_local(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            spellbook: ISpellbook,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
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
            spell:
                The local spell context driving this phase.
            artifact:
                Local compiler artifact with Phase-5 root blueprints in scope.
            spellbook:
                Visible spellbook owning this artifact.
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal (unused in wiring path).
        Returns:
            None.
        """
        artifact.check_cleaned()
        # Stage 1: install local change-control upsert wiring.
        self._ensure_change_control_ready_local(
            spell,
            artifact,
            spellbook,
            conduit_id,
        )

    def _ensure_change_control_ready(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            spellbook: ISpellbook,
            conduit_id: str,
    ) -> None:
        """
        Internal helper to (re)wire change-control after Phase 5 artifacts exist.

        Contract:
            - Requires Phase-5 root-blueprint artifacts to be present.
            - Rebuilds conduit-scoped component-of mappings for owned root ids.
            - Installs a change-control revalidator if missing.
        Args:
            spell:
                Top-level spell used as a context anchor.
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

            This closure is registered on the conduit’s change-control slot, so
            later dirty-root events can drive a full spell-level recompilation
            through the current Spellbook/runtime view.
            """
            validated_roots: Set[str] = set()
            for root_id in dirty_roots:
                spell_instance = spellbook._spell_id_pool[root_id]
                crafter = self._get_required_crafter_from_spell(
                    spell_instance
                )
                crafter.run_all_phases(
                    conduit_id=conduit_id,
                    cancel_event=cancel_event,
                )
                validated_roots.add(root_id)

            return validated_roots

        if not change_control_manager.has_revalidator_for_conduit(conduit_id):
            change_control_manager.set_revalidator(
                conduit_id,
                _revalidate_dirty_roots,
            )

    def _ensure_change_control_ready_local(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            spellbook: ISpellbook,
            conduit_id: str,
    ) -> None:
        """
        Internal helper to upsert local change-control wiring after local Phase 5.

        Contract:
            - Requires local Phase-5 root blueprints on this artifact.
            - Uses component-of upsert semantics to preserve unrelated roots.
            - Registers the same revalidator contract as frame-wide wiring.
        Args:
            spell:
                The local spell entrypoint context.
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
            """
            validated_roots: Set[str] = set()
            for root_id in dirty_roots:
                spell_instance = spellbook._spell_id_pool[root_id]
                crafter = self._get_required_crafter_from_spell(
                    spell_instance
                )
                crafter.run_all_phases(
                    conduit_id=conduit_id,
                    cancel_event=cancel_event,
                )
                validated_roots.add(root_id)

            return validated_roots

        if not change_control_manager.has_revalidator_for_conduit(conduit_id):
            change_control_manager.set_revalidator(
                conduit_id,
                _revalidate_dirty_roots,
            )
