from __future__ import annotations
from threading import RLock
from typing import Any, Dict, List, Optional
# Melder imports
from melder.spellbook.mutations.research.spell.node.spell_mutation_node import SpellMutationNode
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.synchronization.sync_weak_ref import SyncWeakRef


class ResearchSpell(Cleanable):
    """
    Represents a single spell mutation research line, tracking a linear history of changes
    (mutations) made to a spell's blueprint.

    - **Graph:** Owns a graph of `SpellMutationNode` instances.
    - **HEAD:** Tracks the current HEAD node.
    - **Target:** Holds a weak reference (`SyncWeakRef`) to the live spell blueprint object.

    NOTE: This line is scoped within a single Research session.
    """

    def __init__(self, spell_id: str, *, name: Optional[str] = None) -> None:
        """
        Initializes a ResearchSpell line.

        Args:
            spell_id (str): Concrete spell version id (e.g., SHA256) used as the root version for this research line.
            name (Optional[str], optional): Human-readable name for the research line.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._spell_id: str = spell_id
        self._name: str = name or spell_id
        self._lock: RLock = RLock()

        # Live spell blueprint tracking (weak)
        self._spell_ref: Optional[SyncWeakRef[Any]] = None

        # Mutation graph: id -> node, plus a commit-order index.
        self._nodes: Dict[str, SpellMutationNode] = {}
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
            if self._spell_ref is not None:
                try:
                    self._spell_ref.cleanup()
                except Exception:
                    pass
                self._spell_ref = None

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
    def spell_id(self) -> str:
        """
        Returns the root spell version id (e.g., SHA256) for this research line.

        Returns:
            str: The root spell version ID.
        """
        return self._spell_id

    @property
    def name(self) -> str:
        """
        Returns the human-readable name for this research line.

        Returns:
            str: The line's name.
        """
        return self._name

    @property
    def head_id(self) -> Optional[str]:
        """
        Returns the identifier of the current HEAD node in this research line, if any.

        Returns:
            Optional[str]: The ID of the HEAD node.
        """
        return self._head_id

    @property
    def metadata(self) -> Dict[str, Any]:
        """
        Returns a shallow copy of research-line metadata.

        This can store arbitrary annotations (owner agent id, difficulty, tags, scores).

        Returns:
            Dict[str, Any]: A copy of the line's metadata.
        """
        return dict(self._metadata)

    # ------------------------------------------------------------------ #
    # Live spell reference management
    # ------------------------------------------------------------------ #
    def attach_spell(self, spell: Any) -> None:
        """
        Attaches a live spell object (blueprint) to this research line via `SyncWeakRef`.

        This maintains a non-owning reference to the current blueprint under test.

        Args:
            spell (Any): The live spell object (blueprint) to attach.

        Raises:
            ValueError: If `spell` is None.
        """
        self.check_cleaned()
        if spell is None:
            raise ValueError("spell cannot be None")

        with self._lock:
            # Dispose any previous wrapper.
            if self._spell_ref is not None:
                try:
                    self._spell_ref.cleanup()
                except Exception:
                    pass

            # No on_collect callback yet; we just want a weak pointer.
            self._spell_ref = SyncWeakRef(spell, auto_cleanup=False)

    def get_spell(self) -> Optional[Any]:
        """
        Returns the attached live spell object if it still exists.

        Returns:
            Optional[Any]: The live spell object (blueprint) or None if it has been collected or if no spell has been attached.
        """
        self.check_cleaned()
        ref = self._spell_ref
        if ref is None:
            return None
        try:
            return ref.try_get()
        except RuntimeError:
            # Wrapper was cleaned concurrently; treat as missing.
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
    ) -> SpellMutationNode:
        """
        Starts a new spell mutation node on this research line.

        Behavior:
          - Uses `parent_id` if provided, otherwise the current HEAD id.
          - Creates a new `SpellMutationNode` with metadata only (no structure).
          - Caller is expected to populate `structure` and then call :meth:`commit_mutation`.

        Args:
            parent_id (Optional[str], optional): The explicit parent node ID. Defaults to the current HEAD.
            message (Optional[str], optional): A message describing the mutation.
            tags (Optional[List[str]], optional): Tags associated with the mutation.

        Returns:
            SpellMutationNode: The newly created (uncommitted) mutation node.
        """
        self.check_cleaned()

        # Snapshot parent at call time; the caller may commit later.
        effective_parent = parent_id if parent_id is not None else self._head_id

        meta: Dict[str, Any] = {}
        if message is not None:
            meta["message"] = message
        if tags:
            # Take a defensive copy so callers can mutate their list.
            meta["tags"] = list(tags)

        return SpellMutationNode(
            spell_id=self._spell_id,
            parent_id=effective_parent,
            metadata=meta,
            structure=None,
        )

    def commit_mutation(self, node: SpellMutationNode) -> None:
        """
        Commits a fully-populated `SpellMutationNode` into this research line
        and advances HEAD to that node.

        If the node is already present (same id), this is treated as a HEAD move only.

        Args:
            node (SpellMutationNode): The fully populated node to commit.

        Raises:
            ValueError: If `node` is None.
            RuntimeError: If the `ResearchSpell` has been cleaned.
        """
        self.check_cleaned()
        if node is None:
            raise ValueError("node cannot be None")

        with self._lock:
            if self._nodes is None or self._node_ids is None:
                raise RuntimeError("ResearchSpell has been been cleaned.")

            node_id = node.id
            if node_id not in self._nodes:
                self._nodes[node_id] = node
                self._node_ids.append(node_id)

            self._head_id = node_id

    def checkout(self, node_id: str) -> SpellMutationNode:
        """
        Sets the research line HEAD to the given node and returns it.

        This does not automatically apply the mutation to the live spell; it
        only changes the logical HEAD in the research graph.

        Args:
            node_id (str): The ID of the node to checkout.

        Returns:
            SpellMutationNode: The checked-out node.

        Raises:
            ValueError: If `node_id` is empty.
            RuntimeError: If the `ResearchSpell` has been cleaned.
            KeyError: If `node_id` does not exist in this research line.
        """
        self.check_cleaned()
        if not node_id:
            raise ValueError("node_id cannot be empty")

        with self._lock:
            if self._nodes is None:
                raise RuntimeError("ResearchSpell has been cleaned.")

            node = self._nodes.get(node_id)
            if node is None:
                raise KeyError(f"Unknown mutation node id: {node_id!r}")

            self._head_id = node_id
            return node

    def get_head(self) -> Optional[SpellMutationNode]:
        """
        Returns the current HEAD node for this research line, if any.

        Returns:
            Optional[SpellMutationNode]: The HEAD node, or None.
        """
        self.check_cleaned()
        head_id = self._head_id
        if head_id is None:
            return None

        with self._lock:
            if self._nodes is None:
                return None
            return self._nodes.get(head_id)

    def get_node(self, node_id: str) -> SpellMutationNode:
        """
        Retrieves a specific mutation node by id.

        Args:
            node_id (str): The ID of the node to retrieve.

        Returns:
            SpellMutationNode: The requested node.

        Raises:
            ValueError: If `node_id` is empty.
            RuntimeError: If the `ResearchSpell` has been cleaned.
            KeyError: If the node is not present in this research line.
        """
        self.check_cleaned()
        if not node_id:
            raise ValueError("node_id cannot be empty")

        with self._lock:
            if self._nodes is None:
                raise RuntimeError("ResearchSpell has been cleaned.")

            node = self._nodes.get(node_id)
            if node is None:
                raise KeyError(f"Unknown mutation node id: {node_id!r}")
            return node

    def list_nodes(self) -> List[SpellMutationNode]:
        """
        Returns all mutation nodes for this research line in commit order.

        Returns:
            List[SpellMutationNode]: A list of all nodes.
        """
        self.check_cleaned()
        with self._lock:
            if self._nodes is None or self._node_ids is None:
                return []

            # Use commit-order index when possible; fall back to dict values.
            try:
                ids_snapshot = list(self._node_ids)
            except Exception:
                # Fall back to a plain snapshot if concurrent list operation fails.
                return list(self._nodes.values())

            return [self._nodes[nid] for nid in ids_snapshot if nid in self._nodes]
