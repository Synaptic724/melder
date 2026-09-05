# Story: Preserve ordered disposal through compilation and Creations

## Metadata
- Story ID: STORY-2026-09-04-ordered-disposal-runtime
- Epic: EPIC-2026-09-02-ordered-live-spell-disposal
- Epic Ticket: `tickets/epics/2026-09-02_ordered_live_spell_disposal_epic.md`
- Status: review
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-04T21:17:27Z
- Updated: 2026-09-05T10:33:58Z

## User Narrative
As a Melder user, I want each instance disposed in its Spell's established method order
across compiled execution families and supported lifetime scopes.

## Value / MRP Alignment
The binding contract must reach real cleanup, including cached execution paths.

## Ticket Contract
- ENTRY_GATE: Story 1 binding result and applicable patch contracts are available;
  route the selected child task and read its scoped source before editing.
- EXECUTION_BOUNDARY: Disposal metadata in compiler records/plans/namespaces, Creations
  registration/transfer/cleanup, and directly relevant behavioral tests.
- DEPENDENCIES: `tickets/stories/2026-09-04_ordered_disposal_binding_story.md`.
- EXIT_GATE: Both child tasks demonstrate correct method order and established list ownership.
- FAILURE_ESCALATION: Stop on a real compiler/cache representation conflict; preserve the
  documented cache value schema and investigate before changing it.

## Requirements (Functional)
- Runtime consumers use the Spell-owned resolved list directly.
- The priority flag is already resolved; do not re-read configuration at disposal.
- Preserve current registration gates and lifetime-store selection.
- Preserve current cleanup failure behavior and reversed registry/bucket traversal.
- Cold and cached executors must produce identical disposal order.

## Requirements (Non-Functional)
- No new hot-path guards, locks, reflection probes, or mutation callbacks.
- Distinguish an outer tuple of list references from copying each inner disposal list.
- Hash/serialized IR values may require a value projection; document those real boundaries.

## Scope Boundaries
- In scope: compiler disposal propagation and Creations metadata ownership.
- Out of scope: source selection, scope redesign, unrelated locking bugs, crystal replay.

## State Transition Event
- from_state: ready
- to_state: review
- transition_reason: Both runtime tasks are implemented and the combined boundary passes 2,797 tests.

## Dependencies / Related Work
- Contract: `tickets/tasks/2026-09-04_ordered_disposal_patch_contract_task.md`
- Binding: `tickets/tasks/2026-09-04_ordered_disposal_bind_and_spell_task.md`
- Next: `tickets/stories/2026-09-04_ordered_disposal_persistence_story.md`

## Tasks (Implementation Checklist)
- [x] `tickets/tasks/2026-09-04_ordered_disposal_compiler_propagation_task.md` (implemented/in review)
- [x] `tickets/tasks/2026-09-04_ordered_disposal_creations_task.md` (implemented/in review)

## Acceptance Criteria
- Real creation/cleanup uses the exact agreed sequence for both priority modes.
- Lists are not sorted or converted into unordered sets by runtime consumers.
- Existing no-disposal, many, singleton, and scoped registration behavior remains valid.
- No claim of complete runtime coverage without recorded executed checks.

## Validation / Test Plan
Focused compiler-family, cache rehydration, Creations, and real bind/meld/cleanup tests.
Passed: 2,797 selected tests on Windows Python 3.14.0 free-threaded; 51 new regression cases.
Full repository/cross-platform/persistent replay validation and final assets remain pending.

## UX / API / Data Notes
Disposal methods are invoked on the user's instance. Spell holds names, not bound methods.
Missing names are handled during binding under the existing profile boundary.

## Risks / Mitigations
- Removing every tuple mechanically can break schema rows: classify uses before editing.
- Clearing the shared method list during teardown can affect other consumers: drop references
  according to ownership, preserving the existing actual-instance cleanup sequence.

## Applicable Anti-Patterns
- [ ] No compiler rewrite unrelated to disposal metadata.
- [ ] No duplicated live-list owners or private-mutation guards.

## Open Questions
- Family-specific propagation details must be verified from complete source before edits.

## Decision Log
- Method order is established at creation and consumed directly afterward.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none yet; use contract task outputs when created.
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: final accepted program closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: compiler families, list ownership, Creations
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-04T21:17:27Z
  TYPE: PLAN
  CLAIM: Two runtime tasks separate compilation from actual instance storage/disposal.
  EVIDENCE:
  - `src/melder/aether/conduit/creations/creations.py:197-354`
  - `src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_runtime_processor_strategy.py:38-100`
  IMPACT: Consumer work follows the producer contract without changing its policy.
  NEXT: After binding is verified, trace compiler record and plan propagation first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Both tasks are verified and the owner accepts the runtime result.

## Noting Behavior
Record cross-family outcomes and dependencies here; keep tactical evidence in child tasks.

- DATETIME: 2026-09-05T10:33:58Z
  TYPE: MEASURE
  CLAIM: Compiler and Creations propagation are implemented. Seven compiler files and the
    Creations storage owner retain established lists; serialized/hash values stay ordered.
    Real runtime tests found and eliminated two copies embedded in generalized emitted code.
    All 2,797 selected tests pass, including repeated real melds and both priority/override modes.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-09-04_ordered_disposal_compiler_propagation_task.md`
  - `context_compass/tickets/tasks/2026-09-04_ordered_disposal_creations_task.md`
  IMPACT: Runtime phase is in review. No new locks, cleanup-loop rewrite, or mutation support.
  NEXT: Complete configuration transport verification before crystal replay implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Both child tasks are implemented/in review. The combined selected boundary passes 2,797 tests.
The runtime retains one established inner list through compilation, registration, and transfer.
Methods execute in order; existing failure, reverse traversal, and scope cleanup stay unchanged.
Next: configuration transport verification, then persistent capture/restore/graft order and assets.
