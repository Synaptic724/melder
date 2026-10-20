"""
Design-phase probe for TASK-2026-10-15-make_meld_state_checks_follow_spell_state (melder_1, 2026-10-15).

Read-only on src/: every change below is a monkeypatch in this process. Run from the repository root with PYTHONPATH=src.
Part 1 - an automatic world with a Protocol definition bound resolvable=False: does it pin the Book's validation flag
  and take melds off the fast door? Measured as is, and with RiskManager emulating the proposed exclusion.
Part 2 - a SpellContract consumer in a borrower Book, its provider index-linked from a lender: after the lender
  notches the provider, which version does the consumer get - with the meld's contract scan live (today), and with
  the scan removed (state only)?
"""
import inspect
import sys
import time
from typing import Any, Callable, Dict, Optional, Protocol, runtime_checkable

from melder import Aether, Conduit
from melder.aether.aetheric_frame.dev_ops.risk_manager.risk_manager import RiskManager
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.meld import Meld
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Svc:
    """A `unique` dependency."""

    def __init__(self) -> None:
        self.ready = True


class Task:
    """A `many` consumer with one injected service and plain defaults."""

    def __init__(self, svc: Svc, name: str = "task", payload: Optional[Dict[str, Any]] = None) -> None:
        self.svc = svc
        self.name = name
        self.payload = payload


class IThing(Protocol):
    """A descriptive Protocol definition, bound resolvable=False."""

    def run(self) -> None:
        ...


@runtime_checkable
class IService(Protocol):
    """The contract a lender provides."""

    def ping(self) -> str:
        ...


class ImplA:
    """First version of the lent service."""

    def ping(self) -> str:
        return "A"


class ImplB:
    """Second version of the lent service."""

    def ping(self) -> str:
        return "B"


class Consumer:
    """Borrower-side consumer of the contract."""

    def __init__(self, service: IService = SpellContract(spellframe=IService, binding_name="svc")) -> None:
        self.service = service


COUNTS: Dict[str, int] = {"gate": 0, "check": 0}
ORIGINAL_GATE: Callable[..., Any] = Meld._ensure_lineage_resolvable
ORIGINAL_CHECK: Callable[..., Any] = Meld._check_contracts_and_force_revalidation
ORIGINAL_REGISTER: Callable[..., Any] = RiskManager.register_spell
ORIGINAL_UPDATE_STRUCTURAL: Callable[..., Any] = RiskManager._update_structural_risk
ORIGINAL_UPDATE_RESOLUTION: Callable[..., Any] = RiskManager._update_resolution_risk
OBSERVED: Dict[str, set] = {}


def counting_gate(self: Meld, spell: Any) -> None:
    """Count gate entries, then run the real gate."""
    COUNTS["gate"] += 1
    return ORIGINAL_GATE(self, spell)


def counting_check(self: Meld, spell: Any) -> None:
    """Count contract checks, then run the real one."""
    COUNTS["check"] += 1
    return ORIGINAL_CHECK(self, spell)


def removed_check(self: Meld, spell: Any) -> None:
    """Count contract checks and do nothing (the scan removed; state only)."""
    COUNTS["check"] += 1


def excluding_register(self: RiskManager, conduit_id: str, spell: Any) -> None:
    """Emulate the proposed exclusion: an active resolvable=False version holds no risk."""
    if spell is not None and not spell._cleaned and not spell._resolvable:
        lineage = spell.spell_index.id
        OBSERVED.setdefault(conduit_id, set()).add(lineage)
        ORIGINAL_REGISTER(self, conduit_id, spell)
        state = self._conduit_states.get(conduit_id)
        if state is not None:
            state.risky_structural.discard(lineage)
            state.risky_resolution.discard(lineage)
        self._refresh_spellbook_flag(conduit_id)
        return
    if spell is not None and not spell._cleaned:
        OBSERVED.get(conduit_id, set()).discard(spell.spell_index.id)
    ORIGINAL_REGISTER(self, conduit_id, spell)


def excluding_structural(self: RiskManager, conduit_id: str, lineage_id: str, validity: Any) -> None:
    """Ignore structural events for observed-only lineages."""
    if lineage_id in OBSERVED.get(conduit_id, ()):
        return
    ORIGINAL_UPDATE_STRUCTURAL(self, conduit_id, lineage_id, validity)


def excluding_resolution(self: RiskManager, conduit_id: str, lineage_key: str, validity: Any) -> None:
    """Ignore resolution events for observed-only lineages."""
    if lineage_key in OBSERVED.get(conduit_id, ()):
        return
    ORIGINAL_UPDATE_RESOLUTION(self, conduit_id, lineage_key, validity)


def set_exclusion(enabled: bool) -> None:
    """Install or remove the emulated exclusion."""
    OBSERVED.clear()
    RiskManager.register_spell = excluding_register if enabled else ORIGINAL_REGISTER
    RiskManager._update_structural_risk = excluding_structural if enabled else ORIGINAL_UPDATE_STRUCTURAL
    RiskManager._update_resolution_risk = excluding_resolution if enabled else ORIGINAL_UPDATE_RESOLUTION


def fresh_aether() -> None:
    """Install a fresh Aether for the next world."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def fresh_book(frame: str, dynamic: bool, configure: bool = True) -> Spellbook:
    """Return a Book on `frame`; the first Book of a frame sets its posture with caching off."""
    book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    if configure:
        book.configure_aether_frame(
            system_state="dynamic" if dynamic else "automatic",
            disposal=None,
            disposal_method_names=None,
            system_caching_enabled=False,
        )
    return book


def risk_view(book: Spellbook, conduit_id: str) -> str:
    """Name what holds the Book's validation flag up for this conduit."""
    names = {spell.spell_index.id: spell.spell_name for spell in list(book._spells.values())}
    manager = book._get_risk_manager()
    state = manager._conduit_states.get(conduit_id) if manager is not None else None
    if state is None:
        return "no risk bucket"
    structural = sorted(names.get(key, key) for key in state.risky_structural)
    resolution = sorted(names.get(key, key) for key in state.risky_resolution)
    return f"flag={book._spellbook_validation_required} risky_structural={structural} risky_resolution={resolution}"


def time_melds(meld: Callable[[], Any], rounds: int) -> str:
    """Return gate entries and contract checks per meld and microseconds per meld."""
    for _ in range(50):
        meld()
    COUNTS.update(gate=0, check=0)
    start = time.perf_counter()
    for _ in range(rounds):
        meld()
    elapsed = (time.perf_counter() - start) / rounds * 1e6
    return f"gate={COUNTS['gate'] / rounds:.2f} check={COUNTS['check'] / rounds:.2f} {elapsed:.1f} us per meld"


def part_one(rounds: int) -> None:
    """Automatic and dynamic worlds with a Protocol definition, as is and with the exclusion emulated."""
    for dynamic in (False, True):
        for exclusion in (False, True):
            fresh_aether()
            set_exclusion(exclusion)
            frame = f"p1_{'dyn' if dynamic else 'auto'}_{'excl' if exclusion else 'asis'}"
            book = fresh_book(frame, dynamic)
            book.bind(spell=Svc, existence="unique")
            book.bind(spell=Task, existence="many")
            book.bind(spell=IThing, existence="unique", resolvable=False)
            root = book.conjure(name=f"{frame}_root", dynamic=dynamic)
            root.meld(spell=Task)
            print(f"[{frame}] after conjure and one meld: {risk_view(book, root._id)}")
            print(f"  root.meld(Task): {time_melds(lambda: root.meld(spell=Task), rounds)}")
            root.cleanup()
    set_exclusion(False)


def part_two(check_live: bool) -> None:
    """A SpellContract consumer behind an index link, before and after the lender notches the provider."""
    fresh_aether()
    Meld._check_contracts_and_force_revalidation = counting_check if check_live else removed_check
    label = "scan live (today)" if check_live else "scan removed (state only)"
    frame = "p2_live" if check_live else "p2_state"
    lender_book = fresh_book(frame, True)
    borrower_book = fresh_book(frame, True, configure=False)
    id_a = lender_book.bind(spell=ImplA, spellframe=IService, binding_name="svc", existence=Existence.many,
                            permissions="create")
    consumer_id = borrower_book.bind(spell=Consumer, existence=Existence.many, permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    lender.link(borrower)
    index = lender_book.find_spell_by_id(id_a).spell_index
    with borrower.transaction("link", conduits=[borrower, lender]):
        assert borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
    borrower.validate_contracts_and_define()
    consumer = borrower_book.find_spell_by_id(consumer_id)
    first = borrower.meld(spell=Consumer)
    print(f"[{label}] before notch: consumer got {first.service.ping()}; {risk_view(borrower_book, borrower._id)}")
    print(f"  borrower.meld(Consumer): {time_melds(lambda: borrower.meld(spell=Consumer), 200)}")
    try:
        id_b = lender.bind_inactive(spell=ImplB, spell_index=index, spellframe=IService, binding_name="svc",
                                    existence=Existence.many, permissions="create")
    except Exception as exc:
        print(f"  bind_inactive under the same key refused: {type(exc).__name__}: {exc}")
        return
    lender.notch_spell(spell_index=index, spell=lender_book._inactive_spells[id_b])
    state = borrower_book._spell_system_states.get_by_index_id(consumer.spell_index.id)
    print(f"  after notch: consumer lineage {state.validity.name} {sorted(f.name for f in state.flags)}; "
          f"{risk_view(borrower_book, borrower._id)}")
    COUNTS.update(gate=0, check=0)
    try:
        second = borrower.meld(spell=Consumer)
        print(f"  first meld after notch: consumer got {second.service.ping()}; gate={COUNTS['gate']} "
              f"check={COUNTS['check']}; {risk_view(borrower_book, borrower._id)}")
        third = borrower.meld(spell=Consumer)
        print(f"  second meld after notch: consumer got {third.service.ping()}; {risk_view(borrower_book, borrower._id)}")
    except Exception as exc:
        print(f"  meld after notch raised {type(exc).__name__}: {str(exc)[:300]}")
    lender.notch_spell(spell_index=index, spell=lender_book._inactive_spells[id_a])
    COUNTS.update(gate=0, check=0)
    try:
        back = borrower.meld(spell=Consumer)
        print(f"  after notching back to A: consumer got {back.service.ping()}; gate={COUNTS['gate']} "
              f"check={COUNTS['check']}; {risk_view(borrower_book, borrower._id)}")
    except Exception as exc:
        print(f"  meld after notching back raised {type(exc).__name__}: {str(exc)[:300]}")
    Meld._check_contracts_and_force_revalidation = ORIGINAL_CHECK


def main() -> None:
    """Run both parts."""
    Meld._ensure_lineage_resolvable = counting_gate
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    print(f"python {sys.version.split()[0]} gil_enabled={sys._is_gil_enabled()} rounds={rounds}")
    part_one(rounds)
    part_two(check_live=True)
    part_two(check_live=False)


if __name__ == "__main__":
    main()
