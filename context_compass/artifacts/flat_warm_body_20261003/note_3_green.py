"""FACT (second stub) + MEASURE (red/green and shards) notes; step 4 ticked; STATE line; board row."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "executor_cache_world_stamp_20261003"))
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths  # noqa: E402

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
TASK_REL = "tickets/tasks/2026-10-03_certify_and_implement_site_store_constants_task.md"
TASK = os.path.join(CC, TASK_REL)
BOARD = os.path.join(CC, "attention_board.md")
TS = now_utc()
NOTES = f"""- DATETIME: {TS}
  TYPE: FACT
  CLAIM: A second fake-spell stub reads the new slot: `logging_spell` in the door-held-root unit tests builds a
    `SimpleNamespace` with `_owner_creations` and no `_dynamic_environment`, so `_owner_store_constant` raised
    AttributeError on its `unique` root case in the first shard run. The live Spell always carries the slot (False
    before ownership), so the stub gains `_dynamic_environment=False` like `_spell`; the lowering keeps the direct
    read (no `getattr` on an owned attribute). The other `_owner_creations=` stubs in `tests/` never reach the
    site-plan emitter. The component file gained the cache full-hit case the mapping note named: a repeat world
    hydrated from an untouched bundle binds `c0` to ITS Service spell's store and builds its own Service.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_door_held_root.py:132-150
  - src/melder/aether/spellbook/spell.py:1440-1470
  - artifacts/flat_warm_body_20261003/apply_s9.py:1-80
  IMPACT: One more test file in the apply script; the emitter contract is unchanged.
  NEXT: MEASURE note (red/green and the shards).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: {TS}
  TYPE: MEASURE
  CLAIM: Red on the tree's lowering (`$HOME/work/melder_tree`, the new tests copied in): the three automatic-world
    cases fail on exactly the alias line (`spells[0]._owner_creations` in the captured plan) and the three
    unchanged-behaviour cases (dynamic, unowned, per-conduit) pass. Green on `$HOME/work/melder_cc` with
    `apply_s9.py` applied: lowering unit file 50 + component 3 = 53 passed; shards: unit spellbook+utilities+root
    3197 passed / 2 skipped / 7 xfailed (12.8 s), unit aether+crystallizer+MR+build_assets 5171 passed / 1 skipped
    (19.0 s), component 2293 passed / 23 skipped / 1 xfailed (22.5 s), integration spellbook+conduit 878 passed /
    2 skipped / 2 xpassed (8.5 s), integration multithreading+live_sim 51 passed / 1 xfailed (5.7 s), integration
    aether+crystallizer+MR 1093 passed / 3 xfailed (102.8 s). CPython 3.14.7t, `-X gil=0`. Full-tree suites and
    the gauntlet: Not run (owner-run).
  EVIDENCE:
  - artifacts/flat_warm_body_20261003/logs/red_on_tree_lowering.log:1-25
  - artifacts/flat_warm_body_20261003/logs/green_unit_component.log:1-3
  - artifacts/flat_warm_body_20261003/logs/shard_unit_spellbook_utilities_root.log:1-3
  - artifacts/flat_warm_body_20261003/logs/shard_unit_aether_crystallizer_mr.log:1-3
  - artifacts/flat_warm_body_20261003/logs/shard_component.log:1-3
  - artifacts/flat_warm_body_20261003/logs/shard_integration_spellbook_conduit.log:1-3
  - artifacts/flat_warm_body_20261003/logs/shard_integration_multithreading_live_sim.log:1-3
  - artifacts/flat_warm_body_20261003/logs/shard_integration_aether_crystallizer_mr.log:1-3
  IMPACT: The working copy is green; the landing applies the same script to the tree.
  NEXT: land on the tree: `apply_s9.py --root <tree>`, notch 0.2.8221, release-note section, docs, graph,
    patch docs archived, assets and bundles last, post-landing shards, harness re-run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
bad = check_line_lengths(NOTES, exempt=r"^  - (src|tests|artifacts|system_docs)/")
if bad:
    raise SystemExit(f"lines over cap: {bad}")
text, nl = read_text(TASK)
text = replace_once(text, "\n## Context / Handoff Summary\n", "\n" + NOTES + "## Context / Handoff Summary\n", "handoff")
text = replace_once(
    text,
    "- [ ] Implement on the VM copy; emitter unit tests; component tests (both postures, transfer, full hit); shards.",
    "- [x] Implement on the VM copy; emitter unit tests; component tests (both postures, transfer, full hit); shards.",
    "step4",
)
state = (f"\nSTATE {TS}: IN_PROGRESS. S9 implemented and green on the working copy (red on the tree's lowering); "
         "landing next: apply, notch 0.2.8221,\nrelease note, docs, graph, patch docs archived, assets and bundles "
         "last. Resume from the latest note's NEXT.\n")
text = replace_once(text, "\n## Project-Specific Additions\n", state + "\n## Project-Specific Additions\n", "state")
text = re.sub(r"^- Updated: .*$", f"- Updated: {TS}", text, count=1, flags=re.MULTILINE)
write_text(TASK, text, nl)

board, nl = read_text(BOARD)
old_row_head = "| flat_warm_body | in_progress | discovery | claude | fable_0 | none | S9 certified"
start = board.index(old_row_head)
end = board.index("\n", start)
row = board[start:end]
new_row = (
    "| flat_warm_body | in_progress | implementation | claude | fable_0 | none | "
    "Green on the working copy (red on the tree); land on the tree: apply, notch 0.2.8221, release note, docs, "
    "graph, patch docs archived, assets and bundles last, post-landing shards. | "
    "S9 (site/store constants) and S11 (live key objects) certified on the five shapes; if they win, emitted with "
    "tests, docs and a notch; S2a parked. | Harness verdict recorded (ship or DECISION_REQUEST), then landed and "
    f"in review. | {TASK_REL} | {TS} | REQUIRED |"
)
assert row.count("|") == new_row.count("|"), (row.count("|"), new_row.count("|"))
board = board[:start] + new_row + board[end:]
write_text(BOARD, board, nl)
print("noted", TS)
