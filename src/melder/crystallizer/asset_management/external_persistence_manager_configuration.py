
import threading
from typing import Any, Callable, ClassVar, Dict, List, Optional

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class ExternalPersistenceManagerConfiguration(Cleanable):
    """
    Handler configuration for the optional external persistence mesh.

    Purpose:
        Connect crystallizer assets to storage chosen by the application. New
        integrations should normally provide the generic store/fetch/list/delete
        handlers, which carry checkpoints, formations, grafts, and emission
        events. The legacy upload/download/list trio remains available for
        checkpoint-only integrations. Deployments that do not need custom
        storage code can register the first-party `SqliteMeshAdapter` handlers.

    Guidance:
        Callables belong in this separate configuration because executable code
        cannot be serialized into a world record. Author the handlers, choose
        failure/streaming posture, then pass the configuration to
        `Crystallizer.configure_external_persistence_manager(...)`; that facade
        freezes it if necessary and transfers ownership to the asset system.
        A read-only configuration must explicitly disable upload-on-flush.

    Contract:
        - Records expose handler presence flags, never callable objects.
        - Authoring is fluent and mutation closes at `freeze()`.
        - Generic and legacy checkpoint handlers may coexist; legacy handlers
          take the checkpoint-specific path while generic handlers carry the
          rest of the mesh and provide fallback checkpoint transport.
        - Storage credentials, connection lifetime, transactions, and handler
          synchronization remain application responsibilities.

    Threading:
        An `RLock` serializes authoring. Frozen instances are effectively
        immutable, but the eventual handler callables must provide any
        synchronization required by their storage client.

    Lifecycle / Cleanup:
        Caller-owned until attached through the crystallizer facade, after which
        the asset-owned manager owns and eventually cleans it. Cleanup drops
        callable references but never invokes them or deletes remote data.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel

    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frozen",
        "_upload_handler",
        "_download_handler",
        "_list_handler",
        "_upload_on_flush",
        "_strict_uploads",
        "_store_handler",
        "_fetch_handler",
        "_list_units_handler",
        "_delete_handler",
        "_stream_emissions",
    ]

    def __init__(self) -> None:
        """
        Initialize one empty manager configuration (no handlers attached).

        Contract:
            Upload-on-flush defaults True and strict failures/streaming default
            False. Therefore the empty object is intentionally not valid for
            freezing until a write handler is attached or upload-on-flush is
            disabled for a read-only deployment.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frozen: bool = False
        # Optional handler contract: None means "lane not attached"; the
        # manager NO-OPs (upload) or refuses loudly (download/list) on
        # missing handlers per its own verbs.
        self._upload_handler: Optional[Callable[..., Any]] = None
        self._download_handler: Optional[Callable[..., Any]] = None
        self._list_handler: Optional[Callable[..., Any]] = None
        self._upload_on_flush: bool = True
        self._strict_uploads: bool = False
        # Generic mesh lane (external_mesh 2026-07-12): kind-partitioned
        # callables carrying ANY mesh unit (checkpoint/formation/emission).
        # The legacy checkpoint trio above stays byte-compatible; the
        # manager bridges to these when the legacy slots are empty.
        self._store_handler: Optional[Callable[..., Any]] = None
        self._fetch_handler: Optional[Callable[..., Any]] = None
        self._list_units_handler: Optional[Callable[..., Any]] = None
        self._delete_handler: Optional[Callable[..., Any]] = None
        self._stream_emissions: bool = False

    def cleanup(self) -> None:
        """
        Release owned fields and mark the configuration cleaned.

        Contract:
            - Idempotent and terminal; drops every handler reference, knob,
              identity field, and the authoring lock.
            - Does not call user handlers and does not mutate external storage.

        Threading:
            Authoring and handler installation must be quiescent before cleanup.

        Lifecycle / Cleanup:
            Performed by the current owner: caller before attachment or the
            external manager after ownership transfer.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._id
        del self._upload_handler
        del self._download_handler
        del self._list_handler
        del self._upload_on_flush
        del self._strict_uploads
        del self._store_handler
        del self._fetch_handler
        del self._list_units_handler
        del self._delete_handler
        del self._stream_emissions
        del self._frozen
        del self._lock

    @property
    def id(self) -> str:
        """
        Return the stable configuration id.

        Returns:
            str: ULID minted at construction.
        """
        self.check_cleaned()
        return self._id

    @property
    def frozen(self) -> bool:
        """
        Return whether the configuration has been sealed.

        Returns:
            bool: True after freeze().
        """
        self.check_cleaned()
        return self._frozen

    @property
    def upload_handler(self) -> Optional[Callable[..., Any]]:
        """
        Return the attached upload callable, if any.

        Returns:
            Optional[Callable]: The handler or None (lane not attached).
        """
        self.check_cleaned()
        return self._upload_handler

    @property
    def download_handler(self) -> Optional[Callable[..., Any]]:
        """
        Return the attached download callable, if any.

        Returns:
            Optional[Callable]: The handler or None (lane not attached).
        """
        self.check_cleaned()
        return self._download_handler

    @property
    def list_handler(self) -> Optional[Callable[..., Any]]:
        """
        Return the attached list callable, if any.

        Returns:
            Optional[Callable]: The handler or None (lane not attached).
        """
        self.check_cleaned()
        return self._list_handler

    @property
    def upload_on_flush(self) -> bool:
        """
        Return whether flushes also upload through the manager.

        Returns:
            bool: True when the flush path uploads (default).
        """
        self.check_cleaned()
        return self._upload_on_flush

    @property
    def strict_uploads(self) -> bool:
        """
        Return the upload failure posture.

        Returns:
            bool: True when upload failures raise; False when they log
            and continue (default - the local seal/cache lane must never
            die on a remote).
        """
        self.check_cleaned()
        return self._strict_uploads

    @property
    def store_handler(self) -> Optional[Callable[..., Any]]:
        """
        Return the generic mesh store callable (None = lane not attached).

        Returns:
            Optional[Callable]: The handler or None.
        """
        self.check_cleaned()
        return self._store_handler

    @property
    def fetch_handler(self) -> Optional[Callable[..., Any]]:
        """
        Return the generic mesh fetch callable (None = lane not attached).

        Returns:
            Optional[Callable]: The handler or None.
        """
        self.check_cleaned()
        return self._fetch_handler

    @property
    def list_units_handler(self) -> Optional[Callable[..., Any]]:
        """
        Return the generic unit-listing callable (None = not attached).

        Returns:
            Optional[Callable]: The handler or None.
        """
        self.check_cleaned()
        return self._list_units_handler

    @property
    def delete_handler(self) -> Optional[Callable[..., Any]]:
        """
        Return the remote delete callable (None = retention not attached).

        Returns:
            Optional[Callable]: The handler or None.
        """
        self.check_cleaned()
        return self._delete_handler

    @property
    def stream_emissions(self) -> bool:
        """
        Return whether every crystallizer emission streams remote.

        Returns:
            bool: The opt-in tap flag, default False.
        """
        self.check_cleaned()
        return self._stream_emissions

    def with_store_handler(
            self,
            handler: Callable[..., Any],
    ) -> "ExternalPersistenceManagerConfiguration":
        """
        Attach the generic mesh store callable and return `self`.

        Contract:
            - Signature: handler(kind: str, profile_name: str,
              unit_id: str, payload: Dict[str, object]) -> None. Kinds
              today: "checkpoint" (via the legacy bridge), "formation",
              "emission" (the opt-in tap). One callable, one table with a
              kind column, any DB stack - melder never imports it.

        Args:
            handler:
                The user's store callable.

        Returns:
            ExternalPersistenceManagerConfiguration: This instance (fluent).

        Raises:
            RuntimeError: If cleaned or already frozen.
            TypeError: If `handler` is not callable.
        """
        self.check_cleaned()
        if not callable(handler):
            raise TypeError("store handler must be callable.")
        with self._lock:
            if self._frozen:
                raise RuntimeError(
                    "Cannot modify ExternalPersistenceManagerConfiguration after "
                    "freeze."
                )
            self._store_handler = handler
        return self

    def with_fetch_handler(
            self,
            handler: Callable[..., Any],
    ) -> "ExternalPersistenceManagerConfiguration":
        """
        Attach the generic mesh fetch callable and return `self`.

        Contract:
            - Signature: handler(kind: str, unit_id: str) ->
              Optional[Dict[str, object]] (the stored payload, or None
              when the unit is unknown remotely).

        Args:
            handler:
                The user's fetch callable.

        Returns:
            ExternalPersistenceManagerConfiguration: This instance (fluent).

        Raises:
            RuntimeError: If cleaned or already frozen.
            TypeError: If `handler` is not callable.
        """
        self.check_cleaned()
        if not callable(handler):
            raise TypeError("fetch handler must be callable.")
        with self._lock:
            if self._frozen:
                raise RuntimeError(
                    "Cannot modify ExternalPersistenceManagerConfiguration after "
                    "freeze."
                )
            self._fetch_handler = handler
        return self

    def with_list_units_handler(
            self,
            handler: Callable[..., Any],
    ) -> "ExternalPersistenceManagerConfiguration":
        """
        Attach the generic unit-listing callable and return `self`.

        Contract:
            - Signature: handler(kind: str, profile_name: str) ->
              Iterable[str] (the stored unit ids of that kind/profile).

        Args:
            handler:
                The user's listing callable.

        Returns:
            ExternalPersistenceManagerConfiguration: This instance (fluent).

        Raises:
            RuntimeError: If cleaned or already frozen.
            TypeError: If `handler` is not callable.
        """
        self.check_cleaned()
        if not callable(handler):
            raise TypeError("list units handler must be callable.")
        with self._lock:
            if self._frozen:
                raise RuntimeError(
                    "Cannot modify ExternalPersistenceManagerConfiguration after "
                    "freeze."
                )
            self._list_units_handler = handler
        return self

    def with_delete_handler(
            self,
            handler: Callable[..., Any],
    ) -> "ExternalPersistenceManagerConfiguration":
        """
        Attach the remote delete callable and return `self` (retention
        opt-in; the 2026-07-07 "remote retention is the DB owner's
        business" default stands unless this lane is attached).

        Contract:
            - Signature: handler(kind: str, unit_id: str) -> None.

        Args:
            handler:
                The user's delete callable.

        Returns:
            ExternalPersistenceManagerConfiguration: This instance (fluent).

        Raises:
            RuntimeError: If cleaned or already frozen.
            TypeError: If `handler` is not callable.
        """
        self.check_cleaned()
        if not callable(handler):
            raise TypeError("delete handler must be callable.")
        with self._lock:
            if self._frozen:
                raise RuntimeError(
                    "Cannot modify ExternalPersistenceManagerConfiguration after "
                    "freeze."
                )
            self._delete_handler = handler
        return self

    def with_stream_emissions(
            self,
            enabled: bool,
    ) -> "ExternalPersistenceManagerConfiguration":
        """
        Set the opt-in emission tap and return `self`.

        Contract:
            - True streams EVERY crystallizer emission through the store
              handler as a delta row (kind="emission"; lenient+counted -
              a dying DB never blocks the record). Chatty by nature: one
              bind can emit several twins; the choice is per-deployment.

        Args:
            enabled:
                Whether the tap is on.

        Returns:
            ExternalPersistenceManagerConfiguration: This instance (fluent).

        Raises:
            RuntimeError: If cleaned or already frozen.
        """
        self.check_cleaned()
        with self._lock:
            if self._frozen:
                raise RuntimeError(
                    "Cannot modify ExternalPersistenceManagerConfiguration after "
                    "freeze."
                )
            self._stream_emissions = bool(enabled)
        return self

    def with_upload_handler(
            self,
            handler: Callable[..., Any],
    ) -> "ExternalPersistenceManagerConfiguration":
        """
        Attach the upload callable and return `self`.

        Contract:
            - Signature: handler(profile_name: str, checkpoint_id: str,
              cached_item: Dict[str, object]) -> None. The cached item is
              the JSON-safe to_cached_item form - implement with any DB
              stack (psycopg, sqlite3, boto3, ...); melder never imports
              it.

        Args:
            handler:
                The user's upload callable.

        Returns:
            ExternalPersistenceManagerConfiguration: This instance (fluent).

        Raises:
            RuntimeError: If cleaned or already frozen.
            TypeError: If `handler` is not callable.
        """
        self.check_cleaned()
        if not callable(handler):
            raise TypeError("upload handler must be callable.")
        with self._lock:
            if self._frozen:
                raise RuntimeError(
                    "Cannot modify ExternalPersistenceManagerConfiguration after "
                    "freeze."
                )
            self._upload_handler = handler
        return self

    def with_download_handler(
            self,
            handler: Callable[..., Any],
    ) -> "ExternalPersistenceManagerConfiguration":
        """
        Attach the download callable and return `self`.

        Contract:
            - Signature: handler(checkpoint_id: str) ->
              Optional[Dict[str, object]] (the stored cached-item form,
              or None when the id is unknown remotely).

        Args:
            handler:
                The user's download callable.

        Returns:
            ExternalPersistenceManagerConfiguration: This instance (fluent).

        Raises:
            RuntimeError: If cleaned or already frozen.
            TypeError: If `handler` is not callable.
        """
        self.check_cleaned()
        if not callable(handler):
            raise TypeError("download handler must be callable.")
        with self._lock:
            if self._frozen:
                raise RuntimeError(
                    "Cannot modify ExternalPersistenceManagerConfiguration after "
                    "freeze."
                )
            self._download_handler = handler
        return self

    def with_list_handler(
            self,
            handler: Callable[..., Any],
    ) -> "ExternalPersistenceManagerConfiguration":
        """
        Attach the list callable and return `self`.

        Contract:
            - Signature: handler(profile_name: str) -> `Iterable[str]`
              containing remotely stored checkpoint ids for the profile. The
              manager returns lexical ULID order; this is timestamp ordered but
              does not prove exact ordering inside one millisecond.

        Args:
            handler:
                The user's list callable.

        Returns:
            ExternalPersistenceManagerConfiguration: This instance (fluent).

        Raises:
            RuntimeError: If cleaned or already frozen.
            TypeError: If `handler` is not callable.
        """
        self.check_cleaned()
        if not callable(handler):
            raise TypeError("list handler must be callable.")
        with self._lock:
            if self._frozen:
                raise RuntimeError(
                    "Cannot modify ExternalPersistenceManagerConfiguration after "
                    "freeze."
                )
            self._list_handler = handler
        return self

    def with_upload_on_flush(
            self,
            enabled: bool,
    ) -> "ExternalPersistenceManagerConfiguration":
        """
        Set whether flushes also upload, and return `self`.

        Args:
            enabled:
                True routes every flushed item through the upload
                handler.

        Returns:
            ExternalPersistenceManagerConfiguration: This instance (fluent).

        Raises:
            RuntimeError: If cleaned or already frozen.
            TypeError: If `enabled` is not a bool.
        """
        self.check_cleaned()
        if not isinstance(enabled, bool):
            raise TypeError("upload_on_flush must be a bool.")
        with self._lock:
            if self._frozen:
                raise RuntimeError(
                    "Cannot modify ExternalPersistenceManagerConfiguration after "
                    "freeze."
                )
            self._upload_on_flush = enabled
        return self

    def with_strict_uploads(
            self,
            enabled: bool,
    ) -> "ExternalPersistenceManagerConfiguration":
        """
        Set the upload failure posture, and return `self`.

        Args:
            enabled:
                True makes write-handler failures raise; False counts the
                failure and continues (default), preserving local custody.

        Returns:
            ExternalPersistenceManagerConfiguration: This instance (fluent).

        Raises:
            RuntimeError: If cleaned or already frozen.
            TypeError: If `enabled` is not a bool.
        """
        self.check_cleaned()
        if not isinstance(enabled, bool):
            raise TypeError("strict_uploads must be a bool.")
        with self._lock:
            if self._frozen:
                raise RuntimeError(
                    "Cannot modify ExternalPersistenceManagerConfiguration after "
                    "freeze."
                )
            self._strict_uploads = enabled
        return self

    def validate(self) -> bool:
        """
        Validate the attached handlers and knobs.

        Returns:
            bool: True when valid.

        Raises:
            ValueError: If upload_on_flush is enabled with no WRITE lane
                attached (a knob pointing at nothing is a
                misconfiguration, not a no-op). Since the generic mesh
                lane (external_mesh 2026-07-12), the store handler
                satisfies the flush knob - the legacy bridge ships
                checkpoints through it. Read-only configurations
                (fetch/list only) must disable the knob explicitly.
        """
        self.check_cleaned()
        if (
            self._upload_on_flush
            and self._upload_handler is None
            and self._store_handler is None
        ):
            raise ValueError(
                "upload_on_flush is enabled but no write lane is "
                "attached. Attach one via with_upload_handler(...) or "
                "with_store_handler(...), or disable "
                "with_upload_on_flush(False) for read-only "
                "configurations."
            )
        return True

    def freeze(self) -> None:
        """
        Validate and seal the configuration.

        Purpose:
            Close handler authoring before ownership transfers to the live
            manager. Most callers can let the crystallizer facade invoke this
            automatically during attachment.

        Contract:
            - Idempotent when already frozen.
            - NO twin emission here: this configuration carries live
              callables and records as presence flags only through the
              manager's description surface.

        Returns:
            None.

        Raises:
            ValueError: If validation fails.
        """
        self.check_cleaned()
        if self._frozen:
            return
        if not self.validate():
            raise ValueError(
                "ExternalPersistenceManagerConfiguration validation failed."
            )
        with self._lock:
            self._frozen = True

    def describe_presence(self) -> Dict[str, object]:
        """
        Return the record-safe presence description of this configuration.

        Contract:
            - Callables appear as PRESENCE FLAGS only (record law); knobs
              appear as their plain values.

        Returns:
            Dict[str, object]: Plain-value presence payload.
        """
        self.check_cleaned()
        return {
            "upload_handler_present": self._upload_handler is not None,
            "download_handler_present": self._download_handler is not None,
            "list_handler_present": self._list_handler is not None,
            "upload_on_flush": self._upload_on_flush,
            "strict_uploads": self._strict_uploads,
            "store_handler_present": self._store_handler is not None,
            "fetch_handler_present": self._fetch_handler is not None,
            "list_units_handler_present": (
                self._list_units_handler is not None
            ),
            "delete_handler_present": self._delete_handler is not None,
            "stream_emissions": self._stream_emissions,
        }
