<!-- CLOSED 2026-06-30T23:04:50Z (departed-agent cleanup) -->
- Completed: 2026-06-30T23:04:50Z
- Summary: Turned in during departed-agent cleanup (owner optimizer_0 departed); closed via tickets/tasks/completed/2026-06-30_turn_in_departed_agents_optimizer0_hope0_task.md. Prior in-file Notes preserved as the durable record; acceptance not re-verified.

# Task: Generalized `many` step — hoist the creations lock inside the disposal gate

## Metadata
- Task ID: TASK-2026-06-20-generalized-many-disposal-lock-hoist
- Story: UNKNOWN (standalone static-codegen trim; surfaced during EPIC-2026-06-20-adaptive-pgo-di-optimizer audit)
- Status: review
- Owner: cowork
- Agent Name: optimizer_0
- Priority: p2
- Created: 2026-06-20T20:11:15Z
- Updated: 2026-06-20T20:11:15Z

## Objective
Remove a per-meld creations-lock acquisition that the generalized no-overrides emitter took
UNCONDITIONALLY on every `many` step, including non-disposal `many` that never register. Match the
solo / many_only families, which already gate the lock on disposal at codegen-build time.

## Findings (pre-change)
- generalized `_append_step_resolution_source` many branch emitted `with creations_N._lock:`
  unconditionally, then `_append_step_register_source` emitted a RUNTIME `if has_disposal_methods_N:`
  inside it. For a non-disposal `many` step the emitted body was `with lock: if False: pass` -- it
  acquired/released the creations lock every meld for nothing.
- solo (no-disposal many -> pure construct, no lock) and many_only (compile-time
  `if plan_step.spell.has_disposal_methods:` gate) already avoid this.
- Under NOGIL this is not micro: an uncontended lock still costs atomics/barriers, and a contended
  creations lock serializes concurrent melds on one conduit store.

## Change applied
- `_append_step_resolution_source` many branch: removed the unconditional `with creations_N._lock:`;
  now calls `_append_step_register_source` at base step indent.
- `_append_step_register_source` many branch now emits:
      if has_disposal_methods_N:
          with creations_N._lock:
              creations_N.add_many_creations(...)
- Docstring updated: the many branch emits its own disposal-gated lock; singleton branches still rely
  on a caller-emitted lock.
- Net: non-disposal `many` takes no lock and does not register (behavior unchanged, lock removed);
  disposal `many` locks once and registers once (behavior unchanged). Single shared emitted body
  preserved (runtime branch kept; the flag is spell-static).
- FILE: src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py

## Validation
- Standalone compile + behavior check of the emitted step block (outputs/verify_many_lock.py, sandbox
  py3.10): emitted source compiles; non-disposal many -> lock enters 0 / registered 0; disposal many ->
  lock enters 1 / registered 1. GENERATED-SOURCE shape only.
- Melder suite imports under 3.14t and is owner-run -- NOT run here. Owner 3.14t benchmark + suite run
  required before merge.

## Scope Boundaries
- generalized no_overrides emitter only. No change to solo / many_only / overrides lanes.
- No change to Creations, the door compiler, or runtime store semantics.

## Applicable Anti-Patterns
- Runtime branch on a compile-time-known constant (addressed for the lock; the inner
  `if has_disposal_methods_N:` is intentionally retained to keep one shared emitted body).

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: change applied + emitted-shape verified; awaiting owner 3.14t benchmark + suite.

## Notes
- DATETIME: 2026-06-20T20:11:15Z
  TYPE: DECISION
  CLAIM: Applied the minimal lock-hoist (owner-approved in chat: "do the if and then the lock after").
    Lock now taken only for disposal `many`; non-disposal `many` never registers and never locks.
    Behavior preserved; verified at the emitted-source level.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py (many branch + register many branch + docstring)
  - outputs/verify_many_lock.py (compile + behavior check)
  IMPACT: Removes an unconditional per-meld lock on every non-disposal `many` interior step in mixed
    graphs -- a NOGIL serialization point.
  NEXT: owner 3.14t benchmark + suite; then merge.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-20T20:55:00Z
  TYPE: NOTICE
  CLAIM: SUPERSEDED / strengthened. The runtime `if has_disposal_methods_N:` form applied here was
    later replaced by a COMPILE-TIME disposal gate (owner-approved) -- see Item 7 of
    tickets/tasks/2026-06-20_generalized_warm_path_cold_work_hoist_task.md. A non-disposal `many` step
    now emits NO register code at all (no lock, no add, no binds, no branch); a disposal `many` emits
    the lock + add unconditionally with no runtime check. The lock-removal goal of THIS ticket is
    preserved and strengthened (non-disposal many is now fully register-free).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py (`_append_step_resolution_source` many branch compile-time gate)
  - outputs/verify_many_compiletime_gate.py
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
