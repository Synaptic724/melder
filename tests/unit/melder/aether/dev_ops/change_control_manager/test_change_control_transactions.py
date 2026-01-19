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
        scope_keys=["scope:spellbook:spellbook-1"],
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
    assert request.scope_keys == ("scope:spellbook:spellbook-1",)
    assert request.scope_hashes == ("scope-hash",)
    assert request.binding_keys == (("frame", "__default__"),)
    assert request.contract_keys == (("provider", "borrower", "read"),)
    assert request.metadata["note"] == "unit-test"


def test_transaction_manager_build_request_normalizes_scope_hashes() -> None:
    """
    Purpose:
        Validate scope hashes are derived when only scope keys are provided.
    Contract:
        - scope_hashes are populated with SHA256 values.
    Returns:
        None.
    Raises:
        AssertionError: If scope_hashes are missing or mismatched.
    """
    manager = ChangeControlTransactionManager()
    scope_key = "scope:spellbook:spellbook-1"
    request = manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        scope_keys=[scope_key],
    )

    expected = hashlib.sha256(scope_key.encode("utf-8")).hexdigest()
    assert request.scope_hashes == (expected,)


def test_transaction_manager_scope_key_helpers() -> None:
    """
    Purpose:
        Validate scope key helper builders.
    Contract:
        - Builders return normalized scope key strings.
        - Empty inputs raise ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If helper outputs are incorrect.
    """
    manager = ChangeControlTransactionManager()
    assert manager.make_scope_key_spellbook("sb-1") == "scope:spellbook:sb-1"
    assert manager.make_scope_key_conduit("con-1") == "scope:conduit:con-1"
    assert manager.make_scope_key_cluster("cluster-1") == "scope:cluster:cluster-1"
    assert manager.make_scope_key_binding("frame", "__default__") == "binding:frame:__default__"
    assert (
        manager.make_scope_key_contract("frame", "__default__", "peer-1")
        == "contract:frame:__default__:peer-1"
    )

    with pytest.raises(ValueError):
        manager.make_scope_key_conduit("")


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


def test_embargo_manager_advisory_hints() -> None:
    """
    Purpose:
        Validate advisory hints surface embargo records for scopes.
    Contract:
        - Hints return embargo records without mutating state.
    Returns:
        None.
    Raises:
        AssertionError: If advisory hints are incorrect.
    """
    manager = ChangeControlEmbargoManager()
    manager.open_embargo(scope_keys=["scope-a"], reason_tag="bind", owner_request_id="tx-1")

    hints = manager.list_advisory_hints(["scope-a"])
    assert len(hints) == 1
    assert hints[0].scope_key == "scope-a"
    assert hints[0].reason_tag == "bind"


def test_embargo_manager_collect_scope_keys_includes_derived_keys() -> None:
    """
    Purpose:
        Validate derived scope keys are included when collecting embargo scopes.
    Contract:
        - Includes request.scope_keys plus derived spellbook/conduit/binding/contract keys.
    Returns:
        None.
    Raises:
        AssertionError: If derived scope keys are missing.
    """
    manager = ChangeControlEmbargoManager()
    transaction_manager = ChangeControlTransactionManager()
    request = transaction_manager.build_request(
        request_type=ChangeTransactionType.LINK,
        initiator_conduit_id="conduit-1",
        spellbook_id="spellbook-1",
        conduit_ids=["conduit-1", "conduit-2"],
        scope_keys=["scope:spellbook:spellbook-1"],
        binding_keys=[("frame", "__default__")],
        contract_keys=[("frame", "__default__", "conduit-2")],
    )

    scope_keys = manager.collect_scope_keys(request)
    assert "scope:spellbook:spellbook-1" in scope_keys
    assert "scope:conduit:conduit-1" in scope_keys
    assert "scope:conduit:conduit-2" in scope_keys
    assert "binding:frame:__default__" in scope_keys
    assert "contract:frame:__default__:conduit-2" in scope_keys


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


def test_orchestrator_rejects_request_with_derived_embargo() -> None:
    """
    Purpose:
        Validate embargo checks consider derived scope keys.
    Contract:
        - Embargoes tied to binding scopes reject admission even when the
          request omits scope_keys.
    Returns:
        None.
    Raises:
        AssertionError: If derived embargo scope is ignored.
    """
    transaction_manager = ChangeControlTransactionManager()
    conflict_manager = ChangeControlConflictManager()
    embargo_manager = ChangeControlEmbargoManager()
    orchestrator = ChangeControlOrchestrator()

    embargo_manager.open_embargo(
        scope_keys=["binding:frame:__default__"],
        reason_tag="bind",
        owner_request_id="tx-embargo",
    )
    incoming = transaction_manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        binding_keys=[("frame", "__default__")],
    )
    rejected = orchestrator.admit_request(
        incoming,
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
    )
    assert rejected.admitted is False
    assert rejected.embargoes == ("binding:frame:__default__",)


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


def test_orchestrator_applies_and_releases_implicit_embargoes() -> None:
    """
    Purpose:
        Validate implicit embargoes are opened on admission and released on commit.
    Contract:
        - Admission opens embargoes for derived scope keys.
        - Commit releases embargoes for the request.
    Returns:
        None.
    Raises:
        AssertionError: If embargo lifecycle behavior is incorrect.
    """
    transaction_manager = ChangeControlTransactionManager()
    conflict_manager = ChangeControlConflictManager()
    embargo_manager = ChangeControlEmbargoManager()
    orchestrator = ChangeControlOrchestrator()

    request = transaction_manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        spellbook_id="spellbook-1",
        conduit_ids=["conduit-1"],
        binding_keys=[("frame", "__default__")],
    )
    admission = orchestrator.admit_request(
        request,
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
    )
    assert admission.admitted is True

    embargo_scopes = embargo_manager.collect_scope_keys(request)
    assert embargo_scopes
    assert set(embargo_manager.find_embargoes(embargo_scopes)) == set(embargo_scopes)

    orchestrator.commit_request(
        request.request_id,
        transaction_manager=transaction_manager,
        embargo_manager=embargo_manager,
    )
    assert embargo_manager.find_embargoes(embargo_scopes) == ()


def test_orchestrator_staging_registry_tracks_requests() -> None:
    """
    Purpose:
        Validate staged mutation records are created and cleared.
    Contract:
        - Admission creates a staged record for the request.
        - Commit removes the staged record.
    Returns:
        None.
    Raises:
        AssertionError: If staging registry tracking is incorrect.
    """
    transaction_manager = ChangeControlTransactionManager()
    conflict_manager = ChangeControlConflictManager()
    embargo_manager = ChangeControlEmbargoManager()
    orchestrator = ChangeControlOrchestrator()

    request = transaction_manager.build_request(
        request_type=ChangeTransactionType.LINK,
        initiator_conduit_id="conduit-1",
        conduit_ids=["conduit-1", "conduit-2"],
        scope_keys=["scope:conduit:conduit-1"],
        binding_keys=[("frame", "__default__")],
        contract_keys=[("frame", "__default__", "conduit-2")],
    )
    admission = orchestrator.admit_request(
        request,
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
    )
    assert admission.admitted is True
    staged = orchestrator.get_staged(request.request_id)
    assert staged is not None
    assert staged.request_id == request.request_id
    assert staged.conduit_ids == ("conduit-1", "conduit-2")
    assert staged.binding_keys == (("frame", "__default__"),)
    assert staged.contract_keys == (("frame", "__default__", "conduit-2"),)

    orchestrator.commit_request(
        request.request_id,
        transaction_manager=transaction_manager,
        embargo_manager=embargo_manager,
    )
    assert orchestrator.get_staged(request.request_id) is None


def test_orchestrator_abort_clears_in_flight_and_staged() -> None:
    """
    Purpose:
        Validate abort path clears in-flight and staged records.
    Contract:
        - Aborting removes in-flight and staged entries for the request.
    Returns:
        None.
    Raises:
        AssertionError: If abort does not clear state.
    """
    transaction_manager = ChangeControlTransactionManager()
    conflict_manager = ChangeControlConflictManager()
    embargo_manager = ChangeControlEmbargoManager()
    orchestrator = ChangeControlOrchestrator()

    request = transaction_manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        scope_keys=["scope:spellbook:spellbook-1"],
    )
    admission = orchestrator.admit_request(
        request,
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
    )
    assert admission.admitted is True
    assert transaction_manager.get_in_flight(request.request_id) is not None
    assert orchestrator.get_staged(request.request_id) is not None

    orchestrator.abort_request(
        request.request_id,
        transaction_manager=transaction_manager,
        embargo_manager=embargo_manager,
    )
    assert transaction_manager.get_in_flight(request.request_id) is None
    assert orchestrator.get_staged(request.request_id) is None


def test_orchestrator_commit_hook_invoked() -> None:
    """
    Purpose:
        Validate commit hooks are invoked for staged requests.
    Contract:
        - Commit hook receives the staged mutation record.
    Returns:
        None.
    Raises:
        AssertionError: If commit hook is not called.
    """
    transaction_manager = ChangeControlTransactionManager()
    conflict_manager = ChangeControlConflictManager()
    embargo_manager = ChangeControlEmbargoManager()
    orchestrator = ChangeControlOrchestrator()
    called = []

    def _commit_hook(staged) -> None:
        called.append(staged.request_id)

    orchestrator.set_commit_hook(_commit_hook)
    request = transaction_manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        scope_keys=["scope:spellbook:spellbook-1"],
    )
    admission = orchestrator.admit_request(
        request,
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
    )
    assert admission.admitted is True

    orchestrator.commit_request(
        request.request_id,
        transaction_manager=transaction_manager,
        embargo_manager=embargo_manager,
    )
    assert called == [request.request_id]


def test_orchestrator_abort_hook_invoked() -> None:
    """
    Purpose:
        Validate abort hooks are invoked for staged requests.
    Contract:
        - Abort hook receives the staged mutation record.
    Returns:
        None.
    Raises:
        AssertionError: If abort hook is not called.
    """
    transaction_manager = ChangeControlTransactionManager()
    conflict_manager = ChangeControlConflictManager()
    embargo_manager = ChangeControlEmbargoManager()
    orchestrator = ChangeControlOrchestrator()
    called = []

    def _abort_hook(staged) -> None:
        called.append(staged.request_id)

    orchestrator.set_abort_hook(_abort_hook)
    request = transaction_manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        scope_keys=["scope:spellbook:spellbook-1"],
    )
    admission = orchestrator.admit_request(
        request,
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
    )
    assert admission.admitted is True

    orchestrator.abort_request(
        request.request_id,
        transaction_manager=transaction_manager,
        embargo_manager=embargo_manager,
    )
    assert called == [request.request_id]


def test_orchestrator_commit_validator_failure_aborts() -> None:
    """
    Purpose:
        Validate commit validation failures abort and clean up state.
    Contract:
        - Validator error removes in-flight and staged records.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not occur on validation failure.
    """
    transaction_manager = ChangeControlTransactionManager()
    conflict_manager = ChangeControlConflictManager()
    embargo_manager = ChangeControlEmbargoManager()
    orchestrator = ChangeControlOrchestrator()

    def _validator(staged) -> None:
        raise RuntimeError("validation failed")

    orchestrator.set_commit_validator(_validator)
    request = transaction_manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        scope_keys=["scope:spellbook:spellbook-1"],
    )
    admission = orchestrator.admit_request(
        request,
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
    )
    assert admission.admitted is True

    try:
        orchestrator.commit_request(
            request.request_id,
            transaction_manager=transaction_manager,
            embargo_manager=embargo_manager,
        )
    except RuntimeError:
        pass

    assert transaction_manager.get_in_flight(request.request_id) is None
    assert orchestrator.get_staged(request.request_id) is None
import hashlib
import pytest
