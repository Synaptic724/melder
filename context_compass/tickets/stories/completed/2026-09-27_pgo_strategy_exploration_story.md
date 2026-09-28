# Story: PGO strategy exploration - regeneration substrate map, strategy catalogue, measured costs, ranking

## Metadata
- Completed: 2026-09-27T22:34:08Z
- Summary: Exploration turned in on the owner's word: PGO proper measured at ~6 ns per creation on Melder-shaped
  code (tasks 0-0c), the profile-free door fold landed as the name/class warm lane (task 0d, notched 0.2.8201,
  -23..-47% per warm meld by name on the VM), the executor-hold lever dropped on evidence (task 0e), and the
  existing opt-in specializer measured by name (-14% wide8, +20% chain8) as the input to the owner's
  probe-selected-styles direction, which continues under the epic. Tasks 1-4 superseded.
- Story ID: STORY-2026-09-27-pgo-strategy-exploration
- Epic: EPIC-2026-09-27-codegen-pgo-strategies
- Status: done
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-27T19:30:50Z
- Updated: 2026-09-27T22:34:08Z

## User Narrative
As the Melder owner, I want a source-evidenced map of where the runtime can regenerate executors safely
and a catalogue of profile-guided strategies (live, optimistic, opportunistic, per existence type) with
their signals, guards, windows and measured costs, ranked, so that I can pick the first strategy to build
knowing what it costs with the optimizer off and what it can win with it on.

## Value / MRP Alignment
Discovery before build: the last PGO epic parked unstarted because no substrate map existed. The
substrate now has real windows (rebuild windows, door-held build locks, per-key-set plans, structural
snapshot); mapping them and measuring the two costs that decide everything - signal capture and
regeneration - is the smallest thing that makes the build decision honest.

## Ticket Contract
- ENTRY_GATE: the epic; this row on `attention_board.md`.
- EXECUTION_BOUNDARY: reads under the epic's boundary; VM measurement scripts outside the repo (or under
  `artifacts/pgo_strategies_20260927/`); no src edits.
- DEPENDENCIES: `src_components.md` slices for Meld Resolution Runtime, SpellCompiler and Validation
  Pipeline, Creations and SpellSpace (through the index); the June design artifact; the gauntlet.
- EXIT_GATE: the catalogue artifact with evidence pointers, VM numbers labelled directional, a ranked
  recommendation and the owner's pick recorded in the epic's Decision Log.
- FAILURE_ESCALATION: DECISION_REQUEST when two strategies rank close and the choice is a product call.

## Requirements (Functional)
- Substrate map: every seam where an executor, plan or creation context is replaced today (who calls it,
  under which lock or window, what state survives, what a rebuild costs at 29 and 300 spells).
- Signal inventory: what the doors, stores and site plans can count for free or nearly free.
- Catalogue: per strategy - signal, capture point, trigger, window, guard/deopt, existence types, cost
  off/on, expected win, risks; the June guard ladder reconciled with today's epochs and gates.
- Measurements: capture cost and regeneration cost on the persistent gauntlet (VM, directional).

## Requirements (Non-Functional)
- Evidence tier: behaviour claims cite the source read, `path:start-end` covering the logic.
- Overlay rules for any probe code; probes never enter `src/`.

## Scope Boundaries
- In scope: the map, the inventory, the catalogue, the measurements, the ranking.
- Out of scope: implementing a strategy (next story), changing the gauntlet.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner: "turn in your other shit for the melder door" (2026-09-27T22:34:08Z); the door fold
  landed and the
  remaining levers are measured; the PGO direction continues under the epic.

## Dependencies / Related Work
- tickets/epics/2026-09-27_codegen_pgo_strategies_epic.md
- artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md
- tickets/tasks/completed/2026-09-26_investigate_concurrent_first_meld_creation_context_race_task.md (rebuild windows)

## Tasks (Implementation Checklist)
- [x] Task 0 (owner-inserted): composition experiment - the ceiling per creation, ten shapes.
      tickets/tasks/completed/2026-09-27_pgo_codegen_composition_experiment_task.md (done 2026-09-27T19:43:17Z)
- [x] Task 0b (owner-inserted): composition scan of src/melder - width, depth, tree, ceiling per bucket.
      tickets/tasks/completed/2026-09-27_pgo_composition_scan_of_melder_task.md (done 2026-09-27T19:53:07Z)
- [x] Task 1 (superseded by the door fold; PGO proper parked): regeneration substrate map from source (rebuild
      window, context factory, site-plan runtime,
      door epochs, fast doors, cache generations, pool return, SpellSpace reset, revalidation).
- [x] Task 0d (owner's go on the measured proposal): meld entry cache keyed by registered name and class.
      tickets/tasks/completed/2026-09-27_meld_entry_cache_by_name_and_class_task.md
      (done 2026-09-27T22:20:17Z; notched 0.2.8201)
- [x] Task 0e: hold the compiled executor in the warm entry - dropped on evidence (self-replacing slots).
      tickets/tasks/completed/2026-09-27_hold_executor_in_warm_entry_task.md (done 2026-09-27T22:26:33Z)
- [x] Task 2 (superseded; see the epic's next story): profile-signal inventory and capture-cost probe on the gauntlet.
- [x] Task 3 (superseded; the axes carry into the epic's next story): strategy catalogue (live, optimistic,
      opportunistic, existence-type) with guards and windows.
- [x] Task 4 (superseded; specializer measured instead): regeneration-cost measurement and the ranked
      recommendation; owner's pick.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Require meaningful-finding note updates during discovery.

## Acceptance Criteria
- Catalogue artifact complete with evidence; costs measured; ranking accepted; owner's pick recorded.

## Validation / Test Plan
- Discovery only; VM probes labelled directional; nothing owner-run is claimed.

## UX / API / Data Notes
- None until a strategy is picked; any switch will be a configuration flag, default off.

## Risks / Mitigations
- Mapping from documents instead of source -> every seam claim cites the code it read.
- Measuring the wrong thing -> costs measured on the gauntlet's own lanes, not synthetic loops.

## Applicable Anti-Patterns
- [x] No strategy listed without its guard and its window.
- [x] No perf claim from agent-side runs (VM numbers labelled directional).

## Open Questions
- The epic's open questions (granularity, stable existence types, profile persistence).

## Decision Log
- 2026-09-27T19:30:50Z (owner): exploration first; strategies are the deliverable.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/pgo_strategies_20260927/ (created at task 1)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: promoted into the canonical maps when a strategy ships.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: PGO; codegen regeneration; guards; existence types.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-27T19:30:50Z
  TYPE: PLAN
  CLAIM: Task order: substrate map first (the windows decide which strategies are even possible), then the
    signal inventory with its capture-cost probe, then the catalogue, then regeneration cost and ranking.
    Entry points for task 1 from the architecture narrative: `CreationContextRebuild`, `Meld._rebuild_window`,
    `CreationContextFactory.get_or_build_for_spell`, `SitePlanOverrideRuntime` (compile lock, per-key-set
    plans), the `_fast_meld_doors`/`_door_epoch` lane, `Creations.slot_guard`, `SpellSpacePool.prepare_object`,
    `Conduit._prepare_for_pool`, `Meld._ensure_lineage_resolvable`, `CachingSystem` generations.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:874-1000
  - context_compass/system_docs/src_components_index.md:38-45
  IMPACT: Task 1 is a read of the code behind those names, not of the documents that name them.
  NEXT: open task 1 and read `creation_context_rebuild.py`, `meld.py` (rebuild window, doors) and
    `site_plan_override_runtime.py` whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T19:43:17Z
  TYPE: MEASURE
  CLAIM: Task 0 result, in one line: an ideal PGO body wins 180-540 ns per creation (14-63%), of which ~183 ns
    is the constant meld door (3 Python calls, every shape) and the rest is ~45 ns per singleton dependency
    read; the compiled executors already spend one Python call per object and ~20 ns of overhead per
    transient site, so transient-heavy shapes gain the least. Calls saved per creation: 3 Python + 1 C per
    singleton dependency. Details and the call trace in the task and the artifacts.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-27_pgo_codegen_composition_experiment_task.md
  - artifacts/pgo_strategies_20260927/vm_composition_run_gil0_20260927.md
  IMPACT: Two levers, one of them (the door) profile-free; the owner decides whether to continue.
  NEXT: owner's call: continue with task 1 on the door and singleton-read levers, or park the epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T19:53:07Z
  TYPE: MEASURE
  CLAIM: Task 0b: Melder's 373 constructors are 58% width 0, 23% width 1, 8% width 2, 9% width 3-4, 2% width
    5-8, 0% wider; depth at most 5; trees at most 17. Against task 0's model the ceiling for those shapes is
    183-320 ns per creation, 60-90% of it the constant door; PGO body specialization is worth 20-90 ns there.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-27_pgo_composition_scan_of_melder_task.md
  - artifacts/pgo_strategies_20260927/melder_composition_scan_20260927.md
  IMPACT: On real shapes the profile-free door fold is the lever; PGO proper is not justified by Melder's own
    composition. User-application shapes remain UNKNOWN.
  NEXT: owner's call: park the epic and open a door-fold task, or bring a user-application composition.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T20:01:08Z
  TYPE: MEASURE
  CLAIM: Task 0c (the one more test): shapes matching Melder's width distribution, weighted by the scanner's
    shares (58/23/8/9/2%). Bare classes: real 377 ns weighted per creation, ideal PGO body 173 ns, saved 204 ns
    (54%); by bucket the saving is 184 (w0), 212 (w1), 238 (w2), 264 (w3-4), 300 ns (w5-8). With Melder's usual
    inheritance (two-deep base chain, each `__init__` calling `super().__init__()`): real 610 ns, ideal 397,
    saved 212 ns (35%) - the constructors nearly double in cost and the relative win shrinks while the absolute
    win stays ~210 ns. In every bucket 3 Python calls are saved (the door, ~185 ns); the profile-dependent part
    is the remainder, 0-120 ns, growing with singleton width. Per 1000 creations 0.20-0.21 ms; per million 0.2 s.
  EVIDENCE:
  - artifacts/pgo_strategies_20260927/vm_melder_shaped_run_mro0_20260927.md
  - artifacts/pgo_strategies_20260927/vm_melder_shaped_run_mro2_20260927.md
  - tests/experimentation/pgo_codegen_composition_experiment.py (PGO_EXP_MRO_DEPTH, weighted summary)
  IMPACT: On a Melder-shaped codebase PGO proper is worth ~20-30 ns per creation on average; the door fold is
    worth ~185 ns and needs no profile. The squeeze for PGO is not justified by these shapes.
  NEXT: owner decides: park the epic (recommended) and open the door-fold task, or continue.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T20:14:33Z
  TYPE: MEASURE
  CLAIM: Correction of the per-singleton figure, with the attribution measured directly. `Conduit.meld`'s frame
    and fast-path prologue cost 155-195 ns per meld (conduit.py:4527-4576: ~14 loads and branches, the door
    dict.get, a 4-tuple unpack, the epoch and context guards, the executor load); the creation-context lane
    frame costs ~20 ns; the executor's own frame ~20 ns. One emitted singleton site (`spells[0]._owner_creations
    ._creations.get(sid0)` plus the None branch) costs 23 ns in isolation; a bound dict.get 15 ns; a guarded
    closed-over constant 7 ns. So PGO proper is worth 8-16 ns per singleton site, not the ~45 ns inferred from
    the composite deltas; on Melder-shaped code (~0.4 singleton sites per class) that is ~6 ns per creation.
    The profile-free levers - trimming the `Conduit.meld` prologue to the two structural guards and storing the
    executor in the door entry so the lane frame disappears - are worth ~120-170 ns per creation of every shape.
  EVIDENCE:
  - artifacts/pgo_strategies_20260927/door_and_site_attribution_20260927.md
  - src/melder/aether/conduit/conduit.py:4527-4576
  IMPACT: PGO proper on likely shapes (width 0-2): ~6 ns per creation, 1-2%. Door trims: 30-45%.
  NEXT: owner decides; recommendation unchanged - park PGO, open the door-trim task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T20:35:19Z
  TYPE: MEASURE
  CLAIM: A warm direct meld of a stored `unique` singleton costs 180 ns and makes four calls: `Conduit.meld`, the
    door dict.get, the creation-context lane, and the store dict.get (no executor frame); an ideal door entry
    holding the stored instance behind the epoch guard returns it in 21 ns (33 ns with a dict lookup by spell
    id) - about 80% less, all of it `Conduit.meld`'s prologue. A `many` object without disposal methods already
    registers nothing on creation (the solo and transient traces show no store call), so "skip tracking when
    there is no disposal" is already the emitted behaviour; only declared disposal methods add registration.
  EVIDENCE:
  - artifacts/pgo_strategies_20260927/door_and_site_attribution_20260927.md
  - src/melder/aether/conduit/conduit.py:4527-4576
  IMPACT: Recommendation to the owner: park PGO proper; one profile-free door task - precomputed fast-mode
    flag in `Conduit.meld` keeping only the epoch and context guards, the executor and (for stored uniques) the
    instance held in the door entry - worth 30-45% per creation on likely shapes and ~80% per direct singleton
    meld.
  NEXT: owner's decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T20:38:12Z
  TYPE: MEASURE
  CLAIM: Owner correction taken: users do not meld by spell id. The user-facing paths cost more, not less: for a
    width-1 object (VM, GIL disabled) `conduit.meld(spell=Cls)` is 536 ns and `conduit.meld("Name")` 533 ns
    against 372 ns for `meld(spell_id=...)`. Their call list is `Conduit.meld` -> isinstance -> `ConduitMeld.meld`
    -> isinstance -> dict.get (class or name to spell id) -> dict.get (the fast entry) -> the creation-context
    lane -> the compiled executor -> the store read -> the constructor: four Python frames and four C calls of
    dispatch (~330 ns) around a ~110 ns construction. Every previous per-creation figure in this story was
    measured on the spell-id path; on the paths users call the removable dispatch is ~250-300 ns (about half of
    a typical creation), still profile-free.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:4527-4576
  - src/melder/aether/conduit/meld/conduit_meld.py (ConduitMeld.meld)
  IMPACT: The door task's scope is the class/name entry, not the spell-id entry: one lookup keyed by the class or
    registered name straight to the compiled builder, one guard, no forwarding frames.
  NEXT: owner's decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T21:00:36Z
  TYPE: MEASURE
  CLAIM: The one-lookup entry, prototyped over the real runtime objects (real `_fast_meld_doors` entries, the
    real lane and compiled builder, the real `_door_epoch` and `_creation_context` guards, fallback to today's
    `conduit.meld` proven by bumping the epoch), against today's `conduit.meld("Name")` on the VM: solo 453 ->
    195 ns (-57%), w1_singleton 537 -> 269 (-50%), w2_mixed 683 -> 405 (-41%), w4_mixed 888 -> 592 (-33%),
    wide8_singleton 957 -> 651 (-32%), a stored unique melded directly 333 -> 96 ns (-71%). Keying by class
    gives the same numbers. Holding the compiled builder in the entry instead of the forwarding lane takes
    another 3-4 points (solo 180, -60%). Also found: melds by name or class never use `_fast_meld_doors` (only
    melds by id mint and use it); they run a separate warm route inside `ConduitMeld.meld` (two extra calls, two
    lookups) that costs the same whether or not the id entry exists (solo 454 vs 450 ns), which is where the
    ~160 ns gap between the id path and the user paths lives.
  EVIDENCE:
  - artifacts/pgo_strategies_20260927/vm_meld_entry_dispatch_run_gil0_20260927.md
  - tests/experimentation/meld_entry_dispatch_experiment.py:1-60
  - src/melder/aether/conduit/conduit.py:4527-4576
  IMPACT: The proposal is measured: 30-57% per warm creation on the shapes people write and ~70% on direct
    singleton melds, with no profile, no codegen change and no API change.
  NEXT: owner's go opens the implementation task (patch docs first: meld hot path).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T21:30:03Z
  TYPE: FACT
  CLAIM: Mailbox M0-61 (melder_0, 2026-09-27T20:29:26Z) consumed: melder_0 rewrote one test in
    tests/unit/melder/aether/test_aetheric_frame_descriptor.py (the Windows CI failure; its `_CoordinatedLock`
    lost a signal when both threads started together), test-only, no notch. The same helper is copied into 31
    other test files that melder_0 is NOT editing without the owner's approval. Rule for this lane: tell
    melder_0 before editing that file. The meld-entry cache work does not touch it.
  EVIDENCE:
  - tickets/tasks/2026-09-27_harden_frame_descriptor_cleanup_recheck_test_task.md
  - mailbox_board.md:60-70
  IMPACT: No overlap with this lane's files; noted so a later test edit in that file goes through melder_0.
  NEXT: open the meld-entry cache implementation task under this story (owner's go: "give it a shot").
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-27T22:22:47Z
  TYPE: DECISION
  CLAIM: The owner's go ("give it a shot") produced the first landed change of this lane: the name/class-keyed warm
    entry (task 0d, closed 2026-09-27T22:20:17Z). Measured after landing: `conduit.meld("Name")` 453 -> 269 ns solo,
537 ->
    350 with one singleton, 888 -> 687 at width 4, 333 -> 177 for a stored singleton; name, class and id at parity.
    Owner directions: run the tests (done, all shards green on the VM), notch (0.2.8201; melder_0 took 0.2.8202
    the same minute - owner: fine), entry in release_docs/next_version_release.md (done), keep iterating. Next
    lever: hold the compiled executor in the entry to drop the forwarding lane frame (~20 ns, the prototype's
    "another 3-4 points"), which needs the hydration swap sites read first; it touches conduit.py/spell_space.py
    again, so it lands only after melder_0's scope-exit lane (M0-63/F0-5). PGO proper stays parked on the
    numbers (task 0-0c); tasks 1-4 of this story are superseded unless the owner brings user-application shapes.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-27_meld_entry_cache_by_name_and_class_task.md
  - artifacts/pgo_strategies_20260927/vm_meld_entry_dispatch_after_change_gil0_20260927.md
  IMPACT: The story's deliverable shifted from a PGO catalogue to the measured door fold; the epic's exit gate
    ("or the epic parks with the numbers that say no") is met for PGO proper.
  NEXT: open the executor-in-entry task: read `CreationContext` and the hydrators for every in-place slot swap.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T22:27:01Z
  TYPE: DECISION_REQUEST
  CLAIM: Task 0e dropped on evidence: the executor slots are self-replacing by contract (cold -> hot on first
    execution; the opt-in specializer swaps hot -> specialized on a later call and deopts back), so a held
    executor saves ~10 ns (or ~20 on `many` roots by skipping the route door) against a kernel contract and the
    specializer. The warm lane is at its floor short of a leaner public entry shape, which is an API decision.
    Owner's call: close this story and park the epic on the numbers (PGO proper ~6 ns per creation on
    Melder-shaped code; the door fold landed), or name the next target to iterate on.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-27_hold_executor_in_warm_entry_task.md
  - tickets/tasks/completed/2026-09-27_meld_entry_cache_by_name_and_class_task.md
  IMPACT: Nothing left in this lane that measures as worth a src change.
  NEXT: owner's word.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T22:34:08Z
  TYPE: MEASURE
  CLAIM: The existing opt-in singleton specializer (`generalized_singleton_specialization_enabled`), measured by name
    after the door fold (VM, directional, off -> on): w1_singleton 352 -> 340 (-3%), w2_mixed 498 -> 490 (-2%),
    w4_mixed 695 -> 672 (-3%), wide8_singleton 781 -> 674 (-14%, the 8 store reads become guarded constants: C
    calls 9 -> 1), chain8_singleton 353 -> 424 (+20%: the guards cost more than the one site they replace, and the
    always-on selection cannot see it). This is the number behind the owner's direction: alternative codegen
    styles exist in embryo (the specializer is one), and what is missing is data-driven selection (probe, report,
    priority by measured delta) plus more styles (transient inlining), which the epic's next story owns.
  EVIDENCE:
  - artifacts/pgo_strategies_20260927/vm_opt_in_specializer_by_name_gil0_20260927.md
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:600-758
  IMPACT: PGO's per-creation win scales with singleton width and transient depth (16 ns per singleton site, ~20 ns per
    transient frame), not with Melder's own narrow shapes; user-application shapes decide, and a probe is how to
    know without guessing.
  NEXT: none in this story; the epic's next story takes the probe-selected styles.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user (owner directive)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
STATE 2026-09-27T19:30:50Z: IN_PROGRESS. Opened; task 1 (substrate map) is next. Resume from the latest task
STATE line.
STATE 2026-09-27T19:43:17Z: IN_PROGRESS. Task 0 (composition experiment) done; verdict with the owner -
continue or park.
STATE 2026-09-27T19:53:07Z: IN_PROGRESS. Task 0b (Melder composition scan) done: narrow, shallow shapes; the door
is the lever.
STATE 2026-09-27T20:01:08Z: IN_PROGRESS. Task 0c: weighted ~205 ns saved per creation, ~185 of it the door; PGO
proper ~20-30 ns.
STATE 2026-09-27T20:14:33Z: IN_PROGRESS. Attribution measured: Conduit.meld prologue 155-195 ns, lane 20 ns,
singleton site
23 ns of which PGO recovers 8-16; PGO proper ~6 ns per creation on likely shapes.
STATE 2026-09-27T22:22:47Z: IN_PROGRESS. Task 0d landed and closed (0.2.8201); next lever is the
executor-in-entry read, gated on melder_0's lane. PGO proper parked on the numbers.
STATE 2026-09-27T22:27:01Z: REVIEW. Task 0e dropped on evidence; the lane is at its floor. Owner closes or redirects.
STATE 2026-09-27T22:34:08Z: DONE. Turned in on the owner's word; the PGO direction continues under the epic.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
