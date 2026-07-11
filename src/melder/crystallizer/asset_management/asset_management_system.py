"""
Bytes-at-rest custody for the crystallizer (V3 asset_management identity).

Everything durable that is not in-process truth lives here: local checkpoint
cache files, formation files, cache-file retention, and the user's remote DB
seam (ExternalPersistenceManager). The asset system BORROWS the record
(PersistenceSystem) - it reads flush feedstock through the record's public
verbs and lands every reload in the record's insert sink; the record never
calls back (edge law).

Lane: EPIC-2026-07-09-crystallizer-subsystem-decomposition, story S3.
"""

import threading
from typing import Dict, List, Optional, TYPE_CHECKING

from melder.utilities.general_base.cleanable import Cleanable
from melder.crystallizer.asset_management.crystallizer_cache import (
    CrystallizerCache,
)
from melder.crystallizer.asset_management.external_persistence_manager import (
    ExternalPersistenceManager,
)

if TYPE_CHECKING:
    from melder.crystallizer.asset_management.external_persistence_manager_configuration import (
        ExternalPersistenceManagerConfiguration,
    )
    from melder.crystallizer.persistence.persistence_system import (
        PersistenceSystem,
    )


class AssetManagementSystem(Cleanable):
    """
    Own the crystallizer's bytes at rest: cache files, formations, DB seam.

    Purpose:
        One separate location for disk and remote custody (owner ruling,
        2026-07-09): the seal-then-ship flush lane, cache/remote reload
        lanes feeding the record's insert sink, formation file storage,
        and the ExternalPersistenceManager the user attaches for their
        own database.

    Contract:
        - BORROWS the PersistenceSystem: reads feedstock
          (cached_item_form/forms, describe_checkpoint, retention cap,
          active profile name) and calls its insert sink - always through
          PUBLIC record verbs; never reaches into record internals.
        - OWNS the CrystallizerCache and the optional
          ExternalPersistenceManager (replace-on-reconfigure; the old
          manager cleans).
        - FLUSH CONTRACT: seal (ledger) then ship (assets) - local cache
          first, FIFO cache retention at the record's LIVE cap, then the
          lenient remote upload leg (failures count into the manager's
          accounting and never break the local lane).
        - Reload lanes are insert-if-absent via the record's sink;
          retention never runs on reloads (importing history must not
          evict newer crystals).

    Threading:
        One instance RLock guards the manager swap and multi-step
        cache+sink sequences. Lock order is one-way: asset lock -> record
        public verbs (the record locks itself); the record never calls
        the asset system, so no inversion can occur.

    Lifecycle / Cleanup:
        Owned by exactly one Crystallizer and cleaned BEFORE the record
        (this object borrows it). cleanup(): manager first, then the
        cache, then owned references (del posture, lock last); the
        borrowed record is dereferenced, never cleaned.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_persistence_system",
        "_crystallizer_cache",
        "_external_persistence_manager",
    ]

    def __init__(self, persistence_system: PersistenceSystem) -> None:
        """
        Initialize the asset system over one borrowed record.

        Args:
            persistence_system:
                The crystallizer's record. Borrowed collaborator: used
                and stored, never owned or cleaned here.

        Returns:
            None.

        Raises:
            TypeError: If `persistence_system` is None.
        """
        super().__init__()
        if persistence_system is None:
            raise TypeError("persistence_system cannot be None.")
        self._lock: threading.RLock = threading.RLock()
        self._persistence_system: PersistenceSystem = persistence_system
        self._crystallizer_cache: CrystallizerCache = CrystallizerCache()
        self._external_persistence_manager: Optional[
            ExternalPersistenceManager
        ] = None

    def cleanup(self) -> None:
        """
        Clean owned custody (manager, then cache), release references.

        Contract:
            - Idempotent; del posture; lock deleted last.
            - The borrowed record is dereferenced, never cleaned.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if (
                    self._external_persistence_manager is not None
                    and not self._external_persistence_manager.cleaned
            ):
                self._external_persistence_manager.cleanup()
            if not self._crystallizer_cache.cleaned:
                self._crystallizer_cache.cleanup()
        del self._external_persistence_manager
        del self._crystallizer_cache
        del self._persistence_system
        del self._lock

    # ------------------------------------------------------------------
    # Checkpoint cache lanes (moved from PersistenceSystem, S3)
    # ------------------------------------------------------------------

    def flush_checkpoint(self, checkpoint_id: Optional[str] = None) -> List[str]:
        """
        Flush sealed checkpoint(s) to the local cache, then ship remote.

        Purpose:
            The seal-then-ship lane: the record hands out cached-item
            feedstock; this side writes the cache files, FIFO-caps the
            cache at the record's live retention limit, and pushes the
            SAME payloads through the external manager when one is
            attached with uploads enabled (one feedstock pull serves both
            legs).

        Args:
            checkpoint_id:
                One ledger ULID, or None to flush EVERY ledger crystal.

        Returns:
            List[str]:
                The flushed checkpoint ids.

        Raises:
            RuntimeError:
                If the asset system has been cleaned.
            KeyError:
                If `checkpoint_id` names no ledger crystal.
        """
        self.check_cleaned()
        with self._lock:
            cached_items = self._persistence_system.cached_item_forms(
                checkpoint_id
            )
            flushed: List[str] = []
            touched_profiles: List[str] = []
            for cached_item in cached_items:
                item_id = str(cached_item["checkpoint_id"])
                self._crystallizer_cache.store_cached_item(
                    item_id, cached_item
                )
                flushed.append(item_id)
                profile_name = str(
                    cached_item.get("profile_name", "default")
                )
                if profile_name not in touched_profiles:
                    touched_profiles.append(profile_name)
            # Owner ruling: without a DB emitter the cache follows the
            # checkpoint limit too - FIFO the oldest cached files out.
            # Durability beyond the cap is the user's opt-in via a DB
            # emitter; "its on them".
            retention_cap = self._persistence_system.max_persistence_crystals
            for profile_name in touched_profiles:
                self._crystallizer_cache.enforce_cache_retention(
                    profile_name, retention_cap
                )
            # DB opt-in leg: lenient by default - the local lane never
            # dies on a remote failure (the manager accounts for it).
            manager = self._external_persistence_manager
            if manager is not None and manager.upload_enabled:
                for cached_item in cached_items:
                    manager.upload_checkpoint(
                        str(cached_item.get("profile_name", "default")),
                        str(cached_item["checkpoint_id"]),
                        cached_item,
                    )
            return flushed

    def reload_checkpoint_from_cache(
            self,
            checkpoint_id: str,
    ) -> Dict[str, object]:
        """
        Reload one cached checkpoint back into the record.

        Purpose:
            History recovery: the cached item lands in the record's
            insert sink (insert-if-absent - an id already in the ledger
            keeps its live crystal) and the record describes the result.

        Args:
            checkpoint_id:
                ULID of a previously flushed checkpoint.

        Returns:
            Dict[str, object]:
                The (re)loaded checkpoint's describe() summary.

        Raises:
            RuntimeError:
                If the asset system has been cleaned.
            KeyError:
                If no cached item exists for `checkpoint_id`.
        """
        self.check_cleaned()
        with self._lock:
            cached_item = self._crystallizer_cache.load_cached_item(
                checkpoint_id
            )
            self._persistence_system.insert_cached_items([cached_item])
            return self._persistence_system.describe_checkpoint(
                checkpoint_id
            )

    def list_cached_checkpoint_ids(self) -> List[str]:
        """
        Return every checkpoint id present in the local cache.

        Returns:
            List[str]:
                Sorted cached checkpoint ids (empty when nothing flushed).

        Raises:
            RuntimeError:
                If the asset system has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._crystallizer_cache.list_cached_item_ids()

    def reload_profile_from_cache(
            self,
            profile_name: str,
    ) -> Dict[str, object]:
        """
        Reload EVERY cached checkpoint of one profile into the record.

        Purpose:
            "Import a world" the owner's way: a profile's cache folder IS
            its portable form - copy the folder, call this verb on the
            receiving process, then load_checkpoint unfolds the chain.

        Contract:
            - Insert-if-absent via the record's sink; re-running is
              idempotent.
            - Retention dropout does NOT run here (reloading history must
              not evict newer crystals).

        Args:
            profile_name:
                Profile whose cached checkpoints should reload.

        Returns:
            Dict[str, object]:
                {"profile_name": str, "inserted": [ids],
                 "skipped_existing": [ids]}.

        Raises:
            RuntimeError: If the asset system has been cleaned.
            KeyError: If the profile has no cached checkpoints.
        """
        self.check_cleaned()
        with self._lock:
            cached_ids = (
                self._crystallizer_cache.list_cached_item_ids_for_profile(
                    profile_name
                )
            )
            if not cached_ids:
                raise KeyError(
                    "No cached checkpoints exist for profile {0!r}; flush "
                    "some first (flush_checkpoint_to_cache) or copy the "
                    "profile's cache folder into place.".format(profile_name)
                )
            cached_items = [
                self._crystallizer_cache.load_cached_item(cached_id)
                for cached_id in cached_ids
            ]
            summary = self._persistence_system.insert_cached_items(
                cached_items
            )
        return {
            "profile_name": profile_name,
            "inserted": list(summary["inserted"]),
            "skipped_existing": list(summary["skipped_existing"]),
        }

    # ------------------------------------------------------------------
    # Formation file custody (moved from PersistenceSystem, S3)
    # ------------------------------------------------------------------

    def store_formation(
            self,
            formation_record: Dict[str, object],
    ) -> str:
        """
        Persist one captured formation record as a named cache artifact.

        Args:
            formation_record:
                The record assembled by
                `PersistenceSystem.capture_formation_record` (carries its
                own profile_name and formation_name).

        Returns:
            str: Absolute path of the stored formation file.

        Raises:
            RuntimeError: If the asset system has been cleaned.
            ValueError: If the formation name is not filesystem-safe.
        """
        self.check_cleaned()
        with self._lock:
            return self._crystallizer_cache.store_formation(
                str(formation_record["profile_name"]),
                str(formation_record["formation_name"]),
                formation_record,
            )

    def load_formation_record(
            self,
            formation_name: str,
            profile_name: Optional[str] = None,
    ) -> Dict[str, object]:
        """
        Load one stored formation record (payloads + metadata).

        Purpose:
            Shared read lane for the restore facade and the persistence
            analyzer facades.

        Args:
            formation_name:
                The stored formation's name.
            profile_name:
                Profile whose formation store is read; None means the
                record's active profile.

        Returns:
            Dict[str, object]: The stored formation record.

        Raises:
            RuntimeError: If the asset system has been cleaned.
            KeyError: If no formation exists under the name.
        """
        self.check_cleaned()
        with self._lock:
            resolved_name = (
                profile_name
                if profile_name is not None
                else self._persistence_system.active_profile_name
            )
            return self._crystallizer_cache.load_formation(
                resolved_name, formation_name
            )

    def list_formations(
            self,
            profile_name: Optional[str] = None,
    ) -> List[str]:
        """
        Return the targeted profile's stored formation names.

        Args:
            profile_name:
                Profile to list; None means the record's active profile.

        Returns:
            List[str]: Sorted formation names.

        Raises:
            RuntimeError: If the asset system has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            resolved_name = (
                profile_name
                if profile_name is not None
                else self._persistence_system.active_profile_name
            )
            return self._crystallizer_cache.list_formation_names(
                resolved_name
            )

    # ------------------------------------------------------------------
    # External persistence (the DB opt-in seam; moved from Crystallizer)
    # ------------------------------------------------------------------

    def configure_external_persistence_manager(
            self,
            manager_configuration: ExternalPersistenceManagerConfiguration,
    ) -> None:
        """
        Attach the user's external transport.

        Purpose:
            The DB opt-in seam (owner ruling): the user loads their own
            upload/download callables into a SEPARATE configuration -
            their SQL bootstrap, their secrets, their driver - and this
            verb builds the asset-owned ExternalPersistenceManager from
            it.

        Contract:
            - Freezes the configuration if the caller has not (load it
              in, freeze it - the reload-lane law).
            - Re-configuring replaces the previous manager (the old one
              cleans); attach BEFORE relying on upload-on-flush.

        Args:
            manager_configuration:
                The handler-bearing configuration (ownership transfers
                to the built manager).

        Returns:
            None.

        Raises:
            RuntimeError: If the asset system has been cleaned.
            TypeError/ValueError: Propagated from the manager's
                construction contract.
        """
        self.check_cleaned()
        if not manager_configuration.frozen:
            manager_configuration.freeze()
        manager = ExternalPersistenceManager(manager_configuration)
        with self._lock:
            previous = self._external_persistence_manager
            self._external_persistence_manager = manager
        if previous is not None and not previous.cleaned:
            previous.cleanup()

    def describe_external_persistence_manager(self) -> Dict[str, object]:
        """
        Return the attached manager's record-safe presence description.

        Returns:
            Dict[str, object]:
                Presence flags + knobs + failure diagnostics; an
                {"attached": False} stub when no manager is configured.

        Raises:
            RuntimeError: If the asset system has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            manager = self._external_persistence_manager
        if manager is None:
            return {"attached": False}
        description = manager.describe()
        description["attached"] = True
        return description

    def reload_profile_from_external(
            self,
            profile_name: str,
    ) -> Dict[str, object]:
        """
        Download and insert EVERY remote checkpoint of one profile.

        Purpose:
            The remote import lane: the manager downloads the profile's
            stored cached items (list + per-id download through the
            user's callables) and the record inserts them
            insert-if-absent - then load_checkpoint unfolds as usual.

        Args:
            profile_name:
                Profile whose remote history should reload.

        Returns:
            Dict[str, object]:
                {"profile_name", "inserted", "skipped_existing"}.

        Raises:
            RuntimeError: If cleaned, no manager is attached, or
                download/list handlers are missing.
            ValueError: If the remote lists an id it cannot return.
        """
        self.check_cleaned()
        with self._lock:
            manager = self._external_persistence_manager
        if manager is None:
            raise RuntimeError(
                "No ExternalPersistenceManager is attached; call "
                "configure_external_persistence_manager(...) with your "
                "handler configuration first."
            )
        cached_items = manager.download_profile(profile_name)
        summary = self._persistence_system.insert_cached_items(cached_items)
        summary["profile_name"] = profile_name
        return summary
