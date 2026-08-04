# Task: Expand Capability Room Runtime Operations
- Completed: 2026-04-13T22:24:59Z
- Summary: Completed the focused capability-operations slice after cloud, link, cluster, and lesser-conduit behavior were proven on the focused runtime ring.

## Metadata
- Task ID: TASK-2026-04-12-expand-capability-room-runtime-operations
- Story: STORY-2026-04-12-investigate-capability-rift-space-runtime-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T20:20:00Z
- Updated: 2026-04-13T22:24:59Z

## Objective
Exercise and lock the real capability-room operational surface:
- conduit cloud
- lesser conduit creation
- linking
- clusters
- lower-runtime automatic-frame rejection where appropriate

## Ticket Contract
- ENTRY_GATE: the first capability cut is landed and the user asked to keep
  building the system out.
- EXECUTION_BOUNDARY: focused capability runtime/tests only.
- DEPENDENCIES:
  - src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py
  - src/melder/aether/conduit/conduit.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: capability behavior for cloud/link/cluster/lesser flows is proven
  on the focused ring and any missing seams are made explicit.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if this slice requires a larger
  capability integration harness before focused behavior can be proven.

## Scope Boundaries
- In scope:
  - focused capability behavior and tests
  - broad-manual access semantics
- Out of scope:
  - codegen
  - capability integration harness
  - viewer redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the first capability cut is in and the next step is to
  prove the actual room operations that matter.

## Steps / Checklist
- [x] Record the specific runtime operation set in notes.
- [x] Add/update focused capability tests for cloud/link/cluster/lesser flows.
- [x] Patch runtime only if a real missing seam is exposed.
- [x] Run focused validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- focused capability behavior coverage
- explicit note on any remaining missing seams

## Files / Paths Impacted
- tests/unit/melder/aether/test_nexus.py
- codex/context_compass/attention_board.md

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py`

## Risks / Rollback Notes
- Risk: capability still looks broad in theory but unproven in the exact
  runtime behaviors the user cares about.
  Rollback: prove the behavior with focused tests before widening further.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
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
- DATETIME: 2026-04-12T20:20:00Z
  TYPE: PLAN
  CLAIM: The next capability slice does not need a new API first. The current
    room/workstation surface is already broad enough to fetch real conduit
    objects, bind them, target them, and call methods on them. So the next
    useful move is to prove the room behaviors the user actually cares about:
    cloud access, linking, clusters, and lesser creation, plus the lower
    runtime rejection on automatic frames.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py:1-28
  - src/melder/aether/conduit/conduit.py:1421-1514
  - src/melder/aether/conduit/conduit.py:2303-2361
  - src/melder/aether/conduit/conduit.py:2794-2816
  - src/melder/aether/conduit/conduit.py:2874-2999
  IMPACT: Focused capability runtime proofs come before any more room-surface expansion.
  NEXT: add focused capability tests for those operations and see if any real missing seam remains.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T20:35:00Z
  TYPE: FACT
  CLAIM: The focused capability operation slice is now proven on the unit/runtime
    ring. The current capability room can:
    - access conduit cloud on dynamic frames
    - create lesser conduits on automatic frames
    - create/join/leave clusters on dynamic frames
    - link conduits on dynamic frames
    while still respecting the lower automatic-frame runtime floor for
    dynamic-only operations.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:2701-3014
  IMPACT: The current capability room is broader and more real than the first
    cut alone proved.
  NEXT: record validation and decide whether the next step is a capability
    integration harness or more focused room/runtime helpers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T20:35:00Z
  TYPE: MEASURE
  CLAIM: The expanded capability operation slice is green on the focused and
  nearby Rift/capability unit ring.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py` -> 117 passed
  IMPACT: Capability now has meaningful focused coverage beyond raw getters.
  NEXT: summarize the landed capability operation proof and choose whether to
  add a JSON integration harness next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T20:44:35Z
  TYPE: DECISION
  CLAIM: The next capability/runtime expansion should widen the shared
    manual-runtime vocabulary on the base `CommandSystem` instead of adding a
    second near-duplicate API only for capability/dynamic rooms.
    `StaticCommandSystem` should explicitly deny topology-mutation and
    creation-oriented operations, while `CapabilityCommandSystem` and
    `DynamicCommandSystem` inherit the shared manual surface. Codegen-only
    behavior stays outside the base command layer.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:252-789
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:9-382
  - src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py:6-37
  - src/melder/aether/nexus/rift/rift_space/command_system/dynamic_command_system.py:6-21
  - user_direction: "add all those into the command system ... deny them in static mode"
  IMPACT: The next code lane should be a base-command expansion plus explicit
    static denials, not capability-only API drift.
  NEXT: if implementation is approved, stage a follow-on task for widening the
    shared `CommandSystem` manual-runtime surface and adding static overrides
    for the unsafe operations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task proves the actual capability room operations before any wider
capability expansion. The next likely implementation cut is shared command
surface widening with explicit static denials, not a capability-only
manual-runtime fork.
