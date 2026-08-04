<!-- CLOSED 2026-06-30T23:04:50Z (departed-agent cleanup) -->
- Completed: 2026-06-30T23:04:50Z
- Summary: Turned in during departed-agent cleanup (owner optimizer_0 departed); closed via tickets/tasks/completed/2026-06-30_turn_in_departed_agents_optimizer0_hope0_task.md. Prior in-file Notes preserved as the durable record; acceptance not re-verified.

# Epic: Adaptive (Profile-Guided) DI Optimizer

## Metadata
- Epic ID: EPIC-2026-06-20-adaptive-pgo-di-optimizer
- Status: in_progress
- Owner: cowork
- Agent Name: optimizer_0
- Priority: p2
- Created: 2026-06-20T16:23:42Z
- Updated: 2026-06-20T16:23:42Z
- Target Window: 2026-Q3
- Related Program/Initiative: profile-guided meld specialization (optimizer mode)

## Problem / Opportunity
Melder's edge over bottom-up DI containers is the whole-graph model available at compile time.
The runtime already ships a monomorphic inline cache with generation-guard deopt (the
`_fast_meld_doors` + `_door_epoch` fast lane) plus a per-existence specialized executor model.
The unexploited lever is profile-guided specialization: observe each application's real
resolution behavior over its lifetime, then bias meld execution toward the observed common
case, guarded so a wrong guess only costs speed, never correctness.

This was previously captured as a parked future-direction story plus a full design artifact.
The owner has now directed activation, so it is promoted to this epic. Code reality at
promotion: only the substrate exists (the `_fast_meld_doors`/`_door_epoch` lane and the static
`CachingSystem` / `CreationContext` cache seam). No optimizer doors, profiler, profile-strategy
registry, speculative codegen family, or `__optimizations__` cache exist yet. The design's
Stage 0 decider is NOT STARTED.

Owner-stated shape of the optimizer (refinement over the artifact's lead emphasis): the FIRST
profile dimension is temporal / order-of-creation -- learn which singletons are alive and in
what order over a period of time, and use that to reorder which resolution paths meld attempts
first. Reordering which candidate is tried first is correctness-safe by construction (a wrong
guess falls through to the next path; no stale read), so it sidesteps the harder guard problem
that gates "skip the lookup entirely" speculation. It is opt-in: a user enables optimizer mode
via a configuration step, the system learns, and resolution gets faster -- with zero added cost
on the default path when the mode is off.

## MRP Alignment (Most Reasonable Product)
The MRP is a runtime that gets better the longer intelligence lives in it, without ever trading
correctness for speed. It is additive and opt-in (default OFF), so it cannot destabilize the
default path, and it deepens the core capability rather than bolting on a feature. It is the
natural next rung on the existing inline-cache ladder, not a from-scratch JIT, which keeps the
build tractable and the blast radius contained behind a flag.

## Ticket Contract
- ENTRY_GATE: owner directed activation of the parked PGO story (satisfied). Substrate map
  routed as the first child lane; design artifact linked.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/meld/`
  - `src/melder/aether/conduit/creations/`
  - `src/melder/aether/spellbook/spell_compiler/` (phases 8-11 + analyzer/processor/planner)
  - `src/melder/aether/spellbook/configuration/` (opt-in flag surface)
  - `src/melder/utilities/caching_system/` (Stage 5 only)
  - `codex/context_compass/tickets/`, `attention_board.md`, `artifact_board.md`, `artifacts/`
  - Exclusions: no changes to default `ConduitMeld`/`SpellSpaceMeld` semantics; no changes to
    static cache internals; additive, flag-gated modules only.
- DEPENDENCIES:
  - `artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md`
  - `tickets/stories/backlog/2026-06-13_adaptive_pgo_di_optimizer_future_direction_story.md`
  - `tickets/tasks/2026-06-13_executor_construction_lane_trim_task.md` (trim #2 == this)
  - `system_docs/src_architecture.md`
  - `system_docs/src_components.md`
  - `system_docs/readable_src_graph.json`
- EXIT_GATE: required stories accepted; a measured, owner-run speedup on a long-lived reuse
  workload at threads>1 on 3.14t behind a default-off flag; deopt proven correct under
  invalidation; board/closure sync complete.
- FAILURE_ESCALATION: any guard-coverage ambiguity, a measured non-win at the Stage 0 decider,
  or any need to touch default-door/cache semantics is a DECISION_REQUEST to the owner before
  code lands.

## Goals (Outcomes)
- Map the optimizer substrate end to end (meld lane, creations, creation-context, phases 8-11,
  cache seam) with source evidence, so build stories start from fact not assumption.
- Make optimizer mode opt-in and zero-cost-when-off via construction-time door selection.
- Land a temporal / order-of-creation profile that reorders resolution attempts (the safe slice)
  before any present/absent skip-the-lookup speculation.
- Keep the correctness invariant absolute: a wrong speculation is slower, never wrong.

## Non-Goals (Explicit Exclusions)
- No change to default fast-lane semantics or any non-opt-in behavior change.
- No "skip the lookup entirely" speculation until the §4 guard policy is owner-approved.
- No benchmark claims without owner-run numbers on the 3.14t free-threaded target.
- No Stage 5 persistence work unless long-lived warm-start is judged worth it.

## Scope Boundaries
- In scope: profiler/observation, temporal/order profile strategy, processor (phase 9) fusion,
  speculative codegen family, guard ladder + `_door_epoch` coverage, opt-in config, optimizer
  doors, optional `__optimizations__` cache, diagnostics, measurement.
- Out of scope: default-door/runtime redesign outside the optimizer seam; static cache internals;
  mutation-research redesign; phase-scheduler redesign.

## State Transition Event
- from_state: backlog (parked future-direction story)
- to_state: in_progress
- transition_reason: owner directed activation and promotion of the parked story to an epic.

## Success Metrics
- One evidence-backed substrate map covering meld/creations/creation-context/phases 8-11/cache.
- Stage 0 decider specified as an owner-runnable micro-bench with an explicit GO/NO-GO margin.
- Default path provably unchanged when the flag is off (construction-time door selection).
- Eventual: measured end-to-end speedup on a long-lived reuse workload at threads=1/3/5 on 3.14t.

## Requirements (Functional + Non-Functional)
- Opt-in typed flag on the spellbook/runtime config surface, default OFF.
- Construction-time door selection (read the flag once when the conduit builds its door), never a
  per-meld branch -- this is what guarantees zero overhead when off.
- A marshal-safe runtime record (frozen snapshot, never a live reference) as the observe->codegen
  interface, profile artifact, and later cache payload.
- A `ProfileStrategy` registry mirroring the existing strategy-builder pattern; first strategy is
  temporal/order-of-creation (creation order + liveness-over-time).
- Profile-aware phase-9 processor strategy folding the record onto `SpellCodegenModel`.
- Preserve Python 3.14t / no-GIL correctness; guard reads stay single-int-compare discipline.

## Constraints / Assumptions
- Benchmarks are owner-run on the 3.14t free-threaded target; this sandbox is Python 3.10 and
  Melder will not import there -- agent work is read/map/design only, never a perf claim.
- All tested structures remain DAGs over Python objects.
- Spell ids are SHA256 source fingerprints, giving free per-spell uniqueness and invalidation.
- Reordering-which-call-first is sound; present/absent skip speculation needs the §4 guard.

## Dependencies / External References
- Design artifact: `artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md`
- Origin story: `tickets/stories/backlog/2026-06-13_adaptive_pgo_di_optimizer_future_direction_story.md`
- Active trim lane: `tickets/tasks/2026-06-13_executor_construction_lane_trim_task.md`
- Adjacent parked: `tickets/tasks/2026-06-13_skip_dead_overrides_plan_build_task.md`
- Related open epics: `tickets/epics/2026-06-07_optimize_meld_hotpath_epic.md`,
  `tickets/epics/2026-06-06_define_compiler_phase_artifact_directory_cache_epic.md`,
  `tickets/epics/2026-06-02_explore_topdown_compiler_strategy_harness_epic.md`

## Milestones (Track Progress)
- [ ] Milestone 1: Substrate map - meld/creations/creation-context/phases 8-11/cache mapped with
      source evidence in epic Notes.
- [ ] Milestone 2: Stage 0 decider specified - one hand-rolled guarded body + guard, owner-run
      micro-bench at threads=1/3/5 on 3.14t with an explicit GO/NO-GO margin.
- [ ] Milestone 3: Observe-only optimizer doors + runtime record (temporal/order profile).
- [ ] Milestone 4: Processor fusion + `ProfileStrategy` registry feeding `SpellCodegenModel`.
- [ ] Milestone 5: Closed loop (auto trigger + hot-swap install) with measured speedup.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-06-20-optimizer-substrate-map - read-only map of the meld lane,
      creations store-clear surface, creation-context install slot, phases 8-11, and the cache
      seam; record cacheable vs runtime-only boundaries and the §4 guard surface.
- [ ] Story: STORY-2026-06-20-optimizer-stage0-decider - hand-roll one guarded specialized body
      + guard; owner micro-benches vs the generalized resolve on 3.14t. GO/NO-GO gate.
- [ ] Story: STORY-2026-06-20-optimizer-record-and-doors - marshal-safe runtime record +
      construction-selected optimizer doors (observe only); temporal/order-of-creation profile.
- [ ] Story: STORY-2026-06-20-optimizer-processor-fusion - profile-aware phase-9 processor
      strategy + `ProfileStrategy` registry folding the record into model candidates.
- [ ] Story: STORY-2026-06-20-optimizer-speculative-family-and-guard - speculative codegen family
      + guard ladder + `_door_epoch` instance-clear coverage. GATE: deopt matrix + differential
      test.
- [ ] Story: STORY-2026-06-20-optimizer-closed-loop - automatic trigger (threshold + hysteresis)
      + hot-swap install. GATE: measured end-to-end speedup; default path unaffected.
- [ ] Story: STORY-2026-06-20-optimizer-persistence-and-diagnostics - `__optimizations__` cache
      family + diagnostics (skippable for long-lived single-run processes).

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Keep this epic and the design artifact aligned as findings sharpen.
- [ ] Task: Prevent implementation drift before the substrate map and Stage 0 decider land.
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The substrate map is recorded with evidence and a future reader can resume from it.
- The Stage 0 decider has an owner-run number that clears warmup amortization (or the epic parks
  again with that finding recorded).
- A measured, repeatable speedup on a long-lived reuse workload at threads>1 on 3.14t, behind a
  default-off flag, with deopt proven correct under mutation/transfer/cleanup/store-clear.

## Risks / Mitigations
- Risk: profiled-assumption staleness (dependency store-clear without a consumer epoch bump).
  - Mitigation: start with reordering (safe); for skip speculation, existence-class-keyed guard
    policy (design §4) gated by owner signoff before Stage 3.
- Risk: nogil shared-line traffic from richer guards.
  - Mitigation: single-int-compare discipline; reuse the existing nogil-tuned guard ladder.
- Risk: warmup overhead on short-lived processes.
  - Mitigation: opt-in, default OFF, construction-time door selection.
- Risk: shared-worktree disruption across the other active lanes.
  - Mitigation: additive, flag-gated modules only; default doors and cache internals untouched.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No implementation under this epic without owner signoff + patch-framework artifacts for
      system-impacting stages (Stages 3+).
- [ ] No perf or correctness claim from agent-side runs (3.14t benchmarks are owner-run).

## Validation / Test Approach
- Not run. This epic opens with read/map/design only; Melder will not import in the 3.10 sandbox.
- Benchmarking-first: the Stage 0 decider must clear warmup amortization before any build.
- Correctness gates for emitting/installing stages: a deopt matrix
  (mutation / transfer / cleanup / store-clear, concurrent) plus a differential test (same
  workload through default vs optimizer doors -> identical results).

## Rollout / Adoption Plan
- Map the substrate, then specify the Stage 0 decider for the owner to run.
- Build observe-only doors + record, then processor fusion, then the guarded speculative family.
- Close the loop with auto-trigger + install; add persistence/diagnostics last (skippable).
- Each stage is additive, default-OFF, independently testable, and parkable.

## Open Questions
- Profiling granularity: per spell / per (spell, conduit) / per dependency socket?
- Temporal profile shape: order-of-creation only, or also liveness-window / last-seen decay?
- Specialization trigger threshold + hysteresis to avoid specialize/deopt thrash.
- §4 guard policy per existence class (only needed once we move past reordering to skip-lookup).
- No-overrides lanes first, overrides lanes left generic?

## Decision Log
- 2026-06-20: Owner directed activation of the parked PGO story and its promotion to this epic.
- 2026-06-20: Optimizer anchored on the design artifact, with temporal / order-of-creation as the
  FIRST profile dimension (reorder resolution attempts -- the correctness-safe slice) ahead of
  present/absent skip speculation.
- 2026-06-20: Agent optimizer_0 owns the lane; first child lane is the read-only substrate map.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: retain while this lane is live; revisit if superseded or fully implemented.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-06-20T16:23:42Z
  TYPE: DECISION
  CLAIM: Promoted the parked adaptive-PGO optimizer story to this epic per owner direction.
    Optimizer is anchored on the design artifact, refined so the first profile dimension is
    temporal / order-of-creation used to reorder which resolution paths meld tries first (the
    correctness-safe slice), ahead of present/absent skip-the-lookup speculation.
  EVIDENCE:
  - artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md:1-391
  - tickets/stories/backlog/2026-06-13_adaptive_pgo_di_optimizer_future_direction_story.md:1-90
  IMPACT: Establishes the active execution vehicle for the optimizer and sequences the safe slice
    first, deferring the §4 guard problem to a later, gated stage.
  NEXT: run the read-only substrate map (meld/creations/creation-context/phases 8-11/cache) and
    record findings here before any build.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-20T16:23:42Z
  TYPE: FACT
  CLAIM: At promotion only the substrate exists: the `_fast_meld_doors` + `_door_epoch` inline
    cache lives in the meld lane and spell/creation-system, and the static `CachingSystem` /
    `CreationContext` cache seam exists. No optimizer doors, profiler, `ProfileStrategy`
    registry, speculative codegen family, or `__optimizations__` cache are present; Stage 0 is
    not started.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py
  - src/melder/aether/conduit/meld/spellspace_meld.py
  - src/melder/aether/conduit/meld/meld.py
  - src/melder/aether/spellbook/spell.py
  - src/melder/aether/spellbook/spellbook_creation_system.py
  IMPACT: Build stories start from substrate-extension, not greenfield; reduces risk and scopes
    the first lane to mapping + the Stage 0 decider.
  NEXT: map the install slot (`CreationContext`) and the store-clear surface (`Creations`) that
    the guard work will eventually depend on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-20T16:32:53Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Owner requested a full MRP pass over the profile-strategy option space before building.
    Profile menu (each = a future ProfileStrategy): P1 hotness/call-frequency (gate what is worth
    specializing); P2 temporal/order-of-creation (reorder which resolution paths meld tries first);
    P3 dependency-presence (reused-vs-constructed per socket -> short-circuit resolution); P4
    existence/scope-stability (does the singleton truly persist; classify deps for guard choice);
    P5 monomorphism/shape (mono / poly<=K / megamorphic -> inline / PIC / pin generic); P6
    override-usage (no-overrides-first; leave override lanes generic); P7 co-occurrence/subgraph
    path (fuse subtree construction into one straight-line body); P8 value/argument profiling
    (recurring inputs -> partial const-fold; low EV for DI); P9 concurrency/contention (nogil
    lock-mode specialization; ties to executor_construction_lane_trim t3/t5); P10 teardown/
    store-clear timing (deopt driver; informs guard option A/B/C); P11 deopt-rate feedback
    (hysteresis, demote chronic deopters). Cross-cutting knob: granularity = per spell / per
    (spell,conduit) / per dependency socket.
  EVIDENCE:
  - artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md:58-124
  - artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md:211-236
  - system_docs/src_architecture.md:830-872
  IMPACT: Defines the option space the MRP must choose from; sequences correctness-safe value
    ahead of the hard guard problem.
  NEXT: owner picks the v1 profile set + granularity + the Stage-0 decider body to benchmark.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-20T16:32:53Z
  TYPE: DECISION_REQUEST
  CLAIM: Correctness tiers for specialization, increasing EV and risk: Tier 0 REORDER (change
    attempt order; no guard; cannot be wrong) [P2, parts of P7]; Tier 1 SOUND SHORT-CIRCUIT
    (replace full resolution with a cheap LIVE presence-confirm `creations.get_creation(id) is not
    None` + direct return, deopt on miss; re-reads live so always correct) [P3 option C, mono P5];
    Tier 2 GUARDED SKIP (eliminate the live check via epoch / store-generation guards; the design
    §4 problem; needs owner-approved guard policy + nogil care) [P3 options A/B, full PIC, P8, P9].
    Recommended MRP v1: prove the full pipeline (construction-selected optimizer doors -> marshal-
    safe runtime record -> ProfileStrategy registry -> phase-9 fusion -> re-emit -> hot-swap
    install/deopt) on Tier 0 + Tier 1 ONLY, gated by P1 hotness + P11 deopt-feedback + P6
    no-overrides-first, with P4/P10 as observation feeding the later guard decision. Defer Tier 2
    (P3 A/B), full polymorphic-shape cache (P5/Stage 5), subgraph fusion (P7), concurrency
    specialization (P9); drop/park value profiling (P8). Crux tradeoff: pure Tier-0 reordering is
    safest but may be too low-EV to clear Stage-0 warmup; Tier-1 presence-confirm is BOTH sound and
    expected-high-EV (skips validation/dispatch/existence-routing, keeps one live dict-get), so the
    MRP should center on Tier 1. EV numbers are UNKNOWN until the owner runs the Stage-0 decider on
    3.14t.
  EVIDENCE:
  - artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md:81-109
  - artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md:247-281
  IMPACT: Picks a correctness-safe, measurable, extensible v1 that de-risks the §4 guard problem by
    deferring it; the registry/record/door architecture extends to every deferred profile without a
    rewrite.
  NEXT: get owner decisions: (1) v1 profile set, (2) profiling granularity, (3) which tier body to
    hand-roll for the Stage-0 GO/NO-GO bench.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-20T16:33:40Z
  TYPE: FACT
  CLAIM: The warm singleton fast-meld-door hit path is already minimal: one `_fast_meld_doors`
    dict-get, a 4-field live guard ladder (meld-hooks empty, `_door_epoch` int compare, context
    identity, spellbook validation flag), one live executor-slot read, and one emitted-executor
    call returning (instance, created). So the optimizer's headroom is NOT the door wrapper -- it
    is (a) how much leaner a specialized singleton-reuse body is vs the generalized no-overrides
    emitted executor invoked at the door, and (b) multi-thread shared-line/contention cost (code
    cites measured pure-door inflation 2.6x/4.2x at threads=3/5). Per warm meld the saving is a
    handful of ops, not a dozen function calls; the "dozen calls" magnitude is a cold-resolve or
    subgraph-fusion (P7) phenomenon.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:219-276
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:164-252
  IMPACT: EV is workload- and thread-dependent and UNVERIFIED until the Stage-0 decider runs on
    3.14t; whole-app speedup is Amdahl-bounded by how meld-bound the workload is (I/O-bound apps
    trend ~0; meld-bound / long-lived / multi-thread is where a real percentage lives). Sets
    honest expectations before any build.
  NEXT: when the substrate-map story runs, read the generalized vs solo emitted no-overrides
    executor bodies to quantify the per-call op delta a Tier-1 body would remove.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-20T16:33:40Z
  TYPE: FACT
  CLAIM: The runtime ALREADY does check-if-exists-before-create for every singleton existence
    class, so there is no redundant-construction waste for the optimizer to remove. The emitted
    no-overrides executor runs double-checked-locking reuse per singleton step: instance =
    `_get_existing_creation(...)`; if None, take the store lock, re-check, then construct +
    `add_creation`. `_get_existing_creation` returns `creations.get_creation(spell_id)` (a
    `_creations` dict-get) for unique / unique_per_conduit / _cluster / _lineage / _spell_space;
    `many` always constructs by contract.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:935-966
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1342-1377
  - src/melder/aether/conduit/creations/creations.py:269-278
  IMPACT: Re-justifies the optimizer premise. Its value is NOT avoiding construction (already
    avoided) but trimming the reuse-lookup machinery around the existing check on the warm path.
    That is a small, workload/thread-dependent win, so the optimizer is only worth building if
    Stage-0 proves a leaner singleton body beats the current DCL reuse by a margin clearing
    warmup; otherwise it stays parked. The cheap correct lever is existence binding (ensure
    expensive spells use a reuse existence class, not `many`).
  NEXT: offer owner an existence-binding audit (hot/expensive spells on `many` that could reuse)
    as the actually-worth-it action; reserve the optimizer for measured warm-path machinery cost.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-20T17:07:12Z
  TYPE: FACT
  CLAIM: Substrate map (generalized codegen family) read. Structure: CodegenCreationSystem.build
    reads phase-9 model + phase-10 plan, discovery picks a family (solo / many_only / generalized
    / fallback), the family runs ordered CodegenCreationFamilyStep steps over a family-local
    state, and publishes one SpellCodegenCreation. Generalized is MANIFEST-FIRST + LAZY: step 1
    builds a marshal-safe manifest (primitives/tuples/dicts only: route_key, root_spell_id,
    no_overrides {steps_rows, transient_schema, executor_signature}, overrides {plan_rows,
    plan_signature, targets_by_spec}); step 2 publishes COLD doors (closures over manifest+root
    spell) into the executor slots with code objects None and ZERO compile/exec at conjure. First
    meld hydrates once (DCL under a lock) via hydrate_creation_executors -> build_runtime_rows
    (slotted CodegenStepRuntimeRow) -> row-driven emit through the process-wide factory cache ->
    wrap in route-keyed CreationContext doors -> HOT-SWAP into spell._creation_context slots; later
    melds re-read the slot per call and run the hot door. Same hydrator serves live
    (PlanBindingResolver) and cache-load (SpellbookBindingResolver) -- one assembly program, two
    callers. The emitted no-overrides body is already a FLATTENED straight-line per-step
    construct-or-reuse ladder for the whole subgraph (instance_0..N, each _get_existing_creation ->
    DCL -> construct -> register).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:60-127
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/generalized_codegen_creation_strategy.py:29-92
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/manifest/generalized_manifest.py:37-142
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:129-284
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:860-966
  IMPACT: Most of the optimizer's "NEW" infrastructure already exists in spirit, which lowers
    build cost/risk: (1) the manifest IS the design's marshal-safe runtime record -- add observed
    fields (reuse/construct counts, creation order, hotness) behind a manifest_version bump; (2)
    lazy-door hydrate + `_swap_hot_doors` IS the install/deopt primitive (re-specialize = rehydrate
    a biased manifest + swap slot + bump `_door_epoch`); (3) the SpellCodegenStrategy/Builder +
    CodegenCreationFamilyStep pattern is the additive extension seam -- an "optimized" family is a
    drop-in selected by discovery at construction time (zero cost when off); (4) hash_codegen_
    signature / plan_signature already give the polymorphic variation key for the __optimizations__
    cache, which can reuse the manifest-codec pattern; (5) construction is already a flattened step
    ladder, so the real lever is PRUNING/specializing that ladder for the observed-common case
    (collapse always-present singleton steps to direct reads; reorder via the manifest step order),
    not building fusion from scratch.
  NEXT: Stage-0 decider should hand-roll a pruned single-step singleton body emitted in a throwaway
    "optimized" family compiler and bench vs the generalized hot door at threads 1/3/5 on 3.14t.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-20T17:35:20Z
  TYPE: FACT
  CLAIM: Deep read of the no_overrides emit settles the re-walk question and corrects an earlier
    under-claim. The emitted step-plan executor builds `instance_results = {}`, walks EVERY step
    block in order, then `return instance_results[root_instance_key]`. There is NO root-present
    early-return. So every warm meld of a depth>1 graph re-resolves every dependency step
    (creations-target routing + `_get_existing_creation` + instance_results dict write), even when
    the root singleton is already present and none of its deps are needed. The fast-meld-door is
    lean but it CALLS this full-ladder executor, so warm deep-graph melds carry real repeated
    per-step cost that scales with graph depth/width -- the warm path is lean only for solo/shallow
    graphs. Two lean patterns ALREADY exist in the emitter and are the templates to extend: (a) a
    transient unrolled body for all-`many` + no-register plans emits straight-line locals
    (v0..vN, direct call targets, NO get_existing / lock / dict / register); (b) the inlinable-
    common-shape path emits a direct `spell.spell(**deps)` construct call for plain single-dep
    callable steps. The reuse path still routes through `_get_existing_creation` + the
    instance_results dict.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:652-705
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1464-1630
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:488-502
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:547-649
  - src/melder/aether/conduit/meld/conduit_meld.py:263-276
  IMPACT: There IS common warm-path headroom after all -- any non-leaf (depth>1) graph re-walks its
    full dependency ladder on every meld. That is the target, and it scales with depth.
  NEXT: see the ranked no_overrides optimization ideas below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-20T17:35:20Z
  TYPE: PLAN
  CLAIM: Ranked no_overrides hot-path optimizations the profiler would unlock (all profile-gated;
    guards are sound live present-confirms, never stale):
    A. ROOT-PRESENT SHORT-CIRCUIT (biggest, common). Emit a top guard before the ladder:
       `r = creations.get_creation(root_id); if r is not None: return r`, for singleton/per-conduit
       roots observed usually-present. Collapses a warm depth-N meld from N step blocks to one
       lookup. The guard is always safe; profile only decides which roots are worth it (hot +
       usually-present).
    B. LOCALS-BASED UNROLLED SINGLETON BODY. Extend the existing transient unrolled-locals template
       to observed-present singleton reuse with present-confirm guards; drop the instance_results
       dict for stable shapes.
    C. INTERIOR DEAD-DEP PRUNING. For cold/`many` roots that must construct, reduce interior
       always-present dep steps to inline `get_creation` reads (skip routing block + None branch +
       lock + dict write for those steps).
    D. HOIST CREATIONS-TARGET ROUTING. Hoist the shared container selection once instead of
       per-step when most steps resolve against the same conduit/owner store.
    E. WIDEN UNROLL ELIGIBILITY. Profile arity/shape to extend beyond CALL8 and to route
       effectively-constant singleton graphs through an unrolled shape.
    F. DROP the dead root-missing check on proven bodies (minor).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:691-705
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1041-1097
  IMPACT: Magnitude scales with graph depth: real for deep graphs (A collapses N->1 on the common
    warm path), small for solo/shallow. "How common" == the graph-depth / existence distribution
    across real spells, which is exactly the profiler's first output. Build cost is low because A/C/F
    are emit tweaks and B/E reuse the existing transient-unroll + inlinable-shape machinery.
  NEXT: read the manifest_no_overrides hydration runtime + the lane-plan builder (planner) to see
    where always-present candidates would be marked and how the factory/code cache supports
    warm-start; then sketch the root-present short-circuit emit concretely (before/after).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-20T17:55:00Z
  TYPE: CORRECTION
  CLAIM: CORRECTS the 17:35 FACT and RETRACTS PLAN-idea-A. The root-present short-circuit ALREADY
    EXISTS -- not in the codegen step executor, but one layer up in the shared CreationContext door
    template (`creation_runtime_door_compiler.py` `_build_no_overrides_lines`). That door is exactly
    what the slot `CreationContext._no_overrides_executor` holds; it returns `(instance, created)`
    and WRAPS the inner step-plan executor. For EVERY singleton route -- unique, unique_per_conduit,
    spellspace, unique_per_conduit_lineage, unique_per_conduit_cluster -- the emitted door body is:
      creation = <store>.get_creation(_spell_id)
      if creation is not None: return creation, False         # ROOT-PRESENT SHORT-CIRCUIT (exists)
      with <lock>: creation = <store>.get_creation(_spell_id)  # DCL re-check
                   if creation is None: instance = _no_overrides_executor(...); return instance, True
                   return creation, False
    So a warm meld of a present singleton root returns after ONE get_creation and NEVER calls the
    inner step-plan executor. The inner re-walk (the body with no root early-return) is real but is
    only REACHED when the door does not gate: (1) the root is `many`/transient -- the `many` door
    route calls the inner executor UNCONDITIONALLY every meld (no get_creation gate), or (2) a
    singleton root on its COLD first meld (inside the lock). My earlier "every warm depth>1 meld
    re-walks the ladder" was therefore WRONG for singleton roots: those are already O(1) at the door.
    Solo confirms the model -- the solo inner executor is construct-only (no existence check), which
    is only correct because the door gates existence above it.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:600-628
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:542-599
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:629-700
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:528-541
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:176-181
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:256-282
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:196-251
  - src/melder/aether/conduit/meld/conduit_meld.py:121-435
  IMPACT: The genuinely common WARM re-walk in the no_overrides path is exclusively `many`/transient
    ROOTS that depend on now-present singletons -- a MIXED plan. The `many` door route always calls
    the inner executor, and a mixed plan is excluded from the lean transient-unrolled path (gated to
    ALL-`many`, no-register). So those melds re-do, per singleton dep, per call: store routing +
    existence-mode branch + get_creation + instance_results dict write. Singleton roots (even mixed)
    are NOT in scope -- the door gates them; only their cold first meld walks. All-`many` roots are
    already lean (transient unroll). Headroom concentrates on ONE shape: many-root-over-present-
    singletons.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-20T17:55:00Z
  TYPE: PLAN
  CLAIM: REVISED ranked no_overrides hot-path ideas (supersedes the 17:35 A-F list):
    1. (PRIMARY) LEAN INTERIOR READS FOR MANY-ROOT-OVER-SINGLETONS. Widen the transient-unrolled
       emitter to accept singleton deps that profiling marks always-present: emit
       `vK = <hoisted_store>.get_creation(dep_id)` for each present-singleton dep in place of the
       per-step _get_existing_creation + route block + dict write, keep direct construct for the
       `many` steps, drop instance_results. Guard = one present-confirm over the marked deps; deopt
       to the generic step-plan executor on any miss. This is the ONLY common warm re-walk and it is
       exactly P3 (dependency-presence) x P4 (existence-stability) x P2 (temporal/order). Fuses old
       C+E, correctly retargeted OFF singleton roots and ONTO many roots.
    2. HOIST CREATIONS-TARGET ROUTING once when the inner steps share a store (helps the many-root
       cold build and the #1 warm re-walk). (old D)
    3. COLD-PATH BUILD COST. Widen inlinable-common-shape arity (CALLN) so first-meld construction
       (every singleton's cold meld; every churned spell-system) emits direct calls. Matters for
       high-churn / many-short-lived-systems workloads, not steady-state singletons. (old E recast)
    4. (DEFERRED, Tier-2) SINGLETON-ROOT WARM SHAVE. The door's get_creation is the correctness gate
       vs store-clear; removing it (cache the instance in the conduit fast-door) needs a store/
       teardown-generation guard -- the section-4 hard problem. Tiny win, hard guard -- last.
    RETRACTED: old idea A (root-present short-circuit) -- already implemented at the door for all
    singleton routes. old idea F (drop dead root-missing check) -- inner only runs on the construct
    path, so the check is not on any warm singleton path; negligible.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:342-401
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1342-1404
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:528-541
  IMPACT: Narrower but correct: the win is real where the workload melds transient/request-scoped
    roots over app-lifetime singletons (a very common DI shape), and ~zero where the workload is
    steady-state singletons (already door-gated O(1)). "How common" == the share of hot roots whose
    existence is `many` AND whose deps are stable singletons -- a direct profiler readout
    (P1 x P2 x P3 x P4). The profiling MECHANISM spans all three families (it classifies every
    root); the realized speedup concentrates on the many-root-over-singletons slice.
  NEXT: read the lane-plan builder (planner) + many_only manifest to see where step existence-mode +
    a per-dep "always_present" mark would attach, and sketch the widened-unroll emit (before/after)
    for one many-root-over-two-singletons example.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-20T18:08:00Z
  TYPE: FACT
  CLAIM: Answers the user question "is generalized skipping disposal tracking for `many` spells with
    no disposal method?" -- PARTIALLY, and there is an easy residual win. The disposal flag IS known
    statically (`spell.has_disposal_methods`, threaded as the `step_has_disposal_methods` namespace
    tuple) and IS used by all three families, but they specialize it differently for a `many` step:
      - solo (no-disposal many): emits `return call_target()` (fast-transient) or
        `instance = call_target(); return instance` -- NO lock, NO register, NO branch.
      - many_only (no-disposal many): COMPILE-TIME gate `if plan_step.spell.has_disposal_methods:`
        wraps the lock+register, so a non-disposal many step emits just construct + dict-store --
        NO lock, NO register, NO branch.
      - generalized (no-disposal many): emits, EVERY meld, `with creations_N._lock:` UNCONDITIONALLY
        (line 822) wrapping a RUNTIME `if has_disposal_methods_N:` (line 1006). For a non-disposal
        many step that compiles to `with lock: if False: pass` -- it acquires/releases the creations
        lock and evaluates a compile-time-known branch on every meld, for nothing.
    So generalized carries a residual, removable per-meld cost on every non-disposal `many` interior
    step that solo and many_only already avoid. Under NOGIL this is not micro: an uncontended lock
    still costs atomics/barriers, and a CONTENDED creations lock (concurrent melds on one conduit
    store) serializes -- a needless serialization point on the hot path.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:814-830
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1004-1020
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:844-874
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:95-121
  IMPACT: Easy, SOUND, NON-speculative win (no PGO needed). For the generalized many step either:
    (a) MINIMAL -- move the lock INSIDE the disposal branch:
        `if has_disposal_methods_N: with creations_N._lock: add_many_creations(...)`
        (keeps the single shared body + code-object sharing; just stops taking the lock for
        non-disposal many), or
    (b) FULLER -- lift to a compile-time `if plan_step.spell.has_disposal_methods:` gate like
        many_only (leanest; emits zero lock/branch/register for non-disposal many; slightly less
        code-object sharing across disposal shapes).
    Both are correctness-preserving: a non-disposal many is never registered, so the lock was never
    needed. INDEPENDENTLY SHIPPABLE -- candidate for its own static-codegen task, separate from the
    PGO epic. Needs owner signoff + 3.14t benchmark before any source edit (no sandbox import).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-20T18:25:00Z
  TYPE: DECISION
  CLAIM: APPLIED the minimal disposal-lock fix to the generalized `many` step (owner-approved in
    chat: "do the if and then the lock after"). Moved the creations lock from UNCONDITIONAL (wrapping
    a runtime disposal branch) to INSIDE the disposal branch, so a non-disposal `many` step takes no
    lock per meld. Two emit sites changed in
    generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:
      - `_append_step_resolution_source` many branch: removed the unconditional
        `with creations_N._lock:`; now calls `_append_step_register_source` at base step indent.
      - `_append_step_register_source` many branch now emits:
            if has_disposal_methods_N:
                with creations_N._lock:
                    creations_N.add_many_creations(...)
    Docstring updated to state the many branch emits its OWN disposal-gated lock while singleton
    branches still rely on a caller-emitted lock. Behavior unchanged for disposal-bearing many;
    non-disposal many no longer locks. Single shared emitted body preserved (runtime branch kept;
    the flag is spell-static).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py (`_append_step_resolution_source` many branch; `_append_step_register_source` many branch + docstring)
  VERIFICATION: Standalone compile + behavior check of the emitted step block
    (outputs/verify_many_lock.py, sandbox py3.10): emitted source compiles; non-disposal many ->
    lock enters 0 / registered 0; disposal many -> lock enters 1 / registered 1. This checks the
    GENERATED-SOURCE shape only. The Melder suite imports under 3.14t and is owner-run -- NOT run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-20T18:25:00Z
  TYPE: FACT
  CLAIM: AUDIT of generalized for the SAME problem class (compile-time-known facts re-evaluated at
    runtime / unconditional warm-path work). Findings:
    1. (TOP FOLLOW-UP -- same class, and on the WARM path) The singleton reuse read emits
       `instance_N = _get_existing_creation(spell=spell_N, creations=creations_N, existence=existence_N)`.
       `_get_existing_creation` branches on `existence` at runtime, but existence is compile-time
       known per step, and for EVERY singleton existence (unique, unique_per_conduit, cluster,
       lineage, unique_per_spell_space) its body reduces to exactly `creations.get_creation(spell_id)`.
       So each warm interior reuse read pays a helper-call frame + a `spell.spell_id` attr read + an
       existence branch ladder for a result identical to an inline
       `creations_N.get_creation(spell_id_N)` (spell_id_N is already a local). Inlining is provably
       equivalent (the `many` arm of the helper is never reached from a singleton step) and lands ON
       the many-root-over-singletons warm re-walk that is this epic's primary target. Bigger than the
       lock fix; warrants its own signoff.
    2. (vestigial, follows from #1) `_get_existing_creation`'s `if existence is Existence.many:
       return None` arm is dead in practice (a many step never calls the helper); and
       `existence_N = step_existences[N]` becomes unused for singleton steps once #1 inlines the read.
    CLEAN (checked -- NOT problems): static creations-target routing emits a fixed path from
    compile-time target_kind (no runtime target branch); ALL singleton locks sit INSIDE
    `if instance_N is None:` so they are construct-path-only and never taken on the warm/present path;
    after the many fix there is NO remaining unconditional warm-path lock in the generalized
    no_overrides emit; the generic `_construct_spell_instance` recipe read is construct-path-only
    (common shapes already inline a direct call).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1354-1389
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py (`_append_step_resolution_source` singleton branches call the helper for the warm read; `_append_step_creations_target_source` static routing is clean)
  IMPACT: One more same-class win remains and it is the most valuable (per-dep, on the warm reuse
    path); recommend as the next applied change after signoff, with minor vestigial cleanups
    following. No other unconditional warm-path costs found in the generalized no_overrides emit.
  NEXT: on signoff, inline the singleton reuse read (replace the `_get_existing_creation` call with
    `creations_N.get_creation(spell_id_N)`) and drop the now-dead `existence_N` / helper `many` arm.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-20T20:11:15Z
  TYPE: DECISION
  CLAIM: Per owner ("each ticket is fine"), the two static-codegen trims surfaced by this epic's audit
    are split into their own standalone tickets (NOT nested under the PGO epic):
    - tickets/tasks/2026-06-20_generalized_many_disposal_lock_hoist_task.md (APPLIED; status review)
    - tickets/tasks/2026-06-20_generalized_singleton_reuse_read_inline_task.md (draft; awaiting go)
    Both are static phase-11 emit trims that consume existing discovery truth (SpellRuntimeRecord
    spell_id+existence; plan_step.existence); they are NOT the profile-guided work and need no profiling.
    Confirmed the canonical resolution data structure the owner pointed to: SpellRuntimeRecord
    (artifact_processor/data/spell_runtime_analysis.py) holds per-spell_id existence + call_target +
    disposal + spell-kind, keyed in SpellRuntimeAnalysis.records_by_spell_id and published to
    model.spell_runtime_shape (phase 9); the bigger PGO marks (always-present singleton dep, order)
    attach to model.instance_shape (SpellOccurrenceInstanceAnalysis: shared_spell_ids,
    canonical_occurrences) + order_shape + existence_occurrence_shape -- all already on the artifact.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-06-20_generalized_many_disposal_lock_hoist_task.md
  - codex/context_compass/tickets/tasks/2026-06-20_generalized_singleton_reuse_read_inline_task.md
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_runtime_analysis.py
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:54-102
  IMPACT: Keeps this epic focused on the profile-guided optimizer; the static trims ship independently,
    and the PGO marks have a confirmed home on existing phase-9/10 model sections (no new discovery).
  NEXT: execute the inline task on owner go.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when sequencing, scope boundaries, or the guard/profile model change.
- Reference story/task evidence and the design artifact instead of duplicating tactical logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
The parked adaptive-PGO optimizer story is now this active epic. The optimizer is opt-in,
default-OFF, construction-time-door-selected profile-guided specialization of the meld path,
riding the existing `_fast_meld_doors`/`_door_epoch` + hot-swap/deopt machinery. The owner's
refinement: lead with a temporal / order-of-creation profile that reorders which resolution
paths are tried first (correctness-safe), before any present/absent skip-the-lookup speculation
(which is gated on the design §4 guard policy). Only the substrate exists today. First lane is a
read-only substrate map (meld/creations/creation-context/phases 8-11/cache); next is the Stage 0
decider micro-bench, which the owner runs on the 3.14t free-threaded target.
