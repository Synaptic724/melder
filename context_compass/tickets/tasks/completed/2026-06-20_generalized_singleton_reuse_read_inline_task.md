<!-- CLOSED 2026-06-30T23:04:50Z (departed-agent cleanup) -->
- Completed: 2026-06-30T23:04:50Z
- Summary: Turned in during departed-agent cleanup (owner optimizer_0 departed); closed via tickets/tasks/completed/2026-06-30_turn_in_departed_agents_optimizer0_hope0_task.md. Prior in-file Notes preserved as the durable record; acceptance not re-verified.

# Task: Generalized singleton reuse read — inline existence-known `get_creation`

## Metadata
- Task ID: TASK-2026-06-20-generalized-singleton-reuse-read-inline
- Story: UNKNOWN (standalone static-codegen trim; surfaced during EPIC-2026-06-20-adaptive-pgo-di-optimizer audit)
- Status: review
- Owner: cowork
- Agent Name: optimizer_0
- Priority: p2
- Created: 2026-06-20T20:11:15Z
- Updated: 2026-06-20T20:15:00Z

## Objective
On the WARM singleton reuse read, replace the runtime-dispatching helper call
`_get_existing_creation(spell=spell_N, creations=creations_N, existence=existence_N)` with an inline
`creations_N.get_creation(spell_id_N)`. Existence is compile-time-known per step, and for every
singleton existence the helper reduces to exactly `creations.get_creation(spell_id)`.

## Rationale / source-of-truth
- Existence + spell_id are pre-computed in discovery (phase 8 `SpellExistenceOccurrence` /
  `SpellRuntimeRecord`) and frozen as constant namespace tuples in phase 11 (`step_existences`,
  `step_spell_ids`). The runtime branch is a code-sharing choice, not a data gap.
- Lynchpin: `step_spell_ids[N]` is bound to `plan_step.spell.spell_id` (namespace builder), the same
  value the helper reads by AND the register writes by -> the inline is provably identical for every
  singleton existence. The helper's `many` arm is never reached from a singleton step.
- Consumes existing plan/model truth (`plan_step.existence`, `SpellRuntimeRecord`); does NOT re-derive
  discovery.

## Steps / Checklist
- [x] Replace the 7 emitted `_get_existing_creation(...)` call sites in
      `_append_step_resolution_source` (upc/spellspace pre-lock + in-lock; spell_lock_hint pre-lock +
      two in-lock; default-singleton pre-lock + in-lock) with
      `instance_N = creations_N.get_creation(spell_id_N)` at the matching indent. DCL control flow
      preserved exactly.
- [x] Drop the now-unused per-step `existence_N = step_existences[N]` emission (confirmed no remaining
      emitted consumer via grep).
- [ ] (trivial follow-up) Remove now-dead wiring: `step_existences` + `_get_existing_creation`
      signature params + namespace entries (sig 677/684, namespace 1042/1061) and the helper def /
      its dead `many` arm if no external caller. Harmless unused defaults; deferred to keep this diff
      focused on the behavioral change.
- [x] Sandbox compile + behavior check (outputs/verify_singleton_inline.py): present -> 1 read,
      0 lock, 0 construct, 0 register; absent -> 2 reads (DCL), 1 lock, 1 construct, 1 register.
- [ ] Owner 3.14t benchmark + suite.

## Scope Boundaries
- generalized no_overrides emitter only (warm singleton reuse read). `many` branch untouched.
- No change to Creations / door / planner / discovery.

## Applicable Anti-Patterns
- Runtime dispatch on a compile-time-known fact (existence) on the warm path -- the target of this task.

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: inline applied (7 sites) + existence_N dropped; emitted shape verified in sandbox;
  awaiting owner 3.14t benchmark + suite.

## Notes
- DATETIME: 2026-06-20T20:11:15Z
  TYPE: PLAN
  CLAIM: Inline the existence-known singleton reuse read. Provably equivalent (lynchpin verified); lands
    on the many-root-over-singletons warm re-walk (epic's primary target). Higher payoff than the lock
    fix because it is per-dep on the hot path.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:844-954 (7 call sites), :796 (existence_N), :1078-1081 (step_spell_ids binding), :1354-1389 (_get_existing_creation)
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_runtime_analysis.py (SpellRuntimeRecord: spell_id + existence)
  IMPACT: Removes a helper-call frame + `spell.spell_id` attr read + existence branch ladder per
    singleton dep per meld on the warm path.
  NEXT: execute on owner go.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-20T20:15:00Z
  TYPE: DECISION
  CLAIM: APPLIED (owner go in chat). All 7 singleton reuse-read call sites in
    `_append_step_resolution_source` now emit `instance_N = creations_N.get_creation(spell_id_N)`
    (DCL control flow preserved); the dead per-step `existence_N = step_existences[N]` emission was
    removed. Grep confirms zero emitted `_get_existing_creation(` calls and zero emitted
    `existence_{step_index}` references remain; surviving `existence=existence` hits are builder-level
    Python (hydration / register helpers), not generated source.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py (`_append_step_resolution_source` singleton branches + preamble)
  - outputs/verify_singleton_inline.py (emitted-shape behavior check)
  VERIFICATION: Sandbox py3.10 emitted-shape check only -- present singleton: 1 read / 0 lock /
    0 construct / 0 register; absent singleton: 2 reads (DCL) / 1 lock / 1 construct / 1 register.
    Melder suite + 3.14t benchmark are owner-run -- NOT run here.
  RESIDUAL: dead wiring left in place (step_existences + _get_existing_creation sig params + namespace
    entries; helper def). Internally consistent (sig default <-> namespace value both present), unused,
    zero per-meld cost. Trivial follow-up.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
