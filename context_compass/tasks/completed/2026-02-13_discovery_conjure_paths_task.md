Completed: 2026-02-14
Summary: Accepted in closure pass; implementation/discovery outcomes are complete and archived.

# Task: Discovery Conjure Paths

## Metadata
- Task ID: TASK-2026-02-13-discovery-conjure-paths
- Story: STORY-2026-02-13-optimize-conjure-paths
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-13
- Updated: 2026-02-14

## Objective
Build an evidence-backed hotspot map for `Spellbook.conjure` and related
orchestration phases so we can define safe, high-impact optimization tasks.

## Scope Boundaries
- In scope:
- `Spellbook.conjure` orchestration path and hook lifecycle.
- `SpellbookCreationSystem` structural/resolution phase orchestration.
- `PhaseScheduler` usage patterns impacting conjure runtime.
- Existing conjure-related benchmark harness behavior.
- Out of scope:
- Implementing conjure runtime optimizations in this task.
- Meld runtime optimization.
- Mutation runtime wiring.

## Steps / Checklist
- [x] Create and activate discovery task with explicit evidence discipline.
- [x] Trace `Spellbook.conjure` call flow and identify top-level cost centers.
- [x] Trace `SpellbookCreationSystem` orchestration and phase registration costs.
- [x] Correlate findings with existing benchmark/profiling harness.
- [x] Produce ranked hotspot list and propose follow-up implementation tasks.

## Discovery Findings (How Conjure Works)
### 1) Front-door and lifecycle wrapper
- `Spellbook.conjure(...)` takes the lock, blocks repeat conjure on the same
  spellbook, builds a short-lived `SpellbookCreationSystem`, delegates, and
  always runs `SpellbookCreationSystem.cleanup()` in `finally`.
- Evidence: `src/melder/spellbook/spellbook.py:2922`, `src/melder/spellbook/spellbook.py:2985`, `src/melder/spellbook/spellbook.py:3006`, `src/melder/spellbook/spellbook.py:3016`, `src/melder/spellbook/spellbook.py:3018`.

### 2) Conjure orchestration shape
- `SpellbookCreationSystem.conjure()` runs this order:
  1. `_prepare_spellbook_for_conjure` (freeze/bind config if needed + structural phases + disposal metadata),
  2. `_prepare_resolution_for_conjure` (new conduit id + conduit-scoped resolution phases),
  3. `_resolve_conjure_policy` (system-state gate + `_check_all_spells`),
  4. pre-created hooks,
  5. conduit constructor,
  6. activation/wiring hooks and ownership wiring.
- Evidence: `src/melder/spellbook/spellbook_creation_system.py:144`, `src/melder/spellbook/spellbook_creation_system.py:164`, `src/melder/spellbook/spellbook_creation_system.py:168`, `src/melder/spellbook/spellbook_creation_system.py:172`, `src/melder/spellbook/spellbook_creation_system.py:178`, `src/melder/spellbook/spellbook_creation_system.py:184`, `src/melder/spellbook/spellbook_creation_system.py:193`.

### 3) Scheduler lifecycle shape per conjure
- Conjure path runs scheduler lifecycle via `_run_scheduler_with_phases(...)`
  multiple times in one conjure:
  - structural phases (1-4),
  - conduit foundational resolution (5/6/7),
  - conduit plan resolution (8/9/10/11, when no errors).
- Each scheduler run constructs a new `PhaseScheduler`, registers phases,
  executes, then always cleans up.
- Evidence: `src/melder/spellbook/spellbook_creation_system.py:637`, `src/melder/spellbook/spellbook_creation_system.py:743`, `src/melder/spellbook/spellbook_creation_system.py:757`, `src/melder/spellbook/spellbook_creation_system.py:910`, `src/melder/spellbook/spellbook_creation_system.py:933`, `src/melder/spellbook/spellbook_creation_system.py:941`.

### 4) PhaseScheduler runtime cost model
- `PhaseScheduler` creates cancellation state + queue + thread pool state,
  starts workers lazily on first non-empty phase, and joins/tears down workers
  during cleanup.
- `_run_single_phase(...)` creates work via factory, enqueues all units, waits
  on futures with `FIRST_EXCEPTION`, then scans done/pending sets.
- Evidence: `src/melder/utilities/synchronization/phase_scheduler.py:90`, `src/melder/utilities/synchronization/phase_scheduler.py:113`, `src/melder/utilities/synchronization/phase_scheduler.py:161`, `src/melder/utilities/synchronization/phase_scheduler.py:352`, `src/melder/utilities/synchronization/phase_scheduler.py:419`, `src/melder/utilities/synchronization/phase_scheduler.py:476`.

### 5) Spell-wide scans and wiring on conjure path
- Structural and plan phase factories allocate one `UnitOfWork` per local spell
  repeatedly across phases.
- Structural completion re-scans all spells for `is_broken`.
- Conduit activation wires ownership into every spell and may register existing
  user-created objects.
- Policy resolution calls `_check_all_spells()`, which scans spell indexes and
  all recorded versions for global duplicate checks.
- Evidence: `src/melder/spellbook/spellbook_creation_system.py:1481`, `src/melder/spellbook/spellbook_creation_system.py:1515`, `src/melder/spellbook/spellbook_creation_system.py:1549`, `src/melder/spellbook/spellbook_creation_system.py:1583`, `src/melder/spellbook/spellbook_creation_system.py:1656`, `src/melder/spellbook/spellbook_creation_system.py:1696`, `src/melder/spellbook/spellbook_creation_system.py:1736`, `src/melder/spellbook/spellbook_creation_system.py:1776`, `src/melder/spellbook/spellbook_creation_system.py:984`, `src/melder/spellbook/spellbook_creation_system.py:458`, `src/melder/spellbook/spellbook.py:1269`.

## Hotspot Candidates (Ranked)
1. Scheduler lifecycle churn across one conjure:
   three scheduler build/register/run/cleanup cycles before conduit activation.
2. Execution-plan phase cost (Phase 11) inside conduit plan pass:
   prior profile run captured `execution_plan` as the dominant phase slice.
3. Repeated per-phase unit allocation across all spells:
   UnitOfWork list/object creation repeats in phases 1-4 and 8-11.
4. Post-phase full scans:
   `_collect_broken_spells(...)` and cleanup sweeps touch all local spells.
5. Conduit ownership stamping over all spells:
   `_activate_conjured_conduit` -> `define_conduit_into_spells` loops all spells.
6. Duplicate-check scan in `_check_all_spells`:
   nested loop over spell indexes and all historical versions.

## Proposed Follow-up Implementation Tasks
- `TASK-2026-02-14-conjure-scheduler-lifecycle-reduction`:
  reduce scheduler lifecycle churn while preserving phase-order/error contracts.
- `TASK-2026-02-14-conjure-phase-unit-allocation-fastpath`:
  reduce avoidable allocations in phase factory paths and scheduler barriers.
- `TASK-2026-02-14-conjure-activation-and-validation-scan-fastpath`:
  optimize `_check_all_spells`, broken-spell scans, and conduit wiring fast paths.

## Deliverables
- Conjure call-flow map with source evidence.
- Ranked conjure hotspot candidates with rationale.
- Follow-up implementation task proposals in story/task docs.

## Files / Paths Impacted
- `context_compass/stories/completed/2026-02-13_optimize_conjure_paths_story.md`
- `context_compass/tasks/completed/2026-02-13_discovery_conjure_paths_task.md`
- `context_compass/attention_board.md`

## Validation
- `python -m pytest benchmarks/testing_other_di/test_melder_hotpath_profiles.py -q -s` (with `PYTHONPATH=src`) -> `3 passed`.
- Observed from that run:
  - Conjure total: `77.032 ms`
  - Largest printed phase slice: `execution_plan: 44.261 ms`
  - Cycle summary: `conjure avg=73.952 ms`, `meld avg=0.145 ms`, `cleanup avg=1.728 ms`
- Evidence path for profiling harness logic:
  `benchmarks/testing_other_di/test_melder_hotpath_profiles.py:202`,
  `benchmarks/testing_other_di/test_melder_hotpath_profiles.py:214`,
  `benchmarks/testing_other_di/test_melder_hotpath_profiles.py:318`.

## Risks / Rollback Notes
- Risk: blending meld and conjure costs.
- Mitigation: keep findings scoped to `Spellbook.conjure` and creation-system phases.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed
## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Notes section added to enforce active_documentation for in-flight findings.
  EVIDENCE: context_compass/agent_onboarding/agent/general/skills/active_documentation.md:1
  IMPACT: Keeps ticket memory durable across compaction by requiring evidence-backed notes.
  NEXT: Append new findings here as work continues.

## Context / Handoff Summary
Discovery is complete and this task is now in review.
Conjure call flow, scheduler lifecycle hotspots, and follow-up implementation
tasks are documented with source anchors.
Next step: confirm task acceptance and execute the first follow-up implementation
task in story priority order.
