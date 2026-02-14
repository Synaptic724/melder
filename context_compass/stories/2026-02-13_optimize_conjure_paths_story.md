# Story: Optimize Conjure Paths

## Metadata
- Story ID: STORY-2026-02-13-optimize-conjure-paths
- Epic: EPIC-2026-02-13-optimize-melder
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-02-13
- Updated: 2026-02-14

## User Narrative
As a Melder maintainer, I want conjure path hotspots mapped and prioritized, so
that we can reduce conjure overhead without destabilizing runtime behavior.

## Value / MRP Alignment
Conjure cost directly affects startup and rebinding workflows. Discovery-first
analysis protects correctness while giving us targeted optimization steps.

## Requirements (Functional)
- Identify main conjure-path cost centers across phases and orchestration.
- Produce a ranked list of optimization opportunities with evidence anchors.
- Capture candidate follow-up tasks for implementation.

## Requirements (Non-Functional)
- Discovery pass must not change runtime behavior.
- Findings must be reproducible from code/test/benchmark evidence.

## Scope Boundaries
- In scope:
- `Spellbook.conjure` orchestration and associated phase scheduling path.
- Conjure-related data/setup flow in spellbook creation system.
- Out of scope:
- Meld runtime optimization.
- Phase 12 generated executor internals.

## Dependencies / Related Work
- `src/melder/spellbook/spellbook.py`
- `src/melder/spellbook/spellbook_creation_system.py`
- `src/melder/utilities/synchronization/phase_scheduler.py`
- `EPIC-2026-02-13-optimize-melder`

## Discovery Findings (How Conjure Works)
### 1) Conjure front door
- `Spellbook.conjure(...)` is the lock-guarded entrypoint that blocks repeat
  conjure on the same spellbook, instantiates `SpellbookCreationSystem`, then
  delegates and always cleans it up.
- Evidence: `src/melder/spellbook/spellbook.py:2922`, `src/melder/spellbook/spellbook.py:2985`, `src/melder/spellbook/spellbook.py:3006`, `src/melder/spellbook/spellbook.py:3016`, `src/melder/spellbook/spellbook.py:3018`.

### 2) Orchestration sequence
- `SpellbookCreationSystem.conjure()` executes:
  - prepare spellbook (freeze/bind/config + structural phases 1-4),
  - prepare resolution (generate conduit id + run conduit resolution phases 5-11),
  - resolve policy + spell duplicate guard,
  - pre hook -> conduit build -> activation + conduit wiring + post hook.
- Evidence: `src/melder/spellbook/spellbook_creation_system.py:144`, `src/melder/spellbook/spellbook_creation_system.py:164`, `src/melder/spellbook/spellbook_creation_system.py:168`, `src/melder/spellbook/spellbook_creation_system.py:172`, `src/melder/spellbook/spellbook_creation_system.py:184`, `src/melder/spellbook/spellbook_creation_system.py:193`.

### 3) Scheduler lifecycle cost model
- One conjure runs `_run_scheduler_with_phases(...)` up to three times
  (structural pass, foundational resolution pass, plan resolution pass), each
  with new scheduler construction and teardown.
- `PhaseScheduler` spins worker threads lazily and joins them during cleanup.
- Evidence: `src/melder/spellbook/spellbook_creation_system.py:637`, `src/melder/spellbook/spellbook_creation_system.py:743`, `src/melder/spellbook/spellbook_creation_system.py:757`, `src/melder/spellbook/spellbook_creation_system.py:910`, `src/melder/utilities/synchronization/phase_scheduler.py:352`, `src/melder/utilities/synchronization/phase_scheduler.py:161`.

### 4) Broad per-spell scans
- Phase factories repeatedly build one `UnitOfWork` per local spell in phases
  1-4 and 8-11.
- Structural validation then does a second full spell scan via
  `_collect_broken_spells`.
- Conduit activation does another all-spell pass in
  `define_conduit_into_spells`.
- Evidence: `src/melder/spellbook/spellbook_creation_system.py:1481`, `src/melder/spellbook/spellbook_creation_system.py:1656`, `src/melder/spellbook/spellbook_creation_system.py:984`, `src/melder/spellbook/spellbook_creation_system.py:458`.

### 5) Existing profile signal
- Existing profile test run (already executed in this session) showed
  `execution_plan` as the dominant printed phase slice in depth-9 conjure.
- Harness evidence: `benchmarks/testing_other_di/test_melder_hotpath_profiles.py:202`, `benchmarks/testing_other_di/test_melder_hotpath_profiles.py:214`, `benchmarks/testing_other_di/test_melder_hotpath_profiles.py:220`.

## Hotspot Candidates (Ranked)
1. Scheduler lifecycle churn (three scheduler lifecycles per conjure path).
2. Phase 11 execution-plan runtime (largest measured phase in current profile).
3. Per-phase UnitOfWork allocation across all spells (repeated list/object builds).
4. Post-phase and activation scans over all spells.
5. Duplicate/registry scan in `_check_all_spells` before conduit construction.

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-13-discovery-conjure-paths - Build discovery baseline, hotspot map, and prioritized optimization candidates for conjure. (`context_compass/tasks/2026-02-13_discovery_conjure_paths_task.md`)
- [ ] Task: TASK-2026-02-14-conjure-scheduler-lifecycle-reduction - Reduce per-conjure scheduler lifecycle overhead while preserving phase contracts. (`context_compass/tasks/2026-02-14_conjure_scheduler_lifecycle_reduction_task.md`)
- [ ] Task: TASK-2026-02-14-conjure-phase-unit-allocation-fastpath - Reduce avoidable phase-factory/unit allocation overhead in conjure path. (`context_compass/tasks/2026-02-14_conjure_phase_unit_allocation_fastpath_task.md`)
- [ ] Task: TASK-2026-02-14-conjure-activation-and-validation-scan-fastpath - Optimize global scan/wiring passes on conjure path. (`context_compass/tasks/2026-02-14_conjure_activation_and_validation_scan_fastpath_task.md`)

## Acceptance Criteria
- Discovery output identifies top conjure hotspots with evidence.
- Follow-up optimization tasks are documented and prioritized.

## Validation / Test Plan
- Use targeted code-path inspection and relevant existing test/benchmark hooks.
- Record commands and outputs for any executed measurements.

## UX / API / Data Notes
- Internal runtime optimization planning only; no API change in discovery pass.

## Risks / Mitigations
- Risk: conflating conjure and meld costs.
  Mitigation: isolate conjure-only paths in discovery notes.

## Open Questions
- Which conjure workloads should be baseline scenarios for this story?

## Decision Log
- 2026-02-13: Story created from user-requested optimization epic setup.
- 2026-02-14: Activated `TASK-2026-02-13-discovery-conjure-paths`; discovery now running with incremental ticket logging.
- 2026-02-14: Discovery completed with source-anchored call flow + ranked hotspots; added three follow-up implementation tasks.
- 2026-02-14: Scheduler path investigation found and fixed queue-empty exception handling in `PhaseScheduler` worker loop; added regression coverage.
- 2026-02-14: Scheduler lifecycle reduction implemented for conduit resolution by collapsing 5-11 into one scheduler lifecycle with foundational-error plan gating snapshot plus focused regression tests.
- 2026-02-14: Phase-unit-allocation fastpath implemented via shared per-spell factory helper consolidation in `SpellbookCreationSystem`.
- 2026-02-14: Removed redundant conjure duplicate-id recheck (`spellbook._check_all_spells()`) from `_resolve_conjure_policy`; bind-time SHA guard remains unchanged.

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: `TASK-2026-02-14-conjure-scheduler-lifecycle-reduction` is implemented and in review: conduit resolution now executes phases 5-11 through one scheduler lifecycle while preserving foundational-error gating semantics.
  EVIDENCE: context_compass/tasks/2026-02-14_conjure_scheduler_lifecycle_reduction_task.md:6-10, src/melder/spellbook/spellbook_creation_system.py:740-759, src/melder/spellbook/spellbook_creation_system.py:852-933
  IMPACT: Highest-ranked conjure hotspot (scheduler lifecycle churn) now has an implemented fastpath with focused regression coverage.
  NEXT: Confirm acceptance for scheduler-lifecycle reduction, then move to remaining conjure tasks (phase-unit-allocation and activation/validation scan closure).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Conjure duplicate-id recheck was removed from `_resolve_conjure_policy`; duplicate SHA check remains at `Spellbook.bind` front door.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:280, src/melder/spellbook/spellbook_creation_system.py:285, src/melder/spellbook/spellbook.py:2496
  IMPACT: Removes one redundant conjure-path duplicate scan while preserving bind-time collision enforcement.
  NEXT: Confirm acceptance for this activation/validation fastpath change and continue remaining conjure optimization scope.

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: `TASK-2026-02-14-conjure-phase-unit-allocation-fastpath` implementation completed by consolidating eight duplicated per-spell phase factory loops into one shared helper while preserving label/metadata/args contracts.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:1481, src/melder/spellbook/spellbook_creation_system.py:1666, tests/unit/melder/spellbook/test_spellbook.py:1343
  IMPACT: Reduces repeated allocation/lookup scaffolding in conjure setup without semantic drift.
  NEXT: Confirm acceptance and then advance to activation/validation scan fastpath task.

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Next conjure optimization step is the phase-unit-allocation fastpath using a shared per-spell factory helper while preserving labels/metadata/cancel-event contracts.
  EVIDENCE: context_compass/tasks/2026-02-14_conjure_phase_unit_allocation_fastpath_task.md:1, src/melder/spellbook/spellbook_creation_system.py:1481
  IMPACT: Moves optimization forward with low blast radius after scheduler worker-stability fix.
  NEXT: Implement helper extraction and validate targeted spellbook factory tests.

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Conjure scheduler-path work identified a worker-loop exception mismatch (`QueueEmpty` vs custom `Empty`) that could terminate idle workers during sparse long phases.
  EVIDENCE: src/melder/utilities/synchronization/phase_scheduler.py:5, src/melder/utilities/synchronization/phase_scheduler.py:399, tests/unit/melder/utilities/synchronization/test_phase_scheduler.py:185
  IMPACT: Scheduler behavior stability is now guarded before any broader lifecycle/overhead optimizations.
  NEXT: Continue task-level optimization discovery after this correctness fix.

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Notes section added to enforce active_documentation for in-flight findings.
  EVIDENCE: context_compass/agent_onboarding/agent/general/skills/active_documentation.md:1
  IMPACT: Keeps ticket memory durable across compaction by requiring evidence-backed notes.
  NEXT: Append new findings here as work continues.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Discovery is complete and documented.
Scheduler-lifecycle reduction has now been implemented and validated in review.
Next step is user acceptance for scheduler-task closure and then closure routing
for phase-unit-allocation and activation/validation scan tasks.

