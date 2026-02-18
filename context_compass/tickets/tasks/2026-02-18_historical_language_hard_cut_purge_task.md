

# Task: Historical Language Hard-Cut Purge

## Metadata
- Task ID: TASK-2026-02-18-historical-language-hard-cut-purge
- Parent Story: none
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-18T00:35:09Z
- Updated: 2026-02-18T00:38:29Z

## Objective
Remove remaining disallowed historical terminology from `context_compass`
documentation, including completed/examples, so policy language is strictly
forward-only.

## Ticket Contract
- ENTRY_GATE: user directed continuation after forward-only cleanup.
- EXECUTION_BOUNDARY: docs under `context_compass/`.
- DEPENDENCIES: completed onboarding-policy sweep artifacts.
- EXIT_GATE: targeted wording search returns no matches in `context_compass`.
- FAILURE_ESCALATION: raise `CONFLICT` if requested removals would alter
  technical meaning or safety requirements.

## Scope Boundaries
- In scope:
  - `context_compass/examples/`
  - `context_compass/tickets/**/completed/`
  - `context_compass/agent_onboarding/**/README.md` and profile docs
  - `context_compass/artifacts/README.md`
- Out of scope:
  - runtime behavior under `src/`
  - changing technical contracts beyond wording normalization

## Steps / Checklist
- [x] Route active attention to this task.
- [x] Patch remaining wording in active and historical docs.
- [x] Run final repo-wide verification search.
- [ ] Summarize completion and request closure confirmation.

## Validation Plan
- Run the repository wording scan and confirm zero matches for disallowed
  policy terminology.

## Notes
- DATETIME: 2026-02-18T00:35:09Z
  TYPE: FACT
  CLAIM: Residual wording remains in examples/completed docs and a small set of
    onboarding profile files.
  EVIDENCE:
  - context_compass/artifacts/README.md:34-34
  - context_compass/agent_onboarding/default/new/README.md:29-29
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/README.md:24-24
  - context_compass/agent_onboarding/default/engineer/skills/system_orientation.md:37-37
  IMPACT: Forward-only language policy is incomplete without historical-surface
    cleanup.
  NEXT: patch all matched docs and re-run verification.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T00:38:29Z
  TYPE: MEASURE
  CLAIM: Targeted wording purge is complete across `context_compass`; the
    verification scan returns zero matches.
  EVIDENCE:
  - context_compass/artifacts/README.md:34-34
  - context_compass/agent_onboarding/default/new/README.md:29-29
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/README.md:24-24
  - context_compass/agent_onboarding/default/engineer/skills/system_orientation.md:37-37
  - context_compass/examples/example_stories/2026-02-16_system_docs_unification_and_instruction_contract_story_completed.md:108-108
  - context_compass/examples/example_epics/2026-02-16_system_representation_documentation_improvement_epic_completed.md:143-143
  - context_compass/examples/example_completed/2026-01-17_pytest_policy_task_completed.md:4-4
  IMPACT: Forward-only terminology policy is now consistent in active and
    historical documentation surfaces.
  NEXT: summarize completion to user and request closure confirmation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Noting Behavior
- Note focus: tactical findings, immediate impacts, and one-step continuation.

## Context / Handoff Summary
Task opened to finish full historical wording purge after active-policy closure.