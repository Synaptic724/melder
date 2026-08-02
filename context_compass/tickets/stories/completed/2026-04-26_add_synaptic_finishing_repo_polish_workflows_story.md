# Story: Add Synaptic Finishing Repo Polish Workflows
- Completed: 2026-04-27T00:13:15Z
- Summary: Closed after the finishing role gained the new advanced
  `polish_repo_documentation` and `optimize_pytests_for_repo` workflows and
  the lane was routed for review.

## Metadata
- Story ID: STORY-2026-04-26-add-synaptic-finishing-repo-polish-workflows
- Status: done
- Owner: codex
- Agent Name: codex_modder_1
- Priority: p0
- Created: 2026-04-26T20:40:39Z
- Updated: 2026-04-27T00:13:15Z

## User Narrative
As the user, I want the `synaptic_finishing_developer` role to ship role-local
repo finishing workflows for documentation polishing and pytest optimization, so
that I can target one file, one directory, or a whole source tree and get a
slow, system-aware, ticketed finishing lane instead of an ad hoc pass.

## Value / MRP Alignment
This story turns the finishing role into a real repo-scale macro surface. It
keeps the work manual, evidence-backed, and system-aware instead of treating
docstrings or tests like one-shot cleanup.

## Ticket Contract
- ENTRY_GATE: the finishing role already exists and the user explicitly
  requested repo-scale documentation and pytest finishing workflows.
- EXECUTION_BOUNDARY:
  - `context_compass/agent_onboarding/user_defined/synaptic_finishing_developer/WORKFLOWS.MD`
  - `context_compass/agent_onboarding/user_defined/synaptic_finishing_developer/AGENTS.MD`
  - `context_compass/agent_onboarding/user_defined/synaptic_finishing_developer/workflows/**`
  - this story and linked child tasks
  - `context_compass/attention_board.md`
- DEPENDENCIES:
  - `context_compass/agent_onboarding/user_defined/synaptic_finishing_developer/SKILLS.MD`
  - `context_compass/agent_onboarding/user_defined/synaptic_finishing_developer/AGENTS.MD`
  - role-local workflow templates
- EXIT_GATE: both workflows exist, they are registered in the role manifest,
  and the role overlay carries awareness of their intended use.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if either workflow needs to live
  outside `synaptic_finishing_developer` to stay coherent.

## Requirements (Functional)
- Add `polish_repo_documentation` to `synaptic_finishing_developer`.
- Add `optimize_pytests_for_repo` to `synaptic_finishing_developer`.
- Make both workflows advanced role-local workflow definitions.
- Register both workflows in the role `WORKFLOWS.MD`.
- Add role-level awareness text so the finishing overlay knows these workflows
  exist without forcing baseline workflow-doc reads.

## Requirements (Non-Functional)
- Keep both workflows explicitly user-owned and user-triggered.
- Keep both workflows slow, manual, and system-aware.
- Require epic/story/task decomposition inside the workflow design.
- Skip meaningless files and tests explicitly instead of silently.

## Scope Boundaries
- In scope:
  - role-local workflow docs
  - role workflow manifest update
  - finishing-role overlay awareness text
  - ticket and board state for this implementation lane
- Out of scope:
  - running either workflow on the repo
  - creating the recursive repo tickets those workflows would later generate
  - changing global workflow policy

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: the requested finishing-role workflows were authored and
  registered, and the lane is now waiting for review/acceptance.

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-26-author-polish-repo-documentation-workflow
- [x] Task: TASK-2026-04-26-author-optimize-pytests-for-repo-workflow
- [x] Register both workflows in the finishing-role manifest.
- [x] Add concise role-level workflow awareness text to the finishing overlay.

## Acceptance Criteria
- `synaptic_finishing_developer` exposes `polish_repo_documentation`
- `synaptic_finishing_developer` exposes `optimize_pytests_for_repo`
- both workflows are advanced role-local docs
- both workflows build epic/story/task structures around the selected target
- both workflows explicitly skip trivial junk like `__init__` files unless the
  user overrides that behavior
- the documentation workflow is system-aware and public-library oriented
- the pytest workflow is deep, contract-driven, and not coverage theater

## Validation / Test Plan
- Re-read the finishing-role workflow manifest.
- Re-read the finishing-role overlay `AGENTS.MD`.
- Re-read both workflow docs for completeness and alignment.
- Not run:
  - runtime tests are not required because this is a role/workflow-doc change

## Risks / Mitigations
- Risk: the workflows become too abstract and do not enforce real recursive
  ticket mapping.
  Mitigation: both workflow docs explicitly define epic root scope, story per
  meaningful directory, and task per meaningful file.
- Risk: the pytest workflow drifts into filler coverage work.
  Mitigation: the workflow hard-codes importance filters and anti-patterns
  against `__init__`, enum, and trivial-module testing.

## Applicable Anti-Patterns
- [ ] No repo-scale finishing workflow that relies on bulk autogenerated
      docstring spray.
- [ ] No pytest optimization workflow that rewards trivial-file coverage.
- [ ] No workflow registration without explicit role-local placement.

## Decision Log
- These workflows belong in `synaptic_finishing_developer`, not `general`.
- Both workflows should use the advanced format because they orchestrate target
  scoping, recursive ticketization, deep source reading, and staged execution.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-26T20:40:39Z
  TYPE: DECISION
  CLAIM: The new repo-scale finishing workflows should live inside
    `synaptic_finishing_developer` as advanced role-local workflows because the
    user explicitly requested them there and because their behavior depends on
    the role's system-aware documentation and testing posture.
  EVIDENCE:
  - user_instruction: "Add these 2 workflows into synaptic_finishing_developer"
  - user_instruction: "This would allow me to get the agent to build an epic
    around the entire repo and a story around each directory, and a task per
    file"
  IMPACT: The implementation should extend the finishing role directly instead
    of broadening the global workflow surface.
  NEXT: author both advanced workflow docs, register them in the role manifest,
    and add role-level awareness text.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This lane adds two heavy-duty repo finishing workflows to the finishing role.
They are implemented and now await review/acceptance.
