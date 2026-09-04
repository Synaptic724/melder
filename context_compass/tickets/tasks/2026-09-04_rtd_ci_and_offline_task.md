# Task: Implement docs CI parity, RTD configuration, and offline outputs

## Metadata
- Task ID: TASK-2026-09-04-rtd-ci-and-offline
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Story: STORY-2026-09-04-rtd-build-and-hosting
- Story Path: ../stories/2026-09-04_rtd_build_and_hosting_story.md
- Status: draft
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T22:07:46Z
- Updated: 2026-09-04T22:07:46Z

## Objective
Wire the proven local command into CI and RTD configuration, implement version/canonical/source behavior, and build offline formats.

## Ticket Contract
- ENTRY_GATE: Parent story/blueprint read, dependency milestone available, and this task actively routed.
- EXECUTION_BOUNDARY: .readthedocs.yaml, .github/workflows/docs.yml, docs dependency locks/configuration, offline builders, version/source-link code, and docs/maintaining.md.
- DEPENDENCIES: Local foundation/catalog; content and reference contracts; live hosting activation is the separate hosted-project task.
- EXIT_GATE: Acceptance checks have evidence; delivery state and parent story are synchronized.
- FAILURE_ESCALATION: Record concrete failures and preserve unaffected progress; do not infer success.

## Scope Boundaries
- In scope: the declared documentation task and necessary focused validation.
- Out of scope: unrelated runtime changes, other agents' assignments, and unrequested account actions.
- User authorization: implementation requested on 2026-09-04; ordinary scoped edits/checks may proceed.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Implementation task defined; prerequisite work remains ahead of activation.

## Steps / Checklist
- [ ] Read the exact inputs and record one bounded implementation decision.
- [ ] Complete required patch contracts when the change is system-impacting.
- [ ] Implement the scoped deliverable with notes before the next tranche.
- [ ] Validate meaningful behavior/content and record actual outcomes.
- [ ] Synchronize parent story and hand off or close after acceptance.

## Acceptance Criteria
- [ ] Local/CI/RTD configuration share deterministic source assembly and dependencies.
- [ ] Docs dependencies remain separate from runtime dependencies.
- [ ] HTML and defined PDF/ePub handbook outputs are valid and revision-labeled.
- [ ] Public-content selection, redirects/canonical inputs, and recovery steps are explicit.
- [ ] Workflow/static checks and local output review are recorded.

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
- CONTEXT_TOPICS: Implement docs CI parity, RTD configuration, and offline outputs
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

## Applicable Anti-Patterns
- [ ] No silently omitted content or invented validation.
- [ ] No unrecorded scope changes or interference with another agent's work.

## Context / Handoff Summary
Defined task awaiting its dependency milestone.
Wire the proven local command into CI and RTD configuration, implement version/canonical/source behavior, and build offline formats.

