"""
Component tests: index-link emissions and contract inspections against concurrent link, sever and member changes
(cross_object_lock_gaps, 0.2.8231).

The frame mediator orders LINK/UNLINK against NOTCH and the index moves (all claim the participant conduits
EXCLUSIVE), but the owner-side emissions that walk the ward's contract registry run after the owner's transaction
has ended (notch, index moves, bind_inactive) or with no transaction at all (cleanup_spell). A link admitted in that
window resized the registry mid-walk: the verb raised "dictionary changed size during iteration" after its change had
committed, and the borrowers not yet visited were left out of step. A borrower's contract inspection likewise walked
the owner's detail map while the owner wrote it. The emissions now walk under the ward's own lock and the
inspections under the contract's own lock, so the other side waits instead. The contract listing also stopped taking
the conduit lock under the ward lock, which deadlocked it with link and sever.

Each test parks one thread inside its walk (after a real read; nothing is skipped) and drives the other side through
a public verb from another thread.
"""

import threading
from typing import Callable, Dict, Iterator, List, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_ward.contract.contract import Contract
from melder.aether.conduit.conduit_ward.contract.details import Detail, IndexDetail
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook

from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


class _HeadA:
    """Active head of the owner's linked index."""


class _MemberB:
    """Second member of the owner's linked index."""


class _MemberC:
    """Member staged onto the linked index while a borrower inspects its contracts."""


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_lock_gaps() -> Iterator[None]:
    """
    Purpose:
        Give each test a clean Aether singleton and frame registry.
    Returns:
        Iterator[None]: Control returns to the test between the two resets.
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


def _make_book() -> Spellbook:
    """
    Purpose:
        A Spellbook in the dynamic posture the link and index verbs require.
    Returns:
        Spellbook: The new Book.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=configuration)


def _link_index(borrower: Conduit, owner: Conduit, index) -> None:
    """
    Purpose:
        Contract the owner's index to the borrower through an index link.
    """
    with borrower.transaction("link", conduits=[borrower, owner]):
        assert borrower.add_index_to_contract(index=index, conduit=owner, permissions="create")


def _conduit(name: str) -> Conduit:
    """
    Purpose:
        Conjure an empty dynamic root.
    """
    return _make_book().conjure(dynamic=True, name=name)


def _run_with_other_side_mid_walk(
        park_here: Callable[[Callable[[], None]], None],
        walker: Callable[[], object],
        other_side: Callable[[], None],
) -> Tuple[Dict[str, object], bool]:
    """
    Purpose:
        Run `walker` on a thread that parks inside its walk (through `park_here`), start `other_side` on another
        thread, record whether `other_side` finished while the walker was parked, release the walker and join both.
    Returns:
        Tuple[Dict[str, object], bool]: The walker's "result" or "error", and whether `other_side` completed while
            the walker was still parked.
    """
    parked, release, finished = threading.Event(), threading.Event(), threading.Event()
    outcome: Dict[str, object] = {}

    def park() -> None:
        if threading.current_thread() is walker_thread and not parked.is_set():
            parked.set()
            assert release.wait(timeout=30)

    def walk() -> None:
        try:
            outcome["result"] = walker()
        except Exception as exc:
            outcome["error"] = exc

    def other() -> None:
        other_side()
        finished.set()

    park_here(park)
    # Daemon threads, so a regression that deadlocks the two sides fails the test instead of hanging the run.
    walker_thread = threading.Thread(target=walk, daemon=True)
    other_thread = threading.Thread(target=other, daemon=True)
    walker_thread.start()
    try:
        assert parked.wait(timeout=30), "the walker never reached its walk"
        other_thread.start()
        # The fixed walk holds the lock the other side's writer takes, so the other side cannot finish while the
        # walker is parked; before the fix it finished at once and the walker then failed.
        finished_while_parked = finished.wait(timeout=0.5)
    finally:
        release.set()
        walker_thread.join(timeout=10)
        if other_thread.ident is not None:
            other_thread.join(timeout=10)
    assert not walker_thread.is_alive() and not other_thread.is_alive()
    assert finished.is_set()
    return outcome, finished_while_parked


def test_cleanup_spell_destroy_emission_holds_off_a_concurrent_link_and_drops_every_subscription(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    cleanup_spell of an index's sole member while owner.link(C) is admitted: the link waits for the destroy
    emission, cleanup_spell returns normally, and the index-linked borrower drops the dead index.
    """
    owner_book = _make_book()
    id_a = owner_book.bind(spell=_HeadA, existence=Existence.unique, permissions="create", binding_name="a")
    owner = owner_book.conjure(dynamic=True, name="owner")
    first, borrower, newcomer = _conduit("first"), _conduit("borrower"), _conduit("newcomer")
    owner.link(first)
    owner.link(borrower)
    index = owner_book.find_spell_by_spell_id(id_a).spell_index
    index_id = index.id
    _link_index(borrower, owner, index)
    first_contract = owner._conduit_ward._find_contract(first)
    real_get_index_detail_map = Contract._get_index_detail_map

    def park_here(park: Callable[[], None]) -> None:
        def parking(self: Contract, ward) -> Dict[str, IndexDetail]:
            answer = real_get_index_detail_map(self, ward)
            if self is first_contract:
                park()
            return answer

        monkeypatch.setattr(Contract, "_get_index_detail_map", parking)

    outcome, link_finished_mid_walk = _run_with_other_side_mid_walk(
        park_here,
        lambda: owner.cleanup_spell(spell=owner_book.find_spell_by_spell_id(id_a)),
        lambda: owner.link(newcomer),
    )

    assert "error" not in outcome, outcome.get("error")
    assert link_finished_mid_walk is False
    assert owner_book.find_spell_by_spell_id(id_a) is None
    assert index_id not in borrower._spellbook._contracted_indexes
    contract = borrower._conduit_ward._find_contract_by_id(owner._id)
    assert contract._check_index_exists(owner._conduit_ward, index_id) is False
    assert owner._conduit_ward._find_contract(newcomer) is not None


def test_notch_emission_holds_off_a_concurrent_link_and_every_borrower_follows_the_new_head(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    notch_spell on an index linked to two borrowers while owner.link(C) is admitted after the NOTCH transaction
    ended: the link waits for the emission, notch_spell returns normally, and both borrowers hold the new head.
    """
    owner_book = _make_book()
    id_a = owner_book.bind(spell=_HeadA, existence=Existence.unique, permissions="create", binding_name="a")
    owner = owner_book.conjure(dynamic=True, name="owner")
    b1, b2, newcomer = _conduit("b1"), _conduit("b2"), _conduit("newcomer")
    owner.link(b1)
    owner.link(b2)
    index = owner_book.find_spell_by_spell_id(id_a).spell_index
    id_b = owner.bind_inactive(spell=_MemberB, spell_index=index, existence=Existence.unique,
                               permissions="create", binding_name="b")
    spell_b = owner_book._get_owned_spell(id_b)
    _link_index(b1, owner, index)
    _link_index(b2, owner, index)
    real_update_selected = IndexDetail.update_selected

    def park_here(park: Callable[[], None]) -> None:
        def parking(self: IndexDetail, spell_id: str) -> None:
            answer = real_update_selected(self, spell_id)
            park()
            return answer

        monkeypatch.setattr(IndexDetail, "update_selected", parking)

    outcome, link_finished_mid_walk = _run_with_other_side_mid_walk(
        park_here,
        lambda: owner.notch_spell(spell_index=index, spell=spell_b),
        lambda: owner.link(newcomer),
    )

    assert "error" not in outcome, outcome.get("error")
    assert link_finished_mid_walk is False
    for borrower in (b1, b2):
        active: List[str] = list(borrower._spellbook._contracted_spells_by_id.get(owner._id, {}))
        assert id_b in active
        assert id_a not in active


def test_contract_inspection_holds_off_a_concurrent_member_stage(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    A borrower's get_spell_in_contracts while the owner stages a member onto the linked index: the staging waits
    for the inspection's walk, the inspection answers None for an unknown id, and the member then reaches the
    borrower.
    """
    owner_book = _make_book()
    id_a = owner_book.bind(spell=_HeadA, existence=Existence.unique, permissions="create", binding_name="a")
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = _conduit("borrower")
    owner.link(borrower)
    index = owner_book.find_spell_by_spell_id(id_a).spell_index
    owner.bind_inactive(spell=_MemberB, spell_index=index, existence=Existence.unique,
                        permissions="create", binding_name="b")
    _link_index(borrower, owner, index)
    staged: Dict[str, str] = {}
    real_has_spell = Detail.has_spell

    def park_here(park: Callable[[], None]) -> None:
        def parking(self: Detail, spell_id: str) -> bool:
            answer = real_has_spell(self, spell_id)
            park()
            return answer

        monkeypatch.setattr(Detail, "has_spell", parking)

    def stage() -> None:
        staged["id"] = owner.bind_inactive(spell=_MemberC, spell_index=index, existence=Existence.unique,
                                           permissions="create", binding_name="c")

    outcome, stage_finished_mid_walk = _run_with_other_side_mid_walk(
        park_here,
        lambda: borrower.get_spell_in_contracts("0" * 64),
        stage,
    )

    assert "error" not in outcome, outcome.get("error")
    assert outcome["result"] is None
    assert stage_finished_mid_walk is False
    assert staged["id"] in borrower._spellbook._inactive_contracted_spells.get(owner._id, {})


def test_contract_listing_does_not_deadlock_with_a_concurrent_sever(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    get_spells_in_contract_by_conduit while the same conduit severs that link. Before 0.2.8231 the listing held the
    ward lock and then took the conduit lock (through find_contracted_spell) while sever_link holds the conduit lock
    and then takes the ward locks, and both threads hung for good. Now the listing resolves through the Book: the
    sever waits for the listing, the listing returns the lent spell, and the sever then completes.
    """
    owner_book = _make_book()
    lent_id = owner_book.bind(spell=_HeadA, existence=Existence.unique, permissions="create", binding_name="a")
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = _conduit("borrower")
    owner.link(borrower)
    _link_index(borrower, owner, owner_book.find_spell_by_spell_id(lent_id).spell_index)
    severed: Dict[str, object] = {}
    real_get_detail_map = Contract._get_detail_map

    def park_here(park: Callable[[], None]) -> None:
        def parking(self: Contract, ward) -> Dict[str, Detail]:
            answer = real_get_detail_map(self, ward)
            park()
            return answer

        monkeypatch.setattr(Contract, "_get_detail_map", parking)

    def sever() -> None:
        severed["result"] = borrower.sever_link(owner)

    outcome, sever_finished_mid_walk = _run_with_other_side_mid_walk(
        park_here,
        lambda: borrower.get_spells_in_contract_by_conduit(owner._id),
        sever,
    )

    assert "error" not in outcome, outcome.get("error")
    assert sever_finished_mid_walk is False
    assert [sid for sid, _ in outcome["result"]["inbound"]] == [lent_id]
    assert severed["result"] is True


def test_cleanup_spell_of_a_disposed_spell_raises_runtime_error() -> None:
    """
    Disposing a spell a second time - through the Conduit or the Spellbook - raises RuntimeError naming the spell,
    not AttributeError.
    """
    owner_book = _make_book()
    id_a = owner_book.bind(spell=_HeadA, existence=Existence.unique, permissions="create", binding_name="a")
    owner = owner_book.conjure(dynamic=True, name="owner")
    spell = owner_book.find_spell_by_spell_id(id_a)
    owner.cleanup_spell(spell=spell)

    with pytest.raises(RuntimeError, match=f"spell {id_a} has already been disposed"):
        owner.cleanup_spell(spell=spell)
    with pytest.raises(RuntimeError, match=f"spell {id_a} has already been disposed"):
        owner_book.cleanup_spell(spell=spell)
