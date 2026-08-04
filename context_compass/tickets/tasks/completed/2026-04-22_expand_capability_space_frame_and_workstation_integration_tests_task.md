# Task: Expand Capability Space Frame And Workstation Integration Tests
- Completed: 2026-04-24T01:03:27Z
- Summary: Closed during the 2026-04-24 cleanup after the first capability integration tranche was accepted as sufficient.

## Metadata
- Task ID: TASK-2026-04-22-expand-capability-space-frame-and-workstation-integration-tests
- Story: none
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-22T23:10:44Z
- Updated: 2026-04-24T01:03:27Z

## Objective
Add a larger capability-room integration suite that proves frame-link,
default-frame, Nexus-created-frame, rooted-conduit, and workstation-binding
behavior together through real `CapabilityRiftSpace` flows.

## Ticket Contract
- ENTRY_GATE: the strict create-vs-get Nexus contract is landed and the live
  capability-room/runtime docs have been reread this session.
- EXECUTION_BOUNDARY:
  - capability-space integration tests
  - directly related shared test helpers
  - ticket/board state for this lane
- DEPENDENCIES:
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py
  - src/melder/aether/nexus/rift/rift_space/workstation.py
  - src/melder/aether/nexus/rift/command_system/capability_command_system.py
  - tests/integration/melder/aether/test_nexus_frame_authoring_integration.py
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py
- EXIT_GATE: the new capability-space integration set covers the requested
  default-frame link plus Nexus-created-frame/workstation flows and the focused
  integration ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the requested integration
  surface needs runtime changes or a broader test-harness redesign instead of a
  bounded integration-test expansion.

## Scope Boundaries
- In scope:
  - capability-space integration tests for linking to a default frame
  - doing object/workstation operations through capability space
  - creating a new Nexus-managed frame, getting the rooted conduit, and moving
    objects into workstation-visible state
  - about 30 high-signal integration tests, not filler
- Out of scope:
  - runtime feature work unless a test proves a real contract gap
  - unrelated static/codegen room coverage
  - broad test-harness refactors

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the new 30-case capability-space integration matrix is
  implemented and the focused file-level integration run is green.

## Steps / Checklist
- [x] Read the existing capability-space, workstation, and Nexus frame-authoring integration surfaces.
- [x] Identify the real contract matrix for default-frame link, object work, Nexus-created frame, conduit access, and workstation binding.
- [x] Add the new capability-space integration tests.
- [x] Keep the tests contract-level and non-filler.
- [x] Run the focused integration ring.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- expanded capability-space integration test matrix
- focused integration validation result

## Files / Paths Impacted
- tests/integration/melder/aether/
- codex/context_compass/attention_board.md

## Validation
- Executed:
  - `python -m pytest -q tests/integration/melder/aether/test_capability_space_frame_and_workstation_integration.py`
- Result:
  - `30 passed, 2 warnings`

## Risks / Rollback Notes
- Risk: the test count target encourages filler.
  Rollback: keep the matrix organized around distinct contract cases only.
- Risk: capability-room behavior may not yet expose the exact workstation
  object flow the user wants.
  Rollback: prove the missing seam explicitly and stop before widening into
  runtime edits.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

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
- DATETIME: 2026-04-22T23:10:44Z
  TYPE: PLAN
  CLAIM: This task exists to make the new capability-room integration push
    explicit and bounded. The requested surface is larger than one smoke test:
    default-frame link, object work through capability space, Nexus-created
    frames, rooted conduit retrieval, and workstation binding all need to be
    exercised together.
  EVIDENCE:
  - user_instruction: "make some integration tests to link to a default frame, do soe work with some objects, then this might require a good mock setup and then make a new frame get the conduit, put objects in it and then bring them into the workstation? make like 30 integration tests for this using capability space"
  IMPACT: The next step is to read the current capability/workstation/frame
    integration surfaces and build the matrix from real behavior rather than
    inventing tests blindly.
  NEXT: inspect the existing capability-space and frame-authoring integration
    tests plus shared helpers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-22T23:10:44Z
  TYPE: FACT
  CLAIM: The repo already has a reusable live capability-room integration
    harness instead of requiring a new mock-heavy harness from scratch.
    `CapabilityRiftJsonBench` builds a real `CapabilityRiftSpace`, links the
    selected frame, exposes live command/workstation surfaces, and already
    supports multistep turn scripts that bind objects into the workstation and
    execute target calls.
  EVIDENCE:
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py:52-112
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py:164-205
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py:237-307
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py:296-384
  IMPACT: The new test lane should extend the existing capability integration
    harness and its turn-script matrix rather than inventing a new fake-heavy
    test setup.
  NEXT: finish reading the rest of the capability integration matrix and the
    workstation/command seams so the missing contract cases are explicit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-22T23:10:44Z
  TYPE: FACT
  CLAIM: The existing live capability-room surfaces already expose the exact
    operations needed for the requested test lane. `CapabilityRiftSpace`
    inherits the generic viewer posture and composes `CapabilityCommandSystem`,
    `CommandSystem` exposes live conduit fetch plus `meld(...)`,
    `meld_existing_spell(...)`, and `execute_target_method(...)`, and
    `Workstation` already supports `bind_object`, `bind_attribute`,
    `bind_method`, `set_target`, and `call_target`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py:13-88
  - src/melder/aether/nexus/rift/command_system/capability_command_system.py:6-19
  - src/melder/aether/nexus/rift/command_system/command_system.py:376-447
  - src/melder/aether/nexus/rift/command_system/command_system.py:1863-2072
  - src/melder/aether/nexus/rift/rift_space/workstation.py:188-283
  - src/melder/aether/nexus/rift/rift_space/workstation.py:371-518
  IMPACT: The new integration matrix can stay on real runtime behavior without
    a new mock-heavy bench or runtime edits.
  NEXT: add the missing capability integration matrix around default-frame
    link, workstation binding modes, and Nexus-created-frame handoff flows.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-22T23:10:44Z
  TYPE: FACT
  CLAIM: The first run of the new matrix failed only on my spell-metadata
    expectation, not on the capability-room runtime behavior. The command
    spell metadata surfaces report `spell_name='CapabilityWorkspaceService'`
    for the bound service, while the binding name stays separate.
  EVIDENCE:
  - tests/integration/melder/aether/test_capability_space_frame_and_workstation_integration.py:398-407
  - test_run_output: `AssertionError: assert 'CapabilityWorkspaceService' == 'default_live'`
  IMPACT: The metadata assertions should check the service-class spell name or
    the explicit spell id/index/source surfaces, not conflate spell name with
    binding name.
  NEXT: patch the two failing metadata assertions and rerun the new integration
    file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-22T23:10:44Z
  TYPE: MEASURE
  CLAIM: The new capability-space integration lane is green. The added file
    contributes 30 real integration cases across three matrices:
    default-frame link/workstation flows, Nexus-created-frame/workstation
    flows, and dual-frame capability-room handoff flows.
  EVIDENCE:
  - tests/integration/melder/aether/test_capability_space_frame_and_workstation_integration.py:1-820
  - test_run_output: `30 passed, 2 warnings`
  IMPACT: The requested capability-space frame/workstation coverage now exists
    as a real integration surface instead of one-off smoke checks.
  NEXT: review the new test file and decide whether this matrix is sufficient
    or whether another capability-room seam should be added.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the capability-space integration expansion lane requested by the
user. The new 30-case capability-room integration matrix is implemented and
review-ready.
