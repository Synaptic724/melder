

Completed: 2026-02-16T22:32:29Z
Summary: Delivered hard-cut system-doc unification, completed phase tasks, and
  aligned active onboarding/policy references to canonical `system_docs` files.

# Story: System Docs Unification and Instruction Contract

## Metadata
- Story ID: STORY-2026-02-16-system-docs-unification-and-instruction-contract
- Epic: EPIC-2026-02-16-system-representation-documentation-improvement
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-16T22:04:24Z
- Updated: 2026-02-16T22:32:29Z

## User Narrative
As a context_compass maintainer, I want one system-doc folder with both src and
test docs plus explicit instruction docs, so onboarding is simpler while we
keep `src_architecture` and `src_components` as separate core files.

## Value / MRP Alignment
This story reduces navigation overhead without forcing a single giant document.
It keeps top-down and bottom-up separation while making the location model
simpler and token-aware.

## Ticket Contract
- ENTRY_GATE: user approved staged, ticket-first rollout.
- EXECUTION_BOUNDARY: docs-location migration and reference updates only.
- DEPENDENCIES: current architecture/components/test docs and onboarding policy
  references.
- EXIT_GATE: staged migration is documented and executed per task.
- FAILURE_ESCALATION: path-migration risk or onboarding breakage escalated as
  `DECISION_REQUEST`.

## Requirements (Functional)
- Keep two core src docs: `src_architecture` and `src_components`.
- Move src and test docs to one canonical folder location.
- Replace local README dependency with explicit instruction docs:
  `src_architecture_instructions` and `src_components_instructions`.
- Update onboarding/readset/policy references in controlled stages.

## Requirements (Non-Functional)
- Maintain flat-file markdown model.
- Preserve compaction safety and re-onboarding reliability.
- Avoid broad risky sweeps; execute in phases.

## Scope Boundaries
- In scope:
- staged migration plan and staged implementation tasks.
- Out of scope:
- broad rewrite of historical/example/completed artifacts in one pass.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: user approved turning in migration tickets and moving on.

## Dependencies / Related Work
- `context_compass/system_docs/src_architecture.md`
- `context_compass/system_docs/src_components.md`
- `context_compass/system_docs/tests_architecture.md`
- `context_compass/system_docs/tests_components.md`
- `context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt`
- `context_compass/AGENTS.MD`
- `context_compass/agent_onboarding/default/general/skills/context_compaction.md`

## Tasks (Implementation Checklist)
- [x] Task:
      TASK-2026-02-16-system-docs-unification-discovery-and-cutover-plan -
      define canonical folder shape and migration sequence.
- [x] Task:
      TASK-2026-02-16-system-docs-phase1-src-and-tests-docs-move -
      move src/tests docs and add instruction docs.
- [x] Task:
      TASK-2026-02-16-system-docs-phase2-onboarding-reference-migration -
      migrate active policy/readset references.
- [x] Task:
      TASK-2026-02-16-system-docs-phase3-reference-cleanup -
      clean remaining low-risk references over time.

## Acceptance Criteria
- Migration sequence is explicit and ticketed.
- First phase can execute without onboarding breakage.
- User can choose pace phase-by-phase.

## Validation / Test Plan
- `rg` path checks for canonical docs in new folder.
- `rg` checks for stale references in active policy/readset docs.
- Validation status must stay truthful ("Not run" for test suites).

## Risks / Mitigations
- Risk: onboarding failures due to stale path refs.
  Mitigation: phase policy/readset migration before phase-3 cleanup.
- Risk: large search/replace churn.
  Mitigation: limit each phase by explicit task boundary.

## Applicable Anti-Patterns
- [x] No one-shot repo-wide path rewrite.
- [x] No deletion of old paths before active policy references are updated.
- [x] No migration step without rollback notes.

## Open Questions
- Should `tests_*_instructions.md` also be added, or keep only src instruction
  docs for now?

## Decision Log
- 2026-02-16: Chosen approach is phased/ticketed migration over time.
- 2026-02-16: Hard-cut migration approved; no compatibility stubs for
  removed `architecture/` and `components/` paths.

## Notes
- DATETIME: 2026-02-16T22:20:41Z
  TYPE: MEASURE
  CLAIM: All phased unification tasks are executed and in review after the
    hard-cut migration and active policy/reference cleanup.
  EVIDENCE:
  - context_compass/tasks/2026-02-16_system_docs_unification_discovery_and_cutover_plan_task.md:6-6
  - context_compass/tasks/2026-02-16_system_docs_phase1_src_and_tests_docs_move_task.md:6-6
  - context_compass/tasks/2026-02-16_system_docs_phase2_onboarding_reference_migration_task.md:6-6
  - context_compass/tasks/2026-02-16_system_docs_phase3_reference_cleanup_task.md:6-6
  IMPACT: Story objectives are delivered and awaiting user acceptance for
    closure decisions.
  NEXT: Walk through implemented hard-cut outcomes with user and confirm
    acceptance criteria.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-16T22:04:24Z
  TYPE: PLAN
  CLAIM: We will implement system-doc unification as a phased ticket sequence
    rather than one immediate move.
  EVIDENCE:
  - context_compass/tasks/2026-02-16_src_architecture_src_components_ranking_gap_analysis_task.md:150-178
  IMPACT: Migration risk is reduced and onboarding continuity can be verified
    at each phase.
  NEXT: Start phase-1 discovery/cutover-plan task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Focus notes on cross-task migration decisions and rollout safety.
- Keep tactical edits and path evidence in task notes.
- Keep notes append-only and UNKNOWN-first.

## Context / Handoff Summary
Hard-cut system-doc unification executed across phased tasks and accepted;
ready for archive move.