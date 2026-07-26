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
from typing import Dict, List, Optional, TYPE_CHECKING, ClassVar

from melder.utilities.general_base.cleanable import Cleanable
from melder.crystallizer.asset_management.crystallizer_cache import (
    CrystallizerCache,
)
from melder.crystallizer.asset_management.external_persistence_manager import (
    ExternalPersistenceManager,
)
from melder.crystallizer.asset_management.mesh_interface_contract import (
    MeshInterfaceContract,
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

    Registration:
        MELDER KERNEL - guarded (internal manifest). One of the three same-rank
        children `Crystallizer` owns; Melder constructs it and users reach it only through
        `Crystallizer` facades. access=internal.

    Subsystem Context:
        BYTES AT REST of the crystallizer subsystem (sibling to `PersistenceSystem` the record
        and `CrystalLoaderSystem` the unfold). It owns the `CrystallizerCache` and the optional
        `ExternalPersistenceManager`, and BORROWS the record - reading feedstock and calling its
        insert sink through PUBLIC verbs only. Formation files live here.

    System Context:
        Crystallizer layer of the boot order (position 2, after Aether|AetherUtilitySystem). Its
        FLUSH CONTRACT is seal-then-ship: the record seals a checkpoint, then this system writes
        the local cache, applies FIFO retention at the record's LIVE cap, and runs the lenient
        remote upload leg (a remote failure never breaks local custody). Reloads are
        insert-if-absent through the record's sink and never trigger retention.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Own the crystallizer's bytes at rest: cache files, formations, DB
        seam. Melder kernel machinery: read it to understand the runtime, do not drive it
        directly.
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

        Contract:
            Creates and owns one local `CrystallizerCache`; no external manager
            exists until configured. Construction neither reads nor writes the
            filesystem and does not inspect the borrowed record.

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
            - Idempotent and terminal; the external manager cleans before the
              cache, then the borrowed record is dereferenced.
            - The record is never cleaned here, and cache cleanup does not
              delete checkpoint or formation files from disk.
            - The instance lock is deleted last.

        Threading:
            Serialized by the asset lock; no flush, reload, or manager swap may
            race with teardown.

        Lifecycle / Cleanup:
            Called by `Crystallizer.cleanup()` before persistence cleanup,
            satisfying borrower-before-record ownership.

        Returns:
            None.
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
            stored_path = self._crystallizer_cache.store_formation(
                str(formation_record["profile_name"]),
                str(formation_record["formation_name"]),
                formation_record,
            )
            manager = self._external_persistence_manager
        # Flush-shipped mesh lane (external_mesh 2026-07-12, owner
        # ruling): formations ship local-then-remote exactly like
        # checkpoints - lenient + counted, the local artifact never dies
        # on a remote failure.
        if manager is not None and manager.store_enabled:
            manager.store_unit(
                "formation",
                str(formation_record["profile_name"]),
                str(formation_record["formation_name"]),
                formation_record,
            )
        return stored_path

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
            record = self._crystallizer_cache.load_formation(
                resolved_name, formation_name
            )
        # Read gate (record versioning, owner ruling 2026-07-12): a
        # formation written by a NEWER major refuses before any replay.
        from melder.crystallizer.persistence.record_version import (
            RecordVersion,
        )

        RecordVersion.check_readable(
            dict(record), "formation {0!r}".format(formation_name)
        )
        return record

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

    def reload_formations_from_external(
            self,
            profile_name: str,
    ) -> Dict[str, object]:
        """
        Download and store EVERY remote formation of one profile.

        Purpose:
            The formation half of the remote import lane (external_mesh
            2026-07-12): list + per-name fetch through the user's generic
            callables, then insert-if-absent into the local formation
            store - restore_formation reads them as usual afterwards.

        Args:
            profile_name:
                Profile whose remote formations should reload.

        Returns:
            Dict[str, object]:
                {"profile_name", "inserted": [names],
                 "skipped_existing": [names]}.

        Raises:
            RuntimeError: If cleaned, no manager is attached, or the
                generic fetch/list lanes are missing.
            ValueError: If the remote lists a formation it cannot return.
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
        existing = set(self.list_formations(profile_name))
        inserted: List[str] = []
        skipped: List[str] = []
        for formation_name in manager.list_units(
                "formation", profile_name
        ):
            if formation_name in existing:
                skipped.append(formation_name)
                continue
            record = manager.fetch_unit("formation", formation_name)
            if record is None:
                raise ValueError(
                    "Remote listed formation {0!r} for profile {1!r} but "
                    "returned nothing for it - the remote store is "
                    "inconsistent; repair it before reloading.".format(
                        formation_name, profile_name
                    )
                )
            with self._lock:
                self._crystallizer_cache.store_formation(
                    profile_name, formation_name, record
                )
            inserted.append(formation_name)
        return {
            "profile_name": profile_name,
            "inserted": inserted,
            "skipped_existing": skipped,
        }

    def apply_external_retention(
            self,
            profile_name: str,
            max_checkpoints: int,
    ) -> List[str]:
        """
        Delete the oldest remote checkpoints beyond one retention cap.

        Purpose:
            Melder-driven remote retention (owner ruling 2026-07-12,
            opt-in via the delete handler; mirrors the local FIFO cap):
            checkpoint ids are ULIDs, so the sorted listing IS creation
            order - everything before the newest `max_checkpoints` ids
            deletes through the user's callable.

        Contract:
            - Requires the generic list-units AND delete lanes (loud
              refusal otherwise; a retention pass must never guess).
            - Deletes are strict: a failing delete propagates so the
              caller knows the remote was only partially trimmed.

        Args:
            profile_name:
                Profile whose remote checkpoint history is trimmed.
            max_checkpoints:
                How many NEWEST checkpoints survive; must be positive.

        Returns:
            List[str]: The deleted checkpoint ids, oldest first.

        Raises:
            RuntimeError: If cleaned, no manager attached, or the
                list-units/delete lanes are missing.
            ValueError: If `max_checkpoints` is not a positive int.
        """
        self.check_cleaned()
        if (
            not isinstance(max_checkpoints, int)
            or isinstance(max_checkpoints, bool)
            or max_checkpoints <= 0
        ):
            raise ValueError("max_checkpoints must be a positive int.")
        with self._lock:
            manager = self._external_persistence_manager
        if manager is None:
            raise RuntimeError(
                "No ExternalPersistenceManager is attached; call "
                "configure_external_persistence_manager(...) with your "
                "handler configuration first."
            )
        identifiers = manager.list_units("checkpoint", profile_name)
        overflow = identifiers[:-max_checkpoints] if (
            len(identifiers) > max_checkpoints
        ) else []
        for checkpoint_id in overflow:
            manager.delete_unit("checkpoint", checkpoint_id)
        return overflow

    def delete_cached_checkpoint(self, checkpoint_id: str) -> str:
        """
        Evict one checkpoint cached-item from the LOCAL cache by id.

        Purpose:
            System-rank passthrough of the cache's single-item delete
            (asset CRUD completion, 2026-07-11): removes one specific
            cached snapshot without touching neighbours or the sealed
            in-process ledger.

        Args:
            checkpoint_id:
                ULID identity of a previously flushed checkpoint.

        Returns:
            str: The deleted file's path (teach-grade evidence).

        Raises:
            RuntimeError: If the asset system has been cleaned.
            KeyError: If no cached item exists for `checkpoint_id`.
        """
        self.check_cleaned()
        with self._lock:
            return self._crystallizer_cache.delete_cached_item(
                checkpoint_id
            )

    def delete_formation(
            self,
            profile_name: str,
            formation_name: str,
            include_remote: bool = False,
    ) -> Dict[str, object]:
        """
        Delete one stored formation locally and, optionally, remotely.

        Purpose:
            The missing D of the formation CRUD square: formations are
            name-keyed, so no retention pass ever removes them - this is
            the only melder-driven formation delete lane.

        Contract:
            - The local leg always runs (teach-grade KeyError on miss).
            - The remote leg is opt-in and STRICT (mirrors the retention
              law: a failing delete propagates so the caller knows the
              remote was only partially trimmed); it requires the
              generic delete lane and refuses loudly without it.

        Args:
            profile_name:
                Owning profile.
            formation_name:
                The user-chosen formation name to delete.
            include_remote:
                When True, also delete the remote copy through the
                user's delete handler under kind "formation".

        Returns:
            Dict[str, object]: {"deleted_local_path": str,
            "remote_deleted": bool}.

        Raises:
            RuntimeError: If cleaned, or `include_remote` is set with no
                manager/delete lane attached.
            KeyError: If the local formation file does not exist.
        """
        self.check_cleaned()
        with self._lock:
            manager = self._external_persistence_manager
            deleted_local_path = self._crystallizer_cache.delete_formation(
                profile_name, formation_name
            )
        remote_deleted = False
        if include_remote:
            if manager is None:
                raise RuntimeError(
                    "include_remote=True but no ExternalPersistenceManager "
                    "is attached; call "
                    "configure_external_persistence_manager(...) first."
                )
            manager.delete_unit(
                MeshInterfaceContract.UNIT_KIND_FORMATION, formation_name
            )
            remote_deleted = True
        return {
            "deleted_local_path": deleted_local_path,
            "remote_deleted": remote_deleted,
        }

    def store_index_graft(
            self,
            profile_name: str,
            graft_record: Dict[str, object],
    ) -> str:
        """
        Ship one captured spell-index graft record to the user's store.

        Purpose:
            First-class mesh lane for graft records (they previously
            rode no kind - the user had to name one). The record's own
            index_id is the unit id, so grafts are fetchable by the
            identity the capture already carries.

        Contract:
            - Requires a manager with the generic store lane attached (loud
              refusal otherwise; the legacy upload lane cannot carry kinds).
              Handler PRESENCE governs this explicit store, NOT the automatic
              upload_on_flush knob (BUG-161).
            - The record must look like a graft: an "index_id" key is
              required (teach-grade ValueError otherwise). Deeper shape
              truth stays with the producer and the GraftRunner gate.

        Args:
            profile_name:
                The recording profile the graft belongs to.
            graft_record:
                The dict from Crystallizer.capture_index_graft(...).

        Returns:
            str: The unit id the record shipped under (its index_id).

        Raises:
            RuntimeError: If cleaned, no manager attached, the store lane
                is missing, or the remote store failed (lenient mode) - the
                graft lane has no local durable fallback, so a failed store
                is never reported as shipped.
            ValueError: If the record carries no "index_id".
        """
        self.check_cleaned()
        with self._lock:
            manager = self._external_persistence_manager
        if manager is None or not manager.has_store_handler:
            raise RuntimeError(
                "Storing a graft requires an attached manager with the "
                "generic store lane (with_store_handler)."
            )
        index_id = graft_record.get("index_id")
        if not isinstance(index_id, str) or not index_id:
            raise ValueError(
                "graft_record carries no 'index_id'; pass the dict from "
                "capture_index_graft(...) unmodified."
            )
        stored = manager.store_unit(
            MeshInterfaceContract.UNIT_KIND_INDEX_GRAFT,
            profile_name,
            index_id,
            dict(graft_record),
        )
        if not stored:
            # BUG-162: unlike checkpoint/formation writes, the graft lane
            # has NO local durable fallback. In lenient mode store_unit
            # swallows a handler failure into False (and counts it);
            # returning index_id here would report the graft durable when
            # its only copy never shipped, so a caller could discard it.
            raise RuntimeError(
                "graft {0!r} was not stored: the remote store handler "
                "failed (store_failure_count incremented) and this lane "
                "has no local durable fallback. Retry, or set "
                "strict_uploads to surface the handler error "
                "directly.".format(index_id)
            )
        return index_id

    def fetch_index_graft(self, index_id: str) -> Dict[str, object]:
        """
        Fetch one graft record back from the user's store, version-gated.

        Contract:
            - Requires the generic fetch lane (loud refusal otherwise).
            - Absent unit = teach-grade KeyError (a fetch you meant is a
              miss you should hear about).
            - RecordVersion.check_readable gates the payload before it
              is returned, mirroring from_cached_item's reader law.

        Args:
            index_id:
                The captured index id (the unit id grafts ship under).

        Returns:
            Dict[str, object]: The graft record, ready for graft_index.

        Raises:
            RuntimeError: If cleaned or no manager/fetch lane attached.
            ValueError: If the payload's record_version MAJOR is newer
                than this melder can read (RecordVersion.check_readable's
                contract - the reader-gate law).
            KeyError: If the remote store has no such graft.
        """
        self.check_cleaned()
        with self._lock:
            manager = self._external_persistence_manager
        if manager is None:
            raise RuntimeError(
                "Fetching a graft requires an attached manager with the "
                "generic fetch lane (with_fetch_handler)."
            )
        payload = manager.fetch_unit(
            MeshInterfaceContract.UNIT_KIND_INDEX_GRAFT, index_id
        )
        if payload is None:
            raise KeyError(
                "No stored index graft for id {0!r}; check "
                "list_index_grafts(profile).".format(index_id)
            )
        from melder.crystallizer.persistence.record_version import (
            RecordVersion,
        )
        RecordVersion.check_readable(payload, "index graft record")
        return dict(payload)

    def list_index_grafts(self, profile_name: str) -> List[str]:
        """
        List one profile's stored graft ids through the generic lane.

        Args:
            profile_name:
                Profile whose grafts are listed.

        Returns:
            List[str]: Unit ids (captured index ids) the store reports.

        Raises:
            RuntimeError: If cleaned or no manager/list lane attached.
        """
        self.check_cleaned()
        with self._lock:
            manager = self._external_persistence_manager
        if manager is None:
            raise RuntimeError(
                "Listing grafts requires an attached manager with the "
                "generic list lane (with_list_units_handler)."
            )
        return [
            str(unit_id)
            for unit_id in manager.list_units(
                MeshInterfaceContract.UNIT_KIND_INDEX_GRAFT, profile_name
            )
        ]

    def describe_external_interface(self) -> Dict[str, object]:
        """
        Emit the mesh interface contract joined with live presence.

        Purpose:
            The owner's "emit the table and the shape" verb at system
            rank: the static MeshInterfaceContract table plus THIS
            world's live handler presence, so a caller sees both what
            the interface is and which lanes are currently wired.

        Returns:
            Dict[str, object]: The stamped contract dict plus a
            "live_manager" key - the attached manager's describe()
            presence flags, or None when no manager is attached.

        Raises:
            RuntimeError: If the asset system has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            manager = self._external_persistence_manager
        contract = MeshInterfaceContract.describe()
        contract["live_manager"] = (
            manager.describe() if manager is not None else None
        )
        return contract

    @property
    def emission_tap_enabled(self) -> bool:
        """
        Return whether the opt-in emission tap should fire.

        Purpose:
            The emit() hot-path gate: the sink checks this BEFORE building
            a twin payload, so worlds without the tap pay one property
            read and nothing else.

        Returns:
            bool: True when a manager is attached with a store handler
            and stream_emissions opted in.
        """
        self.check_cleaned()
        with self._lock:
            manager = self._external_persistence_manager
        return manager is not None and manager.stream_emissions_enabled

    def stream_emission(
            self,
            profile_name: str,
            crystal_kind: str,
            payload: Dict[str, object],
    ) -> bool:
        """
        Ship one emission event through the user's store handler.

        Contract:
            - Each event rides a FRESH ULID unit id (events are a stream,
              not replace-on-emit rows) with a
              {"crystal_kind", "payload"} envelope.
            - Lenient + counted via the manager's store lane; the R-A
              covenant never blocks on a remote.
            - NO-OP (False) when the tap is not enabled.

        Args:
            profile_name:
                The recording profile.
            crystal_kind:
                The emitted twin's class name.
            payload:
                The twin's describe() dict.

        Returns:
            bool: True when the handler ran successfully.

        Raises:
            RuntimeError: If the asset system has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            manager = self._external_persistence_manager
        if manager is None or not manager.stream_emissions_enabled:
            return False
        from melder.utilities.helpers.ulid_factory import new_ulid
        from melder.crystallizer.persistence.record_version import (
            RecordVersion,
        )

        return manager.store_unit(
            "emission",
            profile_name,
            new_ulid(),
            RecordVersion.stamp({
                "crystal_kind": str(crystal_kind),
                "payload": dict(payload),
            }),
        )
