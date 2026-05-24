from typing import Any, Dict, Optional, Tuple
from unittest.mock import MagicMock

import pytest

from melder.aether.aetheric_frame.dev_ops.devops_identity import DevopsIdentity
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.conduit.conduit_state.conduit_state import ConduitState


def _make_identity(
        *,
        owner_kind: str,
        owner_id: str,
        frame_name: str = "frame-1",
        metadata: Optional[Dict[str, Any]] = None,
        available_transactions: Optional[Tuple[str, ...]] = None,
) -> DevopsIdentity:
    """
    Build one identity object for registry tests.
    """
    return DevopsIdentity(
        owner_kind=owner_kind,
        owner_id=owner_id,
        aetheric_frame_name=frame_name,
        metadata=metadata,
        available_transactions=available_transactions,
    )


@pytest.mark.parametrize(
    ("frame_name", "expected_exception", "expected_message"),
    [
        (1, TypeError, "aetheric_frame_name must be a string."),
        (" ", ValueError, "aetheric_frame_name must not be empty."),
    ],
)
def test_devops_information_registry_init_validates_frame_name(
        frame_name: Any,
        expected_exception: type[BaseException],
        expected_message: str,
) -> None:
    """
    Purpose:
        Validate registry initialization rejects invalid frame names.
    Contract:
        - Frame name must be a non-empty string.
    Returns:
        None.
    Raises:
        AssertionError: If invalid frame names are accepted.
    """
    with pytest.raises(expected_exception, match=expected_message):
        DevopsInformationRegistry(frame_name)


def test_devops_information_registry_register_and_resolve_identity_and_object() -> None:
    """
    Purpose:
        Verify identity registration stores both identity and object references.
    Contract:
        - get_identity and get_object return registered values.
    Returns:
        None.
    Raises:
        AssertionError: If registry storage is incomplete.
    """
    registry = DevopsInformationRegistry("frame-1")
    identity = _make_identity(owner_kind="spellbook", owner_id="book-1")
    marker = object()

    registry.register_identity(identity, object_ref=marker)

    assert registry.get_identity(owner_kind="spellbook", owner_id="book-1") is identity
    assert registry.get_object(owner_kind="spellbook", owner_id="book-1") is marker


def test_devops_information_registry_register_identity_rejects_frame_mismatch() -> None:
    """
    Purpose:
        Verify registry rejects identities from other frames.
    Contract:
        - Frame mismatch raises ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If mismatched identities are accepted.
    """
    registry = DevopsInformationRegistry("frame-1")
    identity = _make_identity(
        owner_kind="spellbook",
        owner_id="book-1",
        frame_name="other-frame",
    )

    with pytest.raises(ValueError, match="does not match this registry"):
        registry.register_identity(identity)


def test_devops_information_registry_register_identity_rejects_different_identity_same_key() -> None:
    """
    Purpose:
        Verify one key cannot map to two different identity objects.
    Contract:
        - Registering a second distinct identity for the same key raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If duplicate identity keys are silently replaced.
    """
    registry = DevopsInformationRegistry("frame-1")
    first = _make_identity(owner_kind="spellbook", owner_id="book-1")
    second = _make_identity(owner_kind="spellbook", owner_id="book-1")
    registry.register_identity(first)

    with pytest.raises(RuntimeError, match="already registered"):
        registry.register_identity(second)


def test_devops_information_registry_refresh_identity_requires_existing_registration() -> None:
    """
    Purpose:
        Verify refresh requires the identity to be registered first.
    Contract:
        - Refreshing an unknown identity raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If unknown identity refresh succeeds.
    """
    registry = DevopsInformationRegistry("frame-1")
    identity = _make_identity(owner_kind="spellbook", owner_id="book-1")

    with pytest.raises(RuntimeError, match="not registered"):
        registry.refresh_identity(identity)


def test_devops_information_registry_rebuilds_spellbook_conduit_relations_from_metadata() -> None:
    """
    Purpose:
        Verify spellbook <-> conduit ownership mirrors are rebuilt from metadata.
    Contract:
        - Spellbook metadata with conduit_id contributes ownership.
        - Conduit metadata with spellbook_id contributes the same ownership.
    Returns:
        None.
    Raises:
        AssertionError: If derived ownership relations are wrong.
    """
    registry = DevopsInformationRegistry("frame-1")
    spellbook_identity = _make_identity(
        owner_kind="spellbook",
        owner_id="book-1",
        metadata={"conduit_id": "conduit-1"},
    )
    conduit_identity = _make_identity(
        owner_kind="conduit",
        owner_id="conduit-1",
        metadata={"spellbook_id": "book-1"},
    )
    conduit_object = MagicMock()
    spellbook_object = MagicMock()

    registry.register_identity(spellbook_identity, object_ref=spellbook_object)
    registry.register_identity(conduit_identity, object_ref=conduit_object)

    assert registry.get_conduits_for_spellbook("book-1") == ("conduit-1",)
    assert registry.get_primary_conduit_id_for_spellbook("book-1") == "conduit-1"
    assert registry.get_spellbook_for_conduit("conduit-1") == "book-1"
    assert registry.get_conduit_objects_for_spellbook("book-1") == (conduit_object,)
    assert registry.get_spellbook_object_for_conduit("conduit-1") is spellbook_object


def test_devops_information_registry_get_primary_conduit_for_spellbook_returns_none_when_missing() -> None:
    """
    Purpose:
        Verify primary conduit lookup returns None without any relation.
    Contract:
        - Missing spellbook mappings return None.
    Returns:
        None.
    Raises:
        AssertionError: If missing mappings raise or return junk.
    """
    registry = DevopsInformationRegistry("frame-1")

    assert registry.get_primary_conduit_id_for_spellbook("book-1") is None


def test_devops_information_registry_get_primary_conduit_for_spellbook_rejects_multiple_conduits() -> None:
    """
    Purpose:
        Verify the paired-conduit helper rejects multiple conduit mappings.
    Contract:
        - Multiple conduits for one spellbook raise RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If multi-conduit spellbook mappings are accepted.
    """
    registry = DevopsInformationRegistry("frame-1")
    registry.register_identity(
        _make_identity(
            owner_kind="conduit",
            owner_id="conduit-1",
            metadata={
                "spellbook_id": "book-1",
                "conduit_state": ConduitState.normal.value,
            },
        )
    )
    registry.register_identity(
        _make_identity(
            owner_kind="conduit",
            owner_id="conduit-2",
            metadata={
                "spellbook_id": "book-1",
                "conduit_state": ConduitState.normal.value,
            },
        )
    )

    with pytest.raises(RuntimeError, match="expected one paired conduit"):
        registry.get_primary_conduit_id_for_spellbook("book-1")


def test_devops_information_registry_ignores_non_normal_conduit_state_for_spellbook_pairing() -> None:
    """
    Purpose:
        Verify lesser and pooled lesser conduit identities do not become the
        primary spellbook pairing.
    """
    registry = DevopsInformationRegistry("frame-1")
    registry.register_identity(
        _make_identity(
            owner_kind="conduit",
            owner_id="lesser-1",
            metadata={
                "spellbook_id": "book-1",
                "conduit_state": ConduitState.lesser.value,
            },
        )
    )
    registry.register_identity(
        _make_identity(
            owner_kind="conduit",
            owner_id="pooled-1",
            metadata={
                "spellbook_id": "book-1",
                "conduit_state": ConduitState.pooled_lesser.value,
            },
        )
    )

    assert registry.get_conduits_for_spellbook("book-1") == tuple()
    assert registry.get_primary_conduit_id_for_spellbook("book-1") is None
    assert registry.get_spellbook_for_conduit("lesser-1") is None
    assert registry.get_spellbook_for_conduit("pooled-1") is None


def test_devops_information_registry_conduit_link_edges_are_bidirectional() -> None:
    """
    Purpose:
        Verify provider/borrower relation registration stays bidirectional.
    Contract:
        - list_borrowers_for_provider and list_providers_for_borrower agree.
    Returns:
        None.
    Raises:
        AssertionError: If bidirectional mirrors diverge.
    """
    registry = DevopsInformationRegistry("frame-1")
    provider = MagicMock()
    borrower = MagicMock()
    registry.register_identity(
        _make_identity(owner_kind="conduit", owner_id="provider-1"),
        object_ref=provider,
    )
    registry.register_identity(
        _make_identity(owner_kind="conduit", owner_id="borrower-1"),
        object_ref=borrower,
    )

    registry.register_conduit_link(
        provider_conduit_id="provider-1",
        borrower_conduit_id="borrower-1",
    )

    assert registry.list_borrowers_for_provider("provider-1") == ("borrower-1",)
    assert registry.list_providers_for_borrower("borrower-1") == ("provider-1",)
    assert registry.list_borrower_conduit_objects_for_provider("provider-1") == (borrower,)
    assert registry.list_provider_conduit_objects_for_borrower("borrower-1") == (provider,)


def test_devops_information_registry_unregister_conduit_link_prunes_empty_buckets() -> None:
    """
    Purpose:
        Verify removing the last conduit link prunes both mirror buckets.
    Contract:
        - Empty provider/borrower buckets are removed.
    Returns:
        None.
    Raises:
        AssertionError: If empty buckets survive.
    """
    registry = DevopsInformationRegistry("frame-1")
    registry.register_conduit_link(
        provider_conduit_id="provider-1",
        borrower_conduit_id="borrower-1",
    )

    registry.unregister_conduit_link(
        provider_conduit_id="provider-1",
        borrower_conduit_id="borrower-1",
    )

    assert registry.list_borrowers_for_provider("provider-1") == ()
    assert registry.list_providers_for_borrower("borrower-1") == ()


def test_devops_information_registry_cluster_membership_edges_are_bidirectional() -> None:
    """
    Purpose:
        Verify cluster membership registration stays bidirectional.
    Contract:
        - Cluster -> conduit and conduit -> cluster lookups agree.
    Returns:
        None.
    Raises:
        AssertionError: If cluster membership mirrors diverge.
    """
    registry = DevopsInformationRegistry("frame-1")
    cluster_object = MagicMock()
    conduit_object = MagicMock()
    registry.register_identity(
        _make_identity(owner_kind="conduit_cluster", owner_id="cluster-1"),
        object_ref=cluster_object,
    )
    registry.register_identity(
        _make_identity(owner_kind="conduit", owner_id="conduit-1"),
        object_ref=conduit_object,
    )

    registry.register_cluster_membership(
        cluster_id="cluster-1",
        conduit_id="conduit-1",
    )

    assert registry.get_conduits_for_cluster("cluster-1") == ("conduit-1",)
    assert registry.get_clusters_for_conduit("conduit-1") == ("cluster-1",)
    assert registry.get_cluster_objects_for_conduit("conduit-1") == (cluster_object,)


def test_devops_information_registry_unregister_cluster_membership_prunes_empty_buckets() -> None:
    """
    Purpose:
        Verify removing the last cluster membership prunes both mirror buckets.
    Contract:
        - Empty cluster/conduit buckets are removed.
    Returns:
        None.
    Raises:
        AssertionError: If empty buckets survive.
    """
    registry = DevopsInformationRegistry("frame-1")
    registry.register_cluster_membership(
        cluster_id="cluster-1",
        conduit_id="conduit-1",
    )

    registry.unregister_cluster_membership(
        cluster_id="cluster-1",
        conduit_id="conduit-1",
    )

    assert registry.get_conduits_for_cluster("cluster-1") == ()
    assert registry.get_clusters_for_conduit("conduit-1") == ()


def test_devops_information_registry_transaction_indexes_support_identity_and_type_queries() -> None:
    """
    Purpose:
        Verify transaction registration populates type and identity reverse indexes.
    Contract:
        - list_transaction_ids_for_identity and list_transaction_ids_for_type
          return the registered id.
        - Live-object queries return the registered object.
    Returns:
        None.
    Raises:
        AssertionError: If reverse transaction indexes are incomplete.
    """
    registry = DevopsInformationRegistry("frame-1")
    tx_object = object()

    registry.register_transaction(
        transaction_id="tx-1",
        transaction_object=tx_object,
        transaction_type="bind",
        identity_keys=(("spellbook", "book-1"), ("conduit", "conduit-1")),
    )

    assert registry.get_transaction("tx-1") is tx_object
    assert registry.list_transaction_ids_for_identity(
        owner_kind="spellbook",
        owner_id="book-1",
    ) == ("tx-1",)
    assert registry.list_transaction_ids_for_type("bind") == ("tx-1",)
    assert registry.list_live_transactions_for_identity(
        owner_kind="conduit",
        owner_id="conduit-1",
    ) == (tx_object,)
    assert registry.list_live_transactions_for_type("bind") == (tx_object,)


def test_devops_information_registry_unregister_transaction_clears_reverse_indexes() -> None:
    """
    Purpose:
        Verify transaction removal clears all reverse index entries.
    Contract:
        - Type and identity indexes are empty after unregister.
    Returns:
        None.
    Raises:
        AssertionError: If reverse transaction entries survive.
    """
    registry = DevopsInformationRegistry("frame-1")
    registry.register_transaction(
        transaction_id="tx-1",
        transaction_object=object(),
        transaction_type="bind",
        identity_keys=(("spellbook", "book-1"),),
    )

    registry.unregister_transaction("tx-1")

    assert registry.get_transaction("tx-1") is None
    assert registry.list_transaction_ids_for_identity(
        owner_kind="spellbook",
        owner_id="book-1",
    ) == ()
    assert registry.list_transaction_ids_for_type("bind") == ()


def test_devops_information_registry_unregister_conduit_identity_clears_related_edges() -> None:
    """
    Purpose:
        Verify conduit identity removal clears link, cluster, and transaction edges.
    Contract:
        - Conduit-side mirrors referencing the identity are removed.
    Returns:
        None.
    Raises:
        AssertionError: If stale relation edges survive conduit removal.
    """
    registry = DevopsInformationRegistry("frame-1")
    conduit_identity = _make_identity(owner_kind="conduit", owner_id="conduit-1")
    registry.register_identity(conduit_identity)
    registry.register_conduit_link(
        provider_conduit_id="conduit-1",
        borrower_conduit_id="borrower-1",
    )
    registry.register_cluster_membership(
        cluster_id="cluster-1",
        conduit_id="conduit-1",
    )
    registry.register_transaction(
        transaction_id="tx-1",
        transaction_object=object(),
        transaction_type="bind",
        identity_keys=(("conduit", "conduit-1"),),
    )

    registry.unregister_identity(owner_kind="conduit", owner_id="conduit-1")

    assert registry.get_identity(owner_kind="conduit", owner_id="conduit-1") is None
    assert registry.list_borrowers_for_provider("conduit-1") == ()
    assert registry.get_clusters_for_conduit("conduit-1") == ()
    assert registry.list_transaction_ids_for_identity(
        owner_kind="conduit",
        owner_id="conduit-1",
    ) == ()


def test_devops_information_registry_describe_returns_detached_summary() -> None:
    """
    Purpose:
        Verify describe returns a detached diagnostic summary.
    Contract:
        - identity_count and transaction_count reflect current registry state.
        - Relation buckets are reported as sorted tuples.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostic summary is incomplete.
    """
    registry = DevopsInformationRegistry("frame-1")
    registry.register_identity(
        _make_identity(
            owner_kind="spellbook",
            owner_id="book-1",
            metadata={"conduit_id": "conduit-1"},
        )
    )
    registry.register_identity(
        _make_identity(
            owner_kind="conduit",
            owner_id="conduit-1",
            metadata={"spellbook_id": "book-1"},
        )
    )
    registry.register_conduit_link(
        provider_conduit_id="conduit-1",
        borrower_conduit_id="borrower-1",
    )
    registry.register_cluster_membership(
        cluster_id="cluster-1",
        conduit_id="conduit-1",
    )
    registry.register_transaction(
        transaction_id="tx-1",
        transaction_object=object(),
        transaction_type="bind",
        identity_keys=(("spellbook", "book-1"),),
    )

    described = registry.describe()

    assert described["aetheric_frame_name"] == "frame-1"
    assert described["identity_count"] == 2
    assert described["transaction_count"] == 1
    assert described["spellbook_to_conduits"] == {"book-1": ("conduit-1",)}
    assert described["provider_to_borrowers"] == {"conduit-1": ("borrower-1",)}
    assert described["cluster_to_conduits"] == {"cluster-1": ("conduit-1",)}


def test_devops_information_registry_cleanup_is_idempotent_and_blocks_reuse() -> None:
    """
    Purpose:
        Verify cleanup clears registry state and blocks later access.
    Contract:
        - cleanup is idempotent.
        - Public accessors fail after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup leaves the registry reusable.
    """
    registry = DevopsInformationRegistry("frame-1")
    registry.register_identity(
        _make_identity(owner_kind="spellbook", owner_id="book-1")
    )

    registry.cleanup()
    registry.cleanup()

    assert not hasattr(registry, "_identities_by_key")
    with pytest.raises(RuntimeError):
        registry.describe()
