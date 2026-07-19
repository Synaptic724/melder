Completed: 2026-06-06T18:18:17Z
Summary: Closed as completed historical work. The first phase-4 convergence slice landed, and the later overlay-first removal / downstream cleanup work superseded this narrower task as the active lane.

# Task: Align Mutation Contract Phase 4 To Late-Bound Hole

## Metadata
- Task ID: TASK-2026-06-06-align-mutation-contract-phase4-to-late-bound-hole
- Story: none
- Status: done
- Owner: codex
- Agent Name: compiler_0
- Priority: p0
- Created: 2026-06-06T09:05:33Z
- Updated: 2026-06-06T18:18:17Z
- Updated: 2026-06-06T09:33:14Z

## Objective
Implement the first convergence slice for mutation contracts:
- stop treating `MutationContract` as blanket-disabled in dynamic mode
- treat unresolved mutation sockets like late-bound holes instead
- use spell-local dirty/reset semantics so the next meld reruns through the
  existing deferred resolution path

## Parent Link
- Epic:
  `tickets/epics/2026-06-04_unblock_mutation_contract_runtime_and_retire_spell_mutation_override_epic.md`

## Ticket Contract
- ENTRY_GATE: the mutation epic now has enough architecture/runtime evidence to
  start the first implementation slice without guessing.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py`
  - `src/melder/aether/spellbook/spell.py`
  - `tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_contract_provider_presence_strategy.py`
  - `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_4.py`
  - `tests/unit/melder/spellbook/test_spell.py`
  - `tests/experimentation/test_mutation_override_requires_mutation_contract_experiment.py`
  - `codex/context_compass/attention_board.md`
  - `codex/context_compass/tickets/tasks/2026-06-06_align_mutation_contract_phase4_to_late_bound_hole_task.md`
- DEPENDENCIES:
  - `tickets/epics/2026-06-04_unblock_mutation_contract_runtime_and_retire_spell_mutation_override_epic.md`
- EXIT_GATE:
  - dynamic-mode `MutationContract` is no longer blanket-disabled in phase 4
  - unresolved mutation sockets are represented as gated/unresolved rather than
    as a permanent disabled feature
  - mutation rebinding dirties/resets spell runtime shape through the existing
    spell-local path only
  - tests cover the new phase-4 semantics and the changed runtime expectation
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the first slice cannot land
  without also changing analyzer/planner/runtime packaging in the same pass.

## Scope Boundaries
- In scope:
  - phase-4 mutation-contract validation semantics
  - phase-4 gated-state publication
  - spell-local dirty/reset behavior for mutation rebinding through existing
    invalidation only
  - targeted unit/experimentation test updates
- Out of scope:
  - planner or phase-11 lane collapse
  - mutation analyzer rewrite redesign
  - final strategy-system convergence

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: this is the smallest implementation slice that moves
  mutation contracts toward the late-bound-hole model without prematurely
  rewriting downstream compiler structure.

## Steps / Checklist
- [x] Change `ContractProviderPresenceStrategy` so dynamic-mode mutation sockets
      are treated as unresolved/gated instead of blanket-disabled.
- [x] Update `CompilerPhase4` to gate unresolved mutation sockets the same way
      unresolved spell contracts are gated.
- [x] Keep mutation rebinding on the existing spell-local invalidation path so
      the next meld re-enters deferred runtime resolution.
- [x] Update validation, phase-4, spell, and experimentation tests.

## Validation
- Not run.
- Planned:
  - targeted pytest for validation strategy tests
  - targeted pytest for compiler phase-4 tests
  - targeted pytest for spell mutation tests
  - targeted pytest for mutation experimentation path

## Applicable Anti-Patterns
- [ ] Do not add a second bespoke meld-time mutation check beside the existing
      spell-contract flow.
- [ ] Do not keep `MutationContract` both "enabled" and still semantically
      unresolved without a gated/runtime-fail path.
- [ ] Do not collapse planner/phase-11 lanes in the same slice.

## Notes
- DATETIME: 2026-06-06T09:05:33Z
  TYPE: PLAN
  CLAIM: The first implementation slice is phase-4 semantics plus spell-local
    dirty/reset behavior. That is the smallest change that can make mutation
    sockets behave like late-bound holes while still reusing the existing
    meld/deferred-resolution pipeline.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:532-580
  - src/melder/aether/spellbook/spell.py:918-998
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py:125-128
  IMPACT: This slice can change semantics safely before planner/phase-11
    convergence work starts.
  NEXT: patch validation semantics first, then update the tests around the new
    unresolved-hole behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T09:33:14Z
  TYPE: FACT
  CLAIM: The first mutation convergence slice is now implemented. Dynamic-mode
    `MutationContract` sockets are no longer blanket-disabled in phase 4; they
    now warn as unresolved (`MUTATION_CONTRACT_MISSING_PROVIDER`) until a
    spell-local mutation binding exists, while automatic mode still errors.
    `CompilerPhase4` now gates unresolved mutation sockets the same way it
    gates unresolved `SpellContract` sockets, and
    `Spell.apply_mutation_override` / `clear_mutation_override` stay on the
    existing spell-local invalidation path so the next meld re-enters deferred
    runtime resolution without introducing extra live-creation eviction
    behavior.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py:116-182
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py:145-173
  - src/melder/aether/spellbook/spell.py:918-998
  - src/melder/aether/spellbook/spell.py:1146-1232
  IMPACT: The system now has the core late-bound-hole semantics needed for
    mutation sockets without adding a second bespoke meld-time mutation check.
    The next meld after mutation rebinding reuses the existing deferred
    resolution path.
  NEXT: decide the second slice: either align analyzer/planner semantics to the
    new contract or collapse the downstream mutation lane assumptions in
    planner/phase-11 packaging.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T09:37:44Z
  TYPE: DECISION
  CLAIM: The temporary owner-creations extraction behavior added during
    mutation rebinding was rejected and removed. This slice now keeps mutation
    rebinding strictly on the existing spell-local invalidation path:
    clear `CreationContext`, mark `resolution_required`, and let the next meld
    re-enter deferred runtime resolution without adding new live-creation
    eviction semantics.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:918-998
  - src/melder/aether/spellbook/spell.py:1146-1232
  - tests/unit/melder/spellbook/test_spell.py:790-832
  IMPACT: The first slice stays aligned to the agreed contract and does not
    widen behavior beyond phase-4 mutation semantics plus the existing
    invalidation/revalidation path.
  NEXT: keep follow-on work focused on downstream analyzer/planner/runtime
    convergence only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T09:33:14Z
  TYPE: MEASURE
  CLAIM: The targeted mutation-contract slice passes the narrow validation,
    phase-4, spell, and experimentation test surface under the project 3.14
    venv.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_contract_provider_presence_strategy.py:320-572
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_4.py:155-211
  - tests/unit/melder/spellbook/test_spell.py:122-175
  - tests/unit/melder/spellbook/test_spell.py:790-832
  - tests/unit/melder/spellbook/test_spell.py:1101-1128
  - tests/experimentation/test_mutation_override_requires_mutation_contract_experiment.py:1-348
  IMPACT: The first slice is stable enough to move from semantic setup into the
    next convergence choice without guessing at the immediate runtime contract.
  NEXT: keep follow-on work scoped to downstream analyzer/planner/runtime shape.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the first concrete implementation slice for mutation contract
convergence: phase-4 late-bound-hole semantics and spell-local dirty/reset
behavior, without yet collapsing planner or phase-11 mutation lanes.
