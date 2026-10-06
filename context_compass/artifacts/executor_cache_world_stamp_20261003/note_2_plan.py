"""Mapping PLAN note, ticket checklist ticks, artifact board rows."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths  # noqa: E402

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
TASK_REL = "tickets/tasks/2026-10-03_require_world_stamp_for_executor_cache_full_hit_task.md"
TASK = os.path.join(CC, TASK_REL)
ARTBOARD = os.path.join(CC, "artifact_board.md")
TS = now_utc()

NOTE = f"""- DATETIME: {TS}
  TYPE: PLAN
  CLAIM: Patch docs written and indexed under system_docs/patches/active/executor_cache_world_stamp_2026_10_03/
    (architecture, component Spellbook Core caching, code description; ENTRY markers; --check OK). Mapping,
    patch section -> implementation step -> validation step:
    (a) code description step 1 (envelope field, property, setter, generation 19) -> caching_system.py edit
    -> caching-system unit tests (round trip through emit and reload; "" when the field is absent; a
    non-string rejected; the emit-shape key set; set_world_stamp's changed bool) and the history pin (19);
    (b) step 2 (the full-hit rule) -> `_build_conjure_cache_state` edit -> cache runtime unit cases: all
    cached + matching stamp full_hit, all cached + mismatch mixed, none cached + mismatch full_miss, disabled
    unchanged (stubs gain `_aetheric_frame_configuration=None`, `_contracted_spells={{}}` and a stamp surface);
    (c) step 3 (the staging write) -> `_stage_spell_payloads_at_conjure_end` edit -> unit: the stamp is
    recorded after re-staging and the emit flagged when it changed, not when equal;
    (d) component validation expectations -> a new component file (caching on, fresh fragment, own conduit
    name): worlds 1-4 of the component patch, red on the tree's rule, green after; the integration surplus
    contract re-pinned as rerun-then-full-hit.
    Order: re-sync the working copy from the tree, write the component file and run it red, then the
    anchored apply script (src + tests), green, then the shards.
  EVIDENCE:
  - system_docs/patches/active/executor_cache_world_stamp_2026_10_03/architecture_patch.md:1-60
  - system_docs/patches/active/executor_cache_world_stamp_2026_10_03/component_patch_spellbook_core_caching.md:1-45
  - system_docs/patches/active/executor_cache_world_stamp_2026_10_03/code_description_patch_executor_cache_admission.md:1-40
  IMPACT: Entry gate satisfied for the working-copy implementation; the tree stays untouched until green.
  NEXT: re-sync `$HOME/work/melder_cc` from the tree; write the component regression file; run it red.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

"""
bad = check_line_lengths(NOTE)
if bad:
    raise SystemExit(f"lines over cap: {bad}")
text, nl = read_text(TASK)
text = replace_once(text, "\n## Context / Handoff Summary\n", "\n" + NOTE + "## Context / Handoff Summary\n", "handoff")
text = replace_once(
    text,
    "- [ ] Re-read in full: `_build_conjure_cache_state`",
    "- [x] Re-read in full: `_build_conjure_cache_state`", "step1")
text = replace_once(
    text,
    "- [ ] Patch docs (architecture, component Spellbook Core / caching, code description of the admission) and the\n"
    "      mapping note; link them here.",
    "- [x] Patch docs (architecture, component Spellbook Core / caching, code description of the admission) and the\n"
    "      mapping note; link them here.", "step2")
old_state = "STATE 2026-10-03T20:36:13Z: IN_PROGRESS. Opened; nothing read or edited yet. Resume from the latest note's NEXT.\n"
new_state = old_state + (f"\nSTATE {TS}: IN_PROGRESS. Tiers read, design decided (world stamp in the envelope, generation 19), patch\n"
                         "docs linked; implementation on the working copy next. Resume from the latest note's NEXT.\n")
text = replace_once(text, old_state, new_state, "state")
text = replace_once(text, "- Updated: 2026-10-03T20:36:13Z", f"- Updated: {TS}", "updated")
write_text(TASK, text, nl)

board, nl = read_text(ARTBOARD)
rows = (
    f"| {TASK_REL} | artifacts/executor_cache_world_stamp_20261003/ | implementation_evidence | active | "
    "retain_as_reference | Lane scripts, the red/green component runs and the shard logs of the working copy. | "
    f"{TS} | REQUIRED |\n"
    f"| {TASK_REL} | system_docs/patches/active/executor_cache_world_stamp_2026_10_03/ | patch_doc | active | "
    "promote_to_documentation | Entry-gate artifacts: the stamp-keyed full hit (architecture), the admission "
    f"before/after (component), the envelope and staging control flow (code description). | {TS} | REQUIRED |\n"
)
board = replace_once(board, "<!-- BEGIN USER-DEFINED: active_artifacts -->\n",
                     "<!-- BEGIN USER-DEFINED: active_artifacts -->\n" + rows, "active_artifacts begin")
write_text(ARTBOARD, board, nl)
print("planned", TS)
