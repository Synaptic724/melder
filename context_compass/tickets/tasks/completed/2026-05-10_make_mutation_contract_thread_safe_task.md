Completed: 2026-06-06T18:18:17Z
Summary: Closed per user direction after MutationContract removal. The object-hardening slice is retained as historical work but is no longer an active runtime direction.

# Task: Make MutationContract Thread Safe

## Metadata
- Task ID: TASK-2026-05-10-make-mutation-contract-thread-safe
- Story:
- Epic: EPIC-2026-05-10-implement-mutation-contract-runtime-socket-management
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-10T20:31:18Z
- Updated: 2026-06-06T18:18:17Z

## Objective
Make `MutationContract` itself thread-safe enough for live in-memory mutation
work by adding an internal `RLock`, a supported update method, and fail-fast
post-cleanup behavior on its public methods/properties.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested this object-level hardening before
  broader MutationContract runtime enablement continues.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/meld/contracts/mutation_contract.py`
  - `tests/unit/melder/aether/conduit/meld/contracts/test_mutation_contract.py`
- DEPENDENCIES:
  - `tickets/tasks/2026-05-10_investigate_mutation_contract_runtime_socket_feature_task.md`
- EXIT_GATE: the contract object has a lock-disciplined cleanup/update/read
  path and the focused unit ring proves the new contract.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if preserving the current
  public field shape prevents an honest thread-safe contract without a wider
  API redesign.

## Scope Boundaries
- In scope:
  - internal `RLock`
  - supported update method
  - lock-disciplined cleanup
  - `check_cleaned()` on public read methods/properties
  - focused unit tests
- Out of scope:
  - MutationContract runtime enablement in SpellCrafter
  - MutationContract spell-facing getters/setters on `Spell`
  - MutationResearch redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user requested direct object-level hardening before
  the broader feature continues.

## Steps / Checklist
- [ ] Add an internal `RLock` to `MutationContract`.
- [ ] Hide mutable state behind supported read/update paths.
- [ ] Make `cleanup()` lock-disciplined and idempotent.
- [ ] Add/adjust focused unit tests for update behavior and cleaned-state guards.
- [ ] Run targeted validation.

## Deliverables
- thread-safe `MutationContract` object
- focused passing unit tests

## Files / Paths Impacted
- src/melder/aether/conduit/meld/contracts/mutation_contract.py
- tests/unit/melder/aether/conduit/meld/contracts/test_mutation_contract.py

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: preserving direct mutable field semantics makes the object only
  partially thread-safe.
  Rollback: treat the new update method as the supported mutation path and
  tighten tests around that contract explicitly.

## Applicable Anti-Patterns
- [ ] No widening into Spell/MutationContract runtime enablement in this task.
- [ ] No fake thread-safety claims without focused tests.
- [ ] No silent public-API drift without matching tests.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-10T20:31:18Z
  TYPE: PLAN
  CLAIM: The current `MutationContract` object is a simple mutable intent
    object with public writable fields and no lock. The bounded hardening pass
    is to add one internal `RLock`, put its public reads and supported writes
    behind that lock, and make cleanup invalidate the object consistently.
  EVIDENCE:
  - src/melder/aether/conduit/meld/contracts/mutation_contract.py:10-210
  - tests/unit/melder/aether/conduit/meld/contracts/test_mutation_contract.py:1-268
  IMPACT: This makes the object safer to use as a live in-memory mutation
    descriptor before broader runtime enablement is added.
  NEXT: patch the contract object and its direct unit tests only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T20:33:51Z
  TYPE: MEASURE
  CLAIM: The object-level hardening slice is landed and green. `MutationContract`
    now owns an internal `RLock`, stores mutable state behind supported
    read/update paths, uses a lock-disciplined cleanup path, and fail-fast
    checks its public methods/properties after cleanup. A new `update_contract(...)`
    method is the supported mutation path, and the focused unit file now proves
    update behavior, cleaned-state failures, and a basic threaded read/write
    smoke path.
  EVIDENCE:
  - src/melder/aether/conduit/meld/contracts/mutation_contract.py:1-300
  - tests/unit/melder/aether/conduit/meld/contracts/test_mutation_contract.py:1-400
  - validation_result:
    `python -m py_compile src/melder/aether/conduit/meld/contracts/mutation_contract.py tests/unit/melder/aether/conduit/meld/contracts/test_mutation_contract.py`
  - validation_result:
    `python -m pytest -q -p no:cacheprovider tests/unit/melder/aether/conduit/meld/contracts/test_mutation_contract.py` -> `31 passed`
  IMPACT: The live descriptor object is now much safer to use as an in-memory
    mutation surface before the larger runtime-enablement work resumes.
  NEXT: return the bounded object-hardening slice for review, then decide
    whether the next step is removing `MUTATION_CONTRACT_DISABLED` or adding
    spell-facing contract enumeration/update APIs first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T21:43:03Z
  TYPE: MEASURE
  CLAIM: The `update_contract(...)` API has now been corrected too. The earlier
    sentinel-driven partial-update signature using `...` was the wrong public
    shape. The method is now a full-replacement contract update with init-like
    types (`spell`, `spellframe`, `binding_name`, `spell_override`,
    `late_binding`), and callers who want to preserve existing state pass the
    current values explicitly. The direct unit ring and the bind/reference
    experiment both stayed green after the change.
  EVIDENCE:
  - src/melder/aether/conduit/meld/contracts/mutation_contract.py:226-286
  - tests/unit/melder/aether/conduit/meld/contracts/test_mutation_contract.py:345-418
  - tests/experimentation/mutation_contract_bind_reference_testbench.py:176-210
  - validation_result:
    `python -m py_compile src/melder/aether/conduit/meld/contracts/mutation_contract.py tests/unit/melder/aether/conduit/meld/contracts/test_mutation_contract.py tests/experimentation/mutation_contract_bind_reference_testbench.py`
  - validation_result:
    `python -m pytest -q -p no:cacheprovider tests/unit/melder/aether/conduit/meld/contracts/test_mutation_contract.py` -> `31 passed`
  - validation_result:
    `python tests/experimentation/mutation_contract_bind_reference_testbench.py` -> `OK_MUTATION_CONTRACT_REFERENCE_SHARED`, `OK_MUTATION_CONTRACT_UPDATE_STUCK`
  IMPACT: The live descriptor now has a cleaner public mutation API that
    matches its construction contract and avoids the confusing ellipsis-based
    sentinel pattern.
  NEXT: return the corrected object-hardening slice for review, then choose the
    next runtime-enablement seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the bounded object-level hardening pass for `MutationContract`.
