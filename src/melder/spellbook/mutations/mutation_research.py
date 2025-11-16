from __future__ import annotations

from threading import RLock
from typing import Any, Dict, List, Optional

import weakref

# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.spellbook.spell_index.spell_index import SpellIndex  # TODO: adjust import path if needed


class SpellMutationNode(Cleanable):
    """
    Represents a single mutation node (commit) in a spell's mutation graph.

    This node captures the structural "to" state for a spell at a point in time.
    The parent node is the implicit "from" state (via `parent_id`).

    NOTE:
        `_spell_id` is expected to be the concrete spell version identifier
        (e.g., SHA256) at the time this node was created.
    """

    def __init__(
            self,
            spell_id: str,
            parent_id: Optional[str] = None,
            *,
            metadata: Optional[Dict[str, Any]] = None,
            structure: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._spell_id: str = spell_id
        self._parent_id: Optional[str] = parent_id
        self._metadata: Dict[str, Any] = metadata or {}
        self._structure: Dict[str, Any] | None = structure
        self._lock: RLock = RLock()

    def cleanup(self) -> None:
        """
        Cleans up the mutation node.

        Idempotent.
        """
        if self._cleaned:
            return
        self._cleaned = True

        self._spell_id = ""
        self._parent_id = None
        self._metadata.clear()
        self._metadata = {}
        self._structure = None
        self._lock = None  # type: ignore[assignment]

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #
    @property
    def id(self) -> str:
        return self._id

    @property
    def spell_id(self) -> str:
        """
        Concrete version id (e.g., SHA256) associated with this node.
        """
        return self._spell_id

    @property
    def parent_id(self) -> Optional[str]:
        return self._parent_id

    @property
    def metadata(self) -> Dict[str, Any]:
        return dict(self._metadata)

    @property
    def structure(self) -> Optional[Dict[str, Any]]:
        """
        Opaque structural snapshot of the "to" state for this mutation.
        """
        return self._structure

    # ------------------------------------------------------------------ #
    # Behavior (placeholders)
    # ------------------------------------------------------------------ #
    @classmethod
    def snapshot_from_spell(
            cls,
            spell: Any,
            *,
            spell_id: str,
            parent_id: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> "SpellMutationNode":
        """
        Creates a new mutation node by introspecting the given spell object.

        This should:
          - Inspect the spell (e.g., via SpellCrafter inspectors).
          - Build a deep structure snapshot.
          - Attach metadata (message, tags, etc.).
          - Use `spell_id` as the concrete version identifier for this snapshot.
        """
        raise NotImplementedError("SpellMutationNode.snapshot_from_spell is not implemented yet.")

    def apply_to_blueprint(self, spell: Any) -> Any:
        """
        Applies this node's `structure` to the provided spell blueprint, producing
        a new blueprint object representing the mutated form.

        The exact semantics (in-place vs new class) are left to the implementation.

        Expected high-level behavior:
          - Take `spell` as the "from" blueprint.
          - Use `self._structure` as the "to" blueprint description.
          - Return a new blueprint / class object aligned with this node.
        """
        raise NotImplementedError("SpellMutationNode.apply_to_blueprint is not implemented yet.")


class CreationMutationNode(Cleanable):
    """
    Represents a single mutation node (commit) in a creation's mutation graph.

    This node captures the runtime "to" state (snapshot or diff) for a single
    live object ("creation").
    """

    def __init__(
            self,
            creation_id: str,
            parent_id: Optional[str] = None,
            *,
            metadata: Optional[Dict[str, Any]] = None,
            snapshot: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._creation_id: str = creation_id
        self._parent_id: Optional[str] = parent_id
        self._metadata: Dict[str, Any] = metadata or {}
        self._snapshot: Dict[str, Any] | None = snapshot
        self._lock: RLock = RLock()

    def cleanup(self) -> None:
        """
        Cleans up the mutation node.

        Idempotent.
        """
        if self._cleaned:
            return
        self._cleaned = True

        self._creation_id = ""
        self._parent_id = None
        self._metadata.clear()
        self._metadata = {}
        self._snapshot = None
        self._lock = None  # type: ignore[assignment]

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #
    @property
    def id(self) -> str:
        return self._id

    @property
    def creation_id(self) -> str:
        return self._creation_id

    @property
    def parent_id(self) -> Optional[str]:
        return self._parent_id

    @property
    def metadata(self) -> Dict[str, Any]:
        return dict(self._metadata)

    @property
    def snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Opaque snapshot/diff of the "to" runtime state for this mutation.
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

        This should:
          - Capture the current attributes/methods (or a structured diff).
          - Attach metadata (message, tags, etc.).
          - Use `creation_id` as the concrete identity of the creation.
        """
        raise NotImplementedError("CreationMutationNode.snapshot_from_creation is not implemented yet.")

    def apply_to_creation(self, creation: Any) -> Any:
        """
        Applies this node's snapshot/diff to the provided live creation instance,
        reshaping it into the node's target state.
        """
        raise NotImplementedError("CreationMutationNode.apply_to_creation is not implemented yet.")


class ResearchSpell(Cleanable):
    """
    Represents a single spell mutation research line.

    - Owns a mutation graph (SpellMutationNode instances).
    - Tracks a head node.
    - Optionally holds a weak reference to the live spell object.

    NOTE:
        This is *within* the scope of a single Research session, which is
        anchored to one SpellIndex (spell lineage). Multiple ResearchSpell
        lines under the same Research may represent competing ideas/branches
        for that same SpellIndex.
    """

    def __init__(self, spell_id: str, *, name: Optional[str] = None) -> None:
        """
        Args:
            spell_id: Concrete spell version id (e.g., SHA256) used as the root
                      version for this research line.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._spell_id: str = spell_id
        self._name: str = name or spell_id
        self._lock: RLock = RLock()

        self._spell_ref: Optional[weakref.ReferenceType[Any]] = None
        self._nodes: ConcurrentDict[str, SpellMutationNode] = ConcurrentDict()
        self._head_id: Optional[str] = None
        self._metadata: Dict[str, Any] = {}

    def cleanup(self) -> None:
        """
        Cleans up the research line and all mutation nodes.

        Idempotent.
        """
        if self._cleaned:
            return
        self._cleaned = True

        with self._lock:
            for _, node in list(self._nodes.items()):
                try:
                    node.cleanup()
                except Exception:
                    pass
            self._nodes.cleanup()
            self._nodes = None  # type: ignore[assignment]

            self._spell_ref = None
            self._head_id = None
            self._metadata.clear()
            self._metadata = {}
            self._spell_id = ""
            self._name = ""
            self._lock = None  # type: ignore[assignment]

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #
    @property
    def id(self) -> str:
        return self._id

    @property
    def spell_id(self) -> str:
        """
        Root spell version id (e.g., SHA256) for this research line.
        """
        return self._spell_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def head_id(self) -> Optional[str]:
        return self._head_id

    @property
    def metadata(self) -> Dict[str, Any]:
        return dict(self._metadata)

    # ------------------------------------------------------------------ #
    # Live spell reference management
    # ------------------------------------------------------------------ #
    def attach_spell(self, spell: Any) -> None:
        """
        Attaches a live spell object (blueprint) to this research line via weakref.

        Intended use:
          - Keep a non-owning reference to the current blueprint under test.
          - Allow background mutations/checkouts to re-shape or re-instantiate
            this blueprint as new versions are explored.
        """
        raise NotImplementedError("ResearchSpell.attach_spell is not implemented yet.")

    def get_spell(self) -> Optional[Any]:
        """
        Returns the attached live spell object if it still exists.

        Returns:
            The live spell object (blueprint) or None if it has been collected.
        """
        raise NotImplementedError("ResearchSpell.get_spell is not implemented yet.")

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

        Typically:
          - Uses `parent_id` (or current head if None) as the logical "from" node.
          - Creates a new SpellMutationNode with metadata only.
          - Caller then snapshots structure and commits it.
        """
        raise NotImplementedError("ResearchSpell.begin_mutation is not implemented yet.")

    def commit_mutation(self, node: SpellMutationNode) -> None:
        """
        Commits a fully-populated SpellMutationNode into this research line
        and advances HEAD to that node.
        """
        raise NotImplementedError("ResearchSpell.commit_mutation is not implemented yet.")

    def checkout(self, node_id: str) -> SpellMutationNode:
        """
        Sets the research line HEAD to the given node and returns it.

        This does not automatically apply the mutation to the live spell; it
        only changes the logical HEAD in the research graph.
        """
        raise NotImplementedError("ResearchSpell.checkout is not implemented yet.")

    def get_head(self) -> Optional[SpellMutationNode]:
        """
        Returns the current HEAD node for this research line, if any.
        """
        raise NotImplementedError("ResearchSpell.get_head is not implemented yet.")

    def get_node(self, node_id: str) -> SpellMutationNode:
        """
        Retrieves a specific mutation node by id.
        """
        raise NotImplementedError("ResearchSpell.get_node is not implemented yet.")

    def list_nodes(self) -> List[SpellMutationNode]:
        """
        Returns all mutation nodes for this research line in undefined order.
        """
        raise NotImplementedError("ResearchSpell.list_nodes is not implemented yet.")


class ResearchCreation(Cleanable):
    """
    Represents a single creation mutation research line.

    - Owns a mutation graph (CreationMutationNode instances).
    - Tracks a head node.
    - Holds a weak reference to the live creation instance.

    NOTE:
        This is scoped under a Research session for a single SpellIndex, but
        the creation_id can represent any specific instance tied to any version
        of that spell lineage.
    """

    def __init__(self, creation_id: str, *, name: Optional[str] = None) -> None:
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._creation_id: str = creation_id
        self._name: str = name or creation_id
        self._lock: RLock = RLock()

        self._creation_ref: Optional[weakref.ReferenceType[Any]] = None
        self._nodes: ConcurrentDict[str, CreationMutationNode] = ConcurrentDict()
        self._head_id: Optional[str] = None
        self._metadata: Dict[str, Any] = {}

    def cleanup(self) -> None:
        """
        Cleans up the research line and all mutation nodes.

        Idempotent.
        """
        if self._cleaned:
            return
        self._cleaned = True

        with self._lock:
            for _, node in list(self._nodes.items()):
                try:
                    node.cleanup()
                except Exception:
                    pass
            self._nodes.cleanup()
            self._nodes = None  # type: ignore[assignment]

            self._creation_ref = None
            self._head_id = None
            self._metadata.clear()
            self._metadata = {}
            self._creation_id = ""
            self._name = ""
            self._lock = None  # type: ignore[assignment]

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #
    @property
    def id(self) -> str:
        return self._id

    @property
    def creation_id(self) -> str:
        return self._creation_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def head_id(self) -> Optional[str]:
        return self._head_id

    @property
    def metadata(self) -> Dict[str, Any]:
        return dict(self._metadata)

    # ------------------------------------------------------------------ #
    # Live creation reference management
    # ------------------------------------------------------------------ #
    def attach_creation(self, creation: Any) -> None:
        """
        Attaches a live creation object to this research line via weakref.
        """
        raise NotImplementedError("ResearchCreation.attach_creation is not implemented yet.")

    def get_creation(self) -> Optional[Any]:
        """
        Returns the attached live creation object if it still exists.
        """
        raise NotImplementedError("ResearchCreation.get_creation is not implemented yet.")

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
        """
        raise NotImplementedError("ResearchCreation.begin_mutation is not implemented yet.")

    def commit_mutation(self, node: CreationMutationNode) -> None:
        """
        Commits a fully-populated CreationMutationNode into this research line
        and advances HEAD.
        """
        raise NotImplementedError("ResearchCreation.commit_mutation is not implemented yet.")

    def checkout(self, node_id: str) -> CreationMutationNode:
        """
        Sets the research line HEAD to the given node and returns it.
        """
        raise NotImplementedError("ResearchCreation.checkout is not implemented yet.")

    def get_head(self) -> Optional[CreationMutationNode]:
        """
        Returns the current HEAD node for this research line, if any.
        """
        raise NotImplementedError("ResearchCreation.get_head is not implemented yet.")

    def get_node(self, node_id: str) -> CreationMutationNode:
        """
        Retrieves a specific mutation node by id.
        """
        raise NotImplementedError("ResearchCreation.get_node is not implemented yet.")

    def list_nodes(self) -> List[CreationMutationNode]:
        """
        Returns all mutation nodes for this research line in undefined order.
        """
        raise NotImplementedError("ResearchCreation.list_nodes is not implemented yet.")


class Research(Cleanable):
    """
    Represents a single research session *anchored to one SpellIndex*.

    - `target_index` identifies the spell lineage (stable ULID).
    - `_root_version` captures the concrete version (SHA256) when this research
      session was created.
    - Owns multiple spell research lines (ResearchSpell) for that lineage.
    - Owns multiple creation research lines (ResearchCreation) for instances
      tied to that lineage.
    """

    def __init__(
            self,
            target_index: SpellIndex,
            name: str,
            *,
            level: Optional[int] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._target_index: SpellIndex = target_index
        self._root_version: Optional[str] = target_index.current  # snapshot of version at research start
        self._name: str = name
        self._level: Optional[int] = level
        self._metadata: Dict[str, Any] = metadata or {}
        self._lock: RLock = RLock()

        # keyed by research id
        self._spell_researches: ConcurrentDict[str, ResearchSpell] = ConcurrentDict()
        self._creation_researches: ConcurrentDict[str, ResearchCreation] = ConcurrentDict()

    def cleanup(self) -> None:
        """
        Cleans up the research session and all spell/creation researches.

        Idempotent.
        """
        if self._cleaned:
            return
        self._cleaned = True

        with self._lock:
            for _, research in list(self._spell_researches.items()):
                try:
                    research.cleanup()
                except Exception:
                    pass
            self._spell_researches.cleanup()
            self._spell_researches = None  # type: ignore[assignment]

            for _, research in list(self._creation_researches.items()):
                try:
                    research.cleanup()
                except Exception:
                    pass
            self._creation_researches.cleanup()
            self._creation_researches = None  # type: ignore[assignment]

            self._target_index = None  # type: ignore[assignment]
            self._root_version = None
            self._name = ""
            self._level = None
            self._metadata.clear()
            self._metadata = {}
            self._lock = None  # type: ignore[assignment]

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #
    @property
    def id(self) -> str:
        """
        Internal research id (not the SpellIndex id).
        """
        return self._id

    @property
    def target_index(self) -> SpellIndex:
        """
        The SpellIndex (stable lineage identity) this research session targets.
        """
        return self._target_index

    @property
    def root_version(self) -> Optional[str]:
        """
        Concrete version id (SHA256) that was active when this research started.
        """
        return self._root_version

    @property
    def name(self) -> str:
        return self._name

    @property
    def level(self) -> Optional[int]:
        return self._level

    @property
    def metadata(self) -> Dict[str, Any]:
        return dict(self._metadata)

    # ------------------------------------------------------------------ #
    # Spell researches
    # ------------------------------------------------------------------ #
    def start_spell_research(self, spell_id: str, *, name: Optional[str] = None) -> ResearchSpell:
        """
        Creates a new ResearchSpell for the given concrete spell id (SHA256)
        and registers it under this research session.

        The spell_id is expected to be a version belonging to this session's
        SpellIndex lineage.
        """
        raise NotImplementedError("Research.start_spell_research is not implemented yet.")

    def get_spell_research(self, research_id: str) -> ResearchSpell:
        """
        Retrieves a spell ResearchSpell by its research id.
        """
        raise NotImplementedError("Research.get_spell_research is not implemented yet.")

    def list_spell_researches(self) -> List[ResearchSpell]:
        """
        Returns all spell ResearchSpell objects in this research session.
        """
        raise NotImplementedError("Research.list_spell_researches is not implemented yet.")

    # ------------------------------------------------------------------ #
    # Creation researches
    # ------------------------------------------------------------------ #
    def start_creation_research(self, creation_id: str, *, name: Optional[str] = None) -> ResearchCreation:
        """
        Creates a new ResearchCreation for the given creation id and registers it.

        `creation_id` is typically an identifier from Creations / Conduit for a
        live object associated (directly or indirectly) with this SpellIndex.
        """
        raise NotImplementedError("Research.start_creation_research is not implemented yet.")

    def get_creation_research(self, research_id: str) -> ResearchCreation:
        """
        Retrieves a creation ResearchCreation by its research id.
        """
        raise NotImplementedError("Research.get_creation_research is not implemented yet.")

    def list_creation_researches(self) -> List[ResearchCreation]:
        """
        Returns all creation ResearchCreation objects in this research session.
        """
        raise NotImplementedError("Research.list_creation_researches is not implemented yet.")

    # ------------------------------------------------------------------ #
    # Version promotion / propagation hook
    # ------------------------------------------------------------------ #
    def promote_spell_version(
            self,
            new_spell_id: str,
            *,
            update_index: bool = True,
            propagate_to_runtime: bool = True,
            drop_legacy_creations: bool = False,
    ) -> None:
        """
        High-level orchestration hook for adopting a new spell version as the
        default for this SpellIndex.

        Intended behavior (when implemented):

          1) Update SpellIndex:
             If `update_index` is True:
               - Call `self._target_index.update(new_spell_id)` so that all
                 future resolution that goes through this SpellIndex sees the
                 new concrete version as the active default.

          2) Propagate to resolution / registries:
             If `propagate_to_runtime` is True:
               - Rebuild or adjust any cached resolution DAGs, SpellMaps, or
                 other structures that assume a specific spell version.
               - Optionally notify Aether / Spellbook / Conduit so that
                 future conjurations and contract bindings align with
                 `new_spell_id`.

          3) Handle old creations:
             Depending on `drop_legacy_creations`:
               - If True:
                   * Locate creations bound to previous spell versions for
                     this SpellIndex and dispose them, or move them into a
                     "rogue/legacy" tracking structure.
               - If False:
                   * Leave existing creations alive, but record in research
                     metadata that they are now legacy relative to the new
                     default version.

        This method does not implement any of that yet; it exists as the
        explicit "when a new spell version comes out we update the SpellIndex
        and propagate it" entrypoint so the orchestration logic has a single,
        well-defined home.
        """
        raise NotImplementedError("Research.promote_spell_version is not implemented yet.")


class MutationResearch(Cleanable):
    """
    Top-level manager for all mutation research sessions.

    Intended to live inside a Conduit (or similar) as the coordinator that:
      - Creates Research sessions anchored to specific SpellIndex instances.
      - Locates sessions for a given SpellIndex.
      - Provides convenience entrypoints to begin spell/creation mutation flows.
    """

    def __init__(self) -> None:
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: RLock = RLock()

        # Keyed by SpellIndex id (ULID string)
        self._sessions_by_index: ConcurrentDict[str, Research] = ConcurrentDict()

    def cleanup(self) -> None:
        """
        Cleans up the manager and all tracked sessions.

        Idempotent.
        """
        if self._cleaned:
            return
        self._cleaned = True

        with self._lock:
            for _, session in list(self._sessions_by_index.items()):
                try:
                    session.cleanup()
                except Exception:
                    pass
            self._sessions_by_index.cleanup()
            self._sessions_by_index = None  # type: ignore[assignment]

            self._lock = None  # type: ignore[assignment]

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #
    @property
    def id(self) -> str:
        return self._id

    # ------------------------------------------------------------------ #
    # Session management
    # ------------------------------------------------------------------ #
    def create_session(
            self,
            target_index: SpellIndex,
            *,
            name: Optional[str] = None,
            level: Optional[int] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> Research:
        """
        Creates a new Research session anchored to the given SpellIndex and
        registers it.

        The SpellIndex represents the spell lineage; this method does not
        modify `target_index.current`, it only uses it to snapshot the
        `root_version` inside the Research.

        If a session for this SpellIndex id already exists, the implementation
        may either:
          - return the existing Research, or
          - raise an error (design choice left to the implementation).
        """
        raise NotImplementedError("MutationResearch.create_session is not implemented yet.")

    def get_session_for_index(self, target_index: SpellIndex) -> Optional[Research]:
        """
        Retrieves the Research session for a given SpellIndex, if it exists.
        """
        raise NotImplementedError("MutationResearch.get_session_for_index is not implemented yet.")

    def get_session_by_index_id(self, index_id: str) -> Optional[Research]:
        """
        Retrieves the Research session by SpellIndex id (ULID string), if it exists.
        """
        raise NotImplementedError("MutationResearch.get_session_by_index_id is not implemented yet.")

    def list_sessions(self) -> List[Research]:
        """
        Returns all Research sessions managed by this object.
        """
        raise NotImplementedError("MutationResearch.list_sessions is not implemented yet.")

    def remove_session_for_index(self, target_index: SpellIndex) -> None:
        """
        Removes and cleans up the Research session associated with the given
        SpellIndex, if it exists.
        """
        raise NotImplementedError("MutationResearch.remove_session_for_index is not implemented yet.")

    # ------------------------------------------------------------------ #
    # Convenience entrypoints
    # ------------------------------------------------------------------ #
    def begin_spell_mutation(
            self,
            target_index: SpellIndex,
            *,
            research_name: Optional[str] = None,
            message: Optional[str] = None,
            tags: Optional[List[str]] = None,
    ) -> SpellMutationNode:
        """
        High-level entrypoint for starting a spell mutation for a given SpellIndex.

        Intended behavior (when implemented):

          - Ensure a Research session exists for `target_index`:
              * If not, create one via `create_session(...)` with an appropriate name.
          - Resolve (or create) a ResearchSpell line within that Research using
            the current concrete version id:
              * `current_id = target_index.current`
              * `research.start_spell_research(current_id, name=...)`
          - Begin a new SpellMutationNode on that ResearchSpell:
              * `research_spell.begin_mutation(message=message, tags=tags)`
          - Return the newly created SpellMutationNode to the caller, who can
            then populate its structure and commit it.

        This is the "start working on a new spell version for this SpellIndex"
        helper that allows an agent to quickly spin up mutation work.
        """
        raise NotImplementedError("MutationResearch.begin_spell_mutation is not implemented yet.")

    def begin_creation_mutation(
            self,
            target_index: SpellIndex,
            creation_id: str,
            *,
            research_name: Optional[str] = None,
            message: Optional[str] = None,
            tags: Optional[List[str]] = None,
    ) -> CreationMutationNode:
        """
        High-level entrypoint for starting a creation mutation tied to a
        particular SpellIndex and a specific creation id.

        Intended behavior (when implemented):

          - Ensure a Research session exists for `target_index` (as above).
          - Resolve (or create) a ResearchCreation line within that Research:
              * `research.start_creation_research(creation_id, name=...)`
          - Begin a new CreationMutationNode on that ResearchCreation:
              * `research_creation.begin_mutation(message=message, tags=tags)`
          - Return the newly created CreationMutationNode to the caller for
            snapshot population and commit.
        """
        raise NotImplementedError("MutationResearch.begin_creation_mutation is not implemented yet.")
