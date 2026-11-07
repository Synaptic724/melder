"""Regression coverage for exact DevOps transaction names and old contracts."""

import base64
import pickle
from threading import RLock
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from melder.aether.aetheric_frame.dev_ops.change_control_manager.change_control_manager import (
    ChangeControlManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.embargo_manager.embargo_manager import (
    ChangeControlEmbargoManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.orchestrator import (
    ChangeControlOrchestrator,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.staged_mutation import (
    ChangeControlStagedMutation,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.transaction_strategy import (
    TransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.transaction_strategy_builder import (
    TransactionStrategyBuilder,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.aether.aetheric_frame.dev_ops.devops_identity import DevopsIdentity
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import DevopsInformationRegistry
from melder.aether.aetheric_frame.dev_ops.information_strategies.transaction_activity_view_strategy import (
    TransactionActivityViewStrategy,
)


@pytest.mark.parametrize("member", tuple(ChangeTransactionType))
def test_transaction_value_is_exact_member_name(member: ChangeTransactionType) -> None:
    """Exact values coexist with the original lowercase by-value reader."""
    assert member.value == member.name
    assert str(member) == member.name
    assert ChangeTransactionType(member.name) is member
    assert ChangeTransactionType(member.name.lower()) is member


@pytest.mark.parametrize(
    "payload,expected",
    (
        ("gASVjAAAAAAAAACMY21lbGRlci5hZXRoZXIuYWV0aGVyaWNfZnJhbWUuZGV2X29wcy5jaGFuZ2VfY29udHJvbF9tYW5hZ2VyLnRyYW5zYWN0aW9uX3JlcXVlc3QudHJhbnNhY3Rpb25fcmVxdWVzdJSMFUNoYW5nZVRyYW5zYWN0aW9uVHlwZZSTlIwEYmluZJSFlFKULg==", ChangeTransactionType.BIND),
        ("gASVmgAAAAAAAACMY21lbGRlci5hZXRoZXIuYWV0aGVyaWNfZnJhbWUuZGV2X29wcy5jaGFuZ2VfY29udHJvbF9tYW5hZ2VyLnRyYW5zYWN0aW9uX3JlcXVlc3QudHJhbnNhY3Rpb25fcmVxdWVzdJSMFUNoYW5nZVRyYW5zYWN0aW9uVHlwZZSTlIwSdHJhbnNmZXJfb3duZXJzaGlwlIWUUpQu", ChangeTransactionType.TRANSFER_OWNERSHIP),
        ("gASVlQAAAAAAAACMY21lbGRlci5hZXRoZXIuYWV0aGVyaWNfZnJhbWUuZGV2X29wcy5jaGFuZ2VfY29udHJvbF9tYW5hZ2VyLnRyYW5zYWN0aW9uX3JlcXVlc3QudHJhbnNhY3Rpb25fcmVxdWVzdJSMFUNoYW5nZVRyYW5zYWN0aW9uVHlwZZSTlIwNY2x1c3Rlcl9sZWF2ZZSFlFKULg==", ChangeTransactionType.CLUSTER_LEAVE),
    ),
)
def test_old_pickles_reconstruct_same_member(payload: str, expected: ChangeTransactionType) -> None:
    """Previously serialized lowercase values remain readable."""
    assert pickle.loads(base64.b64decode(payload)) is expected


@pytest.mark.parametrize("value", ("Bind", "Transfer_Ownership", "unknown", ""))
def test_unknown_value_spellings_are_not_normalized(value: str) -> None:
    """The enum reader accepts only canonical or exact historical values."""
    with pytest.raises(ValueError):
        ChangeTransactionType(value)


def test_builder_resolves_member_old_and_canonical_names() -> None:
    """The existing normalized dispatch keeps all three supported inputs."""
    manager = ChangeControlTransactionManager()
    registry = DevopsInformationRegistry("frame")
    try:
        builder = TransactionStrategyBuilder(manager, registry)
        assert builder.resolve(ChangeTransactionType.BIND) is builder.resolve("bind")
        assert builder.resolve(ChangeTransactionType.BIND) is builder.resolve("BIND")
    finally:
        registry.cleanup()
        manager.cleanup()


def test_admission_and_fact_reporting_keep_lowercase_tokens() -> None:
    """Real admission and commit-delta reporting preserve the original token."""
    manager = ChangeControlTransactionManager()
    embargo = ChangeControlEmbargoManager()
    orchestrator = ChangeControlOrchestrator()
    registry = DevopsInformationRegistry("frame")
    identity = DevopsIdentity(
        owner_kind="spellbook", owner_id="book", aetheric_frame_name="frame",
        metadata={}, available_transactions=("bind",),
    )
    try:
        request = manager.build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="owner", spellbook_id="book", scope_keys=("scope-a",),
        )
        result = orchestrator.admit_request(
            request, transaction_manager=manager, conflict_manager=None, embargo_manager=embargo,
        )
        assert result.admitted
        assert embargo.list_advisory_hints(("scope-a",))[0].reason_tag == "bind"
        staged = orchestrator.get_staged(request.request_id)
        TransactionStrategy.apply_commit_delta(
            devops_information_registry=registry, identity=identity, staged=staged,
        )
        assert registry.get_fact_record(fact_family="bind", region="spellbook:book") is not None
        orchestrator.abort_request(
            request.request_id, transaction_manager=manager, embargo_manager=embargo,
        )
    finally:
        identity.cleanup()
        registry.cleanup()
        orchestrator.cleanup()
        embargo.cleanup()
        manager.cleanup()


def test_activity_view_preserves_member_token_and_plain_input() -> None:
    """Member reporting stays lowercase while plain input keeps its own spelling."""
    registry = DevopsInformationRegistry("frame")
    try:
        registry.register_transaction(transaction_id="tx-1", transaction_object=object(), transaction_type="bind")
        view = TransactionActivityViewStrategy.execute(
            devops_information_registry=registry, metadata={"transaction_type": ChangeTransactionType.BIND},
        )
        assert view["axis_value"] == "bind"
        assert view["transaction_ids"] == ("tx-1",)
        plain = TransactionActivityViewStrategy.execute(
            devops_information_registry=registry, metadata={"transaction_type": "BIND"},
        )
        assert plain["axis_value"] == "BIND"
        assert plain["transaction_ids"] == ("tx-1",)
    finally:
        registry.cleanup()


@pytest.mark.parametrize(
    "kind,should_run",
    ((ChangeTransactionType.BIND, True), ("bind", True), ("BIND", True),
     (ChangeTransactionType.NOTCH, False), ("notch", True), ("NOTCH", True),
     ("Bind", False), ("unrelated", False)),
)
def test_structural_gate_preserves_old_string_and_notch_identity(kind: object, should_run: bool) -> None:
    """Exact and legacy strings enter; only the actual notch member has its special skip."""
    states = SimpleNamespace(_frame=None)
    manager = ChangeControlManager(states)
    index = object()
    spell = SimpleNamespace(
        validation_result_phase4=None,
        _compiler_artifact=SimpleNamespace(_root_blueprint_phase5=object()),
    )
    book = MagicMock()
    book._id = "book"
    book._conjured = True
    book._lock = RLock()
    book._lookup_spells = {("frame", "key"): index}
    book._spells = {index: spell}
    states._frame = SimpleNamespace(_lock=RLock(), _conduits={"conduit": SimpleNamespace(_spellbook=book)})
    staged = ChangeControlStagedMutation.from_request(
        request_id="req-1", request_type=kind, initiator_conduit_id="conduit",
        spellbook_id="book", conduit_ids=("conduit",), scope_keys=(),
        binding_keys=(("frame", "key"),), contract_keys=(), metadata=None,
    )
    try:
        manager._default_structural_validator(staged)
        if should_run:
            book._run_post_conjure_structural_phases.assert_called_once_with([spell])
        else:
            book._run_post_conjure_structural_phases.assert_not_called()
    finally:
        manager.cleanup()

@pytest.mark.parametrize("kind", ("bind", ChangeTransactionType.BIND.value, ChangeTransactionType.BIND))
def test_bind_value_commit_does_not_skip_structural_failure(kind: object) -> None:
    """A canonical bind value must abort when the structural phase rejects the commit."""
    states = SimpleNamespace(
        _frame=None, mark_collection_dependents_dirty=MagicMock(),
        mark_contract_dependents_dirty=MagicMock(),
    )
    manager = ChangeControlManager(states)
    index = object()
    spell = SimpleNamespace(
        validation_result_phase4=None,
        _compiler_artifact=SimpleNamespace(_root_blueprint_phase5=None),
    )
    book = MagicMock()
    book._id = "book"
    book._conjured = True
    book._lock = RLock()
    book._lookup_spells = {("frame", "key"): index}
    book._spells = {index: spell}
    book._run_post_conjure_structural_phases.side_effect = RuntimeError("structural check failed")
    states._frame = SimpleNamespace(_lock=RLock(), _conduits={"conduit": SimpleNamespace(_spellbook=book)})
    identity = DevopsIdentity(
        owner_kind="spellbook", owner_id="book", aetheric_frame_name="frame",
        metadata={}, available_transactions=("bind",),
    )
    try:
        mediator = manager.transaction_mediator()
        session = mediator.begin_transaction(
            identity=identity, transaction_type=kind, initiator_conduit_id="conduit",
            spellbook_id="book", conduit_ids=("conduit",), binding_keys=(("frame", "key"),),
        )
        with pytest.raises(RuntimeError, match="structural check failed"):
            mediator.end_transaction(expected_type=kind)
        book._run_post_conjure_structural_phases.assert_called_once_with([spell])
        assert session.status == "aborted"
        assert manager.transaction_manager().get_in_flight(session.request.request_id) is None
        assert mediator.get_active_session() is None
    finally:
        identity.cleanup()
        manager.cleanup()
