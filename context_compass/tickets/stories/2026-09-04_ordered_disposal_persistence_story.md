# Story: Preserve disposal order in recorded worlds and public documentation

## Metadata
- Story ID: STORY-2026-09-04-ordered-disposal-persistence
- Epic: EPIC-2026-09-02-ordered-live-spell-disposal
- Epic Ticket: `tickets/epics/2026-09-02_ordered_live_spell_disposal_epic.md`
- Status: ready
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-04T21:17:27Z
- Updated: 2026-09-04T21:17:27Z

## User Narrative
As a Melder user, I want recorded and restored worlds to retain disposal policy and order,
with documentation and examples that describe the behavior that actually ships.

## Value / MRP Alignment
Order is only a dependable feature when it survives persistence and every supported path.

## Ticket Contract
- ENTRY_GATE: Producer/runtime results and applicable patch contracts are available;
  activate one child through the attention board.
- EXECUTION_BOUNDARY: SpellCrystal order, active/staged restore and graft, relevant docs,
  generated assets, and final cross-boundary verification.
- DEPENDENCIES: The binding and runtime stories; configuration transport task.
- EXIT_GATE: All three child tasks are verified, artifacts/docs are synchronized, and
  owner accepts program closure. No automatic commit, push, or release.
- FAILURE_ESCALATION: Escalate a real replay identity or differing-host-policy conflict;
  do not silently change recorded identity or invent historical order.

## Requirements (Functional)
- Preserve ordered lists in SpellCrystal instead of alphabetical sorting.
- Restore configuration and its priority flag before rebuilding Spells.
- Include disposal metadata in active/staged, selected/parked/merged replay paths.
- Keep defaults False, first-occurrence deduplication, and class-profile matching scope.
- Public examples cover both priority values and the relationship between book/spell names.

## Requirements (Non-Functional)
- Preserve the passive recorder model; do not move disposal execution into Crystallizer.
- Use existing generic book payloads; avoid duplicate Nexus/Crystallizer priority settings.
- Keep generated assets generated and preserve other agents' documentation work.

## Scope Boundaries
- In scope: the final order contract across record/replay and documentation.
- Out of scope: Nexus rich-config API expansion, unrelated restore redesign, publication.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Owner requested tasks covering later persistence and completion phases.

## Dependencies / Related Work
- `tickets/stories/2026-09-04_ordered_disposal_binding_story.md`
- `tickets/stories/2026-09-04_ordered_disposal_runtime_story.md`
- `tickets/tasks/2026-09-04_disposal_configuration_roundtrip_task.md`

## Tasks (Implementation Checklist)
- [ ] `tickets/tasks/2026-09-04_ordered_disposal_crystal_replay_task.md`
- [ ] `tickets/tasks/2026-09-04_ordered_disposal_docs_assets_task.md`
- [ ] `tickets/tasks/2026-09-04_ordered_disposal_end_to_end_validation_task.md`

## Acceptance Criteria
- Recorded configuration True/False and final names preserve agreed replay behavior.
- No staged/graft omission reintroduces different disposal metadata.
- Runtime and replay outputs agree for the covered supported scopes and compiler families.
- Source assets are regenerated before repository/LLM assets; both freshness checks pass.
- All claims distinguish executed tests from planned or unavailable matrix cells.

## Validation / Test Plan
Child tasks own round-trip, documentation, and final verification. Not run yet.

## UX / API / Data Notes
Book twins hold the configuration; Spell crystals hold resolved method names. These are
different records. Existing old records have already sorted away some original ordering;
do not claim that missing information can be reconstructed without evidence.

## Risks / Mitigations
- Grafting into a differently configured host can change the resolved list and SHA: trace
  identity/selection joins before choosing a replay policy.
- Public documentation may overlap codex_2's Read the Docs work: inspect current boards and
  working changes before editing common files. No agents are delegated by this task stack.

## Applicable Anti-Patterns
- [ ] No hand edits to generated graph/index/payload/corpus files.
- [ ] No claim of historical order restoration from information the record does not contain.

## Open Questions
- Different-host graft policy remains to be traced; the default is not an invented migration.

## Decision Log
- Complete the existing three phases; preserve generic configuration transport.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none yet; link actual patch outputs when available.
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: canonical doc merge and owner-accepted closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: replay, documentation, generated assets, final checks
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-04T21:17:27Z
  TYPE: PLAN
  CLAIM: Phase 3 separates replay implementation, documentation/assets, and final validation.
  EVIDENCE:
  - `src/melder/crystallizer/crystals/spell_crystal.py:143-339`
  - `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1734-2002`
  IMPACT: Completion includes restored behavior and user-facing evidence, not just binding.
  NEXT: After runtime verification, execute the crystal/replay task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] All tasks verified, artifact disposition applied, and owner accepts closure.

## Noting Behavior
Keep cross-task acceptance and release-readiness evidence here; child tasks carry details.

## Context / Handoff Summary
Replay follows producer/runtime work. Documentation and generated assets follow replay.
Final validation reconciles all tasks and available platform evidence without publishing.
No implementation has started, and the discovery probe was not a full Melder test run.

