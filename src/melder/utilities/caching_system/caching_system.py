import logging
import marshal
import sys
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
        - The in-memory store keeps every spell payload as NESTED-MARSHAL
          BYTES (`spell_id` -> `marshal.dumps(payload)`), never as decoded
          containers. Rationale (measured, 2026-07-02 gauntlet 2x2): the
          free-threaded GC scans the full tracked heap per collection, and a
          decoded bundle retained for the process lifetime fattened every
          pass (~13% warm wall regression). `bytes` values are GC-untracked,
          so the resident cache costs collections nothing.
        - `upsert_spell_payload(...)` serializes immediately;
          `get_spell_payload(...)` returns a FRESH decode per call (caller
          mutations are never persisted); `remove_spell_payload(...)` mutates
          only the in-memory dict.
        - `emit()` writes the current in-memory dict to disk.
        - The persisted cache format is one `marshal`-serialized top-level
          dict: `version`, `python`, `frame_name`, `conduit_name`, and
          `spell_payloads` (spell_id -> nested payload bytes). Payloads may
          contain `CodeType` objects, which is why the encoding is `marshal`
          rather than JSON.
        - Integrity is regeneration-based: a corrupt or version-mismatched
          bundle is treated as a cold cache, not repaired.

    Threading / Concurrency:
        - Uses one instance `RLock` to serialize load, mutation, and emit work.
        - Does not rely on OS-level file locks as the primary coordination
          mechanism inside one process.

    Lifecycle / Cleanup:
        - Owns the in-memory cache dictionary and logger wrapper.
        - Does not automatically delete cache files during cleanup.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    # Version 6: zero-provider required collection sockets now inject []
    # (owner policy 2026-07-06): the analyzer publishes empty-collection
    # dependency entries, solo declines collection-bearing models, and all
    # emitters render/assign [] for zero-key collection params. Version-5
    # bundles predate those occurrence rows and emitted bodies.
    # Version 5: the many_only-local row producers (override step rows,
    # no-overrides manifest rows, no-overrides signature rows) also emit
    # `collection_param_names`; version-4 bundles written before that fix
    # hold many_only manifests whose rows lack the field and fail the
    # stricter hydrate, so they must invalidate wholesale.
    # Version 4: step rows carry `collection_param_names` (phase-3 socket
    # truth propagated through phases 9-11) so emitters wrap one-member
    # collection sockets in a list; older payloads lack the field and their
    # emission semantics scalar-unwrapped single-member collections.
    # Version 3 stored spell payloads as nested-marshal BYTES per spell
    # (GC-untracked resident cache; see class contract). Version 2 carried
    # decoded manifest-package dicts; version 1 carried legacy executor
    # shapes. Older bundles are treated as cold cache and regenerated.
    CURRENT_VERSION: ClassVar[int] = 5
    BUNDLE_SUFFIX: ClassVar[str] = ".melc"

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
            / f"{conduit_name}{self.BUNDLE_SUFFIX}"
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
        Return a decoded snapshot of every cached spell payload.

        Contract:
            - O(n) decode per access: payloads are stored as nested-marshal
              bytes, so this property materializes a FRESH decoded dict each
              call. Intended for diagnostics/tests, not hot paths.
            - Mutating the snapshot never affects the stored cache.

        Returns:
            Mapping[str, Any]:
                Spell-id keyed decoded payload snapshot.
        """
        return MappingProxyType({
            spell_id: marshal.loads(payload_bytes)
            for spell_id, payload_bytes
            in self._cache_data["spell_payloads"].items()
        })

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

        Contract:
            - Returns a FRESH decode of the stored payload bytes per call;
              mutating the returned object never affects the stored cache.

        Args:
            spell_id:
                Spell id to resolve.

        Returns:
            Optional[Any]:
                Freshly decoded payload when present, otherwise `None`.
        """
        payload_bytes = self._cache_data["spell_payloads"].get(spell_id)
        if payload_bytes is None:
            return None
        return marshal.loads(payload_bytes)

    def upsert_spell_payload(self, spell_id: str, spell_payload: Any) -> None:
        """
        Add or replace one spell payload in memory.

        Contract:
            - Serializes the payload to nested-marshal bytes IMMEDIATELY, so
              the resident cache never holds decoded (GC-tracked) containers
              and later caller mutations of `spell_payload` are not captured.

        Args:
            spell_id:
                Spell id to add or replace.
            spell_payload:
                Marshal-safe decoded payload for this spell id.

        Returns:
            None.
        """
        payload_bytes = marshal.dumps(spell_payload)
        with self._lock:
            self._cache_data["spell_payloads"][spell_id] = payload_bytes

    def _store_serialized_payload(
            self,
            spell_id: str,
            payload_bytes: bytes,
    ) -> None:
        """
        Store one already-serialized payload without a decode round-trip.

        Contract:
            - Internal seam for payload transfer between cache utilities;
              the bytes MUST originate from another `CachingSystem` store.

        Args:
            spell_id:
                Spell id to add or replace.
            payload_bytes:
                Nested-marshal payload bytes from a sibling cache store.

        Returns:
            None.
        """
        with self._lock:
            self._cache_data["spell_payloads"][spell_id] = payload_bytes

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
        # Move the stored BYTES directly: no decode/re-encode round-trip and
        # no decoded containers created during the transfer.
        payload_bytes = self._cache_data["spell_payloads"].get(spell_id)
        if payload_bytes is None:
            return False
        target_caching_system._store_serialized_payload(
            spell_id, payload_bytes
        )
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
        return {
            "version": self.CURRENT_VERSION,
            "python": sys.implementation.cache_tag,
            "frame_name": self._frame_name,
            "conduit_name": self._conduit_name,
            "spell_payloads": {},
        }

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
            raw_bytes = bundle_path.read_bytes()
            loaded_cache_data = marshal.loads(raw_bytes)
            self._cache_data = self._normalize_loaded_cache_data(
                loaded_cache_data
            )
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
            raise ValueError("Cache bundle is not a dict.")
        version = loaded_cache_data["version"]
        python_tag = loaded_cache_data["python"]
        conduit_name = loaded_cache_data["conduit_name"]
        spell_payloads = loaded_cache_data["spell_payloads"]

        if version != self.CURRENT_VERSION:
            raise ValueError(
                f"Unsupported cache version '{version}'."
            )
        if python_tag != sys.implementation.cache_tag:
            raise ValueError(
                f"Cache python tag '{python_tag}' does not match runtime "
                f"'{sys.implementation.cache_tag}'."
            )
        if conduit_name != self._conduit_name:
            raise ValueError(
                "Cache conduit_name does not match the requested conduit."
            )
        for spell_id, payload_bytes in spell_payloads.items():
            if not isinstance(payload_bytes, bytes):
                # Version-3 bundles store nested-marshal bytes per spell; a
                # decoded container here means a foreign/corrupt bundle, so
                # regenerate cold rather than adopting tracked payloads.
                raise ValueError(
                    f"Cache payload for '{spell_id}' is not nested-marshal "
                    "bytes."
                )
        return {
            "version": version,
            "python": python_tag,
            "frame_name": loaded_cache_data.get("frame_name", self._frame_name),
            "conduit_name": conduit_name,
            "spell_payloads": dict(spell_payloads),
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
            "python": self._cache_data.get(
                "python", sys.implementation.cache_tag
            ),
            "frame_name": self._cache_data.get("frame_name", self._frame_name),
            "conduit_name": self._cache_data["conduit_name"],
            "spell_payloads": self._cache_data["spell_payloads"],
        }
        serialized_cache_data = marshal.dumps(cache_data)
        bundle_path = self._bundle_path
        bundle_path.parent.mkdir(parents=True, exist_ok=True)
        temp_bundle_path = bundle_path.with_suffix(
            self.BUNDLE_SUFFIX + ".tmp"
        )
        temp_bundle_path.write_bytes(serialized_cache_data)
        temp_bundle_path.replace(bundle_path)
        self._cache_data = cache_data
