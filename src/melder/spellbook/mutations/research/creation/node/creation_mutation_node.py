from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional

# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class CreationMutationNode(Cleanable):
    """
    Represents a single mutation node (commit) in a live object's (creation's) mutation graph.

    This node captures the runtime "to" state (snapshot or diff) for a single
    live object managed by a Conduit.
    """

    def __init__(
            self,
            creation_id: str,
            parent_id: Optional[str] = None,
            *,
            metadata: Optional[Dict[str, Any]] = None,
            snapshot: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initializes a CreationMutationNode.

        Args:
            creation_id (str): The unique identifier for the live object instance.
            parent_id (Optional[str], optional): The ID of the previous mutation node in the chain. None if this is the root.
            metadata (Optional[Dict[str, Any]], optional): Free-form annotations for this mutation.
            snapshot (Optional[Dict[str, Any]], optional): The structural snapshot of the live object's state after this mutation.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._creation_id: str = creation_id
        self._parent_id: Optional[str] = parent_id
        self._metadata: Dict[str, Any] = metadata or {}
        self._snapshot: Optional[Dict[str, Any]] = snapshot
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Deterministically tears down this mutation node, clearing references.

        This method is idempotent.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._parent_id = None
            self._metadata.clear()
            self._metadata = None
            self._snapshot = None
        self._lock = None

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #
    @property
    def id(self) -> str:
        """
        Returns the internal node identifier (ULID string).

        Returns:
            str: The node's unique ID.
        """
        return self._id

    @property
    def creation_id(self) -> str:
        """
        Returns the identifier for the live object instance this node belongs to.

        This ID is expected to come from the Creations / LesserCreations manager.

        Returns:
            str: The ID of the target creation.
        """
        return self._creation_id

    @property
    def parent_id(self) -> Optional[str]:
        """
        Returns the parent node id for this creation's mutation chain, or None if root.

        Returns:
            Optional[str]: The ID of the parent node.
        """
        return self._parent_id

    @property
    def metadata(self) -> Dict[str, Any]:
        """
        Returns a shallow copy of metadata annotations for this node.

        Returns:
            Dict[str, Any]: A copy of the mutation's metadata.
        """
        return dict(self._metadata)

    @property
    def snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Returns the opaque snapshot/diff of the "to" runtime state for this mutation.

        Returns:
            Optional[Dict[str, Any]]: The runtime state snapshot.
        """
        return self._snapshot

    # ------------------------------------------------------------------ #
    # Behavior (placeholders)
    # ------------------------------------------------------------------ #
    @classmethod
    def snapshot_from_creation(
            cls,
            creation: Any,
            *,
            creation_id: str,
            parent_id: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> "CreationMutationNode":
        """
        Creates a new mutation node by inspecting the live creation instance.

        This method should:
          - Capture the current attributes/state (or a structured diff).
          - Attach metadata (message, tags, etc.).

        Args:
            creation (Any): The live object instance to inspect.
            creation_id (str): The concrete identity of the creation.
            parent_id (Optional[str], optional): The ID of the parent node.
            metadata (Optional[Dict[str, Any]], optional): Annotation metadata.

        Returns:
            CreationMutationNode: The newly created mutation node.

        Raises:
            NotImplementedError: If the inspection logic is not yet implemented.
        """
        raise NotImplementedError("CreationMutationNode.snapshot_from_creation is not implemented yet.")

    def apply_to_creation(self, creation: Any) -> Any:
        """
        Applies this node's snapshot/diff to the provided live creation instance,
        reshaping it into the node's target state.

        Args:
            creation (Any): The live object instance to mutate.

        Returns:
            Any: The potentially mutated live object instance.

        Raises:
            NotImplementedError: If the mutation application logic is not yet implemented.
        """
        raise NotImplementedError("CreationMutationNode.apply_to_creation is not implemented yet.")
