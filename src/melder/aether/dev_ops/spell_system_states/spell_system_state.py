from __future__ import annotations
import threading
from typing import Iterable, Optional, Set
# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.data_structures.concurrent_set import ConcurrentSet


class SpellSystemState(Cleanable):
    """
    System-level state for a single spell lineage.

    This is intentionally *lightweight* and purely about topology + dirtiness:

    - `spell_index_id`:
        Lineage identifier (ULID from SpellIndex.id).

    - `current_spell_id`:
        The currently promoted version id for this lineage
        (e.g., SpellIndex.current; typically a SHA).

    - `direct_dependencies`:
        Set of dependency ids for this lineage.
        These ids are deliberately generic "spell ids" so the caller can decide
        whether they are version ids or lineage ids. The manager is agnostic.

    - `direct_dependents`:
        Set of ids for lineages that depend on this lineage. This is the
        reverse edge view used for "what breaks if this changes?".

    - `dirty` / `dirty_reason` / `transitively_dirty`:
        Flags used by higher-level orchestration (DevOpsManager / revalidation)
        to know what needs attention.

    - `last_validated_at`:
        Optional timestamp (float seconds) of last successful structural
        validation. Caller is responsible for populating it.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_spell_index_id",
        "_current_spell_id",
        "_direct_dependencies",
        "_direct_dependents",
        "_dirty",
        "_dirty_reason",
        "_transitively_dirty",
        "_last_validated_at",
    ]

    def __init__(self, spell_index_id: str, current_spell_id: str) -> None:
        super().__init__()

        if not spell_index_id:
            raise ValueError("spell_index_id cannot be empty")
        if not current_spell_id:
            raise ValueError("current_spell_id cannot be empty")

        self._lock: threading.RLock = threading.RLock()
        self._spell_index_id: str = spell_index_id
        self._current_spell_id: str = current_spell_id

        # Concurrent topology sets
        self._direct_dependencies: ConcurrentSet = ConcurrentSet()
        self._direct_dependents: ConcurrentSet = ConcurrentSet()

        self._dirty: bool = True
        self._dirty_reason: Optional[str] = "new_lineage"
        self._transitively_dirty: bool = False
        self._last_validated_at: Optional[float] = None

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def cleanup(self) -> None:
        """
        Explicitly dispose references and mark this state as cleaned.

        Follows the Melder cleanup pattern:
        - idempotent
        - guarded by an internal lock
        - null-out references to assist GC
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True

            if self._direct_dependencies is not None:
                self._direct_dependencies.cleanup()
                self._direct_dependencies = None

            if self._direct_dependents is not None:
                self._direct_dependents.cleanup()
                self._direct_dependents = None

            self._dirty = False
            self._dirty_reason = None
            self._transitively_dirty = False
            self._last_validated_at = None

            self._spell_index_id = None
            self._current_spell_id = None

        # Drop lock last
        self._lock = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def spell_index_id(self) -> str:
        self.check_cleaned()
        return self._spell_index_id

    @property
    def current_spell_id(self) -> str:
        self.check_cleaned()
        return self._current_spell_id

    @property
    def direct_dependencies(self) -> Set[str]:
        """
        Snapshot of direct dependencies for this lineage.

        Returns a plain set[str] copy so callers cannot mutate internal state.
        """
        self.check_cleaned()
        with self._lock:
            if self._direct_dependencies is None:
                return set()
            return set(self._direct_dependencies)

    @property
    def direct_dependents(self) -> Set[str]:
        """
        Snapshot of direct dependents for this lineage.

        Returns a plain set[str] copy so callers cannot mutate internal state.
        """
        self.check_cleaned()
        with self._lock:
            if self._direct_dependents is None:
                return set()
            return set(self._direct_dependents)

    @property
    def dirty(self) -> bool:
        self.check_cleaned()
        return self._dirty

    @property
    def dirty_reason(self) -> Optional[str]:
        self.check_cleaned()
        return self._dirty_reason

    @property
    def transitively_dirty(self) -> bool:
        self.check_cleaned()
        return self._transitively_dirty

    @property
    def last_validated_at(self) -> Optional[float]:
        self.check_cleaned()
        return self._last_validated_at

    # ------------------------------------------------------------------
    # Mutation helpers (used by manager / DevOps layer)
    # ------------------------------------------------------------------
    def update_current_spell_id(self, spell_id: str) -> None:
        """
        Update the currently promoted version id for this lineage.

        Caller is responsible for keeping the manager's spell-id index in sync.
        """
        self.check_cleaned()
        if not spell_id:
            raise ValueError("spell_id cannot be empty")

        with self._lock:
            self._current_spell_id = spell_id

    def attach_dependencies(self, dependency_ids: Iterable[str]) -> None:
        """
        Replace the direct-dependency set for this lineage.

        The manager is responsible for keeping reverse edges up to date.
        """
        self.check_cleaned()

        deps = {d for d in dependency_ids if d}
        with self._lock:
            # Rebuild as a fresh concurrent set to avoid stale contents.
            self._direct_dependencies = ConcurrentSet(deps)

    def add_dependent(self, index_id: str) -> None:
        self.check_cleaned()
        if not index_id:
            return
        with self._lock:
            if self._direct_dependents is not None:
                self._direct_dependents.add(index_id)

    def remove_dependent(self, index_id: str) -> None:
        self.check_cleaned()
        if not index_id:
            return
        with self._lock:
            if self._direct_dependents is not None:
                self._direct_dependents.discard(index_id)

    def mark_structural_change(self, reason: str = "structure_changed") -> None:
        self.check_cleaned()
        if not reason:
            reason = "structure_changed"
        with self._lock:
            self._dirty = True
            self._dirty_reason = reason
            self._transitively_dirty = False

    def mark_dependency_change(self, reason: str = "dependencies_changed") -> None:
        self.check_cleaned()
        if not reason:
            reason = "dependencies_changed"
        with self._lock:
            self._dirty = True
            self._dirty_reason = reason
            # Manager decides if this becomes transitively dirty.

    def mark_transitively_dirty(self, reason: str = "dependency_changed") -> None:
        self.check_cleaned()
        if not reason:
            reason = "dependency_changed"
        with self._lock:
            self._dirty = True
            self._transitively_dirty = True
            if self._dirty_reason is None:
                self._dirty_reason = reason

    def clear_dirty(self, last_validated_at: Optional[float]) -> None:
        """
        Mark this lineage as clean after successful validation.
        """
        self.check_cleaned()
        with self._lock:
            self._dirty = False
            self._transitively_dirty = False
            self._dirty_reason = None
            self._last_validated_at = last_validated_at
