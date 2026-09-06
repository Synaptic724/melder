# Story: Define named scope recording and restore semantics

## Metadata
- Story ID: STORY-2026-09-06-named-conduit-crystallizer-contract
- Epic: EPIC-2026-09-06-named-lesser-conduit-discovery
- Status: draft
- Owner: codex
- Agent Name: codex_1
- Created: 2026-09-06T17:17:54Z
- Updated: 2026-09-06T17:17:54Z

## User Narrative
As a Melder user, I want naming a temporary scope not to silently change what a checkpoint captures
or what restoring it creates.

## Value / MRP Alignment
Discoverability must not accidentally become durable ownership or persistence. Recording remains
explicit about which identities and topology it carries.

## Ticket Contract
- ENTRY_GATE: Current emit/fold/replay paths are traced and owner selects ephemeral-scope policy.
- EXECUTION_BOUNDARY: Crystallizer-related naming/topology contracts and their actual emission/replay seams.
- DEPENDENCIES: Directory/lifecycle story and cross-system discovery task.
- EXIT_GATE: Either an evidenced no-change boundary or approved compatible recording/replay behavior is tested.
- FAILURE_ESCALATION: Do not assume discoverable scopes must be persisted or reconstructed as normal roots.

## Questions / Requirements
- Identify whether current records contain lesser topology, root-only topology, scope instances or none.
- Trace all cloud enumeration in snapshot, formation, preflight, folding and restore paths.
- Decide whether named lessers remain ephemeral or participate in an explicitly defined record shape.
- Preserve passive emissions, crystallizer-off behavior, fresh structural identities and public-verb replay.
- Define how pooled id reuse and unregister/reacquire affect any emitted names or removal records.
- Avoid treating named lessers as ownership-transfer/graft roots or creating new Spellbooks on replay.

## Source Orientation
- system_docs/src_components: Crystallizer Root, Persistence Record, And Module-World Surfaces.
- system_docs/src_components: promoted Crystallizer Persistence & Restore detail.
- Canonical subsystem philosophy: artifacts/2026-07-09_crystallizer_philosophy_v3.md.
- Exact emission/loader source paths will be recorded by the cross-system discovery task.

## Tasks / Validation
Create implementation tasks only after deciding whether persistence changes are required.
Then test off/on recording, active versus pooled scopes, checkpoint/formation/replay and unchanged root behavior.

## Findings and Evidence
- Conduit._emit_conduit_twin: normal + dynamic + active Crystallizer only.
  - src/melder/aether/conduit/conduit.py:421-467
- RestoreEngine._conjure_for_book: one conduit per recorded book, rebuilt through conjure.
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1826-1880
- Live-host admission and replay probe cloud names, so non-persisted lessers can still affect collisions.
  - src/melder/crystallizer/crystal_loader_system/load_admission.py:434-544
- The skip-existing fallback passes None as the root name; conjure normalizes that to default.
  Account for that existing behavior when choosing collision rules; do not promise an unnamed root.
  - src/melder/aether/spellbook/spellbook_creation_system.py:856-908

## Notes
- DATETIME: 2026-09-06T17:37:21Z
  TYPE: DECISION_REQUEST
  CLAIM: Recommend keeping named lessers ephemeral. Adding them to the existing conduit twin family
    would require child-aware replay and ownership semantics beyond naming convenience.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:421-467
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1826-1880
  IMPACT: Preserve recording policy; still test collisions against newly discoverable names.
  NEXT: Owner confirms ephemeral scope policy and shared-namespace collision behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Draft. Naming is not authorization to persist ephemeral scopes. Current recording/replay behavior must
be read before selecting a design; no crystal schema or loader edits are authorized yet.
