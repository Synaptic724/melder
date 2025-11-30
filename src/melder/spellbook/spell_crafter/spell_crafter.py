from __future__ import annotations
import threading
from typing import Any, Optional, List, Dict, Tuple
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
from melder.spellbook.spell_types.spell_types import SpellType
from melder.utilities.general_base.cleanable import Cleanable
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_requirements_finder import (
    SpellRequirementsFinder,
)
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_requirements import (
    SpellRequirements,
)
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.utilities.interfaces.interfaces import ISpell, ISpellSystemStates
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from melder.spellbook.spell_crafter.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind


class SpellCrafter(Cleanable):
    """
    Per-spell **compiler / resolution helper**.

    This object owns all *ephemeral* artifacts across the four conceptual
    phases for a single :class:`Spell`:

        1. Requirements (signature → SpellRequirements)
        2. Symbolic graph (requirements → symbolic DI edges)
        3. Local frame / DAG (symbolic graph + Spellbook → executable frame)
        4. Validation (frame + policies → validated / broken flags)

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

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_spell",
        "_requirements",
        "_symbolic_graph",
        "_resolution_frame",
        "_validation_result",
        "_validated",
        "_is_broken",
        "_spell_validator",
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
        self._requirements: Optional[SpellRequirements] = None
        self._symbolic_graph: Optional[SpellSymbolicGraph] = None
        # Phase 3 artifact – currently a SpellResolutionFrame summarising the
        # concrete dependency DAG that is pushed into the owning Spell.
        self._resolution_frame: Optional[SpellResolutionFrame] = None
        self._validation_result: Any = None
        self._validated: bool = False
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
            * Resets validation state.
            * Nulls the Spell reference (but does **not** mutate/dispose the Spell).

        After cleanup, the crafter is unusable.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

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

            if self._validation_result is not None and isinstance(self._validation_result, Cleanable):
                try:
                    self._validation_result.cleanup()
                except Exception:
                    pass

            # Resolution frame is a lightweight summary; just drop it.
            self._resolution_frame = None
            self._validation_result = None
            self._spell_system_states = None
            self._validated = False
            self._is_broken = False
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
    def validation_result(self) -> Any:
        """
        Phase 4 validation result artifact, if any.

        Once Phase 4 is wired, this will typically be a
        :class:`SpellValidationResult` produced by the
        :class:`SpellValidationSystem`. For now the type is kept as ``Any``
        to avoid constraining callers.
        """
        self.check_cleaned()
        return self._validation_result

    @property
    def validated(self) -> bool:
        """
        True if Phase 4 has run and marked this spell as validated.
        """
        self.check_cleaned()
        return self._validated

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
    def _notify_dependencies_updated(self, dependency_ids: List[str]) -> None:
        """
        Notify the SpellSystemStates registry that this spell's direct
        dependencies (by spell_id) have been updated.

        This is the Phase 3 → system-state bridge:

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

          * First try concrete-class match: ``spell_obj.spell is annotation``.
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
        annotation = dep.target_annotation
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
        annotation = dep.target_annotation
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
            Regular DI parameter (annotation, SpellMap, collection).
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
    ) -> SpellRequirements:
        """
        Phase 1 – Requirements Extraction.

        Uses :class:`SpellRequirementsFinder` to:

            * Inspect the spell’s call target (class/function/method).
            * Derive parameter-level DI metadata.
            * Produce a :class:`SpellRequirements` object keyed by the spell’s
              version ID (SpellIndex.current).

        This method is idempotent; repeated calls reuse the same requirements.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)

        if self._requirements is not None:
            return self._requirements

        finder = SpellRequirementsFinder(self._spell)
        requirements = finder.build_requirements(cancel_event=cancel_event)
        # We deliberately do not call finder.cleanup() here, because the finder
        # owns the same SpellRequirements instance we are going to retain.
        self._requirements = requirements
        return requirements

    # ------------------------------------------------------------------
    # Phase 2 – Symbolic Graph
    # ------------------------------------------------------------------

    def run_phase_symbolic_graph(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> SpellSymbolicGraph:
        """
        Phase 2 – Symbolic Graph Construction.

        Consumes Phase 1 requirements and builds a :class:`SpellSymbolicGraph`
        for this spell version. The graph describes DI *intents* (parameter →
        type / SpellMap / contract sockets) but does not bind to concrete
        spell IDs.

        Current strategy
        ----------------
        * Walk all parameter requirements.
        * For each parameter with a DI shape of:
            - SINGLE_BY_ANNOTATION
            - COLLECTION_BY_ANNOTATION
            - SPELLMAP_DEFAULT
            - SPELL_CONTRACT
            - MUTATION_CONTRACT
          construct a :class:`SpellSymbolicDependency` and add it to the graph.

        Notes on contracts / mutation sockets
        -------------------------------------
        * SPELL_CONTRACT and MUTATION_CONTRACT entries are **recorded** in the
          symbolic graph so later phases (5–7, frame-level DevOps) can see
          where contract/mutation sockets exist.
        * Phase 3 currently ignores these shapes for concrete DI resolution;
          they behave as metadata-only edges until we wire the contract/mutation
          semantics into the DAG / change-control machinery.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)

        if self._symbolic_graph is not None:
            return self._symbolic_graph

        requirements = self._requirements or self.run_phase_requirements(
            cancel_event=cancel_event
        )

        # Versioned identity from SpellIndex.
        version_id: str = self._spell.spell_index.current

        deps: List[SpellSymbolicDependency] = []

        for param in requirements.parameters:
            di_shape: ParameterDIShape = param.di_shape

            # Only shapes that participate in the symbolic DI graph.
            if di_shape not in (
                    ParameterDIShape.SINGLE_BY_ANNOTATION,
                    ParameterDIShape.COLLECTION_BY_ANNOTATION,
                    ParameterDIShape.SPELLMAP_DEFAULT,
                    ParameterDIShape.SPELL_CONTRACT,
                    ParameterDIShape.MUTATION_CONTRACT,
            ):
                # Shapes like IGNORE/PLAIN do not participate in DI edges.
                continue

            # Map shape → symbolic metadata.
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

            elif di_shape is ParameterDIShape.SPELL_CONTRACT:
                # Contract socket.
                #
                # For now we reuse the raw annotation as the "target" so that
                # later phases (5–7) can infer what this contract is over,
                # without committing to any specific resolution semantics yet.
                target_annotation = param.annotation
                is_collection = False
                spellmap_default = None

            elif di_shape is ParameterDIShape.MUTATION_CONTRACT:
                # Mutation socket.
                #
                # Same approach as SPELL_CONTRACT: we record the socket +
                # annotation so that later contract/mutation logic (early vs
                # late binding, _mutation_overrides, etc.) has visibility.
                target_annotation = param.annotation
                is_collection = False
                spellmap_default = None

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
            )
            deps.append(dep)

        graph = SpellSymbolicGraph(
            spell_version_id=version_id,
            dependencies=deps,
        )
        self._symbolic_graph = graph
        return graph


    # ------------------------------------------------------------------
    # Phase 3 – Local Frame / DAG
    # ------------------------------------------------------------------
    def _build_local_topology(
            self,
            graph: SpellSymbolicGraph,
            socket_targets: Dict[tuple[str, int], List[str]],
    ) -> SpellLocalTopology:
        """
        Internal

        Build a :class:`SpellLocalTopology` for this Spell's constructor based
        on the symbolic dependency graph and the concrete DI resolutions
        performed in Phase 3.

        Args:
            graph:
                The symbolic dependency graph produced in Phase 2.

            socket_targets:
                A mapping keyed by ``(param_name, position)`` to the list of
                dependency spell IDs that this socket resolved to during
                Phase 3. If a socket did not produce any concrete DI edges
                (e.g. SpellContract / MutationContract), its entry will be
                missing and we treat its targets as an empty tuple.
        """
        spell_id = self._spell.spell_index.current
        descriptors: List[SpellSocketDescriptor] = []

        for dep in graph.dependencies:
            key = (dep.param_name, dep.position)
            target_ids = socket_targets.get(key)
            if target_ids:
                target_spell_ids: Tuple[str, ...] = tuple(target_ids)
            else:
                target_spell_ids = ()

            socket_kind = self._socket_kind_for_dep(dep)
            descriptor = SpellSocketDescriptor(
                spell_id=spell_id,
                param_name=dep.param_name,
                position=dep.position,
                socket_kind=socket_kind,
                is_collection=dep.is_collection,
                is_optional=dep.is_optional,
                target_spell_ids=target_spell_ids,
            )
            descriptors.append(descriptor)

        topology = SpellLocalTopology(
            spell_id=spell_id,
            sockets=descriptors,
        )
        return topology




    def run_phase_local_frame(
            self,
            requirements: SpellRequirements,
            graph: SpellSymbolicGraph,
            cancellation_event: CancellationEvent,
    ) -> DirectedAcyclicWorkGraph:
        """
        Phase 3: Build the concrete DAG for this Spell's local frame.

        Responsibilities:
            * Instantiate a DAG node for this Spell (root of the local frame).
            * Resolve all **normal** DI shapes (single, collection, SpellMap).
            * Add concrete dependency nodes / edges to the DAG.
            * Notify :class:`SpellSystemStates` about dependency topology.

        Note:
            SpellContract and MutationContract sockets are currently treated as
            metadata-only sockets. They participate in the symbolic graph and
            local topology but do not yet produce concrete DI edges. Later
            phases (5–7) and the override pipeline will wire their semantics.
        """
        self.check_cleaned()

        if requirements is None:
            raise ValueError("requirements must not be None.")
        if graph is None:
            raise ValueError("graph must not be None.")
        if cancellation_event is None:
            raise ValueError("cancellation_event must not be None.")

        with self._lock:
            if self._spell is None:
                raise RuntimeError("SpellCrafter has no bound Spell.")

            root_id = self._spell.spell_index.current
            dag = DirectedAcyclicWorkGraph(root_id=root_id)

            # Register the root node first.
            dag.add_node(key=root_id, payload=self._spell)

            # Track all dependency spell IDs for SpellSystemStates.
            dependency_spell_ids: List[str] = []

            # Track per-socket resolutions for local topology:
            # keyed by (param_name, position) -> [spell_id, ...]
            socket_targets: Dict[tuple[str, int], List[str]] = {}

            for dep in graph.dependencies:
                if cancellation_event.is_set():
                    raise RuntimeError("SpellCrafter Phase 3 cancelled.")

                # Determine DI shape and resolve only the "normal" DI shapes.
                di_shape = dep.di_shape

                if di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION:
                    resolved = self._resolve_single_by_annotation(dep)
                elif di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION:
                    resolved = self._resolve_collection_by_annotation(dep)
                elif di_shape is ParameterDIShape.SPELLMAP_DEFAULT:
                    resolved = self._resolve_spellmap_default(dep)
                else:
                    # SpellContract / MutationContract and any future shapes
                    # are currently metadata-only at the DAG level. They still
                    # participate in local topology below.
                    resolved = {}

                if resolved:
                    key = (dep.param_name, dep.position)
                    targets_for_socket = socket_targets.setdefault(key, [])

                    for spell_index, spell_obj in resolved.items():
                        dep_spell_id = spell_index.current
                        dependency_spell_ids.append(dep_spell_id)
                        targets_for_socket.append(dep_spell_id)

                        dag.add_node(key=dep_spell_id, payload=spell_obj)
                        dag.add_dependency(parent_key=dep_spell_id, child_key=root_id)

            # Snapshot local topology for this spell's constructor.
            topology = self._build_local_topology(graph, socket_targets)

            # Update spell state system with dependency IDs and local topology.
            try:
                self._spell_system_states.update_dependencies(
                    self._spell.spell_index,
                    dependency_spell_ids,
                )
                self._spell_system_states.register_local_topology(
                    self._spell.spell_index,
                    topology,
                )
            except Exception as exc:
                self._logger.error(
                    f"Failed to update SpellSystemStates for spell_id={root_id}: {exc!r}",
                    method_name="run_phase_local_frame",
                    exc_info=True,
                )
                raise

            # Attach DAG + dependency info to the Spell for diagnostic / reuse.
            self._spell._add_build_details(
                requirements=requirements,
                graph=graph,
                dag=dag,
                dependency_spell_ids=dependency_spell_ids,
            )

            return dag


    # ------------------------------------------------------------------
    # Phase 4 – Validation
    # ------------------------------------------------------------------

    def run_phase_validation(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> Any:
        """
        Phase 4 – Validation.

        Responsibilities (current increment):

            * Ensure Phase 1–3 artifacts are available.
            * Invoke :class:`SpellValidationSystem` with a fully-populated
              :class:`SpellValidationContext`.
            * Store the resulting validation artifact and derived flags:

                - :attr:`_validation_result`
                - :attr:`_validated`
                - :attr:`_is_broken`

        Validation does **not** mutate the Spellbook or the Spell graph; it
        only produces diagnostics about structural correctness and safety.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)

        if self._validated and self._validation_result is not None:
            return self._validation_result

        # Ensure earlier phases have run so strategies have full context.
        requirements = self._requirements or self.run_phase_requirements(
            cancel_event=cancel_event
        )
        symbolic_graph = self._symbolic_graph or self.run_phase_symbolic_graph(
            cancel_event=cancel_event
        )
        resolution_frame = self._resolution_frame or self.run_phase_local_frame(
            cancel_event=cancel_event
        )

        result = self._spell_validator.validate_spell(
            spell=self._spell,
            requirements=requirements,
            symbolic_graph=symbolic_graph,
            resolution_frame=resolution_frame,
            cancel_event=cancel_event,
        )

        self._validation_result = result
        self._validated = True
        # Treat any validation error as "broken" for now; we can refine this
        # later with severity levels / policies.
        self._is_broken = bool(getattr(result, "has_errors", False))

        return result
    # ------------------------------------------------------------------
    # Phase 5 - Build Deep Dag Structures
    # ------------------------------------------------------------------
    def run_phase_root_blueprints(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 5 – RootResolutionBlueprint assembly (placeholder).

        In the final design, Phase 5 is primarily *frame-level* and will live
        on the Aether/Spellbook side, building deep DAG blueprints for root
        spells and populating a SpellSystemIndex.

        This placeholder exists so:

        - Phase numbering remains clear and consistent.
        - The crafter has an obvious hook for per-spell participation if we
          decide to expose per-spell helpers later (e.g., dumping local recipe
          metadata into the frame-level assembler).

        Current implementation: no-op.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)
        # No-op for now. Root blueprint assembly is handled by frame-level code.

    # ------------------------------------------------------------------
    # Phase 6 – System-level Validation
    # ------------------------------------------------------------------

    def run_phase_system_validation(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 6 – System-level validation (placeholder).

        Final behavior will be:

        - Use SpellSystemStates + frame-level SpellSystemIndex to validate the
          entire DI graph (cycles, provider coverage, existence rules, etc.).
        - Drive SpellValidity for each lineage (valid/gated/invalid/disabled).

        For now, this method is a stub so callers have an obvious link point
        once the frame-level validator is wired.

        Current implementation: no-op.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)
        # No-op for now; real system-level validation is frame/Aether owned.


    # ------------------------------------------------------------------
    # Phase 7 – Change-control / Component-of Index
    # ------------------------------------------------------------------

    def run_phase_change_control(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 7 – Change-control / component-of index (placeholder).

        Final behavior (AI/Dynamic modes) will be:

        - Build the component-of index mapping `spell_id -> root spell_ids`.
        - Maintain dirty spell/root sets when mutations or contract changes
          occur.
        - Provide the hooks that `Meld` uses to reject dirty roots until
          revalidation completes.

        This crafter may expose per-spell helpers for Phase 7, but the main
        logic will live on the frame-level DevOps / SpellSystemStates owner.

        Current implementation: no-op.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)
        # No-op for now; change-control lives at the frame/DevOps layer.


    # ------------------------------------------------------------------
    # Convenience – run all phases
    # ------------------------------------------------------------------

    def run_all_phases(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Convenience helper to run all phases in sequence for this spell.

        This is typically invoked via :meth:`Spell.run_all_phases` (a facade)
        and is intended for batch compilation / `meld()` cycles.

        Execution order:
            1. Requirements (Phase 1)
            2. Symbolic graph (Phase 2)
            3. Local frame / DAG (Phase 3)
            4. Validation (Phase 4)

        Returns:
            None. The crafter retains all intermediate artifacts until
            :meth:`cleanup` is called. The owning Spell only needs to hold the
            final DAG and dependency spell_ids once Phase 3 is fully implemented.
        """
        self.run_phase_requirements(cancel_event=cancel_event)
        self.run_phase_symbolic_graph(cancel_event=cancel_event)
        self.run_phase_local_frame(cancel_event=cancel_event)
        self.run_phase_validation(cancel_event=cancel_event)
        self.run_phase_root_blueprints(cancel_event=cancel_event)
        self.run_phase_system_validation(cancel_event=cancel_event)
        self.run_phase_change_control(cancel_event=cancel_event)
