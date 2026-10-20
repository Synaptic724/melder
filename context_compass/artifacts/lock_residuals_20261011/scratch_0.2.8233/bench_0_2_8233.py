"""
Single-threaded cost of what 0.2.8233 touches, on one src tree (run it once per tree, interleaved).

Usage: python bench_0_2_8233.py <src tree> <tests dir> <dir of gen_classes.py> <rounds>
Prints the median and the minimum ns per operation over `rounds` rounds for:
  bind            - binding a fresh class into an unconjured Book (Spell construction stores one more slot)
  direct_cleanup  - a direct Spell.cleanup() of an owned active spell of a conjured root (the changed route)
  root_teardown   - root.cleanup() of a conjured root holding 50 spells, per spell (Book teardown cleans each spell)
  warm_meld       - a warm meld by id of a unique spell (the meld path, untouched; sanity row)
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
next_class = iter(range(6000))


def dynamic_book(frame: str) -> Spellbook:
    config = SpellbookConfiguration(aether_frame=frame)
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(aetheric_frame=frame, configuration=config)


def bind_fresh(book: Spellbook) -> str:
    return book.bind(spell=getattr(gen, f"S{next(next_class)}"), existence=Existence.unique, permissions="create")


warm_book = dynamic_book("warm")
warm_id = bind_fresh(warm_book)
warm_root = warm_book.conjure(name="warm", dynamic=True)
warm_root.meld(spell_id=warm_id)

results = {"bind": [], "direct_cleanup": [], "root_teardown": [], "warm_meld": []}
for r in range(rounds):
    book = dynamic_book(f"bind{r}")
    start = time.perf_counter_ns()
    for _ in range(100):
        bind_fresh(book)
    results["bind"].append((time.perf_counter_ns() - start) / 100)

    book = dynamic_book(f"direct{r}")
    ids = [bind_fresh(book) for _ in range(50)]
    book.conjure(name=f"direct{r}", dynamic=True)
    spells = [book.find_spell_by_id(spell_id) for spell_id in ids]
    start = time.perf_counter_ns()
    for spell in spells:
        spell.cleanup()
    results["direct_cleanup"].append((time.perf_counter_ns() - start) / len(spells))

    book = dynamic_book(f"teardown{r}")
    for _ in range(50):
        bind_fresh(book)
    root = book.conjure(name=f"teardown{r}", dynamic=True)
    start = time.perf_counter_ns()
    root.cleanup()
    results["root_teardown"].append((time.perf_counter_ns() - start) / 50)

    start = time.perf_counter_ns()
    for _ in range(20000):
        warm_root.meld(spell_id=warm_id)
    results["warm_meld"].append((time.perf_counter_ns() - start) / 20000)
print(f"tree={src} gil={sys._is_gil_enabled()} rounds={rounds}")
for name, samples in results.items():
    print(f"{name:16s} median={statistics.median(samples):10.0f} ns  min={min(samples):10.0f} ns")
