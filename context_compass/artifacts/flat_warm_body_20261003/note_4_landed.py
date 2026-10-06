"""Landing notes on task/story/epic, task -> review, board row and details, artifact board rows."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "executor_cache_world_stamp_20261003"))
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths  # noqa: E402

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
TASK_REL = "tickets/tasks/2026-10-03_certify_and_implement_site_store_constants_task.md"
STORY_REL = "tickets/stories/2026-10-03_flat_warm_body_constants_story.md"
EPIC_REL = "tickets/epics/2026-10-01_static_codegen_and_door_strategies_epic.md"
TASK, STORY, EPIC = (os.path.join(CC, p) for p in (TASK_REL, STORY_REL, EPIC_REL))
BOARD = os.path.join(CC, "attention_board.md")
ARTBOARD = os.path.join(CC, "artifact_board.md")
EXEMPT = r"^  - (src|tests|artifacts|system_docs|release_docs|tickets)/"
TS = now_utc()

TASK_NOTES = f"""- DATETIME: {TS}
  TYPE: FACT
  CLAIM: Landed on the tree at 0.2.8221 (notched above 0.2.8220 at landing): `apply_s9.py` applied to the tree
    (the lowering, the two stubs, four unit tests, the component file; CRLF kept, the door-held test file stays
    LF as it was); release-note section "Shared singleton sites read their store as a constant" plus a packaging
    bullet; `src_architecture.md` (operational invariant, the lowering's code-map extent 1588, handoff) and
    `src_components.md` (SpellCompiler emission bullet, the lowering's code-map extent - stale since 2026-09-26 -
    and handoff) with both indexes rebuilt and checked; the graph re-extracted (--strict), the SitePlanEmission
    descriptor gains the owner-store-constant responsibility, accepted and reassembled (27595 lines, index
    verified); patch docs archived to `system_docs/patches/completed/flat_warm_body_2026_10_03/` (Status
    "promoted and archived"); assets rebuilt in the mirror and copied back (three manifests at v0.2.8221, --check
    OK on the tree); LLM bundles rebuilt and --check OK; no `.git/index.lock` left behind. No cache generation
    moved (plans are emitted from rows). The codex bridge lists no chat for melder_2 or muse_0 in this repository
    (command_0-2 and cc_astra_0 are other repositories' agents), so the notch notice is carried by this ticket,
    the board row and the release note, as for 0.2.8217-0.2.8220.
  EVIDENCE:
  - artifacts/flat_warm_body_20261003/logs/apply_tree.log:1-4
  - artifacts/flat_warm_body_20261003/logs/land_docs.log:1-1
  - artifacts/flat_warm_body_20261003/logs/graph_assemble.log:1-5
  - artifacts/flat_warm_body_20261003/logs/assets_check_tree.log:1-3
  - artifacts/flat_warm_body_20261003/logs/llm_bundles_check.log:1-3
  - release_docs/next_version_release.md:425-441
  - system_docs/patches/completed/flat_warm_body_2026_10_03/architecture_patch.md:1-8
  IMPACT: The change set is complete on the tree; nothing else of this lane is in flight.
  NEXT: MEASURE note (post-landing shards and the harness on the shipped body), then the task goes to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: {TS}
  TYPE: MEASURE
  CLAIM: Post-landing shards on a fresh copy of the tree (`$HOME/work/melder_tree`, 3.14.7t, `-X gil=0`): unit
    spellbook+utilities+root 3257 passed / 2 skipped / 7 xfailed (17.0 s), unit aether+crystallizer+MR+
    build_assets 5171 passed / 1 skipped (22.3 s), component 2293 passed / 23 skipped / 1 xfailed (27.7 s),
    integration spellbook+conduit+multithreading+live_sim 929 passed / 2 skipped / 1 xfailed / 2 xpassed
    (19.0 s), integration aether+crystallizer+MR 1098 passed / 7 xfailed (79.5 s). Harness on the shipped body
    (interleaved plain vs the S9 transform, which is now a no-op): plain medians worker 148 ns (pre-landing plain
    160), context_root 260 (316), wide8_unique 359 (447), wide8_existing 368 (444), chain8_transient 404 (432);
    the transform column is within +-3% of plain on every shape, so the shipped emitter already carries the
    S9 shape. Full-tree suites and the gauntlet: Not run (owner-run).
  EVIDENCE:
  - artifacts/flat_warm_body_20261003/logs/post_landing_unit_spellbook_utilities_root.log:1-2
  - artifacts/flat_warm_body_20261003/logs/post_landing_unit_aether_crystallizer_mr.log:1-2
  - artifacts/flat_warm_body_20261003/logs/post_landing_component.log:1-2
  - artifacts/flat_warm_body_20261003/logs/post_landing_integration_spellbook_conduit_mt_livesim.log:1-2
  - artifacts/flat_warm_body_20261003/logs/post_landing_integration_aether_crystallizer_mr.log:1-2
  - artifacts/flat_warm_body_20261003/logs/interleaved_shipped_body_run1.md:1-7
  - artifacts/flat_warm_body_20261003/logs/interleaved_s9_medians.md:1-8
  IMPACT: The lane's exit gate is met except the owner-run suites and gauntlet; the task is in review.
  NEXT: owner turn-in (full-tree suites and the gauntlet on 0.2.8221; on green the task and story close); then
    the door lane story opens with its epoch audit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
STORY_NOTE = f"""- DATETIME: {TS}
  TYPE: FACT
  CLAIM: S9 landed at 0.2.8221 through the task; S11 retired as already true (every `sid{{i}}` is the live
    Spell's `spell_id` object because plans are emitted at hydration); S2a parked. The dynamic-posture proof is
    the emitted line itself: a dynamic provider's plan is byte-identical to before (the unit and component tests
    assert the alias line), so ownership transfer keeps the per-creation read and the existing transfer tests
    cover it. The "automatic path repoints the store?" open question is closed in source: only
    `Spell._add_owned_conduit` writes `_owner_creations` (conjure; transfer in dynamic posture).
  EVIDENCE:
  - tickets/tasks/2026-10-03_certify_and_implement_site_store_constants_task.md:150-240
  - src/melder/aether/spellbook/spell.py:1440-1470
  IMPACT: The story's acceptance criteria are met on the VM; the owner-run numbers remain.
  NEXT: owner turn-in of the task and this story; the door lane opens after.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

"""
EPIC_NOTE = f"""- DATETIME: {TS}
  TYPE: FACT
  CLAIM: Milestone 3 reached pending the owner's run: the flat warm body (S9) landed at 0.2.8221 with docs,
    graph, assets and bundles current; S11 retired (already true); S2a parked by the owner. Per the recommendation
    the door lane is next: the epoch audit in source, the door harness in dynamic posture, D5, then D1-D3; the PGO
    epic stays untouched (owner, 2026-10-03).
  EVIDENCE:
  - tickets/stories/2026-10-03_flat_warm_body_constants_story.md:100-151
  - tickets/tasks/2026-10-03_certify_and_implement_site_store_constants_task.md:150-240
  IMPACT: The emitter lane is done; the door lane's story is the next active lane on the owner's word.
  NEXT: owner turns the S9 task and story in; open the door story's audit task (patch docs first).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

"""
for block in (TASK_NOTES, STORY_NOTE, EPIC_NOTE):
    bad = check_line_lengths(block, exempt=EXEMPT)
    if bad:
        raise SystemExit(f"lines over cap: {bad}")

# ---- task ----
text, nl = read_text(TASK)
text = replace_once(text, "\n## Context / Handoff Summary\n", "\n" + TASK_NOTES + "## Context / Handoff Summary\n", "task handoff")
text = replace_once(
    text,
    "- [ ] Land on the tree (CRLF), notch above `__version__`, release-note section, docs, graph; patch docs promoted\n"
    "      and archived; assets and LLM bundles LAST; both checks OK; post-landing shards.\n",
    "- [x] Land on the tree (CRLF), notch above `__version__`, release-note section, docs, graph; patch docs promoted\n"
    "      and archived; assets and LLM bundles LAST; both checks OK; post-landing shards.\n",
    "step5")
text = replace_once(text, "- Status: in_progress\n", "- Status: review\n", "task status")
text = replace_once(
    text,
    "- transition_reason: Opened on the owner's word (2026-10-03T21:31:58Z).\n",
    "- transition_reason: Opened on the owner's word (2026-10-03T21:31:58Z).\n"
    "- from_state: in_progress\n"
    "- to_state: review\n"
    f"- transition_reason: Landed at 0.2.8221 with docs, graph, assets and bundles current ({TS}); the owner-run\n"
    "  suites and gauntlet remain.\n",
    "task transition")
text = replace_once(
    text,
    "## Validation\n- Not run.\n",
    "## Validation\n"
    "- Run on the VM (3.14.7t, GIL off): the lowering unit file and the component file (53 passed), six shards on\n"
    "  the working copy and five on a fresh copy of the landed tree (all green; counts in `## Notes`), the harness\n"
    "  on the shipped body (interleaved, run 1).\n"
    "- Not run: the full-tree suites and the persistent gauntlet (owner-run).\n",
    "task validation")
for item in ("- [ ] Steps complete and checked off", "- [ ] Deliverables produced and linked",
             "- [ ] Documentation updated (if needed)", "- [ ] Validation status recorded",
             "- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)",
             "- [ ] No src edit before the harness verdict, the patch docs and the mapping note.",
             "- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.",
             "- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.",
             "- [ ] No status transition without evidence-backed transition reason."):
    text = replace_once(text, item + "\n", item.replace("- [ ]", "- [x]", 1) + "\n", item[:40])
text = replace_once(
    text,
    "- [ ] Run Ticket Microcycle during execution:\n",
    "- [x] Run Ticket Microcycle during execution:\n", "microcycle step")
text = replace_once(
    text,
    "- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.\n",
    "- [x] Document each meaningful finding immediately in `## Notes` before further investigation.\n", "doc step")
state = (f"\nSTATE {TS}: REVIEW. S9 landed at 0.2.8221 (docs, graph, assets, bundles current; post-landing shards green;\n"
         "harness re-run on the shipped body). Owner-owed: full-tree suites and gauntlet, then turn-in. Nothing in flight.\n")
text = replace_once(text, "\n## Project-Specific Additions\n", state + "\n## Project-Specific Additions\n", "task state")
text = re.sub(r"^- Updated: .*$", f"- Updated: {TS}", text, count=1, flags=re.MULTILINE)
write_text(TASK, text, nl)

# ---- story ----
text, nl = read_text(STORY)
text = replace_once(text, "\n## Closure Confirmation\n", "\n" + STORY_NOTE + "## Closure Confirmation\n", "story closure")
text = replace_once(
    text,
    "- Does any automatic-world path repoint a spell's owner store after conjure (upgrade? cluster?) - to verify in\n"
    "  source before the constant is emitted.\n",
    "- Does any automatic-world path repoint a spell's owner store after conjure (upgrade? cluster?) - to verify in\n"
    f"  source before the constant is emitted. CLOSED {TS}: only `Spell._add_owned_conduit` writes\n"
    "  `_owner_creations` (conjure, and ownership transfer in dynamic posture); upgrade conjures a new Book whose\n"
    "  definitions do not transfer, and clusters route through `meld._cluster_creations`, not the owner store.\n",
    "story open question")
state = (f"\nSTATE {TS}: IN_PROGRESS. The task is in review: S9 landed at 0.2.8221; owner-run suites and gauntlet owed;\n"
         "then both tickets close on the owner's word.\n")
text = replace_once(text, "\n## Project-Specific Additions\n", state + "\n## Project-Specific Additions\n", "story state")
text = re.sub(r"^- Updated: .*$", f"- Updated: {TS}", text, count=1, flags=re.MULTILINE)
write_text(STORY, text, nl)

# ---- epic ----
text, nl = read_text(EPIC)
text = replace_once(text, "\n## Closure Confirmation\n", "\n" + EPIC_NOTE + "## Closure Confirmation\n", "epic closure")
state = (f"\nSTATE {TS}: IN_PROGRESS. The flat-warm-body task is in review (S9 landed at 0.2.8221); the door lane opens on\n"
         "the owner's word after the turn-in. Resume from the task's latest STATE line.\n")
text = replace_once(text, "\n## Project-Specific Additions\n", state + "\n## Project-Specific Additions\n", "epic state")
text = re.sub(r"^- Updated: .*$", f"- Updated: {TS}", text, count=1, flags=re.MULTILINE)
write_text(EPIC, text, nl)

# ---- attention board ----
board, nl = read_text(BOARD)
head = "| flat_warm_body | in_progress | implementation | claude | fable_0 | none | Green on the working copy"
start = board.index(head)
end = board.index("\n", start)
row = board[start:end]
new_row = (
    "| flat_warm_body | review | handoff | claude | fable_0 | owner-owed: full-tree suites and gauntlet on 0.2.8221 | "
    "Owner runs the full-tree suites and the gauntlet on 0.2.8221; on green the task and story are turned in and "
    "the door lane story opens (epoch audit first). | "
    "S9 landed at 0.2.8221 (-7..-17% of the plan on roots with unique providers); S11 retired as already true; "
    "S2a parked. | Owner reports the suites/gauntlet or turns the lane in; then the door lane. | "
    f"{TASK_REL} | {TS} | REQUIRED |"
)
assert row.count("|") == new_row.count("|"), (row.count("|"), new_row.count("|"))
board = board[:start] + new_row + board[end:]
board = replace_once(
    board,
    "- flat_warm_body: SWITCH_TRIGGER is the harness verdict (S9/S11 within noise -> DECISION_REQUEST), or the\n"
    "  landing and turn-in; then the door lane story opens (audit first). The PGO epic stays queued with no row\n"
    "  (owner: ignore it). RESUME_HIERARCHY:",
    "- flat_warm_body: SWITCH_TRIGGER is the owner's turn-in of the landed S9 lane (0.2.8221; owner-run suites and\n"
    "  gauntlet owed); then the door lane story opens (epoch audit first, patch docs before any door edit). The PGO\n"
    "  epic stays queued with no row (owner: ignore it). RESUME_HIERARCHY:",
    "details")
write_text(BOARD, board, nl)

# ---- artifact board ----
art, nl = read_text(ARTBOARD)
patch_row_head = f"| {TASK_REL} | system_docs/patches/active/flat_warm_body_2026_10_03/ | patch_doc | active |"
start = art.index(patch_row_head)
end = art.index("\n", start) + 1
art = art[:start] + art[end:]
cleared = (
    f"| {TASK_REL} | system_docs/patches/completed/flat_warm_body_2026_10_03/ | promote_to_documentation | "
    "Promoted to src_architecture and src_components (owner-store constants, 0.2.8221) and the graph at landing; "
    f"three patch docs archived. | {TS} |\n"
)
art = replace_once(art, "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n",
                   "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n" + cleared, "cleared begin")
old_next = ("The S9 harness extension, the interleaved A/B runs and medians, the micro-benchmark, lane scripts and "
            "logs. | 2026-10-03T21:42:10Z | REQUIRED |")
new_next = ("The S9 harness extension, the interleaved A/B runs and medians, the micro-benchmark, apply_s9.py and "
            "land_docs_s9.py (landed at 0.2.8221), the red/green, shard, graph, rebuild and check logs. "
            f"| {TS} | REQUIRED |")
art = replace_once(art, old_next, new_next, "artifacts row")
write_text(ARTBOARD, art, nl)
print("landed", TS)
