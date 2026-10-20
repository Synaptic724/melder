"""S5 warm lease-cycle benchmark: a managed meld or injection plus its release, against the existing meld shapes.

Arms, interleaved per round (each value is ns per cycle; a cycle is the meld and, for managed arms, the release of
the leased object through a bound `ReleaseManagedSpell().release`):
  A  managed direct           auto root: meld(spell=Worker) + release            (plan-constant pool read)
  B  many direct              auto root: meld(spell=Fresh)                       (a new object per meld)
  C  unique direct            auto root: meld(spell=Single)                      (the stored object)
  D  many holder of managed   auto root: meld(spell=Holder) + release(.worker)   (one lease injected)
  E  many holder of many      auto root: meld(spell=FreshHolder)                 (two constructions)
  F  managed direct, dynamic  dynamic root: meld(spell=DynWorker) + release      (per-creation pool read)
  G  many direct, dynamic     dynamic root: meld(spell=DynFresh)                 (a new object per meld)
Run from the tree root: PYTHONPATH=src:. python -X gil=0|1 probe_s5_warm_lease_cycle.py [cycles] [rounds]
"""
import statistics
import sys
import time

import melder
from melder import Existence, ReleaseManagedSpell, Spellbook
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration


class Worker:
    """A resetless managed class (automatic root)."""

    def __init__(self) -> None:
        self.value = 0


class DynWorker:
    """A resetless managed class (dynamic root)."""

    def __init__(self) -> None:
        self.value = 0


class DynFresh:
    """The dynamic shape bound `many`."""

    def __init__(self) -> None:
        self.value = 0


class Fresh:
    """The same shape bound `many`."""

    def __init__(self) -> None:
        self.value = 0


class Single:
    """The same shape bound `unique`."""

    def __init__(self) -> None:
        self.value = 0


class Holder:
    """A `many` holder of one managed Worker."""

    def __init__(self, worker: Worker) -> None:
        self.worker = worker


class FreshHolder:
    """A `many` holder of one `many` Fresh."""

    def __init__(self, fresh: Fresh) -> None:
        self.fresh = fresh


def _dynamic_book(frame: str) -> Spellbook:
    configuration = SpellbookConfiguration(aether_frame=frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    return Spellbook(aetheric_frame=frame, configuration=configuration)


def main() -> None:
    cycles = int(sys.argv[1]) if len(sys.argv) > 1 else 100_000
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    book = Spellbook()
    book.bind(spell=Worker, existence=Existence.managed_spell_quantity, permissions="create")
    book.bind(spell=Fresh, existence=Existence.many, permissions="create")
    book.bind(spell=Single, existence=Existence.unique, permissions="create")
    book.bind(spell=Holder, existence=Existence.many, permissions="create")
    book.bind(spell=FreshHolder, existence=Existence.many, permissions="create")
    root = book.conjure(name="lease_probe_auto")
    dyn_book = _dynamic_book("lease_probe_dynamic")
    dyn_book.bind(spell=DynWorker, existence=Existence.managed_spell_quantity, permissions="create")
    dyn_book.bind(spell=DynFresh, existence=Existence.many, permissions="create")
    dyn_root = dyn_book.conjure(dynamic=True, name="lease_probe_dyn")
    release = ReleaseManagedSpell().release
    meld = root.meld
    dyn_meld = dyn_root.meld

    def arm_a() -> float:
        start = time.perf_counter_ns()
        for _ in range(cycles):
            release(meld(spell=Worker))
        return (time.perf_counter_ns() - start) / cycles

    def arm_b() -> float:
        start = time.perf_counter_ns()
        for _ in range(cycles):
            meld(spell=Fresh)
        return (time.perf_counter_ns() - start) / cycles

    def arm_c() -> float:
        start = time.perf_counter_ns()
        for _ in range(cycles):
            meld(spell=Single)
        return (time.perf_counter_ns() - start) / cycles

    def arm_d() -> float:
        start = time.perf_counter_ns()
        for _ in range(cycles):
            release(meld(spell=Holder).worker)
        return (time.perf_counter_ns() - start) / cycles

    def arm_e() -> float:
        start = time.perf_counter_ns()
        for _ in range(cycles):
            meld(spell=FreshHolder)
        return (time.perf_counter_ns() - start) / cycles

    def arm_f() -> float:
        start = time.perf_counter_ns()
        for _ in range(cycles):
            release(dyn_meld(spell=DynWorker))
        return (time.perf_counter_ns() - start) / cycles

    def arm_g() -> float:
        start = time.perf_counter_ns()
        for _ in range(cycles):
            dyn_meld(spell=DynFresh)
        return (time.perf_counter_ns() - start) / cycles

    arms = {
        "A managed direct": arm_a, "B many direct": arm_b, "C unique direct": arm_c,
        "D many holder of managed": arm_d, "E many holder of many": arm_e, "F managed direct, dynamic": arm_f,
        "G many direct, dynamic": arm_g,
    }
    for arm in arms.values():
        arm()  # warm: first melds compile, pools fill
    results = {name: [] for name in arms}
    for _ in range(rounds):
        for name, arm in arms.items():
            results[name].append(arm())
    gil = "enabled" if sys._is_gil_enabled() else "disabled"
    print(f"python {sys.version.split()[0]} gil={gil} melder={melder.__version__} cycles={cycles} rounds={rounds}")
    for name, values in results.items():
        print(f"{name:28s} min {min(values):8.1f} ns  median {statistics.median(values):8.1f} ns")
    pools = ReleaseManagedSpell().describe(Worker) + ReleaseManagedSpell().describe(DynWorker)
    print("pools after the run:", [(row["spell_name"], row["count"], row["idle_count"]) for row in pools])
    dyn_root.cleanup()
    dyn_book.cleanup()
    root.cleanup()
    book.cleanup()


if __name__ == "__main__":
    main()
