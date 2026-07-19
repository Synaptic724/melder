# Task: Investigate Rift Single Space Invariant
- Completed: 2026-04-19T16:54:36Z
- Summary: Closed during the 2026-04-19 cleanup pass after downstream single-space implementation landed.

## Metadata
- Task ID: TASK-2026-04-18-investigate-rift-single-space-invariant
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T12:12:27Z
- Updated: 2026-04-19T16:54:36Z

## Objective
Investigate how to enforce the intended invariant that one `Rift` owns exactly
one space, that space is created once at Rift construction time, and the active
space cannot later be changed.

## Ticket Contract
- ENTRY_GATE: the user explicitly redirected from the event-system lane to fix
  the one-space-per-Rift problem first.
- EXECUTION_BOUNDARY: investigation and implementation planning only; no source
  edits yet.
- DEPENDENCIES:
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/utilities/interfaces/interfaces.py
  - src/melder/aether/nexus/nexus.py
  - tests/unit/melder/aether/test_rift_runtime_contracts.py
  - tests/unit/melder/aether/test_nexus.py
  - tests/integration/melder/aether/rift/static_rift_json_testbench_support.py
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py
- EXIT_GATE: the live blast radius and the bounded refactor plan are explicit
  enough to propose before implementation.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the single-space invariant
  requires a broader `Rift`/`IRift` redesign than the user intends in this
  pass.

## Scope Boundaries
- In scope:
  - current multi-space storage and API surface on `Rift`
  - direct `Nexus` assumptions about multiple spaces
  - direct unit/integration test assumptions
  - bounded refactor plan for one immutable space per Rift
- Out of scope:
  - actual runtime patching
  - event-system replacement
  - frame-contract changes

## Steps / Checklist
- [ ] Read the live `Rift` multi-space storage and APIs.
- [ ] Read the direct `IRift` multi-space contract.
- [ ] Read the direct `Nexus` consumer path.
- [ ] Read the unit/integration tests that still assume multi-space behavior.
- [ ] Propose the bounded single-space refactor plan.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed blast-radius inventory
- bounded refactor plan

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: a hard single-space invariant breaks existing helper/test code that
  still assumes room lookup by id/name and active-space mutation.
- Rollback: stay investigation-only until the exact replacement API is agreed.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-18T12:12:27Z
  TYPE: FACT
  CLAIM: The current runtime still models `Rift` as a multi-space owner.
    `Rift` stores `_spaces_by_id`, `_space_ids_by_name`, and `_active_space_id`,
    exposes `register_space(...)`, `get_space(...)`, `get_space_by_name(...)`,
    `set_active_space(...)`, and `list_space_ids()`, and `Nexus` still loops
    over `rift.list_space_ids()` when refreshing attached viewers after ACL
    changes.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:92-97
  - src/melder/aether/nexus/rift/rift.py:879-1092
  - src/melder/aether/nexus/nexus.py:2012-2033
  - src/melder/utilities/interfaces/interfaces.py:7589-7673
  IMPACT: The invariant change is real API surgery, not just a private-field
    cleanup.
  NEXT: map the direct unit/integration tests that still assert multi-space
    behavior, then propose the replacement surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T12:12:27Z
  TYPE: FACT
  CLAIM: The direct test surface already narrows the real blast radius. Unit
    tests assert that `list_space_ids()` returns one primary room on create,
    but the true multi-space assumptions live in:
    - `test_rift_register_space_rejects_wrong_owner_and_duplicates`
    - `test_rift_space_lookup_and_active_space_errors_are_explicit`
    - `test_rift_space_lookup_and_active_space_success_paths_use_live_registry`
    Integration benches only use `rift.get_space(rift.active_space_id)` to grab
    the single primary room.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:540-541
  - tests/unit/melder/aether/test_nexus.py:809-817
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:515-588
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:640-644
  - tests/integration/melder/aether/rift/static_rift_json_testbench_support.py:183-190
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py:119-126
  IMPACT: The integration side is already mostly single-space in practice. The
    main work is deleting the multi-space runtime surface and rewriting the few
    direct unit tests that still expect it.
  NEXT: propose the bounded refactor plan, including which methods/properties
    should die and what minimal replacement surface should remain.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the investigation and planning pass for enforcing a one-space,
immutable-space model on `Rift`.
