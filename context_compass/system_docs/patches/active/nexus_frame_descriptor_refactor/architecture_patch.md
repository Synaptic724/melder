# architecture_patch

## Metadata
- Patch ID: nexus_frame_descriptor_refactor
- Status: draft
- Owner: codex
- Created: 2026-04-04T13:10:15Z
- Updated: 2026-04-04T13:10:15Z

## Patch Scope and Non-Goals
- Objective:
  Replace the current fragmented frame-scoped Nexus state with one
  `FrameDescriptor` aggregate per frame.
- Non-goals:
  - final viewer implementation
  - final ACL implementation
  - mutation model redesign

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| nexus | modify | move frame-scoped state under one descriptor aggregate | passive ingest slice |
| frame_descriptor | add | own frame posture, overview, nested records, and future ACL containers | nexus |

## Interface and Boundary Deltas
- Boundary delta 1:
  Frame-scoped Nexus state should be addressed through
  `FrameDescriptor`, not scattered flat Nexus fields.
- Boundary delta 2:
  `AethericFrameConfiguration`, frame overview data, frame-local records, and
  `NexusFrameRecord` should become nested parts of the descriptor.
- Boundary delta 3:
  Future ACL and compiled access layers should target the descriptor rather
  than a flat store.

## Cross-Component Invariants
- Invariant 1:
  One descriptor per frame name.
- Invariant 2:
  Descriptor is a Nexus-side aggregate, not a replacement for the real runtime
  `AethericFrame`.
- Invariant 3:
  Migration must happen in multiple steps, not one broad rewrite.

## Migration and Rollout Order
1. Add patch docs and planning lane.
2. Investigate flat frame-scoped Nexus state and current publish paths.
3. Introduce `FrameDescriptor`.
4. Migrate the first safe frame-scoped fields into it.
5. Retarget publication paths in later slices.

## Rollback Strategy
- Rollback trigger:
  Descriptor introduction proves too invasive for the first slice.
- Rollback steps:
  1. Leave current flat state in place.
  2. Keep patch/task notes with migration findings.
  3. Resume later with a narrower first slice.

## Validation Expectations and Evidence Plan
- Validation item 1:
  Current flat frame-scoped Nexus state is fully mapped before migration.
- Evidence source 1:
  `src/melder/aether/nexus/nexus.py`
- Validation item 2:
  Descriptor contents and first slice are explicit before runtime edits.
- Evidence source 2:
  active task notes + component patch docs

## Ticket Coverage Map
- Epic:
  EPIC-2026-04-04-refactor-nexus-frame-state-around-aethericframe-descriptor
- Story:
  STORY-2026-04-04-aethericframe-descriptor-refactor
- Tasks:
  - TASK-2026-04-04-investigate-aethericframe-descriptor-refactor

## Unknowns and Decision Requests
- UNKNOWN:
  Whether the first descriptor slice should wrap the current store or migrate
  fields immediately.
- DECISION_REQUEST:
  None yet.

## Context / Handoff Summary
- What changed:
  The descriptor refactor now has a patch-governed lane.
- What remains:
  Investigate the migration surface and define the first slice.
- Next entrypoint:
  `component_patch_nexus.md`
