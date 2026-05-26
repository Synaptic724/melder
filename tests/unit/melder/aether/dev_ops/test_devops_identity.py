from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import MagicMock

import pytest

from melder.aether.aetheric_frame.dev_ops.devops_identity import DevopsIdentity


class _RegistrySpy:
    """
    Minimal registry double for DevopsIdentity tests.

    Purpose:
        Capture registry callbacks invoked by DevopsIdentity without pulling in
        the full frame-owned registry implementation.
    """

    def __init__(self) -> None:
        """Initialize empty callback logs."""
        self.register_calls: List[Tuple[DevopsIdentity, Any]] = []
        self.unregister_calls: List[Tuple[str, str]] = []
        self.refresh_calls: List[Tuple[DevopsIdentity, Any]] = []
        self.provider_links: List[Tuple[str, str]] = []
        self.removed_provider_links: List[Tuple[str, str]] = []
        self.cluster_memberships: List[Tuple[str, str]] = []
        self.removed_cluster_memberships: List[Tuple[str, str]] = []

    def register_identity(
            self,
            identity: DevopsIdentity,
            *,
            object_ref: Optional[Any] = None,
    ) -> None:
        """
        Record one identity registration.
        """
        self.register_calls.append((identity, object_ref))

    def unregister_identity(
            self,
            identity: Optional[DevopsIdentity] = None,
            *,
            owner_kind: Optional[str] = None,
            owner_id: Optional[str] = None,
    ) -> None:
        """
        Record one identity unregistration.
        """
        if identity is not None:
            owner_kind = identity.owner_kind
            owner_id = identity.owner_id
        self.unregister_calls.append((str(owner_kind), str(owner_id)))

    def refresh_identity(
            self,
            identity: DevopsIdentity,
            *,
            object_ref: Optional[Any] = None,
    ) -> None:
        """
        Record one identity refresh.
        """
        self.refresh_calls.append((identity, object_ref))

    def register_conduit_link(
            self,
            *,
            provider_conduit_id: str,
            borrower_conduit_id: str,
    ) -> None:
        """
        Record one provider -> borrower link.
        """
        self.provider_links.append((provider_conduit_id, borrower_conduit_id))

    def unregister_conduit_link(
            self,
            *,
            provider_conduit_id: str,
            borrower_conduit_id: str,
    ) -> None:
        """
        Record one provider -> borrower link removal.
        """
        self.removed_provider_links.append(
            (provider_conduit_id, borrower_conduit_id)
        )

    def register_cluster_membership(
            self,
            *,
            cluster_id: str,
            conduit_id: str,
    ) -> None:
        """
        Record one cluster membership add.
        """
        self.cluster_memberships.append((cluster_id, conduit_id))

    def unregister_cluster_membership(
            self,
            *,
            cluster_id: str,
            conduit_id: str,
    ) -> None:
        """
        Record one cluster membership removal.
        """
        self.removed_cluster_memberships.append((cluster_id, conduit_id))


def _make_identity(
        *,
        owner_kind: str = "conduit",
        owner_id: str = "conduit-1",
        aetheric_frame_name: str = "frame-1",
        metadata: Optional[Dict[str, Any]] = None,
        available_transactions: Optional[Tuple[str, ...]] = None,
) -> DevopsIdentity:
    """
    Build a DevopsIdentity with stable defaults for tests.
    """
    return DevopsIdentity(
        owner_kind=owner_kind,
        owner_id=owner_id,
        aetheric_frame_name=aetheric_frame_name,
        metadata=metadata,
        available_transactions=available_transactions,
    )


@pytest.mark.parametrize(
    ("field_name", "kwargs", "expected_message"),
    [
        (
            "owner_kind",
            {
                "owner_kind": 1,
                "owner_id": "conduit-1",
                "aetheric_frame_name": "frame-1",
            },
            "owner_kind must be a string.",
        ),
        (
            "owner_kind",
            {
                "owner_kind": " ",
                "owner_id": "conduit-1",
                "aetheric_frame_name": "frame-1",
            },
            "owner_kind must not be empty.",
        ),
        (
            "owner_id",
            {
                "owner_kind": "conduit",
                "owner_id": 1,
                "aetheric_frame_name": "frame-1",
            },
            "owner_id must be a string.",
        ),
        (
            "owner_id",
            {
                "owner_kind": "conduit",
                "owner_id": "",
                "aetheric_frame_name": "frame-1",
            },
            "owner_id must not be empty.",
        ),
        (
            "aetheric_frame_name",
            {
                "owner_kind": "conduit",
                "owner_id": "conduit-1",
                "aetheric_frame_name": 1,
            },
            "aetheric_frame_name must be a string.",
        ),
        (
            "aetheric_frame_name",
            {
                "owner_kind": "conduit",
                "owner_id": "conduit-1",
                "aetheric_frame_name": " ",
            },
            "aetheric_frame_name must not be empty.",
        ),
    ],
)
def test_devops_identity_init_validates_required_fields(
        field_name: str,
        kwargs: Dict[str, Any],
        expected_message: str,
) -> None:
    """
    Purpose:
        Validate required identity fields reject invalid values.
    Contract:
        - Each required field must be a non-empty string.
    Returns:
        None.
    Raises:
        AssertionError: If invalid field values are accepted.
    """
    del field_name
    with pytest.raises((TypeError, ValueError), match=expected_message):
        DevopsIdentity(**kwargs)


def test_devops_identity_init_normalizes_owner_kind_and_transactions() -> None:
    """
    Purpose:
        Verify initialization normalizes owner kind and transaction names.
    Contract:
        - owner_kind is lowercased and stripped.
        - available_transactions are sorted, deduplicated, and lowercased.
    Returns:
        None.
    Raises:
        AssertionError: If normalization is incorrect.
    """
    identity = _make_identity(
        owner_kind=" Conduit ",
        available_transactions=("Bind", "scan", "bind", "  "),
    )

    assert identity.owner_kind == "conduit"
    assert identity.available_transactions == ("bind", "scan")


def test_devops_identity_metadata_returns_detached_copy() -> None:
    """
    Purpose:
        Verify metadata snapshots are detached from internal state.
    Contract:
        - metadata returns a new dictionary snapshot.
    Returns:
        None.
    Raises:
        AssertionError: If caller mutation leaks back into the identity.
    """
    identity = _make_identity(metadata={"region": "north"})

    metadata = identity.metadata
    metadata["region"] = "south"

    assert identity.metadata == {"region": "north"}


def test_devops_identity_supports_transaction_normalizes_input() -> None:
    """
    Purpose:
        Verify supports_transaction matches normalized transaction names.
    Contract:
        - String input is stripped and lowercased before membership check.
    Returns:
        None.
    Raises:
        AssertionError: If normalized lookup fails.
    """
    identity = _make_identity(available_transactions=("bind", "cluster_link"))

    assert identity.supports_transaction(" Bind ") is True
    assert identity.supports_transaction("cluster_link") is True
    assert identity.supports_transaction("mutation") is False


@pytest.mark.parametrize(
    ("transaction_name", "expected_message", "expected_exception"),
    [
        (1, "transaction_name must be a string.", TypeError),
        (" ", "transaction_name must not be empty.", ValueError),
    ],
)
def test_devops_identity_supports_transaction_validates_input(
        transaction_name: Any,
        expected_message: str,
        expected_exception: type[BaseException],
) -> None:
    """
    Purpose:
        Verify supports_transaction rejects invalid query input.
    Contract:
        - Non-string or empty names raise immediately.
    Returns:
        None.
    Raises:
        AssertionError: If invalid query input is accepted.
    """
    identity = _make_identity()

    with pytest.raises(expected_exception, match=expected_message):
        identity.supports_transaction(transaction_name)


def test_devops_identity_set_available_transactions_replaces_normalized_tuple() -> None:
    """
    Purpose:
        Verify available transaction replacement is normalized and complete.
    Contract:
        - set_available_transactions replaces the whole tuple.
    Returns:
        None.
    Raises:
        AssertionError: If replacement leaves stale values behind.
    """
    identity = _make_identity(available_transactions=("bind",))

    identity.set_available_transactions(("Mutation", "bind", "mutation"))

    assert identity.available_transactions == ("bind", "mutation")


def test_devops_identity_update_metadata_merges_and_refreshes_registry() -> None:
    """
    Purpose:
        Verify metadata updates merge and refresh the attached registry.
    Contract:
        - update_metadata merges keys.
        - Attached registries receive a refresh callback.
    Returns:
        None.
    Raises:
        AssertionError: If metadata merge or refresh behavior is wrong.
    """
    identity = _make_identity(metadata={"region": "north"})
    registry = _RegistrySpy()
    identity.attach_registry(registry, object_ref="obj")

    identity.update_metadata(region="south", lane="alpha")

    assert identity.metadata == {"region": "south", "lane": "alpha"}
    assert registry.refresh_calls[-1] == (identity, None)


def test_devops_identity_attach_registry_rejects_none() -> None:
    """
    Purpose:
        Verify registry attachment requires a registry object.
    Contract:
        - None registry input raises ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If None registry is accepted.
    """
    identity = _make_identity()

    with pytest.raises(ValueError, match="registry must not be None."):
        identity.attach_registry(None)


def test_devops_identity_attach_registry_rejects_different_second_registry() -> None:
    """
    Purpose:
        Verify an identity cannot silently migrate to a different registry.
    Contract:
        - A second distinct registry attachment raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If silent registry migration is allowed.
    """
    identity = _make_identity()
    first = _RegistrySpy()
    second = _RegistrySpy()
    identity.attach_registry(first)

    with pytest.raises(RuntimeError, match="already attached"):
        identity.attach_registry(second)


def test_devops_identity_attach_registry_rolls_back_local_reference_on_failure() -> None:
    """
    Purpose:
        Verify attach_registry rolls back local state if registration fails.
    Contract:
        - _registry is restored to None after a failed registration attempt.
    Returns:
        None.
    Raises:
        AssertionError: If failed registration leaves stale registry state.
    """
    identity = _make_identity()
    registry = _RegistrySpy()
    registry.register_identity = MagicMock(side_effect=RuntimeError("boom"))

    with pytest.raises(RuntimeError, match="boom"):
        identity.attach_registry(registry)

    with pytest.raises(RuntimeError, match="not attached"):
        identity.refresh_registry()


def test_devops_identity_refresh_registry_requires_attached_registry() -> None:
    """
    Purpose:
        Verify refresh_registry fails when no registry is attached.
    Contract:
        - refresh_registry raises RuntimeError without an attached registry.
    Returns:
        None.
    Raises:
        AssertionError: If refresh succeeds without a registry.
    """
    identity = _make_identity()

    with pytest.raises(RuntimeError, match="not attached"):
        identity.refresh_registry()


def test_devops_identity_refresh_registry_forwards_object_reference() -> None:
    """
    Purpose:
        Verify refresh_registry forwards object_ref to the registry.
    Contract:
        - The attached registry receives the same object_ref payload.
    Returns:
        None.
    Raises:
        AssertionError: If object_ref forwarding is lost.
    """
    identity = _make_identity()
    registry = _RegistrySpy()
    marker = object()
    identity.attach_registry(registry)

    identity.refresh_registry(object_ref=marker)

    assert registry.refresh_calls[-1] == (identity, marker)


def test_devops_identity_register_provider_conduit_requires_conduit_identity() -> None:
    """
    Purpose:
        Verify provider registration is restricted to conduit identities.
    Contract:
        - Non-conduit identities raise RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If non-conduit identities can publish provider links.
    """
    identity = _make_identity(owner_kind="spellbook")

    with pytest.raises(RuntimeError, match="Only conduit identities"):
        identity.register_provider_conduit("provider-1")


def test_devops_identity_register_provider_conduit_validates_non_empty_provider_id() -> None:
    """
    Purpose:
        Verify provider registration rejects empty ids.
    Contract:
        - Empty provider ids raise ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If empty provider ids are accepted.
    """
    identity = _make_identity()

    with pytest.raises(ValueError, match="provider_conduit_id must not be empty."):
        identity.register_provider_conduit("")


def test_devops_identity_register_provider_conduit_requires_attached_registry() -> None:
    """
    Purpose:
        Verify provider registration requires an attached registry.
    Contract:
        - Missing registry raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If provider registration works without a registry.
    """
    identity = _make_identity()

    with pytest.raises(RuntimeError, match="not attached"):
        identity.register_provider_conduit("provider-1")


def test_devops_identity_register_and_unregister_provider_conduit_delegate_to_registry() -> None:
    """
    Purpose:
        Verify conduit link publication delegates to the registry.
    Contract:
        - register_provider_conduit publishes provider -> borrower.
        - unregister_provider_conduit removes the same relation.
    Returns:
        None.
    Raises:
        AssertionError: If registry delegation is incorrect.
    """
    identity = _make_identity(owner_id="borrower-1")
    registry = _RegistrySpy()
    identity.attach_registry(registry)

    identity.register_provider_conduit("provider-1")
    identity.unregister_provider_conduit("provider-1")

    assert registry.provider_links == [("provider-1", "borrower-1")]
    assert registry.removed_provider_links == [("provider-1", "borrower-1")]


def test_devops_identity_unregister_provider_conduit_ignores_empty_provider_id() -> None:
    """
    Purpose:
        Verify provider unlink ignores empty ids after kind validation.
    Contract:
        - Empty provider ids are a no-op.
    Returns:
        None.
    Raises:
        AssertionError: If empty ids trigger registry calls.
    """
    identity = _make_identity()
    registry = _RegistrySpy()
    identity.attach_registry(registry)

    identity.unregister_provider_conduit("")

    assert registry.removed_provider_links == []


def test_devops_identity_cluster_membership_requires_cluster_identity() -> None:
    """
    Purpose:
        Verify cluster membership publication is restricted to cluster identities.
    Contract:
        - Non-cluster identities raise RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If non-cluster identities publish cluster membership.
    """
    identity = _make_identity(owner_kind="conduit")

    with pytest.raises(RuntimeError, match="Only conduit-cluster identities"):
        identity.register_cluster_member("conduit-1")


def test_devops_identity_register_cluster_member_validates_non_empty_conduit_id() -> None:
    """
    Purpose:
        Verify cluster membership publication rejects empty member ids.
    Contract:
        - Empty member ids raise ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If empty member ids are accepted.
    """
    identity = _make_identity(owner_kind="conduit_cluster")

    with pytest.raises(ValueError, match="conduit_id must not be empty."):
        identity.register_cluster_member("")


def test_devops_identity_register_and_unregister_cluster_member_delegate_to_registry() -> None:
    """
    Purpose:
        Verify cluster membership calls delegate to the attached registry.
    Contract:
        - register_cluster_member and unregister_cluster_member forward ids exactly.
    Returns:
        None.
    Raises:
        AssertionError: If registry delegation is incorrect.
    """
    identity = _make_identity(
        owner_kind="conduit_cluster",
        owner_id="cluster-1",
    )
    registry = _RegistrySpy()
    identity.attach_registry(registry)

    identity.register_cluster_member("conduit-1")
    identity.unregister_cluster_member("conduit-1")

    assert registry.cluster_memberships == [("cluster-1", "conduit-1")]
    assert registry.removed_cluster_memberships == [("cluster-1", "conduit-1")]


def test_devops_identity_detach_registry_unregisters_and_clears_local_reference() -> None:
    """
    Purpose:
        Verify detach_registry unregisters the identity and clears local state.
    Contract:
        - detach_registry is safe and idempotent.
    Returns:
        None.
    Raises:
        AssertionError: If detachment leaves registry attachment behind.
    """
    identity = _make_identity()
    registry = _RegistrySpy()
    identity.attach_registry(registry)

    identity.detach_registry()
    identity.detach_registry()

    assert registry.unregister_calls == [("conduit", "conduit-1")]
    with pytest.raises(RuntimeError, match="not attached"):
        identity.refresh_registry()


def test_devops_identity_describe_returns_detached_snapshot() -> None:
    """
    Purpose:
        Verify describe exposes detached scalar and metadata state.
    Contract:
        - Returned metadata is detached from internal state.
        - Available transactions are returned as a tuple snapshot.
    Returns:
        None.
    Raises:
        AssertionError: If the diagnostic snapshot is incomplete.
    """
    identity = _make_identity(
        metadata={"region": "north"},
        available_transactions=("bind", "mutation"),
    )

    described = identity.describe()
    described["metadata"]["region"] = "south"

    assert described["owner_kind"] == "conduit"
    assert described["owner_id"] == "conduit-1"
    assert described["aetheric_frame_name"] == "frame-1"
    assert described["available_transactions"] == ("bind", "mutation")
    assert identity.metadata == {"region": "north"}
