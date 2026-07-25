import threading
from typing import List, Optional, ClassVar



# Melder Imports
from melder.aether.spellbook.spell_compiler.symbolic_graph.spell_symbolic_dependency import (
    SpellSymbolicDependency,
)
from melder.utilities.general_base.cleanable import Cleanable

class SpellSymbolicGraph(Cleanable):
    """
    Phase 2 **per-spell symbolic graph**.

    This represents a spell's constructor sockets as a *set of edges* with no
    concrete spell IDs yet. Think of it as a mid-level, versioned description
    of “what this spell wants”, without binding to specific implementations.

    Identity
    --------
    "spell_id" is again the spell's **version ID**:

        "spell.spell_index.selected_spell_id"

    The graph is always scoped per spell version; if a spell mutates and a new
    version is created, a new graph should be built.

    Contents
    --------
    * "dependencies" – list of: class:`SpellSymbolicDependency` objects,
      one per constructor socket represented in the symbolic graph.

    What it does *not* contain
    --------------------------
    * No DAG / topo ordering.
    * No existence policy decisions.
    * No concrete spell_ids for dependencies.
    * No runtime execution logic.

    Those concerns belong to Phase 3 (local frame / DAG) and Phase 4 (validation).

    Registration:
        MELDER KERNEL - guarded. A per-spell Phase-2 artifact; not user-bindable.

    Subsystem Context:
        The aggregate of the `symbolic_graph` package: it owns the list of
        `SpellSymbolicDependency` edges. Built from the Phase-1 `SpellRequirements`
        and consumed by Phase-3 DAG construction.

    System Context:
        Phase 2 (symbolic graph) of the conjure pipeline, scoped per spell version
        (`selected_spell_id`). Symbolic only - it binds to no implementations and
        never touches the live object world; that is Phase 3/4's job.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Phase-2 per-spell symbolic graph: the set of SpellSymbolicDependency "
        "edges (one per constructor socket) for one spell version. No DAG ordering, no concrete "
        "spell ids, no existence policy."
    )
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_spell_id",
        "_dependencies",
    ]

    def __init__(
            self,
            *,
            spell_id: str,
            dependencies: Optional[List['SpellSymbolicDependency']] = None,
    ) -> None:
        """
        Initialize a symbolic graph for one spell version.

        Contract:
            - `spell_id` is required.
            - Stores the dependency edge list by reference and treats it as
              graph-owned after construction.
            - Starts with an empty dependency list when none is supplied.
        """
        super().__init__()

        if not spell_id:
            raise ValueError("spell_id must be a non-empty string.")

        self._lock: threading.RLock = threading.RLock()
        # Same story: stored as _spell_id, semantics = version id.
        self._spell_id: str = spell_id
        self._dependencies: List['SpellSymbolicDependency'] = dependencies or []

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """
        Deterministically tear down this symbolic graph and all its edges.

        This cascades cleanup into all: class:`SpellSymbolicDependency`
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
            self._cleaned = True

            del self._dependencies
            del self._spell_id
        del self._lock

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def spell_id(self) -> str:
        """
        Versioned identity of the owning spell (SpellIndex.selected_spell_id).
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
            * PLAIN

        Returns:
            list[SpellSymbolicDependency]: A shallow copy of the underlying
            dependency list. Mutating the returned list does not affect the
            internal state.
        """
        self.check_cleaned()
        return list(self._dependencies)

