from __future__ import annotations

from threading import RLock
from typing import Any, Dict, Optional

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpellbook, ISpellIndex
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_requirements import (
    SpellRequirements,
)
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.spell_requirements_finder import (
    SpellRequirementsFinder,
)
from melder.spellbook.spell_crafter.spellbook_scanner import SpellbookScanner


class SpellCrafter(Cleanable):
    """
    Internal

    Per-spell **compiler / resolution pipeline orchestrator**.

    This sits between:

        * The raw :class:`Spell` object (identity, metadata, hooks, etc.).
        * The multi-phase resolution / Meld pipeline (requirements, graphs,
          resolution frames, validation, DAG creation).

    Responsibilities (current):

        - Phase 1: drive :class:`SpellRequirementsFinder` for a single spell.
        - Own the Phase 1–4 artifacts for that spell:
            * requirements
            * symbolic graph (placeholder)
            * local resolution frame / DAG (placeholder)
            * validation result + flags
        - Provide a batch helper to run Phase 1 across an entire Spellbook,
          using :class:`SpellbookScanner`.

    Design:

        * The Spell owns identity + final DAG.
        * SpellCrafter owns the temporary compiler artifacts.
        * When you're done with a resolution cycle, `cleanup()` can be used to
          drop these artifacts and leave only the final DAG on the Spell.
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

    def __init__(self, spell: Any) -> None:
        """
        Create a new SpellCrafter for a specific spell.

        Args:
            spell:
                The Spell instance to operate on. This is expected to be an
                instance of :class:`melder.spellbook.spell.Spell`, but is
                typed as ``Any`` here to avoid import cycles.

        Notes:
            - The crafter never takes ownership of the spell's lifecycle.
            - Cleanup of this crafter does **not** cleanup the spell itself.
        """
        Cleanable.__init__(self)

        if spell is None:
            raise ValueError("spell must not be None.")

        self._lock: RLock = RLock()
        self._spell: Any = spell

        # Phase artifacts
        self._requirements: Optional[SpellRequirements] = None
        self._symbolic_graph: Any = None
        self._resolution_frame: Any = None
        self._validation_result: Any = None
        self._validated: bool = False
        self._is_broken: bool = False

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """
        Deterministically tear down this crafter.

        This:
            - Cleans up and drops all Phase 1–4 artifacts.
            - Drops the reference to the spell.
            - Marks the crafter as cleaned.

        It does **not** modify the spell's own state (DAG, metadata, etc.).
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            # Drop requirements + children.
            if self._requirements is not None:
                try:
                    self._requirements.cleanup()
                except Exception:
                    # Never let cleanup explosions propagate.
                    pass

            self._requirements = None
            self._symbolic_graph = None
            self._resolution_frame = None
            self._validation_result = None
            self._validated = False
            self._is_broken = False
            self._spell = None

            self._cleaned = True

    # ------------------------------------------------------------------
    # Core accessors
    # ------------------------------------------------------------------

    @property
    def spell(self) -> Any:
        """
        The underlying Spell object being crafted.

        Exposed as ``Any`` to keep this class decoupled from the concrete
        Spell implementation at import time.
        """
        self.check_cleaned()
        return self._spell

    @property
    def requirements(self) -> Optional[SpellRequirements]:
        """
        Phase 1 artifact for this spell, if it has been computed.
        """
        self.check_cleaned()
        return self._requirements

    @property
    def symbolic_graph(self) -> Any:
        """
        Phase 2 artifact (placeholder) – per-spell symbolic graph.
        """
        self.check_cleaned()
        return self._symbolic_graph

    @property
    def resolution_frame(self) -> Any:
        """
        Phase 3 artifact (placeholder) – concrete per-spell resolution frame / DAG.
        """
        self.check_cleaned()
        return self._resolution_frame

    @property
    def validation_result(self) -> Any:
        """
        Phase 4 artifact (placeholder) – validation result/details.
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
        True if validation classified this spell as broken / unsafe.
        """
        self.check_cleaned()
        return self._is_broken

    # ------------------------------------------------------------------
    # Phase 1 – Requirements Extraction
    # ------------------------------------------------------------------

    def run_phase_requirements(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> SpellRequirements:
        """
        Phase 1 – Requirements Extraction for **this** spell.

        Responsibilities:
            - Inspect the spell’s constructor/signature and metadata.
            - Determine parameter-level DI requirements.
            - Capture existence, spellframe, and binding info.
            - Store a :class:`SpellRequirements` instance in this crafter.

        Returns:
            SpellRequirements: requirements artifact for this spell.
        """
        self.check_cleaned()

        if self._requirements is not None:
            return self._requirements

        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        spell = self._spell
        if spell is None:
            raise RuntimeError("SpellCrafter has been cleaned or has no spell.")

        finder = SpellRequirementsFinder(spell)
        requirements = finder.build_requirements(cancel_event=cancel_event)
        # Store for later phases
        self._requirements = requirements
        return requirements

    # ------------------------------------------------------------------
    # Phase 2 – Symbolic Graph (placeholder)
    # ------------------------------------------------------------------

    def run_phase_symbolic_graph(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> Any:
        """
        Phase 2 – Symbolic Graph Construction.

        In the full implementation, this will:

            - Use Phase 1 requirements to construct a per-spell symbolic graph.
            - Represent DI relationships as nodes/edges, without binding to
              concrete creations yet.

        For now, this is a **no-op placeholder** that:

            - Honours the cancellation event.
            - Returns the current ``_symbolic_graph`` (likely ``None``).
        """
        self.check_cleaned()

        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        # Placeholder – later this will build and assign a real symbolic graph.
        return self._symbolic_graph

    # ------------------------------------------------------------------
    # Phase 3 – Local Resolution Frame / DAG (placeholder)
    # ------------------------------------------------------------------

    def run_phase_local_frame(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> Any:
        """
        Phase 3 – Local Resolution Frame / DAG.

        In the full implementation, this will:

            - Translate the symbolic graph into a concrete, per-spell
              resolution frame / local DAG.
            - Encode the order and actions required for resolution.
            - Eventually push the final DAG into the Spell via
              ``spell._add_build_details(...)``.

        For now, this is a **no-op placeholder** that:

            - Honours the cancellation event.
            - Returns the current ``_resolution_frame`` (likely ``None``).
        """
        self.check_cleaned()

        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        # Placeholder – later this will build and assign a real resolution frame.
        return self._resolution_frame

    # ------------------------------------------------------------------
    # Phase 4 – Validation (placeholder)
    # ------------------------------------------------------------------

    def run_phase_validation(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> Any:
        """
        Phase 4 – Validation.

        In the full implementation, this will:

            - Validate the resolution frame and requirements.
            - Populate :attr:`_validation_result`.
            - Set :attr:`_validated` and :attr:`_is_broken` flags.

        For now, this:

            - Honours the cancellation event.
            - Marks the spell as validated and **not broken** by default.
            - Leaves :attr:`_validation_result` as-is for future expansion.
        """
        self.check_cleaned()

        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

        self._validated = True
        self._is_broken = False
        return self._validation_result

    # ------------------------------------------------------------------
    # Batch Phase 1 – Spellbook-wide helper
    # ------------------------------------------------------------------

    @classmethod
    def run_phase1_for_spellbook(
            cls,
            spellbook: ISpellbook,
            cancel_event: Optional[CancellationEvent] = None,
            include_contracted: bool = False,
    ) -> Dict[ISpellIndex, SpellRequirements]:
        """
        Run Phase 1 (requirements extraction) for every spell in a Spellbook.

        This is a convenience entrypoint for the Resolution / Meld pipeline.

        Args:
            spellbook:
                The Spellbook whose spells should be processed.
            cancel_event:
                Optional cancellation token. If set, this method will abort
                cooperatively via ``cancel_event.throw_if_set()``.
            include_contracted:
                If True, includes contracted spells from other spellbooks;
                if False, only processes local spells.

        Returns:
            Dict[SpellIndex, SpellRequirements]:
                Mapping from SpellIndex to the SpellRequirements instance for
                each processed spell.
        """
        if spellbook is None:
            raise ValueError("spellbook must not be None.")

        scanner = SpellbookScanner(spellbook)
        try:
            results: Dict[ISpellIndex, SpellRequirements] = {}

            iterator = (
                scanner.iter_all_spells()
                if include_contracted
                else scanner.iter_local_spells()
            )

            for index, spell in iterator:
                if cancel_event is not None and cancel_event.is_set:
                    cancel_event.throw_if_set()

                crafter = cls(spell)
                requirements = crafter.run_phase_requirements(cancel_event=cancel_event)
                results[index] = requirements

            return results
        finally:
            # Scanner is purely an iteration helper; we can safely dispose it
            # once the batch operation is complete.
            scanner.cleanup()
