# Task: Implement docs CI parity, RTD configuration, and offline outputs

## Metadata
- Task ID: TASK-2026-09-04-rtd-ci-and-offline
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Story: STORY-2026-09-04-rtd-build-and-hosting
- Story Path: ../stories/2026-09-04_rtd_build_and_hosting_story.md
- Status: in_progress
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T22:07:46Z
- Updated: 2026-09-04T22:07:46Z

## Objective
Wire the proven local command into CI and RTD configuration, implement version/canonical/source behavior, and build offline formats.

## Ticket Contract
- ENTRY_GATE: Parent story/blueprint read, dependency milestone available, and this task actively routed.
- EXECUTION_BOUNDARY: .readthedocs.yaml, docs workflow and its required-CI integration, docs dependency
  locks/configuration, offline builders, version/source-link code, and docs/maintaining.md.
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
- DATETIME: 2026-09-05T00:50:29Z
  TYPE: DECISION
  CLAIM: Add a reusable docs workflow to the existing required CI graph, including the exact job
    evidence list in ci_policy.py. Keep runtime verification in its existing 3.14t workflow.
    RTD supports Python 3.14 and per-format build.jobs overrides; outputs must be staged under
    READTHEDOCS_OUTPUT for html/htmlzip/pdf/epub. Local and hosted formats must share the same builders.
    The handbook will contain the four guide levels, glossary, and selected complete examples.
  EVIDENCE:
  - .github/workflows/ci.yml:1-82
  - .github/scripts/ci_policy.py:16-25
  - .github/scripts/ci_policy.py:96-117
  - https://docs.readthedocs.com/platform/stable/config-file/v2.html
  - https://docs.readthedocs.com/platform/stable/build-customization.html
  IMPACT: A docs failure must block merge-ready just like the existing mandatory checks; account setup
    remains separate from checked-in configuration. Owner retains all commits and pushes.
  NEXT: Implement the curated handbook and format staging, then wire CI and RTD configuration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- [ ] No silently omitted content or invented validation.
- [ ] No unrecorded scope changes or interference with another agent's work.

## Context / Handoff Summary
Defined task awaiting its dependency milestone.
Wire the proven local command into CI and RTD configuration, implement version/canonical/source behavior, and build offline formats.
