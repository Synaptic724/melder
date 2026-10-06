# architecture_patch

## Metadata
- Patch ID: injected_provider_first_direct_meld_2026_09_30
- Status: active
- Owner: user (agent melder_0)
- Created: 2026-09-30T19:31:23Z
- Updated: 2026-09-30T19:31:23Z

## Patch Scope and Non-Goals
- Objective (the owner's option B): a spell bound after conjure and first built as a consumer's dependency melds
  directly afterwards and returns the instance its scope already holds. The consumer's target-local resolution pass
  flags every dependency its Book owns that the pass compiled only inside the consumer's plan - no phase-11 plan and
  no published CreationContext of its own - with `resolution_required`. That dependency's first meld runs its own
  full target pass (phases 5-11) through the deferred lane, which today runs only 8-11 and silently skips a spell
  that has no Phase 5 root blueprint.
- Non-goals: conduit verdicts and the Book validation flag stay as they are (option A, truthful verdicts at local
  Phase 6, is not taken); no public validation trigger and no caller step; the conduit-wide pass, bind, notch,
  transfer and the conjure cache are unchanged; MelderOps revalidation (work package D) is separate.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| SpellCompiler and Validation Pipeline (the target-local pass) | modify | the pass leaves an owned dependency it compiled inside the target's plan with no plan of its own, stamped valid | none |
| Meld Resolution Runtime (the deferred lane) | modify | the lane's 8-11 pass cannot compile a spell with no Phase 5 root blueprint | the target pass flag |
| Spellbook Core; CreationContextRebuild | comments only | three comments give "the deferred lane cannot compile it" as a reason | the lane change |

## Interface and Boundary Deltas
- Internal addition: `SpellbookCreationSystem.flag_dependencies_without_own_plan(spellbook, target_spell_id,
  scoped_spell_ids) -> tuple[str, ...]`, called on the success path of `run_resolution_phases_for_target_spell`.
- `Meld._ensure_runtime_resolution_ready`: a flagged spell that is neither an existing creation nor its current
  Phase 5 root runs `Spellbook._run_resolution_phases_for_target_spell` (5-11) and must then read resolution-valid
  for the conduit, else SpellbookValidationError; every other flagged spell keeps
  `_run_deferred_resolution_phases_for_target_spell` (8-11).
- No public API change and no new error type. The direct meld that raised RuntimeError "Cannot build
  CreationContext before spell_codegen_creation exists." returns the instance.

## Cross-Component Invariants
- After a successful target-local pass, every spell in its Phase 5 scope that the Book owns, that is resolvable and
  that is not an existing creation has a phase-11 plan, or a published CreationContext, or `resolution_required`.
- The flag is written under the dependency's spell lock, taken after the target's (consumer before dependency, the
  build-lock order), so it cannot interleave with that dependency's own resolution lane.
- Both passes of the deferred lane run inside the spell's rebuild window and spell lock, as the 8-11 pass does today.
- The flag changes no verdict; the dependency's own pass stamps its root verdict, as a provider-first meld does.
- Warm melds and spells with a plan are untouched: the doors already read `resolution_required` lock-free.

## Migration Order
1. Component regression tests red (done: 11 failed, the 2 controls pass); unit tests red.
2. The flag helper and its call at the target pass tail; the deferred lane's routing; docstrings and comments.
3. Green: the new tests, the meld, spellbook, conduit and aether suites, the epic's probe. Notch 0.2.8215.
4. System docs, graph descriptors, release note; assets and LLM bundles last.

## Rollback
- Revert the two logic edits together (the comment edits may stay or go); no record, cache or API shape changes.

## Ticket Coverage Matrix
| patch section | ticket |
|---|---|
| all | tickets/tasks/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md |
