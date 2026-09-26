import sys
from tests.experimentation.test_melder_creation_overrides_performance import MelderExperiment
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers.many_only_no_overrides_codegen_creation_compiler as mc
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.manifest_creation_cache import MANIFEST_METADATA_KEY
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering import SitePlanLowering, SitePlanStep
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_override_runtime import SitePlanOverrideRuntime
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.hydration.many_only_hydrator import _resolve_spell_lookup
captured = []
orig = mc.get_or_compile_executor_code
def cap(*, source, source_name):
    captured.append(source)
    return orig(source=source, source_name=source_name)
mc.get_or_compile_executor_code = cap
graph = sys.argv[1]
e = MelderExperiment(); e.setup(graph, "automatic")
spell = e.book.find_spell_by_id(e.root_id)
payload = spell._compiler_artifact._spell_codegen_creation.metadata[MANIFEST_METADATA_KEY]["no_overrides"]
lookup = _resolve_spell_lookup(spell=spell, step_spell_ids=payload["step_spell_ids"])
inner = mc.compile_no_overrides_codegen_creation_executor(codegen_ir={"steps_rows": payload["steps_rows"], "root_spell_id": payload["root_spell_id"], "transient_schema": payload["transient_schema"]}, spell_lookup=lookup)
print("==== INNER"); print(captured[-1])
rows = mc._hydrate_steps_from_rows(steps_rows=payload["steps_rows"], spell_lookup=lookup)
rik = mc._resolve_root_instance_key(steps=rows, root_spell_id=payload["root_spell_id"])
rt = SitePlanOverrideRuntime(steps=tuple(SitePlanStep.from_many_only_row(r) for r in rows), root_spell=spell, root_instance_key=rik, inner_no_overrides_executor=inner)
src, ns, masked = SitePlanLowering.emit(steps=rt._steps, site_graph=rt._site_graph_or_build(), resolution=rt._resolve((), 0), root_instance_key=rik, root_spell_id=spell.spell_id, root_spell_name=spell.spell_name, arity=0)
print("==== LOWERING"); print(src)
