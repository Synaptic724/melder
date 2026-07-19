# Task: Remove Transaction Migration Compat And Owned Introspection

## Metadata
- Task ID: TASK-2026-05-22-remove-transaction-migration-compat-and-owned-introspection
- Story: STORY-2026-05-22-define-spellindex-transfer-and-registration-semantics
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p0
- Created: 2026-05-22T19:57:36Z
- Updated: 2026-06-01T11:37:34Z

## Objective
Remove the backward-compat transaction adapter and the owned-code
`getattr`/`hasattr` migration fallbacks from the `Spellbook` / `Conduit`
transaction seam so the runtime is a direct migration to the new mediator path
and complies with the `synaptic_python_developer` overlay.

## Ticket Contract
- ENTRY_GATE: the full pytest suite is currently green after transaction
  stabilization, but the user explicitly rejected the migration seam because it
  still contains backward-compat and owned-code introspection patterns that
  violate the active Python overlay.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spellbook.py`
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py`
  - directly implicated unit/integration tests only
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `tickets/tasks/2026-05-22_wire_transaction_identity_and_mediator_into_spellbook_and_conduit_task.md`
  - `tickets/tasks/2026-05-22_stabilize_full_pytest_suite_after_transaction_wiring_task.md`
- EXIT_GATE: the compatibility adapter is gone, the owned-code
  `getattr`/`hasattr` migration fallbacks are removed from the transaction seam,
  touched migration methods have acceptable contract docstrings/comments, and
  focused plus full-suite pytest runs are green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if removing the compatibility
  seam requires widening into unrelated architectural migration beyond
  Spellbook/Conduit/mediator surfaces.

## Scope Boundaries
- In scope:
  - remove `_LegacyMediatorAdapter`
  - remove owned-code `getattr` / `hasattr` fallbacks added in the migration seam
  - update directly implicated tests to the direct mediator model
  - tighten docstrings/comments on touched migration methods
- Out of scope:
  - broader transaction architecture beyond this seam
  - unrelated pre-existing introspection patterns outside the touched migration path
  - new feature work

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the user explicitly rejected the current migration seam as
  non-compliant with the active Python overlay and asked for a real migration
  rather than backward-compat glue.

## Steps / Checklist
- [ ] Remove `_LegacyMediatorAdapter` and require the real mediator surface.
- [ ] Remove owned-code `getattr` / `hasattr` fallbacks added in the transaction seam.
- [ ] Update tests/stubs to use the real direct mediator/request model.
- [ ] Tighten docstrings/comments on touched migration methods.
- [ ] Run focused validation for spellbook/conduit/mediator seams.
- [ ] Rerun the full pytest suite.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before
      further investigation.

## Deliverables
- direct mediator-only Spellbook/Conduit migration seam
- removal of owned-code introspection fallbacks introduced by the migration
- updated seam tests/stubs
- full-suite green validation

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-22_remove_transaction_migration_compat_and_owned_introspection_task.md`
- `codex/context_compass/attention_board.md`
- `src/melder/aether/spellbook/spellbook.py`
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py`
- directly implicated tests only

## Validation
- Not run.
- Recommended commands:
  - `./.venv_new/Scripts/python.exe -m pytest -q tests/unit/melder/spellbook/test_spellbook.py tests/unit/melder/aether/conduit/test_conduit_contracts.py tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_mediator.py`
  - `./.venv_new/Scripts/python.exe -m pytest -q`

## Risks / Rollback Notes
- Risk: a few unit tests still rely on weak doubles that were only passing
  because of the compat path.
  Rollback: move the compatibility behavior into the tests/stubs, not the
  runtime seam.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No backward-compat or introspection glue kept just to preserve stale tests.

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
- CLEANUP_TRIGGER: ticket closure

## Noting Behavior
- Note focus: tactical seam violations, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-01T11:37:34Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this remaining active lane for closure and
    requested that it be turned in and moved to the completed task set.
  EVIDENCE:
  - user_instruction
  IMPACT: This task is closed and should no longer route active work on the
    attention board.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-22T19:57:36Z
  TYPE: FACT
  CLAIM: The current transaction migration seam is functionally green but
    profile-noncompliant. The offending patterns are explicit: the Spellbook
    migration still carries `_LegacyMediatorAdapter` plus `hasattr(...)`
    checks, and the conduit contract gate still uses owned-code `getattr(...)`
    fallbacks to accommodate weak test doubles.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:2098-2192
  - src/melder/aether/conduit/conduit.py:3290-3302
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:721-721
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/banned_patterns.md:1-96
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/AGENTS.MD:108-176
  IMPACT: Leaving the seam this way would mean the runtime is not actually a
    clean migration to the new transaction system and still violates the active
    Python overlay that governs this repo.
  NEXT: remove the compat path from Spellbook, move required fallback behavior
    into test doubles, replace migration-seam introspection with direct
    contracts, and rerun focused validation first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-22T20:11:10Z
  TYPE: MEASURE
  CLAIM: The non-Spellbook side of the seam is now cleaner and still green.
    `TransactionMediator` no longer uses `getattr(...)` for its thread-local
    stack or transaction-type normalization, and its docs/comments now state
    the actual model: same-thread recursion must be explicit, while distinct
    same-thread local roots still reach normal admission instead of being
    silently merged.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:106-131
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:424-432
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:726-741
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:756-763
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:877-892
  IMPACT: The mediator side is no longer carrying the same style of owned-code
    introspection garbage that polluted the runtime seam, so the remaining work
    is concentrated back where it belongs: `Spellbook` and then `Conduit`.
  NEXT: stop at the `Spellbook` seam, explain exactly what transaction logic is
    still living there, and wait for alignment before touching it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This is a bounded compliance cleanup lane immediately after full-suite
stabilization. The runtime should remain on the new mediator path, but the
seam must stop relying on backward-compat glue and owned-code introspection.

