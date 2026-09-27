"""Which objects does one Melder scope cycle leave as cyclic garbage? (sandbox diagnostic)"""
import collections, gc, sys
sys.path.insert(0, "/home/claude/work/melder")
sys.path.insert(0, "/home/claude/work/melder/src")
sys.path.insert(0, "/home/claude/work/melder/benchmarks/testing_other_di")
import test_real_world_gauntlet as g
ops = g._build_ops("melder"); ops.spawn_singletons()
calls = [ops.request_scope_cycle, ops.worker_a_scope_cycle, ops.worker_b_scope_cycle]
for i in range(300):  # warm
    calls[i % 3](i % 3)
gc.collect()
gc.disable()
gc.set_debug(gc.DEBUG_SAVEALL)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
for i in range(N):
    calls[i % 3](i % 3)
found = gc.collect()
c = collections.Counter(f"{type(o).__module__}.{type(o).__qualname__}" for o in gc.garbage)
print(f"cycles run={N} unreachable(cyclic) objects={found} per_cycle={found/N:.2f}")
for k, v in c.most_common(25):
    print(f"  {v:8d}  {v/N:6.2f}/cycle  {k}")
gc.set_debug(0); gc.garbage.clear(); gc.enable()
ops.cleanup()
