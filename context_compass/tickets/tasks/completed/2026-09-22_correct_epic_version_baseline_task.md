# Task: Correct the four-epic release baseline

- Completed: 2026-09-22T20:11:00Z
- Summary: Canonical version and draft corrected to 0.2.47, counting four epics from 0.2.43.
  Release tracking corrected; generated assets remain held.

## Metadata
- Task ID: TASK-2026-09-22-correct-epic-version-baseline
- Status: done
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-22T20:07:44Z
- Updated: 2026-09-22T20:11:00Z

## Objective
Use the owner's corrected starting version, 0.2.43. Four completed feature epics yield 0.2.47
in the existing 0.2.x numbering sequence. The prior 0.2.49 result counted two increments twice.

## Ticket Contract
- ENTRY_GATE: Owner explicitly requests correction of the baseline; active board row routes here.
- EXECUTION_BOUNDARY: Version literal, next-release heading, prior version task and build-hold notes.
- DEPENDENCIES: Completed four-epic version task; existing hold on packaged and LLM build assets.
- EXIT_GATE: Canonical version and draft agree on 0.2.47; durable notes record the corrected count.
- FAILURE_ESCALATION: Stop if current version changed independently; preserve all generated assets.

## Scope Boundaries
- In: Correct release metadata and its tracking without changing the completed feature work.
- Out: Runtime changes, generation, wheel builds, publishing, dependency changes and other epics.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Owner-requested correction verified; prior turn-in instruction remains applicable.

## Steps / Checklist
- [x] Read the current version and release draft.
- [x] Correct both to 0.2.47 and supersede the mistaken tracking notes.
- [x] Verify static agreement and turn in the correction under the existing closure request.

## Deliverables
- Corrected package metadata, release heading and durable release tracking.

## Validation
Static checks passed: canonical literal and draft heading agree on 0.2.47, and setuptools still
uses the canonical version attribute. Runtime tests: Not run; this is a metadata-only correction.
No generator, wheel build, dependency sync or publication ran.

## Risks / Rollback Notes
Preserve dated historical evidence of the earlier operation, explicitly marked superseded.
The build-asset hold remains in force throughout this correction.

## Applicable Anti-Patterns
- [x] No additional increments counted from an already incremented intermediate version.
- [x] No generated assets or runtime behavior changed by version correction.

## Artifact Links
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
Append correction and verification evidence with a concrete next action.

## Notes
- DATETIME: 2026-09-22T20:07:44Z
  TYPE: DECISION
  CLAIM: The owner corrected the baseline to 0.2.43. The prior task counted four epics from
    intermediate 0.2.45; replace that result with 0.2.47 while retaining its dated history.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-22_notch_version_for_completed_epics_task.md:15-28
  - tickets/tasks/2026-09-22_refresh_graduation_packaged_assets_when_approved_task.md:11-24
  IMPACT: Only release metadata and the notes that route later packaging need correction.
  NEXT: Read the canonical version and current release draft before editing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-22T20:09:00Z
  TYPE: FACT
  CLAIM: The canonical literal and current release heading both still read 0.2.49. Setuptools
    reads the canonical literal dynamically, so no second package version value needs changing.
  EVIDENCE:
  - src/melder/__version__.py:2-12
  - release_docs/next_version_release.md:1-3
  - pyproject.toml:139-142
  IMPACT: Correct these two lines and supersede the prior task/build-hold version notes.
  NEXT: Apply the 0.2.47 correction without invoking generators or importing Melder.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T20:10:07Z
  TYPE: FACT
  CLAIM: Canonical version and draft heading are now 0.2.47. The prior version task and deferred
    packaging task explicitly supersede 0.2.49. No generated asset file was edited or regenerated.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:1-1
  - tickets/tasks/completed/2026-09-22_notch_version_for_completed_epics_task.md:3-6
  - tickets/tasks/2026-09-22_refresh_graduation_packaged_assets_when_approved_task.md:72-74
  IMPACT: Future packaging will use the corrected baseline without repeating the double count.
  NEXT: Verify static version agreement and complete the correction record.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Completed correction to 0.2.47: baseline 0.2.43 plus purge, graduation, bind hooks and pool hooks.
Static agreement checks passed. The previous 0.2.49 result is superseded. Build generation remains
separately blocked; there is no further version-correction work.
