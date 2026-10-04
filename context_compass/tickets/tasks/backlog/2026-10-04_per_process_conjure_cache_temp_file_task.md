

# Task: Give the conjure-cache emit a per-process temp file so concurrent emitters never collide

## Metadata
- Task ID: TASK-2026-10-04-per-process-conjure-cache-temp-file
- Story: none (standalone robustness task)
- Status: draft
- Owner: user
- Agent Name: unassigned
- Priority: p3
- Created: 2026-10-04T12:15:00Z
- Updated: 2026-10-04T12:15:00Z

## Objective
`CachingSystem._write_current_cache_to_disk_locked` writes `<bundle>.melc.tmp` and replaces the bundle with it.
The temp name is fixed, so two processes emitting the cache of the same frame/conduit name at the same moment
race on one file; on Windows the second open or replace raises `PermissionError` (seen as 4 failures across the
component and integration tiers under `pytest -n 4` on 0.2.8222; the Linux CI runner passes). Use a per-process
unique temp name (pid + random suffix) and keep the atomic replace, so concurrent emitters each land a whole
bundle and the last writer wins.

## Ticket Contract
- ENTRY_GATE: routed on `attention_board.md`; no patch lane needed unless the bundle layout changes (it does not).
- EXECUTION_BOUNDARY: `src/melder/utilities/caching_system/caching_system.py` (the emit path), its unit tests, the
  release note, the CachingSystem component entry.
- DEPENDENCIES: none.
- EXIT_GATE: a two-process (or two-thread with separate CachingSystem instances) emit test that fails before and
  passes after; the four Windows tier failures no longer reproduce under `-n 4`.
- FAILURE_ESCALATION: DECISION_REQUEST if the fix needs the instance lock to become cross-process.

## Scope Boundaries
- In scope: the temp-file name and cleanup of a stale temp on failure.
- Out of scope: cache layout, generation, admission.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: opened from the owner's 0.2.8222 tier results; parked until the owner picks it up.

## Steps / Checklist
- [ ] Reproduce with two emitters on one bundle path (Windows or a simulated open-for-write hold).
- [ ] Per-process temp name + atomic replace; stale-temp cleanup.
- [ ] Regression; release-note line; component entry.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The hardened emit and its regression.

## Files / Paths Impacted
- see EXECUTION_BOUNDARY.

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest tests/unit/melder/utilities -q -p no:cacheprovider`
  - `python -m pytest tests/component tests/integration -q -n 4 -p no:cacheprovider` (Windows)

## Risks / Rollback Notes
- None beyond a leftover temp file on a crash between write and replace; cleanup covers it.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: delete_on_close

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-10-04T12:15:00Z
  TYPE: FACT
  CLAIM: The emit writes a fixed-name temp file beside the bundle and replaces the bundle with it; nothing makes the
  temp name unique per process, so concurrent emitters of one frame/conduit name share it.
  EVIDENCE:
  - src/melder/utilities/caching_system/caching_system.py:884-891
  IMPACT: a Windows `pytest -n 4` run of the suites hits it (4 failures on 0.2.8222); production hosts sharing one
  cache root across processes can too.
  NEXT: owner picks the lane up; reproduce first.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
STATE 2026-10-04T12:15:00Z: DRAFT, parked in the backlog. Opened from the owner's 0.2.8222 tier results.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
