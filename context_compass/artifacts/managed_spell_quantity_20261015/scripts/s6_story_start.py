"""S6: move the story to in_progress, record the plan, route the board row."""
import datetime
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
STORY = ROOT / "tickets/stories/2026-10-15_managed_ownership_transfer_story.md"
BOARD = ROOT / "attention_board.md"

story = STORY.read_text(encoding="utf-8")
edits = [
    ("- Status: ready\n", "- Status: in_progress\n"),
    ("- Updated: 2026-10-15T09:29:51Z\n", f"- Updated: {NOW}\n"),
    (
        """## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: ready once S5 lands.
""",
        f"""## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: S5 landed and closed (0.2.8245, 2026-10-15T18:15:07Z); S6 starts with the transfer path and U9.
- prior: draft -> ready (2026-10-15T09:29:51Z): ready once S5 lands.
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
  CLAIM: S6 started on 0.2.8245. transfer_of_ownership.py is unchanged since 0.2.8240 (S1-S5 did not touch it); S3 and
    S4 already give a pool its `managed` extract/restore row and make the registry follow the store. Order: read
    transfer_of_ownership.py whole (execute, the flip, the inactive-member migration, the creation move, teardown
    and rollback), `_apply_notch` and `_reactivate_owned_spell` (U9), `Spell._add_owned_conduit` and Creations'
    managed rows; probe a managed transfer as it stands (move, no move, rollback, a notch after a transfer, a release
    after the move); then the S6 component patch and mapping note, red tests, the change, validation.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:315-336
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:1019-1050
  IMPACT: S6 may need few or no transfer edits: the patch is written after the probe shows what a transfer already
    does with a pool.
  NEXT: Read transfer_of_ownership.py whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

"""
anchor = "## Closure Confirmation"
assert story.count(anchor) == 1
story = story.replace(anchor, note + anchor)
old_h = """## Context / Handoff Summary
- Scope: S6 - transfer.
- State: ready, blocked on S5.
- Next: read U9.
"""
new_h = """## Context / Handoff Summary
- Scope: S6 - managed pools through ownership transfer (move, no move, rollback, parked members) and the notch (U9).
- State: in_progress on 0.2.8245 (PLAN note).
- Next: read the transfer path and `_apply_notch` whole, then probe a managed transfer as it stands.
"""
assert story.count(old_h) == 1
story = story.replace(old_h, new_h)
STORY.write_text(story, encoding="utf-8")

board = BOARD.read_text(encoding="utf-8")
old_row = "| melder_object_pools | ready | discovery | claude | melder_0 | none | S6:"
assert board.count(old_row) == 1
board = board.replace(old_row, "| melder_object_pools | in_progress | discovery | claude | melder_0 | none | S6:")
BOARD.write_text(board, encoding="utf-8")
print("S6 started", NOW)
