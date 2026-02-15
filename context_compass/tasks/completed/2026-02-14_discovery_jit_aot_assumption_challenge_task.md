# Task: Discovery - JIT/AOT Assumption Challenge and User Discussion



Completed: 2026-02-15
Summary: Closed after user acceptance; implementation and validation artifacts are recorded in this ticket.


## Metadata
- Task ID: TASK-2026-02-14-discovery-jit-aot-assumption-challenge
- Story: STORY-2026-02-14-jit-aot-split-discovery-and-viability
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-15

## Objective
Perform explicit pushback review on the requested split model, surface weak
assumptions with evidence, and discuss alternatives with the user as a tracked
task deliverable.

## Scope Boundaries
- In scope:
- Evidence-backed critique of requested split semantics and alternatives.
- User-facing discussion prep and decision capture.
- Out of scope:
- Implementation changes.

## Steps / Checklist
- [x] Aggregate discovery outputs from phase-order, builder-contract, and spell-flag tasks.
- [x] Identify assumptions that are invalid, risky, or under-specified.
- [x] Prepare concise alternatives with tradeoffs and recommendation.
- [x] Discuss findings with user and record decision in story/epic notes.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- One explicit assumption-challenge summary with evidence.
- One user-reviewed decision entry: accept, adjust, or reject requested split shape.

## Assumption-Challenge Summary (2026-02-15)
### Assumptions Challenged
1. Assumption: split mode requires deferred/partial CreationContext builder behavior.
   Result: challenged.
   Why: current runtime path expects compiled execution callables from context and strict switch-based readiness; partial-context mutation is higher-risk than orchestration gating.
   Evidence: `src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:82-118`, `src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:230-264`, `src/melder/aether/conduit/meld/meld.py:345-373`, `context_compass/tasks/2026-02-14_discovery_jit_aot_creation_context_builder_runtime_contract_task.md:34-44`

2. Assumption: `resolution_required` should become a second validity system.
   Result: challenged.
   Why: validity ownership already exists in `SpellSystemState` + `ConduitResolutionState`; duplicating truth increases drift risk.
   Evidence: `src/melder/aether/dev_ops/spell_system_states/spell_system_state.py:400-424`, `src/melder/aether/dev_ops/spell_system_states/conduit_resolution_state.py:17-51`, `src/melder/aether/conduit/meld/meld.py:569-619`, `context_compass/tasks/2026-02-14_discovery_jit_aot_resolution_required_spell_contract_task.md:31-45`

3. Assumption: requested split is blocked by phase-order mismatch.
   Result: now reduced risk after parity alignment.
   Why: full-run path now executes 6/7 before 8/9/10/11, matching resolution-system ordering direction.
   Evidence: `src/melder/spellbook/spell.py:1337-1348`, `src/melder/spellbook/spellbook_creation_system.py:1315-1331`, `src/melder/spellbook/spellbook_creation_system.py:1398-1426`, `context_compass/tasks/2026-02-15_align_spellcrafter_phase_order_with_spellbook_creation_system_task.md:1-110`

### Alternatives
| Option | Description | Tradeoff |
|---|---|---|
| `A - hybrid_rule_bound` (recommended) | Keep strict builder/factory contracts; gate runtime with `resolution_required` before first context build; clear flag when validity gate passes. | Lowest regression risk; adds orchestration wiring work. |
| `B - deferred_optional_builder` | Allow partial context build and patch/mutate later at runtime. | Highest flexibility, highest contract/lifecycle risk. |
| `C - strict_aot_only` | Keep current behavior and reject split mode scope. | Safest technically, does not satisfy requested flexibility goal. |

## Files / Paths Impacted
- `context_compass/epics/2026-02-14_jit_aot_phase_split_configuration_epic.md`
- `context_compass/stories/2026-02-14_jit_aot_split_discovery_and_viability_story.md`
- `context_compass/tasks/2026-02-14_discovery_jit_aot_phase_order_contract_task.md`
- `context_compass/tasks/2026-02-14_discovery_jit_aot_creation_context_builder_runtime_contract_task.md`
- `context_compass/tasks/2026-02-14_discovery_jit_aot_resolution_required_spell_contract_task.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "run_all_phases|run_structural_phases|Cannot build CreationContext" src/melder/spellbook src/melder/aether/conduit/meld/creation_context`

## Risks / Rollback Notes
- Risk: Discussion may be skipped and hidden assumptions proceed into implementation.
- Mitigation: keep this as mandatory completion gate before implementation story activation.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [x] Acceptance criteria reviewed with user and confirmed
## Notes
- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: User accepted the `A hybrid_rule_bound` direction with one scope refinement: keep `full_ahead_of_time_compilation=true` as default and require propagation behavior for conjure bind, late bind, and transfer ownership while excluding contracted-spell owner rewrites.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_jit_aot_assumption_challenge_task.md:31-53, context_compass/tasks/2026-02-15_discovery_jit_aot_propagation_contract_surfaces_task.md:1-88
  IMPACT: Decision gate is resolved; remaining work is execution-surface discovery plus implementation ticket execution.
  NEXT: Run `TASK-2026-02-15-discovery-jit-aot-propagation-contract-surfaces` before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Discovery outputs now provide an evidence-backed challenge package: builder/factory recommendation (`hybrid_rule_bound`) plus `resolution_required` lifecycle table, with phase-order parity aligned.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_jit_aot_creation_context_builder_runtime_contract_task.md:34-44, context_compass/tasks/2026-02-14_discovery_jit_aot_resolution_required_spell_contract_task.md:31-45, context_compass/tasks/2026-02-15_align_spellcrafter_phase_order_with_spellbook_creation_system_task.md:1-110
  IMPACT: We can request an explicit user decision now instead of continuing speculative discovery.
  NEXT: Present challenge summary and alternatives to user; record decision in story/epic notes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: DECISION_REQUEST
  CLAIM: Need user decision on assumption challenge outcome: choose `A hybrid_rule_bound`, `B deferred_optional_builder`, or `C strict_aot_only`.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_jit_aot_assumption_challenge_task.md:31-53
  IMPACT: Decision unblocks implementation-task generation and prevents further drift from speculative scope.
  NEXT: Await user choice, then create implementation tasks aligned to selected option.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-14
  TYPE: PLAN
  CLAIM: This task is the dedicated lane for explicit pushback, including surfacing whether "phases 1-7 now, 8-12 later" conflicts with current ordering and build contracts.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:5058-5069, src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:82-86, context_compass/epics/2026-02-14_jit_aot_phase_split_configuration_epic.md:1-1
  IMPACT: Guarantees we challenge weak assumptions before coding.
  NEXT: Run first three discovery tasks, then produce user discussion summary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Task deliverables are complete and option selection is resolved (`A` with
non-breaking default). Follow-on work has moved to
`TASK-2026-02-15-discovery-jit-aot-propagation-contract-surfaces` before
implementation starts.


