"""Per-layer cost of the solo plain meld (bound existing object, Existence.unique) - owner benchmark setup.

Run from a tree root with PYTHONPATH=src:. Median of 7 x 300k direct calls per layer, ns.
"""
import statistics, sys, time, warnings
warnings.simplefilter("ignore")
from benchmarks.testing_other_di import test_overrides_all as bench


def per_call_ns(fn, n=300000):
    samples = []
    for _ in range(7):
        s = time.perf_counter_ns()
        for _ in range(n):
            fn()
        samples.append((time.perf_counter_ns() - s) / n)
    return statistics.median(samples)


spec = {g.name: g for g in bench._override_graphs()}["solo"]
ops = bench._build_override_melder(spec)
ops.get_root()
conduit = ops.get_root.__closure__ and [c.cell_contents for c in ops.get_root.__closure__
                                        if type(c.cell_contents).__name__ == "Conduit"][0]
root_id = [c.cell_contents for c in ops.get_root.__closure__ if isinstance(c.cell_contents, str)][0]
meld = conduit._meld
spell = meld._spell_id_pool[root_id]
ctx = spell._creation_context
door = ctx._no_overrides_instance_executor
obj = door(meld)
print(f"python {sys.version.split()[0]} gil={sys._is_gil_enabled()}")
rows = {
    "floor: lambda": per_call_ns(lambda: None),
    "benchmark get_root": per_call_ns(ops.get_root),
    "conduit.meld(spell_id=)": per_call_ns(lambda: conduit.meld(spell_id=root_id)),
    "ConduitMeld.meld(id)": per_call_ns(lambda: meld.meld(root_id)),
    "existing door": per_call_ns(lambda: door(meld)),
}
print(" | ".join(f"{k} {v:6.1f}" for k, v in rows.items()))
ops.cleanup()
