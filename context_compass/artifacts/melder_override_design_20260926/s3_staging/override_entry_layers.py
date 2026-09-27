"""Per-layer cost of one root-key override meld vs a normal meld (owner's four graphs, many_only).

Run from a tree root with PYTHONPATH=src:. Median of 7 x n direct calls per layer.
Layers: public conduit.meld(override=) -> ConduitMeld.meld -> CreationContext override door ->
SitePlanOverrideRuntime dispatcher -> key-set plan. References: public normal meld, inner executor.
"""
import statistics, sys, time
from tests.experimentation.test_melder_creation_overrides_performance import MelderExperiment, _root_inputs
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.manifest_creation_cache import MANIFEST_METADATA_KEY
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering import SitePlanStep
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
for graph, n in (("shallow", 20000), ("wide", 20000), ("diamond", 20000)):
    e = MelderExperiment()
    e.setup(graph, "automatic")
    conduit, root_id = e.conduit, e.root_id
    inputs = _root_inputs(conduit.meld(spell_id=root_id))
    key = next(iter(inputs))
    one = {key: inputs[key]}
    conduit.meld(spell_id=root_id, override=one)
    spell = e.book.find_spell_by_id(root_id)
    ctx = spell._creation_context
    meld = conduit._meld
    payload = spell._compiler_artifact._spell_codegen_creation.metadata[MANIFEST_METADATA_KEY]["no_overrides"]
    lookup = _resolve_spell_lookup(spell=spell, step_spell_ids=payload["step_spell_ids"])
    inner = compile_no_overrides_codegen_creation_executor(
        codegen_ir={"steps_rows": payload["steps_rows"], "root_spell_id": payload["root_spell_id"],
                    "transient_schema": payload["transient_schema"]},
        spell_lookup=lookup,
    )
    rows = _hydrate_steps_from_rows(steps_rows=payload["steps_rows"], spell_lookup=lookup)
    runtime = SitePlanOverrideRuntime(
        steps=tuple(SitePlanStep.from_many_only_row(r) for r in rows), root_spell=spell,
        root_instance_key=_resolve_root_instance_key(steps=rows, root_spell_id=payload["root_spell_id"]),
        inner_no_overrides_executor=inner,
    )
    dispatch = runtime.execute_with_overrides
    dispatch(meld, one)
    plan = runtime._plans[tuple(one)]
    rows_ns = {
        "normal public": per_call_ns(lambda: conduit.meld(spell_id=root_id), n),
        "inner executor": per_call_ns(lambda: inner(meld), n),
        "override public": per_call_ns(lambda: conduit.meld(spell_id=root_id, override=one), n),
        "ConduitMeld.meld": per_call_ns(lambda: meld.meld(root_id, spell_override=one), n),
        "override door": per_call_ns(lambda: ctx._overrides_executor(meld, one), n),
        "dispatcher": per_call_ns(lambda: dispatch(meld, one), n),
        "plan": per_call_ns(lambda: plan(meld, one), n),
    }
    print(f"{graph} (key {key!r}): " + " | ".join(f"{k} {v:6.1f}" for k, v in rows_ns.items()))
    runtime.cleanup()
    e.cleanup()
