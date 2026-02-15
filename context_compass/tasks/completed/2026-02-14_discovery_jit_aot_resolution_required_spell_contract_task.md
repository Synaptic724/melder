# Task: Discovery - JIT/AOT `resolution_required` Spell Contract



Completed: 2026-02-15
Summary: Closed after user acceptance; implementation and validation artifacts are recorded in this ticket.


## Metadata
- Task ID: TASK-2026-02-14-discovery-jit-aot-resolution-required-spell-contract
- Story: STORY-2026-02-14-jit-aot-split-discovery-and-viability
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-15

## Objective
Define a concrete lifecycle contract for `resolution_required: bool` on spells,
including who sets it, who clears it, and how it interacts with validity gates.

## Scope Boundaries
- In scope:
- Spell lifecycle and runtime gating semantics tied to deferred resolution.
- Out of scope:
- Implementing the field and runtime behavior in code.

## Steps / Checklist
- [x] Identify current spell lifecycle states relevant to structural and resolution readiness.
- [x] Identify where runtime gating currently revalidates/executes resolution.
- [x] Draft lifecycle table for `resolution_required` transitions.
- [x] Define fail-fast conditions when deferred resolution cannot complete.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- One `resolution_required` lifecycle table with transitions and owners.
- One recommendation for validity behavior in split mode.

## `resolution_required` Lifecycle Table (2026-02-15)
| Transition | Owner | Trigger | Required Action | Evidence |
|---|---|---|---|---|
| `False -> True` (deferred runtime needed) | split-mode orchestration (new JIT/AOT config path) | Any event that gates structural/resolution readiness after a spell was previously runnable (structural mutation, dependency/contract gating, execution-plan refresh) | Mark spell as requiring runtime resolution before context build; keep creation-context invalidated/cleaned as needed. | `src/melder/spellbook/spell.py:1151-1159`, `src/melder/spellbook/spell.py:1439-1477`, `src/melder/aether/dev_ops/spell_system_states/spell_system_state.py:400-424`, `src/melder/aether/conduit/meld/meld.py:734-774` |
| `True -> False` (runtime resolution satisfied) | runtime gate near meld resolution path | Resolution validity reaches `valid` for the active conduit after gated/unknown revalidation path runs | Clear `resolution_required` immediately before first context build/read path to keep flag/state aligned with effective readiness. | `src/melder/aether/conduit/meld/meld.py:569-616`, `src/melder/aether/conduit/meld/meld.py:336-348`, `src/melder/spellbook/spell.py:469-497` |
| `True -> ERROR` (deferred runtime could not resolve) | runtime gate near meld resolution path | Resolution validity is `invalid`/`disabled`/`cleaned`, or remains unresolved after revalidation attempt | Fail fast with validation error; do not build/use creation context. | `src/melder/aether/conduit/meld/meld.py:590-619`, `src/melder/spellbook/spellbook_creation_system.py:1509-1519` |
| `any -> True` (re-gate after contract/mutation changes) | contract/mutation-change paths | SpellContract revalidation forced or mutation overlay toggled | Re-gate resolution, invalidate cached context, and require runtime resolution again before build. | `src/melder/aether/conduit/meld/meld.py:621-774`, `src/melder/spellbook/spell.py:1439-1477` |

### Recommendation
Use `resolution_required` as an orchestration marker only, not a second validity system. Keep `SpellSystemState` and `ConduitResolutionState` as the source of truth, and let `resolution_required` mirror whether runtime revalidation must run before context build on the current access path.

## Files / Paths Impacted
- `src/melder/spellbook/spell.py`
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/spellbook/spellbook.py`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "run_structural_phases|run_all_phases|_get_or_build_creation_context" src/melder/spellbook/spell.py`
  - `rg -n "_ensure_lineage_resolvable|_run_resolution_phases_for_target_spell" src/melder/aether/conduit/meld/meld.py src/melder/spellbook/spellbook.py`

## Risks / Rollback Notes
- Risk: Poorly defined flag semantics could hide invalid-state bugs.
- Rollback: discovery-only task; no runtime code changes in this task.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [x] Acceptance criteria reviewed with user and confirmed
## Notes
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Existing runtime already enforces structural/resolution validity gates before context retrieval and contains explicit fail-fast outcomes for unresolved/invalid resolution states.
  EVIDENCE: src/melder/aether/conduit/meld/meld.py:336-348, src/melder/aether/conduit/meld/meld.py:402-458, src/melder/aether/conduit/meld/meld.py:569-619, src/melder/spellbook/spell.py:469-497
  IMPACT: `resolution_required` should hook into this existing gate sequence instead of introducing a parallel resolver entrypoint.
  NEXT: Finalize lifecycle transitions with owner/trigger table and propose integration behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: Recommend `resolution_required` as a lightweight orchestration flag that mirrors existing validity-gate needs (`True` when revalidation is required before build, `False` after gate passes), with fail-fast semantics delegated to current meld/validation paths.
  EVIDENCE: src/melder/aether/conduit/meld/meld.py:569-619, src/melder/aether/conduit/meld/meld.py:621-774, src/melder/spellbook/spell.py:1151-1159, src/melder/spellbook/spell.py:1439-1477, src/melder/aether/dev_ops/spell_system_states/spell_system_state.py:400-424, src/melder/aether/dev_ops/spell_system_states/conduit_resolution_state.py:17-51
  IMPACT: Minimizes state-model churn and keeps split-mode behavior aligned with existing validity ownership.
  NEXT: Surface this lifecycle table to user and, on approval, create implementation tasks for flag wiring + runtime gate clear/set points.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: DECISION
  CLAIM: Activated this task as the next epic discovery tranche after completing builder/factory contract matrix; focus now is an explicit `resolution_required` lifecycle transition table.
  EVIDENCE: context_compass/tasks/2026-02-14_discovery_jit_aot_creation_context_builder_runtime_contract_task.md:34-44, context_compass/tasks/2026-02-14_discovery_jit_aot_creation_context_builder_runtime_contract_task.md:103-106
  IMPACT: Epic discovery proceeds without waiting idle on implementation approval.
  NEXT: Extract spell/meld/runtime validity hooks and draft lifecycle transition table with owners and fail-fast points.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Meld runtime already includes lineage revalidation and conduit-scoped resolution gating before instance resolution, and spells expose both structural-only and full phase helpers.
  EVIDENCE: src/melder/aether/conduit/meld/meld.py:402-430, src/melder/spellbook/spell.py:1270-1336, src/melder/spellbook/spellbook.py:3075-3150
  IMPACT: `resolution_required` should likely integrate with existing lineage gating rather than inventing a parallel state system.
  NEXT: Draft transition table and review with user in assumption-challenge discussion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Lifecycle discovery is complete with an evidence-backed transition table and
recommendation. Next step is user acceptance, then implementation task creation
for `resolution_required` set/clear wiring around existing runtime validity gates.


