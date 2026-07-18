from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_pool import ConduitPool
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
    dynamic: bool = False,
    root_conduit_id: Optional[str] = None,
) -> Conduit:
    """
    Build a Conduit with the current injected-service constructor contract.

    Args:
        spellbook:
            Spellbook stub carrying the shared mediator double.
        configuration:
            Locked spellbook configuration for construction.
        conduit_state:
            Target conduit state (normal or lesser).
        aetheric_frame:
            Frame name for registry wiring.
        policy:
            Ward policy for the new conduit.
        dynamic:
            Whether the dynamic environment is forced on.
        root_conduit_id:
            Root id for lesser conduits.

    Returns:
        Conduit:
            The constructed conduit instance.
    """
    aetheric_frame_object = MagicMock()
    aetheric_frame_object._conduits = {}
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
    if conduit_state is ConduitState.lesser:
        root = MagicMock()
        root._id = root_conduit_id
        root._conduit_pool = ConduitPool(
            root_conduit=root,
            baseline_idle=10,
            max_idle=10,
        )
        aetheric_frame_object._conduits[root_conduit_id] = root
    conduit = Conduit(
        spellbook=spellbook,
        configuration=configuration,
        conduit_state=conduit_state,
        aetheric_frame_name=aetheric_frame,
        aetheric_frame=aetheric_frame_object,
        policy=policy,
        creation_gate_controller=CreationGateController(),
        dynamic=dynamic,
        root_conduit_id=root_conduit_id,
    )
    if conduit_state is ConduitState.normal:
        aetheric_frame_object._conduits[conduit._id] = conduit
    return conduit


def test_link_admits_link_transaction_through_mediator_around_ward_mutation(
    conduit_dynamic_normal: Conduit,
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Purpose:
        Regression for BUG-006: public ``Conduit.link`` must self-admit a
        ``link`` change-control transaction through the frame mediator (the
        shape ``sever_link`` already uses) instead of mutating the ward
        directly under only the conduit lock.
    Contract:
        - The mediator sees ``start_transaction`` BEFORE the ward mutation
          and ``end_transaction(success=True)`` AFTER it.
        - The admitted request is a ``link`` transaction from the
          ``conduit.link`` origin surface naming both participant conduits.
        - The public result still reports the ward outcome.
    """
    peer = _build_conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.normal,
        aetheric_frame="default",
        policy=Policies.default,
        dynamic=True,
    )
    try:
        mediator = spellbook_stub._transaction_mediator
        journal: List[str] = []

        def _record_start(**kwargs: Any) -> None:
            """
            Record mediator admission in the interleave journal.
            """
            journal.append("start_transaction")

        def _record_link(target: Conduit) -> bool:
            """
            Record the ward mutation in the interleave journal.

            Args:
                target:
                    Link target forwarded by the conduit.

            Returns:
                bool:
                    Ward success result.
            """
            journal.append("ward_link")
            return True

        def _record_end(**kwargs: Any) -> None:
            """
            Record transaction finalization in the interleave journal.
            """
            journal.append("end_transaction")

        mediator.start_transaction.side_effect = _record_start
        mediator.end_transaction.side_effect = _record_end
        conduit_dynamic_normal._conduit_ward = MagicMock()
        conduit_dynamic_normal._conduit_ward._link.side_effect = _record_link

        result = conduit_dynamic_normal.link(peer)

        assert result is True
        assert journal == ["start_transaction", "ward_link", "end_transaction"]
        start_kwargs: Dict[str, Any] = mediator.start_transaction.call_args.kwargs
        assert start_kwargs["transaction_type"] == ChangeTransactionType.LINK
        metadata = start_kwargs["metadata"]
        assert metadata["origin_surface"] == "conduit.link"
        assert conduit_dynamic_normal._id in metadata["conduit_ids"]
        assert peer._id in metadata["conduit_ids"]
        end_kwargs: Dict[str, Any] = mediator.end_transaction.call_args.kwargs
        assert end_kwargs["expected_type"] == ChangeTransactionType.LINK
        assert end_kwargs["success"] is True
    finally:
        peer.cleanup()


def test_link_denied_by_mediator_blocks_ward_mutation_and_raises(
    conduit_dynamic_normal: Conduit,
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Purpose:
        Denied admission must be a full stop: no ward mutation, no topology
        change, and the denial surfaces to the caller. On the pre-fix code
        the mediator was never consulted, so a denial could not block the
        mutation at all.
    Contract:
        - ``start_transaction`` denial propagates as the raised error.
        - The ward ``_link`` mutation is never invoked.
    """
    peer = _build_conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.normal,
        aetheric_frame="default",
        policy=Policies.default,
        dynamic=True,
    )
    try:
        mediator = spellbook_stub._transaction_mediator
        mediator.start_transaction.side_effect = RuntimeError(
            "link admission denied by change-control"
        )
        conduit_dynamic_normal._conduit_ward = MagicMock()

        with pytest.raises(RuntimeError, match="link admission denied"):
            conduit_dynamic_normal.link(peer)

        conduit_dynamic_normal._conduit_ward._link.assert_not_called()
    finally:
        peer.cleanup()


def test_link_ward_failure_ends_link_transaction_unsuccessfully(
    conduit_dynamic_normal: Conduit,
    configuration_automatic: SpellbookConfiguration,
    spellbook_stub: MagicMock,
) -> None:
    """
    Purpose:
        A ward failure inside the admitted window must finalize the
        transaction as unsuccessful and re-raise, so the mediator never
        holds a dangling admitted ``link`` request for a mutation that
        never happened.
    Contract:
        - The ward error propagates to the caller unchanged.
        - ``end_transaction`` fires exactly once with ``success=False``.
    """
    peer = _build_conduit(
        spellbook=spellbook_stub,
        configuration=configuration_automatic,
        conduit_state=ConduitState.normal,
        aetheric_frame="default",
        policy=Policies.default,
        dynamic=True,
    )
    try:
        mediator = spellbook_stub._transaction_mediator
        conduit_dynamic_normal._conduit_ward = MagicMock()
        conduit_dynamic_normal._conduit_ward._link.side_effect = RuntimeError(
            "ward link mutation failed"
        )

        with pytest.raises(RuntimeError, match="ward link mutation failed"):
            conduit_dynamic_normal.link(peer)

        mediator.end_transaction.assert_called_once()
        end_kwargs: Dict[str, Any] = mediator.end_transaction.call_args.kwargs
        assert end_kwargs["expected_type"] == ChangeTransactionType.LINK
        assert end_kwargs["success"] is False
    finally:
        peer.cleanup()
