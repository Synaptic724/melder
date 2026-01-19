from melder.aether.dev_ops.change_control_manager.conflict_manager.conflict_manager import (
    ChangeControlConflictManager,
)
from melder.aether.dev_ops.change_control_manager.embargo_manager.embargo_manager import (
    ChangeControlEmbargoManager,
)
from melder.aether.dev_ops.change_control_manager.orchestrator.orchestrator import (
    ChangeControlOrchestrator,
)
from melder.aether.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)


def test_transaction_manager_build_request_populates_fields() -> None:
    """
    Purpose:
        Validate build_request returns a fully populated request payload.
    Contract:
        - request_id uses the "tx-" prefix.
        - scope keys, hashes, and metadata are normalized into tuples/dicts.
    Returns:
        None.
    Raises:
        AssertionError: If the request payload is missing expected fields.
    """
    manager = ChangeControlTransactionManager()
    request = manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        spellbook_id="spellbook-1",
        conduit_ids=["conduit-1", "conduit-2"],
        scope_keys=["spellbook:spellbook-1"],
        scope_hashes=["scope-hash"],
        binding_keys=[("frame", "__default__")],
        contract_keys=[("provider", "borrower", "read")],
        metadata={"note": "unit-test"},
    )

    assert request.request_id.startswith("tx-")
    assert request.request_type is ChangeTransactionType.BIND
    assert request.initiator_conduit_id == "conduit-1"
    assert request.spellbook_id == "spellbook-1"
    assert request.conduit_ids == ("conduit-1", "conduit-2")
    assert request.scope_keys == ("spellbook:spellbook-1",)
    assert request.scope_hashes == ("scope-hash",)
    assert request.binding_keys == (("frame", "__default__"),)
    assert request.contract_keys == (("provider", "borrower", "read"),)
    assert request.metadata["note"] == "unit-test"


def test_transaction_manager_in_flight_and_audit_logging() -> None:
    """
    Purpose:
        Validate in-flight registry updates and audit logging behavior.
    Contract:
        - add_in_flight stores the request and invokes the audit callback.
        - remove_in_flight clears the request from the registry.
    Returns:
        None.
    Raises:
        AssertionError: If in-flight state or audit logging is incorrect.
    """
    manager = ChangeControlTransactionManager()
    captured: list[str] = []

    def _audit(request) -> None:
        captured.append(request.request_id)

    manager.set_audit_logger(_audit)
    request = manager.build_request(
        request_type=ChangeTransactionType.LINK,
        initiator_conduit_id="conduit-1",
    )
    manager.add_in_flight(request)

    assert manager.get_in_flight(request.request_id) is request
    assert captured == [request.request_id]

    manager.remove_in_flight(request.request_id)
    assert manager.get_in_flight(request.request_id) is None


def test_transaction_manager_link_mirror_tracks_borrowers() -> None:
    """
    Purpose:
        Validate link mirror tracking for borrower/provider relationships.
    Contract:
        - register_link adds borrower to provider set.
        - unregister_link removes borrower and clears empty providers.
    Returns:
        None.
    Raises:
        AssertionError: If link mirror tracking is incorrect.
    """
    manager = ChangeControlTransactionManager()
    manager.register_link(borrower_conduit_id="borrower-1", provider_conduit_id="provider-1")
    assert manager.list_borrowers_for_provider("provider-1") == {"borrower-1"}

    manager.unregister_link(borrower_conduit_id="borrower-1", provider_conduit_id="provider-1")
    assert manager.list_borrowers_for_provider("provider-1") == set()


def test_conflict_manager_detects_scope_overlap() -> None:
    """
    Purpose:
        Validate scope-key overlap detection for conflict checks.
    Contract:
        - Overlapping scope keys yield a conflict id.
        - Disjoint scope keys yield no conflicts.
    Returns:
        None.
    Raises:
        AssertionError: If conflict detection is incorrect.
    """
    transaction_manager = ChangeControlTransactionManager()
    conflict_manager = ChangeControlConflictManager()

    active = transaction_manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        scope_keys=["shared-scope"],
    )
    incoming = transaction_manager.build_request(
        request_type=ChangeTransactionType.LINK,
        initiator_conduit_id="conduit-2",
        scope_keys=["shared-scope"],
    )

    conflicts = conflict_manager.find_conflicts(incoming, [active])
    assert conflicts == (active.request_id,)

    disjoint = transaction_manager.build_request(
        request_type=ChangeTransactionType.LINK,
        initiator_conduit_id="conduit-3",
        scope_keys=["other-scope"],
    )
    assert conflict_manager.find_conflicts(disjoint, [active]) == ()


def test_embargo_manager_open_close_and_find() -> None:
    """
    Purpose:
        Validate embargo open/close and lookup behavior.
    Contract:
        - open_embargo marks scopes as embargoed.
        - close_embargo releases all scopes for the owner.
    Returns:
        None.
    Raises:
        AssertionError: If embargo tracking is incorrect.
    """
    manager = ChangeControlEmbargoManager()
    manager.open_embargo(scope_keys=["scope-a", "scope-b"], reason_tag="bind", owner_request_id="tx-1")

    assert manager.find_embargoes(["scope-a"]) == ("scope-a",)
    assert set(manager.find_embargoes(["scope-a", "scope-b"])) == {"scope-a", "scope-b"}

    manager.close_embargo("tx-1")
    assert manager.find_embargoes(["scope-a", "scope-b"]) == ()


def test_orchestrator_rejects_conflicting_request() -> None:
    """
    Purpose:
        Validate orchestrator denies requests that conflict on scope keys.
    Contract:
        - A conflicting request is rejected with conflict evidence.
        - The rejected request is not added to the in-flight registry.
    Returns:
        None.
    Raises:
        AssertionError: If admission or registry behavior is incorrect.
    """
    transaction_manager = ChangeControlTransactionManager()
    conflict_manager = ChangeControlConflictManager()
    embargo_manager = ChangeControlEmbargoManager()
    orchestrator = ChangeControlOrchestrator()

    active = transaction_manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        scope_keys=["shared-scope"],
    )
    admission = orchestrator.admit_request(
        active,
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
    )
    assert admission.admitted is True

    incoming = transaction_manager.build_request(
        request_type=ChangeTransactionType.LINK,
        initiator_conduit_id="conduit-2",
        scope_keys=["shared-scope"],
    )
    rejected = orchestrator.admit_request(
        incoming,
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
    )
    assert rejected.admitted is False
    assert rejected.conflicts == (active.request_id,)
    assert transaction_manager.get_in_flight(incoming.request_id) is None


def test_orchestrator_rejects_embargoed_request() -> None:
    """
    Purpose:
        Validate orchestrator denies requests when embargoes are active.
    Contract:
        - Embargoed scope keys block admission.
        - Rejection evidence includes embargoed scope keys.
    Returns:
        None.
    Raises:
        AssertionError: If embargo admission behavior is incorrect.
    """
    transaction_manager = ChangeControlTransactionManager()
    conflict_manager = ChangeControlConflictManager()
    embargo_manager = ChangeControlEmbargoManager()
    orchestrator = ChangeControlOrchestrator()

    embargo_manager.open_embargo(scope_keys=["blocked-scope"], reason_tag="bind", owner_request_id="tx-embargo")
    incoming = transaction_manager.build_request(
        request_type=ChangeTransactionType.LINK,
        initiator_conduit_id="conduit-2",
        scope_keys=["blocked-scope"],
    )
    rejected = orchestrator.admit_request(
        incoming,
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
    )
    assert rejected.admitted is False
    assert rejected.embargoes == ("blocked-scope",)


def test_orchestrator_commit_clears_in_flight_request() -> None:
    """
    Purpose:
        Validate commit_request removes admitted requests from in-flight registry.
    Contract:
        - Admitted requests are removed from in-flight on commit.
    Returns:
        None.
    Raises:
        AssertionError: If commit does not clear the in-flight registry.
    """
    transaction_manager = ChangeControlTransactionManager()
    conflict_manager = ChangeControlConflictManager()
    embargo_manager = ChangeControlEmbargoManager()
    orchestrator = ChangeControlOrchestrator()

    request = transaction_manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        scope_keys=["scope-commit"],
    )
    admission = orchestrator.admit_request(
        request,
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
    )
    assert admission.admitted is True
    assert transaction_manager.get_in_flight(request.request_id) is not None

    orchestrator.commit_request(
        request.request_id,
        transaction_manager=transaction_manager,
        embargo_manager=embargo_manager,
    )
    assert transaction_manager.get_in_flight(request.request_id) is None
