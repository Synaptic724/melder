from __future__ import annotations

from typing import Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
    apply_dynamic_defaults_for_spellbook_configuration,
)
@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_transactions() -> None:
    """
    Purpose:
        Ensure component transaction tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_spellbook(*, dynamic: bool) -> Spellbook:
    """
    Purpose:
        Build a spellbook for conduit transaction component tests.
    Contract:
        - system_state defaults to automatic or dynamic.
        - phase_scheduler_workers_per_spellbook is set.
    Args:
        dynamic: Whether to enable dynamic defaults.
    Returns:
        Spellbook: Configured spellbook.
    """
    config = SpellbookConfiguration()
    if dynamic:
        apply_dynamic_defaults_for_spellbook_configuration(config)
    else:
        apply_automatic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=config)


def _get_local_spell_by_version_id(
        spellbook: Spellbook,
        spell_id: str,
) -> Optional[object]:
    """
    Purpose:
        Resolve one locally owned spell by its current version id.
    Contract:
        - Returns the first local spell whose SpellIndex.current matches the
          supplied version id.
        - Returns None when no local spell matches.
    Args:
        spellbook: Spellbook whose local spell map should be searched.
        spell_id: Current version id to resolve.
    Returns:
        Optional[object]: Matching local spell object, or None when absent.
    """
    for spell_index, spell in spellbook.spells.items():
        if spell_index.current == spell_id:
            return spell
    return None


def test_component_conduit_begin_transaction_link_requires_dynamic_mode() -> None:
    """
    Purpose:
        Validate link transactions are rejected in automatic mode.
    Contract:
        - begin_transaction("link") raises when conduit is not dynamic.
    Returns:
        None.
    Raises:
        AssertionError: If link admission does not enforce dynamic mode.
    """
    owner_book = _make_spellbook(dynamic=False)
    peer_book = _make_spellbook(dynamic=False)
    owner = owner_book.conjure(name="owner")
    peer = peer_book.conjure(name="peer")
    try:
        with pytest.raises(RuntimeError, match="dynamic mode"):
            owner.begin_transaction("link", conduits=[owner, peer])
    finally:
        owner.cleanup()
        peer.cleanup()


def test_component_conduit_begin_transaction_link_registers_in_flight() -> None:
    """
    Purpose:
        Validate link transactions register in-flight requests.
    Contract:
        - In-flight request includes borrower and peer conduit ids.
        - Request scope keys include the borrower conduit scope.
    Returns:
        None.
    Raises:
        AssertionError: If in-flight registration is incorrect.
    """
    owner_book = _make_spellbook(dynamic=True)
    borrower_book = _make_spellbook(dynamic=True)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    change_control = Aether()._get_change_control_manager("default")
    try:
        borrower.begin_transaction("link", conduits=[borrower, owner])
        in_flight = change_control.transaction_manager().list_in_flight()
        assert len(in_flight) == 1
        request = in_flight[0]
        assert request.request_type is ChangeTransactionType.LINK
        assert borrower.id in request.conduit_ids
        assert owner.id in request.conduit_ids
        assert f"scope:conduit:{borrower.id}" in request.scope_keys
    finally:
        borrower.end_transaction("link")
        owner.cleanup()
        borrower.cleanup()


def test_component_conduit_transaction_context_closes_in_flight() -> None:
    """
    Purpose:
        Validate transaction context manager clears in-flight requests.
    Contract:
        - In-flight request exists inside the context.
        - In-flight registry is cleared after context exit.
    Returns:
        None.
    Raises:
        AssertionError: If context does not clear in-flight state.
    """
    owner_book = _make_spellbook(dynamic=True)
    borrower_book = _make_spellbook(dynamic=True)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    change_control = Aether()._get_change_control_manager("default")
    try:
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert len(change_control.transaction_manager().list_in_flight()) == 1
        assert change_control.transaction_manager().list_in_flight() == []
    finally:
        owner.cleanup()
        borrower.cleanup()


def test_component_conduit_begin_transaction_bind_registers_spellbook_session_in_registry() -> None:
    """
    Purpose:
        Validate conduit-side bind entry registers the live spellbook bind session.
    Contract:
        - begin_transaction("bind") through the conduit surface produces one
          live bind transaction visible by spellbook identity and type.
    Returns:
        None.
    Raises:
        AssertionError: If the live bind session is not mirrored correctly.
    """
    spellbook = _make_spellbook(dynamic=True)
    conduit = spellbook.conjure(automatic=False, name="root")
    registry = conduit._aetheric_frame.devops_information_registry
    try:
        conduit.begin_transaction("bind")
        sessions = registry.list_live_transactions_for_identity(
            owner_kind="spellbook",
            owner_id=spellbook.id,
        )
        assert len(sessions) == 1
        assert sessions[0].request.request_type is ChangeTransactionType.BIND
        assert registry.list_live_transactions_for_type("bind") == sessions
    finally:
        conduit.end_transaction("bind")
        conduit.cleanup()


def test_component_conduit_end_transaction_bind_clears_spellbook_session_registry_mirror() -> None:
    """
    Purpose:
        Validate conduit-side bind exit clears the live registry mirror.
    Contract:
        - Ending a conduit-initiated bind transaction removes the mirrored bind session.
    Returns:
        None.
    Raises:
        AssertionError: If the live bind session remains mirrored after end.
    """
    spellbook = _make_spellbook(dynamic=True)
    conduit = spellbook.conjure(automatic=False, name="root")
    registry = conduit._aetheric_frame.devops_information_registry
    try:
        conduit.begin_transaction("bind")
        conduit.end_transaction("bind")
        assert registry.list_live_transactions_for_identity(
            owner_kind="spellbook",
            owner_id=spellbook.id,
        ) == ()
    finally:
        conduit.cleanup()


def test_component_conduit_bind_transaction_context_exposes_active_request() -> None:
    """
    Purpose:
        Validate conduit-side bind context exposes the live active request.
    Contract:
        - The mediator active request is a bind request while the context is live.
    Returns:
        None.
    Raises:
        AssertionError: If the active request is missing or wrong.
    """
    spellbook = _make_spellbook(dynamic=True)
    conduit = spellbook.conjure(automatic=False, name="root")
    mediator = spellbook._get_required_transaction_mediator()
    try:
        with conduit.transaction("bind"):
            request = mediator.get_active_request()
            assert request is not None
            assert request.request_type is ChangeTransactionType.BIND
        assert mediator.get_active_request() is None
    finally:
        conduit.cleanup()


def test_component_conduit_begin_transaction_link_registers_live_registry_session() -> None:
    """
    Purpose:
        Validate conduit-side link entry registers the live conduit session in the registry.
    Contract:
        - begin_transaction("link") through the conduit surface produces one
          live link transaction visible by conduit identity and type.
    Returns:
        None.
    Raises:
        AssertionError: If the live link session is not mirrored correctly.
    """
    owner_book = _make_spellbook(dynamic=True)
    borrower_book = _make_spellbook(dynamic=True)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    registry = borrower._aetheric_frame.devops_information_registry
    try:
        borrower.begin_transaction("link", conduits=[borrower, owner])
        sessions = registry.list_live_transactions_for_identity(
            owner_kind="conduit",
            owner_id=borrower.id,
        )
        assert len(sessions) == 1
        assert sessions[0].request.request_type is ChangeTransactionType.LINK
        assert registry.list_live_transactions_for_type("link") == sessions
    finally:
        borrower.end_transaction("link")
        owner.cleanup()
        borrower.cleanup()


@pytest.mark.parametrize(
    "flag_name",
    (
        "disable_linking",
        "disable_all_transactions_after_conjure",
    ),
)
def test_component_conduit_begin_transaction_link_respects_frame_disable_flags(
        flag_name: str,
) -> None:
    """
    Purpose:
        Validate conduit-side link entry respects frame posture disable flags.
    Contract:
        - Link transactions are rejected when the matching frame gate is disabled.
    Args:
        flag_name: Frame configuration flag that should block link entry.
    Returns:
        None.
    Raises:
        AssertionError: If link entry bypasses the frame posture gate.
    """
    owner_book = _make_spellbook(dynamic=True)
    borrower_book = _make_spellbook(dynamic=True)
    getattr(borrower_book._aetheric_frame_configuration, f"with_{flag_name}")(True)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        with pytest.raises(RuntimeError, match="disabled"):
            borrower.begin_transaction("link", conduits=[borrower, owner])
    finally:
        owner.cleanup()
        borrower.cleanup()


@pytest.mark.parametrize(
    "flag_name",
    (
        "disable_bind",
        "disable_all_transactions_after_conjure",
    ),
)
def test_component_conduit_bind_respects_frame_disable_flags(
        flag_name: str,
) -> None:
    """
    Purpose:
        Validate conduit-side bind entry respects frame posture disable flags.
    Contract:
        - Public conduit.bind is rejected when the matching frame gate is disabled.
    Args:
        flag_name: Frame configuration flag that should block bind entry.
    Returns:
        None.
    Raises:
        AssertionError: If conduit.bind bypasses the frame posture gate.
    """
    spellbook = _make_spellbook(dynamic=True)
    getattr(spellbook._aetheric_frame_configuration, f"with_{flag_name}")(True)
    conduit = spellbook.conjure(automatic=False, name="root")
    try:
        with pytest.raises(RuntimeError, match="disabled"):
            conduit.bind(
                spell=BasicService,
                existence=Existence.unique,
                permissions="create",
            )
    finally:
        conduit.cleanup()


def test_component_conduit_begin_transaction_transfer_registers_live_registry_session() -> None:
    """
    Purpose:
        Validate conduit-side transfer entry registers the live conduit session.
    Contract:
        - begin_transaction("transfer_ownership") produces one live transfer
          session visible by conduit identity and type.
        - The staged transfer metadata preserves the target conduit and spell
          lineage identifiers needed by the execution body.
    Returns:
        None.
    Raises:
        AssertionError: If the live transfer session is not mirrored correctly.
    """
    owner_book = _make_spellbook(dynamic=True)
    target_book = _make_spellbook(dynamic=True)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    target = target_book.conjure(automatic=False, name="target")
    registry = owner._aetheric_frame.devops_information_registry
    spell = _get_local_spell_by_version_id(owner_book, spell_id)
    assert spell is not None
    started = False
    try:
        owner.begin_transaction(
            "transfer_ownership",
            metadata={
                "target_conduit_id": target.id,
                "spell_id": spell_id,
                "spell_index_id": spell.spell_index.id,
            },
        )
        started = True
        sessions = registry.list_live_transactions_for_identity(
            owner_kind="conduit",
            owner_id=owner.id,
        )
        assert len(sessions) == 1
        session = sessions[0]
        assert str(session.request.request_type) == "transfer_ownership"
        assert set(session.request.conduit_ids) == {owner.id, target.id}
        assert session.staged.binding_keys == (spell.key,)
        assert session.staged.metadata["target_conduit_id"] == target.id
        assert session.staged.metadata["spell_id"] == spell_id
        assert session.staged.metadata["spell_index_id"] == spell.spell_index.id
    finally:
        if started:
            owner.end_transaction("transfer_ownership")
        owner.cleanup()
        target.cleanup()


def test_component_conduit_transfer_transaction_context_clears_live_registry_session() -> None:
    """
    Purpose:
        Validate the transfer transaction context clears the live registry mirror.
    Contract:
        - A live transfer session exists inside the context.
        - The registry mirror is empty again after context exit.
    Returns:
        None.
    Raises:
        AssertionError: If the transfer session survives context exit.
    """
    owner_book = _make_spellbook(dynamic=True)
    target_book = _make_spellbook(dynamic=True)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    target = target_book.conjure(automatic=False, name="target")
    registry = owner._aetheric_frame.devops_information_registry
    spell = _get_local_spell_by_version_id(owner_book, spell_id)
    assert spell is not None
    try:
        with owner.transaction(
                "transfer_ownership",
                metadata={
                    "target_conduit_id": target.id,
                    "spell_id": spell_id,
                    "spell_index_id": spell.spell_index.id,
                },
        ):
            sessions = registry.list_live_transactions_for_identity(
                owner_kind="conduit",
                owner_id=owner.id,
            )
            assert len(sessions) == 1
            assert str(sessions[0].request.request_type) == "transfer_ownership"
        assert registry.list_live_transactions_for_identity(
            owner_kind="conduit",
            owner_id=owner.id,
        ) == ()
    finally:
        owner.cleanup()
        target.cleanup()


def test_component_conduit_transfer_spell_ownership_moves_spell_and_clears_registry_state() -> None:
    """
    Purpose:
        Validate the public transfer surface moves the lineage and clears the
        live registry mirror after success.
    Contract:
        - transfer_spell_ownership moves the SpellIndex lineage to the target
          spellbook.
        - The moved spell reports the target conduit as owner.
        - No live transfer session remains mirrored after completion.
    Returns:
        None.
    Raises:
        AssertionError: If lineage stewardship or registry cleanup is wrong.
    """
    owner_book = _make_spellbook(dynamic=True)
    target_book = _make_spellbook(dynamic=True)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    target = target_book.conjure(automatic=False, name="target")
    registry = owner._aetheric_frame.devops_information_registry
    spell = _get_local_spell_by_version_id(owner_book, spell_id)
    assert spell is not None
    spell_index_id = spell.spell_index.id
    try:
        summary = owner.transfer_spell_ownership(
            spell=spell_id,
            target_conduit=target,
        )
        assert summary["spell_id"] == spell_id
        assert summary["source"] == owner.id
        assert summary["target"] == target.id
        assert owner_book.get_spell_by_index_id(spell_index_id) is None
        transferred_spell = target_book.get_spell_by_index_id(spell_index_id)
        assert transferred_spell is not None
        assert transferred_spell._owner_conduit_id == target.id
        assert registry.list_live_transactions_for_identity(
            owner_kind="conduit",
            owner_id=owner.id,
        ) == ()
    finally:
        owner.cleanup()
        target.cleanup()


def test_component_conduit_transfer_transaction_abort_clears_registry_and_preserves_lineage() -> None:
    """
    Purpose:
        Validate aborted transfer transactions clear the live registry mirror.
    Contract:
        - A raised exception inside the transfer transaction aborts the root session.
        - The source spell remains owned by the source spellbook.
        - No live transfer session remains mirrored after abort.
    Returns:
        None.
    Raises:
        AssertionError: If abort cleanup or lineage preservation is wrong.
    """
    owner_book = _make_spellbook(dynamic=True)
    target_book = _make_spellbook(dynamic=True)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")
    target = target_book.conjure(automatic=False, name="target")
    registry = owner._aetheric_frame.devops_information_registry
    spell = _get_local_spell_by_version_id(owner_book, spell_id)
    assert spell is not None
    spell_index_id = spell.spell_index.id
    try:
        with pytest.raises(RuntimeError, match="boom"):
                with owner.transaction(
                        "transfer_ownership",
                        metadata={
                            "target_conduit_id": target.id,
                            "spell_id": spell_id,
                            "spell_index_id": spell.spell_index.id,
                        },
                ):
                    raise RuntimeError("boom")

        assert registry.list_live_transactions_for_type("transfer_ownership") == ()
        assert owner_book.get_spell_by_index_id(spell_index_id) is not None
        assert target_book.get_spell_by_index_id(spell_index_id) is None
    finally:
        owner.cleanup()
        target.cleanup()


def test_component_conduit_begin_transaction_cluster_link_registers_live_registry_session() -> None:
    """
    Purpose:
        Validate conduit-side cluster-link entry registers the live conduit session.
    Contract:
        - begin_transaction("cluster_link") produces one live cluster-link
          session visible by conduit identity.
        - The request retains the participating conduit ids and cluster metadata.
    Returns:
        None.
    Raises:
        AssertionError: If the live cluster-link session is not mirrored correctly.
    """
    owner_book = _make_spellbook(dynamic=True)
    borrower_book = _make_spellbook(dynamic=True)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    registry = borrower._aetheric_frame.devops_information_registry
    started = False
    try:
        borrower.begin_transaction(
            "cluster_link",
            conduit_ids=[owner.id],
            metadata={
                "cluster_id": "cluster-a",
                "conduit_ids": (borrower.id, owner.id),
            },
        )
        started = True
        sessions = registry.list_live_transactions_for_identity(
            owner_kind="conduit",
            owner_id=borrower.id,
        )
        assert len(sessions) == 1
        session = sessions[0]
        assert str(session.request.request_type) == "cluster_link"
        assert set(session.request.conduit_ids) == {borrower.id, owner.id}
        assert session.request.metadata["cluster_id"] == "cluster-a"
    finally:
        if started:
            borrower.end_transaction("cluster_link")
        owner.cleanup()
        borrower.cleanup()


def test_component_conduit_cluster_link_transaction_context_clears_live_registry_session() -> None:
    """
    Purpose:
        Validate the cluster-link transaction context clears the live registry mirror.
    Contract:
        - A live cluster-link session exists inside the context.
        - The registry mirror is empty again after context exit.
    Returns:
        None.
    Raises:
        AssertionError: If the cluster-link session survives context exit.
    """
    owner_book = _make_spellbook(dynamic=True)
    borrower_book = _make_spellbook(dynamic=True)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    registry = borrower._aetheric_frame.devops_information_registry
    try:
        with borrower.transaction(
                "cluster_link",
                conduit_ids=[owner.id],
                metadata={
                    "cluster_id": "cluster-a",
                    "conduit_ids": (borrower.id, owner.id),
                },
        ):
            sessions = registry.list_live_transactions_for_identity(
                owner_kind="conduit",
                owner_id=borrower.id,
            )
            assert len(sessions) == 1
            assert str(sessions[0].request.request_type) == "cluster_link"
        assert registry.list_live_transactions_for_identity(
            owner_kind="conduit",
            owner_id=borrower.id,
        ) == ()
    finally:
        owner.cleanup()
        borrower.cleanup()


def test_component_conduit_cluster_link_transaction_abort_clears_live_registry_session() -> None:
    """
    Purpose:
        Validate aborted cluster-link transactions clear the live registry mirror.
    Contract:
        - A raised exception inside the cluster-link transaction aborts the root session.
        - No live cluster-link session remains mirrored after abort.
    Returns:
        None.
    Raises:
        AssertionError: If abort leaves a live cluster-link session behind.
    """
    owner_book = _make_spellbook(dynamic=True)
    borrower_book = _make_spellbook(dynamic=True)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    registry = borrower._aetheric_frame.devops_information_registry
    try:
        with pytest.raises(RuntimeError, match="boom"):
            with borrower.transaction(
                    "cluster_link",
                    conduit_ids=[owner.id],
                    metadata={
                        "cluster_id": "cluster-a",
                        "conduit_ids": (borrower.id, owner.id),
                    },
            ):
                raise RuntimeError("boom")

        assert registry.list_live_transactions_for_type("cluster_link") == ()
    finally:
        owner.cleanup()
        borrower.cleanup()


@pytest.mark.parametrize(
    "flag_name",
    (
        "disable_transfer_of_ownership",
        "disable_all_transactions_after_conjure",
    ),
)
def test_component_conduit_begin_transaction_transfer_respects_frame_disable_flags(
        flag_name: str,
) -> None:
    """
    Purpose:
        Validate conduit-side transfer entry respects frame posture disable flags.
    Contract:
        - Transfer transactions are rejected when the matching frame gate is disabled.
    Args:
        flag_name: Frame configuration flag that should block transfer entry.
    Returns:
        None.
    Raises:
        AssertionError: If transfer entry bypasses the frame posture gate.
    """
    owner_book = _make_spellbook(dynamic=True)
    target_book = _make_spellbook(dynamic=True)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    getattr(owner_book._aetheric_frame_configuration, f"with_{flag_name}")(True)
    owner = owner_book.conjure(automatic=False, name="owner")
    target = target_book.conjure(automatic=False, name="target")
    spell = _get_local_spell_by_version_id(owner_book, spell_id)
    assert spell is not None
    try:
        with pytest.raises(RuntimeError, match="disabled"):
            owner.begin_transaction(
                "transfer_ownership",
                metadata={
                    "target_conduit_id": target.id,
                    "spell_id": spell_id,
                    "spell_index_id": spell.spell_index.id,
                },
            )
    finally:
        owner.cleanup()
        target.cleanup()


@pytest.mark.parametrize(
    "flag_name",
    (
        "disable_transfer_of_ownership",
        "disable_all_transactions_after_conjure",
    ),
)
def test_component_conduit_transfer_spell_ownership_respects_frame_disable_flags(
        flag_name: str,
) -> None:
    """
    Purpose:
        Validate the public transfer surface respects frame posture disable flags.
    Contract:
        - transfer_spell_ownership is rejected when the matching frame gate is disabled.
    Args:
        flag_name: Frame configuration flag that should block transfer execution.
    Returns:
        None.
    Raises:
        AssertionError: If the public transfer surface bypasses the frame gate.
    """
    owner_book = _make_spellbook(dynamic=True)
    target_book = _make_spellbook(dynamic=True)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    getattr(owner_book._aetheric_frame_configuration, f"with_{flag_name}")(True)
    owner = owner_book.conjure(automatic=False, name="owner")
    target = target_book.conjure(automatic=False, name="target")
    try:
        with pytest.raises(RuntimeError, match="disabled"):
            owner.transfer_spell_ownership(
                spell=spell_id,
                target_conduit=target,
            )
    finally:
        owner.cleanup()
        target.cleanup()


@pytest.mark.parametrize(
    "flag_name",
    (
        "disable_conduit_cluster",
        "disable_all_transactions_after_conjure",
    ),
)
def test_component_conduit_begin_transaction_cluster_link_respects_frame_disable_flags(
        flag_name: str,
) -> None:
    """
    Purpose:
        Validate conduit-side cluster-link entry respects frame posture disable flags.
    Contract:
        - Cluster-link transactions are rejected when the matching frame gate is disabled.
    Args:
        flag_name: Frame configuration flag that should block cluster-link entry.
    Returns:
        None.
    Raises:
        AssertionError: If cluster-link entry bypasses the frame posture gate.
    """
    owner_book = _make_spellbook(dynamic=True)
    borrower_book = _make_spellbook(dynamic=True)
    getattr(borrower_book._aetheric_frame_configuration, f"with_{flag_name}")(True)
    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        with pytest.raises(RuntimeError, match="disabled"):
            borrower.begin_transaction(
                "cluster_link",
                conduit_ids=[owner.id],
                metadata={
                    "cluster_id": "cluster-a",
                    "conduit_ids": (borrower.id, owner.id),
                },
            )
    finally:
        owner.cleanup()
        borrower.cleanup()


@pytest.mark.parametrize(
    "metadata",
    (
        {"spell_id": "spell-only"},
        {"target_conduit_id": "target-only"},
    ),
)
def test_component_conduit_begin_transaction_transfer_requires_complete_metadata(
        metadata: Dict[str, object],
) -> None:
    """
    Purpose:
        Validate transfer entry rejects incomplete planning metadata.
    Contract:
        - Missing target metadata or missing spell metadata causes the strategy
          planning step to raise before a live session is created.
    Args:
        metadata: Incomplete transfer metadata payload under test.
    Returns:
        None.
    Raises:
        AssertionError: If incomplete transfer metadata is accepted.
    """
    owner_book = _make_spellbook(dynamic=True)
    target_book = _make_spellbook(dynamic=True)
    owner = owner_book.conjure(automatic=False, name="owner")
    target = target_book.conjure(automatic=False, name="target")
    registry = owner._aetheric_frame.devops_information_registry
    normalized_metadata = dict(metadata)
    if normalized_metadata.get("target_conduit_id") == "target-only":
        normalized_metadata["target_conduit_id"] = target.id
    try:
        with pytest.raises(RuntimeError):
            owner.begin_transaction(
                "transfer_ownership",
                metadata=normalized_metadata,
            )
        assert registry.list_live_transactions_for_type("transfer_ownership") == ()
    finally:
        owner.cleanup()
        target.cleanup()
