"""Integration regressions for contract_recheck_on_notch_2026_10_16: rule 2 and D2 (melder_1, 2026-10-16).

A satisfied SpellContract is not checked on every meld. A change of what a spell resolves - a notch, park,
reactivation or removal of its provider's active copy, or (D2) a notch of anything it depends on, in its Book or
another - marks it for revalidation, and its next meld rechecks it and rebuilds against the versions now active, or
fails with the error a first meld of them gives. Objects already built keep what they were built with.

Each test builds its own dynamic frame with caching off: a lender Book lends a provider under (IService, "svc") and
a borrower Book's consumer holds a SpellContract on that key, or one Book holds a dependency chain.
"""
import threading
from typing import Any, Iterator, List, Protocol, Tuple, runtime_checkable

import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError
from tests._spell_identity_test_support import version_of


@runtime_checkable
class IService(Protocol):
    """The contract a lender provides."""

    def ping(self) -> str:
        """Name the version that answered."""
        ...


@runtime_checkable
class IDep(Protocol):
    """The contract of a dependency."""

    def tag(self) -> str:
        """Name the version that answered."""
        ...


class Missing:
    """A type nobody binds."""


class ImplA:
    """First version of the lent service."""

    def ping(self) -> str:
        """Answer "A"."""
        return "A"


class ImplB:
    """Second version of the lent service."""

    def ping(self) -> str:
        """Answer "B"."""
        return "B"


class ImplBroken:
    """A version whose __init__ needs a type nobody binds."""

    def __init__(self, missing: Missing) -> None:
        """Keep the input nobody can provide."""
        self.missing = missing

    def ping(self) -> str:
        """Never reached: the version cannot be built."""
        return "broken"


class DepA:
    """First implementer of IDep."""

    def tag(self) -> str:
        """Answer "d1"."""
        return "d1"


class DepB:
    """Second implementer of IDep, the notch target."""

    def tag(self) -> str:
        """Answer "d2"."""
        return "d2"


class Dep:
    """A dependency bound by its class."""

    def tag(self) -> str:
        """Answer "d1"."""
        return "d1"


class Dep2(Dep):
    """A subclass of Dep, which the kind rule does not select for an annotation naming Dep."""

    def tag(self) -> str:
        """Answer "d2"."""
        return "d2"


class PChain:
    """Depends on IDep."""

    def __init__(self, dep: IDep) -> None:
        """Keep the dependency."""
        self.dep = dep


class QChain:
    """Depends on PChain, two hops from IDep."""

    def __init__(self, p: PChain) -> None:
        """Keep the dependency."""
        self.p = p


class PClass:
    """Depends on Dep's class."""

    def __init__(self, dep: Dep) -> None:
        """Keep the dependency."""
        self.dep = dep


class QClass:
    """Depends on PClass."""

    def __init__(self, p: PClass) -> None:
        """Keep the dependency."""
        self.p = p


class ImplWithIDep:
    """A lent service with a dependency of its own."""

    def __init__(self, dep: IDep) -> None:
        """Keep the dependency."""
        self.dep = dep

    def ping(self) -> str:
        """Answer "P+" and the dependency's tag."""
        return "P+" + self.dep.tag()


class Consumer:
    """The borrower's consumer of the (IService, "svc") contract."""

    def __init__(self, service: IService = SpellContract(spellframe=IService, binding_name="svc")) -> None:
        """Keep the contracted provider."""
        self.service = service


class User:
    """Depends on the borrower's contract consumer."""

    def __init__(self, c: Consumer) -> None:
        """Keep the consumer."""
        self.c = c


class _Lent:
    """
    A lender and a borrower conduit, the lent provider's index, and the consumer's spell id.

    Purpose:
        The lent-provider world of the rule-2 scenarios, built by `_lend`.
    """

    def __init__(
            self,
            lender_book: Spellbook,
            borrower_book: Spellbook,
            lender: Conduit,
            borrower: Conduit,
            index: SpellIndex,
            provider_id: str,
            consumer_id: str,
    ) -> None:
        """Keep the world's parts; the tests clean the conduits."""
        self.lender_book = lender_book
        self.borrower_book = borrower_book
        self.lender = lender
        self.borrower = borrower
        self.index = index
        self.provider_id = provider_id
        self.consumer_id = consumer_id

    def meld_ping(self) -> str:
        """Meld the consumer through the borrower and ask its provider."""
        return self.borrower.meld(spell=Consumer).service.ping()

    def notch_to(self, impl: type) -> str:
        """Stage `impl` in the provider's index and notch to it; return its version id."""
        new_id = self.lender.bind_inactive(spell=impl, spell_index=self.index, spellframe=IService,
                                           binding_name="svc", existence=Existence.many, permissions="create")
        self.notch_back(new_id)
        return new_id

    def notch_back(self, version_id: str) -> None:
        """Notch the provider's index to a version it holds, named by its id (active or parked)."""
        self.lender.notch_spell(spell_index=self.index, spell_id=version_id)

    def cleanup(self) -> None:
        """Tear the borrower down, then the lender."""
        self.borrower.cleanup()
        self.lender.cleanup()


@pytest.fixture(autouse=True)
def fresh_aether() -> Iterator[None]:
    """Give every test a fresh Aether, rebound on Spellbook and Conduit, and reset it after."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture
def resolution_passes(monkeypatch: pytest.MonkeyPatch) -> List[str]:
    """Record the spell name of every target-local 5-11 pass a meld runs."""
    passes: List[str] = []
    original = Spellbook._run_resolution_phases_for_target_spell

    def _counting(self: Spellbook, conduit_id: str, spell: Any) -> Any:
        passes.append(spell.spell_name)
        return original(self, conduit_id, spell)

    monkeypatch.setattr(Spellbook, "_run_resolution_phases_for_target_spell", _counting)
    return passes


def _books(frame: str) -> Tuple[Spellbook, Spellbook]:
    """Two Books on a fresh dynamic frame with caching off."""
    first = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    first.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                 system_caching_enabled=False)
    second = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    return first, second


def _lend(frame: str, impl: type, *, consumer_existence: Existence = Existence.many,
          index_link: bool = True) -> _Lent:
    """The lender lends `impl` under (IService, "svc") by an index link (or a version grant) to the consumer."""
    lender_book, borrower_book = _books(frame)
    provider_id = lender_book.bind(spell=impl, spellframe=IService, binding_name="svc", existence=Existence.many,
                                   permissions="create")
    consumer_id = borrower_book.bind(spell=Consumer, existence=consumer_existence, permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    lender.link(borrower)
    index = lender_book.find_spell_by_spell_id(provider_id).spell_index
    with borrower.transaction("link", conduits=[borrower, lender]):
        if index_link:
            assert borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
        else:
            assert borrower.add_spell_to_contract(spell_id=provider_id, conduit=lender, permissions="create")
    return _Lent(lender_book, borrower_book, lender, borrower, index, provider_id, consumer_id)


def _assert_lost_contract_reported(error: SpellbookValidationError) -> None:
    """The refusal names the lost contract and its remedy (D1-B), not the generic gated line."""
    message = str(error)
    assert "has no provider for its SpellContract" in message
    assert "add_index_to_contract" in message
    assert "[SPELL_CONTRACT_MISSING_PROVIDER]" in message
    assert "No validation error was recorded" not in message


def test_contract_consumer_follows_notch_notch_back_and_repeat_notch_with_one_rebuild_each(
        resolution_passes: List[str],
) -> None:
    """
    S1: the consumer follows its lender's notch to B, the notch back to A and a repeat notch to B; each change
    costs one 5-11 pass at the next meld and warm melds none; an object built before a notch keeps its provider.
    """
    world = _lend("s1", ImplA)
    try:
        before = world.borrower.meld(spell=Consumer)
        assert before.service.ping() == "A"
        resolution_passes.clear()
        assert [world.meld_ping() for _ in range(5)] == ["A"] * 5
        assert resolution_passes == []

        b_id = world.notch_to(ImplB)
        assert world.meld_ping() == "B"
        assert resolution_passes == ["Consumer"]
        assert world.meld_ping() == "B"
        assert resolution_passes == ["Consumer"]
        assert before.service.ping() == "A"

        resolution_passes.clear()
        world.notch_back(world.provider_id)
        assert world.meld_ping() == "A"
        assert world.meld_ping() == "A"
        assert resolution_passes == ["Consumer"]

        resolution_passes.clear()
        world.notch_back(b_id)
        assert world.meld_ping() == "B"
        assert world.meld_ping() == "B"
        assert resolution_passes == ["Consumer"]
    finally:
        world.cleanup()


def test_a_notch_marks_the_contract_consumer_and_builds_nothing(resolution_passes: List[str]) -> None:
    """A notch leaves the consumer gated with `contract_unvalidated` and runs no pass until the consumer melds."""
    world = _lend("marked", ImplA)
    try:
        assert world.meld_ping() == "A"
        resolution_passes.clear()

        world.notch_to(ImplB)

        state = world.borrower_book.find_spell_by_spell_id(world.consumer_id).system_state
        assert state.validity is SpellValidity.gated
        assert state.has_flag(SpellState.contract_unvalidated)
        assert resolution_passes == []
    finally:
        world.cleanup()


def test_a_unique_consumer_keeps_its_object_after_a_notch_and_builds_the_new_version_after_a_purge() -> None:
    """S6: mark only - the stored unique object keeps its provider; a purge lets the next meld build version B."""
    world = _lend("s6", ImplA, consumer_existence=Existence.unique)
    try:
        first = world.borrower.meld(spell=Consumer)
        world.notch_to(ImplB)

        again = world.borrower.meld(spell=Consumer)
        assert again is first
        assert again.service.ping() == "A"

        world.borrower.purge(spell=Consumer)
        assert world.meld_ping() == "B"
    finally:
        world.cleanup()


def test_a_notch_to_an_unresolvable_version_raises_the_first_melds_error_and_a_notch_back_recovers() -> None:
    """S3: the consumer meets the error a first meld of ImplBroken gives, and follows the notch back to A."""
    world = _lend("s3", ImplA)
    try:
        assert world.meld_ping() == "A"
        world.notch_to(ImplBroken)

        with pytest.raises(UnresolvedInputError, match="ImplBroken.missing expects Missing"):
            world.meld_ping()

        world.notch_back(world.provider_id)
        assert world.meld_ping() == "A"
    finally:
        world.cleanup()


def test_destroying_the_providers_index_fails_the_consumer_naming_the_lost_contract() -> None:
    """S4: an index destroy fails the consumer with SpellbookValidationError naming the contract and the remedy."""
    world = _lend("s4", ImplA)
    try:
        assert world.meld_ping() == "A"
        world.lender.cleanup_spell(spell=world.lender_book.find_spell_by_spell_id(world.provider_id))

        with pytest.raises(SpellbookValidationError) as raised:
            world.meld_ping()

        assert not isinstance(raised.value, MeldExecutionError)
        _assert_lost_contract_reported(raised.value)
    finally:
        world.cleanup()


def test_releasing_the_index_link_fails_the_consumer_naming_the_lost_contract() -> None:
    """An index uncontract fails the consumer's next meld with the lost contract and its remedy."""
    world = _lend("uncontract_index", ImplA)
    try:
        assert world.meld_ping() == "A"
        world.borrower.remove_index_from_contract(index_id=world.index.id, conduit=world.lender)

        with pytest.raises(SpellbookValidationError) as raised:
            world.meld_ping()

        _assert_lost_contract_reported(raised.value)
    finally:
        world.cleanup()


def test_releasing_a_version_grant_fails_the_consumer_naming_the_lost_contract() -> None:
    """A version uncontract fails the consumer's next meld with the lost contract and its remedy."""
    world = _lend("uncontract_spell", ImplA, index_link=False)
    try:
        assert world.meld_ping() == "A"
        with world.borrower.transaction("link", conduits=[world.borrower, world.lender]):
            world.borrower.remove_spell_from_contract(spell_id=world.provider_id, conduit=world.lender)

        with pytest.raises(SpellbookValidationError) as raised:
            world.meld_ping()

        _assert_lost_contract_reported(raised.value)
    finally:
        world.cleanup()


def test_a_notch_back_reactivates_a_version_grant_and_its_consumer_rebuilds_with_one_pass(
        resolution_passes: List[str],
) -> None:
    """
    D3: the notch to B parks the borrower's version grant of A, so the consumer fails naming the lost contract; the
    notch back to A makes that copy active again, the consumer builds A with one 5-11 pass, an object built before
    keeps its provider, and a linked peer that never borrowed A gains no provider.
    """
    world = _lend("anchored_back", ImplA, index_link=False)
    bystander_book = Spellbook(aetheric_frame="anchored_back",
                               configuration=SpellbookConfiguration("anchored_back").with_defaults())
    # A version of Consumer of its own: one class is one spell, and the borrower bound Consumer.
    bystander_id = bystander_book.bind(spell=version_of(Consumer, bystander=True), binding_name="bystander",
                                       existence=Existence.many, permissions="create")
    bystander = bystander_book.conjure(dynamic=True, name="bystander")
    try:
        world.lender.link(bystander)
        before = world.borrower.meld(spell=Consumer)
        assert before.service.ping() == "A"

        world.notch_to(ImplB)
        with pytest.raises(SpellbookValidationError) as lost:
            world.meld_ping()
        _assert_lost_contract_reported(lost.value)

        resolution_passes.clear()
        world.notch_back(world.provider_id)
        assert resolution_passes == []
        assert world.meld_ping() == "A"
        assert world.meld_ping() == "A"
        assert resolution_passes == ["Consumer"]
        assert before.service.ping() == "A"

        with pytest.raises(SpellbookValidationError) as untouched:
            bystander.meld(spell_id=bystander_id)
        _assert_lost_contract_reported(untouched.value)
    finally:
        bystander.cleanup()
        world.cleanup()


def test_a_grant_of_a_parked_version_becomes_active_when_the_lender_notches_to_it() -> None:
    """
    D3: a version granted while parked stays off resolution - the consumer fails naming the lost contract - until
    the lender notches to it; the notch makes the borrower's copy active and the consumer builds that version. The
    grant takes the parked Spell object (until 0.2.8253 `get_spell_by_id` answered a parked id with the active
    member).
    """
    lender_book, borrower_book = _books("grant_parked")
    a_id = lender_book.bind(spell=ImplA, spellframe=IService, binding_name="svc", existence=Existence.many,
                            permissions="create")
    borrower_book.bind(spell=Consumer, existence=Existence.many, permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        lender.link(borrower)
        index = lender_book.find_spell_by_spell_id(a_id).spell_index
        b_id = lender.bind_inactive(spell=ImplB, spell_index=index, spellframe=IService, binding_name="svc",
                                    existence=Existence.many, permissions="create")
        parked_b = lender_book._get_owned_spell(b_id)
        with borrower.transaction("link", conduits=[borrower, lender]):
            assert borrower.add_spell_to_contract(spell=parked_b, conduit=lender, permissions="create")
        with pytest.raises(SpellbookValidationError) as lost:
            borrower.meld(spell=Consumer)
        _assert_lost_contract_reported(lost.value)

        lender.notch_spell(spell_index=index, spell_id=b_id)
        assert borrower.meld(spell=Consumer).service.ping() == "B"
    finally:
        borrower.cleanup()
        lender.cleanup()


def _chain(frame: str, *, by_class: bool = False) -> Tuple[Spellbook, Conduit, SpellIndex, type, type]:
    """
    One Book: Dep, P(dep) and Q(p), all `many`; by class (PClass, QClass over Dep) or by IDep (PChain, QChain).

    By class, Dep is bound under the category "Dep" - the address a bare bind gives it - so its next version can be
    staged under the same binding: every version of an index is bound the way its first version was (2026-10-25).
    """
    book, _ = _books(frame)
    if by_class:
        dep_id = book.bind(spell=Dep, existence=Existence.many, permissions="create", spellframe="Dep")
        p_cls, q_cls = PClass, QClass
    else:
        dep_id = book.bind(spell=DepA, spellframe=IDep, binding_name="dep", existence=Existence.many,
                           permissions="create")
        p_cls, q_cls = PChain, QChain
    book.bind(spell=p_cls, existence=Existence.many, permissions="create")
    book.bind(spell=q_cls, existence=Existence.many, permissions="create")
    root = book.conjure(dynamic=True, name="root")
    return book, root, book.find_spell_by_spell_id(dep_id).spell_index, p_cls, q_cls


def _notch_dep(book: Spellbook, root: Conduit, index: SpellIndex, *, by_class: bool = False) -> None:
    """Stage the dependency's next version (DepB under IDep, or Dep2 by class) and notch to it."""
    if by_class:
        new_id = root.bind_inactive(
            spell=Dep2, spell_index=index, existence=Existence.many, permissions="create", spellframe="Dep",
        )
    else:
        new_id = root.bind_inactive(spell=DepB, spell_index=index, spellframe=IDep, binding_name="dep",
                                    existence=Existence.many, permissions="create")
    root.notch_spell(spell_index=index, spell_id=new_id)


def test_c1_a_dependent_two_hops_away_follows_a_dependency_notch() -> None:
    """C1: Q -> P -> Dep in one Book, Q melded before the notch: Q and P build the new Dep version."""
    book, root, index, p_cls, q_cls = _chain("c1")
    try:
        assert root.meld(spell=q_cls).p.dep.tag() == "d1"
        _notch_dep(book, root, index)

        assert root.meld(spell=q_cls).p.dep.tag() == "d2"
        assert root.meld(spell=q_cls).p.dep.tag() == "d2"
        assert root.meld(spell=p_cls).dep.tag() == "d2"
    finally:
        root.cleanup()


def test_c2_a_chain_never_melded_before_a_dependency_notch_builds_the_new_version() -> None:
    """C2: nothing melded before the notch: Q builds the new Dep version instead of failing on the old plan."""
    book, root, index, p_cls, q_cls = _chain("c2")
    try:
        _notch_dep(book, root, index)

        assert root.meld(spell=q_cls).p.dep.tag() == "d2"
        assert root.meld(spell=p_cls).dep.tag() == "d2"
    finally:
        root.cleanup()


def test_c3_a_chain_melded_before_a_dependency_notch_follows_it_from_either_end() -> None:
    """C3: P and Q melded before the notch, Q first after it: both build the new Dep version."""
    book, root, index, p_cls, q_cls = _chain("c3")
    try:
        assert root.meld(spell=p_cls).dep.tag() == "d1"
        assert root.meld(spell=q_cls).p.dep.tag() == "d1"
        _notch_dep(book, root, index)

        assert root.meld(spell=q_cls).p.dep.tag() == "d2"
        assert root.meld(spell=p_cls).dep.tag() == "d2"
    finally:
        root.cleanup()


def test_c4_a_notch_to_a_version_the_annotation_does_not_select_raises_the_first_melds_error() -> None:
    """C4: Dep notched to its subclass, which `dep: Dep` does not select: Q fails as a first meld would."""
    book, root, index, _, q_cls = _chain("c4", by_class=True)
    try:
        assert root.meld(spell=q_cls).p.dep.tag() == "d1"
        _notch_dep(book, root, index, by_class=True)

        with pytest.raises(UnresolvedInputError, match="PClass.dep expects Dep"):
            root.meld(spell=q_cls)
    finally:
        root.cleanup()


def _across(frame: str) -> Tuple[Spellbook, Spellbook, Conduit, Conduit, SpellIndex]:
    """
    X1's world: the lender's ImplWithIDep (dep: IDep) and DepA index-linked into a borrower whose Consumer holds the
    (IService, "svc") contract and whose User depends on Consumer; links made after both conjures.
    """
    lender_book, borrower_book = _books(frame)
    dep_id = lender_book.bind(spell=DepA, spellframe=IDep, binding_name="dep", existence=Existence.many,
                              permissions="create")
    p_id = lender_book.bind(spell=ImplWithIDep, spellframe=IService, binding_name="svc", existence=Existence.many,
                            permissions="create")
    borrower_book.bind(spell=Consumer, existence=Existence.many, permissions="create")
    borrower_book.bind(spell=User, existence=Existence.many, permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    lender.link(borrower)
    p_index = lender_book.find_spell_by_spell_id(p_id).spell_index
    d_index = lender_book.find_spell_by_spell_id(dep_id).spell_index
    with borrower.transaction("link", conduits=[borrower, lender]):
        assert borrower.add_index_to_contract(index=p_index, conduit=lender, permissions="create")
        assert borrower.add_index_to_contract(index=d_index, conduit=lender, permissions="create")
    return lender_book, borrower_book, lender, borrower, d_index


def test_a_contract_consumers_dependent_resolves_the_provider_linked_after_conjure() -> None:
    """
    The link regression: User, compiled at conjure with Consumer's SpellContract default unresolved, builds Consumer
    with the provider the link supplied (the link marks Consumer, and its mark walks on to User).
    """
    lender_book, borrower_book, lender, borrower, _ = _across("x1link")
    try:
        assert borrower.meld(spell=User).c.service.ping() == "P+d1"
    finally:
        borrower.cleanup()
        lender.cleanup()


def test_x1_a_dependency_notch_in_the_lending_book_reaches_the_borrowers_dependents() -> None:
    """X1: the lender notches the dependency of its lent provider; the borrower's User builds P over DepB."""
    lender_book, borrower_book, lender, borrower, d_index = _across("x1")
    try:
        assert borrower.meld(spell=User).c.service.ping() == "P+d1"
        new_id = lender.bind_inactive(spell=DepB, spell_index=d_index, spellframe=IDep, binding_name="dep",
                                      existence=Existence.many, permissions="create")
        lender.notch_spell(spell_index=d_index, spell_id=new_id)

        assert borrower.meld(spell=User).c.service.ping() == "P+d2"
        assert borrower.meld(spell=User).c.service.ping() == "P+d2"
        assert borrower.meld(spell=Consumer).service.ping() == "P+d2"
        assert lender.meld(spellframe=IService, binding_name="svc").ping() == "P+d2"
    finally:
        borrower.cleanup()
        lender.cleanup()


def test_melds_racing_notches_get_a_version_or_the_lost_provider_refusal_and_end_on_the_last_version() -> None:
    """
    Melds of the consumer on four threads race 20 notches between A and B (GIL off on 3.14t): each meld returns
    a version, or the lost-provider refusal while a notch has the copy parked; nothing else is raised, and the
    first meld after the race builds the version the last notch selected.
    """
    world = _lend("race", ImplA)
    stop = threading.Event()
    unexpected: List[BaseException] = []

    def _meld_until_stopped() -> None:
        while not stop.is_set():
            try:
                world.meld_ping()
            except SpellbookValidationError:
                continue
            except BaseException as exc:
                unexpected.append(exc)
                return

    threads = [threading.Thread(target=_meld_until_stopped) for _ in range(4)]
    try:
        assert world.meld_ping() == "A"
        for thread in threads:
            thread.start()
        b_id = world.notch_to(ImplB)
        versions = [b_id, world.provider_id] * 10
        for version_id in versions[1:]:
            world.notch_back(version_id)
    finally:
        stop.set()
        for thread in threads:
            thread.join(timeout=60)
    try:
        assert unexpected == []
        assert world.meld_ping() == "A"
    finally:
        world.cleanup()


class _BoundDuringFanOut:
    """A spell a borrower binds while a lender's notch fans out (design 2's lock guard)."""

    def ping(self) -> str:
        """Answer "bound"."""
        return "bound"


def _hook_lender_fan_out(monkeypatch: pytest.MonkeyPatch, world: _Lent, during: Any) -> None:
    """Run `during()` once, inside the lender's first `_activate_borrowed_spell`, then the real fan-out step."""
    original = Conduit._activate_borrowed_spell
    fired = threading.Event()

    def _wrapped(self: Conduit, spell_id: str) -> None:
        if self is world.lender and not fired.is_set():
            fired.set()
            during()
        original(self, spell_id)

    monkeypatch.setattr(Conduit, "_activate_borrowed_spell", _wrapped)


def test_a_borrower_meld_issued_during_a_lenders_notch_fan_out_waits_and_gets_the_new_version(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Design 2 (TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout): a lender's notch moves its borrowers
    while their creation gates are still parked, so a borrower meld issued during that fan-out waits for the notch to
    end and builds the version it selected; it never runs between the park and the reactivation.
    """
    world = _lend("fanout_park", ImplA)
    seen: List[str] = []
    threads: List[threading.Thread] = []

    def _meld_now() -> None:
        meld = threading.Thread(target=lambda: seen.append(world.meld_ping()))
        meld.start()
        meld.join(0.5)
        seen.append("parked" if meld.is_alive() else "ran")
        threads.append(meld)

    try:
        assert world.meld_ping() == "A"
        _hook_lender_fan_out(monkeypatch, world, _meld_now)
        world.notch_to(ImplB)
        for thread in threads:
            thread.join(10)
        assert seen == ["parked", "B"]
    finally:
        world.cleanup()


def test_a_fan_out_error_during_a_lenders_notch_undoes_the_whole_notch(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    The owner's choice for design 2: when moving the borrowers fails, the notch is undone - the lender's index is back
    on the outgoing version, the borrower still melds it, and the error propagates.
    """
    from melder.aether.conduit.conduit_ward.conduit_ward import ConduitWard

    world = _lend("fanout_undo", ImplA)
    original = ConduitWard._emit_index_notch

    def _failing_forward(self: ConduitWard, index: SpellIndex, old_spell_id: Any, new_spell_id: str) -> None:
        if new_spell_id != world.provider_id:
            raise RuntimeError("fan-out boom")
        original(self, index, old_spell_id, new_spell_id)

    try:
        assert world.meld_ping() == "A"
        monkeypatch.setattr(ConduitWard, "_emit_index_notch", _failing_forward)
        with pytest.raises(RuntimeError, match="fan-out boom"):
            world.notch_to(ImplB)
        assert world.index.selected_spell_id == world.provider_id
        assert world.meld_ping() == "A"
    finally:
        world.cleanup()


def test_a_borrower_bind_during_a_lenders_notch_fan_out_finishes_after_it(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Design 2's lock guard: a borrower-side bind issued while the lender's notch fans out (holding its seal and taking
    the borrower Book's lock) neither deadlocks the notch nor fails; it completes, and the borrower follows the notch.
    """
    world = _lend("fanout_bind", ImplA)
    bound: List[str] = []
    threads: List[threading.Thread] = []

    def _bind_now() -> None:
        bind = threading.Thread(target=lambda: bound.append(
            world.borrower_book.bind(spell=_BoundDuringFanOut, existence=Existence.many, permissions="create")
        ))
        bind.start()
        bind.join(0.3)
        threads.append(bind)

    try:
        assert world.meld_ping() == "A"
        _hook_lender_fan_out(monkeypatch, world, _bind_now)
        world.notch_to(ImplB)
        for thread in threads:
            thread.join(30)
        assert not any(thread.is_alive() for thread in threads)
        assert len(bound) == 1
        assert world.meld_ping() == "B"
    finally:
        world.cleanup()
