from typing import Collection, Dict, List, Mapping, Optional, Set

from mypy_extensions import mypyc_attr

from melder.aether.conduit.spell_compiler_system.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)
from melder.aether.conduit.spell_compiler_system.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.spell_crafter.system.spell_system_adjacency_builder import (
    SpellSystemAdjacencyBuilder,
)
from melder.aether.spellbook.spell_crafter.system.spell_system_adjacency_snapshot import (
    SpellSystemAdjacencySnapshot,
)
from melder.aether.spellbook.spell_crafter.system.spell_system_index import (
    SpellSystemIndex,
)
from melder.aether.spellbook.spell_crafter.system.spell_system_node import (
    SpellSystemNode,
)
from melder.aether.spellbook.spell_crafter.system.spell_system_root_blueprint_builder import (
    SpellSystemRootBlueprintBuilder,
)
from melder.aether.spellbook.spell_crafter.topology.spell_local_topology import (
    SpellLocalTopology,
)
from melder.utilities.interfaces.irootresolutionblueprint import IRootResolutionBlueprint
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.interfaces.ispellbook import ISpellbook
from melder.utilities.interfaces.ispellsystemstate import ISpellSystemState
from melder.utilities.interfaces.ispellsystemstates import ISpellSystemStates
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


@mypyc_attr(native_class=True)
class CompilerPhase5:
    """
    Static compiler phase 5 surface.

    Purpose:
        Expose the current rooted-blueprint build behavior through a compiler-
        owned phase class.

    Contract:
        - Slot-only phase surface with no explicit `__init__`.
        - Directly ports the canonical `SpellCrafter` phase-5 behavior.
        - Does not own spell, artifact, spellbook, or runtime collaborator
          lifecycle.
    """

    __slots__ = ()

    @staticmethod
    def _get_required_crafter_from_spell(spell: ISpell):
        """
        Return the live crafter attached to one spell or raise.

        Args:
            spell:
                Spell expected to own a live SpellCrafter.

        Returns:
            Any:
                The live crafter instance.

        Raises:
            RuntimeError:
                If the spell has no attached crafter.
        """
        crafter = spell._crafter
        if crafter is None:
            raise RuntimeError("Spell must have a live SpellCrafter.")
        return crafter

    def _get_required_spellbook_frame_name(self, spellbook: ISpellbook) -> str:
        """
        Resolve the owning frame name from the provided spellbook.

        Args:
            spellbook:
                Spellbook whose owning frame is required.

        Returns:
            str: Aetheric frame name.

        Raises:
            RuntimeError:
                If the spellbook does not expose a concrete frame name.
        """
        frame_name = spellbook._aetheric_frame
        if frame_name is None:
            raise RuntimeError("SpellCrafter requires a concrete owning frame name.")
        return frame_name

    def _get_required_current_spell_id(self, spell: ISpell) -> str:
        """
        Resolve the current spell version id for the bound spell.

        Args:
            spell:
                Spell expected to have a current version id.

        Returns:
            str: Current spell id.

        Raises:
            RuntimeError:
                If the spell has no current version id.
        """
        current_spell_id = spell.spell_index.current
        if current_spell_id is None:
            raise RuntimeError("SpellCrafter requires a bound spell current id.")
        return current_spell_id

    def _get_required_spell_system_states(
            self,
            spell_system_states: ISpellSystemStates,
    ) -> ISpellSystemStates:
        """
        Require a live SpellSystemStates collaborator.

        Args:
            spell_system_states:
                Candidate collaborator.

        Returns:
            ISpellSystemStates: Validated SpellSystemStates.

        Raises:
            RuntimeError:
                If the state registry is missing.
        """
        if spell_system_states is None:
            raise RuntimeError(
                "SpellCrafter requires a live SpellSystemStates surface."
            )
        return spell_system_states

    def _get_required_spell_state_by_spell_id(
            self,
            spell_system_states: ISpellSystemStates,
            spell_id: str,
    ) -> ISpellSystemState:
        """
        Resolve the spell-system state for a given spell id.

        Args:
            spell_system_states:
                Validated SpellSystemStates view.
            spell_id:
                Spell id to resolve.

        Returns:
            ISpellSystemState: Resolved state for the requested spell id.

        Raises:
            RuntimeError:
                If no spell state exists for `spell_id`.
        """
        state = self._get_required_spell_system_states(
            spell_system_states
        ).get_by_spell_id(spell_id)
        if state is None:
            raise RuntimeError(
                "SpellCrafter requires a live SpellSystemState for spell id "
                f"'{spell_id}'."
            )
        return state

    def _set_root_blueprint_phase5(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            blueprint: IRootResolutionBlueprint,
    ) -> None:
        """
        Attach the Phase 5 root blueprint for this spell.

        Contract:
            - Stores the owned-root blueprint that later validation and plan
              phases consume.
            - Refreshes Phase 2-5 exported IR.
            - Invalidates later Phase 8-11 IR caches because they depend on the
              rooted blueprint shape.
        """
        artifact.check_cleaned()
        if blueprint is None:
            raise ValueError("blueprint must not be None.")
        artifact._root_blueprint_phase5 = blueprint
        SharedCompilerExecutions.capture_phase2_5_codegen_ir(spell, artifact)
        SharedCompilerExecutions.reset_phase8_11_codegen_ir(spell, artifact)

    def _set_spell_system_index_phase5(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            index: SpellSystemIndex,
    ) -> None:
        """
        Attach the Phase 5 spell-system index for this spell.

        Contract:
            - Stores the spell-local handle to the wider system index.
            - Refreshes Phase 2-5 exported IR.
            - Invalidates later Phase 8-11 IR caches because downstream
              planning may depend on index content.
        """
        artifact.check_cleaned()
        if index is None:
            raise ValueError("index must not be None.")
        artifact._spell_system_index_phase5 = index
        SharedCompilerExecutions.capture_phase2_5_codegen_ir(spell, artifact)
        SharedCompilerExecutions.reset_phase8_11_codegen_ir(spell, artifact)

    def _collect_local_scope_spell_ids(
            self,
            *,
            root_spell_id: str,
            snapshot: SpellSystemAdjacencySnapshot,
    ) -> Set[str]:
        """
        Collect dependency-closure spell ids for local Phase 5-7 execution.

        Purpose:
            Limit local Phase 5-7 execution to the target spell and all spells
            it depends on directly or transitively.
        Contract:
            - Traverses dependency edges from root to leaves.
            - Returns only ids present in the provided snapshot.
            - Never mutates the snapshot.
        Args:
            root_spell_id:
                Target spell id whose dependency closure should be resolved.
            snapshot:
                Visibility-filtered adjacency snapshot.
        Returns:
            Set[str]:
                Target spell id plus dependency closure.
        """
        if root_spell_id not in snapshot.all_spell_ids:
            return set()

        scoped_spell_ids: Set[str] = set()
        pending: List[str] = [root_spell_id]

        while pending:
            spell_id = pending.pop()
            if spell_id in scoped_spell_ids:
                continue
            if spell_id not in snapshot.all_spell_ids:
                continue
            scoped_spell_ids.add(spell_id)
            for dependency_id in snapshot.dependencies.get(spell_id, ()):
                if dependency_id not in scoped_spell_ids:
                    pending.append(dependency_id)

        return scoped_spell_ids

    def _build_system_index_for_snapshot(
            self,
            *,
            snapshot: SpellSystemAdjacencySnapshot,
            spell_lookup: Dict[str, ISpell],
            spell_system_states: ISpellSystemStates,
    ) -> SpellSystemIndex:
        """
        Build a SpellSystemIndex for a pre-filtered adjacency snapshot.

        Purpose:
            Share index construction between frame-wide and local Phase 5 paths.
        Contract:
            - Requires every snapshot spell id to be present in ``spell_lookup``.
            - Resolves lineage ids from SpellSystemStates.
            - Does not mutate snapshot or spell_lookup.
        Args:
            snapshot:
                Snapshot to materialize into an index.
            spell_lookup:
                Visible spell_id -> spell map.
            spell_system_states:
                Borrowed SpellSystemStates surface.
        Returns:
            SpellSystemIndex:
                Index populated for all snapshot spell ids.
        """
        system_index = SpellSystemIndex()
        for spell_id, deps in snapshot.dependencies.items():
            lineage_id = self._get_required_spell_state_by_spell_id(
                spell_system_states,
                spell_id,
            ).spell_index_id
            spell_instance = spell_lookup[spell_id]

            node = SpellSystemNode(
                spell_id=spell_id,
                lineage_id=lineage_id,
                dependencies=deps,
                existence=spell_instance.existence,
                spell_type=spell_instance.spell_type,
                conduit_id=spell_instance._owner_conduit_id,
                ward_id=None,
                is_root=spell_id in snapshot.root_spell_ids,
            )
            system_index.upsert_node(node)

        return system_index

    def _attach_phase5_artifacts_for_snapshot(
            self,
            *,
            snapshot: SpellSystemAdjacencySnapshot,
            root_blueprints: Mapping[str, IRootResolutionBlueprint],
            system_index: SpellSystemIndex,
            spell_lookup: Dict[str, ISpell],
            root_builder: SpellSystemRootBlueprintBuilder,
    ) -> None:
        """
        Attach Phase 5 artifacts to all spells participating in a snapshot.

        Purpose:
            Ensure scoped spells have consistent Phase 5 artifacts before
            Phase 6-11 are executed.
        Contract:
            - Updates only spells included in ``snapshot.all_spell_ids``.
            - Existing-creation spells get index only and skip blueprints.
            - Builds fallback per-spell blueprint when not present as a root.
        Args:
            snapshot:
                Scoped adjacency snapshot.
            root_blueprints:
                Root blueprint map produced for this snapshot.
            system_index:
                System index for this snapshot.
            spell_lookup:
                Visible spell_id -> spell map.
            root_builder:
                Builder used for per-spell fallback blueprints.
        Returns:
            None.
        """
        for spell_id in snapshot.all_spell_ids:
            spell_instance = spell_lookup[spell_id]
            target_artifact = spell_instance._compiler_artifact
            self._set_spell_system_index_phase5(
                spell_instance,
                target_artifact,
                system_index,
            )

            if spell_instance.is_existing_creation:
                continue

            blueprint = root_blueprints.get(spell_id)
            if blueprint is None:
                blueprint = root_builder.build_blueprint_for_spell_id(
                    root_spell_id=spell_id,
                    snapshot=snapshot,
                )
            self._set_root_blueprint_phase5(
                spell_instance,
                target_artifact,
                blueprint,
            )

    def _filter_snapshot_to_visible_spells(
            self,
            *,
            snapshot: SpellSystemAdjacencySnapshot,
            visible_spell_ids: Collection[str],
    ) -> SpellSystemAdjacencySnapshot:
        """
        Filter a frame-wide adjacency snapshot to spells visible in this Spellbook.

        Purpose:
            Restrict an adjacency snapshot to the subset of spell ids visible to
            the current Spellbook.
        Contract:
            - Preserves all edges whose source and target are visible.
            - Preserves topologies for visible spells only.
            - Recomputes root spell ids after visibility filtering.
            - Does not mutate the source snapshot.
        Args:
            snapshot:
                Full frame adjacency snapshot.
            visible_spell_ids:
                Spell ids that should remain visible in the filtered result.
        Returns:
            SpellSystemAdjacencySnapshot:
                Snapshot filtered to visible spell ids.
        """
        all_spell_ids: Collection[str] = visible_spell_ids
        dependencies: Dict[str, Set[str]] = {}
        reverse_dependencies: Dict[str, Set[str]] = {}
        topologies: Dict[str, "SpellLocalTopology"] = {}

        for spell_id in all_spell_ids:
            deps = snapshot.dependencies.get(spell_id, set())
            filtered_deps = {dep_id for dep_id in deps if dep_id in all_spell_ids}
            dependencies[spell_id] = filtered_deps
            for dep_id in filtered_deps:
                reverse_dependencies.setdefault(dep_id, set()).add(spell_id)

            topology = snapshot.topologies.get(spell_id)
            if topology is not None:
                topologies[spell_id] = topology

        root_spell_ids = {spell_id for spell_id in all_spell_ids if spell_id not in reverse_dependencies}

        return SpellSystemAdjacencySnapshot(
            dependencies=dependencies,
            reverse_dependencies=reverse_dependencies,
            all_spell_ids=all_spell_ids,
            root_spell_ids=root_spell_ids,
            topologies=topologies,
        )

    def _filter_root_blueprints_to_owned(
            self,
            spellbook: ISpellbook,
            root_blueprints: Mapping[str, IRootResolutionBlueprint],
    ) -> Dict[str, IRootResolutionBlueprint]:
        """
        Filter root blueprints to owned spell ids only.

        Purpose:
            Limit component-of rebuilds to spell ids owned by this spellbook.

        Contract:
            - Returns a filtered mapping containing only roots owned by this
              spellbook.
            - Does not mutate the provided mapping.
        Args:
            spellbook:
                Spellbook whose owned roots should be preserved.
            root_blueprints:
                Root blueprint map keyed by root spell id.
        Returns:
            Dict[str, IRootResolutionBlueprint]:
                Filtered root blueprint map containing only owned roots.
        """
        owned_spell_ids = spellbook._spells_by_id.keys()
        return {
            root_id: blueprint
            for root_id, blueprint in root_blueprints.items()
            if root_id in owned_spell_ids
        }

    def run(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            spellbook: ISpellbook,
            spell_system_states: ISpellSystemStates,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 5 entrypoint.

        Build deep DAG blueprints (`RootResolutionBlueprints`) and a frame-level
        `SpellSystemIndex` using existing Phase 1-4 artifacts.

        Responsibilities:
            - Build adjacency from system states.
            - Filter to spellbook-visible spell ids.
            - Build deep DAGs and phase-5 index.
            - Attach phase-5 artifacts to participating spells.
            - Update owning artifact phase-2-5 codegen cache and invalidate
              phase 8-11 cache when outputs change.
            - Rebuild component-of index in change control and register a dirty-root revalidator.

        Args:
            spell:
                Bound target spell for this phase call.
            artifact:
                Phase artifact receiving phase-5 caches.
            spellbook:
                Spellbook used for visibility and ownership boundaries.
            spell_system_states:
                Required SpellSystemStates dependency.
            conduit_id:
                Conduit identifier used by change-control rebuild registration.
            cancel_event:
                Optional cancellation handle.

        Returns:
            None.
        """
        artifact.check_cleaned()

        # --- 1. Build adjacency snapshot from system states ----------------
        adjacency_builder = SpellSystemAdjacencyBuilder()
        required_spell_system_states = self._get_required_spell_system_states(
            spell_system_states
        )
        snapshot = adjacency_builder.build(required_spell_system_states)

        # --- 2. Filter to spellbook-visible spells -------------------------
        visible_spell_ids = spellbook._spell_id_pool.keys()
        filtered_snapshot = self._filter_snapshot_to_visible_spells(
            snapshot=snapshot,
            visible_spell_ids=visible_spell_ids,
        )

        # --- 3. Build deep DAGs for visible roots --------------------------
        root_builder = SpellSystemRootBlueprintBuilder()
        root_blueprints = root_builder.build_root_blueprints(filtered_snapshot)

        # --- 4. Construct system-level index -------------------------------
        system_index = self._build_system_index_for_snapshot(
            snapshot=filtered_snapshot,
            spell_lookup=spellbook._spell_id_pool,
            spell_system_states=required_spell_system_states,
        )

        self._attach_phase5_artifacts_for_snapshot(
            snapshot=filtered_snapshot,
            root_blueprints=root_blueprints,
            system_index=system_index,
            spell_lookup=spellbook._spell_id_pool,
            root_builder=root_builder,
        )

        artifact._spell_system_index_phase5 = system_index
        artifact._entire_dag_blueprint_phase5 = {
            root_id: blueprint
            for root_id, blueprint in root_blueprints.items()
        }
        SharedCompilerExecutions.capture_phase2_5_codegen_ir(spell, artifact)
        SharedCompilerExecutions.reset_phase8_11_codegen_ir(spell, artifact)

        # Rebuild component-of index and register a revalidation hook for dirty roots.
        frame_name = self._get_required_spellbook_frame_name(spellbook)
        change_control_manager = spellbook._aether._get_change_control_manager(frame_name)
        owned_root_blueprints = self._filter_root_blueprints_to_owned(
            spellbook,
            root_blueprints,
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
            Revalidate the supplied dirty roots for this conduit.

            This closure is the phase-5 bridge back into change control.
            Change-control notifies this hook with root ids that became dirty so
            each root spell can rebuild foundational phases in the same conduit.

            Contract:
                - Resolves each root spell from the live spellbook `_spell_id_pool`.
                - Reuses the owning SpellCrafter for each root.
                - Re-runs foundational phases via `run_all_phases(...)`.
                - Returns only successfully revalidated root ids.

            Returns:
                Set[str]:
                    Root ids that successfully revalidated for this conduit.
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

    def run_local(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            spellbook: ISpellbook,
            spell_system_states: ISpellSystemStates,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 5 local entrypoint.

        Build phase-5 artifacts for the target spell and its transitive
        dependency closure only.

        Responsibilities:
            - Build a full snapshot, then narrow to visible and locally-scoped
              ids.
            - Construct local root blueprints and phase-5 index.
            - Attach phase-5 artifacts only to scoped spells.
            - Update the invoking artifact phase-2-5 cache and invalidate
              phase 8-11 when needed.
            - Upsert owned components for this conduit and register a revalidator.

        Args:
            spell:
                Target spell whose local scope is rooted from its current id.
            artifact:
                Phase artifact receiving scoped phase-5 caches.
            spellbook:
                Spellbook providing visibility and ownership boundaries.
            spell_system_states:
                Required SpellSystemStates dependency.
            conduit_id:
                Conduit identifier used by change-control upsert registration.
            cancel_event:
                Optional cancellation handle.

        Returns:
            None.
        """
        artifact.check_cleaned()
        target_spell_id = self._get_required_current_spell_id(spell)

        # --- 1. Build adjacency snapshot and scope to spellbook visibility ---
        adjacency_builder = SpellSystemAdjacencyBuilder()
        required_spell_system_states = self._get_required_spell_system_states(
            spell_system_states
        )
        snapshot = adjacency_builder.build(required_spell_system_states)

        spell_lookup = spellbook._spell_id_pool
        visible_spell_ids = spell_lookup.keys()
        visible_snapshot = self._filter_snapshot_to_visible_spells(
            snapshot=snapshot,
            visible_spell_ids=visible_spell_ids,
        )

        scoped_spell_ids = self._collect_local_scope_spell_ids(
            root_spell_id=target_spell_id,
            snapshot=visible_snapshot,
        )
        scoped_snapshot = self._filter_snapshot_to_visible_spells(
            snapshot=visible_snapshot,
            visible_spell_ids=scoped_spell_ids,
        )

        root_builder = SpellSystemRootBlueprintBuilder()
        local_root_blueprints = root_builder.build_root_blueprints(scoped_snapshot)
        system_index = self._build_system_index_for_snapshot(
            snapshot=scoped_snapshot,
            spell_lookup=spell_lookup,
            spell_system_states=required_spell_system_states,
        )
        self._attach_phase5_artifacts_for_snapshot(
            snapshot=scoped_snapshot,
            root_blueprints=local_root_blueprints,
            system_index=system_index,
            spell_lookup=spell_lookup,
            root_builder=root_builder,
        )

        artifact._spell_system_index_phase5 = system_index
        artifact._entire_dag_blueprint_phase5 = {
            root_id: blueprint
            for root_id, blueprint in local_root_blueprints.items()
        }
        SharedCompilerExecutions.capture_phase2_5_codegen_ir(spell, artifact)
        SharedCompilerExecutions.reset_phase8_11_codegen_ir(spell, artifact)

        frame_name = self._get_required_spellbook_frame_name(spellbook)
        change_control_manager = spellbook._aether._get_change_control_manager(frame_name)
        owned_root_blueprints = self._filter_root_blueprints_to_owned(
            spellbook,
            local_root_blueprints,
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
            Revalidate the supplied dirty roots for this conduit.

            Local phase-5 builds a scoped component view and needs the same dirty
            root callback shape as frame-wide phase-5.

            Contract:
                - Resolves each root spell from the live spellbook `_spell_id_pool`.
                - Reuses the owning SpellCrafter per root.
                - Re-runs foundational phases via `run_all_phases(...)`.
                - Returns only successfully revalidated root ids.

            Returns:
                Set[str]:
                    Root ids that successfully revalidated for this conduit.
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
