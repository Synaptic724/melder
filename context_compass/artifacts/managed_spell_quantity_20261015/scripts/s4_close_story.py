"""S4 turn-in: close STORY-2026-10-15-release_managed_spell (summary, status, transition, checklists, resume view)."""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
NOW = sys.argv[2]
STORY = ROOT / "tickets/stories/2026-10-15_release_managed_spell_story.md"

story = STORY.read_text(encoding="utf-8")
title = "# Story: release_managed_spell - the class-keyed registry, the lease and the package-root exports\n"
summary = f"""{title}
- Completed: {NOW}
- Summary: landed 0.2.8244 - `ReleaseManagedSpell` (the Aether-owned singleton: register/unregister following the
  root stores, the lock-free class-keyed release and the cold resolver, `managed`, `release_all`, `describe`),
  `ManagedSpellLease`, the Creations register/unregister calls, the cleanup-safe reads they need, four package-root
  exports. Whole tree green in both GIL modes. Release-note section "`Existence.managed_spell_quantity`: objects
  leased from a root-owned pool and released back" extended.
"""
edits = [
    (title, summary),
    ("- Status: in_progress\n", "- Status: done\n"),
    (
        """## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: S3 landed and closed (0.2.8243, 2026-10-15); S4 starts with U11.
""",
        """## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: acceptance criteria met with red-then-green tests in both GIL modes and the whole tree green in
  both modes; routing measured; notched 0.2.8244 (delegated routine closure under the owner's go-ahead).
- prior: ready -> in_progress (2026-10-15T14:16:58Z): S3 landed and closed (0.2.8243); S4 started with U11.
""",
    ),
    ("- [ ] Implement; green in both GIL modes.\n", "- [x] Implement; green in both GIL modes.\n"),
    ("- [ ] Notch, release note, epic spec update, close, board sync.\n",
     "- [x] Notch, release note, epic spec update, close, board sync.\n"),
    ("- [ ] Enforce Ticket Microcycle across all linked tasks.\n",
     "- [x] Enforce Ticket Microcycle across all linked tasks.\n"),
    ("- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.\n",
     "- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.\n"),
    ("- [ ] No story-state transition without linked task-state evidence.\n",
     "- [x] No story-state transition without linked task-state evidence.\n"),
    ("- [ ] No closure while required tasks remain active or un-routed.\n",
     "- [x] No closure while required tasks remain active or un-routed.\n"),
    ("- [ ] No cross-task synthesis claims without ticket-note evidence pointers.\n",
     "- [x] No cross-task synthesis claims without ticket-note evidence pointers.\n"),
    ("- [ ] No `src/` edit before the component patch and the mapping note exist.\n",
     "- [x] No `src/` edit before the component patch and the mapping note exist.\n"),
    ("- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n",
     "- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n"),
    ("- [ ] Applicable anti-pattern checks are clear or escalated with evidence.\n",
     "- [x] Applicable anti-pattern checks are clear or escalated with evidence.\n"),
]
for old, new in edits:
    assert story.count(old) == 1, old[:70]
    story = story.replace(old, new)
start = story.index("## Context / Handoff Summary")
end = story.index("## Project-Specific Additions")
handoff = """## Context / Handoff Summary
- Scope: S4 - the Aether-owned `ReleaseManagedSpell` singleton, `ManagedSpellLease`, the Creations register and
  unregister calls, the cleanup-safe reads they need, the package-root exports.
- State: done; landed 0.2.8244 (the FACT, DECISION and MEASURE notes; runs/s4_validation_index.md).
- Open for the owner's review: the lease on the package root and the holding-root record (DECISION note).
- Next: S5 (STORY-2026-10-15-managed_dispense_codegen) - meld leases through the emitted plans and
  `Conduit.managed_spell_meld` returns a `ManagedSpellLease`.

"""
story = story[:start] + handoff + story[end:]
updated_lines = [line for line in story.splitlines() if line.startswith("- Updated: ")]
assert len(updated_lines) == 1
story = story.replace(updated_lines[0], f"- Updated: {NOW}")
STORY.write_text(story, encoding="utf-8")
print("story closed", NOW)
