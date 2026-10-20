"""
D3 probe (EPIC-2026-10-14-slotted_lifetime_ownership_fixes): two removal paths found while re-reading the D3 code.

Cases:
  m1 transfer with move_creations=True into a target that already holds its own per-conduit instance of the spell
     (it borrowed and melded it): does the move drop the target's own instance undisposed?
  l1 a lesser of the borrower melds a per-conduit SpellContract consumer; the lender severs, links and grants again:
     does the lesser keep its consumer, and is it served again?
  l2 the same, but the first lender is torn down and a second lender provides the spell: does the lesser serve the
     consumer built over the first lender's disposed resource?

Run (from a tree root that has src/ and tests/):  PYTHONPATH=src:. python probe_d3_move_and_lesser.py
"""
import sys
from typing import Any, Callable, Dict, List, Tuple

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration


class Closable:
    """Base of every probe object: `close` is the declared disposal method and `closes` counts Melder's calls."""

    def __init__(self) -> None:
        self.closes = 0

    def close(self) -> None:
        self.closes += 1


class M1Holder(Closable):
    """`unique_per_conduit` spell owned by the source, borrowed and melded by the target (m1)."""


class LResource(Closable):
    """`unique` spell owned by a lender and granted to the borrower (l1, l2)."""


class LConsumer(Closable):
    """`unique_per_conduit` SpellContract consumer bound on the borrower (l1, l2)."""

    def __init__(self, dep=SpellContract(spell=LResource)) -> None:
        super().__init__()
        self.dep = dep


def reset_world() -> None:
    """Fresh Aether, as the component tests do."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def dynamic_configuration(frame: str) -> SpellbookConfiguration:
    """A dynamic configuration for one frame with one phase worker."""
    configuration = SpellbookConfiguration(aether_frame=frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def attempt(action: Callable[[], Any]) -> Tuple[bool, Any]:
    """Run one action; return (True, value) or (False, 'ExceptionType: message')."""
    try:
        return True, action()
    except BaseException as error:  # the probe reports every outcome, including ExceptionGroup
        return False, f"{type(error).__name__}: {str(error).splitlines()[0][:140] if str(error) else ''}"


def stored(conduit: Conduit, spell_id: str) -> Any:
    """What one conduit's own store holds under a spell id (None when absent or the store is gone)."""
    try:
        return conduit._creations._creations.get(spell_id)
    except AttributeError:
        return None


def bind(book: Spellbook, spell: type, existence: Existence) -> str:
    """Bind one probe class with its `close` disposal method."""
    return book.bind(spell=spell, existence=existence, permissions="create", disposal_method_names=["close"])


def grant(borrower: Conduit, lender: Conduit, spell_id: str) -> Any:
    """Link the lender to the borrower and grant one of the lender's spells; return the contract check."""
    lender.link(borrower)
    with borrower.transaction("link", conduits=[borrower, lender]):
        borrower.add_spell_to_contract(spell_id=spell_id, conduit=lender, permissions="create")
    return borrower.validate_contracts_and_define()


def case_m1() -> Dict[str, Any]:
    """Move a per-conduit spell into a target that already holds its own instance of it."""
    frame = "d3-m1"
    source_book = Spellbook(aetheric_frame=frame, configuration=dynamic_configuration(frame))
    holder_id = bind(source_book, M1Holder, Existence.unique_per_conduit)
    source = source_book.conjure(dynamic=True, name="d3-m1-source")
    target = Spellbook(aetheric_frame=frame).conjure(dynamic=True, name="d3-m1-target")
    out: Dict[str, Any] = {}
    try:
        out["setup_grant"] = bool(grant(target, source, holder_id))
        target_own = target.meld(spell_id=holder_id)
        source_own = source.meld(spell_id=holder_id)
        out["setup_distinct_instances"] = target_own is not source_own
        out["setup_target_store_holds_its_own"] = stored(target, holder_id) is target_own
        ok, value = attempt(lambda: source.transfer_spell_ownership(
            spell=holder_id, target_conduit=target, move_creations=True))
        out["transfer"] = "ok" if ok else value
        out["after_target_store_holds"] = (
            "source's" if stored(target, holder_id) is source_own else
            "its own" if stored(target, holder_id) is target_own else repr(stored(target, holder_id)))
        out["after_target_own_closes"] = target_own.closes
        out["after_source_own_closes"] = source_own.closes
        ok, value = attempt(lambda: target.meld(spell_id=holder_id))
        out["after_target_meld"] = ("source's" if ok and value is source_own else
                                    "its own" if ok and value is target_own else
                                    "new" if ok else value)
    finally:
        attempt(source.cleanup)
        attempt(target.cleanup)
    out["final_target_own_closes"] = target_own.closes
    out["final_source_own_closes"] = source_own.closes
    return out


def case_l1() -> Dict[str, Any]:
    """A lesser's consumer when the lender severs, then links and grants again."""
    frame = "d3-l1"
    lender_book = Spellbook(aetheric_frame=frame, configuration=dynamic_configuration(frame))
    resource_id = bind(lender_book, LResource, Existence.unique)
    lender = lender_book.conjure(dynamic=True, name="d3-l1-lender")
    borrower_book = Spellbook(aetheric_frame=frame)
    consumer_id = bind(borrower_book, LConsumer, Existence.unique_per_conduit)
    borrower = borrower_book.conjure(dynamic=True, name="d3-l1-borrower")
    out: Dict[str, Any] = {}
    lesser = None
    try:
        out["setup_grant"] = bool(grant(borrower, lender, resource_id))
        lesser = borrower.create_lesser_conduit()
        in_lesser = lesser.meld(spell_id=consumer_id)
        in_root = borrower.meld(spell_id=consumer_id)
        out["setup_lesser_store_holds_it"] = stored(lesser, consumer_id) is in_lesser
        out["setup_distinct"] = in_lesser is not in_root
        ok, value = attempt(lambda: lender.sever_link(borrower))
        out["sever"] = "ok" if ok else value
        out["after_sever_root_store_holds_it"] = stored(borrower, consumer_id) is in_root
        out["after_sever_lesser_store_holds_it"] = stored(lesser, consumer_id) is in_lesser
        out["after_sever_closes_root_lesser"] = (in_root.closes, in_lesser.closes)
        ok, value = attempt(lambda: grant(borrower, lender, resource_id))
        out["regrant"] = "ok" if ok else value
        ok, value = attempt(lambda: lesser.meld(spell_id=consumer_id))
        out["after_regrant_lesser_meld"] = "same consumer" if ok and value is in_lesser else (
            "new consumer" if ok else value)
    finally:
        if lesser is not None:
            attempt(lesser.cleanup)
        attempt(borrower.cleanup)
        attempt(lender.cleanup)
    out["final_closes_root_lesser"] = (in_root.closes, in_lesser.closes)
    return out


def case_l2() -> Dict[str, Any]:
    """A lesser's consumer when its lender is torn down and a second lender provides the spell."""
    frame = "d3-l2"
    first_book = Spellbook(aetheric_frame=frame, configuration=dynamic_configuration(frame))
    resource_id = bind(first_book, LResource, Existence.unique)
    first = first_book.conjure(dynamic=True, name="d3-l2-first")
    borrower_book = Spellbook(aetheric_frame=frame)
    consumer_id = bind(borrower_book, LConsumer, Existence.unique_per_conduit)
    borrower = borrower_book.conjure(dynamic=True, name="d3-l2-borrower")
    out: Dict[str, Any] = {}
    lesser = None
    second = None
    try:
        out["setup_grant"] = bool(grant(borrower, first, resource_id))
        lesser = borrower.create_lesser_conduit()
        in_lesser = lesser.meld(spell_id=consumer_id)
        resource = in_lesser.dep
        first.cleanup()
        out["after_first_teardown_resource_closes"] = resource.closes
        out["after_first_teardown_lesser_store_holds_it"] = stored(lesser, consumer_id) is in_lesser
        second_book = Spellbook(aetheric_frame=frame)
        second_id = bind(second_book, LResource, Existence.unique)
        second = second_book.conjure(dynamic=True, name="d3-l2-second")
        ok, value = attempt(lambda: grant(borrower, second, second_id))
        out["second_grant"] = "ok" if ok else value
        ok, value = attempt(lambda: lesser.meld(spell_id=consumer_id))
        out["after_second_grant_lesser_meld"] = (
            "same consumer (dep closed)" if ok and value is in_lesser and value.dep.closes else
            "same consumer" if ok and value is in_lesser else "new consumer" if ok else value)
    finally:
        if lesser is not None:
            attempt(lesser.cleanup)
        attempt(borrower.cleanup)
        if second is not None:
            attempt(second.cleanup)
        attempt(first.cleanup)
    out["final_lesser_consumer_closes"] = in_lesser.closes
    return out


CASES: List[Tuple[str, Callable[[], Dict[str, Any]]]] = [
    ("m1", case_m1),
    ("l1", case_l1),
    ("l2", case_l2),
]


def main() -> int:
    """Run the selected cases (all when none is named) and print one line per observation."""
    wanted = set(sys.argv[1:])
    for name, case in CASES:
        if wanted and name not in wanted:
            continue
        reset_world()
        ok, value = attempt(case)
        if not ok:
            print(f"{name}.ERROR = {value}")
            continue
        for key, observed in value.items():
            print(f"{name}.{key} = {observed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
