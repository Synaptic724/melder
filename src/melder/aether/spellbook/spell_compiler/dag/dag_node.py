from typing import Any, Callable, Dict, List, Set, ClassVar



# Melder Imports
from melder.utilities.general_base.cleanable import Cleanable

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

    Subsystem Context:
        The node type of the `dag` package: `DirectedAcyclicWorkGraph` owns these and
        computes a topological order over them; param-aware edges
        (`children_by_param` / `incoming_params`) let the override system target one
        socket later.

    System Context:
        Phase 3 (local frame / DAG) of the conjure pipeline. Its edges model "must be
        created before me" for resolution ordering.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. A node in the resolution DAG: a keyed unit of work with "
        "dependency/dependent DagNode sets and param-aware edges (children_by_param / "
        "incoming_params). Lightweight - no separate Edge objects."
    )
    __slots__ = Cleanable.__slots__ + [
        "_children_by_param",
        "_dependencies",
        "_dependents",
        "_id",
        "_incoming_params",
        "_payload",
        "_tasks",
    ]
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

        # Nodes this node depends on (parents) and nodes that depend on this node (children)
        self._dependencies: Set["DagNode"] = set()
        self._dependents: Set["DagNode"] = set()

        # Optional task callbacks executed when this node is processed
        self._tasks: List[Callable[[], Any]] = []

        # ------------------------------------------------------------------ #
        # Param / socket metadata (Melder-specific)
        # ------------------------------------------------------------------ #

        # For this node as a *parent*: param_name -> set of child nodes
        # Example: root._children_by_param[ "repo"] -> {RepoNode}
        self._children_by_param: Dict[str, Set["DagNode"]] = {}

        # For this node as a *child*: parent node -> param_name
        # Example: repo_node._incoming_params[root_node] == "repo"
        self._incoming_params: Dict["DagNode", str] = {}

    # --------------------------------------------------------------------- #
    # Cleanup
    # --------------------------------------------------------------------- #
    def cleanup(self) -> None:
        """
        Fully detach this node from the graph and clear payload,
        dependencies, dependents, and tasks.

        Idempotent.
        """
        if self._cleaned:
            return
        self._cleaned = True
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

        # Clear param metadata
        self._children_by_param.clear()
        self._incoming_params.clear()

        # Clear tasks
        self._tasks.clear()

    # --------------------------------------------------------------------- #
    # Properties
    # --------------------------------------------------------------------- #
    @property
    def id(self) -> str:
        """Return the stable node identifier used by the DAG."""
        return self._id

    @property
    def payload(self) -> Any | None:
        """Return the optional payload attached to this node."""
        return self._payload

    @payload.setter
    def payload(self, value: Any | None) -> None:
        """Replace the optional payload attached to this node."""
        self.check_cleaned()
        self._payload = value

    @property
    def dependencies(self) -> Set["DagNode"]:
        """
        Nodes that this node depends on (must be processed first).
        """
        return self._dependencies

    @property
    def dependents(self) -> Set["DagNode"]:
        """
        Nodes that depend on this node.
        """
        return self._dependents

    @property
    def children_by_param(self) -> Dict[str, Set["DagNode"]]:
        """
        Param-aware view of this node's outgoing edges.

        Keys are parameter names on the *parent*; values are the child nodes
        that are wired into that parameter.
        """
        return self._children_by_param

    @property
    def incoming_params(self) -> Dict["DagNode", str]:
        """
        Param-aware view of this node's incoming edges.

        Keys are parent nodes; values are the parameter name on the parent
        that targets this node.
        """
        return self._incoming_params

    # --------------------------------------------------------------------- #
    # Configuration
    # --------------------------------------------------------------------- #
    def add_dependency(
            self,
            dependency: "DagNode",
            *,
            param_name: str | None = None,
    ) -> None:
        """
        Adds a dependency edge: `self` depends on `dependency`.

        Args:
            dependency:
                Node that must be processed before this node.
            param_name:
                Optional name of the parameter on *this node* that points
                to "dependency". When provided, param-level metadata is
                updated so override systems can target this socket later.
        """
        self.check_cleaned()
        if dependency is self:
            raise ValueError("DagNode cannot depend on itself.")
        if dependency not in self._dependencies:
            self._dependencies.add(dependency)
            dependency._dependents.add(self)

            if param_name is not None:
                # `self` is the child from the perspective of constructor params;
                # the parameter lives on `self` and points at `dependency`.
                existing = self._incoming_params.get(dependency)
                if existing is not None and existing != param_name:
                    # Single parent->child edge should not carry multiple param names.
                    raise ValueError(
                        f"DagNode {self._id!r} already has incoming param "
                        f"{existing!r} from parent {dependency._id!r}; "
                        f"cannot also register {param_name!r}."
                    )
                self._incoming_params[dependency] = param_name
                dependency._children_by_param.setdefault(param_name, set()).add(self)

    def add_task(self, fn: Callable[[], Any]) -> None:
        """
        Optional

        Registers a callable to be executed when this node is processed.

        This is primarily for testing / demonstration and is not required
        for Melder's spell resolution. It is kept to minimize behavioural
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
        """Return a compact debug representation of the node and edge counts."""
        return f"DagNode(id={self._id!r}, deps={len(self._dependencies)}, dependents={len(self._dependents)})"
