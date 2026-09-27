"""S2 parity probe: the lowering's empty-key-set plan vs the family's inner no-overrides executor (many_only graphs).

Run from a tree root with PYTHONPATH=src:. Times direct calls (no meld entry, no door) per graph.
"""
import statistics, sys, time
from tests.experimentation.test_melder_creation_overrides_performance import MelderExperiment
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.manifest_creation_cache import MANIFEST_METADATA_KEY
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering import SitePlanLowering, SitePlanStep
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_override_runtime import SitePlanOverrideRuntime
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.hydration.many_only_hydrator import _resolve_spell_lookup
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers.many_only_no_overrides_codegen_creation_compiler import (
    _hydrate_steps_from_rows, _resolve_root_instance_key, compile_no_overrides_codegen_creation_executor,
)


def per_call_ns(fn, n):
    samples = []
    for _ in range(7):
        s = time.perf_counter_ns()
        for _ in range(n):
            fn()
        samples.append((time.perf_counter_ns() - s) / n)
    return statistics.median(samples)


print(f"python {sys.version.split()[0]} gil={sys._is_gil_enabled()}")
for graph, n in (("shallow", 20000), ("wide", 20000), ("diamond", 20000), ("deep", 400)):
    e = MelderExperiment()
    e.setup(graph, "automatic")
    conduit = e.conduit
    conduit.meld(spell_id=e.root_id)
    spell = e.book.find_spell_by_id(e.root_id)
    manifest = spell._compiler_artifact._spell_codegen_creation.metadata[MANIFEST_METADATA_KEY]
    payload = manifest["no_overrides"]
    lookup = _resolve_spell_lookup(spell=spell, step_spell_ids=payload["step_spell_ids"])
    inner = compile_no_overrides_codegen_creation_executor(
        codegen_ir={"steps_rows": payload["steps_rows"], "root_spell_id": payload["root_spell_id"],
                    "transient_schema": payload["transient_schema"]},
        spell_lookup=lookup,
    )
    rows = _hydrate_steps_from_rows(steps_rows=payload["steps_rows"], spell_lookup=lookup)
    rik = _resolve_root_instance_key(steps=rows, root_spell_id=payload["root_spell_id"])
    runtime = SitePlanOverrideRuntime(
        steps=tuple(SitePlanStep.from_many_only_row(r) for r in rows), root_spell=spell,
        root_instance_key=rik, inner_no_overrides_executor=inner,
    )
    resolution = runtime._resolve((), 0)
    source, namespace, masked = SitePlanLowering.emit(
        steps=runtime._steps, site_graph=runtime._site_graph_or_build(), resolution=resolution,
        root_instance_key=rik, root_spell_id=spell.spell_id, root_spell_name=spell.spell_name, arity=0,
    )
    exec(compile(source, "<s2_parity>", "exec"), namespace)
    plan = namespace[SitePlanLowering.PLAN_FUNCTION_NAME]
    meld = conduit._meld
    ov = {}
    a, b = type(inner(meld)), type(plan(meld, ov))
    assert a is b, (a, b)
    t_inner = per_call_ns(lambda: inner(meld), n)
    t_plan = per_call_ns(lambda: plan(meld, ov), n)
    t_meld = per_call_ns(lambda: conduit.meld(spell_id=e.root_id), n)
    print(f"{graph:8} inner {t_inner:9.1f} ns | lowering plan {t_plan:9.1f} ns ({100 * t_inner / t_plan:5.1f}% speed) | public meld {t_meld:9.1f} ns | plan lines {source.count(chr(10))}")
    for m in masked:
        m.cleanup()
    runtime.cleanup()
    e.cleanup()
