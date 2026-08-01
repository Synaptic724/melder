# Task: FINDING-4 - frame posture cheatsheet hardcodes a count that drifted

## Metadata
- Task ID: TASK-2026-08-01-frame-posture-cheatsheet-count-drift
- Status: review
- Owner: cowork
- Agent Name: examples_0
- Priority: p3
- Parent: EPIC-2026-08-01-ux-aix-harness-red-remediation
- Created: 2026-08-01T11:18:00Z
- Updated: 2026-08-01T12:58:00Z

## Problem / Opportunity
1 red. `03_advanced/07_frame_posture_cheatsheet.py` prints 17 items from its own
dict and then asserts `total == 15`. The count is hand-maintained over a surface
that grew.

## Context
This is the same silent-derived-count failure mode `special_instructions/new_skills/
system_doc_index_generation.md` was written about: the C1 Code Map generated at 550
modules and was silently wrong at 553. A hardcoded number describing a live surface
will drift again, so the fix should remove the class of bug, not just the instance.

## Ticket Contract
- ENTRY_GATE: red reproduced; live knob count established from source. MET.
- EXECUTION_BOUNDARY: `UX_and_AIX_experiences/03_advanced/07_frame_posture_cheatsheet.py`
  ONLY. No source.
- DEPENDENCIES: held behind FINDING-1 and FINDING-3 per the epic's tranche order.
- EXIT_GATE: example green; the assertion can no longer disagree with the list it
  describes.
- FAILURE_ESCALATION: DECISION_REQUEST if the cheatsheet turns out to be missing
  knobs the live posture actually has - that would be a documentation gap, not
  arithmetic.

## Applicable Anti-Patterns
- Bumping 15 to 17 and moving on. That fixes today's number and guarantees the same
  red the next time a knob lands.

## Acceptance Criteria
- [ ] The assertion is derived from the example's own dict, not hardcoded.
- [ ] The cheatsheet's knob list matches the live `AethericFrameConfiguration`
      surface, or the difference is deliberate and stated.
- [ ] Example green on an owner 3.14t run.

## Validation Plan
Owner harness run.

## Notes

- DATETIME: 2026-08-01T11:18:00Z
  TYPE: FACT
  CLAIM: Arithmetic drift with a knowable cause. The example's dict contains 17
    entries: 14 real posture knobs plus 3 preset METHODS
    (`automatic_defaults`, `dynamic_defaults`, `with_defaults`), which are not
    knobs. The live `AethericFrameConfiguration` exposes exactly those 14 public
    knobs: system_state, ai_native_enabled, rift_enabled,
    shared_framewide_spellbook_configuration, system_caching_enabled,
    system_cache_root_path, and the seven `disable_*` brakes, plus
    max_transaction_wait_time_in_seconds. The stale 15 is consistent with a former
    12-knob posture (12 + 3 presets); the caching pair was added later, the dict was
    updated, the hardcoded total was not.
  EVIDENCE:
    - UX_and_AIX_experiences/03_advanced/07_frame_posture_cheatsheet.py:40-62
    - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py
  IMPACT: Two questions to settle, not one: the arithmetic, and whether presets
    belong in a count labelled "posture knobs mapped" at all. They are methods, so
    counting them inflates the number a reader will quote.
  NEXT: Derive the total from the dict itself; consider printing knobs and presets
    as separate totals so the label stays honest.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Artifact Links (Optional)
- none.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Context / Handoff Summary
Cause identified and the live number established at 14 knobs + 3 presets. Held
behind the two contract rulings per the epic's tranche order.
