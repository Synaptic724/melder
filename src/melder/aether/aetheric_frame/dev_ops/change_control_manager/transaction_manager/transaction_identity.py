import threading
from typing import Any, Dict, Iterable, Optional, Tuple, ClassVar

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.utilities.general_base.cleanable import Cleanable


class TransactionIdentity(Cleanable):
    """
    Lightweight transaction submitter identity for frame-local change control.

    Purpose:
        Provide one stable identity surface that any transaction-submitting
        runtime object can carry and hand into the mediator. The mediator uses
        this object to understand who is entering the frame mutation domain,
        what frame the submitter belongs to, and which transaction kinds the
        submitter is expected to originate.

    Contract:
        - `owner_kind`, `owner_id`, and `frame_name` are stable identifiers.
        - `available_transactions` is a normalized tuple of lowercase names.
        - `metadata` is mutable only through the explicit update helpers.
        - Cleanup is idempotent and drops the identity surface permanently.

    Threading:
        - Internal metadata and available-transaction mutation is guarded by an
          `RLock`.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_owner_kind",
        "_owner_id",
        "_frame_name",
        "_metadata",
        "_available_transactions",
    ]

    def __init__(
            self,
            *,
            owner_kind: str,
            owner_id: str,
            frame_name: str,
            metadata: Optional[Dict[str, Any]] = None,
            available_transactions: Optional[Iterable[str]] = None,
    ) -> None:
        """
        Initialize one transaction identity surface.

        Args:
            owner_kind:
                Stable owner kind label such as `spellbook` or `conduit`.
            owner_id:
                Stable object identifier inside the frame.
            frame_name:
                Aetheric frame name the owner belongs to.
            metadata:
                Optional detached descriptive metadata.
            available_transactions:
                Optional iterable of lowercase transaction names the owner is
                expected to originate.

        Raises:
            ValueError: If any required identity field is empty.
            TypeError: If any required identity field is not a string.
        """
        super().__init__()
        for field_name, value in (
            ("owner_kind", owner_kind),
            ("owner_id", owner_id),
            ("frame_name", frame_name),
        ):
            if not isinstance(value, str):
                raise TypeError(f"{field_name} must be a string.")
            if not value.strip():
                raise ValueError(f"{field_name} must not be empty.")

        self._lock: threading.RLock = threading.RLock()
        self._owner_kind: str = owner_kind.strip().lower()
        self._owner_id: str = owner_id
        self._frame_name: str = frame_name
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

    def cleanup(self) -> None:
        """
        Idempotently retire this identity surface.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._metadata.clear()
            del self._owner_kind
            del self._owner_id
            del self._frame_name
            del self._metadata
            del self._available_transactions
        del self._lock

    @property
    def owner_kind(self) -> str:
        """Return the normalized owner kind label."""
        self.check_cleaned()
        return self._owner_kind

    @property
    def owner_id(self) -> str:
        """Return the stable owner identifier."""
        self.check_cleaned()
        return self._owner_id

    @property
    def frame_name(self) -> str:
        """Return the owning frame name."""
        self.check_cleaned()
        return self._frame_name

    @property
    def metadata(self) -> Dict[str, Any]:
        """Return a detached metadata snapshot."""
        self.check_cleaned()
        with self._lock:
            return dict(self._metadata)

    @property
    def available_transactions(self) -> Tuple[str, ...]:
        """Return the declared transaction kinds for this identity."""
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
        candidate = transaction_name.strip().lower()
        if not candidate:
            raise ValueError("transaction_name must not be empty.")
        with self._lock:
            return candidate in self._available_transactions

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

    def describe(self) -> Dict[str, Any]:
        """
        Return a detached diagnostic description of this identity.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "owner_kind": self._owner_kind,
                "owner_id": self._owner_id,
                "frame_name": self._frame_name,
                "metadata": dict(self._metadata),
                "available_transactions": self._available_transactions,
            }
