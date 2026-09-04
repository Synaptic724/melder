# Task: Preserve resolved disposal order through crystals and replay

## Metadata
- Task ID: TASK-2026-09-04-ordered-disposal-crystal-replay
- Story: STORY-2026-09-04-ordered-disposal-persistence
- Story Ticket: `tickets/stories/2026-09-04_ordered_disposal_persistence_story.md`
- Epic Ticket: `tickets/epics/2026-09-02_ordered_live_spell_disposal_epic.md`
- Status: ready
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-04T21:17:27Z
- Updated: 2026-09-04T21:17:27Z

## Objective
Preserve the final method-list order in SpellCrystal and all existing active/staged
restore and graft paths, using the already established configuration and binding policy.

## Ticket Contract
- ENTRY_GATE: Configuration transport and runtime tasks verified; persistence patch read;
  activate this task on the board before implementation.
- EXECUTION_BOUNDARY: SpellCrystal metadata capture, RestoreEngine active/staged binds,
  GraftRunner selected/parked/merge binds, and targeted round-trip tests.
- DEPENDENCIES:
  `tickets/tasks/2026-09-04_disposal_configuration_roundtrip_task.md`
  `tickets/tasks/2026-09-04_ordered_disposal_creations_task.md`
- EXIT_GATE: Preserved ordered names and policy across supported replay paths, with explicit
  evidence for identity joins and any differing-host case still unresolved.
- FAILURE_ESCALATION: Stop on a real host-policy/recorded-identity conflict; no silent mapping
  fix or assumed historical order. Record the exact case and ask only if a user policy is needed.

## Scope Boundaries
- In scope: existing replay grammar, ordered metadata, and missing disposal forwarding.
- Out of scope: new loader architecture, ownership-transfer policy, broader binding families.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Owner requested a separate persistence task after the producer/runtime phases.

## Required Reading and Evidence
Navigate the Crystallizer component and graph rows, then read implementations in full before edits.
- `src/melder/crystallizer/crystals/spell_crystal.py:143-339` (sorted capture)
- `src/melder/crystallizer/crystals/spell_crystal.py:644-661` (property)
- `src/melder/crystallizer/crystals/spell_crystal.py:1064-1138` (describe entry)
- `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1734-1822` (config before binds)
- `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1903-2002` (active/staged)
- `src/melder/crystallizer/crystal_loader_system/graft_runner.py:371-530` (selected/parked/merge)
- Source/test continuations for selection mapping must be read before assuming SHA stability.

## Steps / Checklist
- [ ] Capture ordered values in SpellCrystal without sorting and update its property contract.
- [ ] Preserve metadata in active replay and forward it in staged replay.
- [ ] Forward names for selected, parked, and merged graft members.
- [ ] Trace replay of already-resolved names through the new two-group composition rule;
      prove repeated composition under the same recorded config does not change final order.
- [ ] Trace grafting into a different host config, including anchor lookups by recorded SHA.
      Record any policy question instead of silently treating old/new IDs as interchangeable.
- [ ] Test both priority values, non-alphabetical names, missing/duplicate names, and staged members.
- [ ] Reuse the configuration transport task's evidence; do not add duplicate flag fields.
- [ ] Record results and outstanding compatibility limits before documentation work.

## Deliverables
Order-preserving crystal capture/replay and source-backed identity/selection behavior.

## Files / Paths Impacted
- `src/melder/crystallizer/crystals/spell_crystal.py`
- `src/melder/crystallizer/crystal_loader_system/restore_engine.py`
- `src/melder/crystallizer/crystal_loader_system/graft_runner.py`
- `tests/unit/melder/crystallizer/persistence/test_restore_engine.py`
- Relevant existing graft tests located through the test index.
- `tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py`
- Focused test additions within the existing Crystallizer hierarchy when necessary.

## Validation
- Not run; ticket only. Use a verified supported interpreter.
- Same recorded configuration -> same final ordered methods and appropriate new-world identities.
- Exercise both active and inactive members and all selected/parked/merge forwarding paths.
- Verify resulting cleanup calls, not only persisted list equality.
- Distinguish configuration-flag round trips from complete restored-instance disposal.

## Risks / Rollback Notes
Old SpellCrystal records sorted the names, and old frozenset fingerprints could vary with
hash seed. Do not promise recovery of lost original order. Treat legacy compatibility as
an evidenced data question, not a reason for an invented fallback or blanket ID rewrite.

## Applicable Anti-Patterns
- [ ] No hidden replay policy decision for differently configured hosts.
- [ ] No config enforcement or disposal execution added to the passive Crystallizer.

## Done Checklist
- [ ] Capture/replay changes and focused tests verified.
- [ ] Compatibility limits and actual identity joins documented.
- [ ] Documentation task unblocked; owner accepts closure.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false at ticket creation
- ARTIFACT_PATHS: none yet; consume actual persistence/code-description patches first
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: accepted final doc promotion/closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: recorded configuration, final names, replay identities, graft
- IF_UNKNOWN: none

## Noting Behavior
Record exact payload/host conditions and identity evidence before choosing a replay correction.

## Notes
- DATETIME: 2026-09-04T21:17:27Z
  TYPE: PLAN
  CLAIM: SpellCrystal sorts names, while staged restore and parked/merge graft omit disposal args.
  EVIDENCE:
  - `src/melder/crystallizer/crystals/spell_crystal.py:273-284`
  - `src/melder/crystallizer/crystal_loader_system/restore_engine.py:1945-2002`
  - `src/melder/crystallizer/crystal_loader_system/graft_runner.py:421-530`
  IMPACT: Producer order alone cannot establish the complete recorded-world contract.
  NEXT: Read the persistence patch and complete capture/replay implementations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
No implementation yet. Configuration and final Spell values are separate records. Preserve
their established order and source; inspect host-policy/recorded-ID interactions before graft edits.
Next: `tickets/tasks/2026-09-04_ordered_disposal_docs_assets_task.md`.

