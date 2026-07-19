# Task: Replace Automatic Posture Input With Dynamic Flag

## Metadata
- Task ID: TASK-2026-05-23-replace-automatic-posture-input-with-dynamic-flag
- Story: none
- Status: done
- Owner: codex
- Agent Name: searcher_0
- Priority: p1
- Created: 2026-05-23T15:35:42Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Collapse the redundant conduit posture inputs by making `dynamic` the
canonical constructor/conjure flag and removing the internal `_automatic`
state plus `Conduit._apply_configuration_flags()`.

## Ticket Contract
- ENTRY_GATE: user explicitly selected the posture cleanup as the next slice.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spellbook.py`
  - `src/melder/aether/spellbook/spellbook_creation_system.py`
  - `src/melder/aether/conduit/conduit.py`
  - directly implicated tests/benchmarks that call these APIs
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - current posture model duplicates `system_state`, `automatic`, and
    `__dynamic_environment__`
  - spellspace and gauntlet work are already stable enough to isolate this cut
- EXIT_GATE:
  - runtime uses one canonical `dynamic` signal internally
  - `_automatic` is removed from the runtime path
  - `_apply_configuration_flags()` is removed
  - directly implicated validation is green
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if public compatibility fallout
  is wider than the bounded posture slice can safely absorb.

## Scope Boundaries
- In scope:
  - runtime posture flag cleanup
  - direct `conjure(...)` / `Conduit(...)` flag plumbing
  - directly implicated tests and benchmarks
- Out of scope:
  - `_aetheric_frame_name` removal
  - broader frame identity refactors
  - unrelated performance work

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the runtime posture path is carrying redundant state and
  the user explicitly chose the `automatic -> dynamic` cleanup as the next fix.

## Steps / Checklist
- [ ] Make `dynamic` the canonical runtime posture input.
- [ ] Remove `_automatic` from `SpellbookCreationSystem` and `Conduit`.
- [ ] Remove `Conduit._apply_configuration_flags()`.
- [ ] Update directly implicated tests and benchmarks.
- [ ] Run focused validation on the affected posture surfaces.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one runtime posture cleanup
- one direct validation result for the affected posture surfaces

## Files / Paths Impacted
- `src/melder/aether/spellbook/spellbook.py`
- `src/melder/aether/spellbook/spellbook_creation_system.py`
- `src/melder/aether/conduit/conduit.py`
- directly implicated tests/benchmarks under `tests/**` and `benchmarks/**`
- `codex/context_compass/attention_board.md`
- this task ticket

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\test_spellbook.py tests\unit\melder\aether\conduit\test_conduit_configuration_and_hooks.py tests\unit\melder\aether\conduit\test_conduit_transactions.py`

## Risks / Rollback Notes
- Risk: public API compatibility churn around `automatic=` named calls.
  Rollback: keep a bounded compatibility alias while removing internal
  `_automatic` state.
- Risk: message/assertion drift in tests that reference automatic-mode wording.
  Rollback: update only directly implicated posture assertions in this slice.

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
- DATETIME: 2026-06-01T11:05:49Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this lane as complete and requested that
    it be turned in and moved out of active routing.
  EVIDENCE:
  - user_instruction
  IMPACT: This ticket is now closed and should no longer appear in active
    board routing.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-23T15:35:42Z
  TYPE: PLAN
  CLAIM: The current posture model duplicates the same runtime concept across
    `automatic`, `system_state`, and `__dynamic_environment__`. The bounded
    cleanup is to make `dynamic` the canonical runtime input, remove internal
    `_automatic` storage, and delete `Conduit._apply_configuration_flags()`.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3597-3689
  - src/melder/aether/spellbook/spellbook_creation_system.py:73-183
  - src/melder/aether/spellbook/spellbook_creation_system.py:455-507
  - src/melder/aether/conduit/conduit.py:222-245
  IMPACT: This is a coherent runtime cleanup on its own and does not require
    the much wider `_aetheric_frame_name` field removal in the same patch.
  NEXT: patch the runtime posture files and keep public compatibility bounded.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-23T15:46:17Z
  TYPE: MEASURE
  CLAIM: The posture cleanup landed cleanly as an internal model refactor.
    `dynamic` is now the canonical runtime signal through `Spellbook.conjure`,
    `SpellbookCreationSystem`, and `Conduit`; `_automatic` is removed from the
    internal runtime path; and `Conduit._apply_configuration_flags()` is gone.
    A bounded compatibility alias remains at the public `conjure(...)` /
    `Conduit(...)` boundary so existing `automatic=` callsites still work
    while the runtime no longer stores or derives posture from multiple
    overlapping fields.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3597-3712
  - src/melder/aether/spellbook/spellbook_creation_system.py:72-119
  - src/melder/aether/spellbook/spellbook_creation_system.py:173-205
  - src/melder/aether/spellbook/spellbook_creation_system.py:279-307
  - src/melder/aether/spellbook/spellbook_creation_system.py:455-507
  - src/melder/aether/conduit/conduit.py:155-230
  - src/melder/aether/conduit/conduit.py:770-775
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\test_spellbook.py tests\unit\melder\aether\conduit\test_conduit_configuration_and_hooks.py tests\unit\melder\aether\conduit\test_conduit_transactions.py`
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q benchmarks\testing_other_di\test_melder_gauntlet.py`
  IMPACT: The posture model is now coherent enough to stop fighting duplicate
    `automatic`/`dynamic` sources while leaving the much wider
    `_aetheric_frame_name` refactor for a separate slice.
  NEXT: if you still want the frame-name cleanup, treat that as a separate job
    and do not mix it with more performance work in the same patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task collapses the duplicated conduit posture state onto one canonical
`dynamic` input without bundling the much larger frame-name refactor into the
same patch.

