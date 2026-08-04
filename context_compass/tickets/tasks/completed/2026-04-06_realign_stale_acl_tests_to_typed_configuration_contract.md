# Task: Realign Stale ACL Tests To Typed Configuration Contract
- Completed: 2026-04-06T12:17:44Z
- Summary: Accepted review slice moved out of the active lane during the 2026-04-06 board cleanup after the user advanced to later ACL/frame-surface work.


## Metadata
- Task ID: TASK-2026-04-06-realign-stale-acl-tests-to-typed-configuration-contract
- Story: STORY-2026-04-05-frame-acl-typed-configuration-foundation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T01:20:00Z
- Updated: 2026-04-06T12:17:44Z

## Objective
Repair the stale ACL chain/subsystem tests that still construct legacy JSON
ACL payloads so the active test surface matches the live typed ACL
configuration contract.

## Ticket Contract
- ENTRY_GATE: the typed ACL configuration slice is landed, the user supplied
  concrete failing ACL tests, and certification is restored.
- EXECUTION_BOUNDARY: stale ACL test repair and the smallest required runtime
  contract adjustment only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-05_implement_frame_acl_typed_configuration_foundation.md
  - src/melder/aether/nexus/acl/frame_acl_configuration.py
  - src/melder/aether/nexus/acl/frame_acl_view_configuration.py
  - src/melder/aether/nexus/acl/frame_acl_codegen_configuration.py
  - tests/unit/melder/aether/test_frame_acl_chain_matrix.py
  - tests/unit/melder/aether/test_frame_acl_configuration_chain.py
  - tests/unit/melder/aether/test_frame_acl_subsystem.py
- EXIT_GATE: the stale ACL tests use the live configuration contract or an
  intentional compatibility path, and the affected ACL test surface passes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the smallest correct fix
  requires restoring broader legacy JSON compatibility instead of updating the
  tests.

## Scope Boundaries
- In scope:
  - failing ACL chain/subsystem/unit tests
  - minimal ACL loader/runtime adjustment if the contract truly requires it
  - focused validation for the affected ACL test surface
- Out of scope:
  - new ACL features
  - viewer/frame-link integration
  - broad repo-wide test cleanup

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the task was turned in during the cleanup pass after the user advanced to later ACL/frame-surface work.
## Steps / Checklist
- [x] Confirm whether the failing tests are stale or whether the runtime needs
      a compatibility path.
- [x] Update the failing ACL tests to the live typed config shape or add the
      minimal intentional loader adapter.
- [x] Run the affected ACL test surface.
- [x] Document findings, implementation, and validation in `## Notes`.

## Deliverables
- repaired ACL chain/subsystem tests
- minimal runtime adjustment if required
- focused validation evidence

## Files / Paths Impacted
- src/melder/aether/nexus/acl/
- tests/unit/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_chain_matrix.py tests/unit/melder/aether/test_frame_acl_configuration_chain.py tests/unit/melder/aether/test_frame_acl_subsystem.py`

## Risks / Rollback Notes
- Risk: restoring broad legacy JSON compatibility would silently weaken the
  new typed ACL contract.
  Rollback: keep the fix test-local unless direct runtime evidence proves
  compatibility is intended.

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
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-06T01:20:00Z
  TYPE: PLAN
  CLAIM: The next bounded repair slice is the stale ACL test surface the user
    pasted. The typed ACL configuration objects now require view/codegen child
    config identity fields, while several older ACL chain/subsystem tests still
    construct the legacy `{frame_name, view_acl, codegen_acl}` payload shape.
    The first job is to prove whether those tests are simply stale or whether
    the runtime intentionally still supports that legacy JSON contract.
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_acl_chain_matrix.py:32-32
  - tests/unit/melder/aether/test_frame_acl_configuration_chain.py:29-29
  - tests/unit/melder/aether/test_frame_acl_subsystem.py:103-103
  - src/melder/aether/nexus/acl/frame_acl_configuration.py:210-210
  - src/melder/aether/nexus/acl/frame_acl_view_configuration.py:88-88
  IMPACT: We should not blindly loosen the new ACL runtime if the real problem
    is stale tests.
  NEXT: inspect the failing tests and the typed ACL JSON loader path together,
    then classify the repair as test-only or minimal compatibility restore.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T01:28:00Z
  TYPE: FACT
  CLAIM: The current failing surface is stale-test drift against the new typed
    ACL configuration loader. The chain tests still build legacy JSON payloads
    like `{frame_name, view_acl, codegen_acl}`, and the subsystem test still
    uses the even older `{frame_acl, conduit_acls, spellbook_acls, spell_acls}`
    shape. The live loader now reads `view_configuration` and
    `codegen_configuration`, and the child config constructors require
    non-empty `profile_name` / `profile_version` fields plus the
    view-side `minimum_spell_payload_profile_name`.
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_acl_chain_matrix.py:117-117
  - tests/unit/melder/aether/test_frame_acl_chain_matrix.py:393-417
  - tests/unit/melder/aether/test_frame_acl_configuration_chain.py:86-323
  - tests/unit/melder/aether/test_frame_acl_subsystem.py:103-104
  - src/melder/aether/nexus/acl/frame_acl_configuration.py:210-214
  - src/melder/aether/nexus/acl/frame_acl_view_configuration.py:206-209
  - src/melder/aether/nexus/acl/frame_acl_view_configuration.py:87-93
  - src/melder/aether/nexus/acl/frame_acl_codegen_configuration.py:190-191
  - src/melder/aether/nexus/acl/frame_acl_codegen_configuration.py:82-85
  IMPACT: The default expectation should be to realign the stale tests to the
    live typed contract unless direct runtime evidence proves broader legacy
    compatibility is intentional.
  NEXT: read the failing test files and one passing typed-config test file
    fully, then patch the stale tests to the new JSON payload shape.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T01:38:00Z
  TYPE: FACT
  CLAIM: The repair stays test-local so far. The stale chain/subsystem tests
    now build valid typed ACL payloads instead of the legacy JSON shapes. Each
    test file now has a small helper that emits the live
    `view_configuration` / `codegen_configuration` payload structure with the
    required profile identity fields, while still preserving distinct payload
    markers where the tests need different revisions or history nodes.
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_acl_chain_matrix.py:1-541
  - tests/unit/melder/aether/test_frame_acl_configuration_chain.py:1-380
  - tests/unit/melder/aether/test_frame_acl_subsystem.py:1-254
  IMPACT: We can validate the stale surface without broadening the runtime
    loader contract yet.
  NEXT: run the affected ACL test files and see whether any deeper contract
    mismatch remains.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T01:40:00Z
  TYPE: MEASURE
  CLAIM: The targeted stale ACL surface is green. The repaired chain matrix,
    configuration chain, and subsystem tests all passed after the stale JSON
    payloads were realigned to the live typed ACL configuration contract. No
    runtime compatibility widening was required for this slice.
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_acl_chain_matrix.py:1-541
  - tests/unit/melder/aether/test_frame_acl_configuration_chain.py:1-380
  - tests/unit/melder/aether/test_frame_acl_subsystem.py:1-254
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_acl_chain_matrix.py tests/unit/melder/aether/test_frame_acl_configuration_chain.py tests/unit/melder/aether/test_frame_acl_subsystem.py
  IMPACT: The specific stale ACL failures the user pasted are resolved without
    weakening the live typed loader contract.
  NEXT: review the repaired test slice with the user and decide whether to
    broaden validation to the wider ACL suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to repair the stale ACL chain/subsystem tests after the typed
ACL configuration rollout changed the accepted JSON payload shape.



