"""
Item (c), unforced stress: nothing is patched or paused. One thread binds module-level classes into a Book of
frame-a while frames a and b exist (process-wide spell ids, the default, so every bind runs the cross-frame sweep).
Another thread onboards tenants: it constructs a Spellbook for a new frame (frame birth), and in mode "churn" it
then cleans that frame (frame detach), so the frame count stays small, as with tenants that come and go.

Usage: python c_unforced_stress.py <src copy> <dir holding gen_classes.py> <n binds> <mode: grow|churn> <max frames>
"""
import collections
import importlib
import sys
import threading
import time

src, gen_dir, n_classes, mode, max_frames = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], int(sys.argv[5])
sys.path.insert(0, src)
sys.path.insert(0, gen_dir)
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.existence.existence import Existence

gen = importlib.import_module("gen_classes")
classes = [getattr(gen, f"S{i}") for i in range(n_classes)]

Aether._reset_singleton_for_tests()
aether = Aether()
Spellbook._aether = aether
Conduit._aether = aether
book_a = Spellbook(aetheric_frame="frame-a")
book_b = Spellbook(aetheric_frame="frame-b")
assert aether.process_wide_unique_spell_ids

failures = collections.Counter()
done = threading.Event()
stats = {"births": 0, "detaches": 0}


def binder():
    for cls in classes:
        try:
            book_a.bind(spell=cls, existence=Existence.unique, permissions="create")
        except Exception as exc:
            failures[f"{type(exc).__name__}: {str(exc).splitlines()[0][:100]}"] += 1
    done.set()


def tenants():
    kept = []
    j = 0
    while not done.is_set() and j < max_frames:
        name = f"tenant-{j}"
        kept.append(Spellbook(aetheric_frame=name))
        stats["births"] += 1
        if mode == "churn":
            aether.get_frame(name).cleanup()
            stats["detaches"] += 1
        j += 1


t0 = time.perf_counter()
threads = [threading.Thread(target=binder), threading.Thread(target=tenants)]
for t in threads:
    t.start()
for t in threads:
    t.join()
elapsed = time.perf_counter() - t0
registered = len(book_a._spells)
print(f"mode={mode} gil={sys._is_gil_enabled()} binds={n_classes} registered={registered} "
      f"births={stats['births']} detaches={stats['detaches']} frames_now={len(aether._aetheric_frames)} "
      f"elapsed={elapsed:.2f}s")
print("bind failures:", dict(failures) if failures else "none")
