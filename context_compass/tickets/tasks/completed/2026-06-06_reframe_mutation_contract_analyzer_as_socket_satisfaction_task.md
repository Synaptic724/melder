Completed: 2026-06-06T18:18:17Z
Summary: Closed as superseded-completed. The investigation proved analyzer churn was not the active seam, and the work moved downstream into planner / phase-11 convergence instead.

# Task: Reframe Mutation Contract Analyzer As Socket Satisfaction

## Metadata
- Task ID: TASK-2026-06-06-reframe-mutation-contract-analyzer-as-socket-satisfaction
- Story: none
- Status: done
- Owner: codex
- Agent Name: compiler_0
- Priority: p0
- Created: 2026-06-06T09:44:36Z
- Updated: 2026-06-06T18:18:17Z

## Objective
Map and then implement the analyzer-side convergence so mutation is treated as
**satisfaction of mutation sockets into the current resolved graph**, not as a
post-hoc override overlay concept.

## Parent Link
- Epic:
  `tickets/epics/2026-06-04_unblock_mutation_contract_runtime_and_retire_spell_mutation_override_epic.md`

## Ticket Contract
- ENTRY_GATE: phase-4 mutation semantics are now corrected enough that the next
  coherent waterfall step is analyzer convergence.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py`
  - `src/melder/aether/spellbook/spell_compiler/spell_analyzer/data/spell_occurrence_graph_analysis.py`
  - `src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py`
  - `src/melder/aether/spellbook/spell.py`
  - `codex/context_compass/tickets/tasks/2026-06-06_reframe_mutation_contract_analyzer_as_socket_satisfaction_task.md`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/tasks/2026-06-06_align_mutation_contract_phase4_to_late_bound_hole_task.md`
  - `tickets/epics/2026-06-04_unblock_mutation_contract_runtime_and_retire_spell_mutation_override_epic.md`
- EXIT_GATE:
  - analyzer responsibilities are mapped clearly enough to implement without
    guessing
  - the target analyzer contract is explicit in ticket notes
  - no code changes are made until the mapped plan is reviewed
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if analyzer convergence cannot be
  isolated cleanly from planner/model changes.

## Scope Boundaries
- In scope:
  - current analyzer mutation responsibilities
  - target analyzer contract
  - exact symbol/file change map for implementation
  - explicit non-goals for this phase
- Out of scope:
  - planner lane collapse
  - phase-11 creation packaging changes
  - MutationContract removal
  - broad runtime binder changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the next waterfall step after phase-4 correction is to
  reframe the analyzer around mutation-socket satisfaction instead of override
  overlay semantics.

## Requirements
- `MutationContract` itself is permanent and is not being removed.
- analyzer must stop telling the wrong story about mutation being a
  post-dependency overlay when the real semantics are "current mutation binding
  satisfies mutation sockets"
- no implementation starts until the analyzer plan is explicit enough to review
  directly against the files

## Steps / Checklist
- [ ] Map the current analyzer mutation responsibilities.
- [ ] Write the target analyzer contract in notes.
- [ ] Identify exact symbol-level replacements/renames needed for the analyzer.
- [ ] Identify what model fields and downstream assumptions this analyzer change
      will pressure without touching them yet.
- [ ] Review the mapped analyzer plan with the user before code edits.

## Validation
- Not run.

## Applicable Anti-Patterns
- [ ] Do not remove `MutationContract` itself.
- [ ] Do not silently widen into planner or phase-11 changes in this task.
- [ ] Do not keep using "override overlay" language if the actual target is
      socket satisfaction.

## Notes
- DATETIME: 2026-06-06T09:44:36Z
  TYPE: PLAN
  CLAIM: The analyzer is the next correct waterfall seam because it is still
    the first middle-layer component that treats mutation as a post-hoc
    dependency rewrite instead of as satisfaction of mutation sockets into the
    current resolved graph. Fixing planner or phase-11 first would harden the
    wrong middle model further.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:711-724
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:968-1245
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py:43-60
  IMPACT: The analyzer plan needs to be explicit before the next code slice so
    downstream convergence is based on the corrected graph semantics.
  NEXT: map the analyzer responsibilities and write the target contract without
    changing code yet.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T09:44:36Z
  TYPE: DECISION
  CLAIM: Current evidence does not prove the analyzer algorithm is wrong.
    Mutation dependency rewriting in the analyzer may already be the correct
    middle-layer implementation. The stronger proven issue is downstream:
    planner, phase-11 discovery/creation packaging, and runtime binder
    selection still encode mutation as a permanent third family.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:711-724
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py:43-60
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system.py:41-58
  IMPACT: Analyzer change is no longer the active mutation lane.
  NEXT: move active routing to the downstream planner/phase-11 convergence map.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the analyzer planning seam only. The goal is to map how mutation
currently enters the occurrence graph and how it should instead behave as
satisfaction of mutation sockets into the current resolved graph, while keeping
planner and phase-11 work out of scope until the analyzer plan is agreed.
