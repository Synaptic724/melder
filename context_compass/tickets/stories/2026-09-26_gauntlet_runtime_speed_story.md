

# Story: Melder wins the real-world gauntlet hot path (scope-cycle runtime speed)

## Metadata
- Story ID: STORY-2026-09-26-gauntlet-runtime-speed
- Epic: none (standalone; outside the IR epic's boundary and separate from the override performance epic)
- Status: in_progress
- Owner: user
- Agent Name: melder_2
- Priority: p1
- Created: 2026-09-26T15:43:24Z
- Updated: 2026-09-26T21:38:55Z

## User Narrative
As the Melder owner, I want Melder's per-scope-cycle runtime on the real-world gauntlet (free-threaded, three
threads) to match or beat dishka and dependency-injector, so that Melder wins the benchmark it is compared on
without changing any public behavior.

## Value / MRP Alignment
The gauntlet exercises what every user pays per request: scope create, warm melds, scope cleanup. A faster core
with unchanged contracts (existence semantics, cleanup ordering, thread-safety) is MRP work. A speedup that
weakens a cleanup or concurrency guarantee is out.

## Ticket Contract
- ENTRY_GATE: board row routes to the active child task; owner decisions D1-D3 recorded in that task.
- EXECUTION_BOUNDARY: measurement and attribution first, read-only on src/ and benchmarks/; each code change is
  its own task behind patch docs and names its files; no public API change.
- DEPENDENCIES: melder_0's override performance lane (owns the warm meld call); fable_0's 2026-09-25 per-cycle
  counts and the deferred door-diet request on the IR epic; owner-run numbers for every accepted gain.
- EXIT_GATE: owner-run gauntlet meets the agreed target in the same run as the competitors; suites green on
  3.14t and GIL for every change; the owner accepts.
- FAILURE_ESCALATION: CONFLICT when a candidate needs another agent's files; DECISION_REQUEST for the target and
  candidate selection; BLOCKER when no comparable measurement is possible.

## Requirements (Functional)
- No change to meld results, existence semantics, cleanup and disposal ordering, or error behavior.

## Requirements (Non-Functional)
- Every claimed gain is measured: same-run comparison with dishka and dependency-injector, repeated runs,
  dispersion reported; VM numbers are relative only and owner-run numbers are authoritative.
- No new lock on a warm path; suites green on 3.14t and GIL.

## Scope Boundaries
- In scope: gauntlet measurement protocol; per-scope-cycle attribution (outer and request scope create and
  cleanup, pooled lesser and SpellSpace acquire and return, creations disposal, ID minting, per-cycle locks);
  candidate changes in that lifecycle.
- Out of scope: the warm meld call and override plans (melder_0) unless the owner reassigns them; import/boot
  setup (parked by the owner on 2026-09-25) unless reopened; compiler phases (IR epic); changing what the
  gauntlet measures without owner approval.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner answered D1-D3 (2026-09-26T15:45:57Z): meld and SpellSpace hot path, VM copy plus owner runs,
  setup parked.

## Dependencies / Related Work
- tickets/tasks/2026-09-26_build_site_plan_lowering_task.md (melder_0; warm meld call, cross-thread refcounts)
- tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md:825-865 (door-diet request, owner deferral)
- tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md:594-624 (2026-09-25 cProfile counts)

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-09-26-measure-gauntlet-scope-cycle-costs - reproduce, attribute, rank candidates (no code).
- [ ] Task: TASK-2026-09-26-emit-positional-constructor-args - P1, positional constructor arguments.
- [ ] Task: TASK-2026-09-26-spellspace-meld-warm-id-lane - P4, SpellSpace.meld warm id lane.
- [ ] Task: TASK-2026-09-26-attribute-gauntlet-tail-spikes - Melder-only multi-millisecond cycle spikes.
- [ ] Task: TASK-2026-09-26-spellspace-build-locks - can spellspace-scoped first builds skip their locks.
- [ ] Task: TASK-2026-09-26-remove-nested-slot-guard-take - door-called first builds take their build lock once.
- [ ] Task: one task per candidate the owner picks, each behind patch docs and a gauntlet gate.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- The target is set by the owner after the attribution task; the natural candidate is melder hot_scopes/s at or
  above dishka's in the same owner run.
- Each change: owner-run before and after, suites green on 3.14t and GIL, system docs updated.

## Validation / Test Plan
- Owner-run gauntlet before and after each change; VM-copy runs for attribution and A/B.

## UX / API / Data Notes
- None; no public surface change is planned.

## Risks / Mitigations
- 2-vCPU VM cannot reproduce three-thread scaling -> VM numbers are relative; owner-run confirms.
- Overlap with melder_0's warm-meld work -> file ownership named per task; mailbox notice before a shared file.
- Cross-day variance on the owner machine (competitors moved 1.28x-1.79x between the 09-25 and 09-26 runs) ->
  ratios within one run only.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- D1-D3, in the child task's DECISION_REQUEST.

## Decision Log
- 2026-09-26T15:45:57Z: focus on the meld and SpellSpace hot path (and resolution if the profile points
  there); VM copy for attribution, owner-run for claimed gains; setup parked. See the child task's DECISION note.
- 2026-09-26T17:29:58Z: P3 (deferred refcounting through a ctypes call into an unstable CPython API) dropped in
  every form by the owner, opt-in flag included; the prototype stays in artifacts as research only.
- 2026-09-26T17:32:38Z: owner go-ahead for clean levers, each gated by VM A/B, suites on 3.14t (gil 0/1) and
  the GIL build, a 30k soak, a NOTICE to the file owner and a byte-identical apply.
- 2026-09-26T20:35:11Z: owner direction: optimize code, not the benchmark; pools and their shells are created when they are today (no prewarming). Conjure-time hydration withdrawn; levers must remove work.
- 2026-09-26T21:16:14Z: owner closed lever 1's lifecycle as measured and asked to look at the spellspace build locks (own discovery task).
- 2026-09-26T21:38:55Z: owner go-ahead to implement the nested slot-guard removal, safe shape only ("just do it ... make it safe"); melder_2 implements.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/gauntlet_runtime_speed_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: story closure; the owner confirms retention.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-26T15:43:24Z
  TYPE: PLAN
  CLAIM: Story shape: one attribution task first (no code), then one gauntlet-gated task per candidate the owner
    picks. The child task carries the baseline, the environment facts and the D1-D3 request.
  EVIDENCE: tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:1-40
  IMPACT: No code changes until the per-cycle cost map exists and the owner picks.
  NEXT: Owner answers D1-D3 in the child task.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T19:14:12Z
  TYPE: DECISION
  CLAIM: Where the levers stand.
    - P1 is in the tree since 16:16Z, but melder_0's S2b-2 (17:26Z) moved normal melds onto the site-plan lowering,
      which passes operands positionally itself. P1's code is now off the normal path, and its fate goes with
      S2b-3.
    - P3 is dropped (owner).
    - Lever 1, string interning: no gain, dropped.
    - Lever 2, thread-affine pools: -6% to -7% per cycle on Linux. It changes pooling semantics and its Windows
      effect is unknown, so it waits for a design.
    - P4, SpellSpace.meld warm id lane: validated twice, about -17% per cached space meld and -2% to -3% per
      gauntlet cycle. Its task is open for the apply.
    - Side finding, a pre-existing RISK (measure task): the documents promise an active-scope check on
      SpellSpace.meld that the source does not perform. The owner decides between enforcing it and correcting
      the documents.
  EVIDENCE:
  - tickets/tasks/2026-09-26_emit_positional_constructor_args_task.md:182-205
  - tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:577-650
  - tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:699-727
  - tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:765-791
  - tickets/tasks/2026-09-26_spellspace_meld_warm_id_lane_task.md:1-170
  IMPACT: The gauntlet's positional gain now belongs to melder_0's lowering. melder_2's next levers are the scope
    lifecycle and pools, both files in this lane.
  NEXT: Land P4; then take the owner's Windows gauntlet run and the scope-check decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T20:29:19Z
  TYPE: FACT
  CLAIM: State after the owner's Windows runs on 0.2.68-0.2.70 (19:31Z to 20:05Z).
    - hot_scopes/s is 0.86-0.88x dishka, up from 0.78x in the morning. The SpellSpace window is at parity on the
      request and worker_b lanes.
    - The tail is attributed: Melder's only specific spike is turn 0's first-use hydration and compile, and no GC
      fires in the loop.
    - The remaining average gap, about 0.2 ms per iteration, is half in the worker lanes' cycles and half in
      thread-exit cost outside them. On 3.14t that cost grows with state built on worker threads, which Melder's
      lazy first use leaves behind.
    - Conjure-time hydration is the shared next lever, pending the owner's pick.
  EVIDENCE:
  - tickets/tasks/2026-09-26_attribute_gauntlet_tail_spikes_task.md:245-369
  - tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:793-816
  IMPACT: The next implementation task opens on the owner's pick; P1 waits for closure and P4 for acceptance.
  NEXT: Owner decisions, per the tail task's DECISION_REQUEST.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

- DATETIME: 2026-09-26T21:32:12Z
  TYPE: FACT
  CLAIM: Where the levers stand after the owner closed lever 1's lifecycle (21:15Z).
    - Spellspace build locks (own task, in review): every slotted first build takes the same slot guard twice
      (door, then the site plan's root-site miss). Removing the nested take saves about 0.3 us per worker cycle
      on the VM (-4%) and changes nothing observable if the door keeps its guard. Dropping the door's guard
      instead is safe only in the no-hooks lanes. The code is melder_0's, and the owner picks who implements.
    - Dropping the last guard for spellspace builds needs a new thread rule for spellspaces. Not recommended now.
    - Still open for the owner: P1 closure, P4 acceptance, the SpellSpace active-scope RISK, the
      system_document_view race, and the tail task's optional 200k trend run.
  EVIDENCE:
  - tickets/tasks/2026-09-26_spellspace_build_locks_task.md:235-302
  - tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md:1137-1149
  IMPACT: No implementation task opens until the owner picks. The story's next measurable gain is that removal.
  NEXT: Owner decision on the build-locks DECISION_REQUEST.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Attribution is done (measure task). In the tree: P1 (off the normal path since S2b-2) and P4 (0.2.68), both in
review. Dropped: P3, interning, conjure-time hydration. Lever 1's lifecycle is closed as measured. The next gain is
removing the nested slot-guard take on first builds (about 0.3 us per worker cycle on the VM). It is in the build-locks
task's DECISION_REQUEST and waits on the owner's pick of who implements it (melder_0's code). Owner decisions are
listed in the last note.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
