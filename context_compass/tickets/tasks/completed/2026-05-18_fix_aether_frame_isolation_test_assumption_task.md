# Task: fix aether frame isolation test assumption

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction before final completion. Latest lane state remains below.


## Metadata
- Task ID: TASK-2026-05-18-fix-aether-frame-isolation-test-assumption
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p2
- Created: 2026-05-18T13:55:26Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the non-Nexus full-suite blocker in the Aether integration frame-isolation
test by correcting the stale assumption about cross-frame spell ids.

## Ticket Contract
- ENTRY_GATE: full-suite non-Nexus rerun now fails in
  `test_aether_frame_isolation_for_conduit_and_spell_lookup`
- EXECUTION_BOUNDARY:
  - `tests/integration/melder/aether/test_aether_integration_frames.py`
- DEPENDENCIES:
  - current `Spellbook._get_conduit_by_spell_id(...)` behavior normalizes
    `"default"` to the caller's frame
- EXIT_GATE: the frame-isolation integration test is green with a truthful
  cross-frame lookup assertion
- FAILURE_ESCALATION: raise `BLOCKER` if the runtime path actually ignores the
  caller frame and the test is not stale

## Notes
- DATETIME: 2026-05-18T13:55:26Z
  TYPE: FACT
  CLAIM: The failing frame-isolation assertion is stale because both spellbooks
    bind the same `BasicService`, which produces the same `spell_id`. The
    default lookup path already scopes `"default"` to the caller's own frame,
    so `conduit_a.get_conduit_by_spell_id(spell_id_b)` resolves `conduit_a`
    when `spell_id_b == spell_id_a`.
  EVIDENCE:
  - tests/integration/melder/aether/test_aether_integration_frames.py:64-116
  - src/melder/spellbook/spellbook.py:1520-1544
  - src/melder/aether/conduit/conduit.py:1549-1570
  IMPACT: The test should use distinct spell identities across the two frames
    if it wants to prove cross-frame isolation.
  NEXT: patch the test to bind a different spell in frame-b, then rerun the
    targeted integration test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Bounded integration-test-assumption fix for the next non-Nexus suite blocker.
