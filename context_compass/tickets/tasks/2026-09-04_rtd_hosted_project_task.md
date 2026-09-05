# Task: Verify and configure the intended Read the Docs project

## Metadata
- Task ID: TASK-2026-09-04-rtd-hosted-project
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Story: STORY-2026-09-04-rtd-build-and-hosting
- Story Path: ../stories/2026-09-04_rtd_build_and_hosting_story.md
- Status: blocked
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T22:07:46Z
- Updated: 2026-09-05T12:06:59Z

## Objective
Connect the reviewable site to its intended hosted project and verify Git builds, PR previews, versions, hosted search, canonical links, and downloads.

## Ticket Contract
- ENTRY_GATE: Parent story/blueprint read, dependency milestone available, and this task actively routed.
- EXECUTION_BOUNDARY: Authorized RTD project/repository integration and settings; corresponding checked-in configuration corrections and setup evidence.
- DEPENDENCIES: Reviewable local/CI site; identified RTD project/account access; concrete publication review before external writes when required.
- EXIT_GATE: Acceptance checks have evidence; delivery state and parent story are synchronized.
- FAILURE_ESCALATION: Record concrete failures and preserve unaffected progress; do not infer success.

## Scope Boundaries
- In scope: the declared documentation task and necessary focused validation.
- Out of scope: unrelated runtime changes, other agents' assignments, and unrequested account actions.
- User authorization: implementation requested on 2026-09-04; ordinary scoped edits/checks may proceed.

## State Transition Event
- from_state: draft
- to_state: blocked
- transition_reason: Advertised public latest URL returns a not-found page. Actual project URL/branch
  and explicit private-dashboard read permission are pending owner input.

## Steps / Checklist
- [ ] Read the exact inputs and record one bounded implementation decision.
- [ ] Complete required patch contracts when the change is system-impacting.
- [ ] Implement the scoped deliverable with notes before the next tranche.
- [ ] Validate meaningful behavior/content and record actual outcomes.
- [ ] Synchronize parent story and hand off or close after acceptance.

## Acceptance Criteria
- [ ] Project ownership, repository, branch, and commit are verified.
- [ ] A real preview build completes and its output matches the intended revision.
- [ ] Version/search/notification/canonical/redirect settings are verified.
- [ ] Hosted downloads are the tested outputs.
- [ ] No unavailable setting or account action is reported as completed.

## Validation
- Not run. Implementation task just created.
- Use the parent story's validation plan and report local/hosted/execution results separately.

## Risks / Mitigations
- Canonical source and existing lessons can change concurrently; verify relevant inputs before edits.
- Hosting/dependency availability is an external-state check, not permission to invent completion.
- Keep the four owner-defined learning levels and prominent examples invariant.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false until this task produces or owns a supporting artifact.
- ARTIFACT_PATHS: none; the parent story links the shared blueprint.
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Record task-owned artifact disposition before accepted closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Verify and configure the intended Read the Docs project
- IF_UNKNOWN: none

## Noting Behavior
- Finish a coherent read/work unit and append evidence, impact, and one next action.
- Keep notes append-only; label unverified claims explicitly.

## Notes
- DATETIME: 2026-09-04T22:07:46Z
  TYPE: PLAN
  CLAIM: Implement this bounded part of the accepted documentation program under its existing story.
  EVIDENCE:
  - artifacts/2026-09-04_readthedocs_site_blueprint.md:293-344
  - Owner implementation instruction on 2026-09-04.
  IMPACT: The complete program now has explicit execution tasks and dependency boundaries.
  NEXT: Activate this task when its dependency milestone is available.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T12:06:59Z
  TYPE: BLOCKER
  CLAIM: Browser retrieval confirms the advertised public latest page is not available. Dashboard
    opening was rejected by automatic approval review for possible private account/project access
    without explicit authorization. Two concise questions request project identity and read-only access.
  EVIDENCE:
  - https://melder.readthedocs.io/en/latest/
  - Automatic approval rejection for https://app.readthedocs.org/projects/melder/.
  IMPACT: Cannot verify project settings, build logs, chosen revision, or live reader features yet.
    Public-only/local review continues in the quality task; no dashboard workaround or account write.
  NEXT: Obtain the owner's actual project URL/branch and dashboard read authorization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Applicable Anti-Patterns
- [ ] No silently omitted content or invented validation.
- [ ] No unrecorded scope changes or interference with another agent's work.

## Context / Handoff Summary
Public latest URL currently returns RTD's not-found page. Project identity/branch and private-dashboard
read authorization are pending. Automatic approval review rejected the attempted dashboard read;
do not retry or access it indirectly without authorization. Complete local quality work independently.
