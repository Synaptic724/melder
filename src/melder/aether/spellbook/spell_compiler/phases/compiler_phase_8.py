from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
        RootResolutionBlueprint,
    )
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import (
        SpellSystemStates,
    )
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )



from melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)
from melder.aether.spellbook.spell_compiler.blueprints.occurrence_plan import (
    OccurrencePlanBuilder,
)



class CompilerPhase8:
    """
    Compiler phase 8 surface.

    Purpose:
        Expose the current occurrence-plan build behavior through a compiler-
        owned phase class.

    Contract:
        - Slot-only phase surface with no explicit `__init__`.
        - Directly ports the canonical `SpellCrafter` phase-8 behavior.
        - Does not own spell, artifact, spellbook, or runtime collaborator
          lifecycle.
    """

    __slots__ = ()

    def _get_required_root_blueprint_phase5(
            self,
            artifact: SpellCompilerArtifact,
    ) -> RootResolutionBlueprint:
        """
        Return the Phase 5 root blueprint or raise.

        Purpose:
            Resolve and validate phase-5 blueprint dependency before compiling
            occurrence artifacts.
        Contract:
            - Raises when the Phase-5 root blueprint is missing.
            - Returns a non-None blueprint map for downstream occurrence-plan
              construction.
        Args:
            artifact:
                Compiler artifact carrying phase-5 state.
        Returns:
            RootResolutionBlueprint:
                The current root blueprint required for phase-8.
        """
        root_blueprint = artifact._root_blueprint_phase5
        if root_blueprint is None:
            raise RuntimeError("SpellCrafter Phase 5 root blueprint is required.")
        return root_blueprint

    def _freeze_phase11_schema_value(self, value: Any) -> Any:
        """
        Normalize arbitrary values into deterministic schema-safe forms.

        Purpose:
            Convert mutable/composite runtime values to deterministic, hashable
            representations for signature construction.
        Contract:
            - Preserves primitive scalar values.
            - Recursively normalizes container structures.
            - Falls back to a canonical string representation for unknown types.
        Args:
            value:
                Any object participating in schema/signature capture.
        Returns:
            Any:
                Deterministic, immutable, hashable representation.
        """
        return SharedCompilerExecutions.freeze_phase11_schema_value(value)

    def _build_phase8_occurrence_plan_fast_key(
            self,
            *,
            root_blueprint: Optional[RootResolutionBlueprint],
            spell_lookup: Optional[Dict[str, Spell]],
            spellbook: Spellbook,
            spell_system_states: Optional[SpellSystemStates],
    ) -> Optional[Tuple[Any, ...]]:
        """
        Build a lightweight deterministic key for phase8 signature reuse.

        Purpose:
            Avoid recomputing deep phase8 signature hashing when inputs are
            unchanged between warm runs.
        Contract:
            - Returns None when required inputs are unavailable.
            - Returns None when any spell has a mutation override, forcing the
              deep signature path.
            - Mirrors no-mutation phase8 signature surfaces used for plan reuse.
        Args:
            root_blueprint:
                Phase-5 root blueprint for this spell.
            spell_lookup:
                Spell lookup map keyed by spell id.
            spellbook:
                Active spellbook used to resolve contracted routing state.
            spell_system_states:
                Optional spell system states for local topology capture.
        Returns:
            Optional[Tuple[Any, ...]]:
                Deterministic fast-key tuple or None when deep-signature fallback
                is required.
        """
        if root_blueprint is None or spell_lookup is None:
            return None

        try:
            ordered_node_ids = tuple(root_blueprint.ordered_node_ids)
            path_registry_identity = id(root_blueprint.path_registry)
            blueprint_socket_rows = tuple(
                (
                    socket_ref.node_id,
                    socket_ref.param_name,
                    socket_ref.param_path_id,
                    socket_ref.socket_kind.value,
                )
                for socket_ref in (root_blueprint.socket_refs or ())
            )
        except Exception:
            return None

        try:
            spell_rows_list: List[Tuple[Any, ...]] = []
            for spell_id, candidate_spell in sorted(spell_lookup.items()):
                if candidate_spell.mutation_override:
                    return None
                spell_rows_list.append(
                    (
                        spell_id,
                        candidate_spell.spell_index.current,
                        candidate_spell.existence.name,
                        bool(candidate_spell.is_existing_creation),
                    )
                )
            spell_rows = tuple(spell_rows_list)
        except Exception:
            return None

        topology_rows: Tuple[Any, ...] = ()
        local_topologies = None
        if spell_system_states is not None:
            local_topologies = getattr(spell_system_states, "_local_topologies", None)
        if local_topologies is not None:
            try:
                topology_rows_list: List[Tuple[Any, ...]] = []
                for spell_id in sorted(local_topologies.keys()):
                    topology = local_topologies.get(spell_id)
                    if topology is None:
                        continue
                    socket_rows = tuple(
                        (
                            socket.param_name,
                            tuple(sorted(socket.target_spell_ids)),
                        )
                        for socket in topology.sockets
                    )
                    topology_rows_list.append((spell_id, socket_rows))
                topology_rows = tuple(topology_rows_list)
            except Exception:
                return None

        try:
            contracted_lookup = spellbook._lookup_contracted_spells
            contracted_maps = spellbook._contracted_spells
            frame_configuration = spellbook._aetheric_frame_configuration
            if frame_configuration is None:
                return None
            system_state = frame_configuration.system_state
        except Exception:
            return None

        try:
            contracted_rows_list: List[Tuple[Any, ...]] = []
            for conduit_id in sorted(contracted_lookup.keys()):
                lookup_map = contracted_lookup.get(conduit_id)
                if lookup_map is None:
                    continue
                contracted_map = contracted_maps.get(conduit_id)
                for contract_key in sorted(lookup_map.keys()):
                    spell_index = lookup_map.get(contract_key)
                    if spell_index is None:
                        continue
                    provider_spell_id = None
                    if contracted_map is not None:
                        provider_spell = contracted_map.get(spell_index)
                        if provider_spell is not None:
                            provider_spell_id = provider_spell.spell_index.current
                    contracted_rows_list.append(
                        (
                            conduit_id,
                            contract_key[0],
                            contract_key[1],
                            provider_spell_id,
                        )
                    )
            contracted_rows = tuple(contracted_rows_list)
        except Exception:
            return None

        return (
            root_blueprint.root_spell_id,
            ordered_node_ids,
            path_registry_identity,
            blueprint_socket_rows,
            spell_rows,
            topology_rows,
            system_state,
            contracted_rows,
        )

    def _build_phase8_occurrence_plan_input_signature(
            self,
            *,
            root_blueprint: Optional[RootResolutionBlueprint],
            spell_lookup: Optional[Dict[str, Spell]],
            spellbook: Spellbook,
            spell_system_states: Optional[SpellSystemStates],
    ) -> Optional[str]:
        """
        Build a deterministic phase8 input signature for occurrence-plan reuse.

        Purpose:
            Detect semantic drift in phase8 inputs so warm runs can safely skip
            redundant occurrence-plan rebuilds when inputs are unchanged.
        Contract:
            - Returns None when required inputs are unavailable, forcing rebuild.
            - Includes blueprint shape, spell mutation/existence signals, local
              topology socket structure, and contracted-provider routing state.
        Args:
            root_blueprint:
                Phase-5 root blueprint for this spell.
            spell_lookup:
                Spell lookup map keyed by spell id.
            spellbook:
                Active spellbook providing contracted spell wiring context.
            spell_system_states:
                Optional system state for local topology snapshot.
        Returns:
            Optional[str]:
                Deterministic signature string, or None when rebuild is required.
        """
        if root_blueprint is None or spell_lookup is None:
            return None

        try:
            ordered_node_ids = tuple(root_blueprint.ordered_node_ids)
            path_registry_identity = id(root_blueprint.path_registry)
            blueprint_socket_rows = tuple(
                (
                    socket_ref.node_id,
                    socket_ref.param_name,
                    socket_ref.param_path_id,
                    socket_ref.socket_kind.value,
                )
                for socket_ref in (root_blueprint.socket_refs or ())
            )
        except Exception:
            return None

        try:
            spell_rows = tuple(
                (
                    spell_id,
                    candidate_spell.spell_index.current,
                    candidate_spell.existence.name,
                    bool(candidate_spell.is_existing_creation),
                    self._freeze_phase11_schema_value(candidate_spell.mutation_override),
                )
                for spell_id, candidate_spell in sorted(spell_lookup.items())
            )
        except Exception:
            return None

        topology_rows: Tuple[Any, ...] = ()
        local_topologies = None
        if spell_system_states is not None:
            local_topologies = getattr(spell_system_states, "_local_topologies", None)
        if local_topologies is not None:
            try:
                topology_rows_list: List[Tuple[Any, ...]] = []
                for spell_id in sorted(local_topologies.keys()):
                    topology = local_topologies.get(spell_id)
                    if topology is None:
                        continue
                    socket_rows = tuple(
                        (
                            socket.param_name,
                            tuple(sorted(socket.target_spell_ids)),
                        )
                        for socket in topology.sockets
                    )
                    topology_rows_list.append((spell_id, socket_rows))
                topology_rows = tuple(topology_rows_list)
            except Exception:
                return None

        try:
            contracted_lookup = spellbook._lookup_contracted_spells
            contracted_maps = spellbook._contracted_spells
            frame_configuration = spellbook._aetheric_frame_configuration
            if frame_configuration is None:
                return None
            system_state = frame_configuration.system_state
        except Exception:
            return None

        try:
            contracted_rows_list: List[Tuple[Any, ...]] = []
            for conduit_id in sorted(contracted_lookup.keys()):
                lookup_map = contracted_lookup.get(conduit_id)
                if lookup_map is None:
                    continue
                contracted_map = contracted_maps.get(conduit_id)
                for contract_key in sorted(lookup_map.keys()):
                    spell_index = lookup_map.get(contract_key)
                    if spell_index is None:
                        continue
                    provider_spell_id = None
                    if contracted_map is not None:
                        provider_spell = contracted_map.get(spell_index)
                        if provider_spell is not None:
                            provider_spell_id = provider_spell.spell_index.current
                    contracted_rows_list.append(
                        (
                            conduit_id,
                            contract_key[0],
                            contract_key[1],
                            provider_spell_id,
                        )
                    )
            contracted_rows = tuple(contracted_rows_list)
        except Exception:
            return None

        return SharedCompilerExecutions.hash_codegen_signature(
            root_blueprint.root_spell_id,
            ordered_node_ids,
            path_registry_identity,
            blueprint_socket_rows,
            spell_rows,
            topology_rows,
            system_state,
            contracted_rows,
        )

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
            spell: Spell,
            artifact: SpellCompilerArtifact,
            spellbook: Spellbook,
            spell_system_states: Optional[SpellSystemStates],
    ) -> None:
        """
        Phase 8 - Occurrence plan compilation.

        Compiles an OccurrencePlan for spells with attached Phase-5 blueprints.
        Existing-creation spells are treated as a no-op.

        Contract:
            - Requires Phase 5 root blueprint to be present.
            - Builds plan only when the blueprint is available and spell is not
              an existing-creation.
            - Replaces any existing occurrence plan for this artifact.
            - Uses spellbook-managed spell_id_pool as the lookup map.
        Args:
            spell:
                Root spell under compilation.
            artifact:
                Conduit artifact owning phase-8 cached outputs.
            spellbook:
                Active spellbook supplying lookup and runtime wiring.
            spell_system_states:
                Optional system states passed into the builder.
        Returns:
            None.
        """
        artifact.check_cleaned()
        if spell.is_existing_creation:
            return
        root_blueprint = self._get_required_root_blueprint_phase5(artifact)
        spell_lookup = spellbook._spell_id_pool
        phase8_occurrence_plan_fast_key = self._build_phase8_occurrence_plan_fast_key(
            root_blueprint=root_blueprint,
            spell_lookup=spell_lookup,
            spellbook=spellbook,
            spell_system_states=spell_system_states,
        )
        # Stage 1: derive and compare fast-key/signature inputs for warm reuse.
        can_reuse_phase8_signature_fast_key = (
                phase8_occurrence_plan_fast_key is not None
                and artifact._phase8_occurrence_plan_fast_key == phase8_occurrence_plan_fast_key
                and artifact._phase8_occurrence_plan_input_signature is not None
        )
        if can_reuse_phase8_signature_fast_key:
            occurrence_plan_input_signature = artifact._phase8_occurrence_plan_input_signature
        else:
            occurrence_plan_input_signature = self._build_phase8_occurrence_plan_input_signature(
                root_blueprint=root_blueprint,
                spell_lookup=spell_lookup,
                spellbook=spellbook,
                spell_system_states=spell_system_states,
            )
        # Stage 2: cache fast-key for next run and gate rebuild on signature match.
        if phase8_occurrence_plan_fast_key is not None:
            artifact._phase8_occurrence_plan_fast_key = phase8_occurrence_plan_fast_key
        else:
            artifact._phase8_occurrence_plan_fast_key = None
        if (
                occurrence_plan_input_signature is not None
                and occurrence_plan_input_signature == artifact._phase8_occurrence_plan_input_signature
                and artifact._occurrence_plan_phase8 is not None
        ):
            return

        # Stage 3: construct a new occurrence plan and hot-swap outputs.
        builder = OccurrencePlanBuilder(
            root_spell=spell,
            blueprint=root_blueprint,
            spell_lookup=spell_lookup,
            system_states=spell_system_states,
        )
        try:
            plan = builder.build()
        finally:
            builder.cleanup()

        # Hot-swap the plan without cleaning the previous object in-place.
        # Concurrent phase runners may still hold references to the prior plan.
        artifact._occurrence_plan_phase8 = plan
        artifact._phase8_occurrence_plan_input_signature = occurrence_plan_input_signature
        self._mark_phase8_11_codegen_ir_dirty(artifact)

