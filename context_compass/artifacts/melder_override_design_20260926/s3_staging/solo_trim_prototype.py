"""Size two trims of the public solo meld path before editing Conduit.meld (run from a tree root, PYTHONPATH=src:.).

V1: inline cleaned check + positional call into ConduitMeld's id fast lane (no keyword marshaling).
V2: V1 plus the fast-door entry read inlined at the Conduit (saves the ConduitMeld frame on a hit).
Median of 7 x 300k calls, ns; results must be the same object as conduit.meld's.
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


def v1(conduit, spell_id):
    if conduit._cleaned:
        conduit.check_cleaned()
    meld_component = conduit._meld
    if not conduit.__dynamic_environment__:
        return meld_component.meld(spell_id)
    raise AssertionError("prototype covers automatic conduits only")


def v2(conduit, spell_id):
    if conduit._cleaned:
        conduit.check_cleaned()
    meld_component = conduit._meld
    if not conduit.__dynamic_environment__:
        entry = meld_component._fast_meld_doors.get(spell_id)
        if entry is not None:
            door_spell, captured_context, captured_epoch = entry
            spellbook = meld_component._spellbook
            if (
                not meld_component._meld_hooks
                and door_spell._door_epoch == captured_epoch
                and door_spell._creation_context is captured_context
                and not spellbook._spellbook_validation_required
            ):
                instance = captured_context._no_overrides_instance_executor(meld_component)
                if spellbook._cache_emit_required:
                    spellbook._emit_cache_file_if_required()
                return instance
        return meld_component.meld(spell_id)
    raise AssertionError("prototype covers automatic conduits only")


print(f"python {sys.version.split()[0]} gil={sys._is_gil_enabled()}")
for graph in ("solo", "shallow"):
    spec = {g.name: g for g in bench._override_graphs()}[graph]
    ops = bench._build_override_melder(spec)
    cells = [c.cell_contents for c in ops.get_root.__closure__]
    conduit = [c for c in cells if type(c).__name__ == "Conduit"][0]
    root_id = [c for c in cells if isinstance(c, str)][0]
    reference = conduit.meld(spell_id=root_id)
    if graph == "solo":
        assert v1(conduit, root_id) is reference and v2(conduit, root_id) is reference
    rows = {
        "today conduit.meld": per_call_ns(lambda: conduit.meld(spell_id=root_id)),
        "V1": per_call_ns(lambda: v1(conduit, root_id)),
        "V2": per_call_ns(lambda: v2(conduit, root_id)),
    }
    print(f"{graph:8} (plain meld) " + " | ".join(f"{k} {v:6.1f}" for k, v in rows.items()))
    ops.cleanup()
