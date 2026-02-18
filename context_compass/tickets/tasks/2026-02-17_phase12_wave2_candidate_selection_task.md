

# Task: Select Next Phase12 Candidate Ticket After Wave1 Rollback

## Metadata
- Task ID: TASK-2026-02-17-phase12-wave2-candidate-selection
- Story: STORY-2026-02-17-phase12-creation-context-discovery-and-benchmark
- Status: review
- Owner: codex
- Priority: p1
- Created: 2026-02-17T18:26:37Z
- Updated: 2026-02-17T18:28:41Z

## Objective
Determine and route the next concrete implementation ticket after wave-1
rollback, using current branch benchmark evidence and discovered candidate risk
tables.

## Ticket Contract
- ENTRY_GATE: wave-1 implementation task is blocked and discovery evidence is
  complete across all three locations.
- EXECUTION_BOUNDARY:
  - `context_compass/attention_board.md`
  - `context_compass/tickets/tasks/2026-02-17_phase12_wave1_medium_implementation_task.md`
  - `context_compass/tickets/stories/2026-02-17_phase12_creation_context_discovery_and_benchmark_story.md`
  - `context_compass/tickets/epics/2026-02-17_phase12_creation_context_codegen_performance_improvement_epic.md`
  - `benchmarks/testing_other_di/results/codegen_benchmark_existing_change.json`
  - `benchmarks/testing_other_di/results/codegen_benchmark_after_branch_swap.json`
  - `benchmarks/testing_other_di/results/codegen_benchmark_after_branch_compare_chat_ref.json`
- DEPENDENCIES: candidate tables from completed discovery tasks.
- EXIT_GATE: next implementation ticket is selected, created, and routed on the
  attention board with evidence-backed rationale.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if next step requires high-risk
  candidate approval.

## Scope Boundaries
- In scope:
  - benchmark comparison synthesis for routing decisions,
  - next-ticket selection and creation,
  - story/epic/board synchronization.
- Out of scope:
  - direct runtime code edits for candidate implementation,
  - closure of story/epic.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: next implementation lane selected and routed.

## Steps / Checklist
- [x] Synthesize current-branch benchmark results against prior branch evidence.
- [x] Select the next candidate lane for implementation.
- [x] Create the next implementation task ticket.
- [x] Update story/epic checklists and notes for the new active lane.
- [x] Switch `attention_board.md` active routing to the new ticket.

## Deliverables
- Evidence-backed next-ticket selection record.
- New implementation task ticket for the selected lane.
- Synced story/epic/attention-board routing state.

## Validation
- Run.
- Commands:
  - `$env:PYTHONPATH='.;src'; python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --pin-p-cores --profile-iteration-count 5 --baseline-path benchmarks/testing_other_di/results/codegen_benchmark_baseline.json --output-path benchmarks/testing_other_di/results/codegen_benchmark_after_branch_compare_chat_ref.json --allow-baseline-regression`
- Result:
  - `overall_weighted_ratio=0.9967948717948718`, `passed=true`
  - route ratios:
    `warm_override_root_args_ns=0.9615384615384616`,
    `warm_override_targeted_ns=1.0`

## Risks / Rollback Notes
- Risk: selecting a high-risk candidate without explicit approval.
  Mitigation: default to medium-risk lane unless user approves high-risk work.
- Risk: branch noise drives wrong selection.
  Mitigation: compare weighted scores and route-level ratios across runs.

## Applicable Anti-Patterns
- [ ] No next-ticket routing without benchmark evidence pointers.
- [ ] No high-risk lane activation without explicit approval.
- [ ] No board switch without story/epic synchronization.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: task closure

## Noting Behavior
- Note focus: routing decisions, benchmark synthesis, and immediate next action.
- Add a `## Notes` entry after each meaningful finding.
- Keep entries append-only and evidence-backed.

## Notes
- DATETIME: 2026-02-17T18:26:37Z
  TYPE: PLAN
  CLAIM: Next-ticket routing will use the latest branch benchmark evidence and
    discovery risk tables to select a single implementation lane.
  EVIDENCE:
  - tickets/tasks/2026-02-17_phase12_wave1_medium_implementation_task.md:1-144
  - benchmarks/testing_other_di/results/codegen_benchmark_existing_change.json:807-844
  - benchmarks/testing_other_di/results/codegen_benchmark_after_branch_compare_chat_ref.json:807-844
  IMPACT: Execution can continue immediately without remaining blocked on the
    reverted wave-1 lane.
  NEXT: Add story/epic notes for wave-1 pause and switch active routing to this
    next-wave selection task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T18:28:41Z
  TYPE: DECISION
  CLAIM: Selected `OR-M1` as the next isolated medium-risk implementation lane
    and created/routed the corresponding execution task.
  EVIDENCE:
  - tickets/tasks/2026-02-17_phase12_overrides_executor_discovery_task.md:64-68
  - tickets/tasks/2026-02-17_phase12_or_m1_isolated_implementation_task.md:1-115
  - context_compass/attention_board.md:23-46
  IMPACT: Active execution proceeds on a concrete next ticket without reopening
    discovery.
  NEXT: Execute OR-M1 task implementation and validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Selection/routing is complete. Active implementation lane is now
`TASK-2026-02-17-phase12-or-m1-isolated-implementation`.


