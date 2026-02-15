Completed: 2026-02-07
Summary: Closed per reprioritization directive; superseded by full AOT codegen epic and ticket set.

# Epic: Refactor Phase 5-7 to Target-First Revalidation

## Metadata
- Epic ID: EPIC-2026-02-07-phase-5-7-spell-isolated-revalidation
- Status: in_progress
- Owner: Mark + Codex
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-07
- Target Window: 2026-Q1
- Related Program/Initiative: Meld runtime correctness + performance

## Problem / Opportunity
Meld revalidation is entered from a single target spell, but current resolution phases execute with broad spellbook scope. This increases contention, creates avoidable rebuild work, and contributes to concurrency races in phase artifacts. We need a two-lane model: target-first revalidation by default, and a meld-locked full revalidation lane for specific change categories.

Evidence:
- `Meld._ensure_resolution_resolvable` can trigger conduit resolution phases from a single spell path: `src/melder/aether/conduit/meld/meld.py:550`.
- `_run_resolution_phases_for_conduit` runs grouped phases that include all-spell compile factories: `src/melder/spellbook/spellbook.py:3516`, `src/melder/spellbook/spellbook.py:3596`.
- Phase 8 currently cleans old occurrence plan during replace, which can race with concurrent readers: `src/melder/spellbook/spell_crafter/spell_crafter.py:1855`.

## MRP Alignment (Most Reasonable Product)
The durable core is a revalidation model where meld-time repair is targeted to the requested spell closure, while preserving correctness signals in `SpellSystemStates`, and where specific structural events escalate to a full revalidation lane. This keeps behavior coherent, reduces unnecessary work, and improves runtime stability under concurrent meld.

## Goals (Outcomes)
- Make Phase 5-7 execution on meld revalidation operate on target spell closure by default.
- Define explicit escalation triggers that run full revalidation with a meld validation lock.
- Preserve existing transaction/change-control invalidation semantics.
- Remove known phase artifact race conditions tied to broad concurrent recompiles.
- Keep throughput high without introducing a spellbook-global lock.

## Non-Goals (Explicit Exclusions)
- No public API redesign for `Spellbook`, `Conduit`, or `Meld`.
- No full replacement of `SpellSystemStates` or `RiskManager`.
- No blanket "pause all meld" gate.
- No unrelated refactors.

## Scope Boundaries
- In scope:
- Re-scope meld-triggered Phase 5-7 behavior to target spell closure by default.
- Define and implement a full-revalidation escalation lane for specific change categories.
- Add a meld validation lock path for escalated full revalidation.
- Ensure lock strategy remains spell-scoped or validation-scoped, not spellbook-global.
- Update/add tests proving target-only revalidation behavior and race stability.
- Out of scope:
- Redesign of all phase pipelines beyond 5-7 behavior required for this epic.
- Full architecture rewrite of change-control or contract systems.

## Success Metrics
- Concurrency failures containing `OccurrencePlan has already been cleaned` are eliminated in targeted integration coverage.
- Non-escalated meld revalidation for one dirty spell does not rebuild unrelated spells in test instrumentation.
- Escalated full revalidation runs once per event window under validation lock semantics (no duplicate concurrent full runs for the same scope).
- No regression in existing spellbook/conduit integration tests for binding, scan, and contract paths.

## Requirements (Functional + Non-Functional)
- Functional:
- Revalidation triggered from `meld(spell=...)` must prioritize target spell closure over frame-wide rebuild.
- Full revalidation must be available and invoked only for explicit escalation triggers.
- Full revalidation must execute under a meld validation lock path.
- Phase 6 validity writes in `SpellSystemStates` must remain correct for affected target closure.
- Functional behavior for transactions and dirty/gated states must remain intact.
- Non-functional:
- Avoid spellbook-global serialization.
- Keep lock scope minimal and local to affected spell/closure artifacts.
- Preserve deterministic cleanup/lifecycle behavior.

## Constraints / Assumptions
- Existing transaction model remains the source of invalidation triggers.
- Existing `SpellSystemStates` and `RiskManager` remain active control-plane components.
- UNKNOWN: Final closure boundary source for every phase (topology-only vs blueprint+index blend) needs implementation-level confirmation.
- UNKNOWN: Final escalation trigger matrix (exact set of changes that require full revalidation) needs implementation-level confirmation.

## Dependencies / External References
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/spellbook/spellbook.py`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/system/spell_system_validation_system.py`
- `tests/integration/melder/conduit/test_conduit_integration_concurrency.py`

## Milestones (Track Progress)
- [ ] Milestone 1: Define target-first Phase 5-7 contract and escalation trigger matrix.
- [ ] Milestone 2: Implement target-closure revalidation path and preserve state/transaction contracts.
- [ ] Milestone 3: Implement meld-locked full revalidation path for escalated events.
- [ ] Milestone 4: Eliminate phase artifact race in concurrent revalidation scenarios.
- [ ] Milestone 5: Validate with integration + regression suite and document behavior updates.

## Stories (Required to Complete)
- [x] Story: STORY-2026-02-07-phase-5-local-closure - Scope Phase 5 to target closure.
- [x] Story: STORY-2026-02-07-phase-6-local-validation - Scope Phase 6 validation to target closure effects.
- [x] Story: STORY-2026-02-07-phase-7-target-change-control - Make Phase 7 meld path target-focused.
- [ ] Story: STORY-2026-02-07-escalation-trigger-matrix - Define and wire escalation conditions to full revalidation.
- [ ] Story: STORY-2026-02-07-meld-locked-full-revalidation - Add meld validation lock path for escalated full revalidation.
- [ ] Story: STORY-2026-02-07-concurrency-race-hardening - Fix concurrent artifact publish/cleanup race.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-02-07-phase-5-local-closure
- [x] Task: Complete story STORY-2026-02-07-phase-6-local-validation
- [x] Task: Complete story STORY-2026-02-07-phase-7-target-change-control
- [ ] Task: Complete story STORY-2026-02-07-escalation-trigger-matrix
- [ ] Task: Complete story STORY-2026-02-07-meld-locked-full-revalidation
- [ ] Task: Complete story STORY-2026-02-07-concurrency-race-hardening
- [ ] Task: Update `architecture/src_architecture.md` and `components/src_components.md` for new phase ownership boundaries.

## Acceptance Criteria (Epic Done)
- Non-escalated meld-triggered revalidation executes Phase 5-7 for target closure only, not unrelated spells.
- Escalated changes invoke full revalidation via meld validation lock path.
- Concurrency race around Phase 8/9 artifact lifecycle is resolved in relevant integration coverage.
- Existing transaction invalidation behavior remains functionally correct.
- All changed behavior is documented in architecture/components docs.

## Risks / Mitigations
- Risk: Hidden global invariant dependency may be accidentally skipped.
- Mitigation: Add explicit escalation checks and tests for known cross-closure constraints.
- Risk: Escalation trigger matrix is too broad and degrades throughput.
- Mitigation: Add instrumentation and tighten trigger classes to only required events.
- Risk: Escalation trigger matrix is too narrow and misses required full revalidation.
- Mitigation: Add transaction-driven regression cases for link/contract/ownership paths and verify correctness.
- Risk: Lock placement introduces throughput regressions.
- Mitigation: Keep lock scope spell-local and verify with benchmark/concurrency tests.
- Risk: Behavior drift across contracted spell flows.
- Mitigation: Include contract-focused integration cases in validation matrix.

## Validation / Test Approach
- Run targeted integration coverage:
- `tests/integration/melder/conduit/test_conduit_integration_concurrency.py`
- `tests/integration/melder/conduit/test_conduit_integration_spell_contract_variants.py`
- Run spellbook/conduit regression slices tied to recent failures.
- Add focused tests proving unrelated spells are not rebuilt during non-escalated target spell revalidation.
- Add focused tests proving escalated events route through full revalidation lock path.
- Report exact commands and outcomes; if skipped, report `Not run`.

## Rollout / Adoption Plan
- Land implementation in small story increments.
- Keep behavior behind internal flow boundaries first; avoid API churn.
- Update docs after each story to keep handoff context accurate.

## Open Questions
- UNKNOWN: Exact minimum data model needed for Phase 6 local-validation parity with current global strategy checks.
- UNKNOWN: Exact final list of escalation triggers for full revalidation.
- UNKNOWN: Final instrumentation point for "unrelated spell rebuild did not occur" assertions.

## Decision Log
- 2026-02-07: Adopt spell-isolated revalidation direction for Phase 5-7 in meld path; avoid spellbook-global lock strategy.
- 2026-02-07: Adopt two-lane model: target-first revalidation by default, escalated full revalidation under meld validation lock for specific changes.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
This epic captures the agreed direction to make meld-triggered revalidation target-focused (spell closure) for Phase 5-7, with an explicit escalated full-revalidation lane under meld validation lock for specific change classes. Current code evidence shows single-spell meld entry can trigger broad conduit phase runs and contributes to phase artifact race conditions. Next step is to split this epic into stories/tasks and implement incrementally with regression coverage and trigger-matrix validation.

Update 2026-02-07:
- Phase 5/6/7 stories are complete and archived.
- Remaining scope is escalation trigger matrix, meld-locked full revalidation lane, and concurrency race hardening.

