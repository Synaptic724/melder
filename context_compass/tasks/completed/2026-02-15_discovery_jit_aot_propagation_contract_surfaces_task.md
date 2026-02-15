# Task: Discovery - JIT/AOT Propagation Contract Surfaces



Completed: 2026-02-15
Summary: Closed after user acceptance; implementation and validation artifacts are recorded in this ticket.


## Metadata
- Task ID: TASK-2026-02-15-discovery-jit-aot-propagation-contract-surfaces
- Story: STORY-2026-02-14-jit-aot-split-discovery-and-viability
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-15

## Objective
Map the exact source touchpoints for JIT/AOT mode propagation so implementation
can proceed without widening scope or breaking owner semantics.

## Scope Boundaries
- In scope:
- Config/fluent API property surface for `full_ahead_of_time_compilation`.
- Conjure-time stamp path for local/owned spells.
- Late-bind stamp path after conduit exists.
- Transfer-of-ownership propagation path for owned spells only.
- Confirmation that contracted spells keep their existing owner semantics.
- Runtime gate touchpoint for `resolution_required` set/clear.
- Out of scope:
- Any implementation edits in `src/`.

## Steps / Checklist
- [x] Confirm config property defaults and fluent API insertion points.
- [x] Confirm conjure-time ownership stamping insertion point.
- [x] Confirm bind-after-conjure stamping insertion point.
- [x] Confirm transfer ownership owned-only propagation points and contracted-spell exclusions.
- [x] Confirm runtime gate insertion point for `resolution_required`.
- [x] Produce implementation order and file list for downstream tasks.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- One evidence-backed propagation map covering config, conjure, bind, transfer,
  and runtime gate surfaces.
- One explicit implementation order for downstream tasks.

## Propagation Contract-Surface Map (2026-02-15)
| Lane | Touchpoint | Evidence | Decision |
|---|---|---|---|
| Config + fluent API | `Configuration.available_properties`, defaults loader, and fluent methods | `src/melder/spellbook/configuration/configuration.py:76-85`, `src/melder/spellbook/configuration/configuration.py:437-450`, `src/melder/spellbook/configuration/configuration.py:785-919` | Add `full_ahead_of_time_compilation: bool` with default `true` and fluent setter(s). |
| Conjure propagation | Conduit-into-spells ownership wiring loop | `src/melder/spellbook/spellbook_creation_system.py:474-485` | Stamp mode-derived spell state during this loop for local owned spells. |
| Post-conjure bind propagation | Existing late-bind owner stamp branch when conduit already exists | `src/melder/spellbook/spellbook.py:2534-2574` | Apply same mode propagation here for newly bound spells after conjure. |
| Transfer owned-only propagation | Spellbook/owner flip path and owned-dependency transfer guard | `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:890-956`, `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1169-1173` | Re-stamp destination defaults only on owned lineages in transfer flow. |
| Contracted-spell exclusion | Contracted map attach path separate from owned transfer path | `src/melder/spellbook/spellbook.py:1428-1471`, `src/melder/spellbook/spellbook.py:238-239` | Keep contracted spells under contracted ownership semantics; do not owner-rewrite them in transfer propagation. |
| Runtime gate lifecycle | Meld revalidation gate before context build + per-conduit resolution re-run | `src/melder/aether/conduit/meld/meld.py:336-348`, `src/melder/aether/conduit/meld/meld.py:402-430`, `src/melder/aether/conduit/meld/meld.py:569-619` | Implement `resolution_required` orchestration in this runtime gate path, not in builder/factory internals. |

## Implementation Order (Downstream)
1. `TASK-2026-02-15-implement-jit-aot-config-flag-and-fluent-api`
2. `TASK-2026-02-15-implement-jit-aot-conjure-propagation`
3. `TASK-2026-02-15-implement-jit-aot-post-conjure-bind-propagation`
4. `TASK-2026-02-15-implement-jit-aot-transfer-ownership-propagation-non-contracted`
5. `TASK-2026-02-15-implement-jit-aot-runtime-resolution-gate-lifecycle`
6. `TASK-2026-02-15-implement-jit-aot-regression-matrix-and-compatibility`

## Files / Paths Impacted
- `src/melder/spellbook/configuration/configuration.py`
- `src/melder/spellbook/spellbook_creation_system.py`
- `src/melder/spellbook/spellbook.py`
- `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`
- `src/melder/aether/conduit/meld/meld.py`
- `context_compass/stories/2026-02-15_jit_aot_config_flag_and_fluent_api_story.md`
- `context_compass/stories/2026-02-15_jit_aot_conjure_propagation_story.md`
- `context_compass/stories/2026-02-15_jit_aot_post_conjure_bind_propagation_story.md`
- `context_compass/stories/2026-02-15_jit_aot_transfer_ownership_propagation_non_contracted_story.md`
- `context_compass/stories/2026-02-15_jit_aot_runtime_resolution_gate_lifecycle_story.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "load_default_dictionary|with_system_state|with_defaults" src/melder/spellbook/configuration/configuration.py`
  - `rg -n "define_conduit_into_spells|_add_owned_conduit|_set_owner_conduit_id" src/melder/spellbook/spellbook_creation_system.py src/melder/spellbook/spellbook.py`
  - `rg -n "_add_contracted_spell|transfer_spell_ownership|_transfer_owned_dependencies" src/melder/spellbook/spellbook.py src/melder/aether/conduit/conduit.py src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`
  - `rg -n "_ensure_lineage_resolvable|_run_resolution_phases_for_target_spell|_get_or_build_creation_context" src/melder/aether/conduit/meld/meld.py src/melder/spellbook/spell.py`

## Risks / Rollback Notes
- Risk: Missing one propagation surface can reintroduce mode drift.
- Mitigation: Keep this discovery gate mandatory before implementation tasks.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [x] Acceptance criteria reviewed with user and confirmed
## Notes
- DATE: 2026-02-15
  TYPE: FACT
  CLAIM: Discovery confirms all required propagation surfaces and preserves the user constraint that transfer propagation must be owned-only while contracted spells retain contracted owner semantics.
  EVIDENCE: src/melder/spellbook/configuration/configuration.py:76-85, src/melder/spellbook/configuration/configuration.py:437-450, src/melder/spellbook/configuration/configuration.py:785-919, src/melder/spellbook/spellbook_creation_system.py:474-485, src/melder/spellbook/spellbook.py:2534-2574, src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:890-956, src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1169-1173, src/melder/spellbook/spellbook.py:1428-1471, src/melder/spellbook/spellbook.py:238-239, src/melder/aether/conduit/meld/meld.py:336-348, src/melder/aether/conduit/meld/meld.py:402-430, src/melder/aether/conduit/meld/meld.py:569-619
  IMPACT: Implementation can proceed without further repo-wide discovery sprawl.
  NEXT: Move this task to review and route active execution to `TASK-2026-02-15-implement-jit-aot-config-flag-and-fluent-api`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATE: 2026-02-15
  TYPE: PLAN
  CLAIM: Discovery starts from confirmed touchpoints: defaults/fluent API in Configuration, conjure-time ownership stamping in SpellbookCreationSystem, late-bind ownership stamping in Spellbook.bind, owned-only dependency transfer checks in TransferOfOwnership, contracted spell registration path in Spellbook, and runtime resolution gate in Meld.
  EVIDENCE: src/melder/spellbook/configuration/configuration.py:431-450, src/melder/spellbook/configuration/configuration.py:785-918, src/melder/spellbook/spellbook_creation_system.py:457-485, src/melder/spellbook/spellbook.py:2534-2574, src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1160-1173, src/melder/spellbook/spellbook.py:1428-1468, src/melder/aether/conduit/meld/meld.py:402-430, src/melder/aether/conduit/meld/meld.py:569-619
  IMPACT: This keeps implementation scoped and aligned to the user-approved propagation contract.
  NEXT: Produce a concrete file/symbol implementation order and map each target story/task to those touchpoints.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Discovery gate is complete with an evidence-backed propagation map and
implementation order. Next active lane is config flag/fluent API implementation.


