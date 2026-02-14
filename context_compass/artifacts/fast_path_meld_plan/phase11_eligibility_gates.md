# Phase 11 Eligibility Gates (Draft, 2026-01-27)

## Purpose
Define the strict eligibility gates for Phase 11 execution and the fallback
rules to the Phase 8-10 executor.

## Evidence Anchors
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py:MeldRuntime.execute`
  (validity checks, dirty-root gating)
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py:MeldEngine.run`
  (override detection + execution flow)
- `context_compass/artifacts/fast_path_meld_plan/codex_exploration/phase8_10_migration_plan_2026-01-27.md`
  (Phase 11 feasibility notes)

## Phase 11 Eligibility Gates (Strict Best-Case)
### Gate Group A: System + validity
- Spell must be validated (`spell.validated`).
- Spell must not be broken (`spell.is_broken`).
- System validity must not be invalid/gated/disabled.
- Root must not be dirty (change-control manager check).

Evidence: `MeldRuntime.execute` gating path.

### Gate Group B: Plan integrity
- Phase 8 OccurrencePlan exists and is fresh (signature matches current wiring).
- Phase 9 InjectionPlan exists and is fresh.
- Phase 10 PatchMaps exist only if overrides/mutations are allowed (Phase 11
  should be override-free by default).

### Gate Group C: No dynamic features
- No overrides supplied (root or socket).
- No mutation overrides.
- No spellspace requirement (or spellspace already validated and bound).
- No contract override payloads (SpellContract overrides absent).

### Gate Group D: Executor compatibility
- All steps in the plan are of supported types (class/method/lambda existing creation).
- No unresolved contracts or late-bound wiring.
- Creation targets (owner/caller/spellspace) are stable and encoded in plan.

## Fallback Rules
If any gate fails, fall back to the Phase 8-10 executor (or legacy runtime if
Phase 8-10 artifacts are missing).

Fallback reasons should be recorded for observability (hit-rate tracking).

## Notes
- Phase 11 is optional and should never be required for correctness.
- Any mismatch or stale artifact should trigger immediate fallback.

## Open Questions
- What is the definitive plan signature for Phase 11 gating?
