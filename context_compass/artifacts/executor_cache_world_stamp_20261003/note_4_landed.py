"""Landing FACT note, ticket state -> review, board row and artifact board sync."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths  # noqa: E402

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
TASK_REL = "tickets/tasks/2026-10-03_require_world_stamp_for_executor_cache_full_hit_task.md"
TASK = os.path.join(CC, TASK_REL)
BOARD = os.path.join(CC, "attention_board.md")
ARTBOARD = os.path.join(CC, "artifact_board.md")
TS = now_utc()

NOTE = f"""- DATETIME: {TS}
  TYPE: FACT
  CLAIM: Landed on the tree at 0.2.8220 (fable_1's rebind lane had notched 0.2.8219 and closed its rebuild window at
    21:01Z; no shared file was edited concurrently). `apply_world_stamp.py --root <tree>` (src + tests, per-line
    endings kept), `land_docs.py` (notch, release-note section "Fixed: a warm creation cache no longer replays an
    executor compiled in another world" plus the packaging bullet and the rebuild line, the architecture's conjure
    sequence, operational invariant, failure mode, code map (spellbook_creation_system.py 3482 lines,
    caching_system.py 887) and handoff entry, the component map's generation-19 bullet and conjure flow, the
    conjure citation 616-721 remeasured to 616-740 in both maps; patch docs archived under
    system_docs/patches/completed/executor_cache_world_stamp_2026_10_03/). Both indexes --check OK; the citation
    bounds recipe reports no problem. Graph: extract --strict, the two descriptors' responsibilities extended,
    both nodes accepted, assembled (584 sections, 1212 nodes, 1394 edges). Assets rebuilt in the VM mirror and
    copied back (8 files; bind guard unchanged at 620), --check OK on the tree; LLM bundles rebuilt and --check
    OK; no .git/index.lock. Post-landing shards on a fresh copy of the tree (GIL off): unit spellbook+utilities+
    root files+build_assets 3362 passed; component 2290 passed; integration spellbook+conduit 878 passed. Not
    run: integration aether/crystallizer/mutation_research/multithreading/live_sim on the landed copy (the
    aether+crystallizer+mutation_research shard passed on the working copy before landing), the owner's
    full-tree suites and the gauntlet.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:1-3
  - system_docs/src_architecture_index.md:14-20
  - system_docs/src_components_index.md:14-20
  - artifacts/executor_cache_world_stamp_20261003/land_docs.py:1-60
  - artifacts/executor_cache_world_stamp_20261003/logs/assets_check_tree.log:1-3
  - artifacts/executor_cache_world_stamp_20261003/logs/llm_bundles_check.log:1-3
  - artifacts/executor_cache_world_stamp_20261003/logs/post_landing_unit_spellbook_utilities_root.log:1-1
  - artifacts/executor_cache_world_stamp_20261003/logs/post_landing_component.log:1-1
  - artifacts/executor_cache_world_stamp_20261003/logs/post_landing_integration_spellbook_conduit.log:1-1
  IMPACT: The defect is fixed on the tree with unit, integration and component regression tests; one contract was
    retired on purpose (a removed spell is a changed world: one recompile, then full hits) - the owner's call to
    keep or revert that at turn-in. Lane in review.
  NEXT: owner runs the full-tree suites and the gauntlet and turns the lane in (with the S8 and matcher lanes).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
bad = check_line_lengths(NOTE)
if bad:
    raise SystemExit(f"lines over cap: {bad}")
text, nl = read_text(TASK)
text = replace_once(text, "\n## Context / Handoff Summary\n", "\n" + NOTE + "## Context / Handoff Summary\n", "handoff")
text = replace_once(text, "- Status: in_progress\n", "- Status: review\n", "status")
text = replace_once(text, "- Updated: 2026-10-03T20:43:41Z", f"- Updated: {TS}", "updated")
text = replace_once(
    text,
    "- transition_reason: Opened on the owner's word (2026-10-03T20:36:13Z); the RISK note of the S8 task (reproduced\n"
    "  twice, cold cache resolves) is the entry evidence.\n",
    "- transition_reason: Opened on the owner's word (2026-10-03T20:36:13Z); the RISK note of the S8 task (reproduced\n"
    "  twice, cold cache resolves) is the entry evidence.\n"
    "- from_state: in_progress\n"
    "- to_state: review\n"
    f"- transition_reason: Landed at 0.2.8220 with tests, docs, graph, patch docs archived, assets and bundles ({TS});\n"
    "  owner-run suites and gauntlet pending.\n", "transition")
text = replace_once(
    text,
    "- [ ] Land on the tree (CRLF), notch above `__version__` (0.2.8218 now), release-note section, docs, graph\n",
    "- [x] Land on the tree (CRLF), notch above `__version__` (0.2.8218 now), release-note section, docs, graph\n", "step4")
text = replace_once(
    text,
    "## Validation\n- Not run.\n- Recommended commands:\n",
    "## Validation\n"
    "- Working copy before landing and a fresh copy of the landed tree (GIL off, sharded): unit spellbook+utilities+\n"
    "  root+build_assets 3362, component 2290, integration spellbook+conduit 878 passed on the landed copy;\n"
    "  integration aether+crystallizer+mutation_research 1093 passed on the working copy. Not run: integration\n"
    "  multithreading and live_sim, the owner's full-tree suites, the gauntlet.\n"
    "- Recommended commands:\n", "validation")
text = replace_once(
    text,
    "  - system_docs/patches/active/executor_cache_world_stamp_2026_10_03/ (patch docs; written before the edit)\n",
    "  - system_docs/patches/completed/executor_cache_world_stamp_2026_10_03/ (patch docs; promoted and archived)\n", "artifact path")
text = text.rstrip("\n").replace(
    "## Project-Specific Additions",
    f"STATE {TS}: REVIEW. Landed at 0.2.8220; owner-run suites and gauntlet pending; the retired surplus full-hit\n"
    "contract is the owner's call at turn-in. Resume from the latest note's NEXT.\n\n## Project-Specific Additions") + "\n"
write_text(TASK, text, nl)

board, nl = read_text(BOARD)
old_row_start = "| executor_cache_world_stamp | in_progress | discovery | claude | fable_0 | none | "
assert board.count(old_row_start) == 1
start = board.index(old_row_start)
end = board.index("\n", start) + 1
new_row = (
    "| executor_cache_world_stamp | review | handoff | claude | fable_0 | none | "
    "Owner runs the full-tree suites and the gauntlet on 0.2.8220 and turns it in with the S8 and matcher lanes; "
    "owner's call on the retired surplus full hit (a removed spell is a changed world: one recompile). | "
    "The executor cache admits a full hit only on the recorded world stamp (generation 19); the stale-executor "
    "defect is fixed with unit, integration and component regressions; landed with notch, docs, graph, assets. | "
    "Owner turns it in or reports a red suite. | "
    f"{TASK_REL} | {TS} | REQUIRED |\n"
)
board = board[:start] + new_row + board[end:]
old_detail = (
    "- executor_cache_world_stamp: SWITCH_TRIGGER is the fix landed and turned in, or a CONFLICT when fable_1's\n"
    "  rebind repair claims spellbook_creation_system.py first (one writer per file), or a DECISION_REQUEST if an\n"
    "  existing cache test depends on a full hit across a changed world. RESUME_HIERARCHY:\n")
new_detail = (
    "- executor_cache_world_stamp: SWITCH_TRIGGER is the owner's turn-in of the landed fix (0.2.8220) or a red\n"
    "  suite; the file overlap with fable_1's rebind lane did not occur (DevOps control plane only). RESUME_HIERARCHY:\n")
board = replace_once(board, old_detail, new_detail, "detail")
write_text(BOARD, board, nl)

art, nl = read_text(ARTBOARD)
old_patch_row_start = f"| {TASK_REL} | system_docs/patches/active/executor_cache_world_stamp_2026_10_03/ | patch_doc | active | "
assert art.count(old_patch_row_start) == 1
s = art.index(old_patch_row_start)
e = art.index("\n", s) + 1
art = art[:s] + art[e:]
cleared = (
    f"| {TASK_REL} | system_docs/patches/completed/executor_cache_world_stamp_2026_10_03/ | promote_to_documentation | "
    "Promoted to src_architecture and src_components (executor-cache world stamp, 0.2.8220) and the graph at landing; "
    f"three patch docs archived. | {TS} |\n"
)
art = replace_once(art, "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n",
                   "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n" + cleared, "cleared begin")
old_art_row = (
    f"| {TASK_REL} | artifacts/executor_cache_world_stamp_20261003/ | implementation_evidence | active | "
    "retain_as_reference | Lane scripts, the red/green component runs and the shard logs of the working copy. | ")
assert art.count(old_art_row) == 1
s = art.index(old_art_row)
e = art.index("\n", s) + 1
art = art[:s] + (
    f"| {TASK_REL} | artifacts/executor_cache_world_stamp_20261003/ | implementation_evidence | active | "
    "retain_as_reference | apply_world_stamp.py and land_docs.py (landed at 0.2.8220), the red run on the tree's rule, "
    f"the green and shard logs, the rebuild and check logs. | {TS} | REQUIRED |\n") + art[e:]
write_text(ARTBOARD, art, nl)
print("closed-out", TS)
