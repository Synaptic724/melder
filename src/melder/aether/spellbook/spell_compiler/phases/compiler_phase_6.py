from typing import TYPE_CHECKING, Any, Collection, Dict, List, Optional, Set, Tuple

if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
        RootResolutionBlueprint,
    )
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spellbook import Spellbook

from mypy_extensions import mypyc_attr

from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import (
    SpellValidity,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.spell_compiler.system.spell_system_index import (
    SpellSystemIndex,
)
from melder.aether.spellbook.spell_compiler.system.spell_system_validation_state import (
    SpellSystemValidationState,
)
from melder.aether.spellbook.spell_compiler.system.spell_system_validation_system import (
    SpellSystemValidationSystem,
)
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_compiler.system.validation.broken_spell_in_dag_strategy import (
    BrokenSpellInDagStrategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.contract_graph_cycle_strategy import (
    ContractGraphCycleStrategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.contracted_version_drift_strategy import (
    ContractedVersionDriftStrategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.cycle_detection_strategy import (
    CycleDetectionStrategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.dependency_type_sanity_strategy import (
    DependencyTypeSanityStrategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.graph_consistency_strategy import (
    GraphConsistencyStrategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.identity_mixing_strategy import (
    IdentityMixingStrategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.index_coverage_strategy import (
    IndexCoverageStrategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.index_dependency_sanity_strategy import (
    IndexDependencySanityStrategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.lineage_alignment_strategy import (
    LineageAlignmentStrategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.lineage_version_conflict_strategy import (
    LineageVersionConflictStrategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.missing_phase4_strategy import (
    MissingPhase4Strategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.ownership_consistency_strategy import (
    OwnershipConsistencyStrategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.root_coverage_strategy import (
    RootCoverageStrategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.root_lineage_conflict_strategy import (
    RootLineageConflictStrategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.root_reachability_strategy import (
    RootReachabilityStrategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.root_scale_limit_strategy import (
    RootScaleLimitStrategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.root_viability_strategy import (
    RootViabilityStrategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.scope_ordering_strategy import (
    ScopeOrderingStrategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.socket_ref_sanity_strategy import (
    SocketRefSanityStrategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.topology_dependency_mismatch_strategy import (
    TopologyDependencyMismatchStrategy,
)
from melder.aether.spellbook.spell_compiler.system.validation.visibility_gap_strategy import (
    VisibilityGapStrategy,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


@mypyc_attr(native_class=True)
class CompilerPhase6:
    """
    Compiler phase 6 surface.

    Purpose:
        Expose the current system-validation behavior through a compiler-owned
        phase class.

    Contract:
        - Slot-only phase surface with no explicit `__init__`.
        - Directly ports the canonical `SpellCrafter` phase-6 behavior.
        - Does not own spell, artifact, spellbook, or runtime collaborator
          lifecycle.
    """

    __slots__ = ()

    def _get_required_entire_dag_blueprint_phase5(
            self,
            artifact: SpellCompilerArtifact,
    ) -> Dict[str, RootResolutionBlueprint]:
        """
            Return the Phase 5 root-blueprint map or raise.
            
            Returns:
                Dict[str, RootResolutionBlueprint]: Root blueprint map keyed by
                root spell id.
        """
        root_blueprints = artifact._entire_dag_blueprint_phase5
        if root_blueprints is None:
            raise RuntimeError(
                "SpellCrafter Phase 5 root blueprint map is required."
            )
        return root_blueprints

    def _get_required_spell_system_index_phase5(
            self,
            artifact: SpellCompilerArtifact,
    ) -> SpellSystemIndex:
        """
            Return the Phase 5 system index or raise.
            
            Returns:
                SpellSystemIndex: Attached Phase 5 system index.
        """
        system_index = artifact._spell_system_index_phase5
        if system_index is None:
            raise RuntimeError("SpellCrafter Phase 5 system index is required.")
        return system_index

    def _collect_local_visibility_gap_diagnostics(
            self,
            *,
            spell: Spell,
            spell_system_states: SpellSystemStates,
            scoped_spell_ids: Collection[str],
            spell_lookup: Dict[str, Spell],
            root_ids: Collection[str],
    ) -> List[SystemDiagnostic]:
        """
        Collect visibility-gap diagnostics for local Phase 6 validation.

        Purpose:
            Detect unresolved dependency spell ids in local topologies before
            system validation and later occurrence-plan compilation steps.
        Contract:
            - Emits one ERROR diagnostic per unique missing dependency edge.
            - Uses topology target_spell_ids as the source of truth.
            - Keeps spell visibility evaluation read-only with no state mutation.
        Args:
            spell:
                The top-level spell used for deterministic local root-id fallback.
            spell_system_states:
                Active system state view for topology lookups.
            scoped_spell_ids:
                Spell ids participating in the local validation scope.
            spell_lookup:
                Visible spell_id -> spell map for the current Spellbook.
            root_ids:
                Root ids for the local validation scope.
        Returns:
            List[SystemDiagnostic]:
                Visibility-gap diagnostics, empty when the scope is fully visible.
        """
        spell.spell_index.current
        ordered_root_ids = sorted(root_ids)
        root_id = ordered_root_ids[0] if ordered_root_ids else spell.spell_index.current
        diagnostics: List[SystemDiagnostic] = []
        seen: Set[Tuple[str, str, str]] = set()
        for spell_id in scoped_spell_ids:
            topology = spell_system_states.get_local_topology_by_id(spell_id)
            if topology is None:
                continue
            for socket in topology.iter_sockets():
                for dependency_id in socket.target_spell_ids:
                    if dependency_id in spell_lookup:
                        continue
                    signature = (spell_id, socket.param_name, dependency_id)
                    if signature in seen:
                        continue
                    seen.add(signature)
                    diagnostics.append(
                        SystemDiagnostic(
                            code="visibility_gap_dependency_filtered",
                            message=(
                                f"Spell '{spell_id}' parameter '{socket.param_name}' "
                                f"depends on '{dependency_id}', but that dependency is "
                                "not visible to this Spellbook."
                            ),
                            severity=SystemDiagnosticSeverity.ERROR,
                            spell_id=spell_id,
                            root_id=root_id,
                            source="LocalVisibilityGapGuard",
                            details={
                                "spell_id": spell_id,
                                "param_name": socket.param_name,
                                "missing_dependency_id": dependency_id,
                            },
                        )
                    )
        return diagnostics

    def _collect_local_blueprint_visibility_gap_diagnostics(
            self,
            *,
            blueprints: Dict[str, RootResolutionBlueprint],
            spell_lookup: Dict[str, Spell],
    ) -> List[SystemDiagnostic]:
        """
        Collect visibility-gap diagnostics from local Phase 5 root blueprints.

        Purpose:
            Catch hidden dependency nodes that are present in blueprint DAGs but
            not visible in this Spellbook's spell pool.
        Contract:
            - Emits one ERROR diagnostic per unique (root_id, missing_spell_id).
            - Keeps blueprint and spell pools read-only while collecting gaps.
        Args:
            blueprints:
                Local root blueprints produced by local Phase 5.
            spell_lookup:
                Visible spell_id -> spell map for the current Spellbook.
        Returns:
            List[SystemDiagnostic]:
                Visibility-gap diagnostics derived from blueprint DAG contents.
        """
        diagnostics: List[SystemDiagnostic] = []
        seen: Set[Tuple[str, str]] = set()
        for root_id, blueprint in blueprints.items():
            dag = blueprint.dag
            for dependency_id in dag.nodes.keys():
                if dependency_id in spell_lookup:
                    continue
                signature = (root_id, dependency_id)
                if signature in seen:
                    continue
                seen.add(signature)
                diagnostics.append(
                    SystemDiagnostic(
                        code="visibility_gap_dependency_filtered",
                        message=(
                            f"Root '{root_id}' references dependency "
                            f"'{dependency_id}', but that dependency is not "
                            "visible to this Spellbook."
                        ),
                        severity=SystemDiagnosticSeverity.ERROR,
                        spell_id=dependency_id,
                        root_id=root_id,
                        source="LocalVisibilityGapGuard",
                        details={
                            "root_id": root_id,
                            "missing_dependency_id": dependency_id,
                        },
                    )
                )
        return diagnostics

    def _build_strategies(self) -> List[Any]:
        """
            Build the fixed phase-6 validation strategy pipeline.
            
            Purpose:
                Centralize the strategy objects used by both frame-wide and local
                system-validation execution so both paths keep the same policy.
            Contract:
                - Order of strategies remains canonical for deterministic diagnostics.
                - Returns a new list instance on each call to avoid accidental sharing.
            Returns:
                List[Any]:
                    Ordered validation strategy instances for phase-6 execution.
        """
        return [
            CycleDetectionStrategy(),
            BrokenSpellInDagStrategy(),
            GraphConsistencyStrategy(),
            MissingPhase4Strategy(),
            RootReachabilityStrategy(),
            RootCoverageStrategy(),
            IndexDependencySanityStrategy(),
            VisibilityGapStrategy(),
            TopologyDependencyMismatchStrategy(),
            IdentityMixingStrategy(),
            ContractedVersionDriftStrategy(),
            LineageAlignmentStrategy(),
            IndexCoverageStrategy(),
            LineageVersionConflictStrategy(),
            RootLineageConflictStrategy(),
            OwnershipConsistencyStrategy(),
            DependencyTypeSanityStrategy(),
            ScopeOrderingStrategy(),
            ContractGraphCycleStrategy(),
            RootScaleLimitStrategy(),
            RootViabilityStrategy(),
            SocketRefSanityStrategy(),
        ]

    def run_frame_wide(
            self,
            artifact: SpellCompilerArtifact,
            spellbook: Spellbook,
            spell_system_states: SpellSystemStates,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 6 - System-level validation.

        Runs system-level validation strategies over Phase-5 artifacts and
        Phase-4 outcomes. Records per-conduit and per-spell validation state
        on all compiler artifacts.

        Args:
            artifact:
                Conduit-level compiler artifact containing Phase-5 results.
            spellbook:
                Spellbook containing all visible spells for this run.
            spell_system_states:
                System-state graph and topology source for validation execution.
            conduit_id:
                Conduit identifier that scopes visibility and validity recording.
            cancel_event:
                Optional cancellation signal used to terminate long-running work.
        Returns:
            None.
        """
        artifact.check_cleaned()

        # Stage 1: gather phase-4 outcomes and broken-spell tracking.
        phase4_results: Dict[str, Any] = {}
        broken_spell_ids: Set[str] = set()

        spell_lookup: Dict[str, Spell] = spellbook._spell_id_pool
        for spell_id, spell_instance in spell_lookup.items():
            phase4_results[spell_id] = spell_instance._compiler_artifact._validation_result_phase4
            if spell_instance._compiler_artifact._is_broken:
                broken_spell_ids.add(spell_id)

        # Stage 2: execute the canonical phase-6 validation strategy set.
        validator = SpellSystemValidationSystem(strategies=self._build_strategies())
        validation_state: SpellSystemValidationState = validator.validate(
            index=self._get_required_spell_system_index_phase5(artifact),
            blueprints=self._get_required_entire_dag_blueprint_phase5(artifact),
            phase4_results=phase4_results,
            broken_spell_ids=broken_spell_ids,
            spell_system_states=spell_system_states,
            conduit_id=conduit_id,
            spell_lookup=spell_lookup,
            cancel_event=cancel_event,
        )

        # Stage 3: cache validation state across the full frame/crafting scope.
        artifact._validation_result_phase6 = validation_state
        artifact._validated_phase6 = True
        for spell_instance in spell_lookup.values():
            target_artifact = spell_instance._compiler_artifact
            target_artifact._validation_result_phase6 = validation_state
            target_artifact._validated_phase6 = True

    def run_local(
            self,
            spell: Spell,
            artifact: SpellCompilerArtifact,
            spellbook: Spellbook,
            spell_system_states: SpellSystemStates,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 6 local entrypoint.

        Purpose:
            Validate only the locally scoped Phase 5 graph produced by local
            root-blueprint flow.
        Contract:
            - Uses the same validation strategy set as frame-wide Phase 6.
            - Returns early after recording visibility-gap diagnostics.
            - Publishes phase-6 state only on scoped spell artifacts.
        Args:
            spell:
                The local spell entry context.
            artifact:
                Local compiler artifact containing the current scope graph.
            spellbook:
                Spellbook containing all visible spells.
            spell_system_states:
                System state view used for topology and validity writes.
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the pipeline.
        Returns:
            None.
        """
        artifact.check_cleaned()
        spell_lookup_pool = spellbook._spell_id_pool
        index = artifact._spell_system_index_phase5
        blueprints = artifact._entire_dag_blueprint_phase5
        if index is None or blueprints is None:
            raise RuntimeError("Phase 6 local requires Phase 5 local artifacts.")

        phase4_results: Dict[str, Any] = {}
        broken_spell_ids: Set[str] = set()
        scoped_spell_lookup: Dict[str, Spell] = {}

        for spell_id in index.nodes.keys():
            spell_instance = spell_lookup_pool[spell_id]
            scoped_spell_lookup[spell_id] = spell_instance
            target_artifact = spell_instance._compiler_artifact
            phase4_results[spell_id] = target_artifact._validation_result_phase4
            if target_artifact._is_broken:
                broken_spell_ids.add(spell_id)

        # Stage 1: collect local visibility-gap diagnostics before running
        # heavyweight validation.
        visibility_gap_diagnostics = self._collect_local_visibility_gap_diagnostics(
            spell=spell,
            spell_system_states=spell_system_states,
            scoped_spell_ids=index.nodes.keys(),
            spell_lookup=spell_lookup_pool,
            root_ids=blueprints.keys(),
        )
        visibility_gap_diagnostics.extend(
            self._collect_local_blueprint_visibility_gap_diagnostics(
                blueprints=blueprints,
                spell_lookup=spell_lookup_pool,
            )
        )
        # Stage 2: fail fast when visibility gaps are detected.
        if visibility_gap_diagnostics:
            spell_system_states.bulk_set_conduit_spell_validity(
                conduit_id,
                {spell_id: SpellValidity.invalid for spell_id in index.nodes.keys()},
                change_reason=SpellStateChangeReason.validation_failed,
            )
            spell_system_states.bulk_set_conduit_root_validity(
                conduit_id,
                {root_id: SpellValidity.invalid for root_id in blueprints.keys()},
                change_reason=SpellStateChangeReason.validation_failed,
            )
            spell_system_states.record_conduit_diagnostics(
                conduit_id,
                visibility_gap_diagnostics,
            )
            validation_state = SpellSystemValidationState(
                is_valid=False,
                errors=visibility_gap_diagnostics,
                warnings=[],
                nodes=index.nodes,
            )
            artifact._validation_result_phase6 = validation_state
            artifact._validated_phase6 = True
            for spell_instance in scoped_spell_lookup.values():
                target_artifact = spell_instance._compiler_artifact
                target_artifact._validation_result_phase6 = validation_state
                target_artifact._validated_phase6 = True
            return

        # Stage 3: run scoped system validation and propagate state.
        validator = SpellSystemValidationSystem(strategies=self._build_strategies())
        validation_state = validator.validate(
            index=index,
            blueprints=blueprints,
            phase4_results=phase4_results,
            broken_spell_ids=broken_spell_ids,
            spell_system_states=spell_system_states,
            conduit_id=conduit_id,
            spell_lookup=scoped_spell_lookup,
            cancel_event=cancel_event,
        )

        artifact._validation_result_phase6 = validation_state
        artifact._validated_phase6 = True
        for spell_instance in scoped_spell_lookup.values():
            target_artifact = spell_instance._compiler_artifact
            target_artifact._validation_result_phase6 = validation_state
            target_artifact._validated_phase6 = True

