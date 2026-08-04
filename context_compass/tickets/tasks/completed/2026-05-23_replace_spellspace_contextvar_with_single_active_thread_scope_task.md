# Task: Replace Spellspace ContextVar With Thread-Local Spellspace Stack
- Completed: 2026-05-30T15:06:13Z
- Summary: Closed by explicit user instruction during the 2026-05-30 compiler-strategy lane reset. This ticket is superseded as an active route by the new execution-strategy compiler direction.


## Metadata
- Task ID: TASK-2026-05-23-replace-spellspace-contextvar-with-thread-local-spellspace-stack
- Story: none
- Status: done
- Owner: codex
- Agent Name: searcher_0
- Priority: p0
- Created: 2026-05-23T14:28:23Z
- Updated: 2026-05-30T15:06:13Z

## Objective
Replace the per-conduit dynamic `ContextVar` spellspace stack with a
thread-local spellspace stack that preserves recursive spellspace push/pop
behavior without dynamic `ContextVar` lifetime issues.

## Ticket Contract
- ENTRY_GATE: user explicitly selected the new contract: keep recursive
  spellspace semantics, but stop using dynamic `ContextVar` storage.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/aether/conduit/creations/creations.py`
  - directly implicated spellspace tests under `tests/**`
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - spellspace runtime currently uses a per-conduit `ContextVar`
  - component/integration/unit spellspace tests are the contract surface
- EXIT_GATE:
  - runtime uses the new thread-local spellspace stack storage
  - nested spellspace entry/exit still restores the prior active scope
  - directly implicated tests are updated and green
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if one or more existing tests
  prove that nested spellspace behavior is still required outside the contract
  the user just selected.

## Scope Boundaries
- In scope:
  - spellspace active-scope storage
  - conduit spellspace enter/exit behavior
  - creations active-spellspace lookup
  - directly implicated spellspace tests and experiments
- Out of scope:
  - broader conduit lighter-init work
  - DevOps identity or ConduitWard changes
  - unrelated benchmark files

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly chose to preserve spellspace
  recursion semantics while replacing the per-conduit `ContextVar`.

## Steps / Checklist
- [ ] Replace the conduit spellspace `ContextVar` storage with per-thread state.
- [ ] Preserve nested `enter_spellspace()` push/pop semantics on the same thread.
- [ ] Update `Creations.get_active_spellspace()` to use the new storage.
- [ ] Update directly implicated unit/component/integration/experimental tests.
- [ ] Run focused validation on the updated spellspace surfaces.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one runtime spellspace storage change
- one thread-local recursive spellspace contract
- updated spellspace tests that match the new contract

## Files / Paths Impacted
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/creations/creations.py`
- `tests/unit/melder/aether/conduit/test_conduit_lifecycle.py`
- `tests/component/melder/aether/conduit/test_conduit_component_spellspace_creations.py`
- `tests/integration/melder/conduit/test_conduit_integration_existence.py`
- directly implicated spellspace tests under `tests/integration/melder/conduit/**`
- directly implicated spellspace experiment files under `tests/experimentation/**`
- `codex/context_compass/attention_board.md`
- this task ticket

## Validation
- Focused validation ran.
- Commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\test_conduit_lifecycle.py tests\component\melder\aether\conduit\test_conduit_component_spellspace_creations.py tests\integration\melder\conduit\test_conduit_integration_existence.py tests\integration\melder\conduit\test_conduit_integration_spellspace_hooks.py tests\integration\melder\conduit\test_conduit_integration_spellspace_additional.py tests\integration\melder\conduit\test_conduit_integration_spellspace_edgecases.py`
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\experimentation\test_spellspace_cross_thread_scope_experiment.py`

## Risks / Rollback Notes
- Risk: tests or runtime flows still assume nested spellspace recursion.
  Rollback: surface the concrete failing contract and ask before widening.
- Risk: one or more experiments rely on raw `_spellspace_stack.set(...)`.
  Rollback: update those to the new explicit thread-local helper surface
  instead of preserving the old `ContextVar` internals.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

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
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: task closure

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-23T14:28:23Z
  TYPE: PLAN
  CLAIM: The selected spellspace contract is now explicit: preserve recursive
    push/pop semantics, but stop using a per-conduit dynamic `ContextVar`.
    The implementation work is to replace that storage mechanism while keeping
    nested restoration behavior intact.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:265-268
  - src/melder/aether/conduit/conduit.py:681-713
  - src/melder/aether/conduit/creations/creations.py:581-588
  - tests/unit/melder/aether/conduit/test_conduit_lifecycle.py:360-378
  - tests/component/melder/aether/conduit/test_conduit_component_spellspace_creations.py:165-193
  - tests/integration/melder/conduit/test_conduit_integration_spellspace_hooks.py:79-93
  IMPACT: The next step is the runtime edit in `Conduit` and `Creations`,
    keeping the current nested-restoration behavior while replacing the storage
    primitive.
  NEXT: patch the runtime spellspace storage and entry/exit behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-23T14:44:48Z
  TYPE: MEASURE
  CLAIM: The spellspace runtime now keeps its recursive push/pop behavior
    while dropping the dynamic per-conduit `ContextVar` storage. `Conduit`
    now uses a conduit-owned thread-local spellspace stack holder, `Creations`
    reads the active spellspace from that new holder, nested spellspace tests
    remain green, and the cross-thread experiment now correctly asserts that
    active spellspace state is not inherited by spawned threads.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:264-268
  - src/melder/aether/conduit/conduit.py:681-713
  - src/melder/aether/conduit/creations/creations.py:80-81
  - src/melder/aether/conduit/creations/creations.py:581-586
  - src/melder/aether/conduit/spell_space/spell_space_thread_state.py:1-71
  - tests/experimentation/test_spellspace_cross_thread_scope_experiment.py:169-193
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\test_conduit_lifecycle.py tests\component\melder\aether\conduit\test_conduit_component_spellspace_creations.py tests\integration\melder\conduit\test_conduit_integration_existence.py tests\integration\melder\conduit\test_conduit_integration_spellspace_hooks.py tests\integration\melder\conduit\test_conduit_integration_spellspace_additional.py tests\integration\melder\conduit\test_conduit_integration_spellspace_edgecases.py`
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\experimentation\test_spellspace_cross_thread_scope_experiment.py`
  IMPACT: The immediate `ContextVar` lifetime concern is removed from the
    conduit spellspace runtime without changing `unique_per_spell_space`
    semantics or nested spellspace behavior.
  NEXT: move back to the broader conduit lesser-scope cost work and measure
    whether spellspace churn meaningfully improved on the Melder-only gauntlet.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-23T15:00:18Z
  TYPE: MEASURE
  CLAIM: The directly drifted meld unit tests are now aligned to the new
    spellspace state holder as well. The file had still been constructing
    `Creations` with raw `ContextVar` instances in helper paths and direct
    spellspace live-creation tests; those are now using the same
    `SpellSpaceThreadState` contract as the runtime, and the full meld unit
    file is green again.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/meld/test_meld.py:1-20
  - tests/unit/melder/aether/conduit/meld/test_meld.py:731-757
  - tests/unit/melder/aether/conduit/meld/test_meld.py:2296-2407
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\meld\test_meld.py`
  IMPACT: The spellspace runtime change is no longer carrying obvious unit-test
    drift on the meld side, so the next performance/debugging pass can focus on
    lesser-conduit cost rather than more spellspace contract fallout.
  NEXT: resume the lesser-conduit cost investigation from the Melder gauntlet
    with spellspace drift cleared.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task changes spellspace from dynamic per-conduit `ContextVar` stack
storage to thread-local stack storage while preserving recursive spellspace
entry/exit behavior and active-scope validation.
