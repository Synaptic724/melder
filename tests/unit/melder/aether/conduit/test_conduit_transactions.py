from unittest.mock import MagicMock

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.utilities.synchronization.creation_gate_controller import CreationGateController


def _build_conduit(
    *,
    spellbook: MagicMock,
    configuration: SpellbookConfiguration,
    conduit_state: ConduitState,
    aetheric_frame: str = "default",
    policy: Policies = Policies.default,
    automatic: bool = True,
    root_conduit_id: str | None = None,
) -> Conduit:
    """
    Build a Conduit with the current injected-service constructor contract.
    """
    aetheric_frame_object = MagicMock()
    conduit_cloud = MagicMock()
    conduit_cloud.create_cluster.return_value = None
    conduit_cloud.delete_cluster.return_value = None
    conduit_cloud.add_conduit_to_cluster.return_value = None
    conduit_cloud.remove_conduit_from_cluster.return_value = None
    conduit_cloud.get_clusters_for_conduit.return_value = []
    conduit_cloud.refresh_cluster_shares_for_conduit.return_value = None
    conduit_cloud.get_conduit_by_id.return_value = None
    conduit_cloud.get_conduit_by_name.return_value = None
    aetheric_frame_object._conduit_cloud = conduit_cloud
    aetheric_frame_object.devops_information_registry = DevopsInformationRegistry(
        aetheric_frame
    )
    aetheric_frame_object.register_root_conduit.return_value = None
    aetheric_frame_object.unregister_root_conduit.return_value = None
    if conduit_state is ConduitState.lesser and root_conduit_id is None:
        root_conduit_id = "root-1"
    return Conduit(
        spellbook=spellbook,
        configuration=configuration,
        conduit_state=conduit_state,
        aetheric_frame_name=aetheric_frame,
        aetheric_frame=aetheric_frame_object,
        policy=policy,
        creation_gate_controller=CreationGateController(),
        automatic=automatic,
        root_conduit_id=root_conduit_id,
    )


def test_conduit_begin_transaction_link_accepts_conduits_list(
    conduit_dynamic_normal: Conduit,
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
    aether_stub: MagicMock,
) -> None:
    """
    Purpose:
        Validate link transactions accept explicit conduit object lists.
    Contract:
        - begin_transaction accepts conduits and forwards their ids.
        - The request includes both local and peer conduit ids.
    Args:
        conduit_dynamic_normal: Dynamic normal conduit under test.
        configuration_automatic: Automatic configuration fixture.
        spellbook_stub: Spellbook stub fixture used by the conduit.
        aether_stub: Aether stub fixture for isolation.
    Returns:
        None.
    """
    peer = _build_conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.normal,
        aetheric_frame="default",
        policy=Policies.default,
        automatic=False,
    )
    try:
        spellbook_stub.begin_transaction = MagicMock()
        conduit_dynamic_normal.begin_transaction(
            ChangeTransactionType.LINK,
            conduits=[conduit_dynamic_normal, peer],
        )
        spellbook_stub.begin_transaction.assert_called_once()
        conduit_ids = spellbook_stub.begin_transaction.call_args.kwargs["conduit_ids"]
        assert conduit_dynamic_normal._id in conduit_ids
        assert peer._id in conduit_ids
    finally:
        peer.cleanup()


def test_conduit_begin_transaction_link_requires_peer(
    conduit_dynamic_normal: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """
    Purpose:
        Validate link transactions require explicit peer conduits.
    Contract:
        - begin_transaction raises when only the local conduit is provided.
        - Spellbook begin_transaction is not invoked on failure.
    Args:
        conduit_dynamic_normal: Dynamic normal conduit under test.
        spellbook_stub: Spellbook stub fixture used by the conduit.
    Returns:
        None.
    """
    spellbook_stub.begin_transaction = MagicMock()
    with pytest.raises(RuntimeError, match="peer conduit"):
        conduit_dynamic_normal.begin_transaction(
            ChangeTransactionType.LINK,
            conduits=[conduit_dynamic_normal],
        )
    spellbook_stub.begin_transaction.assert_not_called()


def test_conduit_begin_transaction_link_requires_conduits_argument(
    conduit_dynamic_normal: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """Link transactions should fail when the conduits list is omitted."""
    spellbook_stub.begin_transaction = MagicMock()

    with pytest.raises(RuntimeError, match="require conduits"):
        conduit_dynamic_normal.begin_transaction(ChangeTransactionType.LINK)

    spellbook_stub.begin_transaction.assert_not_called()


def test_conduit_begin_transaction_rejects_non_normal_conduits(
    conduit_lesser: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """Only normal conduits may begin change transactions."""
    spellbook_stub.begin_transaction = MagicMock()

    with pytest.raises(RuntimeError, match="Only normal conduits"):
        conduit_lesser.begin_transaction(ChangeTransactionType.BIND)

    spellbook_stub.begin_transaction.assert_not_called()


def test_conduit_begin_transaction_dynamic_only_string_requires_dynamic_mode(
    conduit_normal: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """Dynamic-only transaction strings should be rejected in non-dynamic mode."""
    spellbook_stub.begin_transaction = MagicMock()

    with pytest.raises(RuntimeError, match="require dynamic mode"):
        conduit_normal.begin_transaction("link")

    spellbook_stub.begin_transaction.assert_not_called()


def test_conduit_begin_transaction_rejects_non_conduit_objects_in_link_list(
    conduit_dynamic_normal: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """Link transactions should reject non-conduit objects in the conduits list."""
    spellbook_stub.begin_transaction = MagicMock()

    with pytest.raises(TypeError, match="Conduit"):
        conduit_dynamic_normal.begin_transaction(
            ChangeTransactionType.LINK,
            conduits=[conduit_dynamic_normal, object()],
        )

    spellbook_stub.begin_transaction.assert_not_called()


def test_conduit_begin_transaction_link_requires_local_conduit_presence(
    conduit_dynamic_normal: Conduit,
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
) -> None:
    """Link transactions should require the local conduit in the conduits list."""
    peer = _build_conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.normal,
        aetheric_frame="default",
        policy=Policies.default,
        automatic=False,
    )
    try:
        spellbook_stub.begin_transaction = MagicMock()
        with pytest.raises(RuntimeError, match="local conduit"):
            conduit_dynamic_normal.begin_transaction(
                ChangeTransactionType.LINK,
                conduits=[peer],
            )
        spellbook_stub.begin_transaction.assert_not_called()
    finally:
        peer.cleanup()


def test_conduit_end_transaction_rejects_non_normal_conduits(
    conduit_lesser: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """Only normal conduits may end change transactions."""
    spellbook_stub.end_transaction = MagicMock()

    with pytest.raises(RuntimeError, match="Only normal conduits"):
        conduit_lesser.end_transaction()

    spellbook_stub.end_transaction.assert_not_called()


def test_conduit_begin_transaction_appends_explicit_conduit_ids_for_non_link_requests(
    conduit_dynamic_normal: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """Non-link transactions should merge explicit conduit_ids and include the local conduit."""
    spellbook_stub.begin_transaction = MagicMock()

    conduit_dynamic_normal.begin_transaction("bind", conduit_ids=["peer-1"])

    conduit_ids = spellbook_stub.begin_transaction.call_args.kwargs["conduit_ids"]
    assert "peer-1" in conduit_ids
    assert conduit_dynamic_normal._id in conduit_ids


def test_begin_binding_transaction_delegates_to_begin_transaction(
    conduit_dynamic_normal: Conduit,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The bind string path should flow straight through begin_transaction."""
    begin_transaction = MagicMock()
    monkeypatch.setattr(
        Conduit,
        "begin_transaction",
        lambda self, transaction_type, **kwargs: begin_transaction(transaction_type, **kwargs),
    )

    conduit_dynamic_normal.begin_transaction("bind")

    begin_transaction.assert_called_once_with("bind")


def test_end_binding_transaction_rejects_non_normal_conduits(
    conduit_lesser: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """Only normal conduits may end bind-family transactions."""

    with pytest.raises(RuntimeError, match="Only normal conduits"):
        conduit_lesser.end_transaction("bind")



def test_end_binding_transaction_delegates_for_normal_conduit(
    conduit_dynamic_normal: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """Normal conduits should forward bind-family end to the mediator path."""
    mediator = MagicMock()
    conduit_dynamic_normal._get_required_transaction_mediator = lambda: mediator

    conduit_dynamic_normal.end_transaction("bind")

    mediator.end_transaction.assert_called_once_with(
        expected_type="bind",
        success=True,
    )


def test_binding_transaction_ends_on_exception(
    conduit_dynamic_normal: Conduit,
    spellbook_stub: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The bind transaction context should always end on exceptions."""
    begin_transaction = MagicMock()
    end_transaction = MagicMock()
    monkeypatch.setattr(
        Conduit,
        "begin_transaction",
        lambda self, transaction_type, **kwargs: begin_transaction(
            transaction_type,
            **kwargs,
        ),
    )
    monkeypatch.setattr(
        Conduit,
        "end_transaction",
        lambda self, transaction_type=None, success=True: end_transaction(
            transaction_type=transaction_type,
            success=success,
        ),
    )

    with pytest.raises(RuntimeError, match="boom"):
        with conduit_dynamic_normal.transaction("bind"):
            raise RuntimeError("boom")

    begin_transaction.assert_called_once_with("bind")
    end_transaction.assert_called_once_with(
        transaction_type="bind",
        success=False,
    )


def test_conduit_transaction_context_ends_on_exception(
    conduit_dynamic_normal: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """The transaction context manager should always end the transaction, even on exceptions."""
    spellbook_stub.begin_transaction = MagicMock()
    spellbook_stub.end_transaction = MagicMock()

    with pytest.raises(RuntimeError, match="boom"):
        with conduit_dynamic_normal.transaction("bind"):
            raise RuntimeError("boom")

    spellbook_stub.begin_transaction.assert_called_once()
    spellbook_stub.end_transaction.assert_called_once_with(
        transaction_type="bind",
        success=False,
    )


