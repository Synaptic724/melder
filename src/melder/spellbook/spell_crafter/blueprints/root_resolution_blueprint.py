import threading
from typing import List, Optional, Sequence

from mypy_extensions import mypyc_attr

# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.dag.dag_index import DagIndex, PathRegistry, SocketRef
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
@mypyc_attr(native_class=True)
class RootResolutionBlueprint(Cleanable):
    """
    Phase 5 rooted deep-DAG artifact for one spell.

    This blueprint is the handoff object between structural spell compilation
    and the later system/planning phases. It does not discover dependencies or
    validate policy by itself; instead, it packages the rooted DAG, stable
    execution order, and socket-targeting metadata that later components use
    for system validation, change-control/component-of wiring, and Phase 8-10
    planning/override targeting.

    Contract:
        - `root_spell_id` is the versioned identity of the root spell at
          blueprint-build time.
        - `root_lineage_id` is optional lineage metadata for DevOps/change-
          control use; graph semantics remain version-id-based.
        - The blueprint owns its DAG, socket reference collection, and
          targeting index.
        - Consumers should treat exposed list/index data as read-only, even
          when accessors return copies.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_root_spell_id",
        "_root_lineage_id",
        "_dag",
        "_ordered_node_ids",
        "_socket_refs",
        "_dag_index",
        "_dag_index_build_lock",
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
        """
        Initialize a rooted deep-DAG blueprint.

        Args:
            root_spell_id:
                Versioned spell id for the root node this blueprint represents.
            root_lineage_id:
                Optional lineage id for DevOps/change-control consumers.
            dag:
                Owned deep DAG for the root spell's reachable dependency
                closure.
            ordered_node_ids:
                Optional precomputed topological order. Dependencies should
                appear before the root.
            socket_refs:
                Optional prebuilt socket-reference collection for targeting.
            dag_index:
                Optional prebuilt targeting index. When omitted, a fresh empty
                `DagIndex` is allocated.

        Contract:
            - `root_spell_id` and `dag` are required.
            - Sequence inputs are copied into blueprint-owned lists.
            - The blueprint always owns a non-None `DagIndex`.
        """
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
        self._dag_index_build_lock: threading.Lock = threading.Lock()


    # ------------------------------------------------------------------ #
    # Cleanup                                                            #
    # ------------------------------------------------------------------ #

    def cleanup(self) -> None:
        """
        Deterministically tear down the blueprint and its heavy children.

        Behaviour:
            * Idempotent - safe to call multiple times.
            * Cleans up the DAG and index if present.
            * Drops references to node ids and socket refs to help GC.

        Contract:
            Cleanup releases only blueprint-owned artifacts. It does not mutate
            the spell/runtime payload objects stored inside the DAG.
        """
        if self._cleaned:
            return

        self._cleaned = True

        if self._dag is not None:
            self._dag.cleanup()
        if self._dag_index is not None:
            self._dag_index.cleanup()

        self._socket_refs.clear()
        self._ordered_node_ids.clear()

        del self._dag_index_build_lock
        del self._ordered_node_ids
        del self._dag_index
        del self._socket_refs
        del self._dag
        del self._root_spell_id
        del self._root_lineage_id


    # ------------------------------------------------------------------ #
    # Properties                                                         #
    # ------------------------------------------------------------------ #

    @property
    def root_spell_id(self) -> str:
        """
        Return the versioned root spell id for this blueprint.
        """
        self.check_cleaned()
        return self._root_spell_id

    @property
    def root_lineage_id(self) -> Optional[str]:
        """
        Return the optional lineage id for the root spell.

        This value is metadata for DevOps/change-control consumers; execution
        and targeting are still key off `root_spell_id`.
        """
        self.check_cleaned()
        return self._root_lineage_id

    @property
    def dag(self) -> DirectedAcyclicWorkGraph:
        """
        Return the owned deep DAG for this root.

        The DAG nodes are keyed by spell version id and represent the full
        reachable dependency closure rooted at `root_spell_id`.
        """
        self.check_cleaned()
        return self._dag

    @property
    def ordered_node_ids(self) -> List[str]:
        """
        Return the stable topological order for this rooted DAG.

        Contract:
            Returns a copy of the stored order so callers cannot mutate the
            blueprint's internal list. Dependencies appear before the root.
        """
        self.check_cleaned()
        return list(self._ordered_node_ids)

    @property
    def socket_refs(self) -> List[SocketRef]:
        """
        Return all socket references participating in this rooted DAG.

        Each socket ref carries the root-relative path information later used
        for override targeting, diagnostics, and patch-map construction. The
        returned list is a copy.
        """
        self.check_cleaned()
        return list(self._socket_refs)

    @property
    def dag_index(self) -> DagIndex:
        """
        Return the targeting index built over `socket_refs`.

        Note:
            The index maps are built lazily. Call ensure_dag_index_built()
            before using the index for targeting-heavy runtime work.
        """
        self.check_cleaned()
        return self._dag_index

    @property
    def path_registry(self) -> PathRegistry:
        """
        Return the PathRegistry that interns root-relative parameter paths for
        this blueprint.
        """
        self.check_cleaned()
        return self._dag_index.path_registry

    # ------------------------------------------------------------------ #
    # Mutators used by the Phase 5 frame compiler                        #
    # ------------------------------------------------------------------ #

    def add_socket_ref(self, socket: SocketRef) -> None:
        """
        Append a single socket reference and index it.

        Contract:
            - SocketRef param_path_id must belong to this blueprint's registry.
            - If the DagIndex is already built, the new socket is inserted into
              the live index immediately.
        """
        self.check_cleaned()
        if socket is None:
            raise ValueError("socket must not be None.")
        self._socket_refs.append(socket)
        if self._dag_index is not None and self._dag_index.is_built:
            self._dag_index.add_socket(socket)

    def ensure_dag_index_built(self) -> None:
        """
        Ensure the DagIndex maps are populated for override targeting.

        Contract:
            - Idempotent and thread-safe.
            - Uses socket_refs as the source of truth.
        """
        self.check_cleaned()
        if self._dag_index is None:
            self._dag_index = DagIndex()
        if self._dag_index.is_built:
            return
        if self._dag_index_build_lock is None:
            self._dag_index_build_lock = threading.Lock()
        with self._dag_index_build_lock:
            if self._dag_index.is_built:
                return
            sockets = self._socket_refs or []
            self._dag_index.rebuild(sockets)

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
