# Task: Start the next-version release draft with scoped purge

## Metadata
- Task ID: TASK-2026-09-21-draft-next-version-release
- Status: review
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-21T00:30:00Z
- Updated: 2026-09-21T00:37:37Z

## Objective
Create release_docs/next_version_release.md documenting the accepted purge feature and how to use it.
Keep this as an unpublished next-version draft without choosing a package version or release date.

## Ticket Contract
- ENTRY_GATE: Owner explicitly requested this filename, folder and purge content.
- EXECUTION_BOUNDARY: Release draft and its coordination records. No runtime edits or publication.
- DEPENDENCIES: Accepted purge implementation, usage guide and executed feature validation.
- EXIT_GATE: Draft covers both input paths, single/all modes, returns, scope authority and disposal.
- FAILURE_ESCALATION: Keep unselected version/date unset; do not invent unrelated release changes.

## Scope and Deliverables
- In scope: One portable Markdown draft in release_docs, suitable for later GitHub release use.
- Out of scope: Version bump, release publication, changes to the previous 0.2.43 notes.
- Deliverable: release_docs/next_version_release.md.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Draft written and manually checked against the implemented purge contracts.

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
- No release publication or package version change.
- No local-path hyperlinks that break when pasted onto GitHub.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none

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

## Context / Handoff Summary
release_docs/next_version_release.md is written and reviewed against current purge behavior. It is
an unpublished draft with version/date unassigned, no local hyperlinks and no unrelated release items.

## Noting Behavior
Keep draft scope and any later owner revisions here; implementation evidence remains in the purge task.
