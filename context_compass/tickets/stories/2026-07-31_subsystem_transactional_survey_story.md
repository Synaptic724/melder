# Story: Survey what MR / Nexus / Crystallizer actually need transactionalized

## Metadata
- Story ID: STORY-2026-07-31-subsystem-transactional-survey
- Epic ID: EPIC-2026-07-31-aetheric-mediator-subsystem
- Status: ready
- Owner: cowork
- Agent Name: UNASSIGNED (deliberately - see note)
- Priority: p1
- Created: 2026-07-31T23:00:41Z
- Updated: 2026-08-02T17:40:00Z

## Problem / Opportunity
We do not yet know WHAT to transactionalize in each subsystem, only that each
invented its own concurrency control. Before wiring, each subsystem needs a
survey answering: what structural mutations does it perform, what does it
currently protect them with, what scope keys would express that, and what are its
"basic conditions" emitted on enable.

## Ticket Contract
- ENTRY_GATE: core plane vocabulary exists (claim modes + scope key shape).
- EXECUTION_BOUNDARY: READ-ONLY survey. No code changes under this story.
- EXIT_GATE: three task surveys complete with source evidence.
- FAILURE_ESCALATION: RAISE if a subsystem's protection cannot be expressed as
  scope claims - that is a finding, not a failure.

## Tasks
- [ ] TASK-2026-07-31-survey-mr-transactional-surface
- [ ] TASK-2026-07-31-survey-nexus-transactional-surface
- [x] TASK-2026-07-31-survey-crystallizer-transactional-surface (bootstrap_0, 2026-08-02T17:40:00Z)

## Acceptance Criteria
- Each survey names the subsystem's structural mutation verbs with file:line.
- Each names its CURRENT protection mechanism and what that mechanism misses.
- Each proposes scope keys and modes.
- Each answers "what basic conditions does this subsystem emit when enabled".

## Notes
- DATETIME: 2026-07-31T23:00:41Z
  TYPE: DECISION
  CLAIM: Left UNASSIGNED on purpose. These surveys should be run by agents with
    FRESH context, not inherited from the long investigation session that
    produced the epic. Each task is written to be self-contained.
  EVIDENCE:
  - context_compass/tickets/epics/2026-07-31_aetheric_mediator_subsystem_epic.md
  IMPACT: Keeps survey quality independent of one contaminated session.
  NEXT: Any agent may claim one survey task.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Progress
- 2026-08-02T17:40:00Z (bootstrap_0): CRYSTALLIZER survey COMPLETE. Two CONFLICT
  findings recorded, one of them the epic's own central claim now VERIFIED from
  source rather than inherited: `_ensure_frame` (Aether lock, aether.py:893-941)
  and `bind_frame_configuration` (frame lock, aetheric_frame.py:626+) are two
  acquisitions on two different locks, called as two statements at
  restore_engine.py:1706-1708, and the LoadGate cannot close the window because
  it is consulted at exactly two sites - transaction_mediator.py:359 and :501,
  both NEW-ROOT mediator ingresses - and a frame under construction has no
  mediator. Second CONFLICT: all-or-nothing teardown is not compensation -
  `_teardown_built` swallows every per-unit cleanup error by contract, so a
  partial teardown leaves live objects with no record of which ones failed, and
  claim-release ordering is not equivalent to build-order teardown because
  claims and built units are not 1:1.
  Also found: `graft_index` mutates live books with NO load-authority span (its
  own docstring: "Unlike a world load it is NOT one transaction"), and
  `record_spell_crystal` is a read-then-act pair across two locks. Neither is
  inexpressible - both are simply unclaimed today.
  CORRECTED a Starting Fact: the ticket said "80-site shortfall ledger"; actual
  is 36 call sites / 18 distinct reason strings, all in restore_engine.py. The
  ticket told me to re-verify rather than trust, so this is the mechanism
  working.
- 2026-08-02T18:05:00Z (bootstrap_0): CORRECTION filed against my own crystallizer
  survey, Q4. I asserted that `ix` means "I will later escalate this to exclusive"
  and used that to justify proposing NO `ix` anywhere. Both `ClaimMode`
  definitions say otherwise and agree with each other: `ix` is the PARENT-SCOPE
  MARKER for hierarchical claims (embargo_manager.py `ClaimMode`;
  aetheric_mediator/claim_mode.py `ClaimMode`). Hold `ix` on the parent, `x` on
  the child, and disjoint children proceed in parallel. One row changes: the
  graft should claim `ix` on `spellbook:<id>` and `conduit:<id>` and keep `x` on
  the index it actually mutates - otherwise a graft into one index needlessly
  blocks a graft into a different index of the same book. `crystallizer:load:world`
  stays `x`. The two CONFLICT findings are unaffected. ANY AGENT TAKING THE MR OR
  NEXUS SURVEY SHOULD READ THAT CORRECTION FIRST so the same wrong premise does
  not get re-derived twice more.
  Two surveys remain OPEN and UNASSIGNED: MR and Nexus. I did not claim them -
  the story's own DECISION note says these should run on FRESH context and I now
  carry the crystallizer read, so a different agent taking one of the remaining
  two is better for the story than me taking all three.

## Context / Handoff Summary
Three read-only surveys. Self-contained by design so a fresh agent can take one
without reading the whole investigation history.
