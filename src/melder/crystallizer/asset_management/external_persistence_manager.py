
import threading
from typing import Any, Callable, ClassVar, Dict, List, Optional

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.crystallizer.asset_management.external_persistence_manager_configuration import (
    ExternalPersistenceManagerConfiguration,
)
from melder.utilities.general_base.cleanable import Cleanable


class ExternalPersistenceManager(Cleanable):
    """
    User-callable transport for the crystallizer's external mesh.

    Purpose:
        Carry checkpoint cached-items, formations, index grafts, and emission
        events across a host-owned persistence boundary without imposing a
        database dependency. The user owns storage bootstrap, credentials,
        durability, and handler synchronization; Melder owns the value-shaped
        callable contract and failure accounting.

    Contract:
        - Constructed from and owns one frozen
          `ExternalPersistenceManagerConfiguration`; the containing
          `AssetManagementSystem` owns this manager.
        - Legacy checkpoint upload/download/list handlers bridge to the generic
          store/fetch/list lanes, allowing one handler family to carry the
          complete mesh.
        - Write lanes are handler-gated no-ops when absent. Failures follow the
          strictness knob: lenient by default so local custody survives remote
          failure; strict mode re-raises user exceptions.
        - Download lanes: missing handlers refuse loudly (a caller asking
          for remote history with no remote attached is a
          misconfiguration).
        - Handlers are LIVE USER CODE: they run outside any
          PersistenceSystem lock, and the manager never records them
          (presence flags only via describe()).

    Threading:
        Handler invocations are deliberately unguarded; user code owns its own
        synchronization and may be invoked concurrently. The manager lock
        protects only lenient failure-counter increments. The installed
        configuration is frozen and read-only while live.

    Lifecycle / Cleanup:
        Owned by one `AssetManagementSystem` at a time. Cleanup releases the
        owned configuration and counters but never calls a remote handler to
        close, delete, or otherwise mutate user storage.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_configuration",
        "_upload_failure_count",
        "_store_failure_count",
    ]

    def __init__(
            self,
            configuration: ExternalPersistenceManagerConfiguration,
    ) -> None:
        """
        Initialize the manager over one frozen configuration.

        Contract:
            Ownership of the already-frozen configuration transfers to this
            manager. No handler is invoked during construction, and both
            lenient failure counters start at zero.

        Args:
            configuration:
                The user's sealed handler configuration. Ownership
                transfers to this manager (cleanup cleans it).

        Returns:
            None.

        Raises:
            TypeError: If `configuration` is None or the wrong type.
            ValueError: If the configuration is not frozen.
        """
        super().__init__()
        if not isinstance(configuration, ExternalPersistenceManagerConfiguration):
            raise TypeError(
                "ExternalPersistenceManager requires a "
                "ExternalPersistenceManagerConfiguration."
            )
        if not configuration.frozen:
            raise ValueError(
                "ExternalPersistenceManagerConfiguration must be frozen before "
                "constructing the manager (call freeze())."
            )
        self._lock: threading.RLock = threading.RLock()
        self._configuration: ExternalPersistenceManagerConfiguration = configuration
        # Diagnostic surface for the lenient upload lane: callers/tests
        # can see how many remote pushes failed without raising.
        self._upload_failure_count: int = 0
        # Same posture for the generic mesh store lane (external_mesh
        # 2026-07-12): formation ships + emission-tap rows count here.
        self._store_failure_count: int = 0

    def cleanup(self) -> None:
        """
        Clean the owned configuration and mark the manager cleaned.

        Contract:
            - Idempotent and terminal; cleans the owned configuration before
              deleting counters and the manager lock.
            - Does not invoke upload, store, fetch, list, or delete handlers.
              Remote connection/resource lifetime remains the user's contract.

        Threading:
            Callers must quiesce handler invocations before cleanup; cleanup is
            not serialized against user callbacks.

        Lifecycle / Cleanup:
            The owning asset system cleans the manager before its local cache.
        """
        if self._cleaned:
            return
        self._cleaned = True
        if not self._configuration.cleaned:
            self._configuration.cleanup()
        del self._configuration
        del self._upload_failure_count
        del self._store_failure_count
        del self._lock

    @property
    def upload_enabled(self) -> bool:
        """
        Return whether the flush path should upload through this manager.

        Returns:
            bool: True when a WRITE lane is attached AND upload_on_flush
            is set. Since the generic mesh lane (external_mesh
            2026-07-12) the store handler counts: upload_checkpoint
            bridges to store_unit("checkpoint", ...) when no legacy
            upload handler exists, so a quartet-only configuration ships
            flushes exactly like the legacy trio (mirrors validate()'s
            widened write-lane rule).
        """
        self.check_cleaned()
        return (
            (
                self._configuration.upload_handler is not None
                or self._configuration.store_handler is not None
            )
            and self._configuration.upload_on_flush
        )

    @property
    def upload_failure_count(self) -> int:
        """
        Return how many lenient-mode uploads have failed so far.

        Returns:
            int: Count of swallowed-and-counted upload failures.
        """
        self.check_cleaned()
        return self._upload_failure_count

    def upload_checkpoint(
            self,
            profile_name: str,
            checkpoint_id: str,
            cached_item: Dict[str, object],
    ) -> bool:
        """
        Push one cached checkpoint item through the user's upload handler.

        Contract:
            - NO-OP (returns False) when no upload handler is attached.
            - Lenient default: a handler exception increments
              upload_failure_count and returns False - the local
              seal/cache lane never dies on a remote. strict_uploads=True
              re-raises instead. This documented best-effort posture is
              the ONLY sanctioned broad-except in this class.

        Args:
            profile_name:
                Owning profile (the handler's partitioning key).
            checkpoint_id:
                The item's ULID.
            cached_item:
                JSON-safe to_cached_item payload.

        Returns:
            bool: True when the handler ran successfully.

        Raises:
            RuntimeError: If the manager has been cleaned.
            Exception: The handler's own error, when strict_uploads.
        """
        self.check_cleaned()
        handler = self._configuration.upload_handler
        if handler is None:
            # LEGACY BRIDGE (external_mesh 2026-07-12): the generic store
            # lane carries checkpoints when no dedicated handler exists -
            # one callable set can serve the whole mesh.
            return self.store_unit(
                "checkpoint", profile_name, checkpoint_id, cached_item
            )
        try:
            handler(profile_name, checkpoint_id, dict(cached_item))
            return True
        except Exception:
            if self._configuration.strict_uploads:
                raise
            with self._lock:
                self._upload_failure_count += 1
            return False

    def download_checkpoint(
            self,
            checkpoint_id: str,
    ) -> Optional[Dict[str, object]]:
        """
        Fetch one cached checkpoint item through the download handler.

        Args:
            checkpoint_id:
                The wanted item's ULID.

        Returns:
            Optional[Dict[str, object]]:
                The stored cached-item payload, or None when the remote
                does not hold the id.

        Raises:
            RuntimeError: If cleaned, or no download handler is attached
                (asking for remote history with no remote is a
                misconfiguration, refused loudly).
        """
        self.check_cleaned()
        handler = self._configuration.download_handler
        if handler is None:
            # LEGACY BRIDGE: the generic fetch lane serves checkpoints
            # when no dedicated handler exists; only a fully read-less
            # configuration refuses.
            if self._configuration.fetch_handler is not None:
                return self.fetch_unit("checkpoint", checkpoint_id)
            raise RuntimeError(
                "ExternalPersistenceManager has no download handler attached; "
                "attach one via with_download_handler(...) or "
                "with_fetch_handler(...) before asking for remote "
                "checkpoints."
            )
        payload = handler(checkpoint_id)
        return dict(payload) if payload is not None else None

    def download_profile(
            self,
            profile_name: str,
    ) -> List[Dict[str, object]]:
        """
        Fetch EVERY stored checkpoint item of one profile.

        Contract:
            - Requires BOTH the list and download handlers.
            - Ids sort into ULID (creation) order before download; an id
              the list reported but download returns None for raises
              (the remote contradicted itself - refuse loudly).

        Args:
            profile_name:
                Profile whose remote history is wanted.

        Returns:
            List[Dict[str, object]]:
                Cached-item payloads, oldest first (possibly empty).

        Raises:
            RuntimeError: If cleaned, or either handler is missing.
            ValueError: If the remote lists an id it cannot return.
        """
        self.check_cleaned()
        list_handler = self._configuration.list_handler
        if list_handler is None:
            # LEGACY BRIDGE: the generic listing lane serves checkpoint
            # history when no dedicated handler exists.
            if self._configuration.list_units_handler is not None:
                identifiers = self.list_units("checkpoint", profile_name)
            else:
                raise RuntimeError(
                    "ExternalPersistenceManager has no list handler attached; "
                    "attach one via with_list_handler(...) or "
                    "with_list_units_handler(...) before asking for a "
                    "profile's remote history."
                )
        else:
            identifiers = sorted(
                str(entry) for entry in list_handler(profile_name)
            )
        payloads: List[Dict[str, object]] = []
        for checkpoint_id in identifiers:
            payload = self.download_checkpoint(checkpoint_id)
            if payload is None:
                raise ValueError(
                    "Remote listed checkpoint {0!r} for profile {1!r} "
                    "but returned nothing for it - the remote store is "
                    "inconsistent; repair it before reloading.".format(
                        checkpoint_id, profile_name
                    )
                )
            payloads.append(payload)
        return payloads

    @property
    def store_enabled(self) -> bool:
        """
        Return whether flush-shipped mesh lanes should store remote.

        Returns:
            bool: True when a store handler is attached AND
            upload_on_flush is set (the flush knob governs every
            flush-shipped lane, legacy and generic alike).
        """
        self.check_cleaned()
        return (
            self._configuration.store_handler is not None
            and self._configuration.upload_on_flush
        )

    @property
    def has_store_handler(self) -> bool:
        """
        Return whether a generic store handler is attached.

        Returns:
            bool: True when a store handler is wired, independent of the
            upload_on_flush knob. Explicit store operations (e.g. graft
            storage) depend on handler PRESENCE, not on the automatic
            checkpoint-flush upload policy (BUG-161).
        """
        self.check_cleaned()
        return self._configuration.store_handler is not None

    @property
    def stream_emissions_enabled(self) -> bool:
        """
        Return whether the opt-in emission tap should fire.

        Returns:
            bool: True when a store handler is attached AND
            stream_emissions was opted in.
        """
        self.check_cleaned()
        return (
            self._configuration.store_handler is not None
            and self._configuration.stream_emissions
        )

    @property
    def store_failure_count(self) -> int:
        """
        Return how many lenient-mode generic stores have failed so far.

        Returns:
            int: Count of swallowed-and-counted store failures.
        """
        self.check_cleaned()
        return self._store_failure_count

    def store_unit(
            self,
            kind: str,
            profile_name: str,
            unit_id: str,
            payload: Dict[str, object],
    ) -> bool:
        """
        Push one mesh unit through the user's generic store handler.

        Contract:
            - NO-OP (returns False) when no store handler is attached.
            - Lenient default mirrors the upload lane: handler exceptions
              increment store_failure_count and return False;
              strict_uploads=True re-raises. This is the second sanctioned
              broad-except in this class (same documented posture).

        Args:
            kind:
                Mesh unit kind ("checkpoint" | "formation" | "emission").
            profile_name:
                Owning profile (the handler's partitioning key).
            unit_id:
                The unit's identity (ULID / formation name / event ULID).
            payload:
                JSON-safe unit payload.

        Returns:
            bool: True when the handler ran successfully.

        Raises:
            RuntimeError: If the manager has been cleaned.
            Exception: The handler's own error, when strict_uploads.
        """
        self.check_cleaned()
        handler = self._configuration.store_handler
        if handler is None:
            return False
        try:
            handler(str(kind), profile_name, unit_id, dict(payload))
            return True
        except Exception:
            if self._configuration.strict_uploads:
                raise
            with self._lock:
                self._store_failure_count += 1
            return False

    def fetch_unit(
            self,
            kind: str,
            unit_id: str,
    ) -> Optional[Dict[str, object]]:
        """
        Fetch one mesh unit through the user's generic fetch handler.

        Args:
            kind:
                Mesh unit kind.
            unit_id:
                The wanted unit's identity.

        Returns:
            Optional[Dict[str, object]]:
                The stored payload, or None when the remote lacks it.

        Raises:
            RuntimeError: If cleaned, or no fetch handler is attached
                (asking for remote units with no read lane is a
                misconfiguration, refused loudly).
        """
        self.check_cleaned()
        handler = self._configuration.fetch_handler
        if handler is None:
            raise RuntimeError(
                "ExternalPersistenceManager has no fetch handler attached; "
                "attach one via with_fetch_handler(...) before asking for "
                "remote mesh units."
            )
        payload = handler(str(kind), unit_id)
        return dict(payload) if payload is not None else None

    def list_units(
            self,
            kind: str,
            profile_name: str,
    ) -> List[str]:
        """
        List one kind's stored unit ids through the user's handler.

        Args:
            kind:
                Mesh unit kind.
            profile_name:
                Profile whose units are wanted.

        Returns:
            List[str]: Sorted unit ids (ULID kinds sort into creation
            order for free).

        Raises:
            RuntimeError: If cleaned, or no list-units handler attached.
        """
        self.check_cleaned()
        handler = self._configuration.list_units_handler
        if handler is None:
            raise RuntimeError(
                "ExternalPersistenceManager has no list-units handler "
                "attached; attach one via with_list_units_handler(...) "
                "before asking for remote unit listings."
            )
        return sorted(str(entry) for entry in handler(str(kind), profile_name))

    def delete_unit(self, kind: str, unit_id: str) -> None:
        """
        Delete one mesh unit through the user's opt-in delete handler.

        Contract:
            - Retention is opt-in (owner ruling 2026-07-12; the
              2026-07-07 "remote retention is the DB owner's business"
              default stands without this handler): no handler = loud
              refusal, never a silent skip.
            - Deletes are NOT lenient: a retention pass that silently
              half-runs would lie about the remote's contents.

        Args:
            kind:
                Mesh unit kind.
            unit_id:
                The unit to delete.

        Returns:
            None.

        Raises:
            RuntimeError: If cleaned, or no delete handler is attached.
            Exception: The handler's own error (propagated).
        """
        self.check_cleaned()
        handler = self._configuration.delete_handler
        if handler is None:
            raise RuntimeError(
                "ExternalPersistenceManager has no delete handler attached; "
                "attach one via with_delete_handler(...) before asking for "
                "remote retention."
            )
        handler(str(kind), unit_id)

    def describe(self) -> Dict[str, object]:
        """
        Return the record-safe description of this manager.

        Contract:
            - Callables appear as presence flags only (record law).

        Returns:
            Dict[str, object]: Presence payload + failure diagnostics.
        """
        self.check_cleaned()
        description = self._configuration.describe_presence()
        description["upload_failure_count"] = self._upload_failure_count
        description["store_failure_count"] = self._store_failure_count
        return description
