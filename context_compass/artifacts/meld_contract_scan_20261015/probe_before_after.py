"""
Before/after probe for TASK-2026-10-15-make_meld_state_checks_follow_spell_state (melder_1, 2026-10-15).

Run it twice from /tmp with PYTHONPATH naming the tree under test:
  before: /tmp/cc_res/nonres/base/src - a copy of the real tree's src at 0.2.8246 (the change absent)
  after:  /tmp/cc_res/nonres/tree/src - the scratch tree with the change applied
Every frame is configured with system_caching_enabled=False, so no conjure cache is written, and the generated module
of probe classes lives under /tmp/cc_res/nonres/probes. Timing passes run unwrapped. Counting passes wrap
Meld._ensure_lineage_resolvable, RiskManager.register_conduit and RiskManager._refresh_spellbook_flag only to count and
time their calls; the wrappers change no behaviour.

Part 1 - microseconds per warm meld (median and min of R repeats of N melds):
  auto_plain, auto_definition, dyn_plain, dyn_definition: a `many` Task over a `unique` Svc, without and with a
  Protocol definition bound resolvable=False; auto_override: a consumer that gets a class definition's value by
  override; dyn_borrower_contract: a SpellContract consumer in a borrower Book behind an index link (the contract
  check, which this change leaves alone).
Part 2 - gate entries per meld and the Book flag for the same worlds.
Part 3 - conjure of an automatic Book with S resolvable spells and D definitions: conjure wall time, register_conduit
  time and the refreshes it makes.
Part 4 - a dynamic world with D definitions: late bind of a new class plus its first meld, then warm melds of an older
  spell; refreshes and their cost in a separate counting pass.
Usage: python probe_before_after.py <label> [spells] [late]; PROBE_PARTS (default 1234) picks the parts and
PROBE_CONJURE_REPEATS (default 3) the conjure repeats of part 3, PROBE_DEFINITIONS (default 0,20,100) the
definition counts of parts 3 and 4.
"""
import os
import statistics
import sys
import time
from typing import Any, Callable, Dict, List, Protocol, Tuple, runtime_checkable

PROBE_DIR = "/tmp/cc_res/nonres/probes"
DEFINITION_COUNTS = [int(value) for value in os.environ.get("PROBE_DEFINITIONS", "0,20,100").split(",")]
MAX_DEFINITIONS = max(DEFINITION_COUNTS)


def write_world_module(spells: int, definitions: int, late: int) -> None:
    """Write the generated module of probe classes (outside every tree) and put its folder first on sys.path."""
    lines: List[str] = ['"""Generated probe classes (melder_1, meld_state_gate probe)."""', "from typing import Protocol", ""]
    for i in range(spells):
        lines += [f"class C{i}:", f'    """Resolvable probe spell {i}."""', "", "    def __init__(self) -> None:",
                  f"        self.index = {i}", "", ""]
    for j in range(definitions):
        lines += [f"class P{j}(Protocol):", f'    """Probe definition {j}, bound resolvable=False."""', "",
                  f"    def run_{j}(self) -> None:", "        ...", "", ""]
    for k in range(late):
        lines += [f"class L{k}:", f'    """Late-bound probe spell {k}."""', "", "    def __init__(self) -> None:",
                  f"        self.index = {k}", "", ""]
    os.makedirs(PROBE_DIR, exist_ok=True)
    with open(os.path.join(PROBE_DIR, "probe_world_classes.py"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    if PROBE_DIR not in sys.path:
        sys.path.insert(0, PROBE_DIR)


SPELLS = int(sys.argv[2]) if len(sys.argv) > 2 else 200
LATE = int(sys.argv[3]) if len(sys.argv) > 3 else 30
write_world_module(SPELLS, MAX_DEFINITIONS, LATE)

import melder  # imported after the module write, so both trees see the same generated probe classes
import probe_world_classes as world
from melder import Aether, Conduit
from melder.aether.aetheric_frame.dev_ops.risk_manager.risk_manager import RiskManager
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
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
    """A `many` consumer of the service."""

    def __init__(self, svc: Svc) -> None:
        self.svc = svc


class IThing(Protocol):
    """A descriptive Protocol definition, bound resolvable=False."""

    def run(self) -> None:
        ...


class ShapeDefinition:
    """A class definition bound resolvable=False; its consumers get a shape by override."""

    def __init__(self, sides: int = 3) -> None:
        self.sides = sides


class Painter:
    """A consumer whose only provider is the definition."""

    def __init__(self, shape: ShapeDefinition) -> None:
        self.shape = shape


@runtime_checkable
class IService(Protocol):
    """The contract a lender provides."""

    def ping(self) -> str:
        ...


class ImplA:
    """The lent service."""

    def ping(self) -> str:
        return "A"


class Consumer:
    """Borrower-side consumer of the contract."""

    def __init__(self, service: IService = SpellContract(spellframe=IService, binding_name="svc")) -> None:
        self.service = service


ORIGINAL_GATE: Callable[..., Any] = Meld._ensure_lineage_resolvable
ORIGINAL_REGISTER_CONDUIT: Callable[..., Any] = RiskManager.register_conduit
ORIGINAL_REFRESH: Callable[..., Any] = RiskManager._refresh_spellbook_flag
CALLS: Dict[str, List[float]] = {"gate": [], "register_conduit": [], "refresh": []}


def counting_gate(self: Meld, spell: Any) -> None:
    """Count one gate entry, then run the real gate."""
    CALLS["gate"].append(0.0)
    return ORIGINAL_GATE(self, spell)


def timed_register_conduit(self: RiskManager, conduit_id: str, spellbook: Any) -> None:
    """Time one register_conduit call."""
    start = time.perf_counter()
    try:
        return ORIGINAL_REGISTER_CONDUIT(self, conduit_id, spellbook)
    finally:
        CALLS["register_conduit"].append((time.perf_counter() - start) * 1e6)


def timed_refresh(self: RiskManager, conduit_id: str) -> None:
    """Time one flag refresh."""
    start = time.perf_counter()
    try:
        return ORIGINAL_REFRESH(self, conduit_id)
    finally:
        CALLS["refresh"].append((time.perf_counter() - start) * 1e6)


def set_counting(enabled: bool) -> None:
    """Install or remove the counting wrappers and reset the counters."""
    for values in CALLS.values():
        values.clear()
    Meld._ensure_lineage_resolvable = counting_gate if enabled else ORIGINAL_GATE
    RiskManager.register_conduit = timed_register_conduit if enabled else ORIGINAL_REGISTER_CONDUIT
    RiskManager._refresh_spellbook_flag = timed_refresh if enabled else ORIGINAL_REFRESH


def fresh_aether() -> None:
    """Install a fresh Aether for the next world."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def fresh_book(frame: str, dynamic: bool, configure: bool = True) -> Spellbook:
    """A Book on `frame`; the first Book of a frame sets its posture with caching off."""
    book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    if configure:
        book.configure_aether_frame(
            system_state="dynamic" if dynamic else "automatic",
            disposal=None,
            disposal_method_names=None,
            system_caching_enabled=False,
        )
    return book


World = Tuple[Spellbook, Callable[[], Any], List[Any]]


def world_plain(dynamic: bool, definition: bool) -> World:
    """Svc, Task and, optionally, a Protocol definition."""
    frame = f"{'dyn' if dynamic else 'auto'}_{'definition' if definition else 'plain'}"
    book = fresh_book(frame, dynamic)
    book.bind(spell=Svc, existence="unique")
    book.bind(spell=Task, existence="many")
    if definition:
        book.bind(spell=IThing, existence="unique", resolvable=False)
    root = book.conjure(name=f"{frame}_root", dynamic=dynamic)
    root.meld(spell=Task)
    return book, (lambda: root.meld(spell=Task)), [root]


def world_override() -> World:
    """A consumer of a class definition, melded with the shape supplied by override."""
    book = fresh_book("auto_override", False)
    book.bind(spell=ShapeDefinition, existence="many", resolvable=False)
    book.bind(spell=Painter, existence="many")
    root = book.conjure(name="auto_override_root")
    shape = object()
    root.meld(spell=Painter, override={"shape": shape})
    return book, (lambda: root.meld(spell=Painter, override={"shape": shape})), [root]


def world_borrower() -> World:
    """A SpellContract consumer in a borrower Book; its provider is index-linked from a lender."""
    lender_book = fresh_book("dyn_borrower", True)
    borrower_book = fresh_book("dyn_borrower", True, configure=False)
    provider_id = lender_book.bind(spell=ImplA, spellframe=IService, binding_name="svc", existence=Existence.many,
                                   permissions="create")
    borrower_book.bind(spell=Consumer, existence=Existence.many, permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    lender.link(borrower)
    index = lender_book.find_spell_by_id(provider_id).spell_index
    with borrower.transaction("link", conduits=[borrower, lender]):
        assert borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
    borrower.validate_contracts_and_define()
    borrower.meld(spell=Consumer)
    return borrower_book, (lambda: borrower.meld(spell=Consumer)), [borrower, lender]


WORLDS: List[Tuple[str, Callable[[], World], int, int]] = [
    ("auto_plain", lambda: world_plain(False, False), 2000, 5),
    ("auto_definition", lambda: world_plain(False, True), 2000, 5),
    ("dyn_plain", lambda: world_plain(True, False), 2000, 5),
    ("dyn_definition", lambda: world_plain(True, True), 2000, 5),
    ("auto_override", world_override, 2000, 5),
    ("dyn_borrower_contract", world_borrower, 100, 3),
]


def close(roots: List[Any]) -> None:
    """Tear the world's roots down in order."""
    for root in roots:
        root.cleanup()


def part_one_and_two() -> None:
    """Microseconds per warm meld (unwrapped), then gate entries per meld (counting pass)."""
    for name, build, melds, repeats in WORLDS:
        fresh_aether()
        book, meld, roots = build()
        for _ in range(50):
            meld()
        samples: List[float] = []
        for _ in range(repeats):
            start = time.perf_counter()
            for _ in range(melds):
                meld()
            samples.append((time.perf_counter() - start) / melds * 1e6)
        flag = book._spellbook_validation_required
        set_counting(True)
        for _ in range(100):
            meld()
        gates = len(CALLS["gate"]) / 100
        set_counting(False)
        close(roots)
        print(f"P1 {name}: median {statistics.median(samples):.2f} us min {min(samples):.2f} us per meld "
              f"({repeats} x {melds}); P2 flag={flag} gate={gates:.2f} per meld")


def build_conjure_world(definitions: int, tag: str) -> Tuple[Spellbook, float, Any]:
    """Bind SPELLS resolvable spells and `definitions` definitions, conjure, return the Book, ms and root."""
    book = fresh_book(tag, False)
    for i in range(SPELLS):
        book.bind(spell=getattr(world, f"C{i}"), existence="many")
    for j in range(definitions):
        book.bind(spell=getattr(world, f"P{j}"), existence="unique", resolvable=False)
    start = time.perf_counter()
    root = book.conjure(name=f"{tag}_root")
    return book, (time.perf_counter() - start) * 1e3, root


def part_three(definition_counts: List[int], repeats: int) -> None:
    """Conjure time (unwrapped), then register_conduit time and refreshes (counting pass)."""
    for definitions in definition_counts:
        times: List[float] = []
        for r in range(repeats):
            fresh_aether()
            book, elapsed, root = build_conjure_world(definitions, f"conj_{definitions}_{r}")
            times.append(elapsed)
            flag = book._spellbook_validation_required
            root.cleanup()
        fresh_aether()
        set_counting(True)
        book, _, root = build_conjure_world(definitions, f"conj_{definitions}_count")
        register_us = sum(CALLS["register_conduit"])
        refreshes = len(CALLS["refresh"])
        refresh_us = sum(CALLS["refresh"])
        set_counting(False)
        root.cleanup()
        print(f"P3 conjure S={SPELLS} D={definitions}: median {statistics.median(times):.1f} ms min {min(times):.1f} ms "
              f"({repeats} runs) flag={flag}; register_conduit {register_us:.0f} us, {refreshes} refreshes "
              f"totalling {refresh_us:.0f} us")


def late_world(definitions: int, tag: str, base: int) -> Tuple[Spellbook, Any]:
    """A dynamic world with `base` resolvable spells (all melded once) and `definitions` definitions."""
    book = fresh_book(tag, True)
    for i in range(base):
        book.bind(spell=getattr(world, f"C{i}"), existence="many")
    for j in range(definitions):
        book.bind(spell=getattr(world, f"P{j}"), existence="unique", resolvable=False)
    root = book.conjure(name=f"{tag}_root", dynamic=True)
    for i in range(base):
        root.meld(spell=getattr(world, f"C{i}"))
    return book, root


def part_four(definition_counts: List[int], base: int) -> None:
    """Late bind plus first meld, then warm melds of C0 (unwrapped); refreshes per late class (counting pass)."""
    for definitions in definition_counts:
        fresh_aether()
        book, root = late_world(definitions, f"late_{definitions}", base)
        bind_and_first: List[float] = []
        warm: List[float] = []
        for k in range(LATE):
            late_class = getattr(world, f"L{k}")
            start = time.perf_counter()
            root.bind(spell=late_class, existence="many")
            root.meld(spell=late_class)
            bind_and_first.append((time.perf_counter() - start) * 1e6)
            start = time.perf_counter()
            for _ in range(200):
                root.meld(spell=world.C0)
            warm.append((time.perf_counter() - start) / 200 * 1e6)
        flag = book._spellbook_validation_required
        root.cleanup()
        fresh_aether()
        book, root = late_world(definitions, f"late_{definitions}_count", base)
        set_counting(True)
        for k in range(LATE):
            late_class = getattr(world, f"L{k}")
            root.bind(spell=late_class, existence="many")
            root.meld(spell=late_class)
        refreshes = list(CALLS["refresh"])
        set_counting(False)
        root.cleanup()
        print(f"P4 dynamic D={definitions}: late bind + first meld median {statistics.median(bind_and_first):.0f} us; "
              f"warm meld of C0 after it median {statistics.median(warm):.2f} us; flag={flag}; "
              f"{len(refreshes) / LATE:.1f} refreshes per late class, mean {statistics.mean(refreshes):.2f} us, "
              f"max {max(refreshes):.2f} us")


def main() -> None:
    """Label the tree under test and run the four parts."""
    label = sys.argv[1] if len(sys.argv) > 1 else "unlabelled"
    print(f"{label}: python {sys.version.split()[0]} gil_enabled={sys._is_gil_enabled()} "
          f"melder {melder.__version__} from {os.path.dirname(melder.__file__)}; "
          f"SpellState.non_resolvable present={'non_resolvable' in SpellState.__members__}")
    parts = os.environ.get("PROBE_PARTS", "1234")
    repeats = int(os.environ.get("PROBE_CONJURE_REPEATS", "3"))
    if "1" in parts or "2" in parts:
        part_one_and_two()
    if "3" in parts:
        part_three(DEFINITION_COUNTS, repeats)
    if "4" in parts:
        part_four(DEFINITION_COUNTS, 20)


if __name__ == "__main__":
    main()
