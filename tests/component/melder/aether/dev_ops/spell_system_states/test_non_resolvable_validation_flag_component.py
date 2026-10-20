"""Component coverage: a resolvable=False definition no longer holds its Book's validation flag (meld_state_gate).

Real Spellbook, Conduit, SpellSystemStates and RiskManager wiring, no external IO. A definition bound
resolvable=False - a Protocol or a class kept for discovery and versioning, whose consumers receive the value by
override - carries `SpellState.non_resolvable` from its registration, and RiskManager leaves its never-filled
verdict out of the Book flag. The definition is still refused at every meld door, and every resolvable lineage keeps
its own risk: through notches both ways, ownership transfers (and a rolled-back one), a borrower that gets a version
back after a repeat notch, a contract consumer that follows its lender's notch, and melds racing notches.
"""

import threading
from collections.abc import Iterator
from typing import Any, ClassVar, Dict, List, Protocol, runtime_checkable

import pytest

from melder import Aether, Conduit
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership import TransferOfOwnership
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.meld import Meld
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


class Engine:
    """A resolvable `unique` service."""

    def __init__(self) -> None:
        """Mark the service ready."""
        self.ready: bool = True


class Machine:
    """A resolvable `many` consumer of the service."""

    def __init__(self, engine: Engine) -> None:
        """Keep the injected service."""
        self.engine: Engine = engine


class IThing(Protocol):
    """A descriptive Protocol definition; Melder never resolves it."""

    def run(self) -> None:
        """The behaviour implementers provide."""
        ...


class ShapeDefinition:
    """A class definition bound resolvable=False; its consumers receive a shape by override."""

    calls: ClassVar[int] = 0

    def __init__(self, sides: int = 3) -> None:
        """Count a construction, which must never happen through Melder."""
        ShapeDefinition.calls += 1
        self.sides: int = sides


class Painter:
    """A consumer whose only provider is the definition, so the shape is an override-required input."""

    def __init__(self, shape: ShapeDefinition) -> None:
        """Keep the supplied shape."""
        self.shape: ShapeDefinition = shape


class Widget:
    """The resolvable version of the widget lineage."""

    def __init__(self) -> None:
        """Mark the widget built."""
        self.built: bool = True


class WidgetDefinition:
    """The resolvable=False version of the same lineage."""

    calls: ClassVar[int] = 0

    def __init__(self) -> None:
        """Count a construction, which must never happen through Melder."""
        WidgetDefinition.calls += 1


@runtime_checkable
class IService(Protocol):
    """The contract a lender provides to a borrower."""

    def ping(self) -> str:
        """Name the version."""
        ...


class ImplA:
    """First version of the lent service."""

    def ping(self) -> str:
        """Name this version."""
        return "A"


class ImplB:
    """Second version of the lent service."""

    def ping(self) -> str:
        """Name this version."""
        return "B"


class Consumer:
    """A borrower-side consumer of the lent contract."""

    def __init__(self, service: IService = SpellContract(spellframe=IService, binding_name="svc")) -> None:
        """Keep the contracted service."""
        self.service: IService = service


@pytest.fixture(autouse=True)
def reset_melder() -> Iterator[None]:
    """Fresh cold Aether and fresh construction counters before and after every case."""
    Aether._reset_singleton_for_tests()
    world = Aether()
    Spellbook._aether = world
    Conduit._aether = world
    ShapeDefinition.calls = 0
    WidgetDefinition.calls = 0
    try:
        yield
    finally:
        Aether._reset_singleton_for_tests()
        world = Aether()
        Spellbook._aether = world
        Conduit._aether = world


@pytest.fixture
def gate_entries(monkeypatch: pytest.MonkeyPatch) -> Dict[str, int]:
    """Count entries into the meld-time validation gate, which runs only while the Book flag is up."""
    counter: Dict[str, int] = {"count": 0}
    original = Meld._ensure_lineage_resolvable

    def counting(meld: Meld, spell: Any) -> None:
        """Count one entry, then run the real gate."""
        counter["count"] += 1
        original(meld, spell)

    monkeypatch.setattr(Meld, "_ensure_lineage_resolvable", counting)
    return counter


def _book(frame: str, *, dynamic: bool, configure: bool = True) -> Spellbook:
    """A Book on `frame`; the first Book of a frame sets the frame's posture, with caching off."""
    book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    if configure:
        book.configure_aether_frame(
            system_state="dynamic" if dynamic else "automatic",
            disposal=None,
            disposal_method_names=None,
            system_caching_enabled=False,
        )
    return book


def _flagged(book: Spellbook, spell_id: str) -> bool:
    """Whether the lineage of `spell_id` carries `SpellState.non_resolvable`; the published set must agree."""
    spell = book.find_spell_by_spell_id(spell_id)
    assert spell is not None
    states = book._spell_system_states
    flagged = states.index_has_flag(spell.spell_index.id, SpellState.non_resolvable)
    assert (spell.spell_index.id in states.non_resolvable_index_ids) is flagged
    return flagged


def test_component_automatic_world_definition_leaves_the_flag_down_and_melds_skip_the_gate(
        gate_entries: Dict[str, int],
) -> None:
    """A Protocol definition no longer pins an automatic Book's flag; it is still refused at the door."""
    book = _book("nonres-auto", dynamic=False)
    book.bind(spell=Engine, existence="unique")
    book.bind(spell=Machine, existence="many")
    definition_id = book.bind(spell=IThing, existence="unique", resolvable=False)
    root = book.conjure(name="nonres-auto-root")
    try:
        assert _flagged(book, definition_id) is True
        assert book._spellbook_validation_required is False
        first = root.meld(spell=Machine)
        gate_entries["count"] = 0
        for _ in range(5):
            assert root.meld(spell=Machine).engine is first.engine
        assert gate_entries["count"] == 0
        with pytest.raises(MeldExecutionError, match="resolvable=False"):
            root.meld(spell_id=definition_id)
    finally:
        root.cleanup()


def test_component_dynamic_world_late_bound_definition_leaves_the_flag_down(gate_entries: Dict[str, int]) -> None:
    """A definition bound after conjure in a dynamic world raises no flag; the next melds skip the gate."""
    book = _book("nonres-dynamic", dynamic=True)
    book.bind(spell=Engine, existence="unique")
    book.bind(spell=Machine, existence="many")
    root = book.conjure(name="nonres-dynamic-root", dynamic=True)
    try:
        root.meld(spell=Machine)
        assert book._spellbook_validation_required is False
        definition_id = root.bind(spell=IThing, existence="unique", resolvable=False)
        assert _flagged(book, definition_id) is True
        assert book._spellbook_validation_required is False
        gate_entries["count"] = 0
        root.meld(spell=Machine)
        assert gate_entries["count"] == 0
        with pytest.raises(MeldExecutionError, match="resolvable=False"):
            root.meld(spell_id=definition_id)
    finally:
        root.cleanup()


def test_component_override_consumer_of_a_definition_melds_without_the_gate(gate_entries: Dict[str, int]) -> None:
    """A consumer that receives the definition's value by override melds with the flag down, and nothing builds it."""
    book = _book("nonres-override", dynamic=False)
    book.bind(spell=ShapeDefinition, existence="many", resolvable=False)
    book.bind(spell=Painter, existence="many")
    root = book.conjure(name="nonres-override-root")
    try:
        assert book._spellbook_validation_required is False
        square = object()
        circle = object()
        assert root.meld(spell=Painter, override={"shape": square}).shape is square
        gate_entries["count"] = 0
        assert root.meld(spell=Painter, override={"shape": circle}).shape is circle
        assert gate_entries["count"] == 0
        assert ShapeDefinition.calls == 0
    finally:
        root.cleanup()


def test_component_notch_to_a_definition_and_back_moves_the_flag(gate_entries: Dict[str, int]) -> None:
    """A notch to the definition keeps the flag down; the notch back raises it until the next meld revalidates."""
    book = _book("nonres-notch", dynamic=True)
    widget_id = book.bind(spell=Widget, spellframe="widgets", binding_name="widget", existence="many")
    root = book.conjure(name="nonres-notch-root", dynamic=True)
    try:
        assert root.meld(spell_id=widget_id).built is True
        assert book._spellbook_validation_required is False
        index = book.find_spell_by_spell_id(widget_id).spell_index
        definition_id = root.bind_inactive(spell=WidgetDefinition, spell_index=index, spellframe="widgets",
                                           binding_name="widget", existence="many", resolvable=False)

        root.notch_spell(spell_index=index, spell=book._inactive_spells[definition_id])
        assert _flagged(book, definition_id) is True
        assert book._spellbook_validation_required is False
        with pytest.raises(MeldExecutionError, match="resolvable=False"):
            root.meld(spellframe="widgets", binding_name="widget")

        root.notch_spell(spell_index=index, spell=book._inactive_spells[widget_id])
        assert _flagged(book, widget_id) is False
        assert book._spellbook_validation_required is True
        gate_entries["count"] = 0
        assert root.meld(spellframe="widgets", binding_name="widget").built is True
        assert gate_entries["count"] >= 1
        assert book._spellbook_validation_required is False
        assert WidgetDefinition.calls == 0
    finally:
        root.cleanup()


def test_component_borrower_revalidates_a_version_it_gets_back_after_a_repeat_notch(
        gate_entries: Dict[str, int],
) -> None:
    """A borrower that gets v1 back after notching to an already-compiled definition revalidates it at its next meld."""
    lender_book = _book("nonres-borrower", dynamic=True)
    borrower_book = _book("nonres-borrower", dynamic=True, configure=False)
    widget_id = lender_book.bind(spell=Widget, spellframe="widgets", binding_name="widget", existence="many",
                                 permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        lender.link(borrower)
        index = lender_book.find_spell_by_spell_id(widget_id).spell_index
        with borrower.transaction("link", conduits=[borrower, lender]):
            assert borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
        borrower.validate_contracts_and_define()
        assert borrower.meld(spell_id=widget_id).built is True
        assert borrower_book._spellbook_validation_required is False
        definition_id = lender.bind_inactive(spell=WidgetDefinition, spell_index=index, spellframe="widgets",
                                             binding_name="widget", existence="many", permissions="create",
                                             resolvable=False)
        lender.notch_spell(spell_index=index, spell=lender_book._inactive_spells[definition_id])
        assert borrower_book._spellbook_validation_required is False
        lender.notch_spell(spell_index=index, spell=lender_book._inactive_spells[widget_id])
        assert borrower.meld(spell_id=widget_id).built is True
        assert borrower_book._spellbook_validation_required is False

        # At a notch commit only a member never compiled runs phases 1-4, so this second notch to the definition
        # leaves the lineage gated; the notch back then publishes no gate event, and the borrower gets v1 back by
        # reactivation, which never re-registers it with RiskManager. The re-published validity raises its flag.
        lender.notch_spell(spell_index=index, spell=lender_book._inactive_spells[definition_id])
        assert borrower_book._spellbook_validation_required is False
        lender.notch_spell(spell_index=index, spell=lender_book._inactive_spells[widget_id])
        assert borrower_book._spellbook_validation_required is True
        gate_entries["count"] = 0
        assert borrower.meld(spell_id=widget_id).built is True
        assert gate_entries["count"] >= 1
        resolution = borrower_book._spell_system_states.get_conduit_resolution_state(borrower.id)
        assert resolution.get_spell_validity(widget_id) is SpellValidity.valid
        assert WidgetDefinition.calls == 0
    finally:
        borrower.cleanup()
        lender.cleanup()


def test_component_transferred_definition_keeps_the_exclusion_on_its_new_owner() -> None:
    """A definition moved to another root carries the flag there and holds neither Book's flag up."""
    owner_book = _book("nonres-transfer", dynamic=True)
    target_book = _book("nonres-transfer", dynamic=True, configure=False)
    definition_id = owner_book.bind(spell=ShapeDefinition, existence="many", permissions="create", resolvable=False)
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")
    try:
        assert owner_book._spellbook_validation_required is False
        owner.transfer_spell_ownership(spell=definition_id, target_conduit=target)
        assert target_book.find_spell_by_spell_id(definition_id) is not None
        assert _flagged(target_book, definition_id) is True
        assert target_book._spellbook_validation_required is False
        assert owner_book._spellbook_validation_required is False
        with pytest.raises(MeldExecutionError, match="resolvable=False"):
            target.meld(spell_id=definition_id)
        assert ShapeDefinition.calls == 0
    finally:
        target.cleanup()
        owner.cleanup()


def test_component_rolled_back_transfer_keeps_the_exclusion_on_the_source(monkeypatch: pytest.MonkeyPatch) -> None:
    """A transfer that fails after the flip rolls back with the definition still excluded on its owner."""
    owner_book = _book("nonres-rollback", dynamic=True)
    target_book = _book("nonres-rollback", dynamic=True, configure=False)
    definition_id = owner_book.bind(spell=ShapeDefinition, existence="many", permissions="create", resolvable=False)
    owner = owner_book.conjure(dynamic=True, name="owner")
    target = target_book.conjure(dynamic=True, name="target")

    def fail_after_the_flip(transfer: TransferOfOwnership, spell: Any) -> None:
        """Fail the step that follows the ownership flip."""
        raise RuntimeError("forced failure after the flip")

    monkeypatch.setattr(TransferOfOwnership, "_move_creations", fail_after_the_flip)
    try:
        with pytest.raises(Exception, match="forced failure after the flip"):
            owner.transfer_spell_ownership(spell=definition_id, target_conduit=target)
        assert owner_book.find_spell_by_spell_id(definition_id) is not None
        assert _flagged(owner_book, definition_id) is True
        assert owner_book._spellbook_validation_required is False
    finally:
        target.cleanup()
        owner.cleanup()


def test_component_contract_consumer_still_follows_its_lenders_notch_beside_a_definition() -> None:
    """A borrower Book with its own definition keeps today's contract behaviour: the consumer follows the notch."""
    lender_book = _book("nonres-contract", dynamic=True)
    borrower_book = _book("nonres-contract", dynamic=True, configure=False)
    id_a = lender_book.bind(spell=ImplA, spellframe=IService, binding_name="svc", existence=Existence.many,
                            permissions="create")
    borrower_book.bind(spell=Consumer, existence=Existence.many, permissions="create")
    borrower_book.bind(spell=IThing, existence="unique", resolvable=False)
    lender = lender_book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        lender.link(borrower)
        index = lender_book.find_spell_by_spell_id(id_a).spell_index
        with borrower.transaction("link", conduits=[borrower, lender]):
            assert borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
        borrower.validate_contracts_and_define()
        assert borrower.meld(spell=Consumer).service.ping() == "A"
        id_b = lender.bind_inactive(spell=ImplB, spell_index=index, spellframe=IService, binding_name="svc",
                                    existence=Existence.many, permissions="create")

        lender.notch_spell(spell_index=index, spell=lender_book._inactive_spells[id_b])

        assert borrower.meld(spell=Consumer).service.ping() == "B"
    finally:
        borrower.cleanup()
        lender.cleanup()


def test_component_melds_racing_notches_never_build_the_definition() -> None:
    """Concurrent melds while the lineage is notched between its versions build only the resolvable one."""
    book = _book("nonres-race", dynamic=True)
    widget_id = book.bind(spell=Widget, spellframe="widgets", binding_name="widget", existence="many")
    root = book.conjure(name="nonres-race-root", dynamic=True)
    index = book.find_spell_by_spell_id(widget_id).spell_index
    definition_id = root.bind_inactive(spell=WidgetDefinition, spell_index=index, spellframe="widgets",
                                       binding_name="widget", existence="many", resolvable=False)
    stop = threading.Event()
    start = threading.Barrier(5)
    built: List[object] = []
    misses: List[KeyError] = []
    unexpected: List[BaseException] = []

    def meld_until_stopped() -> None:
        """
        Meld the lineage by its binding until the notches end.

        Two outcomes besides a Widget are expected: the definition refused at the door while it is the selected
        version, and a binding lookup that lands inside a notch's swap (the outgoing version already off the active
        maps, the incoming one not yet on them) and finds no spell - Melder's lookups take no Book lock, and a lookup
        inside a notch answers nothing for that lineage. Anything else is a failure.
        """
        start.wait()
        while not stop.is_set():
            try:
                built.append(root.meld(spellframe="widgets", binding_name="widget"))
            except MeldExecutionError as exc:
                if "resolvable=False" not in str(exc):
                    unexpected.append(exc)
            except KeyError as exc:
                if "No spell found for frame='widgets', binding='widget'" in str(exc):
                    misses.append(exc)
                else:
                    unexpected.append(exc)
            except BaseException as exc:
                unexpected.append(exc)

    def notch_back_and_forth() -> None:
        """Notch the lineage to the definition and back twenty times."""
        start.wait()
        try:
            for _ in range(20):
                root.notch_spell(spell_index=index, spell=book._inactive_spells[definition_id])
                root.notch_spell(spell_index=index, spell=book._inactive_spells[widget_id])
        except BaseException as exc:
            unexpected.append(exc)
        finally:
            stop.set()

    threads = [threading.Thread(target=meld_until_stopped) for _ in range(4)]
    threads.append(threading.Thread(target=notch_back_and_forth))
    try:
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=120)
        assert not any(thread.is_alive() for thread in threads)
        assert unexpected == []
        assert WidgetDefinition.calls == 0
        assert all(type(obj) is Widget for obj in built)
        assert root.meld(spellframe="widgets", binding_name="widget").built is True
        assert book._spellbook_validation_required is False
    finally:
        stop.set()
        root.cleanup()
