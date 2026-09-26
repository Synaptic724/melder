import sys, time, statistics
sys.path.insert(0, ".")
from tests.experimentation.test_melder_creation_overrides_performance import MelderExperiment
from v2_prototype import SiteGraph, PlanCompiler
for graph in ("shallow", "wide", "diamond", "deep"):
    w = MelderExperiment(); w.setup(graph, "automatic")
    try:
        meld = w.conduit._meld
        spell = meld._spell_id_pool.get(w.root_id) or meld._resolve_spell_by_id(w.root_id)
        spell._get_or_build_creation_context()
        g_t, c0_t, c1_t = [], [], []
        key = next(iter(w.cases["root_one_reused"][1]))
        for _ in range(5):
            t0 = time.perf_counter(); g = SiteGraph(spell); t1 = time.perf_counter()
            c = PlanCompiler(g); c.compile((), 0); t2 = time.perf_counter()
            c.compile((key,), 0); t3 = time.perf_counter()
            g_t.append(t1 - t0); c0_t.append(t2 - t1); c1_t.append(t3 - t2)
        src = c.sources[((), 0)]
        print(f"{graph:8} sites={len(g.sites):4} graph={1e3*statistics.median(g_t):7.2f} ms  normal_plan={1e3*statistics.median(c0_t):7.2f} ms  key_plan={1e3*statistics.median(c1_t):7.2f} ms  normal_src_lines={src.count(chr(10))}")
    finally:
        w.cleanup()
