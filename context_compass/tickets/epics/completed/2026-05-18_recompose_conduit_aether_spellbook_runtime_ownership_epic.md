# Epic: recompose conduit aether spellbook runtime ownership

- Completed: 2026-05-21T09:48:52Z
- Summary: Closed by explicit user request as a retained-reference architecture epic. The linked refactor plan artifact remains preserved for future reference, but the epic is no longer an active execution route.

## Metadata
- Epic ID: EPIC-2026-05-18-recompose-conduit-aether-spellbook-runtime-ownership
- Status: done
- Owner: codex
- Agent Name: mypy_1
- Priority: p0
- Created: 2026-05-18T16:36:09Z
- Updated: 2026-05-21T09:48:52Z
- Target Window: 2026-Q2
- Related Program/Initiative: conduit-runtime-ownership-recomposition

## Problem / Opportunity
`Conduit` currently depends directly on `Aether` for spell registration,
conduit lookup, conduit cloud, cluster operations, gate/controller access, and
mutation-research access. That makes `Aether` act as both root owner and
service locator. The interface graph mirrors this and exposes import-time
cycles.

## MRP Alignment (Most Reasonable Product)
The long-term foundation needs one runtime ownership story that is coherent in:
- concrete runtime behavior
- interface graph
- typed/mypyc-friendly import structure

This epic is the staged plan for getting there without hiding the problem with
shims or interface cheats.

## Ticket Contract
- ENTRY_GATE: the current conduit/aether/spellbook architecture lane is routed
  and the first bounded task is active
- EXECUTION_BOUNDARY: conduit/runtime ownership decomposition only; no unrelated
  subsystem redesigns
- DEPENDENCIES:
  - artifacts/2026-05-18_conduit_aether_refactor_plan.md
  - tickets/tasks/2026-05-18_align_conduit_aether_dependency_to_spellbook_task.md
- EXIT_GATE: the planned stages are either completed or reduced into accepted
  follow-on stories/tasks with durable architecture notes
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if one stage requires a broader
  owner-boundary redesign than this epic currently frames

## Goals (Outcomes)
- Remove `Conduit -> Aether` as a direct dependency.
- Reassign spellbook-owned upstream queries to `Spellbook`.
- Reassign frame-scoped conduit network behavior to `ConduitCloud`.
- Narrow `Conduit` to explicit injected collaborators rather than root reach-back.

## Non-Goals (Explicit Exclusions)
- Full redesign of every interface in `utilities/interfaces/`
- Unrelated Nexus/ACL cleanup outside what this epic forces
- Global cleanup of all historical tickets/board rows

## Scope Boundaries
- In scope:
  - `Conduit`
  - `Spellbook`
  - `SpellbookCreationSystem`
  - `ConduitCloud`
  - directly implicated interfaces
- Out of scope:
  - unrelated AR/runtime cleanup
  - unrelated mutation subsystem redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a durable architecture plan
  artifact and epic before further implementation work

## Success Metrics
- `Conduit` no longer reaches directly into `Aether`.
- The architecture lanes are described durably enough to survive compaction.
- Each staged cut can be executed without re-deriving the design from chat.

## Requirements (Functional + Non-Functional)
- Keep the plan grounded in actual concrete call buckets.
- No shims as the architectural answer.
- Preserve a path that still works with strict type checking and future mypyc.

## Constraints / Assumptions
- `ConduitCloud` already exists as a frame-scoped conduit registry.
- `SpellbookCreationSystem` already exists as the root conjure orchestration boundary.
- Runtime behavior and interface structure must converge rather than diverge.

## Dependencies / External References
- `artifacts/2026-05-18_conduit_aether_refactor_plan.md`

## Milestones (Track Progress)
- [ ] Milestone 1: first bounded cut complete
  - remove `MutationResearch` from `Conduit`
  - move spellbook-owned Aether work behind `Spellbook`
- [ ] Milestone 2: conduit network bucket moved
  - frame-scoped conduit/cluster operations live behind `ConduitCloud`
- [ ] Milestone 3: gate/controller dependency narrowed
  - `Conduit` uses `CreationGateController` directly instead of `DevOpsManager`

## Stories (Required to Complete)
- [ ] Story: conduit-spellbook-first-cut - remove mutation research and move
      spellbook-owned Aether work behind Spellbook
- [ ] Story: conduitcloud-frame-network-surface - move frame-scoped
      conduit/cluster operations off Aether
- [ ] Story: conduit-gate-controller-narrowing - inject controller directly and
      remove broad DevOps dependency

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: keep the architecture artifact current as stage decisions change
- [ ] Task: keep ticket/board state aligned to the current stage
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- `Conduit` no longer depends directly on `Aether`.
- The stage plan is either completed or reduced into accepted successor lanes.
- Artifact and ticket state are sufficient to resume after compaction.

## Risks / Mitigations
- Risk: `ConduitCloud` could become a new god-object.
  - Mitigation: keep it strictly frame-scoped and conduit-network-specific.
- Risk: `Spellbook` could become a new service locator.
  - Mitigation: only move spellbook-owned upstream work into it.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Stage-local focused validation only after each bounded cut.
- Honest reporting: "Not run." unless executed.

## Rollout / Adoption Plan
- Use the artifact as the current source of truth for staged implementation.
- Reduce each accepted stage into the next bounded ticket slice instead of
  widening implementation in one pass.

## Open Questions
- Which residual root/frame lifecycle operations should stay on `Aether` after
  the conduit network bucket is moved?

## Decision Log
- 2026-05-18: create one durable artifact + epic before more implementation
  work because the lane is approaching compaction pressure.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-05-18_conduit_aether_refactor_plan.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: retain unless a later canonical system doc fully absorbs it

## Notes
- DATETIME: 2026-05-18T16:36:09Z
  TYPE: FACT
  CLAIM: The conduit/aether lane now has a durable planning anchor before
    further implementation. The artifact captures the current diagnosis,
    call-bucket classification, and staged plan for removing `Conduit -> Aether`.
  EVIDENCE:
  - artifacts/2026-05-18_conduit_aether_refactor_plan.md:1-93
  - tickets/tasks/2026-05-18_align_conduit_aether_dependency_to_spellbook_task.md:1-120
  IMPACT: Later passes can resume from file-backed architecture intent instead
    of reconstructing the plan from chat.
  NEXT: keep the first bounded task aligned to Stage 1 of the artifact plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T09:48:52Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this epic and its linked refactor-plan artifact for turn-in as retained historical architecture context rather than as an active execution lane.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-21
  IMPACT: The epic can move to `tickets/epics/completed/`, and the linked artifact can be cleared from `Active Artifact Links` while still being retained as a reference artifact.
  NEXT: move the epic to `tickets/epics/completed/`, clear the active artifact row, and record the retained-reference closure in `artifact_board.md`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic is the durable architecture/program anchor for the conduit/aether
ownership refactor. The linked artifact is the current source of truth for the
staged plan.
