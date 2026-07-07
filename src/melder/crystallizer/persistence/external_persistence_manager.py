
import threading
from typing import Any, Callable, ClassVar, Dict, List, Optional

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.crystallizer.persistence.external_persistence_manager_configuration import (
    ExternalPersistenceManagerConfiguration,
)
from melder.utilities.general_base.cleanable import Cleanable


class ExternalPersistenceManager(Cleanable):
    """
    Remote transport owner for cached checkpoint items (the DB opt-in).

    Purpose:
        Owns UPLOADING and DOWNLOADING of checkpoint cached-items through
        USER-ATTACHED callables (owner ruling: the local cache caps at
        the checkpoint limit; durability beyond it is the user's DB -
        their SQL bootstrap, their secrets, their driver; melder owns the
        seam only, no third-party dependency).

    Contract:
        - Constructed from a FROZEN ExternalPersistenceManagerConfiguration;
          owned by PersistenceSystem (which owns all caches/transports).
        - Upload lane: handler-gated NO-OP when no upload handler is
          attached; failures follow the strictness knob (lenient default
          - the local seal/cache lane must never die on a remote).
        - Download lanes: missing handlers refuse loudly (a caller asking
          for remote history with no remote attached is a
          misconfiguration).
        - Handlers are LIVE USER CODE: they run outside any
          PersistenceSystem lock, and the manager never records them
          (presence flags only via describe()).

    Threading:
        The manager's own lock guards its lifecycle fields only; handler
        invocations are deliberately unguarded (user code owns its own
        synchronization; 3.14t nogil callers may invoke concurrently).

    Lifecycle:
        Owned by exactly one PersistenceSystem. cleanup() cleans the
        owned configuration and deletes owned fields; idempotent.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_configuration",
        "_upload_failure_count",
    ]

    def __init__(
            self,
            configuration: ExternalPersistenceManagerConfiguration,
    ) -> None:
        """
        Initialize the manager over one frozen configuration.

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

    def cleanup(self) -> None:
        """
        Clean the owned configuration and mark the manager cleaned.

        Contract:
            - Idempotent; children first, then del posture.
        """
        if self._cleaned:
            return
        self._cleaned = True
        if not self._configuration.cleaned:
            self._configuration.cleanup()
        del self._configuration
        del self._upload_failure_count
        del self._lock

    @property
    def upload_enabled(self) -> bool:
        """
        Return whether the flush path should upload through this manager.

        Returns:
            bool: True when an upload handler is attached AND
            upload_on_flush is set.
        """
        self.check_cleaned()
        return (
            self._configuration.upload_handler is not None
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
            return False
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
            raise RuntimeError(
                "ExternalPersistenceManager has no download handler attached; "
                "attach one via with_download_handler(...) before asking "
                "for remote checkpoints."
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
            raise RuntimeError(
                "ExternalPersistenceManager has no list handler attached; attach "
                "one via with_list_handler(...) before asking for a "
                "profile's remote history."
            )
        payloads: List[Dict[str, object]] = []
        for checkpoint_id in sorted(
                str(entry) for entry in list_handler(profile_name)
        ):
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
        return description
