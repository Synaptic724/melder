import sys, time, statistics, gc
sys.path.insert(0, ".")
from tests.experimentation.test_melder_creation_overrides_performance import MelderExperiment
from v2_prototype import SlotSwitch, V2Runtime
def avg(call, n=200000):
    gc.disable()
    best = []
    for _ in range(5):
        t = time.perf_counter_ns()
        for _ in range(n): call()
        best.append((time.perf_counter_ns() - t) / n)
    gc.enable()
    return statistics.median(best)
for graph in ("shallow", "wide"):
    w = MelderExperiment(); w.setup(graph, "automatic")
    try:
        cm = w.conduit._meld
        spell = cm._spell_id_pool.get(w.root_id) or cm._resolve_spell_by_id(w.root_id)
        spell._get_or_build_creation_context()
        rt = V2Runtime(spell); sw = SlotSwitch(spell, rt); sw.use("v2")
        inputs = w.cases["root_one_reused"][1]
        ov = dict(inputs); key = tuple(ov)
        public = w.cases["root_one_reused"][0]
        public(); disp = rt.dispatcher; plan = rt.plans[key]; normal = rt.normal
        pub_normal = w.cases["normal"][0]
        r = {
          "public normal (fast door)": avg(pub_normal),
          "v2 normal plan direct": avg(lambda: normal(cm)),
          "public override {a}": avg(public),
          "dispatcher direct": avg(lambda: disp(cm, ov)),
          "plan direct": avg(lambda: plan(cm, ov)),
          "tuple(ov)+get": avg(lambda: rt.plans.get(tuple(ov))),
        }
        for k, v in r.items(): print(f"{graph:8} {k:28} {v:7.1f} ns")
    finally:
        sw.use("current"); w.cleanup()
