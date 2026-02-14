# Epic: Snapshot and Ownership Copy Audit (Phase + Meld)

## Metadata
- Epic ID: EPIC-2026-02-14-snapshot-ownership-cleanup-audit
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14
- Target Window: 2026-Q1
- Related Program/Initiative: Phase Testing Follow-Up and Meld Runtime Hygiene

## Problem / Opportunity
Phase and meld paths include multiple snapshot and copy operations that can add
avoidable O(n) overhead on warm paths if the copied structures are already
deterministically invalidated or ownership is clear. We need a focused audit to
separate required isolation copies from unnecessary duplication.

## MRP Alignment (Most Reasonable Product)
The MRP outcome is a clear ownership and mutation policy for snapshot/copy
sites in phase/meld hot paths, backed by evidence and safe follow-up tasks.
This avoids speculative optimization and preserves contract correctness.

## Goals (Outcomes)
- Build an evidence-backed inventory of snapshot/copy sites in phase + meld paths.
- Classify each site as required, optional, or UNKNOWN with explicit rationale.
- Convert validated opportunities into small, ranked follow-up tasks.
- Keep lifecycle/cleanup ownership rules explicit for any copy-removal proposals.

## Non-Goals (Explicit Exclusions)
- Large refactors across unrelated subsystems.
- Public API changes for spellbook/meld override contracts.
- Blindly removing copies without contract proof.

## Scope Boundaries
- In scope:
- Discovery and classification of snapshot/copy behavior in phase and meld flows.
- Ticket/documentation updates with evidence ranges and ranked recommendations.
- Out of scope:
- Broad performance rewrites across the repository.
- Mechanical sweeps unrelated to snapshot/ownership semantics.

## Success Metrics
- Discovery story/task produce a concrete inventory with evidence ranges.
- Each high-value copy site has an explicit keep/remove/defer decision.
- At least one follow-up optimization task is created (or explicit defer rationale recorded).

## Requirements (Functional + Non-Functional)
- Use strict Ticket Microcycle during discovery.
- Document every meaningful finding immediately in ticket `## Notes`.
- Use begin/end evidence ranges in every new note entry.
- Keep UNKNOWN-first discipline for any unverified contract assumptions.

## Constraints / Assumptions
- Constraints:
- Preserve dirty/revalidation semantics while evaluating copy-removal ideas.
- Preserve current thread-safety and isolation guarantees unless revalidated.
- Assumptions:
- Current warm-path profiling work remains the active lane; this epic can start
  as deferred-ready and execute after current simple passes.

## Dependencies / External References
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/aether/conduit/meld/overrides/graph_mutator.py`
- `src/melder/spellbook/spellbook.py`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `context_compass/epics/2026-02-14_phase_testing_epic.md`

## Milestones (Track Progress)
- [ ] Milestone 1: Discovery inventory completed for phase + meld snapshot/copy sites.
- [ ] Milestone 2: Keep/remove/defer decision matrix completed with risks.
- [ ] Milestone 3: Ranked follow-up implementation tasks created (if approved).

## Stories (Required to Complete)
- [ ] Story: STORY-2026-02-14-snapshot-ownership-cleanup-audit - Discover and classify snapshot/copy ownership sites across phase and meld paths.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-02-14-snapshot-ownership-cleanup-audit.
- [ ] Task: Verify Ticket Microcycle enforcement across active stories/tasks.

## Acceptance Criteria (Epic Done)
- Discovery artifacts identify meaningful snapshot/copy sites with evidence.
- Each candidate has explicit decision state: keep, remove, or defer.
- Approved follow-up tasks are scoped with rollback/testing expectations.

## Risks / Mitigations
- Risk: removing a copy could leak mutable shared state across calls.
  Mitigation: require ownership/lifecycle proof and targeted regression tests
  before implementation tasks.
- Risk: discovery scope balloons across unrelated systems.
  Mitigation: keep scope to phase + meld lanes and request confirmation before
  expanding beyond defined file set.

## Validation / Test Approach
- Discovery phase: documentation and evidence validation only.
- Implementation follow-ups (if created): targeted pytest suites and harness reruns.

## Rollout / Adoption Plan
- Run discovery task first and attach evidence-backed recommendations.
- Review keep/remove/defer decisions with user.
- Execute approved follow-up tasks in ranked order.

## Open Questions
- Which snapshot/copy sites are mandatory for concurrency safety vs historical carry-over?
- Where does deterministic invalidation make immediate-copy defensiveness unnecessary?

## Decision Log
- 2026-02-14: Created a dedicated deferred-ready epic for snapshot/ownership
  cleanup review so this lane is tracked separately from current simple-pass
  optimization execution.

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Phase and meld paths include explicit snapshot/copy behavior that is a valid discovery target for ownership/perf classification (spellbook state snapshot copies, meld override normalization copies, phase11 plan variant structure copies, and graph mutator socket-ref copying).
  EVIDENCE: src/melder/spellbook/spellbook.py:951-1008, src/melder/aether/conduit/meld/meld.py:807-913, src/melder/spellbook/spell_crafter/spell_crafter.py:3857-3866, src/melder/aether/conduit/meld/overrides/graph_mutator.py:139-141
  IMPACT: The epic can start from concrete source anchors instead of speculative assumptions.
  NEXT: Execute `TASK-2026-02-14-discovery-snapshot-ownership-cleanup-audit`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Epic is created as deferred-ready scope for the snapshot/ownership cleanup lane.
Discovery is not started yet. Next action is to run the linked discovery task
after current simple-pass execution priorities are complete.
