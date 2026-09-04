# Task: Preserve the established disposal list through Creations

## Metadata
- Task ID: TASK-2026-09-04-ordered-disposal-creations
- Story: STORY-2026-09-04-ordered-disposal-runtime
- Story Ticket: `tickets/stories/2026-09-04_ordered_disposal_runtime_story.md`
- Epic Ticket: `tickets/epics/2026-09-02_ordered_live_spell_disposal_epic.md`
- Status: ready
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-04T21:17:27Z
- Updated: 2026-09-04T22:06:16Z

## Objective
Have Creations retain and consume the established Spell disposal list directly, including
extraction/restoration, while preserving existing lifetime and cleanup behavior.

## Ticket Contract
- ENTRY_GATE: Binding/compiler tasks verified, runtime patch consumed, and board routes here.
- EXECUTION_BOUNDARY: Creations disposal metadata registration, extraction/restoration,
  existing invocation loop, and focused real runtime checks.
- DEPENDENCIES: `tickets/tasks/2026-09-04_ordered_disposal_compiler_propagation_task.md`.
- EXIT_GATE: Actual cleanup follows the exact established method order; direct metadata
  ownership survives supported extraction/restoration without changing lifetime routing.
- FAILURE_ESCALATION: Record a real ownership/teardown conflict; do not solve hypothetical
  private-field mutation or expand into unrelated scheduling/locking repairs.

## Scope Boundaries
- In scope: disposal names accompanying existing object records and their consumption.
- Out of scope: new configuration reads, new reflection probes, new disposal scopes or methods.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Owner requested a separate scoped Creations implementation task.

## Required Reading and Evidence
Navigate Component: Creations and SpellSpace / Subcomponent: Creations Disposal Pipeline;
read the full Creations file and the affected caller methods before editing.
- `src/melder/aether/conduit/creations/creations.py:93-354` (registration/cleanup)
- `src/melder/aether/conduit/creations/creations.py:369-500` (extract/restore)
- `src/melder/aether/conduit/conduit.py:1386-1428` (existing-object forwarding)
- `src/melder/aether/spellbook/spell.py:500-603` (metadata cleanup ownership)
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1500-1584`
- `tests/unit/melder/aether/conduit/creations/test_creations_disposal_all_methods_regression.py:1-211`
- Reopen reverse-order regressions and relevant test architecture/components.

## Steps / Checklist
- [ ] Remove redundant method-list copies in add_creation/add_many_creations.
- [ ] Preserve the same established list through extraction and restoration of stored objects.
- [ ] Keep has_disposal_methods gating, no-disposal paths, and existing many/singleton routing.
- [ ] Preserve the invocation loop and current stop-on-first-method-failure behavior.
- [ ] Preserve reversed registry and many-bucket traversal; do not promise a stronger total
      chronology across interleaved keys than the existing implementation provides.
- [ ] Verify list lifetime against Spell/Creations teardown: do not clear a shared list while
      another owner may still need its names for real instance cleanup.
- [ ] Test real bind/meld/cleanup in both priority modes; record results and remaining gaps.

## Deliverables
Direct list ownership in Creations, accurate contracts, and meaningful cleanup regressions.

## Files / Paths Impacted
- `src/melder/aether/conduit/creations/creations.py`
- Direct caller changes only if the explicit list contract cannot already be forwarded.
- `tests/unit/melder/aether/conduit/creations/test_creations.py`
- `tests/unit/melder/aether/conduit/creations/test_creations_disposal_all_methods_regression.py`
- `tests/unit/melder/aether/conduit/creations/test_creations_disposal_reverse_order_regression.py`
- `tests/component/melder/aether/conduit/test_conduit_component_creations.py`
- `tests/integration/melder/conduit/test_conduit_integration_disposal_ordering.py`

## Validation
- Not run; ticket only. Use supported Python 3.14.
- Methods record actual call order, with class definition order intentionally different.
- Cover singleton and many entries, reusable clear/pool cleanup, and extract/restore.
- Preserve failure handling: later methods on one failing object stop, other entries continue.
- Verify many objects without matched names remain on their current untracked path.
- Assertions about list identity are justified only by the explicit sharing requirement.

## Risks / Rollback Notes
The current Creations loop already invokes all names in stored sequence. Avoid rewriting it
to solve a producer-order problem. No new getattr/hasattr existence check is requested.

## Applicable Anti-Patterns
- [ ] No duplicate configuration enforcement during disposal.
- [ ] No new snapshots or defensive owned-field guards.

## Done Checklist
- [ ] Real cleanup order and transfer metadata tests verified.
- [ ] Source/contracts and notes updated; downstream replay unblocked.
- [ ] Owner accepts closure; no unrequested ticket cleanup.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false at ticket creation
- ARTIFACT_PATHS: none yet; consume actual runtime patch first
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: accepted program closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: instance cleanup, reference lifetime, extraction/restoration
- IF_UNKNOWN: none

## Noting Behavior
Capture real ownership and behavioral findings before continuing; separate existing from changed behavior.

## Notes
- DATETIME: 2026-09-04T21:17:27Z
  TYPE: PLAN
  CLAIM: Creations currently copies names at registration/transfer and invokes them sequentially.
  EVIDENCE:
  - `src/melder/aether/conduit/creations/creations.py:197-354`
  - `src/melder/aether/conduit/creations/creations.py:369-500`
  IMPACT: Change metadata ownership narrowly while retaining actual cleanup semantics.
  NEXT: Consume the runtime patch and read the full Creations implementation/callers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:58:36Z
  TYPE: FACT
  CLAIM: Full Creations and ConduitCreations reads confirm six method-list copy sites:
    singleton/many registration, singleton/many extraction, and singleton/many restoration.
    ConduitCreations delegates without another conversion. The existing-object Conduit
    caller already forwards Spell metadata. The invocation loop uses the stored sequence
    directly and stops only that object's chain on its first failure; the outer loop
    continues in reversed-key/reversed-bucket order and aggregates failures.
  EVIDENCE:
  - `src/melder/aether/conduit/creations/creations.py:197-357`
  - `src/melder/aether/conduit/creations/creations.py:369-500`
  - `src/melder/aether/conduit/creations/conduit_creations.py:95-133`
  - `src/melder/aether/conduit/conduit.py:1386-1428`
  - `src/melder/aether/spellbook/spell.py:500-603`
  IMPACT: Retain the established inner list through the six contacts; preserve registry
    detachment before cleanup, which is a real lifecycle operation, not a disposable-list
    snapshot to remove. Spell cleanup deletes its name reference without clearing the
    collection, so other holders can still use it. Do not introduce list.clear() there.
    Existing registration locks, scoped-store selection, cleanup failure behavior, and
    no-disposable fast paths remain unchanged.
  NEXT: At implementation, verify real cleanup and extract/restore behavior using the
    producer/compiler list contract, including clear_all and pool reuse.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
The invocation loop already runs names in order; upstream frozensets caused order loss.
Preserve existing error behavior and scope traversal. No implementation yet.
Next: `tickets/tasks/2026-09-04_ordered_disposal_crystal_replay_task.md`.
