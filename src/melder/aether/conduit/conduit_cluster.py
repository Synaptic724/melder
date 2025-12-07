import threading
from typing import Dict, Set

from melder.spellbook.bind.spell_index import SpellIndex
from melder.utilities.general_base.cleanable import Cleanable


class ConduitCluster(Cleanable):
    """
    Encapsulates cluster membership and shared-spell registry.

    - members: set of conduit_ids.
    - shared_spells: owner_conduit_id -> set[SpellIndex] (roots to auto-share).
    - auto_link_dependencies: when True, sharing pulls dependency closure.
    """

    __slots__ = (
        "_lock",
        "_name",
        "members",
        "shared_spells",
        "auto_link_dependencies",
        "_cleaned",
    )

    def __init__(self, name: str, auto_link_dependencies: bool = True):
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._name: str = name
        self.members: Set[str] = set()
        self.shared_spells: Dict[str, Set[SpellIndex]] = {}
        self.auto_link_dependencies: bool = auto_link_dependencies

    def cleanup(self):
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            if self.members is not None:
                self.members.clear()
            if self.shared_spells is not None:
                for v in self.shared_spells.values():
                    try:
                        v.clear()
                    except Exception:
                        pass
                self.shared_spells.clear()
            self.auto_link_dependencies = None
            self._name = None
            self._cleaned = True
        self._lock = None

    def add_member(self, conduit_id: str) -> None:
        with self._lock:
            self.members.add(conduit_id)

    def remove_member(self, conduit_id: str) -> None:
        with self._lock:
            self.members.discard(conduit_id)
            self.shared_spells.pop(conduit_id, None)

    def add_shared_spell(self, owner_id: str, spell_index: SpellIndex) -> None:
        with self._lock:
            bucket = self.shared_spells.setdefault(owner_id, set())
            bucket.add(spell_index)

    def remove_shared_spell(self, owner_id: str, spell_index: SpellIndex) -> None:
        with self._lock:
            bucket = self.shared_spells.get(owner_id)
            if bucket is None:
                return
            bucket.discard(spell_index)
            if not bucket:
                self.shared_spells.pop(owner_id, None)

    def get_shared_spells(self) -> Dict[str, Set[SpellIndex]]:
        with self._lock:
            return {k: set(v) for k, v in self.shared_spells.items()}

    def get_members(self) -> Set[str]:
        with self._lock:
            return set(self.members)
