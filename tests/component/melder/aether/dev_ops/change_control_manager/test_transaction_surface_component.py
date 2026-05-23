from typing import Any, Optional, Tuple
from unittest.mock import MagicMock

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.aetheric_frame.dev_ops.devops_identity import DevopsIdentity


class _FakeCluster:
    """
    Minimal cluster surface exposing member ids for strategy planning.
    """

    def __init__(self, members: Tuple[str, ...]) -> None:
        """
        Store one detached member set.
        """
        self._members = set(members)

    def get_members(self):
        """
        Return a detached membership snapshot.
        """
        return set(self._members)


def _make_frame(frame_name: str) -> AethericFrame:
    """
    Build one live frame for component transaction-surface tests.
    """
    return AethericFrame(Aether(), frame_name)


def _register_spellbook_identity(
        frame: AethericFrame,
        *,
        spellbook_id: str,
        conjured: bool,
        conduit_id: Optional[str] = None,
) -> Tuple[DevopsIdentity, MagicMock]:
    """
    Register one spellbook identity and backing object on the frame registry.
    """
    identity = DevopsIdentity(
        owner_kind="spellbook",
        owner_id=spellbook_id,
        aetheric_frame_name=frame.name,
        metadata={
            "conjured": conjured,
            "conduit_id": conduit_id,
        },
        available_transactions=("bind", "scan"),
    )
    spellbook = MagicMock()
    identity.attach_registry(frame.devops_information_registry, object_ref=spellbook)
    return identity, spellbook


def _register_conduit_identity(
        frame: AethericFrame,
        *,
        conduit_id: str,
        spellbook_id: str,
        available_transactions: Tuple[str, ...] = (
            "link",
            "cluster_link",
            "transfer_ownership",
        ),
) -> Tuple[DevopsIdentity, MagicMock]:
    """
    Register one conduit identity and backing object on the frame registry.
    """
    identity = DevopsIdentity(
        owner_kind="conduit",
        owner_id=conduit_id,
        aetheric_frame_name=frame.name,
        metadata={"spellbook_id": spellbook_id},
        available_transactions=available_transactions,
    )
    conduit = MagicMock()
    conduit._id = conduit_id
    conduit._spellbook = MagicMock()
    conduit._spellbook._id = spellbook_id
    conduit.get_spell_by_id = MagicMock()
    conduit.get_spell_by_index_id = MagicMock()
    identity.attach_registry(frame.devops_information_registry, object_ref=conduit)
    return identity, conduit


def test_component_transaction_surface_pre_conjure_bind_start_and_end_calls_spellbook_local_hooks() -> None:
    """
    Purpose:
        Validate the live mediator routes bind start/end through the spellbook object.
    Contract:
        - Pre-conjure bind uses spellbook-owned identity.
        - Strategy on_start and on_end call the spellbook local bind hooks.
    Returns:
        None.
    Raises:
        AssertionError: If bind start/end skips spellbook-local hooks.
    """
    frame = _make_frame("component-tx-surface-pre-conjure")
    try:
        identity, spellbook = _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-1",
            conjured=False,
        )
        mediator = frame.dev_ops_manager.change_control_manager.transaction_mediator()

        session = mediator.start_transaction(
            identity=identity,
            transaction_type="bind",
            metadata={},
        )

        assert session.request.request_type.value == "bind"
        spellbook._prepare_bind_transaction_state.assert_called_once_with()

        mediator.end_transaction_for_identity(
            identity=identity,
            transaction_type="bind",
        )

        spellbook._clear_bind_transaction_state.assert_called_once_with()
    finally:
        frame.cleanup()


def test_component_transaction_surface_post_conjure_bind_plan_includes_cluster_scope() -> None:
    """
    Purpose:
        Validate post-conjure bind planning uses the live frame registry topology.
    Contract:
        - Paired conduit and cluster membership are reflected in staged metadata.
    Returns:
        None.
    Raises:
        AssertionError: If post-conjure bind planning misses cluster topology.
    """
    frame = _make_frame("component-tx-surface-post-conjure")
    try:
        spellbook_identity, spellbook = _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-1",
            conjured=True,
            conduit_id="conduit-1",
        )
        conduit_identity, _conduit = _register_conduit_identity(
            frame,
            conduit_id="conduit-1",
            spellbook_id="spellbook-1",
        )
        cluster_identity = DevopsIdentity(
            owner_kind="conduit_cluster",
            owner_id="cluster-1",
            aetheric_frame_name=frame.name,
            metadata={"cluster_name": "alpha"},
            available_transactions=("cluster_link",),
        )
        cluster_identity.attach_registry(
            frame.devops_information_registry,
            object_ref=_FakeCluster(("conduit-1",)),
        )
        frame.devops_information_registry.register_cluster_membership(
            cluster_id="cluster-1",
            conduit_id="conduit-1",
        )

        mediator = frame.dev_ops_manager.change_control_manager.transaction_mediator()
        session = mediator.start_transaction(
            identity=spellbook_identity,
            transaction_type="bind",
            metadata={},
        )

        assert session.request.initiator_conduit_id == "conduit-1"
        assert session.request.conduit_ids == ("conduit-1",)
        assert "cluster-1" in session.request.metadata["affected_cluster_ids"]
        mediator.end_transaction_for_identity(
            identity=spellbook_identity,
            transaction_type="bind",
        )
        spellbook._clear_bind_transaction_state.assert_called_once_with()
        assert conduit_identity.owner_id == "conduit-1"
    finally:
        frame.cleanup()


def test_component_transaction_surface_link_start_tracks_spellbook_and_conduit_participants() -> None:
    """
    Purpose:
        Validate live link transactions stage the expected participant surface.
    Contract:
        - Link sessions record both conduit ids and affected spellbook ids.
    Returns:
        None.
    Raises:
        AssertionError: If staged metadata omits participants.
    """
    frame = _make_frame("component-tx-surface-link")
    try:
        conduit_identity, _source = _register_conduit_identity(
            frame,
            conduit_id="conduit-1",
            spellbook_id="spellbook-1",
        )
        _register_conduit_identity(
            frame,
            conduit_id="conduit-2",
            spellbook_id="spellbook-2",
        )
        _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-1",
            conjured=True,
            conduit_id="conduit-1",
        )
        _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-2",
            conjured=True,
            conduit_id="conduit-2",
        )

        mediator = frame.dev_ops_manager.change_control_manager.transaction_mediator()
        session = mediator.start_transaction(
            identity=conduit_identity,
            transaction_type="link",
            metadata={"conduit_ids": ("conduit-2",)},
        )

        assert set(session.request.conduit_ids) == {"conduit-1", "conduit-2"}
        assert session.request.metadata["affected_spellbook_ids"] == (
            "spellbook-1",
            "spellbook-2",
        )
        mediator.end_transaction_for_identity(
            identity=conduit_identity,
            transaction_type="link",
        )
    finally:
        frame.cleanup()


def test_component_transaction_surface_cluster_link_start_tracks_cluster_metadata() -> None:
    """
    Purpose:
        Validate live cluster-link transactions stage cluster and conduit participants.
    Contract:
        - Cluster id and conduit ids are preserved in the staged request metadata.
    Returns:
        None.
    Raises:
        AssertionError: If cluster metadata is incomplete.
    """
    frame = _make_frame("component-tx-surface-cluster-link")
    try:
        cluster_identity = DevopsIdentity(
            owner_kind="conduit_cluster",
            owner_id="cluster-1",
            aetheric_frame_name=frame.name,
            metadata={"cluster_name": "alpha"},
            available_transactions=("cluster_link",),
        )
        cluster_identity.attach_registry(
            frame.devops_information_registry,
            object_ref=_FakeCluster(("conduit-1", "conduit-2")),
        )
        _register_conduit_identity(
            frame,
            conduit_id="conduit-1",
            spellbook_id="spellbook-1",
        )
        _register_conduit_identity(
            frame,
            conduit_id="conduit-2",
            spellbook_id="spellbook-2",
        )
        _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-1",
            conjured=True,
            conduit_id="conduit-1",
        )
        _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-2",
            conjured=True,
            conduit_id="conduit-2",
        )

        mediator = frame.dev_ops_manager.change_control_manager.transaction_mediator()
        session = mediator.start_transaction(
            identity=cluster_identity,
            transaction_type="cluster_link",
            metadata={
                "cluster_id": "cluster-1",
                "conduit_ids": ("conduit-1", "conduit-2"),
            },
        )

        assert session.request.metadata["cluster_id"] == "cluster-1"
        assert set(session.request.conduit_ids) == {"conduit-1", "conduit-2"}
        mediator.end_transaction_for_identity(
            identity=cluster_identity,
            transaction_type="cluster_link",
        )
    finally:
        frame.cleanup()


def test_component_transaction_surface_update_transaction_for_identity_extends_staged_contract_keys() -> None:
    """
    Purpose:
        Validate live staged metadata updates by identity.
    Contract:
        - update_transaction_for_identity refreshes contract keys on the active session.
    Returns:
        None.
    Raises:
        AssertionError: If staged contract keys are not updated.
    """
    frame = _make_frame("component-tx-surface-update")
    try:
        conduit_identity, _source = _register_conduit_identity(
            frame,
            conduit_id="conduit-1",
            spellbook_id="spellbook-1",
        )
        _register_conduit_identity(
            frame,
            conduit_id="conduit-2",
            spellbook_id="spellbook-2",
        )
        _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-1",
            conjured=True,
            conduit_id="conduit-1",
        )
        _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-2",
            conjured=True,
            conduit_id="conduit-2",
        )

        mediator = frame.dev_ops_manager.change_control_manager.transaction_mediator()
        session = mediator.start_transaction(
            identity=conduit_identity,
            transaction_type="link",
            metadata={"conduit_ids": ("conduit-2",)},
        )

        updated = mediator.update_transaction_for_identity(
            identity=conduit_identity,
            transaction_type="link",
            contract_keys=(("frame", "__default__", "conduit-2"),),
        )

        assert updated is True
        assert session.staged.contract_keys == (("frame", "__default__", "conduit-2"),)
        mediator.end_transaction_for_identity(
            identity=conduit_identity,
            transaction_type="link",
        )
    finally:
        frame.cleanup()


def test_component_transaction_surface_registry_tracks_live_transaction_session() -> None:
    """
    Purpose:
        Validate the frame-owned registry mirrors live mediator sessions.
    Contract:
        - Starting a transaction registers the live session by identity and type.
        - Ending the transaction removes the mirrored session.
    Returns:
        None.
    Raises:
        AssertionError: If registry mirroring drifts from live session state.
    """
    frame = _make_frame("component-tx-surface-registry")
    try:
        identity, _spellbook = _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-1",
            conjured=False,
        )
        mediator = frame.dev_ops_manager.change_control_manager.transaction_mediator()

        session = mediator.start_transaction(
            identity=identity,
            transaction_type="bind",
            metadata={},
        )

        live_by_identity = frame.devops_information_registry.list_live_transactions_for_identity(
            owner_kind="spellbook",
            owner_id="spellbook-1",
        )
        assert live_by_identity == (session,)
        assert frame.devops_information_registry.list_live_transactions_for_type("bind") == (
            session,
        )

        mediator.end_transaction_for_identity(
            identity=identity,
            transaction_type="bind",
        )

        assert frame.devops_information_registry.list_live_transactions_for_identity(
            owner_kind="spellbook",
            owner_id="spellbook-1",
        ) == ()
    finally:
        frame.cleanup()


def test_component_transaction_surface_bind_update_transaction_extends_binding_keys() -> None:
    """
    Purpose:
        Validate live bind sessions accept identity-based binding-key updates.
    Contract:
        - update_transaction_for_identity refreshes staged binding keys.
    Returns:
        None.
    Raises:
        AssertionError: If staged binding metadata does not update.
    """
    frame = _make_frame("component-tx-surface-bind-update")
    try:
        identity, spellbook = _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-1",
            conjured=False,
        )
        mediator = frame.dev_ops_manager.change_control_manager.transaction_mediator()

        session = mediator.start_transaction(
            identity=identity,
            transaction_type="bind",
            metadata={},
        )
        updated = mediator.update_transaction_for_identity(
            identity=identity,
            transaction_type="bind",
            binding_keys=(("frame", "__default__"),),
        )

        assert updated is True
        assert session.staged.binding_keys == (("frame", "__default__"),)
        mediator.end_transaction_for_identity(
            identity=identity,
            transaction_type="bind",
        )
        spellbook._clear_bind_transaction_state.assert_called_once_with()
    finally:
        frame.cleanup()


def test_component_transaction_surface_update_transaction_returns_false_without_active_session() -> None:
    """
    Purpose:
        Validate staged updates no-op when no matching live session exists.
    Contract:
        - update_transaction_for_identity returns False without an active session.
    Returns:
        None.
    Raises:
        AssertionError: If inactive updates return True.
    """
    frame = _make_frame("component-tx-surface-no-session")
    try:
        identity, _spellbook = _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-1",
            conjured=False,
        )
        mediator = frame.dev_ops_manager.change_control_manager.transaction_mediator()

        assert (
            mediator.update_transaction_for_identity(
                identity=identity,
                transaction_type="bind",
                binding_keys=(("frame", "__default__"),),
            )
            is False
        )
    finally:
        frame.cleanup()


def test_component_transaction_surface_end_transaction_for_identity_requires_matching_session() -> None:
    """
    Purpose:
        Validate identity-based end rejects when no session matches.
    Contract:
        - Missing sessions raise RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If missing sessions are silently ignored.
    """
    frame = _make_frame("component-tx-surface-end-missing")
    try:
        identity, _spellbook = _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-1",
            conjured=False,
        )
        mediator = frame.dev_ops_manager.change_control_manager.transaction_mediator()

        with pytest.raises(RuntimeError, match="No active transaction session exists"):
            mediator.end_transaction_for_identity(
                identity=identity,
                transaction_type="bind",
            )
    finally:
        frame.cleanup()


def test_component_transaction_surface_mark_abort_only_clears_registry_mirror_on_end() -> None:
    """
    Purpose:
        Validate abort-only sessions clear the live transaction mirror on end.
    Contract:
        - mark_active_session_abort_only poisons the session.
        - Ending the session removes the mirrored transaction from the registry.
    Returns:
        None.
    Raises:
        AssertionError: If abort teardown leaves mirrored transaction state behind.
    """
    frame = _make_frame("component-tx-surface-abort")
    try:
        identity, spellbook = _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-1",
            conjured=False,
        )
        mediator = frame.dev_ops_manager.change_control_manager.transaction_mediator()

        session = mediator.start_transaction(
            identity=identity,
            transaction_type="bind",
            metadata={},
        )
        mediator.mark_active_session_abort_only(reason="fail")
        mediator.end_transaction_for_identity(
            identity=identity,
            transaction_type="bind",
        )

        assert session.status == session.STATUS_ABORTED
        assert frame.devops_information_registry.list_live_transactions_for_identity(
            owner_kind="spellbook",
            owner_id="spellbook-1",
        ) == ()
        spellbook._clear_bind_transaction_state.assert_called_once_with()
    finally:
        frame.cleanup()


def test_component_transaction_surface_get_active_request_returns_live_root_request() -> None:
    """
    Purpose:
        Validate live root requests are observable on the active thread.
    Contract:
        - get_active_request returns the session root request while active.
    Returns:
        None.
    Raises:
        AssertionError: If active requests are not exposed.
    """
    frame = _make_frame("component-tx-surface-active-request")
    try:
        identity, _spellbook = _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-1",
            conjured=False,
        )
        mediator = frame.dev_ops_manager.change_control_manager.transaction_mediator()

        session = mediator.start_transaction(
            identity=identity,
            transaction_type="bind",
            metadata={},
        )

        assert mediator.get_active_request() is session.request
        mediator.end_transaction_for_identity(
            identity=identity,
            transaction_type="bind",
        )
    finally:
        frame.cleanup()


def test_component_transaction_surface_describe_reports_live_request_ids() -> None:
    """
    Purpose:
        Validate mediator describe exposes current request ids.
    Contract:
        - describe includes the active request id while the session is live.
    Returns:
        None.
    Raises:
        AssertionError: If request-id reporting drifts.
    """
    frame = _make_frame("component-tx-surface-describe")
    try:
        identity, _spellbook = _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-1",
            conjured=False,
        )
        mediator = frame.dev_ops_manager.change_control_manager.transaction_mediator()

        session = mediator.start_transaction(
            identity=identity,
            transaction_type="bind",
            metadata={},
        )

        described = mediator.describe()
        assert described["request_ids"] == (session.request.request_id,)
        mediator.end_transaction_for_identity(
            identity=identity,
            transaction_type="bind",
        )
    finally:
        frame.cleanup()


def test_component_transaction_surface_link_session_registers_live_transaction_mirror() -> None:
    """
    Purpose:
        Validate link sessions are mirrored through the frame registry.
    Contract:
        - A live link session is discoverable by conduit identity and type.
    Returns:
        None.
    Raises:
        AssertionError: If link session mirroring is incomplete.
    """
    frame = _make_frame("component-tx-surface-link-registry")
    try:
        conduit_identity, _source = _register_conduit_identity(
            frame,
            conduit_id="conduit-1",
            spellbook_id="spellbook-1",
        )
        _register_conduit_identity(
            frame,
            conduit_id="conduit-2",
            spellbook_id="spellbook-2",
        )
        _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-1",
            conjured=True,
            conduit_id="conduit-1",
        )
        _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-2",
            conjured=True,
            conduit_id="conduit-2",
        )
        mediator = frame.dev_ops_manager.change_control_manager.transaction_mediator()

        session = mediator.start_transaction(
            identity=conduit_identity,
            transaction_type="link",
            metadata={"conduit_ids": ("conduit-2",)},
        )

        assert frame.devops_information_registry.list_live_transactions_for_identity(
            owner_kind="conduit",
            owner_id="conduit-1",
        ) == (session,)
        assert frame.devops_information_registry.list_live_transactions_for_type("link") == (
            session,
        )
        mediator.end_transaction_for_identity(
            identity=conduit_identity,
            transaction_type="link",
        )
    finally:
        frame.cleanup()


def test_component_transaction_surface_cluster_link_session_registers_live_transaction_mirror() -> None:
    """
    Purpose:
        Validate cluster-link sessions are mirrored through the frame registry.
    Contract:
        - A live cluster-link session is discoverable by cluster identity and type.
    Returns:
        None.
    Raises:
        AssertionError: If cluster-link session mirroring is incomplete.
    """
    frame = _make_frame("component-tx-surface-cluster-registry")
    try:
        cluster_identity = DevopsIdentity(
            owner_kind="conduit_cluster",
            owner_id="cluster-1",
            aetheric_frame_name=frame.name,
            metadata={"cluster_name": "alpha"},
            available_transactions=("cluster_link",),
        )
        cluster_identity.attach_registry(
            frame.devops_information_registry,
            object_ref=_FakeCluster(("conduit-1", "conduit-2")),
        )
        _register_conduit_identity(
            frame,
            conduit_id="conduit-1",
            spellbook_id="spellbook-1",
        )
        _register_conduit_identity(
            frame,
            conduit_id="conduit-2",
            spellbook_id="spellbook-2",
        )
        _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-1",
            conjured=True,
            conduit_id="conduit-1",
        )
        _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-2",
            conjured=True,
            conduit_id="conduit-2",
        )
        mediator = frame.dev_ops_manager.change_control_manager.transaction_mediator()

        session = mediator.start_transaction(
            identity=cluster_identity,
            transaction_type="cluster_link",
            metadata={
                "cluster_id": "cluster-1",
                "conduit_ids": ("conduit-1", "conduit-2"),
            },
        )

        assert frame.devops_information_registry.list_live_transactions_for_identity(
            owner_kind="conduit_cluster",
            owner_id="cluster-1",
        ) == (session,)
        assert frame.devops_information_registry.list_live_transactions_for_type(
            "cluster_link"
        ) == (session,)
        mediator.end_transaction_for_identity(
            identity=cluster_identity,
            transaction_type="cluster_link",
        )
    finally:
        frame.cleanup()


def test_component_transaction_surface_bind_session_exposes_active_request() -> None:
    """
    Purpose:
        Validate bind sessions expose the current active root request.
    Contract:
        - get_active_request returns the bind request while the session is live.
    Returns:
        None.
    Raises:
        AssertionError: If the live bind request is not exposed.
    """
    frame = _make_frame("component-tx-surface-bind-active")
    try:
        identity, _spellbook = _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-1",
            conjured=False,
        )
        mediator = frame.dev_ops_manager.change_control_manager.transaction_mediator()

        session = mediator.start_transaction(
            identity=identity,
            transaction_type="bind",
            metadata={},
        )

        assert mediator.get_active_request() is session.request
        mediator.end_transaction_for_identity(
            identity=identity,
            transaction_type="bind",
        )
    finally:
        frame.cleanup()


def test_component_transaction_surface_link_session_exposes_active_request() -> None:
    """
    Purpose:
        Validate link sessions expose the current active root request.
    Contract:
        - get_active_request returns the live link request while the session is active.
    Returns:
        None.
    Raises:
        AssertionError: If the live link request is not exposed.
    """
    frame = _make_frame("component-tx-surface-link-active")
    try:
        conduit_identity, _source = _register_conduit_identity(
            frame,
            conduit_id="conduit-1",
            spellbook_id="spellbook-1",
        )
        _register_conduit_identity(
            frame,
            conduit_id="conduit-2",
            spellbook_id="spellbook-2",
        )
        _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-1",
            conjured=True,
            conduit_id="conduit-1",
        )
        _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-2",
            conjured=True,
            conduit_id="conduit-2",
        )
        mediator = frame.dev_ops_manager.change_control_manager.transaction_mediator()

        session = mediator.start_transaction(
            identity=conduit_identity,
            transaction_type="link",
            metadata={"conduit_ids": ("conduit-2",)},
        )

        assert mediator.get_active_request() is session.request
        mediator.end_transaction_for_identity(
            identity=conduit_identity,
            transaction_type="link",
        )
    finally:
        frame.cleanup()


def test_component_transaction_surface_bind_session_describe_updates_after_binding_key_extension() -> None:
    """
    Purpose:
        Validate bind session describe reflects a live updated request id set.
    Contract:
        - describe keeps the active request id visible after binding-key extension.
    Returns:
        None.
    Raises:
        AssertionError: If mediator describe drifts after staged updates.
    """
    frame = _make_frame("component-tx-surface-bind-describe")
    try:
        identity, _spellbook = _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-1",
            conjured=False,
        )
        mediator = frame.dev_ops_manager.change_control_manager.transaction_mediator()

        session = mediator.start_transaction(
            identity=identity,
            transaction_type="bind",
            metadata={},
        )
        mediator.update_transaction_for_identity(
            identity=identity,
            transaction_type="bind",
            binding_keys=(("frame", "__default__"),),
        )

        assert mediator.describe()["request_ids"] == (session.request.request_id,)
        assert session.staged.binding_keys == (("frame", "__default__"),)
        mediator.end_transaction_for_identity(
            identity=identity,
            transaction_type="bind",
        )
    finally:
        frame.cleanup()


def test_component_transaction_surface_link_session_describe_updates_after_contract_extension() -> None:
    """
    Purpose:
        Validate link session describe remains stable after staged contract updates.
    Contract:
        - describe keeps the active request id visible after contract-key extension.
    Returns:
        None.
    Raises:
        AssertionError: If mediator describe drifts after contract updates.
    """
    frame = _make_frame("component-tx-surface-link-describe")
    try:
        conduit_identity, _source = _register_conduit_identity(
            frame,
            conduit_id="conduit-1",
            spellbook_id="spellbook-1",
        )
        _register_conduit_identity(
            frame,
            conduit_id="conduit-2",
            spellbook_id="spellbook-2",
        )
        _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-1",
            conjured=True,
            conduit_id="conduit-1",
        )
        _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-2",
            conjured=True,
            conduit_id="conduit-2",
        )
        mediator = frame.dev_ops_manager.change_control_manager.transaction_mediator()

        session = mediator.start_transaction(
            identity=conduit_identity,
            transaction_type="link",
            metadata={"conduit_ids": ("conduit-2",)},
        )
        mediator.update_transaction_for_identity(
            identity=conduit_identity,
            transaction_type="link",
            contract_keys=(("frame", "__default__", "conduit-2"),),
        )

        assert mediator.describe()["request_ids"] == (session.request.request_id,)
        assert session.staged.contract_keys == (("frame", "__default__", "conduit-2"),)
        mediator.end_transaction_for_identity(
            identity=conduit_identity,
            transaction_type="link",
        )
    finally:
        frame.cleanup()


def test_component_transaction_surface_cluster_link_describe_reports_active_request() -> None:
    """
    Purpose:
        Validate cluster-link sessions keep the active request visible in describe.
    Contract:
        - describe includes the active cluster-link request id while the session is live.
    Returns:
        None.
    Raises:
        AssertionError: If active cluster-link requests disappear from describe.
    """
    frame = _make_frame("component-tx-surface-cluster-describe")
    try:
        cluster_identity = DevopsIdentity(
            owner_kind="conduit_cluster",
            owner_id="cluster-1",
            aetheric_frame_name=frame.name,
            metadata={"cluster_name": "alpha"},
            available_transactions=("cluster_link",),
        )
        cluster_identity.attach_registry(
            frame.devops_information_registry,
            object_ref=_FakeCluster(("conduit-1", "conduit-2")),
        )
        _register_conduit_identity(
            frame,
            conduit_id="conduit-1",
            spellbook_id="spellbook-1",
        )
        _register_conduit_identity(
            frame,
            conduit_id="conduit-2",
            spellbook_id="spellbook-2",
        )
        _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-1",
            conjured=True,
            conduit_id="conduit-1",
        )
        _register_spellbook_identity(
            frame,
            spellbook_id="spellbook-2",
            conjured=True,
            conduit_id="conduit-2",
        )
        mediator = frame.dev_ops_manager.change_control_manager.transaction_mediator()

        session = mediator.start_transaction(
            identity=cluster_identity,
            transaction_type="cluster_link",
            metadata={
                "cluster_id": "cluster-1",
                "conduit_ids": ("conduit-1", "conduit-2"),
            },
        )

        assert mediator.describe()["request_ids"] == (session.request.request_id,)
        mediator.end_transaction_for_identity(
            identity=cluster_identity,
            transaction_type="cluster_link",
        )
    finally:
        frame.cleanup()
