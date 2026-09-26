"""Time warm plain melds on the current tree (run from a tree root, PYTHONPATH=src:.).

Cases: the benchmark's solo root (existing object, `Existence.unique`), a class bound `Existence.unique` (warm
reuse) and a class bound `Existence.many` (construct each call). `conduit.meld(spell_id=...)` on the main thread
and on a worker thread (objects built by the main thread); median of 7 x 200k calls, ns.
"""
import statistics, sys, threading, time, warnings
warnings.simplefilter("ignore")
from benchmarks.testing_other_di import test_overrides_all as bench
from melder import Aether, Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


def per_call_ns(fn, n=200000):
    samples = []
    for _ in range(7):
        s = time.perf_counter_ns()
        for _ in range(n):
            fn()
        samples.append((time.perf_counter_ns() - s) / n)
    return statistics.median(samples)


def in_worker(fn):
    out = []
    t = threading.Thread(target=lambda: out.append(per_call_ns(fn)))
    t.start()
    t.join()
    return out[0]


class Plain:
    def __init__(self) -> None:
        self.value = 0


def report(label, fn):
    fn()
    print(f"  {label:22} main {per_call_ns(fn):7.1f} ns | worker {in_worker(fn):7.1f} ns")


print(f"python {sys.version.split()[0]} gil={sys._is_gil_enabled()}")
spec = {g.name: g for g in bench._override_graphs()}["solo"]
ops = bench._build_override_melder(spec)
report("solo (existing object)", ops.get_root)
ops.cleanup()

Aether._reset_singleton_for_tests()
aether = Aether()
Spellbook._aether = aether
Conduit._aether = aether
spellbook = Spellbook(aetheric_frame="timing")
spellbook.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
unique_id = spellbook.bind(spell=Plain, existence=Existence.unique, permissions="create")
conduit = spellbook.conjure(name="timing")
report("class unique (reuse)", lambda: conduit.meld(spell_id=unique_id))
conduit.cleanup()

Aether._reset_singleton_for_tests()
aether = Aether()
Spellbook._aether = aether
Conduit._aether = aether
spellbook = Spellbook(aetheric_frame="timing")
spellbook.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
many_id = spellbook.bind(spell=Plain, existence=Existence.many, permissions="create")
conduit = spellbook.conjure(name="timing")
report("class many (construct)", lambda: conduit.meld(spell_id=many_id))
conduit.cleanup()
