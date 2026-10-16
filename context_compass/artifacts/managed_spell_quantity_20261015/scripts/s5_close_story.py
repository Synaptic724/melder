"""S5 turn-in: close STORY-2026-10-15-managed_dispense_codegen (summary, status, transition, checklists, resume view)."""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
NOW = sys.argv[2]
STORY = ROOT / "tickets/stories/2026-10-15_managed_dispense_codegen_story.md"

story = STORY.read_text(encoding="utf-8")
title = "# Story: managed_dispense_codegen - leases through emitted plans, doors and Conduit.managed_spell_meld\n"
summary = f"""{title}
- Completed: {NOW}
- Summary: landed 0.2.8245 - meld and injection lease from the managed pools through the emitted plans (leasing and
  fresh managed sites, the inline pop, the reserve-first miss with recorded children, the widened F9 return), the
  door rows on the many templates, the per-path predicates, the solo decline, the manifest key, the specializer
  decline and `Conduit.managed_spell_meld`. Whole tree green in both GIL modes; every non-managed emitted plan
  byte-identical. Release-note section "`Existence.managed_spell_quantity`: objects leased from a root-owned pool
  and released back" extended.
"""
edits = [
    (title, summary),
    ("- Status: in_progress\n", "- Status: done\n"),
    (
        """  into the object's record, the failed-construction return, overrides, the door, the specializer decline, cache
  generation 21.
""",
        """  into the object's record, the failed-construction return, overrides, the door, the specializer decline (cache
  generation 21 dropped by the DECISION note of 2026-10-15T16:18:21Z).
""",
    ),
    (
        """## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: S4 landed and closed (0.2.8244, 2026-10-15T15:39:41Z); S5 starts with the baseline and U7/U8.
- prior: draft -> ready (2026-10-15T09:29:51Z): ready once S4 lands.
""",
        """## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: acceptance criteria met with red-then-green tests in both GIL modes, the whole tree green in
  both modes, the emission gate identical and the warm cycle measured; notched 0.2.8245 (delegated routine closure
  under the owner's go-ahead).
- prior: ready -> in_progress (2026-10-15T15:47:49Z): S4 landed and closed (0.2.8244); S5 started with the baseline
  and U7/U8.
- prior: draft -> ready (2026-10-15T09:29:51Z): ready once S4 lands.
""",
    ),
    ("- [ ] Red tests: lowering shapes, component dispense tests, integration tests.\n",
     "- [x] Red tests: lowering shapes, component dispense tests, integration tests.\n"),
    ("- [ ] Implement; emission diff; green in both GIL modes; the spellbook, conduit and codegen suites.\n",
     "- [x] Implement; emission diff; green in both GIL modes; the spellbook, conduit and codegen suites.\n"),
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
    ("- U7, U8 (epic B7) - read in source before the patch.\n",
     "- None. U7 and U8 answered (DECISION note 2026-10-15T15:50:36Z, FACT note 2026-10-15T16:06:32Z); the pre-conjure\n"
     "  staging gap (FACT note 2026-10-15T16:18:21Z) goes to S6 and the owner.\n"),
    ("- 2026-10-15 (melder_0): per-path sites; F9 return kept; own-parameter overrides unpooled (epic Decision Log).\n",
     "- 2026-10-15 (melder_0): per-path sites; F9 return kept; own-parameter overrides unpooled (epic Decision Log).\n"
     "- 2026-10-15 (melder_0): the dispense design (DECISION note 2026-10-15T16:18:21Z) - door rows on the many\n"
     "  templates, no cache generation 21, F9 widened to any failure before the consumer exists and to a lost race,\n"
     "  one consumer per leasing site; `managed_spell_meld` gives a fresh own-override object to the pool on release\n"
     "  (epic Decision Log, open to the owner's review).\n"),
]
for old, new in edits:
    assert story.count(old) == 1, old[:70]
    story = story.replace(old, new)
start = story.index("## Context / Handoff Summary")
end = story.index("## Project-Specific Additions")
handoff = """## Context / Handoff Summary
- Scope: S5 - leases through emitted plans and doors; `Conduit.managed_spell_meld`.
- State: done; landed 0.2.8245 (the FACT, DECISION and MEASURE notes; runs/s5_validation_index.md; the emission diff
  identical over 4461 entries).
- Open for the owner's review: `managed_spell_meld` with own-parameter overrides gives the fresh object to the pool on
  release (epic Decision Log); the pre-conjure staging gap (FACT note 2026-10-15T16:18:21Z) goes to S6 and the owner.
- Next: S6 (STORY-2026-10-15-managed_ownership_transfer) - pools through move, no move, rollback and notch (U9).

"""
story = story[:start] + handoff + story[end:]
updated_lines = [line for line in story.splitlines() if line.startswith("- Updated: ")]
assert len(updated_lines) == 1
story = story.replace(updated_lines[0], f"- Updated: {NOW}")
long = [line for line in story.splitlines() if len(line) > 120 and not line.lstrip().startswith("- ")]
assert not long, long
STORY.write_text(story, encoding="utf-8")
print("story closed", NOW)
