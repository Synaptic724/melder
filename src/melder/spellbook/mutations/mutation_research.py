from threading import RLock
from typing import Any, Dict, List, Optional
# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.mutations.research.research import Research
from melder.utilities.interfaces import IAethericFrame
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

# TODO(MutationResearch): Implement the real mutation promotion contract here.
#
# Required contract:
# - SpellIndex.id = stable lineage identity.
# - SpellIndex.current = active concrete spell version id.
# - Spell.spell_id = physical SHA256-backed identity of one specific Spell
#   object.
#
# Do NOT implement mutation as "rewrite spell.spell_id on the existing Spell
# object." A promoted mutation should behave like a new concrete spell version,
# not an in-place identity rewrite.
#
# The likely implementation shape we need is:
# 1. Build a brand new Spell object for the mutated version.
#    - New spell gets its own new spell_id/fingerprint.
#    - New spell keeps the existing SpellIndex lineage object.
#    - New spell gets fresh profiles/runtime artifacts as needed.
# 2. Register that new Spell object into the owning Spellbook under the same
#    lineage.
#    - Replace the active entry in Spellbook._spells[spell_index].
#    - Update Spellbook._lookup_spells for the same logical spell key.
#    - Update Spellbook._spells_by_id / _spell_id_pool from old spell_id to new
#      spell_id.
#    - Decide contracted-spell behavior explicitly instead of assuming the same
#      object slides forward.
# 3. Advance SpellIndex.current to the new spell_id only after the new Spell is
#    fully registered.
#    - SpellIndex.current should become the pointer to the promoted version.
#    - Historical spell ids should remain in SpellIndex._versions.
# 4. Refresh frame/runtime state for the new active version.
#    - SpellSystemStates current_spell_id must move to the new version.
#    - Any cached crafter / resolution / execution-plan artifacts tied to the
#      old Spell object must not be silently reused unless explicitly valid.
#    - Ownership stamping for the new Spell must be reapplied if the Spell is
#      already conduit-owned.
# 5. Update Nexus canonical state as a promotion, not an in-place rewrite.
#    - Remove old SpellRecord keyed by (spellbook_id, old_spell_id).
#    - Publish new SpellRecord keyed by (spellbook_id, new_spell_id).
#    - Keep lineage_id stable across the swap.
# 6. Define rollback semantics.
#    - If registration/promotion fails partway through, the old Spell must stay
#      active and SpellIndex.current must not move.
#
# Open design questions that still need explicit answers:
# - Are contracted spells promoted to new Spell objects independently, or do
#   they rebind to the newly promoted owner spell object?
# - Do existing live creations remain bound to the old version, get invalidated,
#   or migrate under an explicit compatibility rule?
# - Which phase pipeline must rerun before a promoted version is considered
#   publishable / meldable?
#
# Until this contract exists, keep mutation continuity logic provisional and do
# not assume spell.spell_id must track SpellIndex.current by mutating the old
# Spell object in place.

class MutationResearch(Cleanable):
    """
    Top-level manager for all mutation research sessions within a Conduit or coordinating entity.

    - **Role:** Coordinates and tracks `Research` sessions anchored to specific spell lineages (`SpellIndex`).
    - **Entrypoints:** Provides convenience methods to start new mutation flows for spells or creations.
    """
    __melder_internal__ = _mrg.sentinel
    def __init__(self, aetheric_frame: IAethericFrame) -> None:
        """
        Initializes the MutationResearch manager.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: RLock = RLock()
        self._aetheric_frame = aetheric_frame

        # Keyed by SpellIndex id (ULID string)
        self._sessions_by_index: Dict[str, Research] = {}

    def cleanup(self) -> None:
        """
        Cleans up the manager and all tracked `Research` sessions.

        This method is idempotent.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._sessions_by_index is not None:
                for _, session in list(self._sessions_by_index.items()):
                    try:
                        session.cleanup()
                    except Exception:
                        pass
                try:
                    self._sessions_by_index.clear()
                except Exception:
                    pass
                self._sessions_by_index = None
            self._aetheric_frame = None

        self._lock = None

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #
    @property
    def id(self) -> str:
        """
        Returns the ULID identifier for this manager instance.

        Returns:
            str: The manager's unique ID.
        """
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
        Creates a new `Research` session anchored to the given SpellIndex and registers it.

        If a session for this SpellIndex id already exists, the existing one is returned.

        Args:
            target_index (SpellIndex): The spell lineage to anchor the session to.
            name (Optional[str], optional): Human-friendly name for the session.
            level (Optional[int], optional): Optional level/difficulty for the session.
            metadata (Optional[Dict[str, Any]], optional): Arbitrary metadata.

        Returns:
            Research: The resolved or newly created Research session.

        Raises:
            ValueError: If `target_index` is None or lacks a valid 'id' attribute.
            RuntimeError: If the `MutationResearch` manager has been cleaned.
        """
        self.check_cleaned()
        if target_index is None:
            raise ValueError("target_index cannot be None")

        index_id = getattr(target_index, "id", None)
        if not index_id:
            raise ValueError("SpellIndex is expected to expose a non-empty 'id' attribute.")

        session_name = name or f"Research:{index_id}"

        with self._lock:
            if self._sessions_by_index is None:
                raise RuntimeError("MutationResearch has been cleaned.")

            existing = self._sessions_by_index.get(index_id)
            if existing is not None:
                return existing

            session = Research(target_index=target_index, name=session_name, level=level, metadata=metadata)
            self._sessions_by_index[index_id] = session
            return session

    def get_session_for_index(self, target_index: SpellIndex) -> Optional[Research]:
        """
        Retrieves the `Research` session for a given SpellIndex, if it exists.

        Args:
            target_index (SpellIndex): The spell lineage to search for.

        Returns:
            Optional[Research]: The Research session, or None.
        """
        self.check_cleaned()
        if target_index is None:
            return None

        index_id = getattr(target_index, "id", None)
        if not index_id:
            return None

        with self._lock:
            if self._sessions_by_index is None:
                return None
            return self._sessions_by_index.get(index_id)

    def get_session_by_index_id(self, index_id: str) -> Optional[Research]:
        """
        Retrieves the `Research` session by SpellIndex id (ULID string), if it exists.

        Args:
            index_id (str): The ID of the SpellIndex.

        Returns:
            Optional[Research]: The Research session, or None.
        """
        self.check_cleaned()
        if not index_id:
            return None

        with self._lock:
            if self._sessions_by_index is None:
                return None
            return self._sessions_by_index.get(index_id)

    def list_sessions(self) -> List[Research]:
        """
        Returns all `Research` sessions managed by this object.

        Returns:
            List[Research]: A list of all Research sessions.
        """
        self.check_cleaned()
        with self._lock:
            if self._sessions_by_index is None:
                return []
            return list(self._sessions_by_index.values())

    def remove_session_for_index(self, target_index: SpellIndex) -> None:
        """
        Removes and cleans up the `Research` session associated with the given SpellIndex, if it exists.

        Args:
            target_index (SpellIndex): The spell lineage whose session should be removed.
        """
        self.check_cleaned()
        if target_index is None:
            return

        index_id = getattr(target_index, "id", None)
        if not index_id:
            return

        with self._lock:
            if self._sessions_by_index is None:
                return

            session = self._sessions_by_index.pop(index_id, None)

        if session is not None:
            try:
                session.cleanup()
            except Exception:
                pass

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
    ) -> 'SpellMutationNode':
        """
        High-level entrypoint for starting a spell mutation for a given SpellIndex.

        Behavior:
          - Ensures a Research session exists for `target_index`.
          - Resolves (or creates) a `ResearchSpell` line for the current spell version of that index.
          - Begins a new `SpellMutationNode` on that `ResearchSpell` and returns it.

        Args:
            target_index (SpellIndex): The spell lineage to target.
            research_name (Optional[str], optional): Optional name for the new research line/session.
            message (Optional[str], optional): Message for the new mutation node.
            tags (Optional[List[str]], optional): Tags for the new mutation node.

        Returns:
            SpellMutationNode: The newly created (uncommitted) mutation node.

        Raises:
            ValueError: If `target_index` is None.
            RuntimeError: If the `SpellIndex.current` version is not set.
        """
        self.check_cleaned()
        if target_index is None:
            raise ValueError("target_index cannot be None")

        # Resolve/create session
        session = self.get_session_for_index(target_index)
        if session is None:
            session = self.create_session(target_index, name=research_name)

        current_id = getattr(target_index, "current", None)
        if not current_id:
            raise RuntimeError("SpellIndex.current is not set; cannot begin spell mutation.")

        # Resolve or create a spell research line for this concrete version.
        spell_research: Optional['ResearchSpell'] = None
        for candidate in session.list_spell_researches():
            if candidate.spell_id == current_id:
                spell_research = candidate
                break

        if spell_research is None:
            spell_research = session.start_spell_research(current_id, name=research_name)

        return spell_research.begin_mutation(message=message, tags=tags)

    def begin_creation_mutation(
            self,
            target_index: SpellIndex,
            creation_id: str,
            *,
            research_name: Optional[str] = None,
            message: Optional[str] = None,
            tags: Optional[List[str]] = None,
    ) -> 'CreationMutationNode':
        """
        High-level entrypoint for starting a creation mutation tied to a particular SpellIndex and a specific creation id.

        Behavior:
          - Ensures a Research session exists for `target_index`.
          - Resolves (or creates) a `ResearchCreation` line for `creation_id`.
          - Begins a new `CreationMutationNode` on that line and returns it.

        Args:
            target_index (SpellIndex): The spell lineage to associate with the mutation.
            creation_id (str): The identifier for the live creation instance to mutate.
            research_name (Optional[str], optional): Optional name for the new research line/session.
            message (Optional[str], optional): Message for the new mutation node.
            tags (Optional[List[str]], optional): Tags for the new mutation node.

        Returns:
            CreationMutationNode: The newly created (uncommitted) mutation node.

        Raises:
            ValueError: If `target_index` or `creation_id` is empty.
        """
        self.check_cleaned()
        if target_index is None:
            raise ValueError("target_index cannot be None")
        if not creation_id:
            raise ValueError("creation_id cannot be empty")

        # Resolve/create session
        session = self.get_session_for_index(target_index)
        if session is None:
            session = self.create_session(target_index, name=research_name)

        # Resolve or create a creation research line.
        creation_research: Optional['ResearchCreation'] = None
        for candidate in session.list_creation_researches():
            if candidate.creation_id == creation_id:
                creation_research = candidate
                break

        if creation_research is None:
            creation_research = session.start_creation_research(creation_id, name=research_name)

        return creation_research.begin_mutation(message=message, tags=tags)
