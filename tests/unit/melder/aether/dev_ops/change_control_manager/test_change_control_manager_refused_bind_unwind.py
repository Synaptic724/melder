"""Unit coverage for the unwind of a refused late-bind window (failed_late_bind_is_undone, #330, 2026-11-23).

ChangeControlManager remembers a bind request its structural validator refuses, and its default abort hook - which
the orchestrator runs on the committing thread before it releases the request's claims - has the request's Spellbook
undo the window. Every other failure, and an in-window abort, unwinds nothing. The structural validator also refuses
a staged bind spell the binding thread already compiled broken inside its window. These tests drive a manager over a
mocked SpellSystemStates with a Spellbook double that records what it is asked to do.
"""

from types import SimpleNamespace
from typing import List, Optional, Tuple
from unittest.mock import MagicMock

import pytest

from melder.aether.aetheric_frame.dev_ops.change_control_manager.change_control_manager import ChangeControlManager
from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.staged_mutation import (
    ChangeControlStagedMutation,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError

SCOPE = "scope:spellbook:spellbook-1"


class _BookDouble:
    """
    Spellbook double for the abort hook and the structural validator.

    Purpose:
        Record each window unwind with the refusal it was handed and whether the request was still in flight
        (its claims held) when it ran, and each structural-phase run with the spells it was handed.
    """

    def __init__(self, manager: Optional[ChangeControlManager] = None) -> None:
        """Start with nothing recorded; `manager` lets an unwind check the request is still in flight."""
        self._manager = manager
        self._conjured: bool = True
        self.request_id: Optional[str] = None
        self.unwinds: List[Tuple[BaseException, bool]] = []
        self.phase_runs: List[List[object]] = []

    def _unwind_refused_bind_window(self, refusal: BaseException) -> None:
        """Record one unwind and whether the refused request still held its claims."""
        in_flight = False
        if self._manager is not None and self.request_id is not None:
            in_flight = self._manager.transaction_manager().get_in_flight(self.request_id) is not None
        self.unwinds.append((refusal, in_flight))

    def _run_post_conjure_structural_phases(self, spells: List[object]) -> None:
        """Record one structural-phase run."""
        self.phase_runs.append(list(spells))


@pytest.fixture
def manager() -> ChangeControlManager:
    """A manager over a mocked SpellSystemStates."""
    return ChangeControlManager(MagicMock())


def _resolve_to(monkeypatch: pytest.MonkeyPatch, book: Optional[_BookDouble]) -> None:
    """Make every staged mutation resolve to `book` (or to no Spellbook)."""
    monkeypatch.setattr(ChangeControlManager, "_resolve_spellbook_for_staged", lambda self, staged: book)


def _refuse_structurally(manager: ChangeControlManager, refusal: BaseException) -> None:
    """Install a structural validator that refuses every request with `refusal`."""

    def _structural(staged: ChangeControlStagedMutation) -> None:
        raise refusal

    manager.set_structural_validator(_structural)


def _admit(manager: ChangeControlManager, request_type: ChangeTransactionType) -> str:
    """Admit one request of `request_type` on the Spellbook scope and return its id."""
    request = manager.transaction_manager().build_request(
        request_type=request_type,
        initiator_conduit_id="conduit-1",
        scope_keys=[SCOPE],
    )
    admission = manager.admit_request(request)
    assert admission.admitted is True
    return request.request_id


def test_a_bind_refused_by_the_structural_validator_has_its_book_unwind_the_window_with_claims_held(
        manager: ChangeControlManager,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The refusal reaches the Book's unwind before the claims are released, then propagates unchanged."""
    book = _BookDouble(manager)
    _resolve_to(monkeypatch, book)
    refusal = SpellbookValidationError([])
    _refuse_structurally(manager, refusal)
    book.request_id = _admit(manager, ChangeTransactionType.BIND)

    with pytest.raises(SpellbookValidationError) as raised:
        manager.commit_request(book.request_id)

    assert raised.value is refusal
    assert book.unwinds == [(refusal, True)]
    assert manager.transaction_manager().get_in_flight(book.request_id) is None


def test_any_structural_refusal_of_a_bind_unwinds_not_only_a_validation_error(
        manager: ChangeControlManager,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A phase that fails with another exception is a refusal too: what the bind registered is undone."""
    book = _BookDouble(manager)
    _resolve_to(monkeypatch, book)
    refusal = KeyError("phase failure")
    _refuse_structurally(manager, refusal)
    book.request_id = _admit(manager, ChangeTransactionType.BIND)

    with pytest.raises(KeyError):
        manager.commit_request(book.request_id)

    assert book.unwinds == [(refusal, True)]


def test_a_bind_refused_by_the_commit_validator_unwinds_nothing(
        manager: ChangeControlManager,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Only the structural validator's refusal of a bind is remembered; a later validator's failure is not."""
    book = _BookDouble(manager)
    _resolve_to(monkeypatch, book)
    manager.set_structural_validator(lambda staged: None)

    def _validator(staged: ChangeControlStagedMutation) -> None:
        raise RuntimeError("commit validator refused")

    manager.set_commit_validator(_validator)
    request_id = _admit(manager, ChangeTransactionType.BIND)

    with pytest.raises(RuntimeError, match="commit validator refused"):
        manager.commit_request(request_id)

    assert book.unwinds == []


def test_a_refused_notch_unwinds_nothing(manager: ChangeControlManager, monkeypatch: pytest.MonkeyPatch) -> None:
    """A notch is undone inside its own window; its structural refusal does not reach the bind unwind."""
    book = _BookDouble(manager)
    _resolve_to(monkeypatch, book)
    _refuse_structurally(manager, SpellbookValidationError([]))
    request_id = _admit(manager, ChangeTransactionType.NOTCH)

    with pytest.raises(SpellbookValidationError):
        manager.commit_request(request_id)

    assert book.unwinds == []


def test_an_aborted_bind_window_unwinds_nothing(manager: ChangeControlManager, monkeypatch: pytest.MonkeyPatch) -> None:
    """An in-window abort keeps today's contract: the abort hook runs and its spells stay."""
    book = _BookDouble(manager)
    _resolve_to(monkeypatch, book)
    request_id = _admit(manager, ChangeTransactionType.BIND)

    manager.abort_request(request_id)

    assert book.unwinds == []
    assert manager.transaction_manager().get_in_flight(request_id) is None


def test_each_refused_bind_unwinds_once_and_leaves_no_record_behind(
        manager: ChangeControlManager,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two refused binds unwind once each, with their own refusals; a later in-window abort finds no record."""
    book = _BookDouble(manager)
    _resolve_to(monkeypatch, book)
    refusals = [RuntimeError("first refusal"), RuntimeError("second refusal")]
    for refusal in refusals:
        _refuse_structurally(manager, refusal)
        book.request_id = _admit(manager, ChangeTransactionType.BIND)
        with pytest.raises(RuntimeError):
            manager.commit_request(book.request_id)
    manager.set_structural_validator(lambda staged: None)
    aborted_id = _admit(manager, ChangeTransactionType.BIND)

    manager.abort_request(aborted_id)

    assert [refusal for refusal, _held in book.unwinds] == refusals


def test_a_refused_bind_whose_book_cannot_be_resolved_says_so_on_the_refusal(
        manager: ChangeControlManager,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With no Spellbook to unwind, the refusal still propagates and carries a note that nothing was undone."""
    _resolve_to(monkeypatch, None)
    refusal = RuntimeError("refused")
    _refuse_structurally(manager, refusal)
    request_id = _admit(manager, ChangeTransactionType.BIND)

    with pytest.raises(RuntimeError) as raised:
        manager.commit_request(request_id)

    assert raised.value is refusal
    assert any("could not be undone" in note for note in raised.value.__notes__)


def _staged(request_type: ChangeTransactionType) -> ChangeControlStagedMutation:
    """A staged mutation of `request_type` with one binding key, as a late bind of one spell stages it."""
    return ChangeControlStagedMutation.from_request(
        request_id=f"req-{request_type.value}",
        request_type=request_type,
        initiator_conduit_id="conduit-1",
        spellbook_id="spellbook-1",
        conduit_ids=("conduit-1",),
        scope_keys=(),
        binding_keys=(("frame", "binding"),),
        contract_keys=(),
        metadata=None,
    )


def _spell(name: str, *, compiled: bool, broken: bool) -> SimpleNamespace:
    """A staged spell stand-in: a Phase 4 result when compiled, and whether that result is broken."""
    return SimpleNamespace(
        name=name,
        validation_result_phase4=object() if compiled else None,
        is_broken=broken,
        _compiler_artifact=SimpleNamespace(_root_blueprint_phase5=object() if compiled else None),
    )


def _stage_spells(monkeypatch: pytest.MonkeyPatch, book: _BookDouble, spells: List[SimpleNamespace]) -> None:
    """Make the staged binding keys resolve to `spells` in `book`."""
    _resolve_to(monkeypatch, book)
    monkeypatch.setattr(
        ChangeControlManager,
        "_resolve_spells_for_binding_keys",
        lambda self, spellbook, binding_keys: list(spells) if spellbook is book else [],
    )


def test_a_staged_bind_spell_already_compiled_broken_is_refused_after_the_uncompiled_ones_run(
        manager: ChangeControlManager,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The binding thread compiled it broken inside its window: the commit refuses it, naming only that spell."""
    book = _BookDouble()
    pending = _spell("pending", compiled=False, broken=False)
    broken = _spell("broken", compiled=True, broken=True)
    valid = _spell("valid", compiled=True, broken=False)
    _stage_spells(monkeypatch, book, [pending, broken, valid])

    with pytest.raises(SpellbookValidationError) as raised:
        manager._default_structural_validator(_staged(ChangeTransactionType.BIND))

    assert raised.value.broken_spells == [broken]
    assert book.phase_runs == [[pending]]


def test_a_staged_bind_spell_already_compiled_valid_commits(
        manager: ChangeControlManager,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A spell the binding thread compiled valid is neither recompiled nor refused."""
    book = _BookDouble()
    _stage_spells(monkeypatch, book, [_spell("valid", compiled=True, broken=False)])

    manager._default_structural_validator(_staged(ChangeTransactionType.BIND))

    assert book.phase_runs == []


def test_a_notch_member_already_compiled_broken_is_not_refused_by_the_bind_check(
        manager: ChangeControlManager,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A notch checks its incoming version inside its own window; the bind-only check leaves notch members alone."""
    book = _BookDouble()
    _stage_spells(monkeypatch, book, [_spell("member", compiled=True, broken=True)])

    manager._default_structural_validator(_staged(ChangeTransactionType.NOTCH))

    assert book.phase_runs == []
