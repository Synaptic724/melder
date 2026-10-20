"""Append the S5 U8 FACT note (re-verified after the 2026-10-15 compaction) to the S5 story."""
import datetime
import pathlib
import sys

STORY = pathlib.Path("context_compass/tickets/stories/2026-10-15_managed_dispense_codegen_story.md")
SC = "src/melder/aether/spellbook/spell_compiler"
CG = SC + "/codegen_creation_system"


def main() -> int:
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    note = f"""- DATETIME: {now}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: U8 answered from source (re-read after the compaction). Two predicates decide sharedness by `existence is
    not many`: the instance processor's `_is_shared_existence` (one `(spell_id, None)` key and a canonical occurrence
    per shared spell) and the occurrence analyzer's (collapses a shared spell's occurrences during the walk); both
    must answer False for managed so a managed spell gets one instance key per path. Phase 10: solo claims any model
    with one visible spell and no collection socket, whatever its existence; many_only needs every visible spell
    many, so it never claims a managed model; generalized takes the rest. The generalized manifest's route-key
    whitelist names six families and raises for "managed". The lane plan's other existence branches are metadata the
    site plan never reads: `_build_fast_transient_plan` returns None unless every step is many (a managed root gets
    the non-fast door), `_creation_target_for_existence` falls to OWNER, the lock hint is "creations_lock",
    `_should_register` is True; `SitePlanStep.from_generalized_row` keeps only the existence and the spell-lock hint.
    The phase-11 signature row hashes the existence name. `_register_spell_instance_prebound` raises for any other
    existence, and only the straight-line specializer reaches it (the manifest no-overrides compiler's namespace; the
    hydrator imports only its builder, its two row predicates and the root-key resolver); its capture set is `unique`
    rows and its many-feeds-holder decline does not see managed rows.
  EVIDENCE:
  - {SC}/artifact_processor/strategies/spell_occurrence_instance_processor_strategy.py:112-119
  - {SC}/artifact_processor/strategies/spell_occurrence_instance_processor_strategy.py:131-203
  - {SC}/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:732-737
  - {SC}/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:777-916
  - {SC}/codegen_planner/codegen_plan_discovery_system/strategies/solo_codegen_plan_discovery_strategy.py:52-81
  - {SC}/codegen_planner/codegen_plan_discovery_system/strategies/many_only_codegen_plan_discovery_strategy.py:52-95
  - {CG}/strategies/generalized/manifest/generalized_manifest.py:72-91
  - {SC}/codegen_planner/data/spell_generalized_codegen_lane_plan.py:2463-2660
  - {SC}/codegen_planner/data/spell_generalized_codegen_lane_plan.py:2661-2706
  - {CG}/shared_assets/site_plan_lowering.py:168-191
  - {SC}/phases/shared_compiler_executions.py:1062-1110
  - {CG}/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:400-457
  - {CG}/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:59-78
  - {CG}/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:1123-1207
  - {CG}/strategies/generalized/hydration/generalized_hydrator.py:270-362
  - {CG}/strategies/generalized/hydration/generalized_hydrator.py:558-645
  IMPACT: S5's edits outside the lowering and the doors: both predicates return False for managed; solo discovery
    declines a model whose existence counts hold managed; the manifest whitelist gains "managed"; a pure row
    predicate beside `rows_feed_many_into_non_many_step` makes `_install_specializing_door` keep the plain door for
    a graph with a managed row. Nothing else in phases 9-11 branches on two kinds of existence, and rows map the
    existence by name, so managed rows hydrate unchanged; existing models take none of the new branches.
  NEXT: Read override_key_resolver.py whole (how winning keys cut a managed site), then the pool's
    reserve/abandon/adopt.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
    text = STORY.read_text(encoding="utf-8")
    anchor = "## Closure Confirmation"
    if text.count(anchor) != 1:
        print("anchor count", text.count(anchor))
        return 1
    text = text.replace(anchor, note + anchor)
    old_updated = [line for line in text.splitlines() if line.startswith("- Updated: ")]
    if len(old_updated) != 1:
        print("updated lines", old_updated)
        return 1
    text = text.replace(old_updated[0], f"- Updated: {now}")
    STORY.write_text(text, encoding="utf-8", newline="")
    width = max(len(line) for line in note.splitlines())
    print("note appended", now, "max width", width)
    return 0


if __name__ == "__main__":
    sys.exit(main())
