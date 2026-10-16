"""
Probe: when does a meld enter Meld._ensure_lineage_resolvable, and how often does it scan SpellContract defaults?

TASK-2026-10-15-trace_meld_contract_scan_gate (melder_1). Read-only on src/: it patches counters onto the Meld class
in this process only. Run from the repository root with PYTHONPATH=src. Each scenario starts a fresh Aether, binds,
conjures, reads the Spellbook's validation flag and the RiskManager's risky sets for the root conduit, then melds and
counts gate entries, contract scans and inspect.signature calls, and times the meld with the scan live and stubbed.
"""
import inspect
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Protocol

from melder import Aether, Conduit
from melder.aether.conduit.meld.meld import Meld
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook


class Svc:
    """A `unique` dependency."""

    def __init__(self) -> None:
        self.ready = True


class Task:
    """A `many` consumer shaped like a request object: one injected service, plain defaults."""

    def __init__(self, svc: Svc, name: str = "task", payload: Optional[Dict[str, Any]] = None, retries: int = 3) -> None:
        self.svc = svc
        self.name = name
        self.payload = payload
        self.retries = retries


class Other:
    """A spell bound late on the root and never melded."""

    def __init__(self) -> None:
        self.value = 1


class IThing(Protocol):
    """A descriptive Protocol definition (bound resolvable=False)."""

    def run(self) -> None:
        ...


COUNTS: Dict[str, int] = {"gate": 0, "scan": 0, "signature": 0}
ORIGINAL_SCAN: Callable[..., Any] = Meld.__dict__["_iter_spell_contract_defaults"].__func__
ORIGINAL_GATE: Callable[..., Any] = Meld._ensure_lineage_resolvable
ORIGINAL_SIGNATURE: Callable[..., Any] = inspect.signature


def counting_scan(spell: Any) -> Any:
    """Count contract scans, then run the real one."""
    COUNTS["scan"] += 1
    return ORIGINAL_SCAN(spell)


def stub_scan(spell: Any) -> List[Any]:
    """Count contract scans and return no contracts without inspecting anything."""
    COUNTS["scan"] += 1
    return []


def counting_gate(self: Meld, spell: Any) -> None:
    """Count gate entries, then run the real gate."""
    COUNTS["gate"] += 1
    return ORIGINAL_GATE(self, spell)


def counting_signature(obj: Any, *args: Any, **kwargs: Any) -> Any:
    """Count inspect.signature calls, then run the real one."""
    COUNTS["signature"] += 1
    return ORIGINAL_SIGNATURE(obj, *args, **kwargs)


def fresh_book(frame: str, dynamic: bool) -> Spellbook:
    """Return a Book on a fresh Aether with caching off."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    book.configure_aether_frame(
        system_state="dynamic" if dynamic else "automatic",
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=False,
    )
    return book


def risk_view(book: Spellbook, conduit_id: str) -> str:
    """Name the lineages that hold the Book's validation flag up for this conduit."""
    names = {}
    for spell in list(book._spells.values()):
        names[spell.spell_index.id] = spell.spell_name
    manager = book._get_risk_manager()
    state = manager._conduit_states.get(conduit_id) if manager is not None else None
    if state is None:
        return "no risk bucket for the root"
    structural = sorted(names.get(key, key) for key in state.risky_structural)
    resolution = sorted(names.get(key, key) for key in state.risky_resolution)
    return f"risky_structural={structural} risky_resolution={resolution}"


def measure(label: str, meld: Callable[[], Any], rounds: int) -> str:
    """Meld `rounds` times with the live scan, then with the scan stubbed; report counts and microseconds."""
    for _ in range(50):
        meld()
    Meld._iter_spell_contract_defaults = staticmethod(counting_scan)
    COUNTS.update(gate=0, scan=0, signature=0)
    inspect.signature = counting_signature
    start = time.perf_counter()
    for _ in range(rounds):
        meld()
    live = (time.perf_counter() - start) / rounds * 1e6
    inspect.signature = ORIGINAL_SIGNATURE
    live_counts = dict(COUNTS)
    Meld._iter_spell_contract_defaults = staticmethod(stub_scan)
    start = time.perf_counter()
    for _ in range(rounds):
        meld()
    stubbed = (time.perf_counter() - start) / rounds * 1e6
    Meld._iter_spell_contract_defaults = staticmethod(counting_scan)
    per = {key: round(value / rounds, 2) for key, value in live_counts.items()}
    return (f"  {label}: per meld gate={per['gate']} scan={per['scan']} signature={per['signature']}; "
            f"{live:.1f} us live, {stubbed:.1f} us with the scan stubbed")


def scenario(name: str, dynamic: bool, protocol: bool, late_bind: bool, lesser: bool, rounds: int) -> None:
    """Run one world and print what holds the gate open and what each meld pays."""
    frame = f"probe_{name}"
    book = fresh_book(frame, dynamic)
    book.bind(spell=Svc, existence="unique")
    book.bind(spell=Task, existence="many")
    if protocol:
        book.bind(spell=IThing, existence="unique", resolvable=False)
    root = book.conjure(name=f"{frame}_root", dynamic=dynamic)
    print(f"[{name}] dynamic={dynamic} protocol_def={protocol} late_bind={late_bind} lesser={lesser}")
    print(f"  after conjure: flag={book._spellbook_validation_required}; {risk_view(book, root._id)}")
    root.meld(spell=Task)
    print(f"  after first meld: flag={book._spellbook_validation_required}; {risk_view(book, root._id)}")
    if late_bind:
        root.bind(spell=Other, existence="many")
        print(f"  after late bind: flag={book._spellbook_validation_required}; {risk_view(book, root._id)}")
    print(measure("root.meld(Task)", lambda: root.meld(spell=Task), rounds))
    if lesser:
        child = root.create_lesser_conduit()
        print(measure("lesser.meld(Task)", lambda: child.meld(spell=Task), rounds))
        child.cleanup()
    print(f"  end: flag={book._spellbook_validation_required}")
    root.cleanup()


def main() -> None:
    """Run the scenarios."""
    Meld._ensure_lineage_resolvable = counting_gate
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    print(f"python {sys.version.split()[0]} gil_enabled={sys._is_gil_enabled()} rounds={rounds}")
    started = time.perf_counter()
    import annotationlib
    t0 = time.perf_counter()
    for _ in range(2000):
        ORIGINAL_SIGNATURE(Task, annotation_format=annotationlib.Format.FORWARDREF)
    print(f"inspect.signature(Task, FORWARDREF): {(time.perf_counter() - t0) / 2000 * 1e6:.1f} us per call")
    scenario("auto_plain", dynamic=False, protocol=False, late_bind=False, lesser=False, rounds=rounds)
    scenario("dyn_plain", dynamic=True, protocol=False, late_bind=False, lesser=True, rounds=rounds)
    scenario("dyn_protocol", dynamic=True, protocol=True, late_bind=False, lesser=False, rounds=rounds)
    scenario("dyn_late_bind", dynamic=True, protocol=False, late_bind=True, lesser=False, rounds=rounds)
    print(f"total {time.perf_counter() - started:.1f} s")


if __name__ == "__main__":
    main()
