import json
import os
import threading
from pathlib import Path
from typing import Dict, List

from melder.utilities.general_base.cleanable import Cleanable


class CrystallizerCache(Cleanable):
    """
    Local filesystem cache for persisted checkpoint cached-items.

    Purpose:
        The crystallizer-side sibling of the conjure cache: checkpoint
        cached-items (`PersistenceCrystal.to_cached_item()` payloads) store
        as one JSON file per checkpoint ULID under the shared melder cache
        root at `__melder_cache__/__crystallizer_cache__`. This is the
        BUILT-IN local durability lane; host-owned storage (DB adapters)
        is the persistence epic's adapter contract and layers separately.

    Contract:
        - The cache root always resolves under the melder package root
          (mirrors `AethericFrameConfiguration.resolve_system_cache_root_path`
          semantics): never against the caller's working directory.
        - Writes are ATOMIC (tmp file + os.replace): a reader never sees a
          torn cached-item; re-storing an id overwrites its previous item.
        - Payloads are JSON round-trip safe by construction
          (`to_cached_item` emits plain values; `from_cached_item`
          normalizes list/tuple shapes back).

    Threading:
        One instance RLock serializes storage operations.

    Lifecycle:
        Owned by exactly one PersistenceSystem. `cleanup()` releases owned
        fields (lock last); idempotent.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]

    def __init__(self) -> None:
        """
        Initialize the cache surface.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Release owned fields and mark the cache cleaned.

        Contract:
            - Idempotent; del posture; lock deleted last.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._lock

    @staticmethod
    def resolve_cache_root_path() -> Path:
        """
        Resolve the crystallizer-cache root under the shared cache root.

        Contract:
            - `<melder package root>/__melder_cache__/__crystallizer_cache__`
              for both installed and source-checkout runs.

        Returns:
            Path: Absolute crystallizer-cache root.
        """
        melder_package_root = Path(__file__).resolve().parent.parent.parent
        return (
            melder_package_root / "__melder_cache__" / "__crystallizer_cache__"
        )

    def store_cached_item(
            self,
            checkpoint_id: str,
            cached_item: Dict[str, object],
    ) -> None:
        """
        Store one checkpoint cached-item into the crystallizer cache.

        Contract:
            - Atomic: the payload lands via tmp-file + os.replace, so a
              concurrent reader sees the previous item or the new one,
              never a torn file.
            - Re-storing an id overwrites its previous cached-item.

        Args:
            checkpoint_id:
                ULID identity of the sealed checkpoint.
            cached_item:
                Payload produced by `PersistenceCrystal.to_cached_item()`.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the cache has been cleaned.
            ValueError:
                If `checkpoint_id` is empty.
        """
        self.check_cleaned()
        if not checkpoint_id:
            raise ValueError(
                "store_cached_item requires a non-empty checkpoint_id."
            )
        with self._lock:
            # Profile-scoped layout (owner ruling): checkpoints live
            # under their profile's folder inside the cache root -
            # "make a profile name and put checkpoints under it".
            profile_name = str(cached_item.get("profile_name", "default"))
            profile_directory = self.resolve_cache_root_path() / profile_name
            profile_directory.mkdir(parents=True, exist_ok=True)
            final_path = profile_directory / "{0}.json".format(checkpoint_id)
            tmp_path = profile_directory / "{0}.json.tmp".format(
                checkpoint_id
            )
            tmp_path.write_text(
                json.dumps(cached_item, sort_keys=True), encoding="utf-8"
            )
            os.replace(tmp_path, final_path)

    def enforce_cache_retention(
            self,
            profile_name: str,
            max_cached_items: int,
    ) -> List[str]:
        """
        FIFO-cap one profile's cached checkpoint files.

        Purpose:
            Owner ruling: without a DB emitter, cached files follow the
            same checkpoint limit as the ledger - durability beyond the
            cap is the user's explicit opt-in via a DB emitter (future
            lane). Oldest files (ULID name order = creation order) delete
            first.

        Args:
            profile_name:
                Profile whose cache directory is capped.
            max_cached_items:
                Retention bound (the crystallizer's
                max_persistence_crystals).

        Returns:
            List[str]:
                Checkpoint ids whose cached files were removed (empty
                when under the cap).

        Raises:
            RuntimeError:
                If the cache has been cleaned.
            ValueError:
                If `max_cached_items` is not positive.
        """
        self.check_cleaned()
        if max_cached_items < 1:
            raise ValueError(
                "enforce_cache_retention requires a positive "
                "max_cached_items; received {0}.".format(max_cached_items)
            )
        with self._lock:
            profile_directory = self.resolve_cache_root_path() / profile_name
            if not profile_directory.is_dir():
                return []
            cached = sorted(
                entry for entry in profile_directory.glob("*.json")
            )
            removed: List[str] = []
            while len(cached) > max_cached_items:
                oldest = cached.pop(0)
                oldest.unlink()
                removed.append(oldest.stem)
            return removed

    def load_cached_item(self, checkpoint_id: str) -> Dict[str, object]:
        """
        Load one checkpoint cached-item from the crystallizer cache.

        Args:
            checkpoint_id:
                ULID identity of a previously stored checkpoint.

        Returns:
            Dict[str, object]:
                The cached-item payload, ready for
                `PersistenceCrystal.from_cached_item`.

        Raises:
            RuntimeError:
                If the cache has been cleaned.
            KeyError:
                If no cached item exists for `checkpoint_id`.
        """
        self.check_cleaned()
        with self._lock:
            root = self.resolve_cache_root_path()
            # Profile-scoped layout: search the profile folders (the id
            # is a ULID, unique across profiles; the flat legacy path is
            # also checked for pre-layout caches).
            if root.is_dir():
                for candidate in root.glob("*/{0}.json".format(checkpoint_id)):
                    return json.loads(candidate.read_text(encoding="utf-8"))
                legacy_path = root / "{0}.json".format(checkpoint_id)
                if legacy_path.exists():
                    return json.loads(legacy_path.read_text(encoding="utf-8"))
            raise KeyError(
                "No cached checkpoint item for id {0!r} under {1}. Flush "
                "the checkpoint first (flush_checkpoint) or check "
                "list_cached_item_ids().".format(checkpoint_id, str(root))
            )

    def list_cached_item_ids(self) -> List[str]:
        """
        Return every checkpoint id present in the cache directory.

        Returns:
            List[str]:
                Sorted cached checkpoint ids (empty when nothing was
                flushed or the cache directory does not exist yet).

        Raises:
            RuntimeError:
                If the cache has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            root = self.resolve_cache_root_path()
            if not root.is_dir():
                return []
            # Profile folders + the flat legacy layout both count.
            return sorted(
                {entry.stem for entry in root.glob("*/*.json")}
                | {entry.stem for entry in root.glob("*.json")}
            )

    def list_cached_item_ids_for_profile(
            self,
            profile_name: str,
    ) -> List[str]:
        """
        Return one profile's cached checkpoint ids (creation order).

        Args:
            profile_name:
                Profile whose cache folder is listed.

        Returns:
            List[str]:
                Sorted cached ids (ULID order = creation order; empty
                when the profile has no cached checkpoints).

        Raises:
            RuntimeError:
                If the cache has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            profile_directory = self.resolve_cache_root_path() / profile_name
            if not profile_directory.is_dir():
                return []
            return sorted(
                entry.stem for entry in profile_directory.glob("*.json")
            )

