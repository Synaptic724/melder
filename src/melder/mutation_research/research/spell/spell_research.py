from threading import RLock
from typing import Any, Dict, List, Optional
# Melder imports
from melder.mutation_research.research.spell.node.spell_mutation_node import SpellMutationNode
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.synchronization.sync_weak_ref import SyncWeakRef
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class ResearchSpell(Cleanable):
    """
    One research-session lineage for experimental spell mutations.

    `ResearchSpell` is the mutable research-side record for one spell version as
    it moves through experimental mutation attempts. It owns the mutation-node
    graph for that line, tracks the logical HEAD within that graph, and keeps a
    weak non-owning pointer to the live spell blueprint currently under test.

    Contract:
    - Scope is limited to a single research session; this is not a permanent
      spellbook lineage record.
    - Node history is owned strongly by this object and cleaned with it.
    - The live spell reference is weak on purpose so research bookkeeping does
      not keep the blueprint alive after the owning runtime drops it.
    """
    __melder_internal__ = _mrg.sentinel
    def __init__(self, spell_id: str, *, name: Optional[str] = None) -> None:
        """
        Initialize one research line for a concrete spell version.

        Args:
            spell_id (str): Concrete spell version id (e.g., SHA256) used as the root version for this research line.
            name (Optional[str], optional): Human-readable name for the research line.
        Contract:
            - Creates one local research-line id distinct from the tracked
              `spell_id`.
            - Starts with no attached live spell and no mutation nodes.
            - Starts with no HEAD; HEAD advances only after
              `commit_mutation(...)`.
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
        Tear down this research line and every owned mutation node.

        Contract:
            - Idempotent and lock-guarded.
            - Cleans owned `SpellMutationNode` instances before dropping graph
              containers.
            - Cleans the weak-reference wrapper but does not attempt to clean
              the live spell object itself.
            - Nulls internal references so future callers fail through
              `check_cleaned()`.
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
        Return the research-line identifier local to this session.

        Returns:
            str: The research line's unique ID.
        """
        return self._id

    @property
    def spell_id(self) -> str:
        """
        Return the root spell version id tracked by this research line.

        Returns:
            str: The root spell version ID.
        """
        return self._spell_id

    @property
    def name(self) -> str:
        """
        Return the human-readable label for this research line.

        Returns:
            str: The line's name.
        """
        return self._name

    @property
    def head_id(self) -> Optional[str]:
        """
        Return the current logical HEAD node id, if any.

        HEAD is the node this research line currently considers checked out for
        further mutation or inspection. It is independent of whether a live
        spell blueprint is currently attached.

        Returns:
            Optional[str]: The ID of the HEAD node.
        """
        return self._head_id

    @property
    def metadata(self) -> Dict[str, Any]:
        """
        Return a shallow snapshot of research-line metadata.

        This can store arbitrary annotations (owner agent id, difficulty, tags, scores).

        Returns:
            Dict[str, Any]: A copy of the line's metadata.

        Contract:
            - Returns a detached dictionary so callers cannot mutate internal
              metadata storage directly.
        """
        return dict(self._metadata)

    # ------------------------------------------------------------------ #
    # Live spell reference management
    # ------------------------------------------------------------------ #
    def attach_spell(self, spell: Any) -> None:
        """
        Attach the current live spell blueprint to this research line.

        This maintains a non-owning reference to the current blueprint under
        test. Research bookkeeping uses the weak wrapper so the live spell can
        still disappear naturally when the owning runtime releases it.

        Args:
            spell (Any): The live spell object (blueprint) to attach.
        Contract:
            - Replaces any prior weak wrapper for the previously attached spell.
            - Never takes strong ownership of the live spell.

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
        Return the attached live spell blueprint if it still exists.

        Returns:
            Optional[Any]: The live spell object (blueprint) or None if it has been collected or if no spell has been attached.

        Contract:
            - Returns None when no live spell is attached.
            - Returns None when the weak wrapper has been cleaned or when the
              target has already been garbage collected.
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
        Start a new uncommitted mutation node on this research line.

        Behavior:
          - Uses `parent_id` if provided, otherwise the current HEAD id.
          - Creates a new `SpellMutationNode` with metadata only (no structure).
          - Caller is expected to populate `structure` and then call :meth:`commit_mutation`.

        Args:
            parent_id (Optional[str], optional): The explicit parent node ID. Defaults to the current HEAD.
            message (Optional[str], optional): A message describing the mutation.
            tags (Optional[List[str]], optional): Tags associated with the mutation.

        Contract:
            - Does not mutate line state or HEAD by itself.
            - Captures the effective parent at call time so later HEAD moves do
              not retroactively change the node's parent.
            - Creates a metadata-only node; structure population and commit are
              explicitly separate steps.

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
        Commit a populated mutation node into this research line and advance HEAD.

        If the node is already present (same id), this is treated as a HEAD move only.

        Args:
            node (SpellMutationNode): The fully populated node to commit.

        Contract:
            - Inserts the node into the graph if it is new.
            - Preserves commit-order tracking in `_node_ids` for newly inserted
              nodes.
            - Always advances HEAD to the committed node id, even when the node
              was already known.

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
        Move the logical HEAD to `node_id` and return that node.

        This does not automatically apply the mutation to the live spell; it
        only changes the logical HEAD in the research graph.

        Args:
            node_id (str): The ID of the node to checkout.

        Contract:
            - Changes only the research-line HEAD pointer.
            - Does not mutate the attached live spell or any node contents.

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
        Return the current HEAD node for this research line, if any.

        Returns:
            Optional[SpellMutationNode]: The HEAD node, or None.

        Contract:
            - Returns None when no node has been committed yet.
            - Returns the node currently named by `head_id`; it does not clone
              the node.
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
        Return one mutation node by id.

        Args:
            node_id (str): The ID of the node to retrieve.

        Contract:
            - Returns the live node object stored in this research line.
            - Raises instead of returning None for unknown ids so callers do
              not silently proceed on a missing mutation.

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
        Return every mutation node for this research line in commit order.

        Returns:
            List[SpellMutationNode]: A list of all nodes.

        Contract:
            - Prefers the explicit commit-order index stored in `_node_ids`.
            - Falls back to raw node values only if the commit-order snapshot
              cannot be taken safely.
            - Returns a new list container on every call.
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
