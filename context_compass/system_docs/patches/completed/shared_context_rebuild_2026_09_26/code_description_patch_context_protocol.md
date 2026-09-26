# code_description_patch_context_protocol

## Metadata
- Patch ID: shared_context_rebuild_2026_09_26
- Trigger: concurrency-sensitive publication, reader lifetime, failed leadership.
- Updated: 2026-09-26T13:58:21Z

## Reader control flow (dynamic meld)
1. Resolve and validate as today; run any producer (structural, resolution, deferred) BEFORE admission.
2. `creation_gate.admit_ticket()` (visibility-first; parks while a window has the gate frozen).
3. While `spell.resolution_required`: unregister, `_ensure_runtime_resolution_ready`, admit again.
4. Read the context: `fast_state >= 2` -> slot; else `spell._get_or_build_creation_context()` (election).
5. Call the executor slot (`_no_overrides_instance_executor`, `_no_overrides_executor` or
   `_overrides_executor`); `finally: unregister_ticket()`.

## Writer control flow (producer)
1. `with Meld._rebuild_window(spell), spell._lock:` - the window first.
2. Window enter: take each affected gate's transition lock in index-id order, record prior posture, close,
   close_and_drain(interval=0.001), clear the spell's recorded failure. Entry failure unwinds and re-raises.
3. Phases run under the spell lock (Phase 5 clears the plan and resets the context; Phase 11 republishes).
4. Spell lock released, then window exit: on success publish a context for each spell whose plan is present;
   on failure record the cause for unpublished spells and idle their switch; then restore posture (reopen
   only gates found enabled) and release locks in reverse order. The original error always propagates.

## Edge and error semantics
- Leader build failure: cause recorded, switch 1 -> 0, original re-raised; followers raise chained from it.
- A spell without a plan after the window stays unpublished; its next meld validates normally.
- Drain timeout (30 s) raises RuntimeError from the producer; nothing is left frozen.

## Invariants and idempotency
- One ticket pair per dynamic meld. No input retired while an admitted meld uses it (inside windows).
- CounterSwitch and CreationGate unchanged; no global or per-meld lock.

## Explicit non-goals
- Draining for resets outside windows; automatic-mode rebuild safety; nested self-melds that force a rebuild
  of the same spell (drain themselves, time out).
