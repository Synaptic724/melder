"""Step 1 of the aether_conduit_lookup_api lane: ConduitWard snapshot walk and ConduitCloud.list_conduits.

Usage: python apply_ward_and_cloud.py <tree root>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edit_util import replace_block

ROOT = sys.argv[1]
WARD = os.path.join(ROOT, "src/melder/aether/conduit/conduit_ward/conduit_ward.py")
CLOUD = os.path.join(ROOT, "src/melder/aether/aetheric_frame/conduit_cloud.py")

WARD_OLD = '''    def _get_lesser_conduit(self, conduit_id: str) -> Optional[Conduit]:
        """
        Internal

        Recursively searches for a lesser conduit with the given ID within this conduit's hierarchy.

        Args:
            conduit_id (str): The ID of the conduit to retrieve.

        Returns:
            Optional[Conduit]: The matched conduit if found, else None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        for conduit in self._lesser_conduits.values():
            if conduit._id == conduit_id:
                return conduit
            ward: Optional[ConduitWard] = conduit._conduit_ward
            if ward is not None:
                result = ward._get_lesser_conduit(conduit_id)
                if result is not None:
                    return result
        return None
'''

WARD_NEW = '''    def _get_lesser_conduit(self, conduit_id: str) -> Optional[Conduit]:
        """
        Internal

        Recursively searches for a lesser conduit with the given ID within this conduit's hierarchy.

        Purpose:
            Resolve a live lesser scope (named or anonymous, at any depth) from its conduit id. Used by
            `Conduit.get_lesser_conduit` and, root by root, by `Aether.get_conduit_by_id`.

        Contract:
            - Depth-first over attached children: returns the first child whose `_id` matches, else searches
              that child's own ward, else moves on. Returns None when no attached descendant matches.
            - Walks a SNAPSHOT of `_lesser_conduits` at every level (`dict.copy()`, atomic on the
              free-threaded build), never the live dict. Links write this dict under this ward's lock while a
              returning child pops itself from it under the CHILD's lock (`_detach_for_pool`), so no single
              lock gives a stable view; iterating the live dict could raise "dictionary changed size during
              iteration".
            - Skips a child whose `_conduit_ward` was deleted by hard teardown after the snapshot, and a child
              whose ward is None (a leaf); neither is searched further.
            - Read-only: takes no lock, grants no lease and changes no state. The returned conduit is borrowed.
            - A child attached or detached while the walk runs may or may not be seen; the walk never raises
              for it. A pooled idle shell is detached from its parent, so it never matches.

        Threading:
            Safe to call from any thread without holding a ward lock.

        Args:
            conduit_id (str): The ID of the conduit to retrieve.

        Returns:
            Optional[Conduit]: The matched conduit if found, else None.

        Raises:
            None. A cleaned ward has an empty `_lesser_conduits` and returns None.
        """
        for conduit in self._lesser_conduits.copy().values():
            if conduit._id == conduit_id:
                return conduit
            try:
                ward: Optional[ConduitWard] = conduit._conduit_ward
            except AttributeError:
                # Hard teardown deleted this child's ward after the snapshot; its subtree went with it.
                continue
            if ward is not None:
                result = ward._get_lesser_conduit(conduit_id)
                if result is not None:
                    return result
        return None
'''

CLOUD_OLD = '''    def list_cloud_names(self) -> Tuple[str, ...]:
'''

CLOUD_NEW = '''    def list_conduits(self) -> Tuple[Conduit, ...]:
        """
        Return the named normal-root and lesser-scope conduits registered in this frame.

        Purpose:
            Hand callers the conduit objects behind the named directory, so discovery does not need one
            `get_conduit_by_name` call per listed name.

        Contract:
            - Covers the same NAMED scopes as `list_conduit_names()` / `list_conduit_ids()`: every named normal
              root and every active named lesser, at any depth. Anonymous lessers, idle pooled shells and
              scopes still being constructed are absent.
            - Returns a TUPLE SNAPSHOT taken under the lock; it goes stale the moment a named scope is
              registered, retired or returned to its pool, and a listed scope may be cleaned afterwards.
            - The conduits are borrowed: listing grants no lease and transfers no ownership. Order follows
              registration but is not a contract; pair by `name` / `id`, not by position.

        Threading:
            Reads under `self._lock`, so the result is a coherent snapshot rather than a torn read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the cloud has been cleaned.

        Returns:
            Tuple[Conduit, ...]: Snapshot of the named conduits.
        """
        self.check_cleaned()
        with self._lock:
            return tuple(self._named_conduits.values())

    def list_cloud_names(self) -> Tuple[str, ...]:
'''

print("ward:", replace_block(WARD, WARD_OLD, WARD_NEW))
print("cloud:", replace_block(CLOUD, CLOUD_OLD, CLOUD_NEW))
