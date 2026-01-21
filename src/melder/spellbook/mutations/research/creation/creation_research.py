from threading import RLock
from typing import Any, Dict, List, Optional
# Melder imports
from melder.spellbook.mutations.research.creation.node.creation_mutation_node import CreationMutationNode
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.synchronization.sync_weak_ref import SyncWeakRef
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class ResearchCreation(Cleanable):
    """
    Represents a single creation mutation research line, tracking the runtime history of changes
    (mutations) made to a specific live object instance ("creation").

    - **Graph:** Owns a graph of `CreationMutationNode` instances.
    - **HEAD:** Tracks the current HEAD node.
    - **Target:** Holds a weak reference (`SyncWeakRef`) to the live creation instance.

    NOTE: This line is scoped under a Research session, tied to the lineage of a specific SpellIndex.
    """
    __melder_internal__ = _mrg.sentinel
    def __init__(self, creation_id: str, *, name: Optional[str] = None) -> None:
        """
        Initializes a ResearchCreation line.

        Args:
            creation_id (str): The unique identifier for the live object instance this line targets.
            name (Optional[str], optional): Human-readable name for the research line.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._creation_id: str = creation_id
        self._name: str = name or creation_id
        self._lock: RLock = RLock()

        # Live creation tracking (weak)
        self._creation_ref: Optional[SyncWeakRef[Any]] = None

        # Mutation graph: id -> node, plus commit-order index.
        self._nodes: Dict[str, CreationMutationNode] = {}
        self._node_ids: List[str] = []

        self._head_id: Optional[str] = None
        self._metadata: Dict[str, Any] = {}

    def cleanup(self) -> None:
        """
        Cleans up the research line and all mutation nodes.

        This involves cleaning up the concurrent collections, disposing of the weak reference wrapper, and nulling out references. This method is idempotent.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            # Cleanup nodes
            if self._nodes is not None:
                for _, node in list(self._nodes.items()):
                    try:
                        node.cleanup()
                    except Exception:
                        pass
                try:
                    self._nodes.clear()
                except Exception:
                    pass
                self._nodes = None

            # Cleanup commit-order index
            if self._node_ids is not None:
                try:
                    self._node_ids.clear()
                except Exception:
                    pass
                self._node_ids = None

            # Cleanup weak ref wrapper
            if self._creation_ref is not None:
                try:
                    self._creation_ref.cleanup()
                except Exception:
                    pass
                self._creation_ref = None

            self._head_id = None
            self._metadata.clear()
            self._metadata = None
        self._lock = None

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #
    @property
    def id(self) -> str:
        """
        Returns the research line identifier (ULID string), local to the Research session.

        Returns:
            str: The research line's unique ID.
        """
        return self._id

    @property
    def creation_id(self) -> str:
        """
        Returns the identifier for the creation instance this research line targets.

        Returns:
            str: The target creation's ID.
        """
        return self._creation_id

    @property
    def name(self) -> str:
        """
        Returns the human-readable name of this research line.

        Returns:
            str: The line's name.
        """
        return self._name

    @property
    def head_id(self) -> Optional[str]:
        """
        Returns the identifier of the current HEAD node, if any.

        Returns:
            Optional[str]: The ID of the HEAD node.
        """
        return self._head_id

    @property
    def metadata(self) -> Dict[str, Any]:
        """
        Returns a shallow copy of metadata attached to this research line.

        Returns:
            Dict[str, Any]: A copy of the line's metadata.
        """
        return dict(self._metadata)

    # ------------------------------------------------------------------ #
    # Live creation reference management
    # ------------------------------------------------------------------ #
    def attach_creation(self, creation: Any) -> None:
        """
        Attaches a live creation object to this research line via `SyncWeakRef`.

        Args:
            creation (Any): The live creation object to attach.

        Raises:
            ValueError: If `creation` is None.
        """
        self.check_cleaned()
        if creation is None:
            raise ValueError("creation cannot be None")

        with self._lock:
            if self._creation_ref is not None:
                try:
                    self._creation_ref.cleanup()
                except Exception:
                    pass

            self._creation_ref = SyncWeakRef(creation, auto_cleanup=False)

    def get_creation(self) -> Optional[Any]:
        """
        Returns the attached live creation object if it still exists.

        Returns:
            Optional[Any]: The live creation object or None if it has been collected or is unattached.
        """
        self.check_cleaned()
        ref = self._creation_ref
        if ref is None:
            return None
        try:
            return ref.try_get()
        except RuntimeError:
            return None

    # ------------------------------------------------------------------ #
    # Mutation graph operations
    # ------------------------------------------------------------------ #
    def begin_mutation(
            self,
            *,
            parent_id: Optional[str] = None,
            message: Optional[str] = None,
            tags: Optional[List[str]] = None,
    ) -> CreationMutationNode:
        """
        Starts a new creation mutation node on this research line.

        Behavior:
          - Uses `parent_id` if provided, otherwise the current HEAD id.
          - Creates a new `CreationMutationNode` with metadata only (no snapshot).
          - Caller is expected to populate the `snapshot` and then call :meth:`commit_mutation`.

        Args:
            parent_id (Optional[str], optional): The explicit parent node ID. Defaults to the current HEAD.
            message (Optional[str], optional): A message describing the mutation.
            tags (Optional[List[str]], optional): Tags associated with the mutation.

        Returns:
            CreationMutationNode: The newly created (uncommitted) mutation node.
        """
        self.check_cleaned()

        effective_parent = parent_id if parent_id is not None else self._head_id

        meta: Dict[str, Any] = {}
        if message is not None:
            meta["message"] = message
        if tags:
            meta["tags"] = list(tags)

        return CreationMutationNode(
            creation_id=self._creation_id,
            parent_id=effective_parent,
            metadata=meta,
            snapshot=None,
        )

    def commit_mutation(self, node: CreationMutationNode) -> None:
        """
        Commits a fully-populated `CreationMutationNode` into this research line
        and advances HEAD.

        Args:
            node (CreationMutationNode): The fully populated node to commit.

        Raises:
            ValueError: If `node` is None.
            RuntimeError: If the `ResearchCreation` has been cleaned.
        """
        self.check_cleaned()
        if node is None:
            raise ValueError("node cannot be None")

        with self._lock:
            if self._nodes is None or self._node_ids is None:
                raise RuntimeError("ResearchCreation has been cleaned.")

            node_id = node.id
            if node_id not in self._nodes:
                self._nodes[node_id] = node
                self._node_ids.append(node_id)

            self._head_id = node_id

    def checkout(self, node_id: str) -> CreationMutationNode:
        """
        Sets the research line HEAD to the given node and returns it.

        Args:
            node_id (str): The ID of the node to checkout.

        Returns:
            CreationMutationNode: The checked-out node.

        Raises:
            ValueError: If `node_id` is empty.
            RuntimeError: If the `ResearchCreation` has been cleaned.
            KeyError: If `node_id` is unknown.
        """
        self.check_cleaned()
        if not node_id:
            raise ValueError("node_id cannot be empty")

        with self._lock:
            if self._nodes is None:
                raise RuntimeError("ResearchCreation has been cleaned.")

            node = self._nodes.get(node_id)
            if node is None:
                raise KeyError(f"Unknown creation node id: {node_id!r}")

            self._head_id = node_id
            return node

    def get_head(self) -> Optional[CreationMutationNode]:
        """
        Returns the current HEAD node for this research line, if any.

        Returns:
            Optional[CreationMutationNode]: The HEAD node, or None.
        """
        self.check_cleaned()
        head_id = self._head_id
        if head_id is None:
            return None

        with self._lock:
            if self._nodes is None:
                return None
            return self._nodes.get(head_id)

    def get_node(self, node_id: str) -> CreationMutationNode:
        """
        Retrieves a specific mutation node by id.

        Args:
            node_id (str): The ID of the node to retrieve.

        Returns:
            CreationMutationNode: The requested node.

        Raises:
            ValueError: If `node_id` is empty.
            RuntimeError: If the `ResearchCreation` has been cleaned.
            KeyError: If the node is not present.
        """
        self.check_cleaned()
        if not node_id:
            raise ValueError("node_id cannot be empty")

        with self._lock:
            if self._nodes is None:
                raise RuntimeError("ResearchCreation has been cleaned.")

            node = self._nodes.get(node_id)
            if node is None:
                raise KeyError(f"Unknown creation node id: {node_id!r}")
            return node

    def list_nodes(self) -> List[CreationMutationNode]:
        """
        Returns all mutation nodes for this research line in commit order.

        Returns:
            List[CreationMutationNode]: A list of all nodes.
        """
        self.check_cleaned()
        with self._lock:
            if self._nodes is None or self._node_ids is None:
                return []

            try:
                ids_snapshot = list(self._node_ids)
            except Exception:
                return list(self._nodes.values())

            return [self._nodes[nid] for nid in ids_snapshot if nid in self._nodes]
