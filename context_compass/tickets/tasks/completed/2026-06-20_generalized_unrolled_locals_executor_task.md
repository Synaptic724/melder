<!-- CLOSED 2026-06-30T23:04:50Z (departed-agent cleanup) -->
- Completed: 2026-06-30T23:04:50Z
- Summary: Turned in during departed-agent cleanup (owner optimizer_0 departed); closed via tickets/tasks/completed/2026-06-30_turn_in_departed_agents_optimizer0_hope0_task.md. Prior in-file Notes preserved as the durable record; acceptance not re-verified.

# Task: Generalized executor — straight-line locals (drop `instance_results` dict) for all-inlinable graphs

## Metadata
- Task ID: TASK-2026-06-20-generalized-unrolled-locals-executor
- Story: UNKNOWN (structural runtime lever; surfaced during EPIC-2026-06-20-adaptive-pgo-di-optimizer audit)
- Status: review
- Owner: cowork
- Agent Name: optimizer_0
- Priority: p2
- Created: 2026-06-20T21:05:00Z
- Updated: 2026-06-20T21:30:00Z

## Objective
Remove the per-meld `instance_results` dict from the generalized no_overrides executor for graphs where
every step is inlinable. The dict today serves only three roles: cross-step dependency lookups, the
per-step write, and the final root return. For an all-inlinable graph all three can be replaced with
straight-line `instance_{i}` locals plus a COMPILE-TIME `instance_key -> step_index` map, eliminating:
per-step dict writes, per-dep `instance_results[...]` hash lookups, `step_dep_keys` indexing, the final
`root not in instance_results` check, and the dict allocation itself.

## Why this is safe / uses comptime artifacts
- The executor already binds `instance_{i}` per step (the dict write is separate). After step i,
  `instance_{i}` is always bound (singleton reuse read assigns it before the `if None`; many assigns via
  construct). So later steps can reference `instance_{dep_index}` directly.
- Steps are already in TOPOLOGICAL order (deps before dependents) -- the current dict path relies on
  this too (inlinable reads `instance_results[dep_key]` which must already be populated). So
  `dep_index < i` for every dependency; the local is in scope.
- The `instance_key -> step_index` map is built at compile time from the ordered plan steps
  (instance_shape / plan). No new runtime state.
- Eligibility = every step inlinable (`_inlinable_common_shape(step) is not None`). Inlinable steps
  reference deps explicitly, so no generic `_construct_spell_instance` (which reads the dict
  internally) is needed. Non-eligible graphs fall back to the current dict path unchanged.

## Design (additive; existing dict path is the untouched fallback)
- `_compile_no_overrides_executor_from_steps`: if `_all_steps_inlinable(steps)`, build the UNROLLED
  source (+ trimmed namespace: no root_instance_key/step_instance_keys/step_dep_keys needed); else the
  current step-plan source. Same `root_instance_key` is available here (line ~294).
- Thread an optional `instance_index_by_key: Optional[Dict[key,int]] = None` through
  `_build_step_plan_executor_source` -> `_append_step_resolution_source` -> `_emit_construct_instance`.
  None => byte-identical current behavior (the dict path). Not-None => unrolled:
  - skip `instance_results = {}` and the final `if root_instance_key not in instance_results` check;
    emit `return instance_{root_index}` (root_index = map[root_instance_key]).
  - per step: skip the `instance_results[step_instance_keys[i]] = instance_{i}` write (the local IS the
    result).
  - inlinable construct: emit `param=instance_{map[dep_key]}` instead of
    `param=instance_results[step_dep_keys_i[j]]`; skip the `step_dep_keys_i = step_dep_keys[i]` bind.

## Steps / Checklist
- [x] Add `_all_steps_inlinable(steps)` + `_instance_index_by_key(steps)` helpers.
- [x] Thread `instance_index_by_key` (additive, None-default) through `_emit_construct_instance`,
      `_append_step_resolution_source` (all 5 construct calls + 4 result stores via
      `_append_step_result_store`), and `_build_step_plan_executor_source`.
- [x] Dispatch in `_compile_no_overrides_executor_from_steps` (passes `root_instance_key` to the
      builder; builder picks unrolled iff `_all_steps_inlinable` and the root key maps to a step).
      Namespace NOT trimmed -- unused signature defaults are harmless on the unrolled path, and
      leaving them avoids touching the namespace builder (lower risk).
- [x] Sandbox behavior check (outputs/verify_unroll.py): 3-step graph (Logger unique/OWNER <- root
      Service unique/OWNER depending on Logger + Config many/CALLER). Cold: all built, Service
      constructed with the actual Logger+Config instances (dep passing via `instance_{i}` locals),
      singletons registered, non-disposal many not registered, returns Service. Warm: Logger reused,
      Config reconstructed, Service reused, returns same instance. Asserted NO `instance_results` in
      the unrolled source.
- [x] Syntax: py_compile parsed cleanly through line 1855 (past ALL edits, 608-1057) before the
      pre-existing `_build_unrolled_call_arg_refs` -- i.e. the edits are syntactically valid. (The
      py_compile error at 1855 is a stale/truncated BASH-MOUNT copy of a function NOT touched here;
      the real file via the file tool is intact: `_build_unrolled_call_arg_refs` completes 1855-1965
      with more functions after. Known file-tool vs shell-mount divergence.)
- [ ] OWNER 3.14t suite + gauntlet: AUTHORITATIVE gate. This changes dep-passing AND the bash-mount
      divergence prevented a full-file compile here, so the real-file syntax + behavior must be
      confirmed by the owner's suite before trust. A syntax slip (none expected) would fail at import
      = fast/obvious, not subtle.

## Scope Boundaries
- generalized no_overrides emitter only; all-inlinable graphs only; dict path preserved as fallback.
- No change to phases 1-10 / artifact production / Creations / door.

## Applicable Anti-Patterns
- Per-meld dict allocation + hash lookups where compile-time indices suffice (the target).

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: implemented additive + gated; edits syntactically valid + emitted shape
  behavior-verified in sandbox; awaiting owner 3.14t suite (authoritative, esp. given the bash-mount
  divergence prevented a full-file compile here).

## Notes
- DATETIME: 2026-06-20T21:30:00Z
  TYPE: DECISION
  CLAIM: Implemented the all-inlinable unrolled executor (straight-line `instance_{i}` locals, no
    `instance_results` dict) as a strictly ADDITIVE + GATED change. `instance_index_by_key=None`
    (default) leaves the dict path byte-identical (the fallback); the unrolled path activates only when
    every step is inlinable and the root key maps to a step. Deps read `instance_{dep_index}` locals
    via the compile-time key->index map (sound by the same topological-order + key==instance_key
    invariants the dict path already relies on); per-step dict writes, `step_dep_keys` indexing, the
    dict allocation, and the final membership check are all dropped on the unrolled path.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py (`_emit_construct_instance`, `_all_steps_inlinable`, `_instance_index_by_key`, `_append_step_result_store`, `_append_step_resolution_source`, `_build_step_plan_executor_source`, dispatcher)
  - outputs/verify_unroll.py (cold dep-passing + singleton reuse + many reconstruct + root return; no instance_results)
  VERIFICATION: emitted-shape behavior check passed; py_compile reached line 1855 (past all edits)
    before erroring on the BASH-MOUNT's truncated copy of the pre-existing `_build_unrolled_call_arg_refs`
    (the real file via the file tool is intact). So the edits parse; the bash mount could not be used
    for a full-file compile (file-tool vs shell divergence).
  RISK/CAVEAT: changes dep-passing on the hot path; gated (all-inlinable) + additive (dict fallback)
    so blast radius is the unrolled path, and any syntax slip fails fast at import. NOT trusted until
    the owner runs the 3.14t suite + gauntlet on the real file. Easy clean revert (gate + additive).
  NEXT: owner runs suite + gauntlet (watch hot-phase throughput on many-root-over-singletons and
    deep-singleton graphs -- where the dict removal lands).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
