"""
Single-threaded cost of the three calls 0.2.8232 changes, on one src tree (run it once per tree, interleaved).

Usage: python bench_0_2_8232.py <src tree> <tests dir> <dir of gen_classes.py> <rounds>
Prints the median and the minimum ns per call over `rounds` rounds for:
  find_contracted_spell  - a miss across 8 lending peers (walks all 8)
  inspect_spell          - a provider found after 20 other Books in the frame (stage 2)
  cleanup_spell          - disposing an owned active sole spell (bind outside the timed region)
"""
import importlib
import statistics
import sys
import time

src, tests_dir, gen_dir, rounds = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
for path in (src, tests_dir, gen_dir):
    sys.path.insert(0, path)
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from _frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration

gen = importlib.import_module("gen_classes")
Aether._reset_singleton_for_tests()
aether = Aether()
Spellbook._aether = aether
Conduit._aether = aether
next_class = iter(range(3000))


def dynamic_book(frame: str) -> Spellbook:
    config = SpellbookConfiguration(aether_frame=frame)
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(aetheric_frame=frame, configuration=config)


def conjured(frame: str, name: str):
    book = dynamic_book(frame)
    cls = getattr(gen, f"S{next(next_class)}")
    book.bind(spell=cls, existence=Existence.unique, permissions="create")
    return book, cls, book.conjure(name=name, dynamic=True)


def per_call_ns(call, n: int) -> float:
    start = time.perf_counter_ns()
    for _ in range(n):
        call()
    return (time.perf_counter_ns() - start) / n


_, _, owner = conjured("f", "owner")
for i in range(8):
    conjured("f", f"peer-{i}")[2].link(owner)
inspector_book, _, _ = conjured("g", "inspector")
for i in range(20):
    conjured("g", f"filler-{i}")
_, target_cls, _ = conjured("g", "provider")
dispose_book = dynamic_book("h")
dispose_root = dispose_book.conjure(name="disposer", dynamic=True)

results = {"find_contracted_spell": [], "inspect_spell": [], "cleanup_spell": []}
for _ in range(rounds):
    results["find_contracted_spell"].append(per_call_ns(lambda: owner.find_contracted_spell("no-such-version"), 20000))
    results["inspect_spell"].append(per_call_ns(lambda: inspector_book.inspect_spell(target_cls, "g"), 2000))
    spells = []
    for _ in range(50):
        spell_id = dispose_book.bind(spell=getattr(gen, f"S{next(next_class)}"), existence=Existence.unique,
                                     permissions="create")
        spells.append(dispose_book.find_spell_by_id(spell_id))
    start = time.perf_counter_ns()
    for spell in spells:
        dispose_root.cleanup_spell(spell=spell)
    results["cleanup_spell"].append((time.perf_counter_ns() - start) / len(spells))
print(f"tree={src} gil={sys._is_gil_enabled()} rounds={rounds}")
for name, samples in results.items():
    print(f"{name:22s} median={statistics.median(samples):10.0f} ns  min={min(samples):10.0f} ns")
