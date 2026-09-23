# Task: Start the next-version release draft with scoped purge

## Metadata
- Completed: 2026-09-22T15:13:55Z
- Summary: Added graduation/configuration release details and bumped canonical version to 0.2.45; assets unchanged.
- Task ID: TASK-2026-09-21-draft-next-version-release
- Status: done
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-21T00:30:00Z
- Updated: 2026-09-22T15:13:55Z

## Objective
Create release_docs/next_version_release.md documenting the accepted purge feature and how to use it.
Extend the draft with completed graduation/hook configuration and bump 0.2.44 to 0.2.45. The owner now authorizes the version selection; publication date stays unassigned and build assets stay held.

## Ticket Contract
- ENTRY_GATE: Owner explicitly requested this filename, folder and purge content.
- EXECUTION_BOUNDARY: Release draft, canonical __version__.py metadata and coordination records. No runtime behavior edits, generators, wheel or publication.
- DEPENDENCIES: Accepted purge implementation, usage guide and executed feature validation.
- EXIT_GATE: Draft covers purge and completed graduation/configuration; canonical version matches 0.2.45 and build assets remain untouched.
- FAILURE_ESCALATION: Keep unselected version/date unset; do not invent unrelated release changes.

## Scope and Deliverables
- In scope: One portable Markdown draft in release_docs, suitable for later GitHub release use.
- Out of scope: Build-asset generation, publication, runtime changes and edits to previous 0.2.43 notes.
- Deliverable: release_docs/next_version_release.md.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Owner requested turn-in; 0.2.45 metadata and release draft verified with all 26 captured assets unchanged.

## Steps / Checklist
- [x] Read existing release style and verified purge contracts.
- [x] Write the draft and confirm examples agree with implemented behavior.
- [x] Leave the draft for owner review and later additions.

## Validation
Manual comparison against docs/intermediate/scopes.md and the accepted source/test contracts.
No new runtime test run is required for a release-text-only change.

## Risks / Mitigations
Use no machine-local links or invented version boundary. Describe retained creations and scope
authority precisely; purge does not remove registrations or rewrite existing Python references.

## Applicable Anti-Patterns
- No release publication or generated-asset refresh. Version metadata change is owner-authorized.
- No local-path hyperlinks that break when pasted onto GitHub.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/release_0_2_45_20260922/
- DISPOSITION: retain_as_reference

## Notes
- DATETIME: 2026-09-21T00:30:00Z
  TYPE: PLAN
  CLAIM: Owner requested next_version_release under release_docs, covering the new purge feature.
    Use the accepted APIs and examples; leave the eventual version unspecified.
  EVIDENCE:
  - docs/intermediate/scopes.md:34-86
  - tickets/tasks/completed/2026-09-20_implement_scoped_creation_purge_task.md
  IMPACT: This is a separate draft deliverable; purge epic closeout continues independently.
  NEXT: Write and reread the Markdown release draft.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-21T00:33:00Z
  TYPE: FACT
  CLAIM: Created the next-version Markdown draft with purge selectors, instance shortcut,
    default all/single behavior, return counts, six lifetime authority rows and disposal semantics.
    Reread examples against the accepted source/tests and documented the retained-many prerequisite.
    The draft has no local-path links and assigns neither a release version nor publication date.
  EVIDENCE:
  - release_docs/next_version_release.md:1-95
  - docs/intermediate/scopes.md:34-86
  IMPACT: Ready for owner review and additional release items; nothing has been published.
  NEXT: Owner reviews or extends the draft before choosing the eventual release version.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-22T15:11:40Z
  TYPE: DECISION
  CLAIM: Owner confirms the graduated runtime is ready/conjured, requests ticket turn-in, next-release
    details and a version increment, and explicitly forbids build-asset regeneration. Current canonical
    version is 0.2.44; increment the patch component to 0.2.45. Setuptools reads this literal and the
    uv editable root has no version field, so neither pyproject nor uv.lock needs a duplicate bump.
  EVIDENCE:
  - src/melder/__version__.py:1-12
  - pyproject.toml:137-142
  - uv.lock:333-337
  - Owner's current release/version/turn-in instruction.
  IMPACT: The original draft-only/no-version boundary is superseded for this task. Graduation tickets
    are already completed; close this release task after metadata and portable release text qualify.
  NEXT: Update the draft and canonical version while preserving all generated build assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-22T15:13:55Z
  TYPE: MEASURE
  CLAIM: Updated release_docs/next_version_release.md for 0.2.45 with ready/conjured graduation,
    independent empty Book ownership, hook reset/seeding, shared-frame policy, cleanup and failure
    boundaries. Purge content remains. Canonical __version__ changed from 0.2.44 to 0.2.45.
    Static metadata/draft checks pass; all 26 captured build assets/hardcopy exports are unchanged.
  EVIDENCE:
  - release_docs/next_version_release.md:1-95
  - src/melder/__version__.py:12-12
  - artifacts/release_0_2_45_20260922/validation.json
  IMPACT: Owner-requested release update is complete and turned in. No generator, wheel or publication
    ran. Runtime tests were not repeated for metadata/prose-only changes; prior qualification remains
    accurately attributed in the draft. Graduation tickets were already completed on this request.
  NEXT: None for this update; the owner can add more work before releasing packaged generation.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10
## Context / Handoff Summary
Release draft targets 0.2.45 and includes purge plus completed graduation/configuration details.
Canonical version metadata agrees. Publication remains unassigned; no build assets were regenerated.

## Noting Behavior
Keep release revisions here; implementation evidence remains in the completed purge and graduation tasks.
