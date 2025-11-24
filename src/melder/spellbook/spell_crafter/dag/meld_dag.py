from threading import RLock
from typing import Any, Callable, Dict, List, Optional, Set
# Melder Imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class DagNode(Cleanable):
    """
    Internal

    Represents a single node in a Directed Acyclic Graph used for resolution.

    This is intentionally lightweight:

    - No separate Edge objects.
    - Dependencies are expressed as direct references to other DagNode instances.
    - Optional `payload` and `tasks` allow the same DAG to be reused for:
        * resolution ordering (spell dependencies)
        * simple execution flows (if desired).

    Typical usage in Melder:

        - Each node maps to a "unit of work" (e.g., a spell or constructor).
        - Dependencies model "must be created before me".
        - The DAG object is responsible for computing a topological order.
    """

    def __init__(self, key: str, payload: Any | None = None) -> None:
        """
        Initializes a new DagNode.

        Args:
            key: Stable identifier for the node (e.g., spell id or name).
            payload: Optional arbitrary payload (class, factory, metadata, etc.).
        """
        super().__init__()
        self._id: str = key
        self._payload: Any | None = payload
        self._dependencies: Set["DagNode"] = set()   # Nodes this node depends on
        self._dependents: Set["DagNode"] = set()     # Nodes that depend on this node
        self._tasks: List[Callable[[], Any]] = []

    # --------------------------------------------------------------------- #
    # Cleanup
    # --------------------------------------------------------------------- #
    def cleanup(self) -> None:
        """
        Cleans up the node, dropping references to payload, dependencies,
        dependents, and tasks.

        Idempotent.
        """
        if self._cleaned:
            return

        # No lock is used here; nodes are owned by the DAG and not expected
        # to be mutated concurrently in Melder.
        self._payload = None

        # Break graph links
        for dep in list(self._dependencies):
            dep._dependents.discard(self)
        for dep in list(self._dependents):
            dep._dependencies.discard(self)

        self._dependencies.clear()
        self._dependents.clear()
        self._tasks.clear()
        self._cleaned = True

    # --------------------------------------------------------------------- #
    # Properties
    # --------------------------------------------------------------------- #
    @property
    def id(self) -> str:
        """
        Returns the stable identifier for this node.
        """
        return self._id

    @property
    def payload(self) -> Any | None:
        """
        Returns the payload associated with this node.
        """
        return self._payload

    @payload.setter
    def payload(self, value: Any | None) -> None:
        self.check_cleaned()
        self._payload = value

    @property
    def dependencies(self) -> Set["DagNode"]:
        """
        Returns the set of nodes this node directly depends on.
        """
        return self._dependencies

    @property
    def dependents(self) -> Set["DagNode"]:
        """
        Returns the set of nodes that directly depend on this node.
        """
        return self._dependents

    # --------------------------------------------------------------------- #
    # Configuration
    # --------------------------------------------------------------------- #
    def add_dependency(self, dependency: "DagNode") -> None:
        """
        Adds a dependency edge: `self` depends on `dependency`.

        Args:
            dependency: Node that must be processed before this node.
        """
        self.check_cleaned()
        if dependency is self:
            raise ValueError("DagNode cannot depend on itself.")
        if dependency not in self._dependencies:
            self._dependencies.add(dependency)
            dependency._dependents.add(self)

    def add_task(self, fn: Callable[[], Any]) -> None:
        """
        Optional

        Registers a callable to be executed when this node is processed.

        This is primarily for testing / demonstration and is not required
        for Melder's spell resolution. It is kept to minimize behavioral
        changes from prior DAG usage.
        """
        self.check_cleaned()
        if not callable(fn):
            raise TypeError("Task must be callable.")
        self._tasks.append(fn)

    def run_tasks(self) -> None:
        """
        Executes all registered tasks in insertion order.

        Any exception will propagate to the caller.
        """
        self.check_cleaned()
        for task in self._tasks:
            task()

    def __repr__(self) -> str:
        return f"DagNode(id={self._id!r}, deps={len(self._dependencies)}, dependents={len(self._dependents)})"


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

    def __init__(self) -> None:
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: RLock = RLock()
        self._nodes: Dict[str, DagNode] = {}

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

    def get_node(self, key: str) -> Optional[DagNode]:
        """
        Retrieves a node by key, or None if not present.
        """
        self.check_cleaned()
        return self._nodes.get(key)

    def add_dependency(self, parent_key: str, child_key: str) -> None:
        """
        Adds a dependency edge using node keys.

        Semantics:
            `child_key` depends on `parent_key`

        i.e. `parent` must be processed before `child`.

        Nodes are created on-demand if they don't already exist.
        """
        self.check_cleaned()
        with self._lock:
            parent = self.add_node(parent_key)
            child = self.add_node(child_key)
            child.add_dependency(parent)

    # --------------------------------------------------------------------- #
    # Topological Sorting
    # --------------------------------------------------------------------- #
    def topological_sort(self) -> List[DagNode]:
        """
        Returns a topologically sorted list of nodes.

        - Nodes with no dependencies appear first.
        - An exception is raised if a cycle is detected.

        This method is side-effect free and does not mutate the DAG structure.
        """
        self.check_cleaned()
        with self._lock:
            # Compute indegree for each node based on dependencies
            indegree: Dict[DagNode, int] = {
                node: len(node.dependencies) for node in self._nodes.values()
            }

            # Start with all nodes that have no dependencies
            queue: List[DagNode] = [n for n, deg in indegree.items() if deg == 0]
            ordered: List[DagNode] = []

            idx = 0
            while idx < len(queue):
                node = queue[idx]
                idx += 1
                ordered.append(node)

                for dependent in node.dependents:
                    indegree[dependent] -= 1
                    if indegree[dependent] == 0:
                        queue.append(dependent)

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
        return f"DirectedAcyclicWorkGraph(id={self._id!r}, nodes={len(self._nodes)})"