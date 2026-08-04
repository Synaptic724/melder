# Task: Implement Rift Gate And Rift Gate Controller
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-18-implement-rift-gate-and-rift-gate-controller
- Story: STORY-2026-04-18-investigate-and-plan-rift-gate-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T17:29:47Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Add `RiftGate` and `RiftGateController` as near-copy coordination primitives
for the Rift runtime, with controller ownership on `Nexus` and one gate owned
by each `Rift`.

## Ticket Contract
- ENTRY_GATE: the investigation task proved the creation-gate model is the
  correct first-cut template and the user explicitly approved proceeding with
  the copy-style implementation.
- EXECUTION_BOUNDARY: new Rift gate/controller files, `Nexus`, `Rift`,
  interfaces, and the directly affected unit tests.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_investigate_and_plan_rift_gate_model_task.md
  - src/melder/utilities/synchronization/creation_gate.py
  - src/melder/utilities/synchronization/creation_gate_controller.py
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/utilities/interfaces/interfaces.py
- EXIT_GATE: `RiftGate` and `RiftGateController` exist, `Nexus` owns the
  controller, each `Rift` owns one gate, and the focused validation ring is
  green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if adding the gate/controller
  requires immediate projection or command/view integration beyond this bounded
  first slice.

## Scope Boundaries
- In scope:
  - `src/melder/aether/nexus/rift/rift_gate.py`
  - `src/melder/aether/nexus/rift/rift_gate_controller.py`
  - one gate on each `Rift`
  - one controller on `Nexus`
  - create/register/unregister ownership wiring
  - direct interfaces/tests
- Out of scope:
  - validation-step callback feature
  - projection split
  - command/view/codegen gate integration

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user approved the copy-style first implementation cut.

## Steps / Checklist
- [x] Add `RiftGate` as a near-copy of `CreationGate`.
- [x] Add `RiftGateController` as a near-copy of `CreationGateController`.
- [x] Add one gate field to `Rift`.
- [x] Add one controller field to `Nexus`.
- [x] Wire create/register on `Nexus.create_rift(...)`.
- [x] Wire unregister on `Nexus.remove_rift(...)`.
- [x] Wire cleanup on `Rift.cleanup()`.
- [x] Add focused unit tests.
- [x] Validate the focused ring.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `RiftGate`
- `RiftGateController`
- Nexus/Rift ownership wiring
- focused validation evidence

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift_gate.py
- src/melder/aether/nexus/rift/rift_gate_controller.py
- src/melder/aether/nexus/rift/rift.py
- src/melder/aether/nexus/nexus.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/

## Validation
- `python -m py_compile src/melder/aether/nexus/rift/rift_gate/rift_gate.py src/melder/aether/nexus/rift/rift_gate_controller/rift_gate_controller.py src/melder/aether/nexus/rift/rift.py src/melder/aether/nexus/nexus.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_rift_gate.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py`
- `python -m pytest -q tests/unit/melder/aether/test_rift_gate.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py`
- Result: `131 passed`

## Risks / Rollback Notes
- Risk: stale assumptions about ownership during Rift creation/removal.
- Rollback: keep the first cut bounded to registry/ownership only and avoid
  integrating gate checks into runtime operations yet.

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
- DATETIME: 2026-04-18T18:12:15Z
  TYPE: FACT
  CLAIM: The second bounded Rift-gate slice is now landed. `RiftGate` gained a
    real gate-crossing API through `admit()` plus configurable `entry_mode`
    (`wait` or `raise`), `RiftGateController` can now update entry modes per
    Rift or globally, and `Nexus` exposes the same control surface. This gives
    us the basic "block or fail-fast at the gate" behavior needed before any
    later projection integration work.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_gate/rift_gate.py:1-307
  - src/melder/aether/nexus/rift/rift_gate_controller/rift_gate_controller.py:1-286
  - src/melder/aether/nexus/nexus.py:1-1094
  - src/melder/utilities/interfaces/interfaces.py:7656-8044
  - tests/unit/melder/aether/test_rift_gate.py:1-182
  - tests/unit/melder/aether/test_nexus.py:520-557
  IMPACT: The gate primitive now matches the conduit-style admission semantics
    closely enough that later Rift operations can reuse it directly.
  NEXT: return this task for review and decide whether to close it or wire the
    gate into projection-dependent operations next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T18:12:15Z
  TYPE: MEASURE
  CLAIM: The focused Rift-gate ring remains green after adding entry-mode and
    admit semantics.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift_gate/rift_gate.py src/melder/aether/nexus/rift/rift_gate_controller/rift_gate_controller.py src/melder/aether/nexus/nexus.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_rift_gate.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_gate.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py` -> 135 passed
  IMPACT: The new admission behavior is stable enough to review before we use
    it in later runtime slices.
  NEXT: wait for acceptance before closure or further widening.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T18:07:20Z
  TYPE: DECISION
  CLAIM: The next bounded Rift-gate delta should be an explicit gate-crossing
    method plus configurable entry behavior, not unsafe thread termination. The
    gate should support an admission mode of either `wait` or `raise`, so
    future Rift operations can use the same "check closed, maybe wait, maybe
    raise" semantics as the conduit meld path. We do not need a separate
    continuation-check feature yet because the same admission method can be
    reused at later checkpoints cooperatively.
  EVIDENCE:
  - src/melder/utilities/synchronization/creation_gate.py:150-209
  - src/melder\aether\conduit\conduit.py:2468-2476
  - user_instruction: "when it crosses the gate, we should have the option of stopping it"
  - user_instruction: "if theres a check, we want it to raise so the thread terminates"
  IMPACT: The gate can stay simple and still cover the semantics you want:
    block-before-entry or fail-fast-before-entry, with cooperative reuse inside
    longer-running code later.
  NEXT: add `entry_mode` plus `admit()` to `RiftGate`, then expose mode control
    through the controller and Nexus.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T18:07:20Z
  TYPE: DECISION
  CLAIM: The next likely Rift-gate delta is not unsafe external thread killing.
    The safe model is:
    1. admission control before crossing the gate (`wait` or `raise`)
    2. optional cooperative abort checks after crossing for code that chooses
       to re-check gate state at defined checkpoints.
    Threads already past the gate are in-flight work tracked by tickets; they
    can be drained and observed, but not force-terminated safely from the gate
    itself.
  EVIDENCE:
  - src/melder/utilities/synchronization/creation_gate.py:150-209
  - src/melder/utilities/synchronization/creation_gate.py:211-389
  - src/melder/aether/conduit/conduit.py:2468-2476
  - user_instruction: "the thread when it crosses the gate, we should have the option of stopping it"
  - user_instruction: "something that already passed the gate is basically in deep"
  IMPACT: If we extend `RiftGate`, we should add admission-mode plus
    cooperative checkpoint semantics, not pretend the gate can safely kill
    arbitrary in-flight threads.
  NEXT: wait for approval before widening the gate beyond the landed copy-style
    first cut.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T18:07:20Z
  TYPE: FACT
  CLAIM: The first bounded Rift-gate slice is now landed. `RiftGate` and
    `RiftGateController` exist as near-copies of the creation-gate model,
    `Nexus` owns one controller, each `Rift` owns one gate, `Nexus.create_rift(...)`
    now creates/registers the gate, `Nexus.remove_rift(...)` unregisters it,
    and `Rift.cleanup()` cleans its own gate.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_gate/rift_gate.py:1-223
  - src/melder/aether/nexus/rift/rift_gate_controller/rift_gate_controller.py:1-249
  - src/melder/aether/nexus/rift/rift.py:1-265
  - src/melder/aether/nexus/nexus.py:1-950
  - src/melder/utilities/interfaces/interfaces.py:7656-8015
  - tests/unit/melder/aether/test_rift_gate.py:1-145
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:1-459
  - tests/unit/melder/aether/test_nexus.py:488-557
  IMPACT: The Rift runtime now has a first-class gate/control primitive owned
    in the right places before the later projection integration slice.
  NEXT: return this task for review and decide whether to close it or continue
    directly into wiring the gate into viewer/command/codegen operations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T18:07:20Z
  TYPE: MEASURE
  CLAIM: The focused Rift-gate validation ring is green.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift_gate/rift_gate.py src/melder/aether/nexus/rift/rift_gate_controller/rift_gate_controller.py src/melder/aether/nexus/rift/rift.py src/melder/aether/nexus/nexus.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_rift_gate.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_gate.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py` -> 131 passed
  IMPACT: The first gate/controller slice is stable enough to review before any
    wider runtime integration.
  NEXT: wait for acceptance before closing the lane or widening scope.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T17:29:47Z
  TYPE: PLAN
  CLAIM: The first implementation cut is intentionally narrow: copy the
    creation-gate behavior into the Rift layer, keep controller ownership on
    `Nexus`, keep actual gate ownership on `Rift`, and defer validation-step
    callbacks plus projection integration until later.
  EVIDENCE:
  - tickets/tasks/2026-04-18_investigate_and_plan_rift_gate_model_task.md:87-100
  - user_instruction: "just stick to the plan and add the Riftgate"
  IMPACT: We can land the primitive cleanly without widening into the next
    architecture slice.
  NEXT: patch the new gate/controller files and the ownership wiring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T17:29:47Z
  TYPE: FACT
  CLAIM: The existing Rift/Nexus lifecycle gives us a clean ownership seam for
    the first gate slice. `Nexus.create_rift(...)` constructs the Rift under
    the Nexus lock and registers it immediately afterward, while
    `Nexus.remove_rift(...)` removes the Rift from registries before calling
    `rift.cleanup()`. That means Nexus can create/register one gate during
    Rift creation, unregister it during Rift removal, and let the Rift own the
    actual gate instance for cleanup.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:628-707
  - src/melder/aether/nexus/nexus.py:829-872
  - src/melder/aether/nexus/rift/rift.py:76-151
  - src/melder/aether/nexus/rift/rift.py:199-243
  IMPACT: The first implementation slice can stay bounded to ownership and
    registry wiring without touching command/view/codegen integration yet.
  NEXT: implement `RiftGate`, `RiftGateController`, and the Nexus/Rift wiring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the first bounded `RiftGate` / `RiftGateController`
implementation slice.