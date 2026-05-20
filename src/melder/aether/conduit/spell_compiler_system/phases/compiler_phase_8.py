from typing import Any, Dict, List, Optional, Tuple

from mypy_extensions import mypyc_attr

from melder.aether.conduit.spell_compiler_system.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)
from melder.aether.conduit.spell_compiler_system.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.spell_crafter.blueprints.occurrence_plan import (
    OccurrencePlanBuilder,
)
from melder.utilities.interfaces.irootresolutionblueprint import IRootResolutionBlueprint
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.interfaces.ispellbook import ISpellbook
from melder.utilities.interfaces.ispellsystemstates import ISpellSystemStates
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


@mypyc_attr(native_class=True)
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
    ) -> IRootResolutionBlueprint:
        """
        Return the Phase 5 root blueprint or raise.
        """
        root_blueprint = artifact._root_blueprint_phase5
        if root_blueprint is None:
            raise RuntimeError("SpellCrafter Phase 5 root blueprint is required.")
        return root_blueprint

    def _freeze_phase11_schema_value(self, value: Any) -> Any:
        """
        Normalize arbitrary values into deterministic schema-safe forms.
        """
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if isinstance(value, dict):
            return tuple(
                sorted(
                    (
                        key,
                        self._freeze_phase11_schema_value(item),
                    )
                    for key, item in value.items()
                )
            )
        if isinstance(value, (list, tuple)):
            return tuple(
                self._freeze_phase11_schema_value(item)
                for item in value
            )
        if isinstance(value, set):
            return tuple(
                sorted(
                    (
                        self._freeze_phase11_schema_value(item)
                        for item in value
                    ),
                    key=repr,
                )
            )
        return repr(value)

    def _build_phase8_occurrence_plan_fast_key(
            self,
            *,
            root_blueprint: Optional[IRootResolutionBlueprint],
            spell_lookup: Optional[Dict[str, ISpell]],
            spellbook: ISpellbook,
            spell_system_states: Optional[ISpellSystemStates],
    ) -> Optional[Tuple[Any, ...]]:
        """
        Build a lightweight deterministic key for phase8 signature reuse.
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
            root_blueprint: Optional[IRootResolutionBlueprint],
            spell_lookup: Optional[Dict[str, ISpell]],
            spellbook: ISpellbook,
            spell_system_states: Optional[ISpellSystemStates],
    ) -> Optional[str]:
        """
        Build a deterministic phase8 input signature for occurrence-plan reuse.
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
        """
        artifact._phase8_11_codegen_ir_dirty = True

    def run(
            self,
            spell: ISpell,
            artifact: SpellCompilerArtifact,
            spellbook: ISpellbook,
            spell_system_states: Optional[ISpellSystemStates],
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 8 - Occurrence plan compilation.

        Compiles an OccurrencePlan for spells with attached Phase-5 blueprints.
        Existing-creation spells are treated as a no-op.
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
