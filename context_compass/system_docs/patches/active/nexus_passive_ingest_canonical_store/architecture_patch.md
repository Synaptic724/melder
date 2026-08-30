# architecture_patch

## Metadata
- Patch ID: nexus_passive_ingest_canonical_store
- Status: draft
- Owner: codex
- Created: 2026-04-04T07:46:28Z
- Updated: 2026-04-04T07:46:28Z

## Patch Scope and Non-Goals
- Objective:
  Add the first Nexus-owned canonical record store and passive ingest path so
  frame/conduit/spell data can accumulate before interactive Nexus/Rift
  enablement.
- Non-goals:
  - full viewer/query integration
  - eventstream implementation
  - ACL matrix implementation
  - JSON/CommandOps transport work

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| nexus | add/modify | own canonical store and private passive-ingest publication surface | aetheric_frame_configuration |
| spellbook | modify | publish frame/spell data into Nexus at stable mutation points | nexus |
| conduit | modify | publish root-conduit lifecycle/link updates into Nexus | nexus |

## Interface and Boundary Deltas
- Boundary delta 1:
  Passive canonical record hosting is now distinct from interactive
  `Nexus.enable(...)`. Records may accumulate before Rift/public interaction is
  enabled.
- Boundary delta 2:
  Runtime producers publish directly to private `Nexus` methods; they do not
  route through `Aether` and they do not mutate store internals directly.
- Boundary delta 3:
  Publication is gated by frame posture (`AethericFrameConfiguration`),
  specifically `rift_enabled`, not by interactive Nexus enablement.
- Boundary delta 4:
  The canonical store hosts living records (`FrameRecord`, `ConduitRecord`,
  `SpellRecord`) rather than snapshots or viewer payloads.

## Cross-Component Invariants
- Invariant 1:
  If a frame does not have a bound `AethericFrameConfiguration`, nothing
  publishes.
- Invariant 2:
  If `frame_configuration.rift_enabled` is false, nothing publishes.
- Invariant 3:
  Interactive `Nexus.enable(...)` remains the gate for Rift creation/direct
  interaction only; it does not govern passive record hosting.
- Invariant 4:
  `FrameRecord` publishes first; later spell/conduit publication may
  short-circuit quickly if the frame is not publishable.
- Invariant 5:
  Only root conduits publish by default; lesser conduits remain derived through
  lineage walking unless later promoted to normal.
- Invariant 6:
  Spell publication begins once a Spellbook has successfully conjured so
  `owner_conduit_id` is stable.

## Migration and Rollout Order
1. Add the active patch docs and link them to the active task.
2. Add the Nexus canonical store and living record classes.
3. Add private Nexus publication methods and publishability gating.
4. Wire frame publication from conjure.
5. Wire root-conduit publication and link/sever cleanup updates.
6. Wire spell catch-up publication on conjure and incremental publication on
   bind-after-conjure.
7. Validate the focused Nexus/Aether/Spellbook/Conduit surfaces.

## Rollback Strategy
- Rollback trigger:
  Passive ingest starts to blur with interactive enablement or the canonical
  store shape proves wrong for the first viewer consumer.
- Rollback steps:
  1. Remove private publication calls from producers.
  2. Remove or disable the canonical store.
  3. Leave the frame-level posture object in place.
- Post-rollback verification:
  The runtime returns to the current state where frame posture exists but Nexus
  does not accumulate canonical records yet.

## Validation Expectations and Evidence Plan
- Validation item 1:
  Nexus stores canonical records without requiring interactive enablement.
- Evidence source 1:
  `src/melder/aether/nexus/nexus.py`
- Validation item 2:
  Spellbook publishes frame and spell data only at approved stable points.
- Evidence source 2:
  `src/melder/spellbook/spellbook.py`
  `src/melder/spellbook/spellbook_creation_system.py`
- Validation item 3:
  Conduit publishes root lifecycle/link updates only.
- Evidence source 3:
  `src/melder/aether/conduit/conduit.py`

## Ticket Coverage Map
- Epic:
  EPIC-2026-04-03-frame-surface-query-and-binding
- Story:
  STORY-2026-04-03-frameinfolink-hld
- Tasks:
  - TASK-2026-04-04-implement-nexus-passive-ingest-and-canonical-store

## Unknowns and Decision Requests
- UNKNOWN:
  Whether the first canonical store should be wrapped in a dedicated
  `NexusCanonicalStore` object immediately or start as private dict/set fields
  on `Nexus` and be wrapped later.
- DECISION_REQUEST:
  None yet.

## Context / Handoff Summary
- What changed:
  The passive-ingest slice is now patch-gated as a real runtime architecture
  change instead of an informal next-step note.
- What remains:
  Lock the first store shape and publication points, then implement.
- Next entrypoint:
  `component_patch_nexus.md`
