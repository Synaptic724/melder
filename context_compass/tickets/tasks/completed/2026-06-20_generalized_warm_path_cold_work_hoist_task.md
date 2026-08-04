<!-- CLOSED 2026-06-30T23:04:50Z (departed-agent cleanup) -->
- Completed: 2026-06-30T23:04:50Z
- Summary: Turned in during departed-agent cleanup (owner optimizer_0 departed); closed via tickets/tasks/completed/2026-06-30_turn_in_departed_agents_optimizer0_hope0_task.md. Prior in-file Notes preserved as the durable record; acceptance not re-verified.

# Task: Generalized executor — hoist cold-only work off the warm meld path

## Metadata
- Task ID: TASK-2026-06-20-generalized-warm-path-cold-work-hoist
- Story: UNKNOWN (standalone static-codegen trim; surfaced during EPIC-2026-06-20-adaptive-pgo-di-optimizer audit)
- Status: review
- Owner: cowork
- Agent Name: optimizer_0
- Priority: p2
- Created: 2026-06-20T20:20:00Z
- Updated: 2026-06-20T20:55:00Z

## Objective
The generalized no_overrides executor emits, per step, some work that is only consumed on the COLD
construct path but is currently executed on every (warm) meld. Move that work inside the
`if instance_N is None:` construct branch so warm reuse melds skip it. Same class as the inline-read
and lock-hoist trims; consumes existing plan data only.

## Item 1 — APPLIED: use_spell_lock_N computed on the warm path
- The `use_spell_lock_hint` branch emitted, before the reuse read on EVERY meld:
      use_spell_lock_N = True
      if (caller_creations_lock_held and creations_N is caller_creations):
          use_spell_lock_N = False
  but `use_spell_lock_N` is consulted only inside `if instance_N is None:` (the construct path).
- Change: moved that computation inside `if instance_N is None:` (before `if use_spell_lock_N:`). Warm
  melds now skip the bool + the `is`-compare branch entirely.
- FILE: generalized_no_overrides_codegen_creation_compiler.py (`_append_step_resolution_source`
  use_spell_lock_hint branch).
- VERIFICATION (outputs/verify_spell_lock_hint.py, sandbox py3.10): warm -> 1 read, 0 spell-lock,
  0 creations-lock, 0 construct; cold -> 1 spell-lock, creations-lock, 1 construct, 1 register.
  GENERATED-SOURCE shape only; Melder suite + 3.14t benchmark owner-run (NOT run here).

## Item 2 — APPLIED: cold-only per-step preamble locals
- Preamble previously emitted per step (every meld): `plan_step_N`, `spell_N`, `spell_id_N`,
  `has_disposal_methods_N`, `disposal_methods_N`.
- Warm-needed: `spell_id_N` (the inline read) + `spell_N` (OWNER routing reads
  `spell_N._owner_creations`). Cold-only: `plan_step_N`, `has_disposal_methods_N`,
  `disposal_methods_N`.
- Change: removed the 3 cold-only locals from the preamble. `plan_step_N` is now bound inside
  `_emit_construct_instance` (generic branch only, where it is used); `has_disposal_methods_N` +
  `disposal_methods_N` are bound at the top of `_append_step_register_source`. Pure code motion
  (Python is function-scoped; the locals are bound before their only uses on the cold
  construct/register path). Warm per-step preamble is now just `spell_N` + `spell_id_N`. No stability
  assumption.
- VERIFICATION (outputs/verify_cold_locals.py, sandbox py3.10): warm reuse -> 0 lock and the
  `steps` / `step_has_disposal_methods` / `step_disposal_methods` tuples are NEVER indexed (cold
  locals not bound); cold -> all three bound + construct + register once. Emitted-shape check only;
  suite + 3.14t benchmark owner-run.

## Item 3 — PLANNED (medium): OWNER owner_creations prebind
- OWNER-target routing reads `spell_N._owner_creations` on every (warm) meld. Solo already prebinds a
  stable owner store as a namespace constant (`prebound_owner_creations`, excluding lineage/cluster).
- Plan: mirror solo's prebind in the generalized OWNER routing so warm routing for `unique`/owner
  steps becomes a namespace-constant load instead of an attribute read. Correctness-sensitive
  (owner-store stability); needs the same lineage/cluster exclusions solo uses.

## Item 4 — APPLIED: cold-only `step_dep_keys` local
- `step_dep_keys_N` was bound in the per-step preamble (warm) but consumed only by the INLINED
  construct (cold). Moved into `_emit_construct_instance` (inlinable branch).
- VERIFICATION (outputs/verify_step_dep_keys.py): warm reuse never indexes `step_dep_keys`; cold
  inlined dep-chain still builds with the correct dependency.

## Item 5 — APPLIED: hoisted caller_creations None-check (owner-approved)
- CALLER/SPELLSPACE routing emitted `if caller_creations is None: raise` per caller-routed step, all
  testing the one executor-level `caller_creations` argument. Hoisted to ONE check at the executor top
  (gated on any caller/spellspace step via plan target data); per-step routing is now a direct
  `creations_N = caller_creations` bind. `caller_creations` is never reassigned, so one check == N
  checks on the success path. Only behavioral delta: the (door-unreachable) None error case now fails
  fast at the top before any node constructs, instead of after preceding OWNER nodes — recorded and
  owner-accepted.
- VERIFICATION (outputs/verify_caller_hoist.py): exactly one hoisted guard; None caller raises; store
  present builds both nodes.

## Item 6 — APPLIED: `spell_id_N` off the warm path for `many`
- `spell_id_N` was bound in every step's preamble, but a `many` step uses it only inside its
  disposal-gated register (`many` never does a reuse read). Dropped it from the preamble for `many`
  steps; bound it inside the `if has_disposal_methods_N:` register block. Non-disposal `many` (the
  gauntlet's hot transient case) no longer binds spell_id at all per meld. Singletons keep it in the
  preamble (the reuse read needs it).
- VERIFICATION (outputs/verify_many_spell_id.py): non-disposal many never indexes `step_spell_ids`;
  disposal many binds it in the gate + registers.

## Item 7 — APPLIED: compile-time disposal gate for the `many` register (owner-approved)
- Previously the `many` register was gated at RUNTIME (`if has_disposal_methods_N:` emitted every meld,
  plus the disposal binds). Disposal-ness is spell-static, so the gate moved to COMPILE time in
  `_append_step_resolution_source`:
  `if plan_step.spell.has_disposal_methods: _append_step_register_source(...)`. A non-disposal `many`
  step now emits ZERO register code -- no lock, no add, no disposal/spell_id binds, no branch (just
  construct + dict write). A disposal `many` emits the lock + `add_many_creations` unconditionally (no
  runtime check). Matches solo / many_only. Supersedes the runtime-`if` form from
  tickets/tasks/2026-06-20_generalized_many_disposal_lock_hoist_task.md.
- Tradeoff (owner-accepted): the emitted body is now disposal-shape-specialized, so graphs differing
  only in a step's disposal-ness no longer share a compiled body. Generalized bodies are already
  graph-specific, so the extra compile/setup cost is expected to be small; only matters for very
  short-lived processes (the gauntlet / services amortize it).
- VERIFICATION (outputs/verify_many_compiletime_gate.py): non-disposal-many emitted source contains NO
  `add_many_creations` / `._lock` (constructs only -> 0 lock, 0 register); disposal-many locks +
  registers once.

## Scope Boundaries
- generalized no_overrides emitter only. No change to Creations / door / planner / discovery.

## Applicable Anti-Patterns
- Cold-path work executed on the warm path (the target of this task).

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: Item 1 applied + emitted-shape verified; Items 2-3 planned. Awaiting owner
  3.14t benchmark + suite.

## Notes
- DATETIME: 2026-06-20T20:20:00Z
  TYPE: DECISION
  CLAIM: Applied Item 1 (use_spell_lock_N hoist into the cold construct branch). Warm lock-hint melds
    no longer compute the lock-mode branch. Items 2 (cold preamble locals) and 3 (owner prebind)
    scoped as follow-ons.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py (`_append_step_resolution_source` use_spell_lock_hint branch)
  - outputs/verify_spell_lock_hint.py
  IMPACT: Removes a per-warm-meld conditional (bool + `is`-compare) for every spell-lock-hint singleton
    step.
  NEXT: owner benchmark; then Item 2 / Item 3 on go.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-20T20:30:00Z
  TYPE: DECISION
  CLAIM: Applied Item 2 (cold-only preamble locals hoist). `plan_step_N`, `has_disposal_methods_N`,
    `disposal_methods_N` removed from the per-step preamble; `plan_step_N` now bound in
    `_emit_construct_instance` (generic branch), the two disposal locals at the top of
    `_append_step_register_source`. Warm reuse melds bind only `spell_N` + `spell_id_N`. Pure code
    motion, function-scoped, no stability assumption.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py (preamble; `_emit_construct_instance` generic branch; `_append_step_register_source` top)
  - outputs/verify_cold_locals.py (warm path never indexes the cold tuples; cold path binds all three)
  IMPACT: Drops 3 SUBSCR+STORE ops per step from the warm reuse path (every step of a warm
    many-root-over-singletons / deep-singleton meld).
  RESIDUAL: Item 3 (OWNER owner_creations prebind) still open -- carries a solo-precedented owner-store
    stability assumption; awaiting owner go.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-20T20:45:00Z
  TYPE: DECISION
  CLAIM: Applied three more warm-path trims (Items 4-6): (4) `step_dep_keys_N` moved into the inlined
    construct; (5) `caller_creations` None-check hoisted to one check at the executor top (owner-
    approved in chat); (6) `spell_id_N` dropped from the warm preamble for `many` steps (bound inside
    the disposal register). All pure code-motion / dedup of compile-time-known facts; no stability
    assumption (Item 5's only delta is fail-fast on the door-unreachable None case). Each emitted-shape
    verified in the py3.10 sandbox.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py
  - outputs/verify_step_dep_keys.py, outputs/verify_caller_hoist.py, outputs/verify_many_spell_id.py
  BENCHMARK: owner-run on 3.14t (no-GIL), benchmarks/testing_other_di/test_real_world_gauntlet.py --
    test PASSED (functional). melder gauntlet total(5000)=14049.90ms | avg=2.810ms | median=2.646ms |
    p95=4.694ms (dependency-injector avg 1.572ms; dishka avg 2.103ms). ~89% of melder time is the
    threaded hot phase (2.496ms/iter) -- exactly the path these trims target. CLARIFICATION (owner):
    these changes are MICRO-opts -- small but real (warm-path trims net ~1-2% cumulatively). The
    broader ~22s -> ~14s improvement came from the wider optimization effort and is NOT attributable to
    these micro-opts. Tail is high (max 39.5ms, cv ~41%) -> likely no-GIL contention / GC; the lock
    removals attack that.
  NEXT: remaining static trims are increasingly marginal/target-aware (spell_N off warm for caller
    singletons; disposal_methods_N off the register top for non-disposal many). The big lever for the
    1.3-1.8x gap is structural (drop the instance_results dict for stable chains) -- deferred per owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-20T20:55:00Z
  TYPE: DECISION
  CLAIM: Applied Item 7 -- compile-time disposal gate for the generalized `many` register (owner-
    approved with the sharing/setup tradeoff). Non-disposal `many` (the gauntlet's hot transient case)
    now emits ZERO register code; disposal `many` registers unconditionally under the lock with no
    runtime disposal check. Supersedes the earlier runtime-`if` form (disposal-lock-hoist task).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py (`_append_step_resolution_source` many compile-time gate; `_append_step_register_source` many w/o runtime if; docstring)
  - outputs/verify_many_compiletime_gate.py
  IMPACT: Per non-disposal `many` step per meld, removes the disposal binds + the runtime branch
    entirely (on top of the already-removed lock). The hot transient path in the gauntlet.
  TRADEOFF: disposal-shape now baked into the emitted body -> marginally less code-object sharing ->
    possible small setup/compile increase (owner to watch the ~162ms gauntlet setup figure).
  NEXT: owner 3.14t benchmark (watch hot-phase delta AND setup). Remaining static trims marginal;
    structural unroll is the deferred big lever.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
