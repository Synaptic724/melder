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
        memory after first load, and expose small mutation helpers that flush
        the cache back to disk immediately after each successful change.

    Contract:
        - One instance represents one cache file for one `(frame_name, conduit_name)` pair.
        - The in-memory cache dictionary is loaded once during construction.
        - Mutations are serialized by the instance lock.
        - Successful mutations are flushed immediately to the owned cache file.
        - The persisted cache format is one top-level dict:
          `version`, `conduit_name`, `spell_payloads`, and `sha256`.
        - `spell_payloads` is the single source of truth for cached spell data.
        - Integrity is bundle-level only: `sha256` covers the serialized cache
          payload excluding the `sha256` field itself.

    Threading / Concurrency:
        - Uses one instance `RLock` to serialize load, mutation, and flush work.
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

        Raises:
            TypeError:
                If frame_name or conduit_name is not a string, or if
                cache_root_path is not a `Path`.
            ValueError:
                If frame_name or conduit_name is empty, or if cache_root_path
                is not absolute.
        """
        super().__init__()
        if not isinstance(frame_name, str):
            raise TypeError("frame_name must be a string.")
        if not frame_name.strip():
            raise ValueError("frame_name must not be empty.")
        if not isinstance(conduit_name, str):
            raise TypeError("conduit_name must be a string.")
        if not conduit_name.strip():
            raise ValueError("conduit_name must not be empty.")
        if not isinstance(cache_root_path, Path):
            raise TypeError("cache_root_path must be a Path.")
        if not cache_root_path.is_absolute():
            raise ValueError("cache_root_path must be absolute.")

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
        self.check_cleaned()
        return self._bundle_path

    @property
    def conduit_name(self) -> str:
        """
        Return the conduit name associated with this cache file.

        Returns:
            str:
                Conduit name for this cache.
        """
        self.check_cleaned()
        return self._conduit_name

    @property
    def spell_payloads(self) -> Mapping[str, Any]:
        """
        Return a read-only view of cached spell payloads.

        Returns:
            Mapping[str, Any]:
                Spell-id keyed cache payload view.
        """
        self.check_cleaned()
        return MappingProxyType(self._cache_data["spell_payloads"])

    @property
    def cached_spell_ids(self) -> KeysView[str]:
        """
        Return the live spell-id key view for this cache.

        Returns:
            KeysView[str]:
                Live `dict.keys()` view over cached spell ids.
        """
        self.check_cleaned()
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
        self.check_cleaned()
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
        self.check_cleaned()
        return self._cache_data["spell_payloads"].get(spell_id)

    def upsert_spell_payload(self, spell_id: str, spell_payload: Any) -> None:
        """
        Add or replace one spell payload and flush the cache file.

        Args:
            spell_id:
                Spell id to add or replace.
            spell_payload:
                JSON-serializable spell payload for this spell id.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the flush fails after mutation.
        """
        self.check_cleaned()
        if not isinstance(spell_id, str):
            raise TypeError("spell_id must be a string.")
        if not spell_id:
            raise ValueError("spell_id must not be empty.")
        with self._lock:
            spell_payloads = self._cache_data["spell_payloads"]
            had_existing_payload = spell_id in spell_payloads
            previous_payload = spell_payloads.get(spell_id)
            spell_payloads[spell_id] = spell_payload
            try:
                self._write_current_cache_to_disk_locked()
            except Exception:
                if had_existing_payload:
                    spell_payloads[spell_id] = previous_payload
                else:
                    spell_payloads.pop(spell_id, None)
                raise

    def remove_spell_payload(self, spell_id: str) -> bool:
        """
        Remove one spell payload and flush the cache file.

        Args:
            spell_id:
                Spell id to remove.

        Returns:
            bool:
                True when a payload existed and was removed, otherwise False.
        """
        self.check_cleaned()
        if not isinstance(spell_id, str):
            raise TypeError("spell_id must be a string.")
        if not spell_id:
            raise ValueError("spell_id must not be empty.")
        with self._lock:
            spell_payloads = self._cache_data["spell_payloads"]
            if spell_id not in spell_payloads:
                return False
            previous_payload = spell_payloads.pop(spell_id)
            try:
                self._write_current_cache_to_disk_locked()
            except Exception:
                spell_payloads[spell_id] = previous_payload
                raise
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
            requiring the caller to manually load, add, and remove across two
            cache files.

        Contract:
            - Favors no data loss over perfect atomicity.
            - Writes the target cache first.
            - Removes the source payload only after the target write succeeds.

        Args:
            spell_id:
                Spell id to transfer.
            target_caching_system:
                Target cache utility for the transferred payload.

        Returns:
            bool:
                True when a payload existed and moved, otherwise False.
        """
        self.check_cleaned()
        if target_caching_system is self:
            return False
        spell_payload = self.get_spell_payload(spell_id)
        if spell_payload is None:
            return False
        target_caching_system.upsert_spell_payload(spell_id, spell_payload)
        self.remove_spell_payload(spell_id)
        return True

    def flush(self) -> None:
        """
        Write the current in-memory cache dict to disk.

        Returns:
            None.
        """
        self.check_cleaned()
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
        if not isinstance(loaded_cache_data, dict):
            raise TypeError("Loaded cache data must be a dict.")
        version = loaded_cache_data.get("version")
        conduit_name = loaded_cache_data.get("conduit_name")
        spell_payloads = loaded_cache_data.get("spell_payloads")
        sha256 = loaded_cache_data.get("sha256")

        if not isinstance(version, int):
            raise TypeError("Cache version must be an int.")
        if version != self.CURRENT_VERSION:
            raise ValueError(
                f"Unsupported cache version '{version}'."
            )
        if not isinstance(conduit_name, str):
            raise TypeError("Cache conduit_name must be a string.")
        if conduit_name != self._conduit_name:
            raise ValueError(
                "Cache conduit_name does not match the requested conduit."
            )
        if not isinstance(spell_payloads, dict):
            raise TypeError("Cache spell_payloads must be a dict.")
        if not isinstance(sha256, str):
            raise TypeError("Cache sha256 must be a string.")

        normalized_spell_payloads: dict[str, Any] = {}
        for spell_id, spell_payload in spell_payloads.items():
            if not isinstance(spell_id, str):
                raise TypeError("Cache spell ids must be strings.")
            normalized_spell_payloads[spell_id] = spell_payload

        return {
            "version": version,
            "conduit_name": conduit_name,
            "spell_payloads": normalized_spell_payloads,
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
