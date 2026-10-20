"""S5: move the story to in_progress, record the baseline copies, route the board row."""
import datetime
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
STORY = ROOT / "tickets/stories/2026-10-15_managed_dispense_codegen_story.md"
BOARD = ROOT / "attention_board.md"

story = STORY.read_text(encoding="utf-8")
edits = [
    ("- Status: ready\n", "- Status: in_progress\n"),
    ("- Updated: 2026-10-15T09:29:51Z\n", f"- Updated: {NOW}\n"),
    (
        """## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: ready once S4 lands.
""",
        f"""## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: S4 landed and closed (0.2.8244, 2026-10-15T15:39:41Z); S5 starts with the baseline and U7/U8.
- prior: draft -> ready (2026-10-15T09:29:51Z): ready once S4 lands.
""",
    ),
]
for old, new in edits:
    assert story.count(old) == 1, old[:60]
    story = story.replace(old, new)
note = f"""- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: S5 started on 0.2.8244. The before-image is kept verbatim: the 18 files this story may change (the lowering,
    the door compiler, the override runtime and resolver, the generalized hydrator, manifest and no-overrides
    compiler, the many_only manifest, solo discovery, the two `_is_shared_existence` strategies, the lane plan,
    shared_compiler_executions, caching_system, conduit.py, meld.py) copied to baseline_0_2_8244/ with SHA256SUMS,
    so the emission diff loads the old modules beside the new ones (the D4/D5 probe's method). Order: read the seams
    whole (U7, U8), record them, write the S5 patches and the mapping note, capture the baseline emission over
    representative shapes and the certification harness worlds, red tests, implement, emission diff, green.
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/baseline_0_2_8244/SHA256SUMS.txt:1-18
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/probes/emission_diff_d45.py:1-137
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:300-340
  IMPACT: The byte-identity gate can be checked against a fixed before-image whatever the edit order.
  NEXT: Read site_plan_lowering.py whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

"""
anchor = "## Closure Confirmation"
assert story.count(anchor) == 1
story = story.replace(anchor, note + anchor)
old_h = """## Context / Handoff Summary
- Scope: S5 - dispense through plans and doors; managed_spell_meld.
- State: ready, blocked on S4.
- Next: baseline emission capture.
"""
new_h = """## Context / Handoff Summary
- Scope: S5 - dispense through plans and doors; managed_spell_meld.
- State: in_progress on 0.2.8244; the before-image is in baseline_0_2_8244/ (PLAN note).
- Next: read the seams whole (U7, U8), then the S5 patches.
"""
assert story.count(old_h) == 1
story = story.replace(old_h, new_h)
STORY.write_text(story, encoding="utf-8")

board = BOARD.read_text(encoding="utf-8")
old_row = "| melder_object_pools | ready | discovery | claude | melder_0 | none | S5:"
assert board.count(old_row) == 1
board = board.replace(old_row, "| melder_object_pools | in_progress | discovery | claude | melder_0 | none | S5:")
BOARD.write_text(board, encoding="utf-8")
print("S5 started", NOW)
