# Epic: Profile-guided optimization of codegen - live, optimistic and opportunistic regeneration

## Current Backlog Disposition
- Parked: 2026-09-28T00:57:27Z
- Disposition: backlog_by_owner; superseded by EPIC-2026-09-27-adaptive-creation-contexts, which is parked
  beside it. Its measurements and decision log are the record; nothing here is active.

## Metadata
- Epic ID: EPIC-2026-09-27-codegen-pgo-strategies
- Status: blocked
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-27T19:30:50Z
- Updated: 2026-09-28T00:57:27Z
- Superseded By: tickets/epics/backlog/2026-09-27_adaptive_creation_contexts_epic.md
- Target Window: opened 2026-09-27 on the owner's direction; discovery first
- Related Program/Initiative: SpellCompiler codegen (phases 8-11), Meld runtime, creation caches
- Supersedes: tickets/epics/completed/2026-06-20_adaptive_pgo_di_optimizer_epic.md (closed unstarted in the
  departed-agent cleanup of 2026-06-30; its design artifact is prior art, its substrate map was never made)

## Problem / Opportunity
Melder compiles one executor per spell and family (generalized, many_only, singleton specialization) from
the whole graph at conjure, and since 2026-09-26 it can REBUILD those executors live: a spell's creation
context and phase-11 plan are replaced inside a rebuild window that freezes and drains the spell-index
gate, doors hold per-slot build locks, override melds compile one plan per key set on first use, and the
structural snapshot replays phase 3-4 rows on a warm conjure. That is the substrate the June epic did not
have. What the runtime still does not do is learn from its own execution: every executor is compiled
from static knowledge (existence, sockets, defaults) and never from what actually happens - which
singletons are already stored when a consumer is built, which override key sets recur, which transients
are built ten thousand times per second by which threads, which scopes come and go.

Owner direction (2026-09-27): explore profile-guided optimization of codegen as a set of strategies, not
one mechanism - live PGO (profile, then regenerate in place through the rebuild windows), optimistic PGO
(emit the speculated fast body first, guarded, and fall back), opportunistic PGO (regenerate only when a
safe window opens on its own: pool return, scope exit, revalidation, conjure), and strategies keyed on the
existence types, because the guard cost and the stability of a speculation differ by lifetime.

EVIDENCE:
- context_compass/system_docs/src_architecture.md:874-1000 (rebuild windows, site plans, build locks)
- context_compass/system_docs/src_architecture.md:657-711 (conjure and meld sequences)
- artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md (prior design; guard ladder and door epochs)

## MRP Alignment (Most Reasonable Product)
The MRP is a runtime that gets faster the longer it runs without ever trading correctness for speed:
every speculation is guarded, every regeneration goes through the existing rebuild window, and the
default path with the optimizer off is byte-identical. Discovery comes first: the strategies are ranked
on measured cost and measured benefit on the persistent gauntlet before anything is built.

## Ticket Contract
- ENTRY_GATE: owner direction (2026-09-27); this epic and its first story routed on `attention_board.md`.
- EXECUTION_BOUNDARY: discovery reads anywhere under `src/melder/aether/conduit/meld/`,
  `src/melder/aether/conduit/creations/`, `src/melder/aether/spellbook/spell_compiler/` (phases 8-11,
  codegen_creation_system, structural_snapshot), `src/melder/utilities/caching_system/` and the
  benchmarks; implementation under later stories only, each with patch docs (system-impacting).
- DEPENDENCIES: the persistent runtime gauntlet (`benchmarks/testing_other_di/`), the June design
  artifact, the shared-context rebuild window and door-held build lock work of 2026-09-25/26.
- EXIT_GATE: a strategy catalogue with measured costs and a ranked recommendation accepted by the owner;
  at least one strategy implemented behind a default-off switch with a measured, repeatable speedup on the
  gauntlet at threads>1 on 3.14t (owner-run), deopt proven under mutation, transfer, cleanup, purge and
  pool return; or the epic parks with the numbers that say no.
- FAILURE_ESCALATION: DECISION_REQUEST before any strategy that changes what a warm meld does with the
  optimizer off; BLOCKER if a safe regeneration window cannot be evidenced for a strategy.

## Goals (Outcomes)
- A written catalogue of PGO strategies for this codebase, each with: the profile signal it needs, where
  the signal is captured, the regeneration trigger, the guard or deopt path, the existence types it
  applies to, its cost with the optimizer off and on, and its expected win.
- Measured numbers, not intuition, for signal capture cost and regeneration cost on the gauntlet.
- One strategy shipped end to end, default off, with a differential test proving identical results.

## Non-Goals (Explicit Exclusions)
- No change to what the default path does; no always-on profiling.
- No new cache format until a strategy needs persistence.
- No JIT, no bytecode tricks; codegen is the mechanism, as today.

## Scope Boundaries
- In scope: profile signals, regeneration triggers, guards, existence-type policies, measurement.
- Out of scope: MutationResearch, Crystallizer, Nexus surfaces (they observe, they do not optimize).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner opened the lane (2026-09-27T19:30:50Z); the exploration story is the entry point.
- from_state: in_progress
- to_state: review
- transition_reason: Superseded by EPIC-2026-09-27-adaptive-creation-contexts on the owner's direction
  (2026-09-27T23:49:25Z); the open styles story and its design task moved there; closure awaits the owner's word.

## Success Metrics
- Signal capture with the optimizer on costs under 2% of the gauntlet's per-cycle time; zero with it off.
- The first shipped strategy shows a repeatable speedup on the owner's 10-thread gauntlet run.

## Requirements (Functional + Non-Functional)
- Every speculation has a guard whose failure returns to the generalized path with the same result.
- Regeneration only inside a rebuild window or an equivalent proven-safe seam; never under a meld.
- Overlay rules: `Optional`/`Union`, no `getattr`/`hasattr` on owned code, rich docstrings, pytest unit-first,
  "Not run." until the owner reports.

## Constraints / Assumptions
- 3.14t free-threaded is the target; guards are single-int compares or nothing.
- Agent-side timing is directional only (2-core VM); ranking numbers are owner-run.

## Dependencies / External References
- artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md
- tickets/stories/backlog/2026-06-13_adaptive_pgo_di_optimizer_future_direction_story.md (parked; prior art)
- benchmarks/testing_other_di/test_persistent_runtime_gauntlet.py

## Milestones (Track Progress)
- [ ] Milestone 1: Regeneration substrate mapped from source - which windows exist, what they protect,
      what a rebuild costs, what state survives it.
- [x] Milestone 2 (partial, owner-accepted): the door fold and the specializer numbers stand in for the catalogue;
      the owner picked the probe-selected styles direction.
- [ ] Milestone 3: First strategy shipped default-off with differential and deopt tests; measured win.
- [ ] Milestone 4: Second strategy or park, on the numbers.

## Stories (Required to Complete)
- [x] Story: STORY-2026-09-27-pgo-strategy-exploration - discovery, the door fold (task 0d) and the specializer
      measurement. tickets/stories/completed/2026-09-27_pgo_strategy_exploration_story.md (done 2026-09-27T22:34:08Z)
- [ ] Story: STORY-2026-09-27-probe-selected-codegen-styles - MOVED 2026-09-27T23:49:25Z to the superseding epic;
      opened 2026-09-27T22:44:20Z:
      tickets/stories/backlog/2026-09-27_probe_selected_codegen_styles_story.md. A probe creation context that samples
      per-site timings into the DevOps station with a report, a selection of styles by measured delta (priority by
      benefit), the singleton-capture style (today's opt-in specializer) and a transient-inlining style; opened on
      the owner's approval, patch docs first.
- [ ] Story: second strategy or park.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: keep the catalogue artifact and this epic aligned as measurements land.
- [ ] Task: verify Ticket Microcycle enforcement across the lane.

## Acceptance Criteria (Epic Done)
- Catalogue accepted; one strategy shipped default-off; owner-run gauntlet speedup recorded; deopt matrix
  green owner-run; both canonical system docs updated with the optimizer seam and indexes regenerated.

## Risks / Mitigations
- Stale speculation after a store clear, purge, transfer or notch -> guard on the existing epochs and
  gates; differential test per strategy.
- Profiling cost eats the win -> capture only in the doors that already run, single counters, measured.
- Regeneration thrash -> thresholds with hysteresis; opportunistic triggers only at natural windows.

## Applicable Anti-Patterns
- [ ] No implementation before the substrate map and the owner's pick.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.
- [ ] No strategy without a guard and a deopt test.

## Validation / Test Approach
- Discovery: source reads with `path:start-end` evidence; VM measurements labelled directional.
- Implementation: unit-first, a differential test (default vs optimized doors, identical results), a deopt
  matrix, the persistent gauntlet owner-run.

## Rollout / Adoption Plan
- Discovery story -> owner picks -> patch docs -> one strategy behind a configuration flag -> measure ->
  next strategy or park.

## Open Questions
- Which profile granularity: per spell, per (spell, conduit), per door, per override key set?
- Which existence types carry a stable enough speculation to be worth a guard (unique and per-conduit
  singletons look stable; many transients look like a site-plan pruning problem instead)?
- Where does the profile live between processes, if anywhere (creation cache section vs never persisted)?

## Decision Log
- 2026-09-27T19:30:50Z (owner): open the PGO lane as a strategy exploration; live, optimistic and opportunistic PGO and
  existence-type strategies are the axes; the dynamic regeneration substrate is the enabler.
- 2026-09-27T19:30:50Z (fable_0): remake rather than reopen - the June epic predates site plans, key-set plans, rebuild
  windows and the structural snapshot; its design artifact stays linked as prior art.
- 2026-09-27T19:43:17Z (fable_0, MEASURE): composition experiment ceiling - 3 Python calls (the door) and one C call per
  singleton read per creation; 180-540 ns per creation on the VM; transient-heavy shapes gain least. Owner
  decides whether to continue.
- 2026-09-27T19:53:07Z (fable_0, MEASURE): Melder's own composition is narrow (58% width 0, 23% width 1, none above
  8) and
  shallow (depth at most 5); the ceiling on such shapes is 183-320 ns per creation, mostly the door. Owner
  decides: park PGO proper and fold the door, or bring user-application shapes.
- 2026-09-27T20:01:08Z (fable_0, MEASURE): weighted by Melder's own width distribution an ideal PGO body saves
  ~205-212 ns
  per creation (54% bare, 35% with Melder-like inheritance), of which ~185 ns is the profile-free door; PGO
  proper averages ~20-30 ns. Recommendation: park; fold the door.
- 2026-09-27T20:14:33Z (fable_0, MEASURE, correction): measured directly, `Conduit.meld`'s prologue is 155-195 ns,
  the lane
  frame 20 ns, and a singleton site 23 ns of which a guarded constant recovers 16; PGO proper is ~6 ns per
  creation on Melder-shaped code. The door trims are the lever.
- 2026-09-27T22:34:57Z (owner, DECISION): PGO stays viable - the objection to "park" is that the creation context can be
  organized differently: a probe version gathers data and timings into the DevOps station with a report; several
  codegen styles exist (uniques cache-hit-first vs not, flat easy ones) and are selected by a min-heap over measured
  benefit per area of the app, dropping calls where they are not needed. fable_0's measurement in support: the
  existing opt-in specializer is one such style and shows -14% on wide8_singleton and +20% on chain8_singleton when
  applied blind, so measured selection is the missing piece. Exploration story turned in; the next story owns it.
- 2026-09-27T22:22:47Z (owner + fable_0, DECISION): PGO proper parked on the numbers; the profile-free door fold
  landed as the name/class-keyed warm entry (task 0d, notched 0.2.8201): -23..-47% per warm meld by name on the
  VM, name/class/id at parity. Owner: keep iterating; next lever is the executor held in the entry (drops the
  lane frame).

- 2026-09-27T23:49:25Z (owner + fable_0, DECISION): superseded. The owner asked for an epic collecting every idea
  with a story each (probe collected at a trigger point and harvested; thread and creator context; dynamic
  reporting; a new version of the creation context); that is EPIC-2026-09-27-adaptive-creation-contexts. This
  epic's measurements and decision log stand as its foundation; nothing here is re-opened.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md (prior art, retain_as_reference)
  - artifacts/pgo_strategies_20260927/ (catalogue and measurements; created by the exploration story)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the catalogue is promoted into the canonical maps when a strategy ships.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: PGO; codegen regeneration; guards; existence types.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-27T19:30:50Z
  TYPE: PLAN
  CLAIM: Exploration axes, as hypotheses to be evidenced by the story: (1) LIVE PGO - count what the doors
    already see (store hit/miss per slot, override key-set frequency, build order) and regenerate a spell's
    executor through the existing rebuild window when a threshold trips. (2) OPTIMISTIC PGO - emit the
    speculated body first (singleton-as-constant, most-frequent key-set plan inlined) behind a single
    epoch guard, generalized path on guard failure. (3) OPPORTUNISTIC PGO - regenerate only at windows that
    already exist: pool return, SpellSpace reset, revalidation, warm conjure, so the meld hot path never
    pays for it. (4) EXISTENCE-TYPE strategies - unique/per-conduit/per-space objects: bind stored instances
    as constants in consumers' plans; many transients: prune site plans by observed key sets and pre-size
    allocation; lineage/cluster: elect-once leaders. Each needs its guard, its window and its measured cost.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:874-1000
  - artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md
  IMPACT: The story maps the substrate first, then measures, then ranks; the owner picks.
  NEXT: the exploration story's first task - the regeneration substrate map from source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T22:34:57Z
  TYPE: PLAN
  CLAIM: Shape of the next story, from the owner's direction and the measured substrate: (1) a PROBE style of the
    creation context - the same phase-11 body with a sampled `perf_counter_ns` around each dependency site and the
    constructor, recording per-site hit/miss and ns into a DevOps report (sampling, because a timer call costs ~50-100
    ns and an always-on probe would cost more than it finds); (2) STYLES - the plain body, the singleton-capture body
    (today's specializer, guarded constants, deopt to plain), a transient-inlining body (child constructors inlined
    into the parent, dropping one frame per transient site), and per-area variants only if the probe shows areas
    differ; (3) SELECTION - a priority queue over (spell, style) by measured delta x frequency, swapping a style in
    through the self-replacing slots at natural windows (post-success on the leader thread, pool return, warm
    conjure), keeping the plain body when the probe measures no win (chain8 shows why); (4) the DevOps report as
    the user-visible surface. Each style keeps the guard/deopt contract; the plain body stays byte-identical.
  EVIDENCE:
  - artifacts/pgo_strategies_20260927/vm_opt_in_specializer_by_name_gil0_20260927.md
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:600-758
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:12-110
  IMPACT: The expected win scales with singleton width (~16 ns per site) and transient depth (~20 ns per frame), so
    DI-heavy user shapes gain 15-25% per creation while Melder's own narrow shapes gain 2-3%; the probe is how the
    runtime knows which it is running.
  NEXT: owner approves the story; then patch docs (compiler codegen strategies, creation context, DevOps report).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

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
STATE 2026-09-27T19:30:50Z: IN_PROGRESS. Epic remade over the June one; the exploration story is routed on the board.
Resume from the story's latest STATE line.
STATE 2026-09-27T22:34:57Z: IN_PROGRESS. Exploration story turned in; the owner's probe-selected styles direction is the
next story, pending approval. Resume from the latest note's NEXT.
STATE 2026-09-27T23:49:25Z: REVIEW. Superseded by the adaptive-creation-contexts epic; the styles story and the
design task moved there. Nothing to resume here; close on the owner's word.
STATE 2026-09-28T00:57:27Z: PARKED with the superseding epic (owner shelved the lane).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
