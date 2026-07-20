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
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Frame-local dev-ops identity surface for runtime objects. Melder "
        "kernel machinery: read it to understand the runtime, do not drive it directly."
    )

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

        Returns:
            None.
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
        Idempotently retire this identity and unregister it from its registry.

        Purpose:
            Tear down the identity surface in the correct order so any attached
            registry loses the identity entry before this object deletes the
            fields needed to resolve its owner key.

        Contract:
            - Safe to call multiple times.
            - If a registry is attached, captures the owner key and then
              unregisters outside the identity lock to avoid lock-order
              inversion with registry-side relation rebuilds.
            - Clears metadata and deletes owned fields after external
              unregister work has finished.
            - After cleanup, all public accessors fail through
              `check_cleaned()`.

        Returns:
            None.
        """
        if self._cleaned:
            return
        if self._registry is not None:
            try:
                self._registry.unregister_identity(
                    owner_kind=self._owner_kind,
                    owner_id=self._owner_id,
                )
            except Exception:
                pass
        with self._lock:
            if self._cleaned:
                return
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

        Returns:
            str: Stable lowercased owner kind for this identity.
        """
        
        return self._owner_kind

    @property
    def owner_id(self) -> str:
        """
        Return the stable owner identifier.

        Returns:
            str: Stable owner id registered for this identity.
        """
        
        return self._owner_id

    @property
    def aetheric_frame_name(self) -> str:
        """
        Return the owning frame name for this identity.

        Returns:
            str: Frame name this identity is scoped to.
        """
        
        return self._aetheric_frame_name

    @property
    def metadata(self) -> Dict[str, Any]:
        """
        Return a detached metadata snapshot.

        Contract:
            - Returns a new dictionary snapshot.
            - Callers cannot mutate the identity-owned metadata in place.

        Returns:
            Dict[str, Any]: Copy of the current metadata payload.
        """
        with self._lock:
            return dict(self._metadata)

    @property
    def available_transactions(self) -> Tuple[str, ...]:
        """
        Return the declared transaction kinds for this identity.

        Contract:
            - Returned tuple is already normalized to lowercase values.
            - Ordering is stable because values are sorted during mutation.

        Returns:
            Tuple[str, ...]: Declared transaction kinds for this identity.
        """
        with self._lock:
            return self._available_transactions

    def supports_transaction(self, transaction_name: str) -> bool:
        """
        Return whether this identity declares the given transaction kind.

        Args:
            transaction_name:
                Transaction name to normalize and check.

        Returns:
            bool: `True` when the normalized transaction name is declared.

        Raises:
            TypeError: If `transaction_name` is not a string.
            ValueError: If `transaction_name` is empty after normalization.
        """
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

        Purpose:
            Refresh the identity's transaction-origin surface when runtime
            posture changes, such as lesser-to-normal conduit upgrades.

        Contract:
            - Normalizes values to lowercase strings.
            - Drops empty values.
            - Replaces the whole tuple rather than mutating it incrementally.

        Args:
            transaction_names:
                Iterable of transaction names to normalize and store.

        Returns:
            None.
        """
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

        Contract:
            - Later keys overwrite earlier values.
            - Mutation happens under the identity lock.
            - Metadata updates are local-only; they do not implicitly refresh
              the attached registry.
            - Callers that need registry-side derived state to refresh must
              invoke `refresh_registry(...)` explicitly.

        Args:
            **metadata:
                Key/value metadata updates to merge into the stored payload.

        Returns:
            None.
        """
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

        Contract:
            - Stores the registry reference before attempting registration.
            - Rolls that reference back out if registry registration fails.
            - Does not allow silent migration to a different registry.

        Returns:
            None.
        """
        
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

    def refresh_registry(self, *, object_ref: Optional[Any] = None) -> None:
        """
        Refresh the attached registry entry for this identity.

        Purpose:
            Give owning runtime objects one identity-owned way to push updated
            metadata or object references back into the frame registry without
            reaching into the registry surface directly.

        Args:
            object_ref:
                Optional updated live object reference to store beside this
                identity.

        Returns:
            None.

        Raises:
            RuntimeError:
                If no registry is attached.
        """
        
        registry = None
        with self._lock:
            registry = self._registry
        if registry is None:
            raise RuntimeError("DevopsIdentity is not attached to a registry.")
        registry.refresh_identity(self, object_ref=object_ref)

    def register_provider_conduit(self, provider_conduit_id: str) -> None:
        """
        Register a provider->borrower conduit relation through this identity.

        Purpose:
            Let a conduit-owned identity publish provider/borrower link edges
            into the frame registry without the conduit or ward reaching into
            the registry directly.

        Args:
            provider_conduit_id:
                Provider conduit id linked to this conduit.

        Returns:
            None.

        Raises:
            RuntimeError:
                If this identity is not a conduit identity or has no registry.
            ValueError:
                If provider_conduit_id is empty.
        """
        
        if self._owner_kind != "conduit":
            raise RuntimeError(
                "Only conduit identities may publish provider conduit relations."
            )
        if not provider_conduit_id:
            raise ValueError("provider_conduit_id must not be empty.")
        registry = None
        with self._lock:
            registry = self._registry
        if registry is None:
            raise RuntimeError("DevopsIdentity is not attached to a registry.")
        registry.register_conduit_link(
            provider_conduit_id=provider_conduit_id,
            borrower_conduit_id=self._owner_id,
        )

    def unregister_provider_conduit(self, provider_conduit_id: str) -> None:
        """
        Remove a provider->borrower conduit relation through this identity.

        Args:
            provider_conduit_id:
                Provider conduit id previously linked to this conduit.

        Returns:
            None.

        Raises:
            RuntimeError:
                If this identity is not a conduit identity or has no registry.
        """
        
        if self._owner_kind != "conduit":
            raise RuntimeError(
                "Only conduit identities may remove provider conduit relations."
            )
        if not provider_conduit_id:
            return
        registry = None
        with self._lock:
            registry = self._registry
        if registry is None:
            raise RuntimeError("DevopsIdentity is not attached to a registry.")
        registry.unregister_conduit_link(
            provider_conduit_id=provider_conduit_id,
            borrower_conduit_id=self._owner_id,
        )

    def register_cluster_member(self, conduit_id: str) -> None:
        """
        Register one conduit membership under this cluster identity.

        Purpose:
            Let a cluster-owned identity publish member edges into the frame
            registry without the cluster reaching into the registry directly.

        Args:
            conduit_id:
                Conduit id joining this cluster.

        Returns:
            None.

        Raises:
            RuntimeError:
                If this identity is not a conduit-cluster identity or has no
                registry.
            ValueError:
                If conduit_id is empty.
        """
        
        if self._owner_kind != "conduit_cluster":
            raise RuntimeError(
                "Only conduit-cluster identities may publish cluster membership."
            )
        if not conduit_id:
            raise ValueError("conduit_id must not be empty.")
        registry = None
        with self._lock:
            registry = self._registry
        if registry is None:
            raise RuntimeError("DevopsIdentity is not attached to a registry.")
        registry.register_cluster_membership(
            cluster_id=self._owner_id,
            conduit_id=conduit_id,
        )

    def unregister_cluster_member(self, conduit_id: str) -> None:
        """
        Remove one conduit membership from this cluster identity.

        Args:
            conduit_id:
                Conduit id leaving this cluster.

        Returns:
            None.

        Raises:
            RuntimeError:
                If this identity is not a conduit-cluster identity or has no
                registry.
        """
        
        if self._owner_kind != "conduit_cluster":
            raise RuntimeError(
                "Only conduit-cluster identities may remove cluster membership."
            )
        if not conduit_id:
            return
        registry = None
        with self._lock:
            registry = self._registry
        if registry is None:
            raise RuntimeError("DevopsIdentity is not attached to a registry.")
        registry.unregister_cluster_membership(
            cluster_id=self._owner_id,
            conduit_id=conduit_id,
        )

    def detach_registry(self) -> None:
        """
        Detach this identity from the currently attached registry, if any.

        Contract:
            - Safe when no registry is attached.
            - Clears the local registry reference before asking the registry to
              remove the identity entry.

        Returns:
            None.
        """
        
        registry = None
        with self._lock:
            registry = self._registry
            self._registry = None
        if registry is not None:
            registry.unregister_identity(self)

    def describe(self) -> Dict[str, Any]:
        """
        Return a detached diagnostic description of this identity.

        Contract:
            - Returns only detached scalar/tuple/dict data.
            - Does not expose the attached registry object reference.

        Returns:
            Dict[str, Any]: Diagnostic snapshot of the identity surface.
        """
        
        with self._lock:
            return {
                "owner_kind": self._owner_kind,
                "owner_id": self._owner_id,
                "aetheric_frame_name": self._aetheric_frame_name,
                "metadata": dict(self._metadata),
                "available_transactions": self._available_transactions,
            }
