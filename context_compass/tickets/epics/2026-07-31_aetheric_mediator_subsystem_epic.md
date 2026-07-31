# Epic: AethericMediator - a standalone top-level thread/transaction plane

## Metadata
- Epic ID: EPIC-2026-07-31-aetheric-mediator-subsystem
- Status: in_progress (bootstrap started 2026-07-31 under owner directive)
- Owner: cowork
- Agent Name: helper_f
- Priority: p1
- Created: 2026-07-31T23:00:41Z
- Updated: 2026-07-31T23:00:41Z
- Target Window: UNKNOWN
- Related Program/Initiative: EPIC-2026-07-27-transactional-structure-unwind
  (the investigation that produced this direction)

## Problem / Opportunity

THREE SUBSYSTEMS INDEPENDENTLY SOLVED THE SAME PROBLEM THREE DIFFERENT WAYS.
That is the defect. Not any individual race.

- Crystallizer: `LoadGate` (global exclusive) + engine-local `_build_lock` +
  posture idempotence.
- Nexus: `RiftGate` + `RiftGateController` + drain-and-refresh choreography +
  config-backed timeouts.
- MutationResearch: a declared one-way lock order + a dedicated `_emission_lock`
  + hand-written compensation (`_rollback_claim`, join restore).

Each is a local answer to "coordinate structural mutation across threads",
invented separately because there was no shared plane to reach for. The bug
trail confirms the cost: BUG-031 (emission lock), BUG-048 (lane governance), the
2026-07-12 CreationGate drain-race ticket-first fix - all found and patched once
per subsystem, in that subsystem's own vocabulary.

Two structural facts make this compound rather than stabilise:
1. `Aether._ensure_frame(...)` + `bind_frame_configuration(...)` CANNOT be made
   atomic by anything that exists today, because the only admission authority
   (the mediator) is owned by the frame being created. Not patchable - it needs
   an authority ABOVE.
2. Free-threaded 3.14t removed the accidental serialisation the GIL used to
   provide, so every hand-rolled protection is load-bearing now in a way it was
   not when these were written.

WHAT THIS BUYS: coherence, not correctness. Nothing is on fire today. This is
consolidation so the fourth subsystem does not invent a fourth answer, and so
concurrency bugs stop being discovered once per subsystem.

## MRP Alignment

MRP, not MVP. A half-built admission plane is worse than none: callers trust it
and it silently fails to isolate. The bar is that the claim vocabulary and the
acquisition semantics are right the first time, because all three subsystems will
be written against them.

## Ticket Contract
- ENTRY_GATE: owner directive given 2026-07-31; core bootstrap authorised.
- EXECUTION_BOUNDARY: build the STANDALONE plane only. Wiring into MR/Nexus/
  Crystallizer is a separate story and is gated on the per-subsystem surveys.
- DEPENDENCIES: `melder.utilities` only (Cleanable, synchronization primitives).
  Explicitly NOT `melder.aether`.
- EXIT_GATE: core plane exists and is tested standalone; all three subsystem
  surveys complete; owner rules on wiring order.
- FAILURE_ESCALATION: DECISION_REQUEST on open question 1 and 2 below.

## Owner Constraints (non-negotiable, from the 2026-07-31 directive)
1. Lives at `src/melder/aether/aetheric_mediator/`.
2. Named `aetheric_mediator`.
3. Aether MANAGES it (holds it), and it is constructed IMMEDIATELY, first, right
   after Aether itself is built.
4. IT MUST NOT DEPEND ON AETHER. One-way only: Aether knows about the plane, the
   plane knows nothing about Aether. This is what lets it exist before any frame
   can, and what keeps it testable in isolation.
5. Model it on the WORKING DevOps subsystem - the whole shape, not one component.
   It may omit components, but it is not "just the embargo manager".
6. Wire into MR / Nexus / Crystallizer only when those subsystems are ENABLED AND
   ACTIVE; they emit their basic conditions to the plane.
7. Lightweight, but just as effective.

## Component Split (modelled on DevOps, trimmed)

CORE - all three subsystems need it:
- identity of a claimant (per-identity sessions are what make joins work)
- request carrying a transaction type + `scope_claims`
- claim table with MODES (`x` exclusive / `s` shared / `ix` intent) and atomic
  all-or-nothing acquisition with `(scope_key, holder, mode)` blocking evidence
- orchestrated admission - one acquisition under one admission lock
- mediator front door - ingress, per-identity root sessions, same-thread joins,
  bounded wait-and-retry, commit/abort finalisation
- session - the live span: status, depth, join/leave, rollback actions, abort
  pipeline, failure reason, and the OUTCOME POLICY
- strategy seam - the ABC + registry, as an EXTENSION POINT

DELIBERATELY OMITTED (DevOps-specific, no consumer up here):
- the 15 DevOps strategy families (each subsystem registers its own)
- `apply_commit_delta` / `DevopsFactRecord` baselines
- commit validators / commit hooks, until a caller needs one
- `StagedMutation`, unless staging proves necessary

## Key Design Decisions (recorded, open to challenge)

- ONE SHARED PLANE, not one per subsystem. The crystallizer's job is driving the
  other two (`_replay_mutation_research`, `_replay_nexus`), so per-subsystem
  planes would force acquisition ACROSS planes and manufacture an AB-BA hazard.
  One table means one atomic acquisition over every scope a load needs.
- SCOPE KEYS ARE NAMESPACED AND FLAT: `mr:set:<name>`, `nexus:frame:<name>`,
  `cryst:load:<id>`, `frame:<name>`.
- `LoadGate` IS NOT DELETED, IT IS RE-EXPRESSED as one exclusive claim on a
  world scope key. Today's global-exclusive behaviour is preserved exactly for
  loads that need the whole world; frame-scoped loads claim only their frames and
  gain disjoint parallelism. Backwards compatible by construction.
- THE FRAME-LEVEL DEVOPS MEDIATOR STAYS WHERE IT IS. This is a PEER plane at a
  higher scope, not a replacement. Frame -> its mediator ordering is retained.

## Non-Goals (Explicit Exclusions)
- Replacing or modifying the DevOps frame-level plane.
- Unifying inner frame transactions into the top session (see open question 2).
- Transactionalising Aether itself. Aether hosts the plane; it is not a
  participant.

## Open Questions (BLOCKING - resolve before wiring)
1. Does the top plane claim FRAME scope keys, or only subsystem keys? Claiming
   frames overlaps the frame plane's own scopes and needs a declared order.
   Claiming only subsystem keys leaves frame creation unprotected - which was the
   original hole this started from.
2. Do inner frame transactions JOIN the top session, or stay siblings? Sibling =
   the plane ORGANISES threads. Join = it UNIFIES transactions, which is a much
   larger build and the owner has leaned against it.
3. What are each subsystem's "basic conditions" that get emitted on enable? The
   three surveys answer this.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-07-31-aetheric-mediator-core - build the standalone plane
- [ ] Story: STORY-2026-07-31-subsystem-transactional-survey - what to
      transactionalize in MR / Nexus / Crystallizer
- [ ] Story: STORY-2026-07-31-aetheric-mediator-wiring - activation-gated wiring
      (BLOCKED on the survey + open questions 1 and 2)

## Acceptance Criteria (Epic Done)
- The plane exists standalone with ZERO imports from `melder.aether`, provable by
  a grep in its own test.
- Modes and the compatibility matrix are tested directly.
- Acquisition is proven atomic all-or-nothing under concurrency.
- All three surveys are complete with source evidence.
- Open questions 1 and 2 have recorded owner decisions.
- Wiring has NOT happened without those decisions.

## Risks / Mitigations
- RISK: two admission planes deadlock against each other (AB-BA). MITIGATION:
  declare the one-way order BEFORE building - AETHER PLANE CLAIMS -> FRAME PLANE
  CLAIMS, never the reverse. MR's threadsafety story is a declared order, not a
  discovered one; match that discipline.
- RISK: the plane accretes DevOps depth by default and stops being lightweight.
  MITIGATION: the omitted list above is a contract; adding to it needs a reason
  recorded in the decision log.
- RISK: blast radius across three working subsystems. MITIGATION: the plane ships
  and is tested STANDALONE first; wiring is a separate, gated story.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No import of `melder.aether` from inside the plane.
- [ ] No wiring before the surveys and open questions 1-2 are resolved.

## Validation / Test Approach
Not run. Standalone unit tests belong to the core story; the no-Aether-import
rule should be a test, not a convention.

## Decision Log
- 2026-07-31: Owner directed bootstrap. Name, location, Aether-hosted-but-
  independent, model-on-DevOps, activation-gated wiring, lightweight-but-
  effective. Recorded verbatim in Owner Constraints above.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- DISPOSITION: retain_as_reference

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- IF_UNKNOWN: ask user before implementation

## Notes
- DATETIME: 2026-07-31T23:00:41Z
  TYPE: DECISION
  CLAIM: Epic opened under owner directive. The plane is a CONSOLIDATION play -
    it buys one vocabulary for scope claiming across three subsystems that
    currently have three. It is explicitly NOT sold as fixing a live defect.
  EVIDENCE:
  - context_compass/tickets/epics/2026-07-27_transactional_structure_unwind_epic.md
  IMPACT: Sets the success bar at coherence, so the epic is not judged against an
    outage that does not exist.
  NEXT: Bootstrap the core claim vocabulary; open the three survey tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-31T23:00:41Z
  TYPE: RISK
  CLAIM: The agent filing this epic (helper_f) has a heavily loaded context from
    a long investigation session. The surveys are therefore deliberately written
    as SELF-CONTAINED tasks a FRESH agent can execute without inheriting that
    context.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-07-31_survey_mr_transactional_surface_task.md
  IMPACT: Prevents this epic's quality from depending on one contaminated
    session.
  NEXT: Keep every survey task's Required Reads explicit and short.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary

Owner-directed. Build a standalone top-level thread/transaction plane at
`src/melder/aether/aetheric_mediator/`, hosted by Aether but with ZERO dependency
on it, modelled on the working DevOps change-control subsystem minus its
frame-specific depth.

The single most important constraint: THE PLANE MUST NOT IMPORT `melder.aether`.
That is what lets it be constructed before any frame exists and tested in
isolation. Make it a test, not a convention.

Do not wire it into MR / Nexus / Crystallizer until the three surveys are done and
open questions 1 and 2 have owner decisions. The plane ships standalone first.
