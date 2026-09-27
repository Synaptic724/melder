"""Measure the conjure-time cost of the (now unused) override lane: Phase-9 targeting, Phase-10 overrides plan,
and the many_only manifest override section. Run from a tree root with PYTHONPATH=src:."""
import statistics, sys, time
from collections import defaultdict
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_strategy_builder import (
    SpellArtifactProcessorStrategyBuilder,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.data import many_only_codegen_plan as mop
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.manifest import many_only_manifest as mm
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_codegen_creation_helpers import ManyOnlyCodegenCreationHelpers
from tests.experimentation.test_melder_creation_overrides_performance import MelderExperiment

totals = defaultdict(float)
def wrap(owner, name, label, static=False):
    original = getattr(owner, name)
    func = original
    def timed(*a, **k):
        s = time.perf_counter_ns()
        try:
            return func(*a, **k)
        finally:
            totals[label] += time.perf_counter_ns() - s
    setattr(owner, name, staticmethod(timed) if static else timed)

builder = SpellArtifactProcessorStrategyBuilder()
for name in builder.registered_strategy_names():
    t = type(builder.get_strategy(name))
    orig = t.process
    def timed(self, spell, artifact, model, _o=orig, _n=name):
        s = time.perf_counter_ns()
        try:
            return _o(self, spell, artifact, model)
        finally:
            totals["p9:" + _n] += time.perf_counter_ns() - s
    t.process = timed
builder.cleanup()
wrap(mop.ManyOnlyCodegenPlanBuilder, "_build_overrides_plan", "p10:overrides_plan")
wrap(mop.ManyOnlyCodegenPlanBuilder, "_build_no_overrides_plan", "p10:no_overrides_plan")
wrap(mm, "serialize_targets_by_spec", "p11:serialize_targets")
wrap(ManyOnlyCodegenCreationHelpers, "build_override_step_row", "p11:override_rows", static=True)
print(f"python {sys.version.split()[0]} gil={sys._is_gil_enabled()}")
for graph in ("shallow", "wide", "diamond", "deep"):
    runs = defaultdict(list)
    for _ in range(7):
        totals.clear()
        e = MelderExperiment()
        s = time.perf_counter_ns()
        e.setup(graph, "automatic")
        runs["setup"].append((time.perf_counter_ns() - s) / 1e6)
        e.cleanup()
        for k, v in totals.items():
            runs[k].append(v / 1e6)
    med = {k: statistics.median(v) for k, v in runs.items()}
    lane = sum(v for k, v in med.items() if k in ("p9:spell_override_targeting_processor", "p10:overrides_plan", "p11:serialize_targets", "p11:override_rows"))
    print(f"{graph:8} setup {med['setup']:8.2f} ms | override-lane {lane:7.2f} ms ({100*lane/med['setup']:.1f}%) | " + ", ".join(f"{k}={v:.2f}" for k, v in sorted(med.items()) if k != "setup" and v >= 0.05))
