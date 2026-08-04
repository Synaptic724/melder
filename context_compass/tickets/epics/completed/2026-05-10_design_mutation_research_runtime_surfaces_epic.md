# Epic: Design Mutation Research Runtime Surfaces

- Completed: 2026-07-11T19:30:00Z
- Summary: Closed done on owner directive. Its core prediction EXECUTED: the
  first implementation move it mandated (lift MutationResearch out of
  frame-local ownership up to Aether) landed and stands - MR is the
  Aether-hosted singleton root today. Its own FAILURE_ESCALATION clause
  anticipated the rest: the runtime proved MutationConduit and MutationFrame
  should NOT exist (owner ruling 2026-07-06: conduits and frames carry no
  mutation dimension; the conduit door was later deleted outright). The
  runtime surface became the Rift rooms (13 codegen commands / 6 capability
  reads / ViewSpell annotation) + the silent bind/notch seams; transaction
  layering resolved through the change-control plane + MR's own one-way lock
  order. May-era placeholder scaffolds were deleted in the owner-approved
  ResearchSet rebuild. Canonical record:
  artifacts/2026-07-11_mutation_research_philosophy_v3.md.

## Metadata
- Epic ID: EPIC-2026-05-10-design-mutation-research-runtime-surfaces
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-10T22:28:55Z
- Updated: 2026-05-10T22:28:55Z
- Target Window: 2026-Q2
- Related Program/Initiative: MutationResearch runtime ownership, transaction, and facade architecture

## Problem / Opportunity
The current mutation surface is too low and too fragmented.

Right now:
- `MutationResearch` is owned by `AethericFrame`
- spell-level mutation helpers live directly on `Spell`
- conduit-level dynamic gating and change-control transactions already exist
- spell-index creation gates already exist
- `MutationContract` is still blocked in Phase 4

At the same time, the recent design work made several things clearer:
- `MutationResearch` should likely move up toward `Aether`
- declaration-surface mutation and spell-level structural mutation should not
  be ordinary spell helper calls
- conduit-scoped mutation orchestration needs a dedicated surface instead of
  bloating `Conduit`
- broader frame-level mutation work may need a separate runtime surface too,
  even if that later proves to be unnecessary or narrower than first assumed

This epic exists to hold that broader runtime-surface design before we try to
implement it piecemeal.

## MRP Alignment (Most Reasonable Product)
The MRP is not "build every mutation facade now."

The MRP is:
- define the runtime ownership split cleanly
- define the future `MutationConduit` surface
- define the tentative `MutationFrame` surface
- define where spell/index/conduit/frame transactions belong
- explicitly stage the first implementation order:
  1. move MutationResearch out of frame-local ownership and up toward `Aether`
  2. only then build the higher mutation runtime surfaces

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a dedicated epic for the broader
  MutationConduit / MutationFrame / transaction-surface design instead of
  burying it in the smaller MutationContract runtime task.
- EXECUTION_BOUNDARY: architecture/design only for MutationResearch runtime
  surfaces, ownership, and transaction layering.
- DEPENDENCIES:
  - `artifacts/2026-05-09_mutation_research_philosophy.md`
  - the active MutationContract investigation lane
  - current conduit/change-control/creation-gate seams
- EXIT_GATE: the runtime-surface direction is durable enough that future
  implementation tasks can be opened in the right order without rediscovering
  the model from chat.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the current runtime proves
  that one of the proposed surfaces (especially `MutationFrame`) should not
  exist at all.

## Goals (Outcomes)
- Define why public spell mutation interactions should move above `Spell`.
- Define `MutationConduit` as the conduit-scoped mutation orchestration
  surface.
- Define `MutationFrame` as the frame-scoped mutation transaction surface,
  while preserving the possibility that it may later be reduced or rejected.
- Define the transaction layering:
  - spell / spell-index
  - conduit
  - frame
- Make the implementation order explicit.

## Non-Goals (Explicit Exclusions)
- Implement `MutationConduit` now.
- Implement `MutationFrame` now.
- Remove `MUTATION_CONTRACT_DISABLED` now.
- Finalize all future frame-level mutation operations.

## Scope Boundaries
- In scope:
  - ownership placement
  - facade/orchestrator object definitions
  - transaction layering
  - gating / embargo direction
  - implementation order
- Out of scope:
  - code patches for the full runtime surface
  - final API naming for every method
  - full module-version promotion choreography

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a dedicated epic capturing
  the broader MutationResearch runtime-surface design and future object model.

## Success Metrics
- The mutation runtime surface hierarchy is explicit.
- MutationResearch movement order is explicit.
- `MutationConduit` and `MutationFrame` have a durable written rationale.
- Future implementation tasks can route through this epic cleanly.

## Requirements (Functional + Non-Functional)
- Functional:
  - define the runtime role of `MutationConduit`
  - define the tentative role of `MutationFrame`
  - define the relationship between those facades and:
    - `MutationResearch`
    - `ChangeControlManager`
    - `SpellSystemStates`
    - spell-index creation gates
- Non-functional:
  - no architecture drift back into spell-only mutation helpers
  - no premature implementation pressure
  - explicit uncertainty where frame-level ops remain unknown

## Constraints / Assumptions
- `MutationConduit` should reference, not own, the underlying `Conduit` and
  mutation/runtime support systems.
- `MutationFrame` may end up narrower than first imagined, or even unnecessary.
- The first real implementation move should be lifting MutationResearch out of
  frame-local ownership and up toward `Aether`.

## Dependencies / External References
- `codex/context_compass/artifacts/2026-05-09_mutation_research_philosophy.md`
- `codex/context_compass/tickets/tasks/2026-05-10_investigate_mutation_contract_runtime_socket_feature_task.md`
- `src/melder/aether/conduit/conduit.py`
- `src/melder/spellbook/spell.py`
- `src/melder/utilities/synchronization/creation_gate_controller.py`
- `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`

## Milestones (Track Progress)
- [ ] Milestone 1: define runtime ownership and facade hierarchy
- [ ] Milestone 2: define transaction layering and gate/embargo boundaries
- [ ] Milestone 3: define implementation order and future task cuts

## Stories (Required to Complete)
- [ ] Story: define the Aether-level MutationResearch ownership move
- [ ] Story: define MutationConduit responsibilities and facade boundaries
- [ ] Story: define MutationFrame responsibilities and go/no-go boundary
- [ ] Story: define spell/index/conduit/frame mutation transaction layering

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: update the MutationResearch philosophy artifact with this runtime-surface direction
- [ ] Task: reduce the Aether-level MutationResearch move into implementation-ready work later
- [ ] Task: stage future MutationConduit implementation tasks after the ownership move is accepted
- [ ] Task: verify Ticket Microcycle enforcement across future mutation-runtime stories/tasks

## Acceptance Criteria (Epic Done)
- The broader runtime-surface direction is durable and explicit.
- MutationConduit and MutationFrame are described clearly enough to guide later work.
- The implementation order is explicit: move MutationResearch up first, build
  the facades later.

## Risks / Mitigations
- Risk: we over-commit to `MutationFrame` before knowing whether frame-level ops
  really need a dedicated surface.
  Mitigation: keep `MutationFrame` explicitly tentative and subject to a later
  go/no-go decision.
- Risk: the design gets prematurely stuffed into `Conduit`.
  Mitigation: keep the facade/orchestrator boundary explicit in the epic.

## Applicable Anti-Patterns
- [ ] No epic-state transition without evidence-backed scope.
- [ ] No premature implementation of broad mutation runtime surfaces.
- [ ] No assuming `MutationFrame` is mandatory before runtime evidence says so.

## Validation / Test Approach
- Design-only in this epic.
- Validation is clarity, internal consistency, and readiness for later
  implementation slicing.

## Rollout / Adoption Plan
- First: update the MutationResearch philosophy artifact with this runtime
  surface direction.
- Second: reduce the Aether-level MutationResearch move into implementation work.
- Third: implement `MutationConduit` only after that ownership move lands.
- Fourth: revisit whether `MutationFrame` is truly needed.

## Open Questions
- What exact frame-level mutation operations would justify `MutationFrame`?
- Should spell-index mutation transactions be surfaced through
  `MutationConduit` only, or also exposed through a narrower spell/index proxy?
- How much of the current spell-side mutation helper surface should become
  private before facade work begins?

## Decision Log
- 2026-05-10T22:28:55Z: Opened after the user requested a dedicated epic for
  the broader MutationResearch runtime-surface model, separate from the smaller
  MutationContract runtime task.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-05-10T22:28:55Z
  TYPE: FACT
  CLAIM: The broader mutation-runtime design now needs its own lane. The user
    explicitly wants the ideas around `MutationConduit`, `MutationFrame`,
    spell/index-scoped transactions, and moving MutationResearch up to `Aether`
    to be mapped before implementation starts, because the current smaller
    socket work is no longer the right container for that larger direction.
  EVIDENCE:
  - user_instruction: "make an epic to describe all the changes we need to make for the MutationContract to work and define all these objects MutationConduit and MutationFrame"
  - user_instruction: "we won't be building these things right away we'll actually be managing mutation research first and moving it out of the frame context and up to the aether first"
  IMPACT: Future mutation-runtime implementation now has a dedicated epic
    boundary instead of being overloaded into the smaller runtime-socket lane.
  NEXT: create the companion artifact-update task and route the board to that
    narrower documentation slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: runtime-surface hierarchy, transaction layering, and
  implementation ordering.
- Add notes when the facade boundaries or frame-level go/no-go posture change.
- Keep notes append-only and preserve UNKNOWN-first discipline.

## Salvage Review (owner-directed read-before-archive, 2026-07-11)
Read in full by mutation_0 (epic + all four child tasks + both referenced
artifacts) before final archive. Extracted and recorded in
artifacts/2026-07-11_mutation_research_philosophy_v3.md Open Directions:
lane TYPE classification (from the branch_type_enforcement artifact),
surgical synthesis (the unbuilt half of the May surgical-mutation flow), and
runtime recomposition (the May end-state verb). Both source artifacts stamped
superseded with pointers; artifact board synced. Everything else in this
family is either built (Aether move, config/builder, structural diff, module
SHA identity, multi-agent campaigns), ruled out (MutationConduit/
MutationFrame, interface layer), or already tracked (blast-radius promotion
policy in V3; SpellState producers in the C-docs).

## Context / Handoff Summary
This epic holds the broader MutationResearch runtime-surface design:
MutationResearch ownership above the frame, a future MutationConduit facade, a
tentative MutationFrame facade, and the transaction hierarchy those surfaces
would orchestrate.
