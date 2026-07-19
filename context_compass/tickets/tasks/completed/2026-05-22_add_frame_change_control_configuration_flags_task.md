# Task: Add Frame Change Control Configuration Flags

## Metadata
- Task ID: TASK-2026-05-22-add-frame-change-control-configuration-flags
- Story: STORY-2026-05-22-define-spellindex-transfer-and-registration-semantics
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-22T16:33:10Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Extend `AethericFrameConfiguration` with frame-level change-control policy
settings and set the requested defaults explicitly.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested the config slice first, before
  transaction-engine changes.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aetheric_frame/aetheric_frame_configuration.py`
  - `tests/unit/melder/aether/test_aetheric_frame_configuration.py`
  - `tests/_frame_posture_test_support.py`
- DEPENDENCIES:
  - `tickets/tasks/2026-05-22_investigate_spellindex_transfer_semantic_drift_task.md`
- EXIT_GATE: the new frame configuration properties exist, defaults match the
  user request, and focused unit tests are green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the requested config shape
  collides with existing frame-posture invariants.

## Scope Boundaries
- In scope:
  - frame config fields
  - validation/defaulting logic
  - test posture helper propagation
  - focused unit tests
- Out of scope:
  - wiring the new flags into ChangeControlManager behavior
  - transaction mediator implementation
  - broader runtime policy changes

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the user requested the frame configuration surface first
  so later transaction redesign can bind to a stable config contract.

## Steps / Checklist
- [x] Add the change-control configuration fields to `AethericFrameConfiguration`.
- [x] Set defaults: strict mode, single-root default, mutation disabled by default, all other disable flags false.
- [x] Propagate the fields through frame posture test helpers.
- [x] Add/update focused frame-configuration unit tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before
      further investigation.

## Deliverables
- expanded frame-level change-control config surface
- focused tests covering defaults and posture description

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-22_add_frame_change_control_configuration_flags_task.md`
- `codex/context_compass/attention_board.md`
- `src/melder/aether/aetheric_frame/aetheric_frame_configuration.py`
- `tests/unit/melder/aether/test_aetheric_frame_configuration.py`
- `tests/_frame_posture_test_support.py`

## Validation
- Ran:
  - `pytest -q tests/unit/melder/aether/test_aetheric_frame_configuration.py`

## Risks / Rollback Notes
- Risk: posture equality/description helpers drift if the new config fields are
  added to init but not to comparison/reporting.
  Rollback: keep the slice narrow and update constructor, defaults,
  `matches_posture`, `describe_posture`, and helper builders together.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No wiring runtime behavior to the new flags in this slice.

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
- DATETIME: 2026-05-22T16:33:10Z
  TYPE: FACT
  CLAIM: `AethericFrameConfiguration` is the correct first surface for these
    flags. It already owns the frame-global posture contract (`system_state`,
    `ai_native_enabled`, `rift_enabled`,
    `shared_framewide_spellbook_configuration`), provides defaulting helpers,
    and is already consumed by direct unit tests plus the frame posture helper
    used by integration fixtures. So adding transaction-policy fields here
    keeps the policy frame-local and lets later transaction work read one
    canonical source instead of scattering booleans across Spellbook/Conduit.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:11-355
  - tests/unit/melder/aether/test_aetheric_frame_configuration.py:1-188
  - tests/_frame_posture_test_support.py:1-192
  IMPACT: We can land the config contract cleanly first without touching
    runtime transaction behavior yet.
  NEXT: patch the frame configuration fields/defaults and update the focused
    tests/helpers in the same slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T16:36:00Z
  TYPE: MEASURE
  CLAIM: The frame configuration slice is landed and the focused unit file is
    green (`12 passed`). `AethericFrameConfiguration` now carries the
    frame-local change-control policy surface with these defaults:
    `change_control_mode='strict'`,
    `allow_multiple_root_transactions=False`,
    `disable_all_transactions_after_conjure=False`,
    `disable_mutations=True`,
    `disable_linking=False`,
    `disable_bind=False`,
    `disable_conduit_cluster=False`,
    `disable_transfer_of_ownership=False`, and
    `disable_contract_mutation=False`. The detached frame posture helpers and
    `describe_posture()` / `matches_posture()` now carry the same fields.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:11-355
  - tests/_frame_posture_test_support.py:1-192
  - tests/unit/melder/aether/test_aetheric_frame_configuration.py:1-188
  IMPACT: We now have one canonical frame-local policy surface that later
    transaction redesign can read without scattering more flags through
    Spellbook/Conduit first.
  NEXT: get user review on this config slice, then wire the new frame policy
    into the live change-control path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This is a narrow config-contract slice extracted from the broader transaction
redesign discussion. It should stay focused on the frame-owned configuration
surface and its default values only.

