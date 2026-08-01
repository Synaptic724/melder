# Task: FINDING-2 - 35_one_config_every_book collides two unnamed root conduits

## Metadata
- Task ID: TASK-2026-08-01-shared-config-unnamed-conjure-collision
- Status: review
- Owner: cowork
- Agent Name: examples_0
- Priority: p3
- Parent: EPIC-2026-08-01-ux-aix-harness-red-remediation
- Created: 2026-08-01T11:18:00Z
- Updated: 2026-08-01T12:58:00Z

## Problem / Opportunity
1 red. `02_intermediate/35_one_config_every_book.py` conjures two books in the same
frame with no name. Both root conduits are born `default`, and the frame correctly
refuses the second. The example is wrong; the runtime is right.

## Context
The lesson teaches "one configuration object, every book". Sharing config is the
point; the unnamed conjure is incidental and was never the subject of the lesson.

## Ticket Contract
- ENTRY_GATE: red reproduced with traceback and the passing sibling identified. MET.
- EXECUTION_BOUNDARY: `UX_and_AIX_experiences/02_intermediate/35_one_config_every_book.py`
  ONLY. No source.
- DEPENDENCIES: held behind FINDING-1 and FINDING-3 per the epic's tranche order.
- EXIT_GATE: example green; lesson still teaches shared configuration, not naming.
- FAILURE_ESCALATION: none expected; escalate if naming turns out to change what
  the lesson demonstrates.

## Applicable Anti-Patterns
- Deleting the second conjure to dodge the collision - that would delete the lesson.

## Acceptance Criteria
- [ ] Example passes on an owner 3.14t run.
- [ ] The shared-configuration teaching point is unchanged.
- [ ] Naming is presented as incidental, not as the lesson.

## Validation Plan
Owner harness run. Agent claims nothing.

## Notes

- DATETIME: 2026-08-01T11:18:00Z
  TYPE: FACT
  CLAIM: Runtime is correct and the fix is one line, PROVEN by a passing sibling
    rather than by argument. `AethericFrame.register_root_conduit` refuses a
    duplicate root-conduit name within a frame, and the example calls
    `book_a.conjure()` / `book_b.conjure()` unnamed, so both arrive as `default`.
    The probe `test_probe_manual_config_share_across_books` teaches the SAME shared-
    config lesson and PASSES because it names them: `conjure(name="share-a")` and
    `conjure(name="share-b")`.
  EVIDENCE:
    - UX_and_AIX_experiences/02_intermediate/35_one_config_every_book.py:99-100
    - UX_and_AIX_experiences/pytest_examples/test_intermediate_probes.py:19-20
    - src/melder/aether/aetheric_frame/aetheric_frame.py:363-372
  IMPACT: Lowest-risk red in the epic. No owner ruling needed.
  NEXT: Name both conjures, mirroring the probe; add one comment line so a reader
    learns that root-conduit names are frame-unique.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Artifact Links (Optional)
- none.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Context / Handoff Summary
Diagnosed, one-line fix identified, deliberately held behind the two contract
rulings so the suite's red count keeps pointing at the library defect.
