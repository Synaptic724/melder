from __future__ import annotations

import threading
from typing import Any, Optional, List, Dict

from melder.spellbook.spell_crafter.dag.meld_dag import DirectedAcyclicWorkGraph
# Melder Imports
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
from melder.utilities.interfaces.interfaces import ISpell
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


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
        type / SpellMap) but does not bind to concrete spell IDs.

        Current strategy
        ----------------
        * Walk all parameter requirements.
        * For each parameter with a DI shape of:
            - SINGLE_BY_ANNOTATION
            - COLLECTION_BY_ANNOTATION
            - SPELLMAP_DEFAULT
          construct a :class:`SpellSymbolicDependency` and add it to the graph.

        Returns:
            SpellSymbolicGraph: The per-spell symbolic graph instance.
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
            if di_shape not in (
                    ParameterDIShape.SINGLE_BY_ANNOTATION,
                    ParameterDIShape.COLLECTION_BY_ANNOTATION,
                    ParameterDIShape.SPELLMAP_DEFAULT,
            ):
                # Shapes like IGNORE/PLAIN do not participate in DI edges.
                continue

            if di_shape is ParameterDIShape.SPELLMAP_DEFAULT:
                target_annotation = None
                is_collection = False
                spellmap_default = param.spellmap_default
            elif di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION:
                target_annotation = param.annotation
                is_collection = False
                spellmap_default = None
            else:  # COLLECTION_BY_ANNOTATION
                target_annotation = param.collection_element_annotation
                is_collection = True
                spellmap_default = None

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

    def run_phase_local_frame(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> SpellResolutionFrame:
        """
        Phase 3 – Local Resolution Frame / DAG.

        Responsibilities (current increment):

            * Interpret the symbolic graph in the context of the owning
              :class:`Spellbook` (via :class:`SpellbookScanner`).
            * Map annotations / SpellMaps to **concrete** dependency spell_ids.
            * Build a minimal concrete resolution DAG using
              :class:`DirectedAcyclicWorkGraph`, where each dependency spell
              points into the root spell node.
            * Push the DAG + dependency ids back into the owning :class:`Spell`
              via :meth:`Spell._add_build_details`.
            * Expose a lightweight :class:`SpellResolutionFrame` summary that
              records the spell id and the topological order of the DAG nodes.

        This method is idempotent; repeated calls reuse the same frame.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)

        if self._resolution_frame is not None:
            return self._resolution_frame

        with self._lock:
            # Double-checked locking in case another thread raced us.
            if self._resolution_frame is not None:
                return self._resolution_frame

            # Ensure Phase 1 + 2 have run.
            self._requirements = self._requirements or self.run_phase_requirements(
                cancel_event=cancel_event
            )
            graph = self._symbolic_graph or self.run_phase_symbolic_graph(
                cancel_event=cancel_event
            )

            # If the spell has no DI parameters at all (or no spellbook), we
            # still build a trivial DAG that only contains the root node.
            spellbook = self._spell._spellbook
            root_id = self._spell.spell_index.current

            if spellbook is None:
                dag = DirectedAcyclicWorkGraph()
                dag.add_node(root_id, payload=self._spell)
                ordered_ids = dag.collect_dependency_ids()
                frame = SpellResolutionFrame(
                    spell_id=root_id,
                    ordered_node_ids=ordered_ids,
                )
                self._resolution_frame = frame
                self._spell._add_build_details(
                    dag=dag,
                    dependencies=[],
                )
                return frame

            scanner = SpellbookScanner(spellbook)

            dag = DirectedAcyclicWorkGraph()
            dag.add_node(root_id, payload=self._spell)

            dependency_spell_ids: List[str] = []

            # Build DI edges from the symbolic graph.
            for dep in graph.dependencies:
                self._throw_if_cancelled(cancel_event)

                di_shape = dep.di_shape

                if di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION:
                    resolved = self._resolve_single_by_annotation(scanner, dep)
                elif di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION:
                    resolved = self._resolve_collection_by_annotation(scanner, dep)
                elif di_shape is ParameterDIShape.SPELLMAP_DEFAULT:
                    resolved = self._resolve_spellmap_default(scanner, dep)
                else:
                    # Should not happen given Phase 2 filtering, but we keep
                    # this guard for robustness.
                    continue

                # For SINGLE + SPELLMAP_DEFAULT we expect exactly one entry;
                # for COLLECTION we may have many or zero.
                for spell_index, spell_obj in resolved.items():
                    # SpellIndex exposes the current version id we want to
                    # encode into the DAG.
                    dep_spell_id: str = spell_index.current

                    dependency_spell_ids.append(dep_spell_id)
                    # Nodes are created on-demand; add_dependency will ensure
                    # both parent and child nodes exist.
                    dag.add_node(dep_spell_id, payload=spell_obj)
                    dag.add_dependency(parent_key=dep_spell_id, child_key=root_id)

            # Deduplicate dependency ids while preserving order.
            if dependency_spell_ids:
                seen: set[str] = set()
                unique_dependency_ids: List[str] = []
                for dep_id in dependency_spell_ids:
                    if dep_id in seen:
                        continue
                    seen.add(dep_id)
                    unique_dependency_ids.append(dep_id)
            else:
                unique_dependency_ids = []

            ordered_ids = dag.collect_dependency_ids()
            frame = SpellResolutionFrame(
                spell_id=root_id,
                ordered_node_ids=ordered_ids,
            )
            self._resolution_frame = frame

            # Push the concrete DAG + dependency ids into the owning Spell.
            self._spell._add_build_details(
                dag=dag,
                dependencies=unique_dependency_ids,
            )

            return frame

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
