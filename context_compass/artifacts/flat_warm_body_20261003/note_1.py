"""FACT (emission + hydration read), MEASURE (harness), DECISION (S9 ships, S11 retired) notes."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "executor_cache_world_stamp_20261003"))
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths  # noqa: E402

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
TASK = os.path.join(CC, "tickets/tasks/2026-10-03_certify_and_implement_site_store_constants_task.md")
STORY = os.path.join(CC, "tickets/stories/2026-10-03_flat_warm_body_constants_story.md")
BOARD = os.path.join(CC, "attention_board.md")
TS = now_utc()
NOTES = f"""- DATETIME: {TS}
  TYPE: FACT
  CLAIM: Emission and hydration read whole where the shared-site read lives. `SitePlanEmission.__init__` seeds the
    plan namespace (helpers, `root_spell_id`, `root_spell_name`, `spells` = the kept steps' live Spell objects);
    `_emit_shared_hit` emits, per shared site, `c{{i}} = <route>` then `v{{i}} = c{{i}}._creations.get(sid{{i}})` and the
    miss call `_miss{{i}}(meld, c{{i}}, v...)`; `_route` is `spells[i]._owner_creations` for `Existence.unique` and a
    `meld.<store>` attribute (or the cluster's resolved store) for the other shared existences; `sid{{i}}` is bound
    by `_bind` to `step.spell.spell_id` - the live Spell's attribute - in every plan, because plans are emitted at
    hydration from rows whose `spell` is resolved live (`_hydrate_steps_from_rows` + `SitePlanStep.
    from_generalized_row` / `from_many_only_row`; `_build_site_plan_runtime` -> `SitePlanOverrideRuntime` ->
    `SitePlanLowering.emit`). The manifest package persists rows only (`steps_rows`, `transient_schema`,
    `executor_signature`), never emitted plan source, so a lowering change retires no cached payload. Ownership:
    `define_conduit_into_spells` calls `Spell._add_owned_conduit(conduit._id, name, conduit._creations,
    dynamic_environment=conduit.__dynamic_environment__, ...)` for every owned spell at conjure, which sets
    `_owner_creations` and `_dynamic_environment` under the spell lock; the only other writer is the same method
    (ownership transfer, dynamic posture only). `_owner_creations` is initialised None and `_dynamic_environment`
    False before ownership. The test stub `_spell` in the lowering unit tests carries `_owner_creations` but no
    `_dynamic_environment`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:847-926
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1084-1120
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1331-1443
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:93-220
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:269-425
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/manifest/generalized_manifest.py:39-130
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/manifest_creation_cache.py:1-96
  - src/melder/aether/spellbook/spellbook_creation_system.py:1303-1382
  - src/melder/aether/spellbook/spell.py:1440-1470
  - tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py:35-120
  IMPACT: S11 is already the case (the key object is the live `spell_id`); S9 applies to `unique` sites only (the
    other routes are one attribute read on the `meld` parameter) and can be gated per site on the provider's
    `_dynamic_environment`; no cache generation bump is needed for an emission-only change.
  NEXT: MEASURE note (harness and the interleaved A/B).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: {TS}
  TYPE: MEASURE
  CLAIM: Harness extended with an S9 variant (drop every `c{{i}} = spells[i]._owner_creations` line, bind `c{{i}}` in
    the namespace) and an S11 identity report. Three sequential harness runs showed S9 at -10..-17% on every shape,
    but a sequential table penalises its first variant on this VM (worker plain 203 there vs 166 interleaved), so
    the shipped numbers are the interleaved A/B (plain vs S9 alternating 40k-call batches, 7 rounds, three runs,
    medians; VM load 1.1-2.2): worker (1 unique site) 166/160/159 -> 160/146/148 ns, -7%; context_root (5 unique
    sites) 326/308/316 -> 290/277/264, -11%; wide8_unique (8) 447/448/429 -> 374/374/366, -16%; wide8_existing (8)
    454/444/444 -> 370/367/368, -17%; chain8_transient (1 site over a many chain) 449/427/432 -> 437/428/419, -3%.
    Micro-benchmark on the same interpreter: the alias line costs 8 ns per site (37.1 -> 28.9 ns for one read
    group), matching ~8-10 ns per unique site in the plans. S11: every `sid{{i}}` constant IS the store's key object
    on every shape ("identical"), so there is nothing to ship. S2a (data only, parked): -30..-38% on the two
    existing-object shapes in the sequential table.
  EVIDENCE:
  - artifacts/flat_warm_body_20261003/logs/interleaved_s9_medians.md:1-8
  - artifacts/flat_warm_body_20261003/logs/interleaved_s9_run1.md:1-8
  - artifacts/flat_warm_body_20261003/logs/harness_s9_run1.md:1-60
  - artifacts/flat_warm_body_20261003/logs/micro_owner_store_read.md:1-6
  - artifacts/flat_warm_body_20261003/harness_s9.py:1-80
  IMPACT: S9 is above noise on every shape with unique providers and scales per site; it is the cheapest emitter
    change left (one line per site, no store change, no guard).
  NEXT: DECISION note, then the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: {TS}
  TYPE: DECISION
  CLAIM: Ship S9 as: in `_emit_shared_hit`, a `unique` site whose provider Spell is owned by an automatic conduit
    (`not step.spell._dynamic_environment`) and has an owner store binds `c{{i}}` = `step.spell._owner_creations`
    in the plan namespace and emits no alias line; every other site (the `meld.<store>` routes, a dynamic
    provider, an unowned one) emits today's line. The miss keeps its `c{{i}}` parameter (the call passes the
    global). Rationale: the owner store of an owned spell changes only through `_add_owned_conduit`, which in a
    live world runs again only for ownership transfer (dynamic posture); a notch or late bind re-gates and
    recompiles the plan, which re-emits the constant. No generation bump: plans are emitted at hydration from
    rows. S11 is retired as already true (FACT above). S2a stays parked (owner: rare).
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:1440-1470
  - src/melder/aether/spellbook/spellbook_creation_system.py:1356-1382
  - artifacts/flat_warm_body_20261003/logs/interleaved_s9_medians.md:1-8
  IMPACT: One method and one docstring in the lowering; the `_spell` test stub gains `_dynamic_environment`.
  NEXT: patch docs (architecture, component SpellCompiler codegen, code description) and the mapping note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
bad = check_line_lengths(NOTES, exempt=r"^  - (src|tests|artifacts)/")
if bad:
    raise SystemExit(f"lines over cap: {bad}")
text, nl = read_text(TASK)
text = replace_once(text, "\n## Context / Handoff Summary\n", "\n" + NOTES + "## Context / Handoff Summary\n", "handoff")
text = replace_once(text, "- [ ] Read the shared-site emission and the plan namespace", "- [x] Read the shared-site emission and the plan namespace", "step1")
text = replace_once(text, "- [ ] Harness: S9 and S11 transforms", "- [x] Harness: S9 and S11 transforms", "step2")
text = replace_once(text, f"- Updated: ", f"- Updated: ", "noop")
import re
text = re.sub(r"^- Updated: .*$", f"- Updated: {TS}", text, count=1, flags=re.MULTILINE)
text = text.rstrip("\n").replace("\n## Project-Specific Additions",
    f"\nSTATE {TS}: IN_PROGRESS. S9 certified (-7..-17% of the plan on shapes with unique providers), S11 retired as\n"
    "already true, S2a parked; patch docs next, then the lowering edit. Resume from the latest note's NEXT.\n\n## Project-Specific Additions") + "\n"
write_text(TASK, text, nl)
board, nl = read_text(BOARD)
old = "| tickets/tasks/2026-10-03_certify_and_implement_site_store_constants_task.md | 2026-10-03T21:31:58Z | REQUIRED |"
board = replace_once(board, old, old.replace("2026-10-03T21:31:58Z", TS), "row ts")
board = replace_once(board,
    "Read the shared-site emission and the hydrators' namespace binding, then add S9/S11 to the harness and measure before any patch doc.",
    "S9 certified (-7..-17% of the plan on unique-provider shapes); S11 already true; write the patch docs, then the lowering edit and tests.", "row next")
write_text(BOARD, board, nl)
print("noted", TS)
