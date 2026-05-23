from typing import Any, Callable, Dict, Optional, Tuple

import pytest

from melder.aether.aetheric_frame.dev_ops.change_control_manager.conflict_manager.conflict_manager import (
    ChangeControlConflictManager,
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
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.transaction_strategy_builder import (
    TransactionStrategyBuilder,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_mediator import (
    TransactionMediator,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_session import (
    TransactionSession,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)


def _build_request_and_staged() -> Tuple[object, ChangeControlStagedMutation]:
    """
    Build one admitted-shape request and staged payload for unit tests.
    """
    transaction_manager = ChangeControlTransactionManager()
    request = transaction_manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        spellbook_id="spellbook-1",
        scope_keys=["scope:spellbook:spellbook-1"],
    )
    staged = ChangeControlStagedMutation.from_request(
        request_id=request.request_id,
        request_type=request.request_type,
        initiator_conduit_id=request.initiator_conduit_id,
        spellbook_id=request.spellbook_id,
        conduit_ids=request.conduit_ids,
        scope_keys=request.scope_keys,
        binding_keys=request.binding_keys,
        contract_keys=request.contract_keys,
        metadata=request.metadata,
    )
    return request, staged


@pytest.mark.parametrize(
    ("label", "query", "expected"),
    [
        (
            "conduits_for_spellbook",
            lambda registry: registry.get_conduits_for_spellbook("missing"),
            (),
        ),
        (
            "primary_conduit_for_spellbook",
            lambda registry: registry.get_primary_conduit_id_for_spellbook("missing"),
            None,
        ),
        (
            "conduit_objects_for_spellbook",
            lambda registry: registry.get_conduit_objects_for_spellbook("missing"),
            (),
        ),
        (
            "spellbook_for_conduit",
            lambda registry: registry.get_spellbook_for_conduit("missing"),
            None,
        ),
        (
            "spellbook_object_for_conduit",
            lambda registry: registry.get_spellbook_object_for_conduit("missing"),
            None,
        ),
        (
            "borrowers_for_provider",
            lambda registry: registry.list_borrowers_for_provider("missing"),
            (),
        ),
        (
            "borrower_objects_for_provider",
            lambda registry: registry.list_borrower_conduit_objects_for_provider("missing"),
            (),
        ),
        (
            "providers_for_borrower",
            lambda registry: registry.list_providers_for_borrower("missing"),
            (),
        ),
        (
            "provider_objects_for_borrower",
            lambda registry: registry.list_provider_conduit_objects_for_borrower("missing"),
            (),
        ),
        (
            "conduits_for_cluster",
            lambda registry: registry.get_conduits_for_cluster("missing"),
            (),
        ),
        (
            "clusters_for_conduit",
            lambda registry: registry.get_clusters_for_conduit("missing"),
            (),
        ),
        (
            "cluster_objects_for_conduit",
            lambda registry: registry.get_cluster_objects_for_conduit("missing"),
            (),
        ),
        (
            "transaction_ids_for_identity",
            lambda registry: registry.list_transaction_ids_for_identity(
                owner_kind="spellbook",
                owner_id="missing",
            ),
            (),
        ),
        (
            "live_transactions_for_identity",
            lambda registry: registry.list_live_transactions_for_identity(
                owner_kind="spellbook",
                owner_id="missing",
            ),
            (),
        ),
        (
            "transaction_ids_for_type",
            lambda registry: registry.list_transaction_ids_for_type("missing"),
            (),
        ),
        (
            "live_transactions_for_type",
            lambda registry: registry.list_live_transactions_for_type("missing"),
            (),
        ),
    ],
)
def test_transaction_surface_registry_empty_queries_return_expected_defaults(
        label: str,
        query: Callable[[DevopsInformationRegistry], object],
        expected: object,
) -> None:
    """
    Purpose:
        Verify empty registry queries return stable empty/default values.
    Contract:
        - Missing topology and transaction lookups return empty snapshots or None.
    Returns:
        None.
    Raises:
        AssertionError: If empty-query defaults drift.
    """
    del label
    registry = DevopsInformationRegistry("frame-1")

    assert query(registry) == expected


@pytest.mark.parametrize(
    ("label", "actual", "expected"),
    [
        (
            "spellbook",
            lambda manager: manager.make_scope_key_spellbook("spellbook-1"),
            "scope:spellbook:spellbook-1",
        ),
        (
            "identity",
            lambda manager: manager.make_scope_key_identity(
                owner_kind="conduit_ward",
                owner_id="conduit-1",
            ),
            "scope:conduit_ward:conduit-1",
        ),
        (
            "transaction_owner",
            lambda manager: manager.make_scope_key_transaction_owner(
                owner_kind="spellbook",
                owner_id="spellbook-1",
                transaction_name="bind",
            ),
            "scope:transaction:spellbook:spellbook-1:bind",
        ),
        (
            "conduit",
            lambda manager: manager.make_scope_key_conduit("conduit-1"),
            "scope:conduit:conduit-1",
        ),
        (
            "cluster",
            lambda manager: manager.make_scope_key_cluster("cluster-1"),
            "scope:cluster:cluster-1",
        ),
        (
            "binding",
            lambda manager: manager.make_scope_key_binding("frame", "__default__"),
            "binding:frame:__default__",
        ),
        (
            "contract",
            lambda manager: manager.make_scope_key_contract(
                "frame",
                "__default__",
                "peer-1",
            ),
            "contract:frame:__default__:peer-1",
        ),
    ],
)
def test_transaction_surface_scope_key_builders_return_expected_values(
        label: str,
        actual: Callable[[ChangeControlTransactionManager], str],
        expected: str,
) -> None:
    """
    Purpose:
        Verify normalized scope-key builders return stable formats.
    Contract:
        - Scope-key helpers encode transaction scope using the documented prefixes.
    Returns:
        None.
    Raises:
        AssertionError: If helper output drifts.
    """
    del label
    manager = ChangeControlTransactionManager()

    assert actual(manager) == expected


@pytest.mark.parametrize(
    ("label", "method_name", "expected_status"),
    [
        ("committing", "mark_committing", TransactionSession.STATUS_COMMITTING),
        ("committed", "mark_committed", TransactionSession.STATUS_COMMITTED),
        ("aborted", "mark_aborted", TransactionSession.STATUS_ABORTED),
    ],
)
def test_transaction_surface_session_status_helpers_update_state(
        label: str,
        method_name: str,
        expected_status: str,
) -> None:
    """
    Purpose:
        Verify direct session status helpers update the live status field.
    Contract:
        - Each helper sets the expected runtime status.
    Returns:
        None.
    Raises:
        AssertionError: If status helpers drift.
    """
    del label
    request, staged = _build_request_and_staged()
    session = TransactionSession(
        request=request,
        staged=staged,
        owner_thread_id=1,
    )

    getattr(session, method_name)()

    assert session.status == expected_status


@pytest.mark.parametrize(
    ("label", "surface"),
    [
        ("request", lambda session: session.request),
        ("staged", lambda session: session.staged),
        ("owner_thread_id", lambda session: session.owner_thread_id),
        ("submitter_identity", lambda session: session.submitter_identity),
        ("depth", lambda session: session.depth),
        ("status", lambda session: session.status),
        ("failure_reason", lambda session: session.failure_reason),
        ("describe", lambda session: session.describe()),
    ],
)
def test_transaction_surface_session_cleanup_blocks_public_surfaces(
        label: str,
        surface: Callable[[TransactionSession], object],
) -> None:
    """
    Purpose:
        Verify cleaned sessions block public surface access.
    Contract:
        - Public accessors fail through check_cleaned after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleaned sessions still expose live state.
    """
    del label
    request, staged = _build_request_and_staged()
    session = TransactionSession(
        request=request,
        staged=staged,
        owner_thread_id=1,
    )
    session.cleanup()

    with pytest.raises(RuntimeError):
        surface(session)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("bind", "bind"),
        (" Bind ", "bind"),
        ("link", "link"),
        (ChangeTransactionType.CLUSTER_LINK, "cluster_link"),
        (ChangeTransactionType.TRANSFER_OWNERSHIP, "transfer_ownership"),
    ],
)
def test_transaction_surface_mediator_normalizes_valid_transaction_names(
        value: object,
        expected: str,
) -> None:
    """
    Purpose:
        Verify mediator transaction-name normalization for valid values.
    Contract:
        - Strings are stripped/lowercased.
        - Enum-backed values resolve to their string value.
    Returns:
        None.
    Raises:
        AssertionError: If normalization drifts.
    """
    assert TransactionMediator._normalize_transaction_name(value) == expected


@pytest.mark.parametrize(
    ("value", "expected_exception", "expected_message"),
    [
        (None, TypeError, "transaction_type must be a string-like value."),
        (" ", ValueError, "transaction_type must not be empty."),
        (object(), TypeError, "transaction_type must be a string-like value."),
        (1, TypeError, "transaction_type must be a string-like value."),
    ],
)
def test_transaction_surface_mediator_rejects_invalid_transaction_names(
        value: object,
        expected_exception: type[BaseException],
        expected_message: str,
) -> None:
    """
    Purpose:
        Verify mediator normalization rejects invalid values.
    Contract:
        - Non-string-like or empty values raise.
    Returns:
        None.
    Raises:
        AssertionError: If invalid values are accepted.
    """
    with pytest.raises(expected_exception, match=expected_message):
        TransactionMediator._normalize_transaction_name(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("bind", "bind"),
        (" Link ", "link"),
        (ChangeTransactionType.BIND, "bind"),
        (ChangeTransactionType.LINK, "link"),
        (ChangeTransactionType.CLUSTER_LINK, "cluster_link"),
    ],
)
def test_transaction_surface_strategy_builder_normalizes_valid_transaction_names(
        value: object,
        expected: str,
) -> None:
    """
    Purpose:
        Verify strategy-builder transaction-name normalization for valid values.
    Contract:
        - Strings are stripped/lowercased.
        - Enum values resolve to their string value.
    Returns:
        None.
    Raises:
        AssertionError: If normalization drifts.
    """
    assert TransactionStrategyBuilder._normalize_transaction_name(value) == expected


@pytest.mark.parametrize(
    ("value", "expected_exception", "expected_message"),
    [
        (None, TypeError, "transaction_type must be a ChangeTransactionType or string."),
        (" ", ValueError, "transaction_type must not be empty."),
        (object(), TypeError, "transaction_type must be a ChangeTransactionType or string."),
        (1, TypeError, "transaction_type must be a ChangeTransactionType or string."),
    ],
)
def test_transaction_surface_strategy_builder_rejects_invalid_transaction_names(
        value: object,
        expected_exception: type[BaseException],
        expected_message: str,
) -> None:
    """
    Purpose:
        Verify strategy-builder normalization rejects invalid values.
    Contract:
        - Non-string-like or empty values raise.
    Returns:
        None.
    Raises:
        AssertionError: If invalid values are accepted.
    """
    with pytest.raises(expected_exception, match=expected_message):
        TransactionStrategyBuilder._normalize_transaction_name(value)
