from threading import RLock
from typing import Any, Dict, List, Optional, Set
# Melder imports
from melder.mutation_research.research.creation.creation_research import ResearchCreation
from melder.mutation_research.research.spell.spell_research import ResearchSpell
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class Research(Cleanable):
    """
    Represents a single research session anchored to one SpellIndex (spell lineage).

    - **Target:** `target_index` identifies the stable spell lineage (ULID).
    - **Root Version:** `_root_version` captures the concrete version (SHA256) when this session started.
    - **Contents:** Owns multiple spell research lines (`ResearchSpell`) and creation research lines (`ResearchCreation`) associated with that lineage.
    """
    __melder_internal__ = _mrg.sentinel
    def __init__(
            self,
            target_index: SpellIndex,
            name: str,
            *,
            level: Optional[int] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initializes a Research session.

        Args:
            target_index (SpellIndex): The SpellIndex (stable lineage identity) this research session targets.
            name (str): Human-friendly name for this research session.
            level (Optional[int], optional): Optional "depth" / difficulty / AI autonomy level for this session.
            metadata (Optional[Dict[str, Any]], optional): Arbitrary metadata attached to the session.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._target_index: SpellIndex = target_index
        # snapshot of version at research start
        self._root_version: Optional[str] = target_index.current
        self._name: str = name
        self._level: Optional[int] = level
        self._metadata: Dict[str, Any] = metadata or {}
        self._lock: RLock = RLock()

        # keyed by research id
        self._spell_researches: Dict[str, ResearchSpell] = {}
        self._creation_researches: Dict[str, ResearchCreation] = {}

        # Lightweight indices for quick membership checks / debugging.
        self._spell_research_ids: Set[str] = set()
        self._creation_research_ids: Set[str] = set()

    def cleanup(self) -> None:
        """
        Cleans up the research session and all contained spell/creation research lines.

        This method is idempotent.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            # Spell researches
            if self._spell_researches is not None:
                for _, spell_research in list(self._spell_researches.items()):
                    try:
                        spell_research.cleanup()
                    except Exception:
                        pass
                try:
                    self._spell_researches.clear()
                except Exception:
                    pass

            if self._spell_research_ids is not None:
                try:
                    self._spell_research_ids.clear()
                except Exception:
                    pass

            # Creation researches
            if self._creation_researches is not None:
                for _, creation_research in list(self._creation_researches.items()):
                    try:
                        creation_research.cleanup()
                    except Exception:
                        pass
                try:
                    self._creation_researches.clear()
                except Exception:
                    pass

            if self._creation_research_ids is not None:
                try:
                    self._creation_research_ids.clear()
                except Exception:
                    pass
            self._metadata.clear()

            del self._spell_researches
            del self._spell_research_ids
            del self._creation_researches
            del self._creation_research_ids
            del self._target_index
            del self._root_version
            del self._level
            del self._metadata
        del self._lock

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #
    @property
    def id(self) -> str:
        """
        Returns the internal research id (ULID string).

        Returns:
            str: The session's unique ID.
        """
        return self._id

    @property
    def target_index(self) -> SpellIndex:
        """
        Returns the SpellIndex (stable lineage identity) this research session targets.

        Returns:
            SpellIndex: The target SpellIndex.
        """
        return self._target_index

    @property
    def root_version(self) -> Optional[str]:
        """
        Returns the concrete version id (SHA256) that was active when this research started.

        Returns:
            Optional[str]: The root spell version ID.
        """
        return self._root_version

    @property
    def name(self) -> str:
        """
        Returns the human-friendly name for this research session.

        Returns:
            str: The session's name.
        """
        return self._name

    @property
    def level(self) -> Optional[int]:
        """
        Returns the optional "depth" / difficulty / AI autonomy level for this session.

        Returns:
            Optional[int]: The session level.
        """
        return self._level

    @property
    def metadata(self) -> Dict[str, Any]:
        """
        Returns a shallow copy of metadata attached to this research session.

        Returns:
            Dict[str, Any]: A copy of the session's metadata.
        """
        return dict(self._metadata)

    # ------------------------------------------------------------------ #
    # Spell researches
    # ------------------------------------------------------------------ #
    def start_spell_research(self, spell_id: str, *, name: Optional[str] = None) -> ResearchSpell:
        """
        Resolves or creates a `ResearchSpell` line for the given concrete spell id (SHA256).

        If a `ResearchSpell` already exists for the same `spell_id` and name, it is returned; otherwise a new one is created and registered.

        Args:
            spell_id (str): Concrete spell version id. Expected to belong to this session's SpellIndex lineage.
            name (Optional[str], optional): Optional name for the research line.

        Returns:
            ResearchSpell: The resolved or newly created research line.

        Raises:
            ValueError: If `spell_id` is empty.
            RuntimeError: If the `Research` session has been cleaned.
        """
        self.check_cleaned()
        if not spell_id:
            raise ValueError("spell_id cannot be empty")

        with self._lock:
            if self._spell_researches is None or self._spell_research_ids is None:
                raise RuntimeError("Research has been cleaned.")

            # Try to find an existing line for the same spell version.
            for research in self._spell_researches.values():
                if research.spell_id == spell_id and (name is None or research.name == name):
                    return research

            # Otherwise create a new research line.
            line_name = name or f"{self._name}:spell:{spell_id}"
            research = ResearchSpell(spell_id=spell_id, name=line_name)
            self._spell_researches[research.id] = research
            self._spell_research_ids.add(research.id)
            return research

    def get_spell_research(self, research_id: str) -> ResearchSpell:
        """
        Retrieves a spell `ResearchSpell` by its research id.

        Args:
            research_id (str): The ID of the research line to retrieve.

        Returns:
            ResearchSpell: The requested research line.

        Raises:
            ValueError: If `research_id` is empty.
            RuntimeError: If the `Research` session has been cleaned.
            KeyError: If no such research exists.
        """
        self.check_cleaned()
        if not research_id:
            raise ValueError("research_id cannot be empty")

        with self._lock:
            if self._spell_researches is None:
                raise RuntimeError("Research has been cleaned.")
            research = self._spell_researches.get(research_id)
            if research is None:
                raise KeyError(f"Unknown spell research id: {research_id!r}")
            return research

    def list_spell_researches(self) -> List[ResearchSpell]:
        """
        Returns all spell `ResearchSpell` objects in this research session.

        Returns:
            List[ResearchSpell]: A list of all spell research lines.
        """
        self.check_cleaned()
        with self._lock:
            if self._spell_researches is None:
                return []
            return list(self._spell_researches.values())

    # ------------------------------------------------------------------ #
    # Creation researches
    # ------------------------------------------------------------------ #
    def start_creation_research(self, creation_id: str, *, name: Optional[str] = None) -> ResearchCreation:
        """
        Resolves or creates a `ResearchCreation` line for the given creation id.

        `creation_id` is typically an identifier for a live object instance tied to this SpellIndex's lineage.

        Args:
            creation_id (str): The identifier for the live creation object.
            name (Optional[str], optional): Optional name for the research line.

        Returns:
            ResearchCreation: The resolved or newly created research line.

        Raises:
            ValueError: If `creation_id` is empty.
            RuntimeError: If the `Research` session has been cleaned.
        """
        self.check_cleaned()
        if not creation_id:
            raise ValueError("creation_id cannot be empty")

        with self._lock:
            if self._creation_researches is None or self._creation_research_ids is None:
                raise RuntimeError("Research has been cleaned.")

            for research in self._creation_researches.values():
                if research.creation_id == creation_id and (name is None or research.name == name):
                    return research

            line_name = name or f"{self._name}:creation:{creation_id}"
            research = ResearchCreation(creation_id=creation_id, name=line_name)
            self._creation_researches[research.id] = research
            self._creation_research_ids.add(research.id)
            return research

    def get_creation_research(self, research_id: str) -> ResearchCreation:
        """
        Retrieves a creation `ResearchCreation` by its research id.

        Args:
            research_id (str): The ID of the research line to retrieve.

        Returns:
            ResearchCreation: The requested research line.

        Raises:
            ValueError: If `research_id` is empty.
            RuntimeError: If the `Research` session has been cleaned.
            KeyError: If the research id is unknown.
        """
        self.check_cleaned()
        if not research_id:
            raise ValueError("research_id cannot be empty")

        with self._lock:
            if self._creation_researches is None:
                raise RuntimeError("Research has been cleaned.")

            research = self._creation_researches.get(research_id)
            if research is None:
                raise KeyError(f"Unknown creation research id: {research_id!r}")
            return research

    def list_creation_researches(self) -> List[ResearchCreation]:
        """
        Returns all creation `ResearchCreation` objects in this research session.

        Returns:
            List[ResearchCreation]: A list of all creation research lines.
        """
        self.check_cleaned()
        with self._lock:
            if self._creation_researches is None:
                return []
            return list(self._creation_researches.values())

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
        High-level orchestration hook for adopting a new spell version as the default for this SpellIndex.

        This method:
          - Records the promotion event in metadata.
          - Updates this research session's `root_version`.
          - Optionally attempts to update the `SpellIndex.current` version via its public API.

        The specified behaviors (runtime propagation, creation disposal) are hooks left for the surrounding systems to implement.

        Args:
            new_spell_id (str): The concrete version id (SHA256) to promote.
            update_index (bool, optional): If True, attempts to update the `SpellIndex.current` property. Defaults to True.
            propagate_to_runtime (bool, optional): Flag indicating intent to push the new version to live instances. Defaults to True.
            drop_legacy_creations (bool, optional): Flag indicating intent to dispose of older live instances. Defaults to False.

        Raises:
            ValueError: If `new_spell_id` is empty.
            RuntimeError: If the `Research` session has been cleaned.
        """
        self.check_cleaned()
        if not new_spell_id:
            raise ValueError("new_spell_id cannot be empty")

        with self._lock:
            if self._target_index is None:
                raise RuntimeError("Research has been cleaned and no longer has a target index.")

            # 1) Update SpellIndex
            updated = False
            if update_index:
                index = self._target_index

                if hasattr(index, "update"):
                    try:
                        index.update(new_spell_id)
                        updated = True
                    except Exception:
                        updated = False

                if not updated and hasattr(index, "current"):
                    try:
                        setattr(index, "current", new_spell_id)
                        updated = True
                    except Exception:
                        updated = False

            # Track outcome for debugging/agents even when the index update was
            # intentionally skipped.
            promotions = self._metadata.setdefault("promotions", [])
            promotions.append(
                {
                    "new_spell_id": new_spell_id,
                    "update_index": update_index,
                    "propagate_to_runtime": propagate_to_runtime,
                    "drop_legacy_creations": drop_legacy_creations,
                    "index_update_success": updated,
                }
            )

            # Update local root_version snapshot
            self._root_version = new_spell_id
