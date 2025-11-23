from __future__ import annotations

import threading
from typing import Any, Optional, List

from melder.spellbook.spell_crafter.symbolic_graph.spell_symbolic_dependency import SpellSymbolicDependency
from melder.spellbook.spell_crafter.symbolic_graph.spell_symbolic_graph import SpellSymbolicGraph
from melder.utilities.general_base.cleanable import Cleanable
from melder.spellbook.spell import Spell
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_requirements_finder import (
    SpellRequirementsFinder,
)
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_requirements import (
    SpellRequirements,
)
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)

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

    def __init__(self, spell: Spell) -> None:
        """
        Create a new SpellCrafter for the given :class:`Spell`.

        Args:
            spell:
                The owning Spell. The crafter treats it as read-only, except when
                later phases push the final DAG back into the Spell via internal
                methods like ``_add_build_details`` (not implemented here yet).
        """
        Cleanable.__init__(self)

        if spell is None:
            raise ValueError("spell must not be None.")

        self._lock: threading.RLock = threading.RLock()
        self._spell: Spell = spell

        self._requirements: Optional[SpellRequirements] = None
        self._symbolic_graph: Optional[SpellSymbolicGraph] = None
        self._resolution_frame: Any = None
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
            * Cleans up the resolution frame if it exposes ``cleanup()``.
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

            if self._resolution_frame is not None and hasattr(self._resolution_frame, "cleanup"):
                try:
                    self._resolution_frame.cleanup()
                except Exception:
                    pass

            self._requirements = None
            self._symbolic_graph = None
            self._resolution_frame = None
            self._validation_result = None
            self._validated = False
            self._is_broken = False
            self._spell = None
            self._cleaned = True

        self._lock = None

    # ------------------------------------------------------------------
    # Core properties
    # ------------------------------------------------------------------

    @property
    def spell(self) -> Spell:
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
    def resolution_frame(self) -> Any:
        """
        Phase 3 local resolution frame / DAG (placeholder).

        In the full implementation, this will be a structured object that
        encodes topo order and resolution actions.
        """
        self.check_cleaned()
        return self._resolution_frame

    @property
    def validation_result(self) -> Any:
        """
        Phase 4 validation result artifact, if any.

        Current placeholder is None.
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

        requirements = self._requirements or self.run_phase_requirements(cancel_event=cancel_event)

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
    # Phase 3 – Local Frame / DAG (placeholder)
    # ------------------------------------------------------------------

    def run_phase_local_frame(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> Any:
        """
        Phase 3 – Local Resolution Frame / DAG (placeholder).

        Future responsibilities:
            * Interpret the symbolic graph in the context of the Spellbook.
            * Map annotations / spellframes to actual spell_ids (version IDs).
            * Build a concrete resolution DAG or "ResolutionFrame" structure,
              including topo order and actions.
            * Push the final DAG back into the owning Spell via
              ``spell._add_build_details(dag, dependency_ids)``.

        Current behavior:
            * Honors cancellation.
            * Returns ``self._resolution_frame`` (likely None).
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)

        return self._resolution_frame

    # ------------------------------------------------------------------
    # Phase 4 – Validation (placeholder)
    # ------------------------------------------------------------------

    def run_phase_validation(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> Any:
        """
        Phase 4 – Validation (placeholder).

        Future responsibilities:
            * Validate the resolution frame and symbolic graph against:
                - existence / lifecycle policies
                - cross-conduit boundaries
                - configuration flags
            * Populate ``self._validation_result`` with a rich result object.
            * Set ``self._validated`` and ``self._is_broken`` appropriately.

        Current behavior:
            * Honors cancellation.
            * Marks the spell as validated and not broken.
            * Returns ``self._validation_result`` (currently None).
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)

        self._validated = True
        self._is_broken = False
        return self._validation_result

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
