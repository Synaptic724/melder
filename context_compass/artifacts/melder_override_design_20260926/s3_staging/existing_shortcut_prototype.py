"""Size the existing-object shortcut (run from a tree root, PYTHONPATH=src:.).

today: public conduit.meld (current tree: Conduit-level fast arm calling the existing-object door).
V3: the same guards, then `door_spell.user_created_object` returned without the door call.
Main thread and worker thread, median of 7 x 200k calls, ns; V3 must return the same object.
"""
import statistics, sys, threading, time, warnings
warnings.simplefilter("ignore")
from benchmarks.testing_other_di import test_overrides_all as bench


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


def v3(conduit, spell_id):
    if conduit._cleaned:
        conduit.check_cleaned()
    meld_component = conduit._meld
    entry = meld_component._fast_meld_doors.get(spell_id)
    if entry is not None:
        door_spell, captured_context, captured_epoch = entry
        if (
            not meld_component._meld_hooks
            and door_spell._door_epoch == captured_epoch
            and door_spell._creation_context is captured_context
            and not meld_component._spellbook._spellbook_validation_required
        ):
            existing = door_spell.user_created_object
            if existing is not None:
                spellbook = meld_component._spellbook
                if spellbook._cache_emit_required:
                    spellbook._emit_cache_file_if_required()
                return existing
    return conduit.meld(spell_id=spell_id)


spec = {g.name: g for g in bench._override_graphs()}["solo"]
ops = bench._build_override_melder(spec)
cells = [c.cell_contents for c in ops.get_root.__closure__]
conduit = [c for c in cells if type(c).__name__ == "Conduit"][0]
root_id = [c for c in cells if isinstance(c, str)][0]
reference = conduit.meld(spell_id=root_id)
assert v3(conduit, root_id) is reference
today = lambda: conduit.meld(spell_id=root_id)
shortcut = lambda: v3(conduit, root_id)
print(f"python {sys.version.split()[0]} gil={sys._is_gil_enabled()} solo: "
      f"today main {per_call_ns(today):6.1f} worker {in_worker(today):6.1f} | "
      f"V3 main {per_call_ns(shortcut):6.1f} worker {in_worker(shortcut):6.1f}")
ops.cleanup()
