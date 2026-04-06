from unittest.mock import MagicMock

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.spellbook.configuration.configuration import Configuration


def test_conduit_begin_transaction_link_accepts_conduits_list(
    conduit_dynamic_normal: Conduit,
    configuration_automatic: Configuration,
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
    peer = Conduit(
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

    with pytest.raises(TypeError, match="IConduit"):
        conduit_dynamic_normal.begin_transaction(
            ChangeTransactionType.LINK,
            conduits=[conduit_dynamic_normal, object()],
        )

    spellbook_stub.begin_transaction.assert_not_called()


def test_conduit_begin_transaction_link_requires_local_conduit_presence(
    conduit_dynamic_normal: Conduit,
    configuration_automatic: Configuration,
    spellbook_stub: MagicMock,
) -> None:
    """Link transactions should require the local conduit in the conduits list."""
    peer = Conduit(
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

    conduit_dynamic_normal.begin_transaction(
        ChangeTransactionType.BIND,
        conduit_ids=["peer-1"],
    )

    conduit_ids = spellbook_stub.begin_transaction.call_args.kwargs["conduit_ids"]
    assert "peer-1" in conduit_ids
    assert conduit_dynamic_normal._id in conduit_ids


def test_begin_binding_transaction_delegates_to_begin_transaction(
    conduit_dynamic_normal: Conduit,
) -> None:
    """begin_binding_transaction should forward to begin_transaction with BIND."""
    conduit_dynamic_normal.begin_transaction = MagicMock()

    conduit_dynamic_normal.begin_binding_transaction()

    conduit_dynamic_normal.begin_transaction.assert_called_once_with(
        ChangeTransactionType.BIND
    )


def test_end_binding_transaction_rejects_non_normal_conduits(
    conduit_lesser: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """Only normal conduits may end binding transactions."""
    spellbook_stub.end_binding_transaction = MagicMock()

    with pytest.raises(RuntimeError, match="Only normal conduits"):
        conduit_lesser.end_binding_transaction()

    spellbook_stub.end_binding_transaction.assert_not_called()


def test_end_binding_transaction_delegates_for_normal_conduit(
    conduit_dynamic_normal: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """end_binding_transaction should delegate to the Spellbook for normal conduits."""
    spellbook_stub.end_binding_transaction = MagicMock()

    conduit_dynamic_normal.end_binding_transaction()

    spellbook_stub.end_binding_transaction.assert_called_once_with()


def test_binding_transaction_ends_on_exception(
    conduit_dynamic_normal: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """The binding_transaction context manager should always end the transaction, even on exceptions."""
    conduit_dynamic_normal.begin_binding_transaction = MagicMock()
    conduit_dynamic_normal.end_binding_transaction = MagicMock()

    with pytest.raises(RuntimeError, match="boom"):
        with conduit_dynamic_normal.binding_transaction():
            raise RuntimeError("boom")

    conduit_dynamic_normal.begin_binding_transaction.assert_called_once()
    conduit_dynamic_normal.end_binding_transaction.assert_called_once()


def test_conduit_transaction_context_ends_on_exception(
    conduit_dynamic_normal: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """The transaction context manager should always end the transaction, even on exceptions."""
    spellbook_stub.begin_transaction = MagicMock()
    spellbook_stub.end_transaction = MagicMock()

    with pytest.raises(RuntimeError, match="boom"):
        with conduit_dynamic_normal.transaction(ChangeTransactionType.BIND):
            raise RuntimeError("boom")

    spellbook_stub.begin_transaction.assert_called_once()
    spellbook_stub.end_transaction.assert_called_once_with(
        transaction_type=ChangeTransactionType.BIND
    )
