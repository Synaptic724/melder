import json
import os
import threading
from pathlib import Path
from typing import Dict, List, ClassVar

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class CrystallizerCache(Cleanable):
    """
    Local filesystem custody for checkpoint cached-items and formations.

    Purpose:
        Provide the built-in disk layer beneath `AssetManagementSystem`:
        checkpoint cached-items store as profile-scoped JSON files, while
        user-named formations store beneath each profile's `__formations__`
        directory. The optional external mesh is a separate, user-configured
        durability layer and does not change these local file contracts.

    Contract:
        - The cache root always resolves under the melder package root
          (mirrors `AethericFrameConfiguration.resolve_system_cache_root_path`
          semantics): never against the caller's working directory.
        - Writes are ATOMIC (tmp file + os.replace): a reader never sees a
          torn cached-item; re-storing an id overwrites its previous item.
        - Payloads are JSON round-trip safe by construction
          (`to_cached_item` emits plain values; `from_cached_item`
          normalizes list/tuple shapes back).
        - Checkpoint retention is FIFO by recorded checkpoint number.
          Formations are name-addressed and remain until explicitly deleted.

    Threading:
        One instance RLock serializes storage operations.

    Lifecycle / Cleanup:
        Owned by exactly one `AssetManagementSystem`, not by the persistence
        record. Cleanup releases the in-memory lock only; cached checkpoints
        and formation files deliberately survive for later reload.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Local filesystem custody for checkpoint cached-items and formations. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__: ClassVar[object] = _mrg.sentinel

    __slots__ = Cleanable.__slots__ + [
        "_lock",
    ]

    def __init__(self) -> None:
        """
        Initialize the cache surface.

        Contract:
            Allocates only the synchronization lock. Cache directories are
            resolved or created lazily by storage operations.

        Returns:
            None.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()

    def cleanup(self) -> None:
        """
        Release owned fields and mark the cache cleaned.

        Contract:
            - Idempotent and terminal for this cache object.
            - Deletes no filesystem entry; cleanup is reference teardown, not
              cache eviction. Explicit delete/retention verbs own file removal.
            - Deletes the synchronization lock after operations are quiescent.

        Threading:
            Must not race with a storage operation.

        Lifecycle / Cleanup:
            Invoked by the owning asset system before that system releases its
            borrowed persistence-record reference.

        Returns:
            None.
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
            cap is the user's explicit opt-in through the external mesh.
            Oldest files delete first, where "oldest" is the
            recorded `checkpoint_number` carried in each cached payload
            (monotonic per profile, minted by the record) - NOT the ULID
            filename: two checkpoints sealed within one millisecond share
            a ULID time component and order by their RANDOM tails, so
            name order can invert true creation order (owner-run flake,
            fixed 2026-07-12). Unreadable/legacy files sort oldest and
            reclaim first (a cache file that cannot rehydrate is dead
            weight); files without a usable number fall back to name
            order among themselves.

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

            def _creation_order(path) -> "tuple[int, int, str]":
                """
                True creation-order key for one cached checkpoint file.

                The recorded `checkpoint_number` (monotonic per profile)
                is the authoritative age; ULID filenames tie within one
                millisecond (random tails), so they only break ties.
                Unreadable or non-object payloads sort OLDEST (group 0) so
                dead cache weight reclaims first.
                """
                try:
                    payload = json.loads(
                        path.read_text(encoding="utf-8")
                    )
                    # A checkpoint payload is a JSON object; any other
                    # root shape (list, null, scalar) parses cleanly but
                    # cannot represent a checkpoint, so it is dead weight
                    # and must not crash the sort on `.get()` (BUG-160).
                    if isinstance(payload, dict):
                        number = payload.get("checkpoint_number")
                        if isinstance(number, int):
                            return (1, number, path.name)
                except (OSError, ValueError):
                    pass
                return (0, 0, path.name)

            cached = sorted(
                profile_directory.glob("*.json"),
                key=_creation_order,
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

    def delete_cached_item(self, checkpoint_id: str) -> str:
        """
        Evict one checkpoint cached-item from the crystallizer cache.

        Purpose:
            Single-item delete (asset CRUD completion, 2026-07-11): the
            FIFO retention pass trims by age only; this verb removes one
            specific cached checkpoint by id (a corrupt or unwanted
            snapshot) without touching its neighbours.

        Contract:
            - Mirrors load_cached_item's resolution exactly: the
              profile-scoped layout is searched first, then the flat
              legacy path, so every readable item is deletable.
            - The unlink is a plain file removal; the sealed ledger
              crystal (when still live) is untouched - cache eviction
              never rewrites in-process truth.

        Args:
            checkpoint_id:
                ULID identity of a previously stored checkpoint.

        Returns:
            str: The deleted file's path (teach-grade evidence).

        Raises:
            RuntimeError: If the cache has been cleaned.
            KeyError: If no cached item exists for `checkpoint_id`.
        """
        self.check_cleaned()
        with self._lock:
            root = self.resolve_cache_root_path()
            if root.is_dir():
                for candidate in root.glob("*/{0}.json".format(checkpoint_id)):
                    candidate.unlink()
                    return str(candidate)
                legacy_path = root / "{0}.json".format(checkpoint_id)
                if legacy_path.exists():
                    legacy_path.unlink()
                    return str(legacy_path)
            raise KeyError(
                "No cached checkpoint item for id {0!r} under {1}; "
                "nothing was deleted. Check list_cached_item_ids().".format(
                    checkpoint_id, str(root)
                )
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

    def store_formation(
            self,
            profile_name: str,
            formation_name: str,
            formation_payload: Dict[str, object],
    ) -> str:
        """
        Store one user formation as its named JSON file.

        Contract:
            - Path: <cache root>/{profile}/__formations__/{name}.json
              (atomic tmp+replace; re-storing a name overwrites - the
              user owns their formation names).
            - The name must be filesystem-safe: letters, digits,
              underscore, hyphen.

        Args:
            profile_name:
                Owning profile.
            formation_name:
                The user's name for this formation.
            formation_payload:
                JSON-safe formation record ({"formation_name",
                "profile_name", "scope", "created_at", "description",
                "payloads"}).

        Returns:
            str: Absolute path of the written formation file.

        Raises:
            RuntimeError: If the cache has been cleaned.
            ValueError: If either name is empty or the formation name is
                not filesystem-safe.
        """
        self.check_cleaned()
        if not profile_name or not formation_name:
            raise ValueError(
                "store_formation requires non-empty profile and "
                "formation names."
            )
        if not all(
                ch.isalnum() or ch in "_-" for ch in formation_name
        ):
            raise ValueError(
                "Formation name {0!r} is not filesystem-safe; use "
                "letters, digits, underscore, or hyphen.".format(
                    formation_name
                )
            )
        with self._lock:
            formation_directory = (
                self.resolve_cache_root_path()
                / profile_name
                / "__formations__"
            )
            formation_directory.mkdir(parents=True, exist_ok=True)
            final_path = formation_directory / "{0}.json".format(
                formation_name
            )
            tmp_path = formation_directory / "{0}.json.tmp".format(
                formation_name
            )
            tmp_path.write_text(
                json.dumps(formation_payload, sort_keys=True),
                encoding="utf-8",
            )
            os.replace(tmp_path, final_path)
            return str(final_path)

    def load_formation(
            self,
            profile_name: str,
            formation_name: str,
    ) -> Dict[str, object]:
        """
        Load one stored user formation by profile and name.

        Args:
            profile_name:
                Owning profile.
            formation_name:
                The formation's user-defined name.

        Returns:
            Dict[str, object]: The stored formation record.

        Raises:
            RuntimeError: If the cache has been cleaned.
            KeyError: If no formation exists under the pair.
        """
        self.check_cleaned()
        with self._lock:
            formation_path = (
                self.resolve_cache_root_path()
                / profile_name
                / "__formations__"
                / "{0}.json".format(formation_name)
            )
            if not formation_path.exists():
                raise KeyError(
                    "No formation named {0!r} for profile {1!r} ({2}). "
                    "Check list_formation_names.".format(
                        formation_name, profile_name, str(formation_path)
                    )
                )
            return json.loads(formation_path.read_text(encoding="utf-8"))

    def delete_formation(
            self,
            profile_name: str,
            formation_name: str,
    ) -> str:
        """
        Delete one stored formation file from the local cache.

        Purpose:
            The missing local D of the formation CRUD square (asset CRUD
            completion, 2026-07-11): formations are name-keyed, so no
            FIFO retention pass ever removes them - this verb is the
            only local delete lane.

        Contract:
            - Path form mirrors store/load exactly:
              <cache root>/{profile}/__formations__/{name}.json.
            - Local file removal only; any remote copy is the asset
              system's delete lane (strict, per the retention law).

        Args:
            profile_name:
                Owning profile.
            formation_name:
                The user-chosen formation name to delete.

        Returns:
            str: The deleted file's path (teach-grade evidence).

        Raises:
            RuntimeError: If the cache has been cleaned.
            KeyError: If the formation file does not exist.
        """
        self.check_cleaned()
        with self._lock:
            formation_path = (
                self.resolve_cache_root_path()
                / profile_name
                / "__formations__"
                / "{0}.json".format(formation_name)
            )
            if not formation_path.exists():
                raise KeyError(
                    "No stored formation {0!r} for profile {1!r} at {2}; "
                    "nothing was deleted. Check list_formation_names.".format(
                        formation_name, profile_name, str(formation_path)
                    )
                )
            formation_path.unlink()
            return str(formation_path)

    def list_formation_names(self, profile_name: str) -> List[str]:
        """
        Return one profile's stored formation names.

        Args:
            profile_name:
                Owning profile.

        Returns:
            List[str]: Sorted formation names (empty when none saved).

        Raises:
            RuntimeError: If the cache has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            formation_directory = (
                self.resolve_cache_root_path()
                / profile_name
                / "__formations__"
            )
            if not formation_directory.is_dir():
                return []
            return sorted(
                entry.stem for entry in formation_directory.glob("*.json")
            )

    def list_cached_item_ids_for_profile(
            self,
            profile_name: str,
    ) -> List[str]:
        """
        Return one profile's cached checkpoint ids in lexical ULID order.

        Args:
            profile_name:
                Profile whose cache folder is listed.

        Returns:
            List[str]:
                Lexically sorted cached ids; empty when the profile has no
                cached checkpoints. This is time-ordered at ULID timestamp
                granularity, but random tails do not prove exact order for
                checkpoints minted in the same millisecond.

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

