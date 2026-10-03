"""MEASURE note: the whole suite, sharded, on a fresh copy of the landed tree."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths  # noqa: E402

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
TASK = os.path.join(CC, "tickets/tasks/2026-10-03_require_world_stamp_for_executor_cache_full_hit_task.md")
BOARD = os.path.join(CC, "attention_board.md")
TS = now_utc()
NOTE = f"""- DATETIME: {TS}
  TYPE: MEASURE
  CLAIM: Owner (2026-10-03: "go ahead and finish your fix") - the remaining shards ran on the fresh copy of the
    landed tree (0.2.8220, CPython 3.14.7t, GIL off, VM): integration multithreading + live_sim 51 passed (1
    xfailed); integration aether + crystallizer + mutation_research 1093 passed (3 xfailed); unit aether +
    crystallizer + mutation_research + the package metadata files 5062 passed. With the earlier post-landing
    shards (unit spellbook/utilities/root/build_assets 3362, component 2290, integration spellbook+conduit 878)
    every test directory under tests/unit, tests/component and tests/integration has passed on the landed tree
    (sharded runs on the VM, not one owner-run invocation). Not run: the owner's full-tree suites (one
    invocation, both builds) and the gauntlet.
  EVIDENCE:
  - artifacts/executor_cache_world_stamp_20261003/logs/post_landing_integration_multithreading_live_sim.log:1-1
  - artifacts/executor_cache_world_stamp_20261003/logs/post_landing_integration_aether_crystallizer_mr.log:1-1
  - artifacts/executor_cache_world_stamp_20261003/logs/post_landing_unit_aether_crystallizer_mr.log:1-1
  - artifacts/executor_cache_world_stamp_20261003/logs/post_landing_component.log:1-1
  IMPACT: Nothing in the lane is left undone on the agent side; the retired surplus full hit stands (the owner
    did not object at the report).
  NEXT: owner's turn-in of this lane with the S8 and matcher lanes (or a red suite / gauntlet number).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

"""
bad = check_line_lengths(NOTE)
if bad:
    raise SystemExit(f"lines over cap: {bad}")
text, nl = read_text(TASK)
text = replace_once(text, "\n## Context / Handoff Summary\n", "\n" + NOTE + "## Context / Handoff Summary\n", "handoff")
text = replace_once(text, "- Updated: 2026-10-03T21:09:07Z", f"- Updated: {TS}", "updated")
text = replace_once(
    text,
    "- Working copy before landing and a fresh copy of the landed tree (GIL off, sharded): unit spellbook+utilities+\n"
    "  root+build_assets 3362, component 2290, integration spellbook+conduit 878 passed on the landed copy;\n"
    "  integration aether+crystallizer+mutation_research 1093 passed on the working copy. Not run: integration\n"
    "  multithreading and live_sim, the owner's full-tree suites, the gauntlet.\n",
    "- Fresh copy of the landed tree (0.2.8220, GIL off, sharded): unit 3362 + 5062, component 2290, integration\n"
    "  878 + 1093 + 51 passed - every directory under tests/unit, tests/component and tests/integration. Not run:\n"
    "  the owner's full-tree suites (one invocation, both builds) and the gauntlet.\n", "validation")
write_text(TASK, text, nl)
board, nl = read_text(BOARD)
old = "| tickets/tasks/2026-10-03_require_world_stamp_for_executor_cache_full_hit_task.md | 2026-10-03T21:09:07Z | REQUIRED |"
board = replace_once(board, old, old.replace("2026-10-03T21:09:07Z", TS), "row ts")
write_text(BOARD, board, nl)
print("noted", TS)
