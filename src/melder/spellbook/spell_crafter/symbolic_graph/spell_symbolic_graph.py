import threading
from typing import List, Optional
# Melder Imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SpellSymbolicGraph(Cleanable):
    """
    Phase 2 **per-spell symbolic graph**.

    This represents a spell's constructor sockets as a *set of edges* with no
    concrete spell IDs yet. Think of it as a mid-level, versioned description
    of “what this spell wants”, without binding to specific implementations.

    Identity
    --------
    ``spell_id`` is again the spell's **version ID**:

        ``spell.spell_index.current``

    The graph is always scoped per spell version; if a spell mutates and a new
    version is created, a new graph should be built.

    Contents
    --------
    * ``dependencies`` – list of :class:`SpellSymbolicDependency` objects,
      one per constructor socket represented in the symbolic graph.

    What it does *not* contain
    --------------------------
    * No DAG / topo ordering.
    * No existence policy decisions.
    * No concrete spell_ids for dependencies.
    * No runtime execution logic.

    Those concerns belong to Phase 3 (local frame / DAG) and Phase 4 (validation).
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_spell_id",
        "_dependencies",
    ]

    def __init__(
            self,
            *,
            spell_version_id: str,
            dependencies: Optional[List['SpellSymbolicDependency']] = None,
    ) -> None:
        super().__init__()

        if not spell_version_id:
            raise ValueError("spell_version_id must be a non-empty string.")

        self._lock: threading.RLock = threading.RLock()
        # Same story: stored as _spell_id, semantics = version id.
        self._spell_id: str = spell_version_id
        self._dependencies: List['SpellSymbolicDependency'] = dependencies or []

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """
        Deterministically tear down this symbolic graph and all its edges.

        This cascades cleanup into all :class:`SpellSymbolicDependency`
        instances and clears internal references.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            for dep in self._dependencies:
                try:
                    dep.cleanup()
                except Exception:
                    # Dependency cleanup must never blow up tear-down.
                    pass

            self._dependencies = []
            self._spell_id = None
            self._cleaned = True

        self._lock = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def spell_id(self) -> str:
        """
        Versioned identity of the owning spell (SpellIndex.current).
        """
        self.check_cleaned()
        return self._spell_id

    @property
    def dependencies(self) -> List['SpellSymbolicDependency']:
        """
        All constructor sockets for this spell.

        Each edge corresponds to a parameter represented in Phase 2:

            * SINGLE_BY_ANNOTATION
            * COLLECTION_BY_ANNOTATION
            * SPELLMAP_DEFAULT
            * SPELL_CONTRACT
            * MUTATION_CONTRACT
            * PLAIN

        Returns:
            list[SpellSymbolicDependency]: A shallow copy of the underlying
            dependency list. Mutating the returned list does not affect the
            internal state.
        """
        self.check_cleaned()
        return list(self._dependencies)
