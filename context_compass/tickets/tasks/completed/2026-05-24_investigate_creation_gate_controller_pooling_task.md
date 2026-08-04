# Task: Investigate CreationGateController Pooling

## Metadata
- Task ID: TASK-2026-05-24-investigate-creation-gate-controller-pooling
- Story: none
- Status: done
- Owner: codex
- Agent Name: searcher_0
- Priority: p1
- Created: 2026-05-24T00:45:01Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Determine whether `CreationGateController` can safely pool and recycle conduit
gates, including root-scope gates, without breaking gate lifecycle, drain
semantics, or controller indexing.

## Ticket Contract
- ENTRY_GATE: certification is active for `searcher_0`, and this task is routed
  from `attention_board.md` before any pooling design or implementation work.
- EXECUTION_BOUNDARY:
  - `src/melder/utilities/synchronization/creation_gate_controller.py`
  - `src/melder/utilities/synchronization/creation_gate.py`
  - direct runtime call sites that create or unregister conduit gates
  - directly implicated tests around creation gates and creation-context factory
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - current conduit and creation-context gate usage in runtime
  - current creation-gate tests as evidence for lifecycle expectations
- EXIT_GATE:
  - current gate lifecycle and indexing model is explicit
  - pooling feasibility and constraints are summarized truthfully
  - any implementation recommendation is bounded by actual gate semantics
- FAILURE_ESCALATION: raise `BLOCKER` if pooling would require changing gate
  identity/lifecycle semantics more broadly than the user requested.

## Scope Boundaries
- In scope:
  - whether conduit gates have reusable identity/state today
  - whether cleanup/unregister semantics permit gate reuse
  - whether root and lesser conduit paths can share one pool
  - direct test and runtime seams that would need to change
- Out of scope:
  - implementing pooling before the investigation is complete
  - unrelated synchronization or lock refactors
  - speculative micro-optimizations outside the gate lifecycle

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a gate-pooling investigation
  before any runtime change is attempted.

## Steps / Checklist
- [ ] Read `CreationGate` lifecycle and state model.
- [ ] Read `CreationGateController` registry/indexing model.
- [ ] Read runtime call sites that create, register, and unregister conduit gates.
- [ ] Read direct tests that encode current gate assumptions.
- [ ] Summarize whether pooling is safe, what must reset on reuse, and what
      breaks if we recycle current gate objects.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one evidence-backed gate lifecycle map
- one evidence-backed pooling feasibility assessment
- one bounded recommendation for the next implementation slice if pooling is viable

## Files / Paths Impacted
- `src/melder/utilities/synchronization/creation_gate_controller.py`
- `src/melder/utilities/synchronization/creation_gate.py`
- directly implicated runtime/tests
- `codex/context_compass/attention_board.md`
- this task ticket

## Validation
- Not run.
- Recommended commands:
  - `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\component\melder\utilities\synchronization\test_creation_gate_component.py`
  - `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\meld\creation_context\test_creation_context_factory.py`

## Risks / Rollback Notes
- Risk: `CreationGate` may not be safely reusable after cleanup or close/drain.
  Rollback: keep investigation strict and reject pooling if current semantics
  make reuse unsafe.
- Risk: root/lesser pooling may need extra controller state that costs more than
  it saves.
  Rollback: recommend narrower pooling or no pooling based on evidence.

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
- CLEANUP_TRIGGER: user-directed after the pooling decision is accepted

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
- DATETIME: 2026-05-24T00:45:01Z
  TYPE: PLAN
  CLAIM: The user wants a conduit-gate pool with a hard cap of 20 recycled
    gates, but asked for investigation first. The immediate job is to prove
    whether current `CreationGate` objects are even structurally reusable and
    whether controller indexing semantics tolerate reassignment.
  EVIDENCE:
  - user_request: current thread
  IMPACT: The next correct move is to read the gate/controller lifecycle and
    the direct runtime call sites before designing a pool.
  NEXT: read `creation_gate.py`, `creation_gate_controller.py`, and the direct
    gate creation/unregister call sites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T00:46:43Z
  TYPE: FACT
  CLAIM: Current `CreationGate` objects are not naturally reusable. The gate
    itself has no stored conduit/root/index identity; the controller owns those
    ids in its dict indexes. But the gate owns terminal lifecycle state:
    `_closed`, `enabled`, `_event`, `_tickets`, and `_cleaned`. A gate that has
    been drained via `close_and_wait_until_free(...)` stays `_closed=True`, and
    a gate that has been `cleanup()`'d deletes the very fields needed for use.
    So pooling cannot work by “just reassigning the id” on current gate objects.
  EVIDENCE:
  - src/melder/utilities/synchronization/creation_gate.py:38-66
  - src/melder/utilities/synchronization/creation_gate.py:72-108
  - src/melder/utilities/synchronization/creation_gate.py:287-306
  - src/melder/utilities/synchronization/creation_gate_controller.py:273-318
  - src/melder/utilities/synchronization/creation_gate_controller.py:380-403
  IMPACT: If we want pooling, we need an explicit gate reset/release contract,
    not just controller-level key reassignment. The current lifecycle makes
    reuse unsafe after close/drain or cleanup.
  NEXT: inspect the direct runtime release path (`Conduit` cleanup and
    CreationContextFactory spell-index gates) to see where a future pool would
    need to intercept gate teardown.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to determine whether `CreationGateController` can safely reuse
conduit gates through a bounded pool without violating current gate semantics.

