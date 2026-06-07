import hashlib
import json
import logging
import threading
from pathlib import Path
from types import MappingProxyType
from typing import Any, ClassVar, KeysView, Mapping, Optional, Union

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.utilities.logger.safe_logger import SafeLogger


class CachingSystem(Cleanable):
    """
    Conduit-scoped cache persistence utility.

    Purpose:
        Own one rooted-conduit cache file, keep the decoded cache dictionary in
        memory after first load, and provide the small storage operations the
        Spellbook/runtime cache lane needs.

    Contract:
        - One instance represents one cache file for one
          `(frame_name, conduit_name)` pair.
        - The in-memory cache dictionary is loaded once during construction.
        - `spell_payloads` is the single source of truth for cached spell data.
        - `upsert_spell_payload(...)` and `remove_spell_payload(...)` mutate
          only the in-memory dict.
        - `emit()` writes the current in-memory dict to disk.
        - The persisted cache format is one top-level dict:
          `version`, `conduit_name`, `spell_payloads`, and `sha256`.
        - Integrity is bundle-level only: `sha256` covers the serialized cache
          payload excluding the `sha256` field itself.

    Threading / Concurrency:
        - Uses one instance `RLock` to serialize load, mutation, and emit work.
        - Does not rely on OS-level file locks as the primary coordination
          mechanism inside one process.

    Lifecycle / Cleanup:
        - Owns the in-memory cache dictionary and logger wrapper.
        - Does not automatically delete cache files during cleanup.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    CURRENT_VERSION: ClassVar[int] = 1
    BUNDLE_FILENAME: ClassVar[str] = "bundle.json"

    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frame_name",
        "_conduit_name",
        "_cache_root_path",
        "_bundle_path",
        "_cache_data",
        "_logger",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            conduit_name: str,
            cache_root_path: Path,
            logger: Optional[Union[logging.Logger, Any]] = None,
    ) -> None:
        """
        Build one conduit-scoped cache utility.

        Args:
            frame_name:
                Owning Aether frame name.
            conduit_name:
                Root conduit name used for the conduit-local cache folder.
            cache_root_path:
                Absolute cache root path resolved from the Aether root config.
            logger:
                Optional explicit logger surface. When omitted, the hosted
                channel-logger path is used.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frame_name: str = frame_name
        self._conduit_name: str = conduit_name
        self._cache_root_path: Path = cache_root_path
        self._bundle_path: Path = (
            cache_root_path
            / frame_name
            / conduit_name
            / self.BUNDLE_FILENAME
        )
        if isinstance(logger, SafeLogger):
            self._logger = logger
        elif logger is not None:
            self._logger = InitHelpers.resolve_safe_logger(logger)
        else:
            self._logger = InitHelpers.resolve_channel_logger(
                self,
                groups=["cache", "lifecycle"],
                system_groups=["cache", "aether"],
                props={
                    "frame_name": frame_name,
                    "conduit_name": conduit_name,
                    "bundle_path": str(self._bundle_path),
                },
                channels="system",
            )
        self._cache_data: dict[str, Any] = self._build_empty_cache_data()
        self._load_or_initialize_from_disk()

    @property
    def bundle_path(self) -> Path:
        """
        Return the absolute cache-file path owned by this utility.

        Returns:
            Path:
                Absolute cache bundle path.
        """
        return self._bundle_path

    @property
    def conduit_name(self) -> str:
        """
        Return the conduit name associated with this cache file.

        Returns:
            str:
                Conduit name for this cache.
        """
        return self._conduit_name

    @property
    def spell_payloads(self) -> Mapping[str, Any]:
        """
        Return a read-only view of cached spell payloads.

        Returns:
            Mapping[str, Any]:
                Spell-id keyed cache payload view.
        """
        return MappingProxyType(self._cache_data["spell_payloads"])

    @property
    def cached_spell_ids(self) -> KeysView[str]:
        """
        Return the live spell-id key view for this cache.

        Returns:
            KeysView[str]:
                Live `dict.keys()` view over cached spell ids.
        """
        return self._cache_data["spell_payloads"].keys()

    def cleanup(self) -> None:
        """
        Deterministically release owned runtime state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._cache_data.clear()

            del self._cache_data
            del self._bundle_path
            del self._cache_root_path
            del self._conduit_name
            del self._frame_name
            del self._id

        try:
            self._logger.cleanup()
        except Exception:
            pass
        del self._logger
        del self._lock

    def has_spell_payload(self, spell_id: str) -> bool:
        """
        Return whether one cached spell payload exists.

        Args:
            spell_id:
                Spell id to check.

        Returns:
            bool:
                True when the cache currently has a payload for `spell_id`.
        """
        return spell_id in self._cache_data["spell_payloads"]

    def get_spell_payload(self, spell_id: str) -> Optional[Any]:
        """
        Return one cached spell payload by spell id.

        Args:
            spell_id:
                Spell id to resolve.

        Returns:
            Optional[Any]:
                Cached payload when present, otherwise `None`.
        """
        return self._cache_data["spell_payloads"].get(spell_id)

    def upsert_spell_payload(self, spell_id: str, spell_payload: Any) -> None:
        """
        Add or replace one spell payload in memory.

        Args:
            spell_id:
                Spell id to add or replace.
            spell_payload:
                Spell payload for this spell id.

        Returns:
            None.
        """
        with self._lock:
            self._cache_data["spell_payloads"][spell_id] = spell_payload

    def remove_spell_payload(self, spell_id: str) -> bool:
        """
        Remove one spell payload from memory.

        Args:
            spell_id:
                Spell id to remove.

        Returns:
            bool:
                True when a payload existed and was removed, otherwise False.
        """
        with self._lock:
            spell_payloads = self._cache_data["spell_payloads"]
            if spell_id not in spell_payloads:
                return False
            spell_payloads.pop(spell_id)
            return True

    def transfer_spell_payload_to(
            self,
            spell_id: str,
            target_caching_system: "CachingSystem",
    ) -> bool:
        """
        Move one cached spell payload into another cache utility.

        Purpose:
            Provide the ownership-transfer seam for cache payloads without
            forcing the caller to manually load, add, and remove across two
            cache utilities.

        Contract:
            - Favors no data loss over perfect atomicity.
            - Writes into the target in memory first.
            - Removes the source payload only after the target update succeeds.

        Args:
            spell_id:
                Spell id to transfer.
            target_caching_system:
                Target cache utility for the transferred payload.

        Returns:
            bool:
                True when a payload existed and moved, otherwise False.
        """
        if target_caching_system is self:
            return False
        spell_payload = self.get_spell_payload(spell_id)
        if spell_payload is None:
            return False
        target_caching_system.upsert_spell_payload(spell_id, spell_payload)
        self.remove_spell_payload(spell_id)
        return True

    def emit(self) -> None:
        """
        Write the current in-memory cache dict to disk.

        Returns:
            None.
        """
        with self._lock:
            self._write_current_cache_to_disk_locked()

    def _build_empty_cache_data(self) -> dict[str, Any]:
        """
        Build the default in-memory cache dict for this conduit.

        Returns:
            dict[str, Any]:
                Empty cache payload with stamped metadata and hash.
        """
        cache_data = {
            "version": self.CURRENT_VERSION,
            "conduit_name": self._conduit_name,
            "spell_payloads": {},
        }
        cache_data["sha256"] = self._build_sha256_for_cache_data(cache_data)
        return cache_data

    def _load_or_initialize_from_disk(self) -> None:
        """
        Load cache state from disk or initialize an empty cache dict.

        Returns:
            None.
        """
        bundle_path = self._bundle_path
        if not bundle_path.exists():
            self._cache_data = self._build_empty_cache_data()
            return

        try:
            raw_json = bundle_path.read_text(encoding="utf-8")
            loaded_cache_data = json.loads(raw_json)
            normalized_cache_data = self._normalize_loaded_cache_data(
                loaded_cache_data
            )
            expected_sha256 = normalized_cache_data["sha256"]
            actual_sha256 = self._build_sha256_for_cache_data(
                normalized_cache_data
            )
            if actual_sha256 != expected_sha256:
                raise ValueError("Cache bundle sha256 mismatch.")
            self._cache_data = normalized_cache_data
        except Exception as e:
            self._logger.warning(
                f"Failed to load cache bundle '{bundle_path}': {e}. Resetting to empty cache.",
                "_load_or_initialize_from_disk",
            )
            self._cache_data = self._build_empty_cache_data()

    def _normalize_loaded_cache_data(
            self,
            loaded_cache_data: Any,
    ) -> dict[str, Any]:
        """
        Validate and normalize one loaded cache dict.

        Args:
            loaded_cache_data:
                Raw object loaded from disk.

        Returns:
            dict[str, Any]:
                Normalized cache dict.
        """
        version = loaded_cache_data["version"]
        conduit_name = loaded_cache_data["conduit_name"]
        spell_payloads = loaded_cache_data["spell_payloads"]
        sha256 = loaded_cache_data["sha256"]

        if version != self.CURRENT_VERSION:
            raise ValueError(
                f"Unsupported cache version '{version}'."
            )
        if conduit_name != self._conduit_name:
            raise ValueError(
                "Cache conduit_name does not match the requested conduit."
            )
        return {
            "version": version,
            "conduit_name": conduit_name,
            "spell_payloads": dict(spell_payloads),
            "sha256": sha256,
        }

    def _write_current_cache_to_disk_locked(self) -> None:
        """
        Persist the current cache dict to disk.

        Contract:
            - Caller must already hold the instance lock.
            - Writes to a temp file and atomically replaces the final file.

        Returns:
            None.
        """
        cache_data = {
            "version": self._cache_data["version"],
            "conduit_name": self._cache_data["conduit_name"],
            "spell_payloads": self._cache_data["spell_payloads"],
        }
        cache_data["sha256"] = self._build_sha256_for_cache_data(cache_data)
        serialized_cache_data = json.dumps(
            cache_data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        bundle_path = self._bundle_path
        bundle_path.parent.mkdir(parents=True, exist_ok=True)
        temp_bundle_path = bundle_path.with_suffix(".json.tmp")
        temp_bundle_path.write_text(serialized_cache_data, encoding="utf-8")
        temp_bundle_path.replace(bundle_path)
        self._cache_data = cache_data

    def _build_sha256_for_cache_data(
            self,
            cache_data: Mapping[str, Any],
    ) -> str:
        """
        Build the bundle-level sha256 for one cache dict.

        Args:
            cache_data:
                Cache dict whose `sha256` field should be excluded from the
                hash input.

        Returns:
            str:
                Lowercase hex sha256 digest.
        """
        payload_without_sha256 = {
            "version": cache_data["version"],
            "conduit_name": cache_data["conduit_name"],
            "spell_payloads": cache_data["spell_payloads"],
        }
        serialized_payload = json.dumps(
            payload_without_sha256,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        return hashlib.sha256(serialized_payload).hexdigest()
