import heapq
from threading import RLock
from typing import Any, Dict, Iterable, List, Optional, Tuple

from mypy_extensions import mypyc_attr
from melder.aether.spellbook.spell_crafter.dag.dag_node import DagNode
from melder.aether.spellbook.spell_crafter.dag.socket_kind import SocketKind
# Melder Imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
@mypyc_attr(native_class=True)
class DirectedAcyclicWorkGraph(Cleanable):
    """
    Internal

    A minimal Directed Acyclic Graph implementation specialized for Melder.

    Responsibilities:

    - Track nodes by key.
    - Express dependencies between nodes (no Edge objects).
    - Compute a topological ordering of nodes.
    - Optionally execute node tasks in topological order.
    - Clean up nodes and break references when no longer needed.

    This DAG is *static* from the perspective of resolution:
      - Build it.
      - Topologically sort it.
      - Use the order to resolve and instantiate objects.
      - Cleanup when finished.

    It is intentionally not a general-purpose runtime workflow engine.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_nodes",
        "_socket_kinds",
    ]
    def __init__(self) -> None:
        """
        Initialize an empty DAG with its own identity and lock.

        Contract:
            - Starts with no nodes or recorded socket-kind metadata.
            - Owns a single re-entrant lock for all structural mutation.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: RLock = RLock()
        self._nodes: Dict[str, DagNode] = {}
        self._socket_kinds: Dict[tuple[DagNode, DagNode], SocketKind] = {}

    # --------------------------------------------------------------------- #
    # Cleanup
    # --------------------------------------------------------------------- #
    def cleanup(self) -> None:
        """
        Cleans up the DAG and all contained nodes.

        - Calls `cleanup()` on every node.
        - Clears internal maps and breaks references.
        - Marks this DAG as cleaned.

        Idempotent.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            for node in list(self._nodes.values()):
                try:
                    node.cleanup()
                except Exception:
                    # Cleanup should never explode the caller; failures here
                    # just mean some references may linger a bit longer.
                    pass

            self._nodes.clear()
            self._nodes = {}
            self._cleaned = True


    # --------------------------------------------------------------------- #
    # Core API
    # --------------------------------------------------------------------- #
    @property
    def id(self) -> str:
        """
        Returns the unique identifier for this DAG instance.
        """
        return self._id

    @property
    def nodes(self) -> Dict[str, DagNode]:
        """
        Returns a read-only view of the node map.

        NOTE: Consumers should not mutate the returned dict directly.
        """
        return self._nodes

    def add_node(self, key: str, payload: Any | None = None) -> DagNode:
        """
        Adds (or retrieves) a node with the given key.

        If a node with the same key already exists, it is returned and the
        payload is updated only if `payload` is not None.

        Args:
            key: Node identifier (e.g., spell id).
            payload: Optional payload for the node.

        Returns:
            DagNode: The created or existing node.
        """
        self.check_cleaned()
        if not key:
            raise ValueError("Node key cannot be empty.")

        with self._lock:
            node = self._nodes.get(key)
            if node is not None:
                if payload is not None:
                    node.payload = payload
                return node

            node = DagNode(key=key, payload=payload)
            self._nodes[key] = node
            return node

    def add_nodes_bulk(self, keys: Iterable[str]) -> None:
        """
        Add multiple nodes under a single lock.

        Contract:
            - Skips existing nodes without mutating their payloads.
            - Raises ValueError if any key is empty.
        """
        self.check_cleaned()
        with self._lock:
            for key in keys:
                if not key:
                    raise ValueError("Node key cannot be empty.")
                if key in self._nodes:
                    continue
                self._nodes[key] = DagNode(key=key, payload=None)

    def get_node(self, key: str) -> Optional[DagNode]:
        """
        Retrieves a node by key, or None if not present.
        """
        self.check_cleaned()
        return self._nodes.get(key)

    def add_dependency(
            self,
            parent_key: str,
            child_key: str,
            *,
            param_name: str | None = None,
            socket_kind: SocketKind | None = None,
    ) -> None:
        """
        Adds a dependency edge using node keys.

        Semantics:
            ``child_key`` depends on ``parent_key``

        i.e. ``parent`` must be processed before ``child``.

        Nodes are created on-demand if they don't already exist.

        Args:
            parent_key:
                Id/key for the dependency node that must be processed first.
            child_key:
                Id/key for the node that depends on ``parent_key``.
            param_name:
                Optional name of the constructor parameter on ``child`` that
                is wired to ``parent``. When provided, param-aware metadata
                is updated on both nodes.
            socket_kind:
                Optional classification of the socket (normal / SpellContract /
                MutationContract). When provided, the DAG records this for
                later override/mutation logic.
        """
        self.check_cleaned()
        with self._lock:
            parent = self.add_node(parent_key)
            child = self.add_node(child_key)

            # Wire the core graph edge
            child.add_dependency(parent, param_name=param_name)

            if socket_kind is not None:
                self._socket_kinds[(parent, child)] = socket_kind

    def add_dependencies_bulk(
            self,
            edges: Iterable[Tuple[str, str, Optional[str], Optional[SocketKind]]],
    ) -> None:
        """
        Add multiple dependency edges under a single lock.

        Contract:
            - Each edge is (parent_key, child_key, param_name, socket_kind).
            - Nodes are created on demand if missing.
            - Raises ValueError if any key is empty.
        """
        self.check_cleaned()
        with self._lock:
            for parent_key, child_key, param_name, socket_kind in edges:
                if not parent_key or not child_key:
                    raise ValueError("Node key cannot be empty.")
                parent = self._nodes.get(parent_key)
                if parent is None:
                    parent = DagNode(key=parent_key, payload=None)
                    self._nodes[parent_key] = parent
                child = self._nodes.get(child_key)
                if child is None:
                    child = DagNode(key=child_key, payload=None)
                    self._nodes[child_key] = child
                child.add_dependency(parent, param_name=param_name)
                if socket_kind is not None:
                    self._socket_kinds[(parent, child)] = socket_kind

    # --------------------------------------------------------------------- #
    # Topological Sorting
    # --------------------------------------------------------------------- #
    def topological_sort(self) -> List[DagNode]:
        """
        Returns a topologically sorted list of nodes.

        - Nodes with no dependencies appear first.
        - Nodes with equal dependency state are ordered by node id.
        - An exception is raised if a cycle is detected.

        This method is side-effect free and does not mutate the DAG structure.
        """
        self.check_cleaned()
        with self._lock:
            # Compute indegree for each node based on dependencies
            indegree: Dict[DagNode, int] = {
                node: len(node.dependencies) for node in self._nodes.values()
            }

            # Start with all nodes that have no dependencies, ordered by id.
            queue: List[Tuple[str, DagNode]] = [
                (node.id, node)
                for node, degree in indegree.items()
                if degree == 0
            ]
            heapq.heapify(queue)
            ordered: List[DagNode] = []

            while queue:
                _, node = heapq.heappop(queue)
                ordered.append(node)

                for dependent in sorted(node.dependents, key=lambda item: item.id):
                    indegree[dependent] -= 1
                    if indegree[dependent] == 0:
                        heapq.heappush(queue, (dependent.id, dependent))

            if len(ordered) != len(self._nodes):
                # Cycle detected or inconsistent dependency bookkeeping
                raise RuntimeError(
                    "Cycle detected in DirectedAcyclicWorkGraph or inconsistent dependency state."
                )

            return ordered

    def collect_dependency_ids(self) -> List[str]:
        """
        Convenience helper for SpellCrafter-style usage.

        Returns:
            A list of node ids in topological order.
        """
        return [node.id for node in self.topological_sort()]

    # --------------------------------------------------------------------- #
    # Optional Execution Helpers
    # --------------------------------------------------------------------- #
    def execute(self) -> None:
        """
        Sequentially executes all node tasks in topological order.

        - If a node has no tasks, it is simply skipped.
        - Any exception raised by a task propagates to the caller and halts execution.

        This is primarily for debugging / test harnesses and is not required
        for the core Melder resolution path.
        """
        for node in self.topological_sort():
            node.run_tasks()

    def __repr__(self) -> str:
        """Return a compact debug representation of the DAG and node count."""
        return f"DirectedAcyclicWorkGraph(id={self._id!r}, nodes={len(self._nodes)})"
