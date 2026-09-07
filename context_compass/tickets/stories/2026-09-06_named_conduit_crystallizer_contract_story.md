# Story: Persist and restore named lesser conduit structure

## Metadata
- Story ID: STORY-2026-09-06-named-conduit-crystallizer-contract
- Epic: EPIC-2026-09-06-named-lesser-conduit-discovery
- Status: draft
- Owner: codex
- Agent Name: codex_1, updater_0
- Created: 2026-09-06T17:17:54Z
- Updated: 2026-09-07T11:46:34Z

## User Narrative
As a Melder user, I want a checkpoint to preserve the named lesser conduits that existed and restore
them under the correct parents with the same names and structural roles. Their created instances
and instance data are outside the restoration contract.

## Value / MRP Alignment
Named lesser structure is required persistence scope. Capture, removal, formation selection and both
restore drivers must agree on that structure while preserving the shared Spellbook and lifetime model.

## Ticket Contract
- ENTRY_GATE: Source trace is recorded; remaining lineage/mode/version decisions and patch contracts are approved.
- EXECUTION_BOUNDARY: Crystallizer-related naming/topology contracts and their actual emission/replay seams.
- DEPENDENCIES: Directory/lifecycle story and cross-system discovery task.
- EXIT_GATE: Named lesser structure captures, folds and replays faithfully with lifecycle and compatibility proofs.
- FAILURE_ESCALATION: Reject unsupported topology; never promote a lesser into a root or silently omit required structure.

## Questions / Requirements
- Persist named lesser structural values through the existing passive emission model.
- Carry an explicit root/lesser discriminator, name, immediate parent, root and shared Spellbook anchors.
  Reuse existing conduit-twin fields where truthful; the current emitter omits the immediate parent.
- Emit after successful creation-time naming and lineage attachment, including checkout of prewarmed shells.
- Remove the finished scope from the current record before shell reuse; retain historical sealed checkpoints.
  Add matching conduit-level removal/capture/fold semantics without deleting the borrowed Spellbook subtree.
- Verify removal and re-emission of one pooled id under another name within one window and across windows.
- Rebuild roots explicitly, then recreate lesser hierarchy through parent.create_lesser_conduit using
  translated parent/root identities. Do not conjure extra roots or duplicate the shared Spellbook.
- Serve sequential and parallel restore through coherent shared entity logic and parent-before-child ordering.
- Include required ancestry/descendants in checkpoint/formation scope. A named child under an unnamed parent
  needs an explicit ancestor-retention contract; root_id alone cannot preserve the original hierarchy.
- Validate missing/cyclic parents, root/book mismatches, lifecycle state and duplicate/colliding names before replay.
- Preserve passive emissions, crystallizer-off behavior, fresh structural identities and public-verb replay.
- Keep mode support consistent with recorded frame/book posture; existing conduit emission is dynamic-only.
- Preserve old root-only records as input and ensure old readers refuse new child-topology records safely.
  RecordVersion currently gates on major only; a minor additive stamp cannot protect a root-only reader.
- Reconstruct structure without replaying prior Creations entries or instance data. Ordinary initialization
  and any explicit code-participation hooks still follow their normal public-verb contracts.

## Source Orientation
- system_docs/src_components: Crystallizer Root, Persistence Record, And Module-World Surfaces.
- system_docs/src_components: promoted Crystallizer Persistence & Restore detail.
- Canonical subsystem philosophy: artifacts/2026-07-09_crystallizer_philosophy_v3.md.
- Full source evidence and reading boundaries: tasks/2026-09-06_named_conduit_cross_system_discovery_task.md.

## Source-Backed Implementation Boundaries
| Boundary | Current source behavior | Required design work |
| --- | --- | --- |
| Conduit emission / ConduitCrystal | Normal + dynamic gate; state/root values but no immediate parent or Creations data. | Named-lesser structural emission and explicit parent edge. |
| Profile / checkpoint | Typed twins replace by id; snapshots carry current payloads for journaled identities. | Conduit-level removal and same-id reuse chronology. |
| Formation capture | Conduit anchor selects one conduit; frame anchor gathers matching-book conduits. | Required ancestor/descendant closure. |
| Restore root selection | First matching book conduit is conjured; state and parent are ignored. | Explicit root selection and child replay under translated parents. |
| Sequential / parallel drivers | One shared book interior; no lesser replay stage or child nodes. | Shared ordered hierarchy reconstruction and rollback. |
| Host / structural preflight | Name collision probes and peer-link warnings; no lesser-parent contract. | Required parent validation and explicit collision outcomes. |
| Record version gate | Newer major refuses; same-major unknown fields are accepted. | Forward-safe schema/version policy for child topology. |

## Tasks / Validation
Persistence changes are required. Create exact implementation tasks after the remaining contracts and
patch design are approved. Validate:
- checkpoint while named lesser is active restores its structural role/name/parent;
- checkpoint after release omits that scope while an earlier sealed checkpoint retains it;
- same pooled id under a new name folds correctly in the same window and later windows;
- shared-book root plus multiple/nested named lessers reconstruct without extra roots or books;
- unnamed supporting ancestry follows the selected contract;
- cold and prewarmed creation, parent cleanup, upgrade and failure rollback remain coherent;
- sequential and parallel replay agree;
- restored scopes do not inherit saved created instances or mutable state; later resolution creates normally;
- old root records load, unsupported new records refuse on old readers, and collisions report honestly.

## Findings and Evidence
- Conduit._emit_conduit_twin: normal + dynamic + active Crystallizer only.
  - src/melder/aether/conduit/conduit.py:421-467
- RestoreEngine._conjure_for_book takes the first matching book row without a root/lesser check.
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1827-1881
- Live-host admission and replay probe cloud names; newly persisted lessers participate in collisions.
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

- DATETIME: 2026-09-07T11:46:34Z
  TYPE: DECISION
  CLAIM: Owner requires named-lesser structural persistence/replay. This supersedes the earlier
    ephemeral-only recommendation. The detailed source trace identifies emission, parent edges,
    conduit removal, formation closure, explicit root selection, both drivers and version safety.
    Existing captured values and binding replay confirm that created-instance state is not the target.
  EVIDENCE:
  - Owner's structural persistence correction in this conversation.
  - src/melder/crystallizer/crystals/conduit_crystal.py:92-306
  - src/melder/crystallizer/persistence/persistence_profile.py:1028-1307
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:713-1035
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1714-2125
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2456-2539
  - src/melder/crystallizer/persistence/record_version.py:142-180
  IMPACT: Structural persistence is part of the core feature. Exact ancestry, mode and compatibility
    decisions still need a reviewable patch contract; this story does not authorize runtime edits.
  NEXT: Resolve required unnamed-ancestor treatment and specify the structural record/replay patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Named lesser structure must be persisted and recreated in its original hierarchy. Created objects are
outside this work. The source trace and boundary table replace the old exclusion recommendation.
Parent closure, consistent mode support, collision outcomes and forward-safe versioning remain design details.
