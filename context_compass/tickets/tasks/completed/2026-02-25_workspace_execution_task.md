# Task: Workspace Execution Loop and Dispatch

## Metadata
- Task ID: TASK-2026-02-25-workspace-and-execution
- Story: STORY-2026-02-25-aethericrift-implementation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-25T10:57:22Z
- Updated: 2026-03-15T22:05:00Z
- Created By: e3098096-e1f8-4279-b98f-082737b2cca9

## Objective
Implement the Workspace class that agents interact with directly —
accepting code blocks, routing through the codegen validation pipeline,
dispatching to conduit(s) via Meld, managing session state, and returning
structured results.

## Ticket Contract
- ENTRY_GATE: TASK-2026-02-25-profiles-and-policy complete
- EXECUTION_BOUNDARY: Workspace module and governed execution stage only
- DEPENDENCIES: profiles/policy task, all upstream tasks,
  codegen pipeline design (stages 6-7)
- EXIT_GATE: Workspace accepts code, validates, classifies, dispatches
  to Meld, and returns structured results
- FAILURE_ESCALATION: raise DECISION_REQUEST if dispatch routing or
  session lifecycle edge cases are ambiguous

## Scope Boundaries
- In scope:
  - Workspace class (per-session codegen consumer, bound to one frame)
  - Session modes (static/ephemeral and workstation/persistent)
  - Code submission API (push_code / execute_code)
  - Governed execution (compile + exec in ExecutionContext namespace)
  - Dispatch to conduit(s) via Meld runtime
  - Thread limit enforcement at workspace dispatch (frame + conduit checks)
  - Result boxing (raw objects → ObjectRefs)
  - Structured error responses for agents
  - Session state management (manifest, execution context, object refs)
- Out of scope:
  - Iris logging tier (implemented last per design decision)
  - Transport/auth wrappers (separate layer per ACL decision)
  - Embargo mechanism internals (existing MeldGate substrate)

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: design artifacts approved and dependency tasks identified.

## Steps / Checklist
- [ ] Create `Workspace` class with session configuration.
- [ ] Implement static/ephemeral and workstation/persistent session modes.
- [ ] Implement code submission entry points.
- [ ] Wire validation pipeline (RiftEngine) into workspace execution flow.
- [ ] Implement governed execution (compile + exec in ExecutionContext).
- [ ] Implement dispatch to conduit via Meld.
- [ ] Implement thread limit checks at dispatch (frame + conduit profile).
- [ ] Implement result boxing and ObjectRef management.
- [ ] Implement structured error responses.
- [ ] Implement workspace cleanup (tear down session state, ObjectRefs).
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `Workspace` class with full execution lifecycle.
- `ObjectRef` boxing model.
- Integration tests: code submission → validation → dispatch → result.

## Files / Paths Impacted
- src/melder/aether/aetheric_rift/workspace.py (new)
- src/melder/aether/aetheric_rift/object_ref.py (new)
- src/melder/aether/aetheric_rift/facade.py (workspace creation wiring)

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/aetheric_rift/test_workspace.py -v`
  - `pytest tests/aetheric_rift/test_integration.py -v`

## Risks / Rollback Notes
- Risk: ObjectRef lifecycle leaks under error paths.
  Rollback: add explicit disposal hooks and session-bound cleanup.
- Risk: thread limit rejection UX unclear for agents.
  Rollback: add structured retry-after hints in error response.

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
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= `workflow.ticket_microcycle.minimum_note_score`)
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
- DATETIME: 2026-02-25T10:57:22Z
  TYPE: PLAN
  CLAIM: This task implements the agent-facing execution surface. Workspace is deliberately thin and policy-agnostic per design decision. It receives a behavioral surface from Policy Middleware, dispatches through RiftEngine validation, and routes to Meld. Session modes follow the interview decision: static uses ephemeral sessions, workstation uses explicit sessions.
  EVIDENCE:
  - tickets/artifacts/codegen_validation_pipeline_design.md:75-87
  - tickets/artifacts/aethericrift_facade_and_profile_architecture.md:90-113
  - tickets/artifacts/ai_profile_and_policy_middleware_design.md:153-173
  IMPACT: Completing this task delivers the full agent-facing execution surface for AethericRift v1.
  NEXT: begin after profiles/policy task completes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Final implementation task. Depends on all upstream tasks. Delivers the Workspace that agents use directly to submit code and receive results. Completing this task closes the AethericRift v1 implementation scope.


## Completion Summary
- Completed: 2026-03-15T22:05:00Z
- Summary: Superseded or completed during AR packaging cleanup; retained for historical reference.

