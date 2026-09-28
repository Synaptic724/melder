# Story: Probe creation context - a sampled, self-ending instrumented body harvested at a trigger point

## Metadata
- Story ID: STORY-2026-09-27-probe-creation-context-harvest
- Epic: EPIC-2026-09-27-adaptive-creation-contexts
- Status: draft
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-27T23:42:45Z
- Updated: 2026-09-28T00:57:27Z

## User Narrative
As the Melder owner, I want a probe version of a spell's creation context that counts and, on demand, times
every site and constructor for a bounded window, then harvests what it saw at a trigger point and swaps itself
out for the plain body, so that the runtime learns the structure it actually builds at a cost that ends.

## Value / MRP Alignment
The data source for every other idea. The measured cost bounds it: count-only +4..+11% per call while open,
timed +90..+130%, so the probe must be a window with an end, never an always-on instrument. The self-replacing
executor slots make the swap a contract Melder already has.

## Ticket Contract
- ENTRY_GATE: owner's pick; patch docs (architecture: probe lifecycle; component: SpellCompiler codegen
  strategies, Meld Resolution Runtime) before src.
- EXECUTION_BOUNDARY: `codegen_creation_system/` (a probe emission beside the plain one, the hydrator
  publish point), `creation_context.py` and its factory, `SpellbookConfiguration` switches, `Spell` (value-
  only profile slot), tests.
- DEPENDENCIES: the probe overhead prototype; the versioning story for the swap contract if it lands first,
  otherwise the specializer's swap path.
- EXIT_GATE: the probe body emitted from the same rows as the plain body; window ends by count, time or
  natural window; harvest writes a value-only profile; default off byte-identical; suites green; VM cost
  within the measured bound.
- FAILURE_ESCALATION: BLOCKER if the emitters cannot host an instrumented variant without touching the plain
  body; DECISION_REQUEST on the trigger-point vocabulary.

## Requirements (Functional)
- Switches: profiling on/off, window size (calls), optional timed mode, trigger point kind.
- Probe body: per-site hit/miss counters, per-site and per-constructor ns in timed mode, a call counter.
- Trigger points: N calls, elapsed time, or a natural window (pool return, SpellSpace reset, warm conjure);
  the harvest runs on the building thread after a successful creation, never under a build lock.
- Harvest: a value-only profile record on the spell (and per door where the route differs), then the self-
  swap to the plain body.

## Requirements (Non-Functional)
- Count-only window <= +11% per creation while open, 0 after; timed mode on demand only.
- Default-off path byte-identical (differential test).
- Overlay rules; every emitted variant documented in the component map.

## Scope Boundaries
- In scope: the probe emission, the window, the trigger points, the harvest record, switches, tests, docs.
- Out of scope: the report (its own story), the creator/thread fields (their own story), regeneration.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Drafted from the owner's idea list (2026-09-27T23:42:45Z); opens when the owner picks it.

## Dependencies / Related Work
- Prototype and cost: artifacts/pgo_strategies_20260927/vm_probe_overhead_prototype_gil0_20260927.md
- tests/experimentation/probe_creation_context_prototype.py
- Self-replacing slots: src/melder/aether/conduit/meld/creation_context/creation_context.py:12-110

## Tasks (Implementation Checklist)
- [ ] Task: INVESTIGATE how this idea lands in the `CreationContext` object (slot, executor variant, guard,
      cleanup ordering) before anything else; its finding is the story's first note (owner, 2026-09-27T23:54Z).
- [ ] Task: TASK design: probe emission beside the plain plan, window end, harvest record schema, trigger
      points; patch docs.
- [ ] Task: TASK implement the probe body and the switches; component tests on the window swap and the harvest.
- [ ] Task: TASK measure the window cost on the VM against the prototype numbers; hand the gauntlet to the owner.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- With profiling off: identical bytes and timing within noise. With it on: the profile record shows sites,
  hits/misses, counts (and ns in timed mode) for the window, then the plain body runs.

## Validation / Test Plan
- Unit tests on the emitter; component tests on window end and self-swap; the differential matrix; VM cost
  runs; owner-run gauntlet.

## UX / API / Data Notes
- Switches on `SpellbookConfiguration`; the profile record is value-only (JSON-able).

## Risks / Mitigations
- Probe cost eats the win -> bounded window, count-only by default.
- A rebuild replaces the probe mid-window -> a rebuilt context starts plain; the window restarts only if
  profiling is on.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.

## Open Questions
- Per spell or per (spell, door)? What ends a window in a scope that never returns to a pool?

## Decision Log
- 2026-09-27T23:42:45Z (owner): idea collected into the epic; one story per idea. Ranked second: the owner's
  tool; measured cost already known.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/pgo_strategies_20260927/ (proof and runs shared by the epic; new runs land here)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: promoted into the canonical maps when the story ships.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - probe body; window; trigger point; harvest; self-swap
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-27T23:42:45Z
  TYPE: MEASURE
  CLAIM: Probe overhead on real emitted plans: count-only +18..+43 ns per call (+4..+11%), timed +181..+701 ns
    (+90..+130%, perf_counter_ns = 33 ns); a 1,000-call timed window costs 0.2-0.7 ms once per spell.
  EVIDENCE:
  - artifacts/pgo_strategies_20260927/vm_probe_overhead_prototype_gil0_20260927.md
  - tests/experimentation/probe_creation_context_prototype.py:1-136
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:12-110
  IMPACT: Fixes the window design: count-only by default, timed on demand, always self-ending.
  NEXT: owner picks; then the design task.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
STATE 2026-09-27T23:42:45Z: DRAFT. Collected from the owner's direction; not routed. Opens when the owner
picks it; its first
task is the measurement plan and the patch docs.

STATE 2026-09-28T00:57:27Z: PARKED (backlog_by_owner) with the epic; reopen on the owner's word.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
