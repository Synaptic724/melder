# Story: Adaptive (Profile-Guided) DI Optimizer — Future Architectural Direction

## Metadata
- Story ID: STORY-2026-06-13-adaptive-pgo-di-optimizer
- Epic: EPIC-2026-06-20-adaptive-pgo-di-optimizer
- Status: promoted (activated as EPIC-2026-06-20-adaptive-pgo-di-optimizer)
- Owner: codex
- Agent Name: compiler_strategy_0
- Priority: p3
- Created: 2026-06-13T12:30:00Z
- Updated: 2026-06-20T16:23:42Z

## User Narrative
As the Melder runtime serving long-lived processes (persistent runtime, FasterAPI servers,
the always-on intelligence substrate), I want an **opt-in optimizer that learns each
application's real resolution behavior and re-specializes meld executors toward the observed
common case**, so that the longer a process runs the faster its hot meld paths get — without
ever trading correctness for speed.

This is a **philosophy / direction** ticket: it records what the optimization sweep found, why
the conventional levers are exhausted, and the one genuinely unexploited lever that is unique
to a top-down compiler with a whole-graph model. It is intentionally parked. The current
setup/runtime is in good shape and the owner is satisfied; this exists so the finding is not
lost and the extension path is ready when it is worth pursuing.

## Value / MRP Alignment
Melder's edge over bottom-up DI containers is the **whole-graph model available at compile
time**. Bottom-up containers resolve lazily and cannot reason about lifetime ordering, so they
cannot speculate safely. Melder can: it already emits per-existence specialized executors and
already runs a generation-guarded inline cache on the meld door. Profile-guided specialization
is the natural next rung of that same ladder, and it pays off precisely where the product
lives — **persistent, long-running processes** — which is the mission's center of gravity, not
a side feature. It is MRP-aligned because it is additive and opt-in: it cannot destabilize the
default path, and it deepens the core capability (a runtime that gets better the longer
intelligence lives in it) rather than bolting on a feature.

## Philosophy (why this, why now-as-direction-not-build)
- The cheap and medium optimization wins in the setup/compile pipeline are **measured to be
  gone** (see Findings notes). Continuing to micro-cut already-optimized code is negative EV.
- The remaining real lever is not "remove calls" but "**reorganize them under speculation**":
  observe, specialize to the common case, guard, deopt on a wrong guess. This is the JIT /
  inline-cache playbook (CPython PEP 659, V8 ICs) applied one layer below the interpreter, at
  the DI-resolution layer the interpreter's specializer is blind to.
- The non-negotiable invariant: **a wrong speculation costs speed, never correctness.**
- It is direction-not-build because (a) the owner is satisfied with current performance, (b) it
  is a subsystem with a real (if narrow) new correctness problem, and (c) caching already
  amortizes the cold/setup costs, so the value is specifically in the long-lived runtime regime,
  which can be pursued deliberately later.

## Findings That Motivate This (the sweep, condensed)
Recorded as evidence-backed notes (see Notes section). Summary:
1. Phases 1-10 logic is tapped out (prior pass cut P8/9/10 ~5-7x); residual redundancies are
   micro and not worth the readability/risk cost.
2. PhaseScheduler dispatch is already optimal (chunk-granularity sweep showed no win; the
   workers==1 inline fast-path was already tried and reverted for sound async-contract reasons).
3. Multi-worker conjure scaling is capped by genuinely serial frame-wide phases 5-7 plus mild
   plan-group contention; the one parallelizable slice (P5 steps 4-5) is cold-only and thus
   amortized away by the cache — not worth it — and carries a builder reachability-memo race.
4. The solo P11 emitted executor is irreducible (capped out).
5. The runtime already ships the exact machinery a profile-guided optimizer needs: a
   generation-guarded inline cache (`_fast_meld_doors` + `_door_epoch`), a hot-swap install
   primitive, and deopt-to-generic-lane on guard miss — all nogil-tuned.

## Ticket Contract
- ENTRY_GATE: This story is parked. Activation requires: owner decision to pursue + a resolved
  §4 guard policy (see design doc) + an active board row + child tasks.
- EXECUTION_BOUNDARY: Research/design only while parked. No edits to meld/codegen/cache/config
  source under this story until activated and patch-framework-gated.
- DEPENDENCIES: Design artifact (Artifact Links). Existing fast-door + `_door_epoch` machinery.
- EXIT_GATE: For eventual closure, requires the §7 measurement gate to pass (speculated lane
  beats current fast lane at threads=1/3/5 on 3.14t by a margin clearing profiler warmup) and
  the §4 guard policy implemented behind a default-off flag.
- FAILURE_ESCALATION: If activated, any guard-coverage ambiguity or measured non-win is a
  DECISION_REQUEST back to the owner before code lands.

## Requirements (Functional) — directional, not committed
- Opt-in config flag on `SpellbookConfiguration` (default OFF).
- Per-call-site profiler recording reuse-vs-construct outcomes during a learning window.
- Specialization decision + re-emit of a leaner guarded executor, installed via the existing
  door hot-swap + epoch bump.
- Extended guard ladder covering the profiled assumption (the new correctness surface).

## Requirements (Non-Functional)
- Default path unchanged and unaffected when the flag is OFF.
- Guard cost must stay nogil-friendly (single-int-compare discipline of the existing lane).
- Wrong speculation must deopt, never miscompute.

## Scope Boundaries
- In scope (of the eventual work): profiler, specialization policy, re-emit, extended guard,
  config flag, measurement.
- Out of scope: changing default fast-lane semantics; any non-opt-in behavior change; building
  the "known-present unique" speculation without solving its store-clear guard.

## State Transition Event
- from_state: (new)
- to_state: draft (backlog)
- transition_reason: Finding captured as durable direction; owner satisfied with current state,
  so the work is parked rather than scheduled.

## Dependencies / Related Work
- Design doc: `codex/context_compass/artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md`
- Related closed lanes: `executor_construction_lane_trim`, `phase10_solo_and_many_only_discovery`.

## Tasks (Implementation Checklist)
- [ ] (deferred) Resolve §4 guard-coverage policy with owner.
- [ ] (deferred) Hand-roll one speculated body + guard; micro-bench vs current fast lane.
- [ ] (deferred) If win clears warmup, scope profiler + re-emit + config flag as child tasks.
- [ ] Enforce Ticket Microcycle across all linked tasks (when activated).

## Acceptance Criteria
- (For eventual activation/closure) A measured, repeatable speedup on a long-lived reuse
  workload at threads>1 on 3.14t, behind a default-off flag, with deopt proven correct under
  invalidation (mutation, transfer, cleanup, store-clear).

## Validation / Test Plan
- Benchmarking-first: micro-bench the speculated lane vs `_fast_meld_doors` lane at
  threads=1/3/5 on the native free-threaded interpreter before any commitment to build.
- Correctness: deopt tests for each invalidation chokepoint, including the dependency
  store-clear gap identified in design §4.

## UX / API / Data Notes
- Single opt-in config property; emits a cache item; "the more it runs, the faster it goes."

## Risks / Mitigations
- RISK: profiled-assumption staleness (dependency store-clear without consumer epoch bump).
  MITIGATION: existence-class-keyed guard policy (design §4) — transient needs no guard,
  structurally-tied shared deps use multi-spell epoch, independently-clearable deps use a cheap
  presence-confirm; store-generation counter only if measured necessary.
- RISK: nogil shared-line traffic from richer guards. MITIGATION: keep single-int-compare
  discipline; reuse the existing nogil-tuned guard ladder.
- RISK: warmup overhead on short-lived processes. MITIGATION: opt-in; off by default.
- RISK: shared-worktree disruption. MITIGATION: additive, flag-gated modules only.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No implementation under this story without owner signoff + patch-framework artifacts.

## Open Questions
- Guard policy per existence class (design §4) — confirm hybrid or pick uniform.
- Acceptable to add a `Creations` store-generation counter on hot store ops?
- Profiling granularity: per spell / per (spell, conduit) / per dependency socket?
- Specialization trigger threshold + hysteresis to avoid specialize/deopt thrash.
- No-overrides lanes first, overrides lanes left generic?

## Decision Log
- 2026-06-13: Owner reviewed the design and chose to PARK as future direction; satisfied with
  current performance. Findings + extension path captured here so nothing is lost.
- 2026-06-20: Owner directed activation; promoted to EPIC-2026-06-20-adaptive-pgo-di-optimizer
  (agent optimizer_0). This story is retained as the origin / future-direction record; active
  execution now lives in the epic and its child stories. Owner refinement: lead with a temporal /
  order-of-creation profile that reorders resolution attempts (correctness-safe) ahead of
  present/absent skip speculation.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Retain while this direction is live; revisit if superseded or implemented.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-06-13T12:30:00Z
  TYPE: FACT
  CLAIM: Phases 1-10 compute is tapped; residual redundancies (P3 double-pass over deps +
    redundant `_socket_kind_for_dep`; P10 two-variant lane builds) are micro and the heavy P10
    fast-path build is already single, so fusing buys sub-noise gains for real readability/risk.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:683-748
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:545-562
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1070-1339
  IMPACT: Closes phase-1-10 micro-optimization as negative EV; redirects energy to speculation.
  NEXT: none (parked).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-06-13T12:30:00Z
  TYPE: MEASURE
  CLAIM: Scheduler dispatch is optimal — chunk-granularity sweep at workers=5 moved plan_group
    wall <6% (within noise) while making cheap phases worse; the apparent 4.93x load skew was
    machine-load jitter (re-run of identical config showed 1.70x). Conjure wall is dominated by
    serial frame-wide phases 5-7 + mild plan-group contention, not dispatch.
  EVIDENCE:
  - benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py
  - src/melder/utilities/synchronization/phase_scheduler.py:521-560
  IMPACT: Rules out the scheduler as a lever; confirms caching amortizes the remaining cold
    setup costs.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-06-13T12:30:00Z
  TYPE: FACT
  CLAIM: The profile-guided optimizer's hard core already exists in production: a
    generation-guarded monomorphic inline cache on the meld door (`_fast_meld_doors` entry =
    (door_spell, captured_context, fast_creations, captured_epoch); guard = `_door_epoch ==
    captured_epoch` + context-identity + hooks/validation flags; miss → normal lane rebuilds),
    with hot-swap install and a nogil-tuned single-int guard. `_door_epoch` bumps on every
    spell-level invalidation chokepoint.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:196-245
  - src/melder/aether/spellbook/spell.py:369
  - src/melder/aether/spellbook/spell.py:573
  - src/melder/aether/spellbook/spell.py:592
  - src/melder/aether/conduit/meld/meld.py:631
  - src/melder/aether/spellbook/spellbook_creation_system.py:944
  IMPACT: The optimizer is an EXTENSION of proven machinery, not a from-scratch JIT — greatly
    reduces build risk and cost.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-13T12:30:00Z
  TYPE: RISK
  CLAIM: The one new correctness problem is guard coverage: `_door_epoch` covers structural
    door invalidation but NOT a dependency's instance being cleared from its store by another
    scope's cleanup. Speculating "dep present" therefore needs a per-assumption guard
    (multi-spell epoch / store-generation / cheap presence-confirm), keyed by existence class.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:406-451
  - codex/context_compass/artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md
  IMPACT: This decision gates any implementation; resolving it is the first activation step.
  NEXT: (deferred) confirm §4 guard policy with owner before build.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when this direction is activated, the guard policy is decided, or findings shift.
- Reference the design artifact for detail instead of duplicating it here.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
A full optimization sweep of the setup/compile pipeline (phases 1-10, scheduler, P5
parallelization, solo P11 executor) concluded that the conventional levers are exhausted or
amortized away by caching. The one unexploited, architecture-unique lever is profile-guided
adaptive specialization of meld executors, which can ride the existing `_door_epoch`
inline-cache + hot-swap + deopt machinery. The design is captured in the linked artifact; the
only new correctness problem is guard coverage (design §4). Parked at owner's request — owner
is satisfied with current performance. To resume: decide the §4 guard policy, hand-roll +
micro-bench one speculated body on 3.14t, and only then scope the profiler/re-emit/flag work
behind a default-off configuration.
