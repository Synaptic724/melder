"""Park the PGO epic in tickets/epics/backlog/ on the owner's word (2026-10-04: keep it in the backlog)."""
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "executor_cache_world_stamp_20261003"))
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths  # noqa: E402

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
EPIC = "tickets/epics/2026-09-27_adaptive_creation_contexts_epic.md"
PARKED = "tickets/epics/backlog/2026-09-27_adaptive_creation_contexts_epic.md"
TS = now_utc()
path = os.path.join(CC, EPIC)
text, nl = read_text(path)
text = replace_once(text, "- Status: ready\n", "- Status: ready (parked)\n", "status")
text = replace_once(text, "- Updated: 2026-10-01T00:57:45Z\n", f"- Updated: {TS}\n", "updated")
transition = (
    "- from_state: ready\n- to_state: ready (parked)\n"
    f"- transition_reason: Parked in the backlog on the owner's word ({TS}: \"keep your pgo in the backlog\")\n"
    "  after the static epic was turned in; its thirteen stories and the probe task were already in the backlog.\n"
)
m = re.search(r"## State Transition Event\n(?:.*\n)*?(?=\n## )", text)
assert m, "transition section"
text = text[:m.end()] + transition + text[m.end():]
note = (
    f"- DATETIME: {TS}\n"
    "  TYPE: DECISION\n"
    "  CLAIM: Owner (2026-10-04): the static epic is turned in (S1, S8, S9 shipped; the door lane parked) and this\n"
    "    epic stays in the backlog, not closed. Nothing of it was implemented; the certification table\n"
    "    (artifacts/pgo_strategies_20260927/) and the thirteen story drafts are its record. The static lanes it was\n"
    "    queued behind no longer exist, so it reopens only on the owner's word.\n"
    "  EVIDENCE:\n"
    "  - tickets/epics/completed/2026-10-01_static_codegen_and_door_strategies_epic.md:1-10\n"
    "  IMPACT: No active or ready lane of fable_0 remains; the board carries no row for this epic.\n"
    "  NEXT: none until the owner reopens it.\n"
    "  REREAD: HELPFUL\n"
    "  SCORE_0_TO_10: 7\n\n"
)
bad = check_line_lengths(transition + note, exempt=r"^  - tickets/")
if bad:
    raise SystemExit(f"lines over cap: {bad}")
text = replace_once(text, "\n## Closure Confirmation\n", "\n" + note + "## Closure Confirmation\n", "notes end")
text = text.rstrip("\n").replace(
    "\n## Project-Specific Additions",
    f"\nSTATE {TS}: PARKED (backlog_by_owner). The static epic is closed; this epic and its thirteen stories stay in the\n"
    "backlog until the owner reopens the PGO lane; no board row.\n\n## Project-Specific Additions") + "\n"
write_text(path, text, nl)
target = os.path.join(CC, PARKED)
assert not os.path.exists(target), target
shutil.move(path, target)
print("parked", EPIC, "->", PARKED, TS)
