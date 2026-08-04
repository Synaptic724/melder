<!-- CLOSED 2026-06-30T23:04:50Z (departed-agent cleanup) -->
- Completed: 2026-06-30T23:04:50Z
- Summary: Turned in during departed-agent cleanup (owner optimizer_0 departed); closed via tickets/tasks/completed/2026-06-30_turn_in_departed_agents_optimizer0_hope0_task.md. Prior in-file Notes preserved as the durable record; acceptance not re-verified.

# Task: Port generalized no_overrides creation wins into the many_only step-plan emitter

## Metadata
- Task ID: TASK-2026-06-21-many-only-port-generalized-no-overrides-wins
- Story: UNKNOWN (structural runtime lever; surfaced during EPIC-2026-06-20-adaptive-pgo-di-optimizer audit)
- Status: review
- Owner: cowork
- Agent Name: optimizer_0
- Priority: p2
- Created: 2026-06-21T06:00:00Z
- Updated: 2026-06-21T06:00:00Z

## Objective
Carry the generalized-manifest no_overrides creation optimizations into the many_only
`no_overrides` STEP-PLAN emitter (`many_only_no_overrides_codegen_creation_compiler.py`).
The many_only transient-unrolled path was already optimal; the step-plan path (taken when
ANY step carries disposal methods, or >8-arg constructors, or no transient schema) still
carried the pre-optimization shape. Three generalized wins now apply to it:
1. LOCALS MODE: drop the per-meld `instance_results` dict for all-inlinable graphs; deps
   read straight-line `instance_{i}` locals via a compile-time `instance_key -> step_index`
   map; no dict alloc, no tuple-key hashing, no final root-membership check.
2. DIRECT-STORE REGISTRATION: emit the `_creations` / `_disposable_creations` list stores
   inline under the caller-held lock instead of an `add_many_creations` method call (pure
   dispatch overhead on the disposal hot path).
3. ARTIFACT-SOURCED DISPOSAL: consume the stamped `plan.step_has_disposal_methods` array
   for the disposal gate/routing instead of re-reading the live `plan_step.spell.has_disposal_methods`
   during codegen. Plus the caller-creations None-guard hoist and the dead `plan_step_N`
   alias trim.

## Why this is safe / uses comptime artifacts
- Locals mode is additive + gated: it engages only when every step is inlinable AND every
  dependency key resolves to an emitted step AND the root key maps to a step. Any graph that
  fails the gate falls back to the byte-identical dict path. Sound by the same topological-
  order + key==instance_key invariants the dict path already relies on (and mirrors the live
  generalized-manifest locals mode).
- Direct-store registration is line-for-line equivalent to `add_many_creations`
  (creations.py:241-267): get-or-create the live list + append; get-or-create the disposable
  list + append `(item, list(methods))`. The non-list-slot guard is intentionally dropped
  because `many` existence is fingerprint-stable (a many spell id only ever owns a list slot),
  identical reasoning to the generalized emitter. The lock discipline is unchanged: the caller
  emits `with creations_N._lock:` exactly as before.
- Disposal truth is stamped on the plan/manifest artifact at bind time (it composes into the
  spell fingerprint, so it cannot go stale without rolling the spell version + recompiling).
  Consuming `plan.step_has_disposal_methods` is the fingerprinted source of truth; the live
  `plan_step.spell.has_disposal_methods` read was redundant codegen-time introspection. The
  overrides many_only compiler already gates on the stamped `row["has_disposal_methods"]`;
  this aligns the no_overrides compiler with it.

## Design (additive; dict path + spell-read fallback preserved)
- Thread `step_has_disposal_methods: Optional[Tuple[bool, ...]]` from the plan entry
  (`compile_no_overrides_codegen_creation_executor_from_plan` reads `plan.step_has_disposal_methods`)
  down through `_compile_no_overrides_executor_from_entry_inputs` ->
  `_compile_no_overrides_executor_from_steps` -> `_build_step_plan_executor_source` ->
  `_append_step_resolution_source`. None (schema-rows entry) => fall back to a single
  `bool(plan_step.spell.has_disposal_methods)` derivation (byte-identical to prior behavior).
- `_build_step_plan_executor_source`: build `key_to_step_index`; detect locals mode; emit the
  hoisted `if caller_creations is None` guard once; skip `instance_results = {}` and the final
  root-membership check in locals mode (`return instance_{root_index}`).
- `_append_step_resolution_source`: `plan_step_N` only when not inlinable; `step_dep_keys_N`
  only in dict mode; per-step disposal gate uses the threaded `has_disposal_methods`; the
  `instance_results[...]` store is skipped in locals mode.
- `_emit_construct_instance`: locals mode emits `param=instance_{dep_step_index}` instead of
  `param=instance_results[step_dep_keys_N[j]]`.
- `_append_step_register_source`: direct `_creations`/`_disposable_creations` list stores
  (replaces the `add_many_creations` call).
- `_append_step_creations_target_source`: drops the per-step caller None-guard (now hoisted).

## Steps / Checklist
- [x] Locals mode + caller-guard hoist + `plan_step_N` trim in the step-plan emitter.
- [x] Direct-store registration in `_append_step_register_source`.
- [x] Artifact-sourced disposal flag threaded from `plan.step_has_disposal_methods`
      (spell-read fallback for the schema-rows entry).
- [x] Owner-run harness (benchmarks/testing_other_di/test_family_lane_harness.py):
      lane-routing proof + warm timing, P-core pinned, single-thread, caching disabled.
      Disposal lane confirmed `[no-dict]` / `...step_executor_disposal_aware`; emitted source
      byte-identical after the artifact change (disposal value unchanged).
- [ ] OWNER 3.14t full suite + gauntlet: AUTHORITATIVE gate (thread-safety + correctness on
      the real file). The bash-mount divergence prevents a trustworthy full-file py_compile
      here; a syntax slip would fail fast at import.

## Evidence (owner-run, 5-class all-disposal graph = 7 many instances, best of 4, single-thread, P-core pinned)
- baseline (dict + `add_many_creations`):   4.381 us/meld
- + locals mode / hoist / alias trim:        3.424 us/meld  (-21.8%)
- + direct-store registration:               2.81  us/meld  (-15.0% more; ~36% cumulative)
- artifact disposal flag:                    byte-identical emit, ~2.81 us/meld (no runtime delta; expected)
- Scaling check (deepened 9-class depth-5 = 31 instances): 0.40 -> 0.38 us/instance vs the
  5-class graph -> per-step cost flat, win scales linearly. NOTE: an earlier "disposal at
  parity with transient" claim was an apples-to-oranges artifact (7-instance disposal graph
  vs 31-instance transient graph); on the SAME 31-instance graph disposal is ~4.3x transient
  -- disposal tracking has a real ~0.29 us/instance cost (lock + 4 dict ops + 2 appends).

## Scope Boundaries
- many_only no_overrides step-plan emitter only; transient-unrolled path untouched (already
  optimal); dict path + spell-read fallback preserved.
- No change to phases 1-10 / artifact production / Creations / door / overrides path.
- Solo: NOTHING to port -- solo bakes all facts into the namespace at compile time and its
  hot path is a literal `return call_target()`; singleton registers run cold-only behind the
  door.

## Applicable Anti-Patterns
- Per-meld dict allocation + hash lookups where compile-time indices suffice (locals mode).
- Method-dispatch overhead for a fingerprint-stable store op (direct-store registration).
- Re-introspecting live spell objects in codegen for facts the artifact already stamps
  (artifact-sourced disposal).

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: implemented additive + gated; owner harness confirms routing + emitted
  shape + warm timing (-36% on the disposal step-plan lane, linear scaling); awaiting owner
  3.14t suite + gauntlet (authoritative, esp. given the bash-mount divergence blocked a
  full-file compile here).

## Notes
- DATETIME: 2026-06-21T06:00:00Z
  TYPE: DECISION
  CLAIM: Ported three generalized no_overrides wins into the many_only step-plan emitter
    (locals mode, direct-store registration, artifact-sourced disposal flag) as additive +
    gated changes; dict path and a spell-read disposal fallback remain as untouched fallbacks.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py
    (`_build_step_plan_executor_source`, `_append_step_resolution_source`, `_emit_construct_instance`,
    `_append_step_register_source`, `_append_step_creations_target_source`, disposal-array threading
    through the entry/compile chain)
  - benchmarks/testing_other_di/test_family_lane_harness.py (routing proof + warm timing, all
    four discovery lanes; disposal lane 4.38 -> 2.81 us/meld on the 5-class graph)
  VERIFICATION: owner-run harness: disposal lane `[no-dict]` + `...disposal_aware`, routing
    match True for all lanes; warm timing -36%; artifact change left the emitted source
    byte-identical (disposal value unchanged) as predicted.
  RISK/CAVEAT: thread-safety-critical registration path; mitigated by (a) lock discipline
    unchanged, (b) direct-store equivalence verified against add_many_creations + the
    fingerprint-stable many-slot invariant, (c) locals mode gated with the dict path as
    fallback. NOT trusted until the owner's 3.14t suite + gauntlet pass on the real file.
  NEXT: continue migration -- precompute `step_spell_ids` namespace array (drop the per-meld
    `spell_N.spell_id` attr read on disposal steps) and the `creations_N` dead-alias trim for
    mixed-disposal many graphs (needs a mixed harness lane to measure). Then owner suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
