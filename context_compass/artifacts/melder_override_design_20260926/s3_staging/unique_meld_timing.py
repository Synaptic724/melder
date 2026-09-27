"""One number per process: warm `conduit.meld(spell_id=...)` of a class bound Existence.unique, main thread.

Run from a tree root with PYTHONPATH=src:. Median of 9 x 200k calls, ns. Used for many alternating cross-tree samples.
"""
import statistics, time, warnings
warnings.simplefilter("ignore")
from melder import Aether, Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Plain:
    def __init__(self) -> None:
        self.value = 0


Aether._reset_singleton_for_tests()
aether = Aether()
Spellbook._aether = aether
Conduit._aether = aether
book = Spellbook(aetheric_frame="timing")
book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
sid = book.bind(spell=Plain, existence=Existence.unique, permissions="create")
conduit = book.conjure(name="timing")
conduit.meld(spell_id=sid)
samples = []
for _ in range(9):
    s = time.perf_counter_ns()
    for _ in range(200000):
        conduit.meld(spell_id=sid)
    samples.append((time.perf_counter_ns() - s) / 200000)
print(f"{statistics.median(samples):.1f}")
conduit.cleanup()
