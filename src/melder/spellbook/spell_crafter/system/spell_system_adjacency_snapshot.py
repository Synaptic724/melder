from typing import Dict, Iterable, Optional, Set
# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class SpellSystemAdjacencySnapshot(Cleanable):
    """
    Frame-wide structural view of SpellSystemStates.

    This is a Phase 5 helper that captures *only* the version-id level
    adjacency:

        * dependencies:  spell_id -> {spell_id, ...}
        * reverse_dependencies: spell_id -> {spell_id, ...}
        * all_spell_ids: all spell_ids we know about in this frame
        * root_spell_ids: spells with **no incoming edges**

    Notes
    -----
    * All spell_ids are **version IDs** (spell.spell_index.current).
    * This snapshot is read-only from the caller's perspective; it is
      built once from SpellSystemStates and then treated as immutable
      structural metadata.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_dependencies",
        "_reverse_dependencies",
        "_all_spell_ids",
        "_root_spell_ids",
        "_topologies",
    ]

    def __init__(
            self,
            dependencies: Dict[str, Set[str]],
            reverse_dependencies: Dict[str, Set[str]],
            all_spell_ids: Set[str],
            root_spell_ids: Set[str],
            topologies: Optional[Dict[str, 'SpellLocalTopology']] = None,
    ) -> None:
        super().__init__()
        if dependencies is None:
            raise ValueError("dependencies must not be None.")
        if reverse_dependencies is None:
            raise ValueError("reverse_dependencies must not be None.")
        if all_spell_ids is None:
            raise ValueError("all_spell_ids must not be None.")
        if root_spell_ids is None:
            raise ValueError("root_spell_ids must not be None.")

        self._dependencies: Dict[str, Set[str]] = dependencies
        self._reverse_dependencies: Dict[str, Set[str]] = reverse_dependencies
        self._all_spell_ids: Set[str] = all_spell_ids
        self._root_spell_ids: Set[str] = root_spell_ids
        # SpellLocalTopology references (owned by SpellSystemStates).
        self._topologies: Dict[str, 'SpellLocalTopology'] = topologies or {}


    def cleanup(self) -> None:
        if self._cleaned:
            return
        self._cleaned = True

        if self._dependencies is not None:
            for dependency_set in self._dependencies.values():
                dependency_set.clear()
            self._dependencies.clear()
            self._dependencies = None

        if self._reverse_dependencies is not None:
            for parent_set in self._reverse_dependencies.values():
                parent_set.clear()
            self._reverse_dependencies.clear()
            self._reverse_dependencies = None

        if self._all_spell_ids is not None:
            self._all_spell_ids.clear()
            self._all_spell_ids = None

        if self._root_spell_ids is not None:
            self._root_spell_ids.clear()
            self._root_spell_ids = None

        if self._topologies is not None:
            self._topologies.clear()
            self._topologies = None

    # ------------------------------------------------------------------
    # Read-only accessors
    # ------------------------------------------------------------------
    @property
    def dependencies(self) -> Dict[str, Set[str]]:
        """
        Outgoing edges for each spell version_id:

            spell_id -> { dependency_spell_id, ... }

        The returned dictionary and sets should be treated as read-only
        by callers. Callers may copy if they need to mutate.
        """
        return self._dependencies

    @property
    def reverse_dependencies(self) -> Dict[str, Set[str]]:
        """
        Incoming edges for each spell version_id:

            spell_id -> { parent_spell_id, ... }

        A spell_id that does not appear as a key in this mapping has
        no known incoming edges.
        """
        return self._reverse_dependencies

    @property
    def all_spell_ids(self) -> Set[str]:
        """
        All known spell version_ids participating in this frame.
        """
        return self._all_spell_ids

    @property
    def root_spell_ids(self) -> Set[str]:
        """
        Structural roots for this frame.

        By definition:

            root_spell_ids = all_spell_ids - { any spell_id that appears
                                               as a dependency somewhere }

        These are spells that **nothing else depends on**. They are the
        natural root candidates for RootResolutionBlueprints in Phase 5.
        """
        return self._root_spell_ids

    @property
    def topologies(self) -> Dict[str, 'SpellLocalTopology']:
        """
        Snapshot of local constructor topologies keyed by spell_id.

        The contained topologies are owned by SpellSystemStates; callers
        must not mutate or cleanup them from this snapshot.
        """
        return self._topologies

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    def get_dependencies_for(self, spell_id: str) -> Set[str]:
        """
        Returns the outgoing dependencies for the given spell_id.

        If the spell_id is unknown, an empty set is returned.
        """
        deps = self._dependencies.get(spell_id)
        if deps is None:
            return set()
        return set(deps)

    def get_reverse_dependencies_for(self, spell_id: str) -> Set[str]:
        """
        Returns the incoming dependencies (parents) for the given spell_id.

        If the spell_id has no known parents, an empty set is returned.
        """
        parents = self._reverse_dependencies.get(spell_id)
        if parents is None:
            return set()
        return set(parents)
