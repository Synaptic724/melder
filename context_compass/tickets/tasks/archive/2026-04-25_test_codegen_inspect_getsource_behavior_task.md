# Task: Test Codegen Inspect Getsource Behavior

## Metadata
- Task ID: TASK-2026-04-25-test-codegen-inspect-getsource-behavior
- Story:
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-04-25T22:39:00Z
- Updated: 2026-04-25T22:49:49Z

## Objective
Measure and document what `inspect.getsource(...)` does for a definition
created inside codegen and optionally bound into the live runtime.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested an inspect-based experiment over a
  codegen-created definition.
- EXECUTION_BOUNDARY:
  - current codegen integration harness and directly required helpers
  - one focused experiment or proof test
  - this task ticket and `attention_board.md`
- DEPENDENCIES:
  - `tests/integration/melder/aether/test_codegen_system_integration_matrix.py`
  - `tests/_codegen_system_support.py`
  - current codegen room/runtime surfaces
- EXIT_GATE: the inspect/getsource behavior is evidenced from a focused run and
  recorded clearly enough to explain the real runtime story.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the current codegen profile
  surface blocks the experiment and a new runtime feature would be required.

## Scope Boundaries
- In scope:
  - inspect/getsource behavior for codegen-generated definitions
  - binding the generated definition when needed for the experiment
  - focused validation/measurement
- Out of scope:
  - broad codegen persistence redesign
  - restart/replay provenance
  - unrelated namespace or validator refactors

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly asked to try `inspect.getsource(...)`
  on a codegen-generated definition.

## Steps / Checklist
- [ ] Inspect the current codegen harness and reflection-capable profile path.
- [ ] Record the first evidence-backed constraint in `## Notes`.
- [ ] Run the bounded experiment and capture the behavior.
- [ ] Land a focused test only if that materially helps preserve the result.
- [ ] Record validation/measurement.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- focused measurement of `inspect.getsource(...)` behavior for codegen-created definitions
- optional proof test if warranted

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-25_test_codegen_inspect_getsource_behavior_task.md
- codex/context_compass/attention_board.md
- tests/integration/melder/aether/
- directly required helpers only

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/integration/melder/aether/test_codegen_system_integration_matrix.py -k "getsource"`

## Risks / Rollback Notes
- Risk: the result is environment-specific and should not be overgeneralized.
  Rollback: keep the claim tied to the current codegen compiler/runtime path.

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
- DATETIME: 2026-04-25T22:39:00Z
  TYPE: PLAN
  CLAIM: This is a bounded inspect/getsource experiment over a
    codegen-generated definition. The first step is to use the existing
    codegen integration harness rather than reason abstractly about Python
    introspection.
  EVIDENCE:
  - user_instruction: "yeah so lets try using inspect.getsource and see what happens if you codegen it whats the story there?"
  IMPACT: The lane is measurement first; only add a permanent test if the
    result is worth preserving in the suite.
  NEXT: read the current codegen integration harness and the reflection-capable
    profile path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-25T22:39:00Z
  TYPE: FACT
  CLAIM: The current codegen integration harness can run the experiment without
    a new runtime feature first. A `full_access` codegen room already allows
    `inspect` import plus the room `command` surface, and that command surface
    can return the live root conduit object needed for a real bind call.
  EVIDENCE:
  - tests/_codegen_system_support.py:189-205
  - tests/integration/melder/aether/test_codegen_system_integration_matrix.py:13-26
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py:215-232
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py:150-168
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:200-235
  - src/melder/aether/conduit/conduit.py:2086-2228
  IMPACT: The experiment can stay inside the live codegen room and does not
    need a test-only backdoor or a new command surface first.
  NEXT: land a focused integration test around the measured `inspect` behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T22:39:00Z
  TYPE: FACT
  CLAIM: The first draft of the proof test failed on a frame lookup detail, not
    on the core inspect/bind behavior. The generated spell was registered in
    the `ops` frame, but `Conduit.get_spell_by_id(...)` defaulted to the
    `default` frame when the test tried to fetch it back.
  EVIDENCE:
  - tests/integration/melder/aether/test_codegen_system_integration_matrix.py:181-181
  - src/melder/aether/conduit/conduit.py:1600-1639
  - src/melder/aether/aether.py:1440-1449
  IMPACT: The proof stays valid; the test just needs to query the same frame it
    bound into.
  NEXT: patch the test to fetch the spell from `ops` and rerun the focused ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-25T22:49:49Z
  TYPE: MEASURE
  CLAIM: The focused inspect/getsource proof is green. In the live codegen
    room, `inspect.getsource(...)` fails on the generated class both inside
    the original codegen execution and later outside it after the class
    reference has been bound into the runtime. The bind still lands, and the
    bound reference remains usable through the runtime after the original
    codegen call ends.
  EVIDENCE:
  - tests/integration/melder/aether/test_codegen_system_integration_matrix.py:126-192
  - validation_result: `python -m pytest -q tests/integration/melder/aether/test_codegen_system_integration_matrix.py -k "generated_definition_getsource_fails_but_binding_persists"` -> `1 passed, 41 deselected, 2 warnings`
  IMPACT: The current runtime story is now explicit: reference binding works,
    but `inspect.getsource(...)` is not a reliable provenance recovery path for
    codegen-generated definitions under the current compiler/namespace model.
  NEXT: return the measured behavior and let the user decide whether to stop at
    the proof or widen into provenance design.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the bounded inspect/getsource experiment for codegen-created
definitions.
