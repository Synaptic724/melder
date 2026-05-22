import threading
from typing import TYPE_CHECKING, Any, Dict, Iterable, Optional, Tuple, ClassVar

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
        DevopsInformationRegistry,
    )


class DevopsIdentity(Cleanable):
    """
    Frame-local dev-ops identity surface for runtime objects.

    Purpose:
        Provide one stable identity record that frame-owned runtime objects can
        register into `DevopsInformationRegistry`. The identity describes what
        the object is, which frame it belongs to, and which transaction kinds
        it can originate.

    Contract:
        - `owner_kind`, `owner_id`, and `aetheric_frame_name` are stable.
        - `available_transactions` is a normalized tuple of lowercase names.
        - `metadata` changes only through explicit helper methods.
        - When attached to a registry, cleanup unregisters the identity before
          the identity surface is torn down.

    Threading:
        - Internal mutation is guarded by an `RLock`.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_owner_kind",
        "_owner_id",
        "_aetheric_frame_name",
        "_metadata",
        "_available_transactions",
        "_registry",
    ]

    def __init__(
            self,
            *,
            owner_kind: str,
            owner_id: str,
            aetheric_frame_name: str,
            metadata: Optional[Dict[str, Any]] = None,
            available_transactions: Optional[Iterable[str]] = None,
    ) -> None:
        """
        Initialize one dev-ops identity record.

        Args:
            owner_kind:
                Stable owner kind such as `spellbook`, `conduit`, or
                `conduit_cluster`.
            owner_id:
                Stable object identifier inside the frame.
            aetheric_frame_name:
                Frame name the object belongs to.
            metadata:
                Optional detached descriptive metadata.
            available_transactions:
                Optional iterable of lowercase transaction names the object may
                originate.

        Raises:
            TypeError:
                If any required identity field is not a string.
            ValueError:
                If any required identity field is empty.
        """
        super().__init__()
        for field_name, value in (
            ("owner_kind", owner_kind),
            ("owner_id", owner_id),
            ("aetheric_frame_name", aetheric_frame_name),
        ):
            if not isinstance(value, str):
                raise TypeError(f"{field_name} must be a string.")
            if not value.strip():
                raise ValueError(f"{field_name} must not be empty.")

        self._lock: threading.RLock = threading.RLock()
        self._owner_kind: str = owner_kind.strip().lower()
        self._owner_id: str = owner_id
        self._aetheric_frame_name: str = aetheric_frame_name
        self._metadata: Dict[str, Any] = dict(metadata) if metadata else {}
        self._available_transactions: Tuple[str, ...] = tuple(
            sorted(
                {
                    str(item).strip().lower()
                    for item in (available_transactions or ())
                    if str(item).strip()
                }
            )
        )
        self._registry: Optional["DevopsInformationRegistry"] = None

    def cleanup(self) -> None:
        """
        Idempotently retire this identity and unregister it from the registry.
        """
        if self._cleaned:
            return
        registry = None
        owner_kind = None
        owner_id = None
        with self._lock:
            if self._cleaned:
                return
            registry = self._registry
            owner_kind = self._owner_kind
            owner_id = self._owner_id
            self._registry = None
        if registry is not None:
            try:
                registry.unregister_identity(
                    owner_kind=owner_kind,
                    owner_id=owner_id,
                )
            except Exception:
                pass
        with self._lock:
            self._cleaned = True
            self._metadata.clear()
            del self._owner_kind
            del self._owner_id
            del self._aetheric_frame_name
            del self._metadata
            del self._available_transactions
            del self._registry
        del self._lock

    @property
    def owner_kind(self) -> str:
        """
        Return the normalized owner kind label.
        """
        self.check_cleaned()
        return self._owner_kind

    @property
    def owner_id(self) -> str:
        """
        Return the stable owner identifier.
        """
        self.check_cleaned()
        return self._owner_id

    @property
    def aetheric_frame_name(self) -> str:
        """
        Return the owning frame name for this identity.
        """
        self.check_cleaned()
        return self._aetheric_frame_name

    @property
    def metadata(self) -> Dict[str, Any]:
        """
        Return a detached metadata snapshot.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._metadata)

    @property
    def available_transactions(self) -> Tuple[str, ...]:
        """
        Return the declared transaction kinds for this identity.
        """
        self.check_cleaned()
        with self._lock:
            return self._available_transactions

    def supports_transaction(self, transaction_name: str) -> bool:
        """
        Return whether this identity declares the given transaction kind.
        """
        self.check_cleaned()
        if not isinstance(transaction_name, str):
            raise TypeError("transaction_name must be a string.")
        normalized_name = transaction_name.strip().lower()
        if not normalized_name:
            raise ValueError("transaction_name must not be empty.")
        with self._lock:
            return normalized_name in self._available_transactions

    def set_available_transactions(
            self,
            transaction_names: Iterable[str],
    ) -> None:
        """
        Replace the declared available transaction kinds.
        """
        self.check_cleaned()
        normalized = tuple(
            sorted(
                {
                    str(item).strip().lower()
                    for item in transaction_names
                    if str(item).strip()
                }
            )
        )
        with self._lock:
            self._available_transactions = normalized

    def update_metadata(self, **metadata: Any) -> None:
        """
        Merge descriptive metadata into this identity.
        """
        self.check_cleaned()
        with self._lock:
            self._metadata.update(metadata)

    def attach_registry(
            self,
            registry: "DevopsInformationRegistry",
            *,
            object_ref: Optional[Any] = None,
    ) -> None:
        """
        Attach and register this identity with one frame-owned registry.

        Args:
            registry:
                Registry that should own this identity entry.
            object_ref:
                Optional live object reference to store beside the identity.

        Raises:
            ValueError:
                If registry is None.
            RuntimeError:
                If already attached to a different registry.
        """
        self.check_cleaned()
        if registry is None:
            raise ValueError("registry must not be None.")
        with self._lock:
            if self._registry is not None and self._registry is not registry:
                raise RuntimeError(
                    "DevopsIdentity is already attached to a different registry."
                )
            self._registry = registry
        try:
            registry.register_identity(self, object_ref=object_ref)
        except Exception:
            with self._lock:
                if self._registry is registry:
                    self._registry = None
            raise

    def detach_registry(self) -> None:
        """
        Detach this identity from the currently attached registry, if any.
        """
        self.check_cleaned()
        registry = None
        with self._lock:
            registry = self._registry
            self._registry = None
        if registry is not None:
            registry.unregister_identity(self)

    def describe(self) -> Dict[str, Any]:
        """
        Return a detached diagnostic description of this identity.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "owner_kind": self._owner_kind,
                "owner_id": self._owner_id,
                "aetheric_frame_name": self._aetheric_frame_name,
                "metadata": dict(self._metadata),
                "available_transactions": self._available_transactions,
            }
