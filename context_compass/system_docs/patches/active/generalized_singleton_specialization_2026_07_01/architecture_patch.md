# Architecture Patch: Generalized Singleton Warm-Tail Specialization

- Patch ID: generalized_singleton_specialization_2026_07_01
- Status: in_progress (guard policy APPROVED by owner in chat 2026-07-01; emitter + lazy overrides landed; specializer wiring pending)
- Owner ticket: tickets/tasks/2026-07-01_compiler_phase8_11_generalized_call_savings_task.md
- Agent: fable_0
- Created: 2026-07-01T20:50:00Z

## Objective
Collapse the warm-path cost of OWNER-`unique` steps in the generalized no-overrides lane from
per-step shared-object traffic (spell tuple load + `_owner_creations` attr + shared dict get +
None branch, x N steps x every meld) to one int compare per captured step, by emitting a
specialized executor body after first successful hot execution and hot-swapping it into the
existing self-replacing `CreationContext._no_overrides_executor` slot.

This is trim #2 (adaptive PGO design, Stage 3) realized lean: NO profiler, NO optimizer doors,
NO runtime record. Existence classes are compile-time facts in the generalized manifest rows,
so the "always-present after first construction" fact for `unique` steps is static, not
profiled. Stages 1-2 of the PGO design are skipped by construction.

## Non-Goals
- No overrides-lane specialization (stays generic).
- No `unique_per_conduit` / cluster / lineage / spellspace capture (caller-varying stores;
  cluster/lineage additionally carry membership-change invalidation surfaces).
- No persistence (`__optimizations__` cache, PGO Stage 5) in this patch.
- No changes to default door lanes, fast-meld-door guard ladder, cache internals, or the
  Transaction Admission Plane.
- No mutation-system integration (on hold).

## Changed Components
1. `codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py`
   - NEW: `emit_specialized_step_plan_source(...)` - emits the specialized inner body:
     per-captured-step epoch guards + captured-instance constants; non-captured steps
     (many/caller-routed) emitted exactly as today with captured instances used directly as
     constructor arguments; deopt = tail-call the generic inner executor.
2. `codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py`
   - NEW: one-shot specializer wrapper installed (config-gated) around the hot no-overrides
     door at hydration: first successful execution reads live `unique` instances from owner
     stores, builds the specialized inner + door, swaps the context slot; declines (and swaps
     the plain hot door back) when no step qualifies or any capture target is missing.
3. `aether/spellbook/configuration/spellbook_configuration.py`
   - NEW typed property (default OFF) gating specialization; read ONCE at hydration time,
     never per meld.

## Invariants (must hold after patch)
- Wrong speculation is a slow path, never a wrong result (PGO design non-negotiable).
- Executor slots remain self-replacing; all readers re-read the slot per call (existing
  contract in creation_context.py docstring holds unchanged).
- Capture set is exactly Existence.unique (OWNER store, frame-global, conduit-independent).
- Specialized body is reachable only through lanes that already enforce root-level gates
  (validation flag, dirty roots, door epoch, context identity).
- Overrides door keeps its hydration-captured generic inner (untouched).
- OFF = byte-identical behavior to today (wrapper never installed).

## Guard Policy (the SS4 decision - REQUIRES OWNER SIGNOFF)
Per-existence hybrid, audited 2026-07-01:
- `unique` captured steps: Option A per-dep guard - capture `dep_spell._door_epoch` at
  specialization time; specialized body prologue compares each captured epoch (frame-local
  int compares against default-param ints); any mismatch => tail-call generic inner (deopt).
- Store-clear coverage (the SS4 gap) is CLOSED for this capture set by audit, not by new
  counters: owner stores are cleared only by `Creations.cleanup()` (teardown), and teardown
  paths force validation gating via lineage unregister -> RiskManager; pool recycling
  (`Conduit._prepare_for_pool` -> `reset_for_pool`) and `SpellSpace` reset touch caller/
  spellspace stores only. EVIDENCE: src/melder/aether/conduit/conduit.py:417-434;
  src/melder/aether/conduit/creations/creations.py:94-129,414-495;
  src/melder/aether/conduit/spell_space/spell_space.py:273-310.
- Structural mutations (transfer/link/sever/bind) route through change-control dirty roots ->
  meld raises or revalidates -> phase rebuild -> `_cleanup_creation_context` bumps epoch.
  EVIDENCE: src/melder/aether/spellbook/spell.py:577-600;
  src/melder/aether/conduit/meld/meld.py:715-786.
- No Creations store-generation counter (Option B) and no presence-confirm reads (Option C)
  are added in v1.

## Interface Deltas
- `SpellbookConfiguration`: +1 typed property (name proposal:
  `generalized_singleton_specialization_enabled`, default False).
- `generalized_hydrator.hydrate_creation_executors(...)`: +optional flag parameter (threaded
  from hydration call sites; default preserves current behavior).
- No public API shape changes on Spellbook/Conduit/Meld surfaces.

## Migration Order
1. Emitter function + unit tests (source-shape tests, no live runtime).
2. Hydrator specializer wrapper + config property + component tests.
3. Deopt matrix integration tests (teardown / transfer / hook-attach / context-rebuild /
   concurrent deopt) + differential test (same workload, flag ON vs OFF => identical
   instances, registrations, disposal, errors).
4. User-run 3.14t validation: full unit tree + both gauntlets + contention sweep.

## Rollback
- Config default OFF; rollback = do not enable. Code rollback = delete the emitter function,
  wrapper installation block, and config property; no persistent state exists.

## Ticket Coverage Matrix
| Work item | Ticket |
|---|---|
| All stages of this patch | tickets/tasks/2026-07-01_compiler_phase8_11_generalized_call_savings_task.md |
| Prior evidence (Stage 0 GO, emitted-body facts) | tickets/tasks/2026-06-13_executor_construction_lane_trim_task.md |
| Design source | artifacts/2026-06-13_adaptive_pgo_di_optimizer_design.md |
