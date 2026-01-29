import threading
import time
import inspect
import typing
import types
from typing import Any, Optional, List, Dict, Tuple, Set, Union, get_args, get_origin
# Melder Imports
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import DirectedAcyclicWorkGraph
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.symbolic_graph.spell_symbolic_dependency import (
    SpellSymbolicDependency,
)
from melder.spellbook.spell_crafter.symbolic_graph.spell_symbolic_graph import (
    SpellSymbolicGraph,
)
from melder.spellbook.spell_crafter.spellbook_scanner import SpellbookScanner
from melder.spellbook.spell_crafter.spell_examiner.profiles.resolution_profile import (
    SpellResolutionFrame,
)
from melder.spellbook.spell_crafter.system.spell_system_adjacency_builder import SpellSystemAdjacencyBuilder
from melder.spellbook.spell_crafter.system.spell_system_adjacency_snapshot import SpellSystemAdjacencySnapshot
from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.spell_crafter.system.spell_system_root_blueprint_builder import SpellSystemRootBlueprintBuilder
from melder.spellbook.spell_types.spell_types import SpellType
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_requirements_finder import (
    SpellRequirementsFinder,
)
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_requirements import (
    SpellRequirements,
)
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.contracts.mutation_contract import MutationContract
from melder.utilities.interfaces.interfaces import ISpell, ISpellSystemStates, ISpellbook
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from melder.spellbook.spell_crafter.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.blueprints.patch_maps import (
    MutationPatchMap,
    OverridePatchMap,
    PatchMapBuilder,
)
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import RootResolutionBlueprint
from melder.spellbook.spell_crafter.blueprints.injection_plan import (
    InjectionPlan,
    InjectionPlanBuilder,
)
from melder.spellbook.spell_crafter.blueprints.occurrence_plan import (
    OccurrencePlan,
    OccurrencePlanBuilder,
)
from melder.spellbook.spell_crafter.blueprints.execution_plan import (
    ExecutionPlan,
    ExecutionPlanBuilder,
)
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.spell_system_validation_state import SpellSystemValidationState
from melder.spellbook.spell_crafter.system.spell_system_validation_system import SpellSystemValidationSystem
from melder.spellbook.spell_crafter.system.validation.cycle_detection_strategy import CycleDetectionStrategy
from melder.spellbook.spell_crafter.system.validation.broken_spell_in_dag_strategy import BrokenSpellInDagStrategy
from melder.spellbook.spell_crafter.system.validation.graph_consistency_strategy import GraphConsistencyStrategy
from melder.spellbook.spell_crafter.system.validation.dependency_type_sanity_strategy import (
    DependencyTypeSanityStrategy,
)
from melder.spellbook.spell_crafter.system.validation.index_coverage_strategy import (
    IndexCoverageStrategy,
)
from melder.spellbook.spell_crafter.system.validation.index_dependency_sanity_strategy import (
    IndexDependencySanityStrategy,
)
from melder.spellbook.spell_crafter.system.validation.lineage_alignment_strategy import (
    LineageAlignmentStrategy,
)
from melder.spellbook.spell_crafter.system.validation.lineage_version_conflict_strategy import (
    LineageVersionConflictStrategy,
)
from melder.spellbook.spell_crafter.system.validation.missing_phase4_strategy import MissingPhase4Strategy
from melder.spellbook.spell_crafter.system.validation.ownership_consistency_strategy import (
    OwnershipConsistencyStrategy,
)
from melder.spellbook.spell_crafter.system.validation.root_coverage_strategy import (
    RootCoverageStrategy,
)
from melder.spellbook.spell_crafter.system.validation.root_lineage_conflict_strategy import (
    RootLineageConflictStrategy,
)
from melder.spellbook.spell_crafter.system.validation.root_reachability_strategy import (
    RootReachabilityStrategy,
)
from melder.spellbook.spell_crafter.system.validation.root_scale_limit_strategy import (
    RootScaleLimitStrategy,
)
from melder.spellbook.spell_crafter.system.validation.visibility_gap_strategy import (
    VisibilityGapStrategy,
)
from melder.spellbook.spell_crafter.system.validation.topology_dependency_mismatch_strategy import (
    TopologyDependencyMismatchStrategy,
)
from melder.spellbook.spell_crafter.system.validation.identity_mixing_strategy import (
    IdentityMixingStrategy,
)
from melder.spellbook.spell_crafter.system.validation.contracted_version_drift_strategy import (
    ContractedVersionDriftStrategy,
)
from melder.spellbook.spell_crafter.system.validation.scope_ordering_strategy import (
    ScopeOrderingStrategy,
)
from melder.spellbook.spell_crafter.system.validation.contract_graph_cycle_strategy import (
    ContractGraphCycleStrategy,
)
from melder.spellbook.spell_crafter.system.validation.root_viability_strategy import RootViabilityStrategy
from melder.spellbook.spell_crafter.system.validation.socket_ref_sanity_strategy import SocketRefSanityStrategy
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SpellCrafter(Cleanable):
    """
    Per-spell **compiler / resolution helper**.

    This object owns all *ephemeral* artifacts across the four conceptual
    phases for a single :class:`Spell`:

        1. Requirements (signature ? SpellRequirements)
        2. Symbolic graph (requirements ? symbolic constructor sockets)
        3. Local frame / DAG (symbolic graph + Spellbook ? executable frame)
        4. Validation (frame + policies ? validated / broken flags)

    It also retains selected **frame-level artifacts** produced in later phases
    when they are available for this spell (e.g., Phase 5 blueprints and
    Phase 8-11 plans for constructed spells). Existing-creation spells may
    bypass Phase 8-11 artifacts because they already have instances.

    The :class:`Spell` instance only persists:

        * Its immutable structural metadata (spell_index, spellframe, etc.).
        * The final dependency graph / resolution DAG (once implemented).
        * The final list of concrete dependency spell_ids (version IDs).

    Everything else (requirements, symbolic graph, intermediate frames) is owned
    by this crafter and can be discarded after a resolution cycle by calling
    :meth:`cleanup`.

    Identity
    --------
    All phase artifacts produced by this crafter are keyed by the Spell’s
    **versioned identity**:

        ``spell.spell_index.current``

    That value is written into:

        * :class:`SpellRequirements.spell_id`
        * :class:`SpellSymbolicGraph.spell_id`
        * :class:`SpellSymbolicDependency.spell_id`
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_spell",
        "_requirements",
        "_symbolic_graph",
        "_resolution_frame",
        "_validation_result_phase4",
        "_validated_phase4",
        "_validation_result_phase6",
        "_validated_phase6",
        "_validated",
        "_root_blueprint_phase5",
        "_occurrence_plan_phase8",
        "_injection_plan_phase9",
        "_override_patch_map_phase10",
        "_mutation_patch_map_phase10",
        "_execution_plan_phase11",
        "_spell_system_index_phase5",
        "_is_broken",
        "_entire_dag_blueprint_phase5",
        "_spell_validator",
        "_spell_system_states",
        "_spellbook_scanner",
    ]

    def __init__(self, spell: ISpell) -> None:
        """
        Create a new SpellCrafter for the given :class:`Spell`.

        Args:
            spell:
                The owning Spell. The crafter treats it as read-only, except when
                later phases push the final DAG back into the Spell via internal
                methods like ``_add_build_details``.
        """
        Cleanable.__init__(self)

        if spell is None:
            raise ValueError("spell must not be None.")

        self._lock: threading.RLock = threading.RLock()
        self._spell: ISpell = spell
        self._spell_validator: 'SpellValidationSystem' = self._spell._spellbook._spell_validator
        self._spell_system_states: Optional[ISpellSystemStates] = self._spell._spell_system_states
        self._spellbook_scanner: Optional[SpellbookScanner] = None
        self._requirements: Optional[SpellRequirements] = None
        self._symbolic_graph: Optional[SpellSymbolicGraph] = None
        # Phase 3 artifact – currently a SpellResolutionFrame summarising the
        # concrete dependency DAG that is pushed into the owning Spell.
        self._resolution_frame: Optional[SpellResolutionFrame] = None
        self._validation_result_phase4: Any = None
        self._validated_phase4: bool = False
        self._validation_result_phase6: Any = None
        self._validated_phase6: bool = False
        self._root_blueprint_phase5: Optional[RootResolutionBlueprint] = None
        self._occurrence_plan_phase8: Optional[OccurrencePlan] = None
        self._injection_plan_phase9: Optional[InjectionPlan] = None
        self._override_patch_map_phase10: Optional[OverridePatchMap] = None
        self._mutation_patch_map_phase10: Optional[MutationPatchMap] = None
        self._execution_plan_phase11: Optional[ExecutionPlan] = None
        self._spell_system_index_phase5: Optional[SpellSystemIndex] = None
        self._entire_dag_blueprint_phase5 : Optional[Dict[str, RootResolutionBlueprint]] = None
        self._is_broken: bool = False

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """
        Deterministically tear down this crafter and all owned artifacts.

        Behavior:
            * Cleans up :class:`SpellRequirements` if present.
            * Cleans up :class:`SpellSymbolicGraph` and its dependencies.
            * Resets the resolution frame (the owning :class:`Spell` keeps the
              concrete DAG and dependency ids).
            * Cleans Phase 5 artifacts (root blueprints and system index).
            * Cleans Phase 8 occurrence plans if present.
            * Resets validation state.
            * Nulls the Spell reference (but does **not** mutate/dispose the Spell).

        After cleanup, the crafter is unusable.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._cleanup_phase_artifacts_locked()
            if self._root_blueprint_phase5 is not None:
                try:
                    self._root_blueprint_phase5.cleanup()
                except Exception:
                    pass
            if self._occurrence_plan_phase8 is not None:
                try:
                    self._occurrence_plan_phase8.cleanup()
                except Exception:
                    pass
            if self._injection_plan_phase9 is not None:
                try:
                    self._injection_plan_phase9.cleanup()
                except Exception:
                    pass
            if self._override_patch_map_phase10 is not None:
                try:
                    self._override_patch_map_phase10.cleanup()
                except Exception:
                    pass
            if self._mutation_patch_map_phase10 is not None:
                try:
                    self._mutation_patch_map_phase10.cleanup()
                except Exception:
                    pass
            if self._execution_plan_phase11 is not None:
                try:
                    self._execution_plan_phase11.cleanup()
                except Exception:
                    pass
            if self._spell_system_index_phase5 is not None:
                try:
                    self._spell_system_index_phase5.cleanup()
                except Exception:
                    pass
            if self._entire_dag_blueprint_phase5 is not None:
                for blueprint in list(self._entire_dag_blueprint_phase5.values()):
                    if blueprint is None:
                        continue
                    try:
                        blueprint.cleanup()
                    except Exception:
                        pass
                try:
                    self._entire_dag_blueprint_phase5.clear()
                except Exception:
                    pass
            self._root_blueprint_phase5 = None
            self._occurrence_plan_phase8 = None
            self._injection_plan_phase9 = None
            self._override_patch_map_phase10 = None
            self._mutation_patch_map_phase10 = None
            self._execution_plan_phase11 = None
            self._spell_system_index_phase5 = None
            self._entire_dag_blueprint_phase5 = None
            self._validated_phase4 = False
            self._validated_phase6 = False
            self._is_broken = False
            self._spell_system_states = None
            self._spell = None
            self._spell_validator = None
            self._cleaned = True

        self._lock = None

    # ------------------------------------------------------------------
    # Core properties
    # ------------------------------------------------------------------

    @property
    def spell(self) -> ISpell:
        """
        The owning :class:`Spell` for this crafter.

        Returns:
            Spell: The spell instance supplied at construction time.

        Raises:
            RuntimeError:
                If this crafter has been cleaned.
        """
        self.check_cleaned()
        return self._spell

    @property
    def requirements(self) -> Optional[SpellRequirements]:
        """
        Phase 1 artifact for this spell, if it has been computed.

        This is the same object returned by :meth:`run_phase_requirements`.
        """
        self.check_cleaned()
        return self._requirements

    @property
    def symbolic_graph(self) -> Optional[SpellSymbolicGraph]:
        """
        Phase 2 symbolic graph for this spell, if it has been computed.
        """
        self.check_cleaned()
        return self._symbolic_graph

    @property
    def resolution_frame(self) -> Optional[SpellResolutionFrame]:
        """
        Phase 3 artifact for this spell, if it has been computed.

        The resolution frame is a **summary view** over the concrete
        dependency DAG that is pushed into the owning :class:`Spell` via
        :meth:`Spell._add_build_details`. It records the spell id and the
        topological order of all nodes participating in that DAG.
        """
        self.check_cleaned()
        return self._resolution_frame

    @property
    def validation_result_phase4(self) -> Any:
        """
        Phase 4 validation result artifact, if any.

        Once Phase 4 is wired, this will typically be a
        :class:`SpellValidationResult` produced by the
        :class:`SpellValidationSystem`. For now the type is kept as ``Any``
        to avoid constraining callers.
        """
        self.check_cleaned()
        return self._validation_result_phase4

    @property
    def root_blueprint_phase5(self) -> Optional[RootResolutionBlueprint]:
        """
        Deep DAG blueprint for this spell when Phase 5 attaches one.
        """
        self.check_cleaned()
        return self._root_blueprint_phase5

    @property
    def occurrence_plan_phase8(self) -> Optional[OccurrencePlan]:
        """
        Phase 8 occurrence plan artifact, if compiled for this spell.

        Returns:
            Optional[OccurrencePlan]:
                The compiled OccurrencePlan for this spell, or None if Phase 8
                has not run yet (or the spell bypasses Phase 8).
        """
        self.check_cleaned()
        return self._occurrence_plan_phase8

    @property
    def injection_plan_phase9(self) -> Optional[InjectionPlan]:
        """
        Phase 9 injection plan artifact, if compiled for this spell.

        Returns:
            Optional[InjectionPlan]:
                The compiled InjectionPlan for this spell, or None if Phase 9
                has not run yet (or the spell bypasses Phase 9).
        """
        self.check_cleaned()
        return self._injection_plan_phase9

    @property
    def override_patch_map_phase10(self) -> Optional[OverridePatchMap]:
        """
        Phase 10 override patch map artifact, if compiled for this spell.
        """
        self.check_cleaned()
        return self._override_patch_map_phase10

    @property
    def mutation_patch_map_phase10(self) -> Optional[MutationPatchMap]:
        """
        Phase 10 mutation patch map artifact, if compiled for this spell.
        """
        self.check_cleaned()
        return self._mutation_patch_map_phase10

    @property
    def execution_plan_phase11(self) -> Optional[ExecutionPlan]:
        """
        Phase 11 execution plan artifact, if compiled for this spell.
        """
        self.check_cleaned()
        return self._execution_plan_phase11

    @property
    def spell_system_index_phase5(self) -> Optional[SpellSystemIndex]:
        """Frame-level index built during Phase 5."""
        self.check_cleaned()
        return self._spell_system_index_phase5


    @property
    def validation_result_phase6(self) -> Any:
        """
        Phase 6 validation result artifact, if any.

        Once Phase 6 is wired, this will typically be a
        :class:`SpellValidationResult` produced by the
        :class:`SpellValidationSystem`. For now the type is kept as ``Any``
        to avoid constraining callers.
        """
        self.check_cleaned()
        return self._validation_result_phase6

    @property
    def validated(self) -> bool:
        """
        True if the validation phases classified this spell as valid.
        This requires both Phase 4 and Phase 6 to have passed, and the spell
        not to be marked as broken.
        """
        self.check_cleaned()
        return bool(self._validated_phase4 and self._validated_phase6 and not self._is_broken)

    @property
    def is_broken(self) -> bool:
        """
        True if the validation phase classified this spell as broken / unsafe.
        """
        self.check_cleaned()
        return self._is_broken

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def reset_phase_artifacts(self) -> None:
        """
        Release transient Phase 1-4 and Phase 6 artifacts without disposing the crafter.

        This keeps Phase 5 artifacts and validation flags intact for runtime use.
        """
        self.check_cleaned()
        with self._lock:
            if self._cleaned:
                return
            self._cleanup_phase_artifacts_locked()

    def cleanup_phase_artifacts(self) -> None:
        """
        Backward-compatible alias for reset_phase_artifacts.

        This keeps the SpellCrafter reusable for future phase runs while
        releasing transient Phase 1-4 and Phase 6 artifacts.
        """
        self.reset_phase_artifacts()

    def _cleanup_phase_artifacts_locked(self) -> None:
        """
        Internal helper to clean phase artifacts under the crafter lock.
        """
        if self._requirements is not None:
            try:
                self._requirements.cleanup()
            except Exception:
                pass

        if self._symbolic_graph is not None:
            try:
                self._symbolic_graph.cleanup()
            except Exception:
                pass

        if self._resolution_frame is not None and isinstance(self._resolution_frame, Cleanable):
            try:
                self._resolution_frame.cleanup()
            except Exception:
                pass

        if self._validation_result_phase4 is not None and isinstance(self._validation_result_phase4, Cleanable):
            try:
                self._validation_result_phase4.cleanup()
            except Exception:
                pass

        if self._validation_result_phase6 is not None and isinstance(self._validation_result_phase6, Cleanable):
            try:
                self._validation_result_phase6.cleanup()
            except Exception:
                pass

        if self._spellbook_scanner is not None:
            try:
                self._spellbook_scanner.cleanup()
            except Exception:
                pass
        self._spellbook_scanner = None
        self._resolution_frame = None
        self._requirements = None
        self._symbolic_graph = None
        self._validation_result_phase4 = None
        self._validation_result_phase6 = None

    def set_root_blueprint_phase5(self, blueprint: RootResolutionBlueprint) -> None:
        """
        Set the Phase-5 blueprint for this spell.
        """
        self.check_cleaned()
        if blueprint is None:
            raise ValueError("blueprint must not be None.")
        self._root_blueprint_phase5 = blueprint

    def set_spell_system_index_phase5(self, index: SpellSystemIndex) -> None:
        """Set the Phase-5 spell system index for this spell."""
        self.check_cleaned()
        if index is None:
            raise ValueError("index must not be None.")
        self._spell_system_index_phase5 = index

    def clear_phase5_artifacts(self) -> None:
        """
        Deterministically clear Phase-5 state and dependent Phase 8 artifacts.

        Contract:
            - Drops the Phase 5 blueprint reference.
            - Cleans and nulls any compiled OccurrencePlan.
            - Cleans and nulls any compiled InjectionPlan.
            - Leaves Phase 1-4 artifacts intact.
        """
        self._root_blueprint_phase5 = None
        if self._occurrence_plan_phase8 is not None:
            try:
                self._occurrence_plan_phase8.cleanup()
            except Exception:
                pass
        self._occurrence_plan_phase8 = None
        if self._injection_plan_phase9 is not None:
            try:
                self._injection_plan_phase9.cleanup()
            except Exception:
                pass
        self._injection_plan_phase9 = None
        if self._override_patch_map_phase10 is not None:
            try:
                self._override_patch_map_phase10.cleanup()
            except Exception:
                pass
        self._override_patch_map_phase10 = None
        if self._mutation_patch_map_phase10 is not None:
            try:
                self._mutation_patch_map_phase10.cleanup()
            except Exception:
                pass
        self._mutation_patch_map_phase10 = None
        if self._execution_plan_phase11 is not None:
            try:
                self._execution_plan_phase11.cleanup()
            except Exception:
                pass
        self._execution_plan_phase11 = None
        self._spell_system_index_phase5 = None


    def _notify_dependencies_updated(self, dependency_ids: List[str]) -> None:
        """
        Notify the SpellSystemStates registry that this spell's direct
        dependencies (by spell_id) have been updated.

        This is the Phase 3 ? system-state bridge:

        - It does *not* recompute anything itself.
        - It simply forwards the concrete dependency_ids that were pushed back
          into the owning Spell via ``_add_build_details(...)``.
        """
        # If this crafter has been cleaned, bail early; the manager may already
        # be torn down as part of frame cleanup.
        self.check_cleaned()

        if self._spell_system_states is None or self._spell.spell_index is None:
            return

        # SpellSystemStates.update_dependencies performs its own internal
        # gating and dirty-tracking based on this new edge set.
        self._spell_system_states.update_dependencies(self._spell.spell_index, dependency_ids or [])

    def _throw_if_cancelled(self, cancel_event: Optional[CancellationEvent]) -> None:
        """
        Helper that checks the cancellation token and throws if set.
        """
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

    def _iter_all_spells(self, scanner: SpellbookScanner):
        """
        Small wrapper to keep the scanner usage in one place.

        Centralising this makes it easier to plug in conduit/ward filtering
        later without touching Phase 3 logic.
        """
        return scanner.iter_all_spells()

    def _normalize_annotation_for_matching(self, annotation: Any) -> Any:
        """
        Normalize a DI annotation for Phase 3 matching.

        This unwraps Optional/Union-with-None annotations and converts
        ForwardRef tokens into their string names so name-based matching
        can succeed for local forward references.

        Args:
            annotation:
                The raw annotation object from Phase 1.

        Returns:
            Any:
                The normalized annotation to use for matching.
        """
        if isinstance(annotation, typing.ForwardRef):
            return annotation.__forward_arg__

        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin in (Union, types.UnionType) and args:
            non_none_args: List[Any] = []
            for arg in args:
                if isinstance(arg, typing.ForwardRef):
                    arg_value = arg.__forward_arg__
                else:
                    arg_value = arg
                if arg_value is type(None):
                    continue
                non_none_args.append(arg_value)

            if len(non_none_args) == 1:
                return non_none_args[0]

        return annotation

    def _matches_annotation(
            self,
            annotation: Any,
            binding_name: Optional[str],
            spell_obj: ISpell,
            *,
            require_class_spell: bool,
    ) -> bool:
        """
        Return True if ``spell_obj`` is a candidate for the given annotation.

        Matching rules (Phase 3 view):

          * Optional/Union annotations should be normalized before matching.
          * If the annotation is a string, match by spell name or frame name.
          * Then try concrete-class match: ``spell_obj.spell is annotation``.
          * Then try frame match: ``spell_obj.spellframe is/== annotation``.
          * If ``binding_name`` is not None, require an exact match.

        If ``require_class_spell`` is True, method / lambda style spells are
        excluded. This enforces the rule that *single* DI by plain type-hint
        only ever targets class/creation spells; method/lambda spells must be
        obtained explicitly via SpellMap or root-level meld.
        """
        # Filter out method / lambda style spells for "single" DI.
        if require_class_spell:
            spell_type = spell_obj.spell_type
            if spell_type in (
                    SpellType.METHOD,
                    SpellType.METHOD_WITH_BINDING_NAME,
                    SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
            ):
                return False

        if isinstance(annotation, typing.ForwardRef):
            annotation = annotation.__forward_arg__

        if isinstance(annotation, str):
            if spell_obj.spell_name == annotation:
                if binding_name is not None and spell_obj.binding_name != binding_name:
                    return False
                return True

            frame = spell_obj.spellframe
            if isinstance(frame, str) and frame == annotation:
                if binding_name is not None and spell_obj.binding_name != binding_name:
                    return False
                return True

            if inspect.isclass(frame) and frame.__name__ == annotation:
                if binding_name is not None and spell_obj.binding_name != binding_name:
                    return False
                return True

        # Concrete class match.
        if spell_obj.spell is annotation:
            if binding_name is not None and spell_obj.binding_name != binding_name:
                return False
            return True

        # Frame / protocol / string-key match.
        frame = spell_obj.spellframe
        if frame is annotation or frame == annotation:
            if binding_name is not None and spell_obj.binding_name != binding_name:
                return False
            return True

        return False

    def _resolve_single_by_annotation(
            self,
            scanner: SpellbookScanner,
            dep: SpellSymbolicDependency,
    ) -> Dict[Any, ISpell]:
        """
        Resolve a SINGLE_BY_ANNOTATION dependency to exactly one class/creation
        spell.

        Returns:
            Dict[SpellIndex, ISpell]: mapping with **exactly one** entry.

        Raises:
            RuntimeError:
                If zero or multiple candidates are found.
        """
        annotation = self._normalize_annotation_for_matching(dep.target_annotation)
        # Parameter-level binding metadata does not exist yet; we only support
        # the default binding for now.
        binding_name: Optional[str] = None

        candidates: Dict[Any, ISpell] = {}

        for index, spell_obj in self._iter_all_spells(scanner):
            if self._matches_annotation(
                    annotation,
                    binding_name,
                    spell_obj,
                    require_class_spell=True,
            ):
                candidates[index] = spell_obj

        if not candidates:
            raise RuntimeError(
                f"SpellCrafter Phase 3: no DI candidate found for parameter "
                f"{dep.param_name!r} on spell {self._spell.spell_name!r} "
                f"(annotation={annotation!r})."
            )

        if len(candidates) > 1:
            # Ambiguous single DI – tell the user how to disambiguate.
            names = ", ".join(
                sorted(spell.spell_name for spell in candidates.values())
            )
            raise RuntimeError(
                "SpellCrafter Phase 3: multiple DI candidates found for "
                f"parameter {dep.param_name!r} on spell {self._spell.spell_name!r} "
                f"(annotation={annotation!r}). "
                f"Candidates: {names}. "
                "Use a SpellMap with an explicit spellframe/binding_name or a "
                "collection type (e.g. list[FrameType]) to inject multiple "
                "implementations."
            )

        return candidates

    def _resolve_collection_by_annotation(
            self,
            scanner: SpellbookScanner,
            dep: SpellSymbolicDependency,
    ) -> Dict[Any, ISpell]:
        """
        Resolve a COLLECTION_BY_ANNOTATION dependency to **all** matching
        spells (classes, methods, lambdas) bound under the given frame/type.

        This corresponds to list[FrameType]-style DI where the user explicitly
        asked for "all implementations".

        Returns:
            Dict[SpellIndex, Spell]: mapping of all candidates. It is valid
            for this mapping to be empty (an empty collection will be injected).
        """
        annotation = self._normalize_annotation_for_matching(dep.target_annotation)
        binding_name: Optional[str] = None

        candidates: Dict[Any, ISpell] = {}

        for index, spell_obj in self._iter_all_spells(scanner):
            # For collection DI we deliberately allow methods/lambdas – the
            # frame is the grouping mechanism.
            if self._matches_annotation(
                    annotation,
                    binding_name,
                    spell_obj,
                    require_class_spell=False,
            ):
                candidates[index] = spell_obj

        return candidates

    def _socket_kind_for_dep(self, dep: SpellSymbolicDependency) -> SocketKind:
        """
        Map a symbolic dependency's DI shape into a SocketKind.

        NORMAL:
            Regular DI parameter (annotation, SpellMap, collection) or a
            plain constructor socket.
        SPELL_CONTRACT:
            SpellContract socket – must be satisfied by a provider.
        MUTATION_CONTRACT:
            MutationContract socket – can be rewired at meld-time.

        For now we classify based solely on `dep.di_shape`. If we later
        introduce additional DI shapes, this is the central mapping point.
        """
        di_shape = dep.di_shape

        if di_shape is ParameterDIShape.SPELL_CONTRACT:
            return SocketKind.SPELL_CONTRACT
        if di_shape is ParameterDIShape.MUTATION_CONTRACT:
            return SocketKind.MUTATION_CONTRACT

        return SocketKind.NORMAL

    def _dependency_key_for_dep(
            self,
            dep: SpellSymbolicDependency,
    ) -> Optional[Tuple[str, str]]:
        """
        Internal

        Resolve the canonical dependency key for a NORMAL DI socket.

        For SpellMap defaults, this uses the SpellMap's canonical key.
        For annotation-driven shapes (single/collection), this normalizes
        the frame key from the target annotation using the default binding.

        Args:
            dep: Symbolic dependency being mapped.
        Returns:
            Optional[Tuple[str, str]]: The normalized (frame_key, binding_key),
            or None if the dependency does not participate in DI keying.
        """
        if dep is None:
            return None

        if dep.di_shape is ParameterDIShape.SPELLMAP_DEFAULT:
            spellmap = dep.spellmap_default
            if spellmap is None:
                return None
            return spellmap.canonical_key

        if dep.di_shape in (
            ParameterDIShape.SINGLE_BY_ANNOTATION,
            ParameterDIShape.COLLECTION_BY_ANNOTATION,
        ):
            if dep.target_annotation is None:
                return None
            return SpellInputUtils.normalize_spell_key(
                spellframe=dep.target_annotation,
                binding_name=None,
            )

        return None

    def _resolve_spellmap_default(
            self,
            scanner: SpellbookScanner,
            dep: SpellSymbolicDependency,
    ) -> Dict[Any, ISpell]:
        """
        Resolve a SPELLMAP_DEFAULT dependency using the original SpellMap
        default attached to the parameter.

        SpellMap defaults are **explicit** – they may point at classes,
        methods, lambdas, or frame+binding pairs. We honour the user's
        intent exactly and still enforce uniqueness.
        """
        spellmap = dep.spellmap_default
        if spellmap is None:
            return {}

        candidates: Dict[Any, ISpell] = {}

        # If the SpellMap carries an explicit spell callable/class, that wins.
        explicit_spell = spellmap.spell
        frame = spellmap.spellframe
        binding_name = spellmap.binding_name

        if explicit_spell is not None:
            for index, spell_obj in self._iter_all_spells(scanner):
                if spell_obj.spell is not explicit_spell:
                    continue

                # Optional frame/binding_name refinement.
                if frame is not None:
                    spell_frame = spell_obj.spellframe
                    if not (spell_frame is frame or spell_frame == frame):
                        continue

                if binding_name is not None and spell_obj.binding_name != binding_name:
                    continue

                candidates[index] = spell_obj
        else:
            # Frame+binding only – delegate to the scanner helper.
            frame_candidates = scanner.find_by_frame_and_binding(
                spellmap.spellframe,
                spellmap.binding_name,
                include_contracted=True,
            )
            candidates.update(frame_candidates)

        if not candidates:
            raise RuntimeError(
                "SpellCrafter Phase 3: SpellMap default could not be resolved for "
                f"parameter {dep.param_name!r} on spell {self._spell.spell_name!r}. "
                f"SpellMap={spellmap!r}."
            )

        if len(candidates) > 1:
            names = ", ".join(
                sorted(spell.spell_name for spell in candidates.values())
            )
            raise RuntimeError(
                "SpellCrafter Phase 3: SpellMap default resolved to multiple "
                f"candidates for parameter {dep.param_name!r} on spell "
                f"{self._spell.spell_name!r}. Candidates: {names}. "
                "SpellMap defaults must be unambiguous."
            )

        return candidates

    # ------------------------------------------------------------------
    # Phase 1 – Requirements
    # ------------------------------------------------------------------

    def run_phase_requirements(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 1 – Analyse the Spell constructor and capture DI requirements.

        Responsibilities:
            * Inspect the bound Spell's constructor and classify every parameter
              into a :class:`ParameterDIShape` (normal DI, SpellMap, contracts, etc.).
            * Build a :class:`SpellRequirements` object that records per-parameter
              metadata (name, position, shape, optionality, annotations).
            * Store the requirements on this SpellCrafter (``_requirements``) for
              later phases to consume.

        Contracts:
            * Must only be called for a Spell that is fully constructed and
              attached to a Spellbook.
            * Does **not** call any other phases. The caller is responsible for
              running phases in order.
            * Does **not** mutate the Spell, SpellSystemStates, or any DAG
              structures. It only updates this SpellCrafter's internal state.
            * Does not return a value; consumers read ``self._requirements``.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)

        finder = SpellRequirementsFinder(self._spell)
        requirements = finder.build_requirements(cancel_event=cancel_event)
        # We deliberately do not call finder.cleanup() here, because the finder
        # owns the same SpellRequirements instance we are going to retain.
        self._requirements = requirements

    # ------------------------------------------------------------------
    # Phase 2 – Symbolic Graph
    # ------------------------------------------------------------------

    def run_phase_symbolic_graph(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 2 – Build the symbolic dependency graph for this Spell.

        Responsibilities:
            * Consume Phase 1 requirements and construct a
              :class:`SpellSymbolicGraph` describing all constructor sockets.
            * Create one :class:`SpellSymbolicDependency` per constructor
              parameter that should be represented as a socket, including:
                  - plain (caller-supplied) parameters,
                  - normal DI sockets (single, collection, SpellMap),
                  - SpellContract sockets,
                  - MutationContract sockets.
            * Store the symbolic graph on this SpellCrafter
              (``_symbolic_graph``) for later phases.

        Contracts:
            * Phase 1 (requirements) must already have run successfully.
              This method will raise if requirements are missing; it does
              **not** auto-run Phase 1.
            * Does **not** build any concrete DAG or talk to SpellSystemStates.
            * Does **not** mutate the Spell. It only updates this
              SpellCrafter's internal state.
            * Does not return a value; consumers read ``self._symbolic_graph``.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)

        if self._requirements is None:
            raise RuntimeError(
                "SpellCrafter Phase 2: cannot build symbolic graph before "
                "Phase 1 requirements have completed."
            )

        # Versioned identity from SpellIndex.
        version_id: str = self._spell.spell_index.current

        deps: List[SpellSymbolicDependency] = []

        for param in self._requirements.parameters:
            di_shape: ParameterDIShape = param.di_shape
            contract_key = None
            contract_late_binding = None

            # Only shapes that participate in the symbolic socket graph.
            if di_shape not in (
                    ParameterDIShape.SINGLE_BY_ANNOTATION,
                    ParameterDIShape.COLLECTION_BY_ANNOTATION,
                    ParameterDIShape.SPELLMAP_DEFAULT,
                    ParameterDIShape.PLAIN,
                    ParameterDIShape.SPELL_CONTRACT,
                    ParameterDIShape.MUTATION_CONTRACT,
            ):
                # Shapes like IGNORE do not participate in sockets.
                continue

            # Map shape ? symbolic metadata.
            if di_shape is ParameterDIShape.SPELLMAP_DEFAULT:
                target_annotation = None
                is_collection = False
                spellmap_default = param.spellmap_default

            elif di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION:
                target_annotation = param.annotation
                is_collection = False
                spellmap_default = None

            elif di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION:
                target_annotation = param.collection_element_annotation
                is_collection = True
                spellmap_default = None

            elif di_shape is ParameterDIShape.PLAIN:
                target_annotation = param.annotation
                is_collection = False
                spellmap_default = None

            elif di_shape is ParameterDIShape.SPELL_CONTRACT:
                # Contract socket.
                #
                # For now we reuse the raw annotation as the "target" so that
                # later phases (5-7) can infer what this contract is over,
                # without committing to any specific resolution semantics yet.
                target_annotation = param.annotation
                is_collection = False
                spellmap_default = None
                if isinstance(param.default_value, SpellContract):
                    contract_key = param.default_value.canonical_key

            elif di_shape is ParameterDIShape.MUTATION_CONTRACT:
                # Mutation socket.
                #
                # Same approach as SPELL_CONTRACT: we record the socket +
                # annotation so that later contract/mutation logic (early vs
                # late binding, _mutation_overrides, etc.) has visibility.
                target_annotation = param.annotation
                is_collection = False
                spellmap_default = None
                if isinstance(param.default_value, MutationContract):
                    contract_key = param.default_value.canonical_key
                    contract_late_binding = param.default_value.late_binding

            else:
                # Should not happen given the filter above, but kept for
                # robustness.
                continue

            dep = SpellSymbolicDependency(
                spell_version_id=version_id,
                param_name=param.name,
                position=param.position,
                di_shape=di_shape,
                is_optional=param.is_optional,
                target_annotation=target_annotation,
                is_collection=is_collection,
                spellmap_default=spellmap_default,
                contract_key=contract_key,
                contract_late_binding=contract_late_binding,
            )
            deps.append(dep)

        self._symbolic_graph = SpellSymbolicGraph(
            spell_version_id=version_id,
            dependencies=deps,
        )


    # ------------------------------------------------------------------
    # Phase 3 – Local Frame / DAG
    # ------------------------------------------------------------------
    def _build_local_topology(
            self,
            graph: SpellSymbolicGraph,
            socket_targets: Dict[tuple[str, int], List[str]],
    ) -> SpellLocalTopology:
        """
        Internal helper for Phase 3.

        Construct a :class:`SpellLocalTopology` describing this Spell's
        constructor sockets, based on:

            * the symbolic dependencies from :class:`SpellSymbolicGraph`, and
            * the concrete dependency spell ids resolved during Phase 3.

        For each :class:`SpellSymbolicDependency`:
            * Determine ``socket_kind`` from its :class:`ParameterDIShape`.
            * Copy ``is_collection`` and ``is_optional`` flags from the
              symbolic graph.
            * Look up any concrete targets via ``socket_targets`` using
                ``(param_name, position)``. Normal DI sockets may have one or
                many targets; contract, mutation, and plain sockets will
                typically have none at this phase.
            * Preserve contract metadata for SpellContract / MutationContract
              sockets (canonical key, late-binding flag).
            * Create a :class:`SpellSocketDescriptor` for that parameter.

        The resulting :class:`SpellLocalTopology` is a per-spell, constructor-
        local view of sockets that later phases (blueprint assembly, override
        targeting, change-control) will consume. It is registered into
        :class:`SpellSystemStates` by Phase 3; this method does not talk to
        SpellSystemStates directly.
        """
        self.check_cleaned()

        if self._spell is None or self._spell.spell_index is None:
            raise RuntimeError("SpellCrafter has no bound Spell with a SpellIndex.")

        spell_id = self._spell.spell_index.current
        descriptors: List[SpellSocketDescriptor] = []

        for dep in graph.dependencies:
            key = (dep.param_name, dep.position)
            targets = socket_targets.get(key)
            if targets:
                target_spell_ids = tuple(targets)
            else:
                target_spell_ids = ()

            socket_kind = self._socket_kind_for_dep(dep)

            dependency_key = None
            if socket_kind is SocketKind.NORMAL:
                dependency_key = self._dependency_key_for_dep(dep)

            descriptor = SpellSocketDescriptor(
                  spell_id=spell_id,
                  param_name=dep.param_name,
                  position=dep.position,
                  socket_kind=socket_kind,
                  is_collection=dep.is_collection,
                  is_optional=dep.is_optional,
                  target_spell_ids=target_spell_ids,
                  dependency_key=dependency_key,
                  contract_key=dep.contract_key,
                  contract_late_binding=dep.contract_late_binding,
            )
            descriptors.append(descriptor)

        topology = SpellLocalTopology(
            spell_id=spell_id,
            sockets=descriptors,
        )
        return topology


    def _build_local_frame_dag(
            self,
            requirements: SpellRequirements,
            graph: SpellSymbolicGraph,
            cancellation_event: CancellationEvent,
            *,
            return_dependencies: bool = False,
    ) -> Union[DirectedAcyclicWorkGraph, Tuple[DirectedAcyclicWorkGraph, List[str]]]:
        """
        Internal helper for Phase 3.

        Build the concrete DAG for this Spell's **local frame** and emit
        constructor topology into SpellSystemStates.

        Responsibilities:
            * Add a DAG node for the root Spell (current SpellIndex version).
            * For each symbolic dependency:
                  - resolve normal DI shapes via a SpellbookScanner,
                  - add DAG nodes for resolved dependency spells,
                  - add edges from each dependency node to the root node,
                    tagging edges with ``param_name`` and ``socket_kind``.
            * Track, per constructor socket ``(param_name, position)``, the
              concrete dependency spell ids resolved in this phase.
            * Build a :class:`SpellLocalTopology` from the symbolic graph plus
              the per-socket targets.
            * Call into :class:`SpellSystemStates` to:
                  - record direct dependency spell ids, and
                  - register the local topology for this Spell.

        Important:
            * This helper does **not** mutate the Spell object. All artifacts
              (DAG, topology, dependency ids) remain in this SpellCrafter and
              SpellSystemStates.
            * If ``return_dependencies`` is True, returns a tuple of
              ``(dag, dependency_spell_ids)``; otherwise returns only the DAG.
            * SpellContract and MutationContract sockets take part in the
              symbolic graph and topology, but do not produce DAG edges or
              concrete targets at this stage.
        """
        self.check_cleaned()

        if requirements is None:
            raise ValueError("requirements must not be None.")
        if graph is None:
            raise ValueError("graph must not be None.")

        self._throw_if_cancelled(cancellation_event)

        if self._spell is None or self._spell.spell_index is None:
            raise RuntimeError("SpellCrafter has no bound Spell with a SpellIndex.")

        root_id = self._spell.spell_index.current
        dag = DirectedAcyclicWorkGraph()

        # Register the root node first.
        dag.add_node(key=root_id, payload=self._spell)

        # Track all dependency spell IDs for SpellSystemStates.
        dependency_spell_ids: List[str] = []

        # Track per-socket resolutions for local topology:
        # keyed by (param_name, position) -> [spell_id, ...]
        socket_targets: Dict[tuple[str, int], List[str]] = {}

        self._spellbook_scanner = SpellbookScanner(self._spell._spellbook)

        for dep in graph.dependencies:
            self._throw_if_cancelled(cancellation_event)

            di_shape = dep.di_shape

            # Only "normal" DI shapes produce concrete DAG edges for now.
            if di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION:
                resolved = self._resolve_single_by_annotation(
                    scanner=self._spellbook_scanner,
                    dep=dep,
                )
            elif di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION:
                resolved = self._resolve_collection_by_annotation(
                    scanner=self._spellbook_scanner,
                    dep=dep,
                )
            elif di_shape is ParameterDIShape.SPELLMAP_DEFAULT:
                resolved = self._resolve_spellmap_default(
                    scanner=self._spellbook_scanner,
                    dep=dep,
                )
            else:
                # SpellContract / MutationContract / PLAIN and any future shapes
                # are currently metadata-only at the DAG level. They still
                # participate in local topology below.
                resolved = {}

            if not resolved:
                continue

            key = (dep.param_name, dep.position)
            targets_for_socket = socket_targets.setdefault(key, [])

            for spell_index, spell_obj in resolved.items():
                dep_spell_id = spell_index.current
                dependency_spell_ids.append(dep_spell_id)
                targets_for_socket.append(dep_spell_id)

                dag.add_node(key=dep_spell_id, payload=spell_obj)
                dag.add_dependency(
                    parent_key=dep_spell_id,
                    child_key=root_id,
                    param_name=dep.param_name,
                    socket_kind=self._socket_kind_for_dep(dep),
                )

        # Snapshot local topology for this spell's constructor.
        topology = self._build_local_topology(graph, socket_targets)

        # Update spell-system state with dependency IDs and local topology.
        if self._spell_system_states is not None and self._spell.spell_index is not None:
            self._spell_system_states.update_dependencies(
                self._spell.spell_index,
                dependency_spell_ids,
            )
            self._spell_system_states.register_local_topology(
                self._spell.spell_index,
                topology,
            )

        if return_dependencies:
            return dag, dependency_spell_ids

        return dag


    # ------------------------------------------------------------------
    # Phase 3 – Local frame / DAG
    # ------------------------------------------------------------------

    def run_phase_local_frame(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 3 – Build the local-frame DAG and constructor topology.

        Responsibilities:
            * Consume Phase 1 requirements and Phase 2 symbolic graph for the
              bound Spell.
            * Resolve **normal** DI sockets (single, collection, SpellMap)
              against the Spellbook and build a **local-frame DAG** where:
                  - the root node is this Spell's version id, and
                  - direct edges represent first-hop constructor dependencies.
            * Track, per constructor parameter, which dependency spell ids were
              bound during resolution.
            * Build a :class:`SpellLocalTopology` snapshot that describes all
              sockets (normal, SpellContract, MutationContract) and their
              concrete targets where applicable.
            * Register both:
                  - direct dependency spell ids, and
                  - the local topology
              into :class:`SpellSystemStates`.

        Socket semantics:
            * Normal DI shapes (single, collection, SpellMap) produce DAG nodes,
              DAG edges, and concrete ``target_spell_ids`` entries in topology.
            * SpellContract and MutationContract sockets are **metadata-only** at
              this phase:
                  - they appear in the symbolic graph and topology,
                  - they do **not** produce DAG edges or bound targets yet.
            * Plain parameters are **metadata-only** at this phase:
                  - they appear in the symbolic graph and topology,
                  - they do **not** produce DAG edges or bound targets.

        Contracts:
            * Phases 1 and 2 must already have completed successfully. If
              requirements or symbolic graph are missing, this method raises
              instead of auto-running earlier phases.
            * Assumes the bound Spell is attached to a Spellbook; the internal
              SpellbookScanner is created against that Spellbook.
            * Stores the local DAG and direct dependency list on the Spell via
              :meth:`Spell._add_build_details`, and keeps a
              :class:`SpellResolutionFrame` internally on this SpellCrafter.
            * Does not return a value; callers rely on:
                  - ``self._resolution_frame`` for ordering, and
                  - SpellSystemStates for dependencies and topology.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)

        if self._requirements is None or self._symbolic_graph is None:
            raise RuntimeError(
                "SpellCrafter Phase 3: cannot build local frame before "
                "Phases 1–2 have completed."
            )


        dag, dependency_spell_ids = self._build_local_frame_dag(
            requirements=self._requirements,
            graph=self._symbolic_graph,
            cancellation_event=cancel_event,
            return_dependencies=True,
        )

        # Topological order of node ids (deps first, then root).
        ordered_node_ids = dag.collect_dependency_ids()

        self._resolution_frame  = SpellResolutionFrame(
            spell_id=self._spell.spell_index.current,
            ordered_node_ids=ordered_node_ids,
        )

        # Persist dependency metadata on the Spell for validation and contract linking.
        unique_dependencies = list(dict.fromkeys(dependency_spell_ids))
        try:
            self._spell._add_build_details(
                dag=dag,
                dependencies=unique_dependencies,
            )
        except AttributeError:
            # Test stubs may not implement the build-details hook.
            pass

    # ------------------------------------------------------------------
    # Phase 4 – Validation
    # ------------------------------------------------------------------

    def run_phase_validation(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 4 – Per-spell validation using SpellValidationSystem.

        Responsibilities:
            * Assume Phases 1-3 have completed for this Spell.
            * Delegate to :class:`SpellValidationSystem` to validate this spell
              using:
                  - Phase 1 requirements,
                  - Phase 2 symbolic graph,
                  - Phase 3 resolution frame.
            * Cache the resulting :class:`SpellValidationResult` and expose it
              via :attr:`validation_result`, :attr:`validated`,
              and :attr:`is_broken`.
            * Update global structural validity (SpellSystemState) when available.

        Contracts:
            * Does **not** call Phases 1-3. If any of the required artifacts
              are missing, this method raises.
            * Does **not** mutate the Spell or build any DAGs. It only records
              validation outcome and diagnostics on this SpellCrafter.
            * If the SpellSystemState is no longer valid (unknown/gated/invalid),
              the validation is re-run even if this phase previously completed.
            * Returns ``None``; callers rely on the stored validation result and
              flags instead of a direct return value.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)

        # If we've already validated and the structural state is still valid, do nothing.
        if self._validated_phase4 and self._validation_result_phase4 is not None:
            if self._spell_system_states is not None and self._spell.spell_index is not None:
                state = self._spell_system_states.get_by_index_id(self._spell.spell_index.id)
                if state is None or state.validity is SpellValidity.valid:
                    return
            else:
                return

        # Hard contract: Phases 1–3 must have been run explicitly.
        if (
                self._requirements is None
                or self._symbolic_graph is None
                or self._resolution_frame is None
        ):
            raise RuntimeError(
                "SpellCrafter Phase 4: cannot run validation before Phases 1–3 "
                "have completed."
            )

        # Use the Spellbook-level SpellValidationSystem.
        result = self._spell_validator.validate_spell(
            spell=self._spell,
            requirements=self._requirements,
            symbolic_graph=self._symbolic_graph,
            resolution_frame=self._resolution_frame,
            cancel_event=cancel_event,
        )

        # Cache result + flags on the crafter; the Spell exposes these via
        # properties (validation_result / validated / is_broken).
        self._validation_result_phase4 = result
        self._validated_phase4 = True

        # For now: any error -> broken. You can refine this later via severity.
        self._is_broken = result.has_errors

        # Update global structural validity for this lineage.
        if self._spell_system_states is not None and self._spell.spell_index is not None:
            state = self._spell_system_states.get_by_index_id(self._spell.spell_index.id)
            if state is not None:
                if self._is_broken:
                    state.set_validity(
                        SpellValidity.invalid,
                        change_reason=SpellStateChangeReason.validation_failed,
                    )
                else:
                    state.clear_dirty(time.time())
                    state.set_validity(
                        SpellValidity.valid,
                        change_reason=SpellStateChangeReason.validation_passed,
                    )

    # ------------------------------------------------------------------
    # Phase 5 - Build Deep Dag Structures
    # ------------------------------------------------------------------

    def run_phase_root_blueprints(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 5 entrypoint.

        Builds deep DAG blueprints (RootResolutionBlueprints) and a frame-level
        SpellSystemIndex. This step uses only *existing* Phase 1-4 artifacts;
        no new discovery occurs. The resulting DAGs and index are scoped to
        spells visible to the current Spellbook (local + contracted).

        Phase 5 produces two related outputs:
            - A root-only blueprint map for system validation (Phase 6).
            - Per-spell blueprints attached to constructed spells so Phase 8-11
              compilation can proceed for any meldable spell.

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation handle.

        Returns:
            None.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)
        if not conduit_id:
            raise ValueError("conduit_id must not be empty.")

        # Phase 4 must have run; otherwise system-level work is meaningless.
        if not self._validated_phase4 and self._validation_result_phase4 is None:
            raise RuntimeError(
                "SpellCrafter Phase 5: cannot build root blueprints before "
                "Phase 4 validation has completed."
            )

        # Cache for future calls on this crafter.
        self._throw_if_cancelled(cancel_event)

        # --- 1. Build adjacency snapshot from system states ----------------
        adjacency_builder = SpellSystemAdjacencyBuilder()
        snapshot = adjacency_builder.build(self._spell_system_states)

        self._throw_if_cancelled(cancel_event)

        # --- 2. Filter to spellbook-visible spells -------------------------
        visible_spell_ids: Set[str] = set()
        version_to_spell: Dict[str, ISpell] = {}
        if self._spellbook_scanner is None:
            self._spellbook_scanner = SpellbookScanner(self._spell._spellbook)
        for spell_index, spell_instance in self._spellbook_scanner.iter_spells():
            spell_id = spell_index.current
            visible_spell_ids.add(spell_id)
            version_to_spell[spell_id] = spell_instance

        filtered_snapshot = self._filter_snapshot_to_visible_spells(
            snapshot=snapshot,
            visible_spell_ids=visible_spell_ids,
        )

        self._throw_if_cancelled(cancel_event)

        # --- 3. Build deep DAGs for visible roots --------------------------
        root_builder = SpellSystemRootBlueprintBuilder()
        root_blueprints = root_builder.build_root_blueprints(filtered_snapshot)

        self._throw_if_cancelled(cancel_event)

        # --- 4. Construct system-level index -------------------------------
        system_index = SpellSystemIndex()

        for spell_id, deps in filtered_snapshot.dependencies.items():
            self._throw_if_cancelled(cancel_event)

            lineage_id: Optional[str] = None
            state = self._spell_system_states.get_by_spell_id(spell_id)
            if state is not None:
                lineage_id = state.spell_index_id

            spell_instance = version_to_spell.get(spell_id)
            if lineage_id is None and spell_instance is not None:
                lineage_id = spell_instance.spell_index.id

            node = SpellSystemNode(
                spell_id=spell_id,
                lineage_id=lineage_id,
                dependencies=deps,
                existence=spell_instance.existence if spell_instance is not None else None,
                spell_type=spell_instance.spell_type if spell_instance is not None else None,
                conduit_id=spell_instance._owner_conduit_id if spell_instance is not None else None,
                ward_id=None,
                is_root=spell_id in filtered_snapshot.root_spell_ids,
            )

            system_index.upsert_node(node)

        # --- 5. Attach artifacts to SpellCrafters -------------------------
        for spell_id, spell_instance in version_to_spell.items():
            self._throw_if_cancelled(cancel_event)

            crafter_for_spell = spell_instance._crafter
            if crafter_for_spell is None:
                continue

            crafter_for_spell.set_spell_system_index_phase5(system_index)

            if spell_instance.is_existing_creation:
                # Existing-creation spells do not require execution plans.
                continue

            blueprint = root_blueprints.get(spell_id)
            if blueprint is None:
                blueprint = root_builder.build_blueprint_for_spell_id(
                    root_spell_id=spell_id,
                    snapshot=filtered_snapshot,
                )

            crafter_for_spell.set_root_blueprint_phase5(blueprint)

        # --- 6. Store artifacts on self for completeness -------------------
        # The root-only blueprint map is retained for system validation; per-spell
        # blueprints are attached directly to each SpellCrafter above.
        self._spell_system_index_phase5 = system_index
        self._entire_dag_blueprint_phase5 = root_blueprints

        # Rebuild component-of index in ChangeControlManager if available and
        # register a revalidation hook for dirty roots.
        try:
            spellbook = self._spell._spellbook
            frame_name = spellbook._aetheric_frame
            change_control_manager = spellbook._aether._get_change_control_manager(frame_name)
            if change_control_manager is not None:
                change_control_manager.rebuild_component_of(root_blueprints)

                def _revalidate_dirty_roots(
                        dirty_roots: Set[str],
                        cancel_event: Optional[CancellationEvent],
                ) -> Set[str]:
                    """
                    Re-run Phases 1-7 for the supplied root spell_ids.

                    Returns:
                        Set[str]:
                            Root ids that successfully revalidated.
                    """
                    # Scanner scoped to this invocation to avoid stale spell refs.
                    scanner = SpellbookScanner(spellbook)
                    version_to_spell: Dict[str, ISpell] = {}
                    for spell_index, spell_instance in scanner.iter_spells():
                        version_to_spell[spell_index.current] = spell_instance

                    validated_roots: Set[str] = set()
                    for root_id in dirty_roots:
                        if cancel_event is not None and cancel_event.is_set:
                            cancel_event.throw_if_set()
                        spell_instance = version_to_spell.get(root_id)
                        if spell_instance is None:
                            continue
                        crafter = getattr(spell_instance, "_crafter", None)
                        if crafter is None:
                            continue
                        try:
                            crafter.run_all_phases(conduit_id=conduit_id, cancel_event=cancel_event)
                        except Exception:
                            # Leave dirty flags intact on failure.
                            raise
                        validated_roots.add(root_id)

                    return validated_roots

                change_control_manager.set_revalidator(_revalidate_dirty_roots)
        except Exception:
            # Change control is optional; ignore if unavailable.
            pass

    def _filter_snapshot_to_visible_spells(
            self,
            *,
            snapshot: SpellSystemAdjacencySnapshot,
            visible_spell_ids: Set[str],
    ) -> SpellSystemAdjacencySnapshot:
        """
        Internal

        Filter a frame-wide adjacency snapshot to spells visible in this Spellbook.

        Purpose:
            Ensure Phase-5/6 validation only considers spells that the current
            Spellbook can resolve (local + contracted).
        Contract:
            - Dependencies outside the visible set are excluded.
            - Root spell ids are recomputed for the filtered graph.
            - Topologies are retained only for visible spell ids.
        Args:
            snapshot:
                Frame-wide SpellSystemAdjacencySnapshot to filter.
            visible_spell_ids:
                Version ids visible to this Spellbook.
        Returns:
            SpellSystemAdjacencySnapshot:
                A filtered snapshot scoped to the provided spell ids.
        Raises:
            ValueError:
                If snapshot or visible_spell_ids is None.
        """
        self.check_cleaned()
        if snapshot is None:
            raise ValueError("snapshot must not be None.")
        if visible_spell_ids is None:
            raise ValueError("visible_spell_ids must not be None.")

        all_spell_ids: Set[str] = set(visible_spell_ids)
        dependencies: Dict[str, Set[str]] = {}
        reverse_dependencies: Dict[str, Set[str]] = {}
        topologies: Dict[str, "SpellLocalTopology"] = {}

        for spell_id in all_spell_ids:
            deps = snapshot.dependencies.get(spell_id)
            if deps is None:
                dep_set = set()
            else:
                dep_set = {dep_id for dep_id in deps if dep_id in all_spell_ids}
            dependencies[spell_id] = dep_set
            for dep_id in dep_set:
                parents_for_dep = reverse_dependencies.get(dep_id)
                if parents_for_dep is None:
                    parents_for_dep = set()
                    reverse_dependencies[dep_id] = parents_for_dep
                parents_for_dep.add(spell_id)

            topology = snapshot.topologies.get(spell_id)
            if topology is not None:
                topologies[spell_id] = topology

        all_dependency_ids: Set[str] = set()
        for dep_set in dependencies.values():
            all_dependency_ids.update(dep_set)
        root_spell_ids = all_spell_ids.difference(all_dependency_ids)

        return SpellSystemAdjacencySnapshot(
            dependencies=dependencies,
            reverse_dependencies=reverse_dependencies,
            all_spell_ids=all_spell_ids,
            root_spell_ids=root_spell_ids,
            topologies=topologies,
        )


    # ------------------------------------------------------------------
    # Phase 8 - Occurrence Plan
    # ------------------------------------------------------------------

    def run_phase_occurrence_plan(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 8 - Occurrence plan compilation.

        Compiles an OccurrencePlan for spells with attached Phase-5 blueprints.
        Existing-creation spells are treated as a no-op.

        Contract:
            - Requires Phase 5 artifacts to be available.
            - Builds plan only when a blueprint is attached for this spell.
            - Replaces any existing OccurrencePlan for this spell.

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)
        if not conduit_id:
            raise ValueError("conduit_id must not be empty.")
        if self._spell.is_existing_creation:
            return
        if self._entire_dag_blueprint_phase5 is None:
            raise RuntimeError(
                "SpellCrafter Phase 8: cannot compile occurrence plans before Phase 5 has completed."
            )

        root_blueprint = self._root_blueprint_phase5
        if root_blueprint is None:
            raise RuntimeError(
                "SpellCrafter Phase 8: root blueprint missing for spell."
            )

        if self._spellbook_scanner is None:
            self._spellbook_scanner = SpellbookScanner(self._spell._spellbook)

        spell_lookup: Dict[str, ISpell] = {}
        for spell_index, spell_instance in self._spellbook_scanner.iter_spells():
            spell_lookup[spell_index.current] = spell_instance

        builder = OccurrencePlanBuilder(
            root_spell=self._spell,
            blueprint=root_blueprint,
            spell_lookup=spell_lookup,
            system_states=self._spell_system_states,
        )
        plan = builder.build()

        if self._occurrence_plan_phase8 is not None:
            try:
                self._occurrence_plan_phase8.cleanup()
            except Exception:
                pass

        self._occurrence_plan_phase8 = plan


    # ------------------------------------------------------------------
    # Phase 9 - Injection Plan
    # ------------------------------------------------------------------

    def run_phase_injection_plan(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
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
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.

        Raises:
            ValueError:
                If conduit_id is empty.
            RuntimeError:
                If Phase 8 artifacts are missing for this spell or if the
                root blueprint is missing for this spell.
            OperationCancelledError:
                If cancel_event signals cancellation.

        Threading:
            - Not thread-safe; expected to run under spellbook phase scheduling.

        Lifecycle:
            - Cleans and replaces any prior InjectionPlan for this spell.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)
        if not conduit_id:
            raise ValueError("conduit_id must not be empty.")
        if self._spell.is_existing_creation:
            return

        root_blueprint = self._root_blueprint_phase5
        if root_blueprint is None:
            raise RuntimeError(
                "SpellCrafter Phase 9: root blueprint missing for spell."
            )

        if self._occurrence_plan_phase8 is None:
            raise RuntimeError(
                "SpellCrafter Phase 9: cannot compile injection plans before Phase 8 has completed."
            )

        builder = InjectionPlanBuilder(
            occurrence_plan=self._occurrence_plan_phase8,
        )
        plan = builder.build()

        if self._injection_plan_phase9 is not None:
            try:
                self._injection_plan_phase9.cleanup()
            except Exception:
                pass

        self._injection_plan_phase9 = plan


    # ------------------------------------------------------------------
    # Phase 10 - Patch Maps
    # ------------------------------------------------------------------

    def run_phase_patch_maps(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 10 - Patch map compilation.

        Compiles override and mutation patch maps for spells using
        Phase-5 blueprints. Existing-creation spells are treated as a no-op.

        Purpose:
            Precompute override and mutation targeting so meld can apply
            TargetSpec overrides without scanning the blueprint every call.

        Contract:
            - Requires Phase 5 artifacts to be available.
            - Builds maps only when a blueprint is attached for this spell.
            - Replaces any existing patch maps for this spell.
            - Does not mutate the root blueprint.

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.

        Raises:
            ValueError:
                If conduit_id is empty.
            RuntimeError:
                If Phase 5 artifacts are missing or the root blueprint is missing
                for this spell.
            OperationCancelledError:
                If cancel_event signals cancellation.

        Threading:
            - Not thread-safe; expected to run under spellbook phase scheduling.

        Lifecycle:
            - Cleans and replaces any prior patch maps for this spell.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)
        if not conduit_id:
            raise ValueError("conduit_id must not be empty.")
        if self._spell.is_existing_creation:
            return
        if self._entire_dag_blueprint_phase5 is None:
            raise RuntimeError(
                "SpellCrafter Phase 10: cannot compile patch maps before Phase 5 has completed."
            )

        root_blueprint = self._root_blueprint_phase5
        if root_blueprint is None:
            raise RuntimeError(
                "SpellCrafter Phase 10: root blueprint missing for spell."
            )

        builder = PatchMapBuilder(
            blueprint=root_blueprint,
        )
        override_patch_map = builder.build_override_patch_map()
        mutation_patch_map = builder.build_mutation_patch_map()

        if self._override_patch_map_phase10 is not None:
            try:
                self._override_patch_map_phase10.cleanup()
            except Exception:
                pass
        if self._mutation_patch_map_phase10 is not None:
            try:
                self._mutation_patch_map_phase10.cleanup()
            except Exception:
                pass

        self._override_patch_map_phase10 = override_patch_map
        self._mutation_patch_map_phase10 = mutation_patch_map


    # ------------------------------------------------------------------
    # Phase 11 - Execution Plan
    # ------------------------------------------------------------------

    def run_phase_execution_plan(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 11 - Execution plan compilation.

        Compiles a Phase 11 ExecutionPlan for spells using Phase 8–10
        artifacts. Existing-creation spells are treated as a no-op.

        Contract:
            - Requires Phase 8 artifacts to be available.
            - Uses Phase 9 injection plan when available.
            - Replaces any existing ExecutionPlan for this spell.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)
        if not conduit_id:
            raise ValueError("conduit_id must not be empty.")
        if self._spell.is_existing_creation:
            return

        root_blueprint = self._root_blueprint_phase5
        if root_blueprint is None:
            raise RuntimeError(
                "SpellCrafter Phase 11: root blueprint missing for spell."
            )

        if self._occurrence_plan_phase8 is None:
            raise RuntimeError(
                "SpellCrafter Phase 11: cannot compile execution plans before Phase 8 has completed."
            )

        if self._spellbook_scanner is None:
            self._spellbook_scanner = SpellbookScanner(self._spell._spellbook)

        spell_lookup: Dict[str, ISpell] = {}
        for spell_index, spell_instance in self._spellbook_scanner.iter_spells():
            spell_lookup[spell_index.current] = spell_instance

        builder = ExecutionPlanBuilder(
            occurrence_plan=self._occurrence_plan_phase8,
            injection_plan=self._injection_plan_phase9,
            spell_lookup=spell_lookup,
        )
        plan = builder.build()

        if self._execution_plan_phase11 is not None:
            try:
                self._execution_plan_phase11.cleanup()
            except Exception:
                pass

        self._execution_plan_phase11 = plan


    # ------------------------------------------------------------------
    # Phase 6 - System-level Validation
    # ------------------------------------------------------------------

    def run_phase_system_validation(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 6 - System-level validation.

        Runs system-level validation strategies over Phase-5 artifacts and
        Phase-4 outcomes. Records per-conduit resolution validity via
        SpellSystemStates and caches the frame-level validation state locally.

        Note:
            When Phase-4 results have been cleaned but Phase 4 previously
            completed successfully, we still include a placeholder entry
            in the phase4_results map so MissingPhase4Strategy can treat
            the spell as validated.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)
        if not conduit_id:
            raise ValueError("conduit_id must not be empty.")
        if self._entire_dag_blueprint_phase5 is None or self._spell_system_index_phase5 is None:
            raise RuntimeError(
                "SpellCrafter Phase 6: cannot run system validation before Phase 5 has completed."
            )

        if self._spellbook_scanner is None:
            self._spellbook_scanner = SpellbookScanner(self._spell._spellbook)

        phase4_results: Dict[str, Any] = {}
        broken_spell_ids: Set[str] = set()
        spell_lookup: Dict[str, ISpell] = {}
        phase4_placeholder = object()

        for spell_index, spell_instance in self._spellbook_scanner.iter_spells():
            spell_lookup[spell_index.current] = spell_instance
            crafter = spell_instance._crafter
            if crafter is None:
                continue
            if crafter._validation_result_phase4 is not None:
                phase4_results[spell_index.current] = crafter._validation_result_phase4
            elif crafter._validated_phase4:
                phase4_results[spell_index.current] = phase4_placeholder
            if crafter._is_broken:
                broken_spell_ids.add(spell_index.current)

        strategies = [
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

        validator = SpellSystemValidationSystem(strategies=strategies)
        validation_state: SpellSystemValidationState = validator.validate(
            index=self._spell_system_index_phase5,
            blueprints=self._entire_dag_blueprint_phase5,
            phase4_results=phase4_results,
            broken_spell_ids=broken_spell_ids,
            spell_system_states=self._spell_system_states,
            conduit_id=conduit_id,
            spell_lookup=spell_lookup,
            cancel_event=cancel_event,
        )

        self._validation_result_phase6 = validation_state
        self._validated_phase6 = True


    # ------------------------------------------------------------------
    # Phase 7 – Change-control / Component-of Index
    # ------------------------------------------------------------------

    def run_phase_change_control(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 7 - Change-control wiring.

        Behaviour (frame-level, idempotent):
        - Ensure ChangeControlManager is present for the frame.
        - Ensure the component-of index is (re)built from the Phase-5 root blueprints.
        - Ensure the revalidator hook is registered.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)
        if not conduit_id:
            raise ValueError("conduit_id must not be empty.")
        self._ensure_change_control_ready(conduit_id)

    def _ensure_change_control_ready(self, conduit_id: str) -> None:
        """
        Internal helper to (re)wire change-control after Phase 5 artifacts exist.
        """
        try:
            spellbook = self._spell._spellbook
            frame_name = spellbook._aetheric_frame
            change_control_manager = spellbook._aether._get_change_control_manager(frame_name)
            if change_control_manager is None:
                return
            # Rebuild component-of if we have root blueprints.
            if self._entire_dag_blueprint_phase5:
                change_control_manager.rebuild_component_of(self._entire_dag_blueprint_phase5)
            # Register revalidator if missing.
            if change_control_manager._revalidate_fn is None:
                def _revalidate_dirty_roots(
                        dirty_roots: Set[str],
                        cancel_event: Optional[CancellationEvent],
                ) -> Set[str]:
                    scanner = SpellbookScanner(spellbook)
                    version_to_spell: Dict[str, ISpell] = {}
                    for spell_index, spell_instance in scanner.iter_spells():
                        version_to_spell[spell_index.current] = spell_instance

                    validated_roots: Set[str] = set()
                    for root_id in dirty_roots:
                        if cancel_event is not None and cancel_event.is_set:
                            cancel_event.throw_if_set()
                        spell_instance = version_to_spell.get(root_id)
                        if spell_instance is None:
                            continue
                        crafter = spell_instance._crafter
                        if crafter is None:
                            continue
                        crafter.run_all_phases(conduit_id=conduit_id, cancel_event=cancel_event)
                        validated_roots.add(root_id)

                    return validated_roots

                change_control_manager.set_revalidator(_revalidate_dirty_roots)
        except Exception:
            # Change-control is optional; ignore wiring failures.
            pass


    # ------------------------------------------------------------------
    # Convenience – run all phases
    # ------------------------------------------------------------------

    def run_structural_phases(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Convenience helper to run **structural phases only** (1-4) in sequence.

        This is typically invoked via :meth:`Spell.run_structural_phases` and
        is used for global, conduit-agnostic structural validation.

        Execution order:
            1. Requirements (Phase 1)
            2. Symbolic graph (Phase 2)
            3. Local frame / DAG (Phase 3)
            4. Validation (Phase 4)

        Returns:
            None. The crafter retains all intermediate artifacts until
            :meth:`cleanup` is called. The owning Spell only needs to hold the
            final DAG and dependency spell_ids once Phase 3 is fully implemented.
        Notes:
            Phase artifacts are cleaned after Phase 7; structural data remains in
            SpellSystemStates and on the Spell itself.
        """
        self.run_phase_requirements(cancel_event=cancel_event)
        self.run_phase_symbolic_graph(cancel_event=cancel_event)
        self.run_phase_local_frame(cancel_event=cancel_event)
        self.run_phase_validation(cancel_event=cancel_event)

    def run_all_phases(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Convenience helper to run all phases in sequence for this spell.

        This is typically invoked via :meth:`Spell.run_all_phases` (a facade)
        and is intended for batch compilation / `meld()` cycles.

        Execution order:
            - Phase 1: Requirements
            - Phase 2: Symbolic graph
            - Phase 3: Local frame / DAG
            - Phase 4: Validation
            - Phase 5: Root blueprints
            - Phase 8: Occurrence plan
            - Phase 9: Injection plan
            - Phase 10: Patch maps
            - Phase 11: Execution plan
            - Phase 6: System validation
            - Phase 7: Change control

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None. The crafter retains all intermediate artifacts until
            :meth:`cleanup` is called. The owning Spell only needs to hold the
            final DAG and dependency spell_ids once Phase 3 is fully implemented.
        """
        if not conduit_id:
            raise ValueError("conduit_id must not be empty.")
        self.run_phase_requirements(cancel_event=cancel_event)
        self.run_phase_symbolic_graph(cancel_event=cancel_event)
        self.run_phase_local_frame(cancel_event=cancel_event)
        self.run_phase_validation(cancel_event=cancel_event)
        self.run_phase_root_blueprints(conduit_id, cancel_event=cancel_event)
        self.run_phase_occurrence_plan(conduit_id, cancel_event=cancel_event)
        self.run_phase_injection_plan(conduit_id, cancel_event=cancel_event)
        self.run_phase_patch_maps(conduit_id, cancel_event=cancel_event)
        self.run_phase_execution_plan(conduit_id, cancel_event=cancel_event)
        self.run_phase_system_validation(conduit_id, cancel_event=cancel_event)
        self.run_phase_change_control(conduit_id, cancel_event=cancel_event)
        self.cleanup_phase_artifacts()
