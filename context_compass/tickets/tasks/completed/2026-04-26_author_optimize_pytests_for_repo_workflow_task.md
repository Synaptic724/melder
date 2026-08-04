# Task: Author optimize_pytests_for_repo Workflow
- Completed: 2026-04-27T00:13:15Z
- Summary: Closed after the advanced pytest-optimization workflow was authored
  and registered in the finishing-role manifest.

## Metadata
- Task ID: TASK-2026-04-26-author-optimize-pytests-for-repo-workflow
- Story: STORY-2026-04-26-add-synaptic-finishing-repo-polish-workflows
- Status: done
- Owner: codex
- Agent Name: codex_modder_1
- Priority: p0
- Created: 2026-04-26T20:40:39Z
- Updated: 2026-04-27T00:13:15Z

## Objective
Author a role-local advanced workflow that lets
`synaptic_finishing_developer` target a file, directory, or source tree,
create recursive testing tickets, and then deepen pytest coverage only for
important behavioral files with graph-aware, contract-driven unit, component,
and integration tests.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a pytest-optimization workflow for
  the finishing role.
- EXECUTION_BOUNDARY:
  - `context_compass/agent_onboarding/user_defined/synaptic_finishing_developer/workflows/optimize_pytests_for_repo.md`
  - `context_compass/agent_onboarding/user_defined/synaptic_finishing_developer/WORKFLOWS.MD`
  - `context_compass/agent_onboarding/user_defined/synaptic_finishing_developer/AGENTS.MD`
  - this task
- DEPENDENCIES:
  - finishing-role testing skills
  - finishing-role system-doc baseline reads
- EXIT_GATE: the workflow doc exists, is registered, and explicitly defines
  importance filtering, recursive ticketization, and deep pytest expectations.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the workflow cannot honor the
  user's "important files only" rule without a more formal file-classification
  schema.

## Scope Boundaries
- In scope:
  - one advanced workflow doc
  - manifest registration support
  - role awareness text updates needed for discoverability
- Out of scope:
  - executing the workflow on a real target
  - writing actual tests in this lane

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: the workflow was authored and registered and is ready for
  review.

## Steps / Checklist
- [x] Define target-path input semantics for file, directory, and tree scopes.
- [x] Define epic/story/task decomposition rules.
- [x] Define important-file filters and explicit skip rules.
- [x] Define deep pytest expectations tied to role testing guidance.
- [x] Register the workflow in the finishing-role manifest.

## Deliverables
- `optimize_pytests_for_repo.md`
- finishing-role manifest update

## Validation
- Re-read the workflow doc after authoring.
- Not run:
  - no runtime validation required for this documentation-only workflow authoring task

## Applicable Anti-Patterns
- [ ] No enum or `__init__` testing for coverage optics.
- [ ] No attribute-existence tests pretending to prove behavior.
- [ ] No shallow unit-only dogma where component or integration tests are the
      real contract proof.

## Notes
- DATETIME: 2026-04-26T20:40:39Z
  TYPE: FACT
  CLAIM: The pytest optimization workflow must be selective, not exhaustive. It
    should prioritize important behavioral files and explicitly skip junk work
    such as `__init__` testing and enum-only testing unless the user overrides
    that default.
  EVIDENCE:
  - user_instruction: "we only optimize for important files no weird things
    like enum testing and __init__ testing thats just make work nonsense"
  IMPACT: The workflow needs an explicit importance filter and anti-pattern
    guardrails against coverage theater.
  NEXT: encode the important-file filter, deep test-layer rules, and graph-aware
    test planning contract directly into the advanced workflow definition.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
The pytest optimization workflow is authored and waiting for review.
