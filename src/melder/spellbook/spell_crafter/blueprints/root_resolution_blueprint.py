from typing import Iterable, List, Optional, Sequence
# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.dag.dag_index import DagIndex, SocketRef
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class RootResolutionBlueprint(Cleanable):
    """
    Internal

    Deep DAG blueprint for a single entrypoint spell (Phase 5 artifact).

    This object is intentionally dumb:
        * It does not perform discovery or validation.
        * It just packages:
            - the deep DAG (all reachable version-ids),
            - a stable execution order (dependencies before root),
            - socket metadata for targeting (SocketRef + DagIndex).

    Identity model:
        root_spell_id:
            Version id of the root spell (spell.spell_index.current at compile time).

        root_lineage_id:
            Lineage ULID of the root spell (spell.spell_index.id). Optional metadata
            for DevOps / change-control; graph logic is always version-id based.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_root_spell_id",
        "_root_lineage_id",
        "_dag",
        "_ordered_node_ids",
        "_socket_refs",
        "_dag_index",
    ]

    def __init__(
            self,
            root_spell_id: str,
            root_lineage_id: Optional[str],
            dag: DirectedAcyclicWorkGraph,
            ordered_node_ids: Optional[Sequence[str]] = None,
            socket_refs: Optional[Sequence[SocketRef]] = None,
            dag_index: Optional[DagIndex] = None,
    ) -> None:
        super().__init__()

        if root_spell_id is None:
            raise ValueError("root_spell_id must not be None.")
        if dag is None:
            raise ValueError("dag must not be None.")

        self._root_spell_id: str = root_spell_id
        self._root_lineage_id: Optional[str] = root_lineage_id
        self._dag: DirectedAcyclicWorkGraph = dag

        # Execution order: dependencies first, root last.
        self._ordered_node_ids: List[str] = list(ordered_node_ids) if ordered_node_ids else []

        # Socket metadata (can be populated incrementally by Phase 5 builder).
        self._socket_refs: List[SocketRef] = list(socket_refs) if socket_refs else []

        # Targeting index; always non-None for consumers.
        self._dag_index: DagIndex = dag_index if dag_index is not None else DagIndex()


    # ------------------------------------------------------------------ #
    # Cleanup                                                            #
    # ------------------------------------------------------------------ #

    def cleanup(self) -> None:
        """
        Deterministically tear down the blueprint and its heavy children.

        Behaviour:
            * Idempotent – safe to call multiple times.
            * Cleans up the DAG and index if present.
            * Drops references to node ids and socket refs to help GC.
        """
        if self._cleaned:
            return

        self._cleaned = True

        if self._dag is not None:
            self._dag.cleanup()
            self._dag = None

        if self._dag_index is not None:
            self._dag_index.cleanup()
            self._dag_index = None

        self._ordered_node_ids.clear()
        self._ordered_node_ids = None

        self._socket_refs.clear()
        self._socket_refs = None

        self._root_spell_id = None
        self._root_lineage_id = None


    # ------------------------------------------------------------------ #
    # Properties                                                         #
    # ------------------------------------------------------------------ #

    @property
    def root_spell_id(self) -> str:
        """
        Version id of the entrypoint spell for this blueprint.
        """
        self.check_cleaned()
        return self._root_spell_id

    @property
    def root_lineage_id(self) -> Optional[str]:
        """
        Lineage ULID of the entrypoint spell (SpellIndex.id), if known.
        """
        self.check_cleaned()
        return self._root_lineage_id

    @property
    def dag(self) -> DirectedAcyclicWorkGraph:
        """
        Deep DAG for this root (nodes keyed by spell version id).
        """
        self.check_cleaned()
        return self._dag

    @property
    def ordered_node_ids(self) -> List[str]:
        """
        Topological order for execution: dependencies first, root last.

        Callers should treat this as read-only.
        """
        self.check_cleaned()
        return list(self._ordered_node_ids)

    @property
    def socket_refs(self) -> List[SocketRef]:
        """
        All sockets participating in this deep DAG, with param paths
        from the root (for overrides and diagnostics).
        """
        self.check_cleaned()
        return list(self._socket_refs)

    @property
    def dag_index(self) -> DagIndex:
        """
        Targeting index over `socket_refs` (by path and param name).
        """
        self.check_cleaned()
        return self._dag_index

    # ------------------------------------------------------------------ #
    # Mutators used by the Phase 5 frame compiler                        #
    # ------------------------------------------------------------------ #

    def add_socket_ref(self, socket: SocketRef) -> None:
        """
        Append a single socket reference and index it.
        """
        self.check_cleaned()
        if socket is None:
            raise ValueError("socket must not be None.")
        self._socket_refs.append(socket)
        self._dag_index.add_socket(socket)

    def replace_dag_index(self, index: DagIndex) -> None:
        """
        Replace the underlying DagIndex.

        Normally not needed – Phase 5 can just add sockets via this blueprint.
        Provided for completeness / testing.
        """
        self.check_cleaned()
        if index is None:
            raise ValueError("index must not be None.")
        # Do NOT rebuild sockets here; caller is responsible for consistency.
        self._dag_index = index
