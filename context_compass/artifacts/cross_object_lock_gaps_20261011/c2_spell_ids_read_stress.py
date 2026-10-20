"""
Item (c2), unforced stress (nothing patched or paused): AethericFrame.spells_in_index copies each conjured Book's
live `_spell_ids` set element by element under the FRAME lock, while that Book adds to the set under its OWN lock.

One thread late-binds module-level classes into Book A, a dynamic Book conjured in frame-f, so A's `_spell_ids`
(registered by reference in the frame's cached-id registry) grows. The other thread reads the frame's ids:
  direct  - the public `aether.get_frame("frame-f").spells_in_index()` in a loop;
  conjure - a new dynamic Book in frame-f binds one class and conjures; conjure's preflight
            (`Spellbook._spell_id_integrity_checker` -> `Aether._get_all_spell_ids`) reads the same ids.

Usage (run make_gen_classes_t.py once first; it writes gen_classes_t.py beside it):
       python c2_spell_ids_read_stress.py <src copy> <tests dir> <dir of gen_classes.py> <dir of gen_classes_t.py>
       <direct|conjure> <n late binds>
"""
import collections
import importlib
import sys
import threading
import time
import traceback

src, tests_dir, gen_dir, gen_t_dir, mode, n_binds = sys.argv[1:6] + [int(sys.argv[6])]
for path in (src, tests_dir, gen_dir, gen_t_dir):
    sys.path.insert(0, path)
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from _frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration

gen = importlib.import_module("gen_classes")
gen_t = importlib.import_module("gen_classes_t")
Aether._reset_singleton_for_tests()
aether = Aether()
Spellbook._aether = aether
Conduit._aether = aether


def make_book() -> Spellbook:
    config = SpellbookConfiguration(aether_frame="frame-f")
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(aetheric_frame="frame-f", configuration=config)


book_a = make_book()
for i in range(50):
    book_a.bind(spell=getattr(gen, f"S{i}"), existence=Existence.unique, permissions="create")
root_a = book_a.conjure(name="root-a", dynamic=True)
frame = aether.get_frame("frame-f")

failures = collections.Counter()
reads = {"n": 0}
bind_failures = collections.Counter()
done = threading.Event()


def binder() -> None:
    for i in range(50, 50 + n_binds):
        try:
            book_a.bind(spell=getattr(gen, f"S{i}"), existence=Existence.unique, permissions="create")
        except Exception as exc:
            bind_failures[f"{type(exc).__name__}: {str(exc).splitlines()[0][:90]}"] += 1
    done.set()


def reader() -> None:
    j = 0
    while not done.is_set():
        try:
            if mode == "direct":
                frame.spells_in_index()
            else:
                book_c = make_book()
                book_c.bind(spell=getattr(gen_t, f"T{j}"), existence=Existence.unique, permissions="create")
                book_c.conjure(name=f"c-{j}", dynamic=True)
        except Exception as exc:
            where = traceback.extract_tb(exc.__traceback__)[-1].name
            failures[f"{type(exc).__name__} in {where}: {str(exc).splitlines()[0][:90]}"] += 1
        reads["n"] += 1
        j += 1


t0 = time.perf_counter()
threads = [threading.Thread(target=binder), threading.Thread(target=reader)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"mode={mode} gil={sys._is_gil_enabled()} late_binds={n_binds} a_ids={len(book_a._spell_ids)} "
      f"reads={reads['n']} elapsed={time.perf_counter() - t0:.2f}s")
print("read failures:", dict(failures) if failures else "none")
print("bind failures:", dict(bind_failures) if bind_failures else "none")
