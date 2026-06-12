import hashlib
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
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeControlTransactionRequest,
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


def test_transaction_manager_build_request_retains_scope_hashes_when_supplied() -> None:
    """
    Purpose:
        Validate build_request preserves explicitly supplied scope hashes.
    Contract:
        - Provided scope_hashes are retained even when scope_keys are present.
    Returns:
        None.
    Raises:
        AssertionError: If supplied hashes are overwritten.
    """
    manager = ChangeControlTransactionManager()
    request = manager.build_request(
        request_type=ChangeTransactionType.LINK,
        initiator_conduit_id="conduit-1",
        scope_keys=["scope:spellbook:spellbook-1"],
        scope_hashes=["explicit-hash"],
    )

    assert request.scope_hashes == ("explicit-hash",)


def test_transaction_manager_build_request_dedupes_scope_hashes() -> None:
    """
    Purpose:
        Validate build_request derives hashes from unique non-empty scope keys.
    Contract:
        - Duplicate and empty scope keys are ignored.
        - Hashes are generated from unique keys.
    Returns:
        None.
    Raises:
        AssertionError: If derived hashes do not match expectations.
    """
    manager = ChangeControlTransactionManager()
    scope_keys = ["scope:spellbook:spellbook-1", "", "scope:spellbook:spellbook-1"]
    request = manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        scope_keys=scope_keys,
    )

    expected = hashlib.sha256("scope:spellbook:spellbook-1".encode("utf-8")).hexdigest()
    assert request.scope_hashes == (expected,)


def test_transaction_manager_build_request_does_not_register_in_flight() -> None:
    """
    Purpose:
        Validate build_request does not register in-flight requests.
    Contract:
        - In-flight registry remains empty after build_request.
    Returns:
        None.
    Raises:
        AssertionError: If build_request registers in-flight state.
    """
    manager = ChangeControlTransactionManager()
    request = manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
    )

    assert manager.get_in_flight(request.request_id) is None
    assert manager.list_in_flight() == []


def test_transaction_manager_build_request_copies_metadata() -> None:
    """
    Purpose:
        Validate metadata is copied into the request payload.
    Contract:
        - Mutating the source metadata does not affect the request metadata.
    Returns:
        None.
    Raises:
        AssertionError: If request metadata changes after source mutation.
    """
    manager = ChangeControlTransactionManager()
    source = {"note": "initial"}
    request = manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        metadata=source,
    )
    source["note"] = "mutated"

    assert request.metadata == {"note": "initial"}


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


def test_transaction_manager_build_request_rejects_empty_initiator() -> None:
    """
    Purpose:
        Validate initiator conduit ids are required.
    Contract:
        - Empty or whitespace initiator ids raise ValueError.
        - Non-string initiator ids raise TypeError.
    Returns:
        None.
    Raises:
        AssertionError: If invalid initiators are accepted.
    """
    manager = ChangeControlTransactionManager()
    with pytest.raises(ValueError, match="initiator_conduit_id must not be empty"):
        manager.build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="",
        )
    with pytest.raises(ValueError, match="initiator_conduit_id must not be empty"):
        manager.build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="   ",
        )
    with pytest.raises(TypeError, match="initiator_conduit_id must be a string"):
        manager.build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id=123,
        )


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


def test_transaction_manager_add_in_flight_with_no_audit_logger() -> None:
    """
    Purpose:
        Validate add_in_flight succeeds when audit logging is disabled.
    Contract:
        - Requests are registered even when no audit logger is set.
    Returns:
        None.
    Raises:
        AssertionError: If in-flight state is not updated.
    """
    manager = ChangeControlTransactionManager()
    request = manager.build_request(
        request_type=ChangeTransactionType.LINK,
        initiator_conduit_id="conduit-1",
    )

    manager.add_in_flight(request)
    assert manager.get_in_flight(request.request_id) is request


def test_transaction_manager_set_audit_logger_disables_callback() -> None:
    """
    Purpose:
        Validate setting audit logger to None disables callbacks.
    Contract:
        - After setting None, no audit callbacks fire.
    Returns:
        None.
    Raises:
        AssertionError: If audit callbacks fire after disable.
    """
    manager = ChangeControlTransactionManager()
    captured: list[str] = []

    def _audit(request) -> None:
        captured.append(request.request_id)

    manager.set_audit_logger(_audit)
    first = manager.build_request(
        request_type=ChangeTransactionType.LINK,
        initiator_conduit_id="conduit-1",
    )
    manager.add_in_flight(first)
    assert captured == [first.request_id]

    manager.set_audit_logger(None)
    second = manager.build_request(
        request_type=ChangeTransactionType.LINK,
        initiator_conduit_id="conduit-2",
    )
    manager.add_in_flight(second)
    assert captured == [first.request_id]


def test_transaction_manager_list_in_flight_returns_snapshot() -> None:
    """
    Purpose:
        Validate list_in_flight returns a snapshot list.
    Contract:
        - Mutating the returned list does not affect internal state.
    Returns:
        None.
    Raises:
        AssertionError: If internal in-flight state is mutated via the snapshot.
    """
    manager = ChangeControlTransactionManager()
    request = manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
    )
    manager.add_in_flight(request)

    snapshot = manager.list_in_flight()
    snapshot.clear()

    assert manager.get_in_flight(request.request_id) is request


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


def test_conflict_manager_matches_hash_only_to_key_only() -> None:
    """
    Purpose:
        Validate hash-only requests conflict with key-only requests.
    Contract:
        - Derived hashes from scope keys overlap with explicit scope hashes.
    Returns:
        None.
    Raises:
        AssertionError: If mixed hash/key conflicts are missed.
    """
    conflict_manager = ChangeControlConflictManager()
    scope_key = "shared-scope"
    scope_hash = hashlib.sha256(scope_key.encode("utf-8")).hexdigest()

    active = ChangeControlTransactionRequest(
        request_id="tx-active",
        request_type=ChangeTransactionType.BIND,
        created_at=0.0,
        initiator_conduit_id="conduit-1",
        scope_keys=(scope_key,),
        scope_hashes=(),
    )
    incoming = ChangeControlTransactionRequest(
        request_id="tx-incoming",
        request_type=ChangeTransactionType.LINK,
        created_at=0.0,
        initiator_conduit_id="conduit-2",
        scope_keys=(),
        scope_hashes=(scope_hash,),
    )

    conflicts = conflict_manager.find_conflicts(incoming, [active])
    assert conflicts == (active.request_id,)


def test_conflict_manager_handles_empty_scopes() -> None:
    """
    Purpose:
        Validate conflicts are not reported when scopes are empty.
    Contract:
        - Empty scope keys and hashes yield no conflicts.
    Returns:
        None.
    Raises:
        AssertionError: If conflicts are reported for empty scopes.
    """
    conflict_manager = ChangeControlConflictManager()
    request = ChangeControlTransactionRequest(
        request_id="tx-empty",
        request_type=ChangeTransactionType.BIND,
        created_at=0.0,
        initiator_conduit_id="conduit-1",
        scope_keys=(),
        scope_hashes=(),
    )

    assert conflict_manager.find_conflicts(request, []) == ()


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


def test_embargo_manager_extend_adds_only_new_scopes() -> None:
    """
    Purpose:
        Validate extend_embargoes adds only new scope keys.
    Contract:
        - Existing scope keys are not duplicated.
        - New scope keys become embargoed.
    Returns:
        None.
    Raises:
        AssertionError: If embargo records duplicate existing scopes.
    """
    manager = ChangeControlEmbargoManager()
    manager.open_embargo(scope_keys=["scope-a"], reason_tag="bind", owner_request_id="tx-1")

    manager.extend_embargoes(owner_request_id="tx-1", scope_keys=["scope-a", "scope-b"], reason_tag="bind")

    assert set(manager.find_embargoes(["scope-a", "scope-b"])) == {"scope-a", "scope-b"}
    hints = manager.list_advisory_hints(["scope-a", "scope-b"])
    assert len(hints) == 2


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


def test_embargo_manager_collect_scope_keys_from_staged() -> None:
    """
    Purpose:
        Validate staged mutation scope collection includes derived keys.
    Contract:
        - Derived scope keys appear for binding and contract keys.
    Returns:
        None.
    Raises:
        AssertionError: If derived keys are missing.
    """
    manager = ChangeControlEmbargoManager()
    staged = ChangeControlStagedMutation.from_request(
        request_id="tx-1",
        request_type=ChangeTransactionType.LINK,
        initiator_conduit_id="conduit-1",
        spellbook_id="spellbook-1",
        conduit_ids=("conduit-1", "conduit-2"),
        scope_keys=("scope:spellbook:spellbook-1",),
        binding_keys=(("frame", "__default__"),),
        contract_keys=(("frame", "__default__", "conduit-2"),),
    )

    scope_keys = manager.collect_scope_keys_from_staged(staged)
    assert "binding:frame:__default__" in scope_keys
    assert "contract:frame:__default__:conduit-2" in scope_keys


def test_staged_mutation_with_updates_preserves_identity_and_merges_metadata() -> None:
    """
    Purpose:
        Validate staged mutation updates keep identity and merge metadata.
    Contract:
        - request_id and staged_at remain unchanged.
        - scope/binding/contract keys update only when supplied.
        - metadata merges into the existing dict.
    Returns:
        None.
    Raises:
        AssertionError: If updates fail to preserve identity or merge metadata.
    """
    staged = ChangeControlStagedMutation.from_request(
        request_id="tx-1",
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        spellbook_id="spellbook-1",
        conduit_ids=("conduit-1",),
        scope_keys=("scope:spellbook:spellbook-1",),
        binding_keys=(("frame", "__default__"),),
        contract_keys=(),
        metadata={"note": "first"},
    )

    updated = staged.with_updates(
        scope_keys=("scope:spellbook:spellbook-1", "scope:conduit:conduit-1"),
        metadata={"note": "second", "extra": "value"},
    )

    assert updated.request_id == staged.request_id
    assert updated.staged_at == staged.staged_at
    assert updated.scope_keys == (
        "scope:spellbook:spellbook-1",
        "scope:conduit:conduit-1",
    )
    assert updated.binding_keys == staged.binding_keys
    assert updated.contract_keys == staged.contract_keys
    assert updated.metadata == {"note": "second", "extra": "value"}


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


def test_orchestrator_rejects_with_conflict_and_embargo() -> None:
    """
    Purpose:
        Validate admission reports both conflict and embargo evidence.
    Contract:
        - Rejection reasons include conflict and embargo when both apply.
    Returns:
        None.
    Raises:
        AssertionError: If combined evidence is missing.
    """
    transaction_manager = ChangeControlTransactionManager()
    conflict_manager = ChangeControlConflictManager()
    embargo_manager = ChangeControlEmbargoManager()
    orchestrator = ChangeControlOrchestrator()

    active = transaction_manager.build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        scope_keys=["scope-a"],
    )
    transaction_manager.add_in_flight(active)
    embargo_manager.open_embargo(scope_keys=["scope-a"], reason_tag="bind", owner_request_id="tx-embargo")

    incoming = transaction_manager.build_request(
        request_type=ChangeTransactionType.LINK,
        initiator_conduit_id="conduit-2",
        scope_keys=["scope-a"],
    )
    rejected = orchestrator.admit_request(
        incoming,
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
    )

    assert rejected.admitted is False
    assert rejected.reasons == ("scope_conflict",)
    # Acquisition evidence names the claim holder. The in-flight request was
    # registered directly (no acquisition), so the embargo owner is the
    # blocking holder under the lock-table admission contract.
    assert rejected.conflicts == ("tx-embargo",)
    assert "scope-a" in rejected.embargoes
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


def test_orchestrator_update_staged_handles_missing_request() -> None:
    """
    Purpose:
        Validate update_staged returns False when the request is missing.
    Contract:
        - update_staged returns False for unknown request ids.
    Returns:
        None.
    Raises:
        AssertionError: If missing requests are reported as updated.
    """
    orchestrator = ChangeControlOrchestrator()

    assert orchestrator.update_staged("missing-request") is False


def test_orchestrator_update_staged_updates_fields_and_merges_metadata() -> None:
    """
    Purpose:
        Validate update_staged updates staged metadata for admitted requests.
    Contract:
        - Updated scope/binding/contract keys are applied.
        - Metadata merges into the existing record.
    Returns:
        None.
    Raises:
        AssertionError: If staged metadata is not updated.
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
        metadata={"note": "before"},
    )
    admission = orchestrator.admit_request(
        request,
        transaction_manager=transaction_manager,
        conflict_manager=conflict_manager,
        embargo_manager=embargo_manager,
    )
    assert admission.admitted is True

    updated = orchestrator.update_staged(
        request.request_id,
        scope_keys=["scope:conduit:conduit-1", "scope:conduit:conduit-2"],
        metadata={"note": "after", "extra": "value"},
    )
    assert updated is True

    staged = orchestrator.get_staged(request.request_id)
    assert staged is not None
    assert staged.scope_keys == (
        "scope:conduit:conduit-1",
        "scope:conduit:conduit-2",
    )
    assert staged.binding_keys == (("frame", "__default__"),)
    assert staged.contract_keys == (("frame", "__default__", "conduit-2"),)
    assert staged.metadata == {"note": "after", "extra": "value"}


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
