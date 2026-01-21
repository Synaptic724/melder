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
