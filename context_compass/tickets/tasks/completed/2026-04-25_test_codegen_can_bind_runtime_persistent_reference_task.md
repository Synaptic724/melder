# Task: Test Codegen Can Bind Runtime Persistent Reference
- Completed: 2026-04-26T09:56:44Z
- Summary: Closed after the bounded integration proof showed that a
  codegen-created definition reference can be bound through the live conduit
  and then resolved outside the original codegen call.

## Metadata
- Task ID: TASK-2026-04-25-test-codegen-can-bind-runtime-persistent-reference
- Story:
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T22:29:57Z
- Updated: 2026-04-26T09:56:44Z

## Objective
Add one bounded proof test showing whether codegen can create or import a
bindable definition reference, register it through the live runtime, and then
use that registered reference outside the original codegen execution call.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a real proof test for
  codegen-created reference binding and runtime survival.
- EXECUTION_BOUNDARY:
  - codegen runtime namespace/bind surfaces required to support the proof
  - directly affected tests and helpers under `tests/`
  - this task ticket and `attention_board.md`
- DEPENDENCIES:
  - existing codegen unit/component/integration matrix files
  - current codegen namespace and command/runtime support
- EXIT_GATE: one focused proof test exists, its contract is explicit, and the
  focused validation ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the current runtime does not
  actually expose a bind path from codegen and the task would require a new
  runtime feature instead of a proof test.

## Scope Boundaries
- In scope:
  - proving the bind/reference persistence behavior
  - directly required helper adjustments
- Out of scope:
  - broad codegen API redesign
  - persistence across process restart
  - unrelated namespace or validator work

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the proof test is landed and the focused integration
  validation ring is green.

## Steps / Checklist
- [ ] Inspect the current codegen harness and bind-access surfaces.
- [ ] Record the first evidence-backed constraint in `## Notes`.
- [ ] Add the bounded proof test and any minimal helper support needed.
- [ ] Run focused validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- focused test proving or disproving runtime-sticky reference binding from codegen
- focused validation result

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-25_test_codegen_can_bind_runtime_persistent_reference_task.md
- codex/context_compass/attention_board.md
- tests/unit/melder/aether/
- tests/component/melder/aether/
- tests/integration/melder/aether/
- directly required helpers under `tests/`
- directly required runtime files only if the proof exposes a real gap

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/integration/melder/aether/test_codegen_system_integration_matrix.py -k "bind"`

## Risks / Rollback Notes
- Risk: the current runtime may not expose the bind path in the codegen
  namespace the way the user expects.
  Rollback: stop at the first hard evidence and ask whether to add a runtime
  surface instead of pretending the proof is already possible.

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
- DATETIME: 2026-04-25T22:29:57Z
  TYPE: PLAN
  CLAIM: This task is a bounded proof-test lane for one specific question:
    can codegen produce a bindable definition reference, register it through
    the live runtime, and then use that registered reference outside the
    original codegen execution call.
  EVIDENCE:
  - user_instruction: "if your confident this works, lets test it out go ahead and make a test"
  - user_instruction: "see if you can generate an object and register it such that it survives the codegen space and then gets utilized outside of it"
  IMPACT: The first obligation is to read the existing codegen harness and the
    actual bind-access surface before writing the test.
  NEXT: inspect the integration harness and the current codegen runtime/helper
    surfaces in the minimal scope needed for the proof.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-25T22:29:57Z
  TYPE: FACT
  CLAIM: The current runtime does expose a viable bind path from codegen for a
    proof test. The codegen namespace includes the room `command` object, the
    codegen command surface exposes `get_conduit_by_name(...)`, and the live
    `Conduit` object exposes `begin_binding_transaction()` plus `bind(...)`.
    That means the proof can stay test-only and does not require a new runtime
    feature first.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py:215-232
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py:150-168
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:200-235
  - src/melder/aether/conduit/conduit.py:2086-2159
  - src/melder/aether/conduit/conduit.py:2159-2228
  IMPACT: The experiment should prove reference binding from codegen directly
    through the live codegen room, not through an artificial test-only backdoor.
  NEXT: add an integration test that defines a class in codegen, binds it
    through the live conduit, and then melds it outside the original codegen
    call.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T22:34:53Z
  TYPE: MEASURE
  CLAIM: The proof test is green. A generated class definition created inside
    one codegen execution call can be bound through the live conduit and then
    resolved outside the original codegen call through the normal conduit
    lookup/meld surfaces. In other words, the definition reference survives in
    the runtime after the original code string is gone.
  EVIDENCE:
  - tests/integration/melder/aether/test_codegen_system_integration_matrix.py:126-173
  - validation_result: `python -m pytest -q tests/integration/melder/aether/test_codegen_system_integration_matrix.py -k "bind_generated_reference_and_use_it_afterward"` -> `1 passed, 40 deselected, 2 warnings`
  IMPACT: This proves the repo-specific model directly: codegen can manufacture
    a definition reference, bind it into the live runtime, and use it later
    outside the original codegen namespace execution.
  NEXT: return the proof result and let the user decide whether to close the
    task or widen it into more registration-path experiments.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the bounded proof-test lane for runtime-sticky reference
binding from codegen.
