# architecture_patch

## Metadata
- Patch ID: descriptor_payload_conduit_frame_followup
- Status: draft
- Owner: codex
- Created: 2026-04-05T21:25:04Z
- Updated: 2026-04-05T21:25:04Z

## Patch Scope and Non-Goals
- Objective:
  Implement the conduit/frame descriptor payload follow-up:
  - Protocol-based payload interfaces
  - one `ConduitRecord.payload` field
  - one `FrameRecord.payload` field
  - direct conduit/frame publish/store path updated to the new payload contract
- Non-goals:
  - ACL/view implementation
  - event bus implementation
  - `FrameDescriptor` aggregate redesign
  - `NexusFrameRecord` redesign

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| interfaces | modify | define conduit/frame payload contracts | record contracts |
| conduit record | modify | collapse flat descriptive fields into one payload field | interfaces |
| frame record | modify | collapse flat descriptive fields into one payload field | interfaces |
| descriptor manager | modify | publish/store conduit and frame payloads | record contracts |

## Cross-Component Invariants
- `FrameDescriptor` stays the canonical aggregate and ownership/index host.
- Conduit/frame record identity fields remain stable while descriptive state
  moves into payloads.
- Published payloads must be descriptor-safe and value-oriented.
- Empty conduit/frame payloads are invalid and must fail fast.

## Context / Handoff Summary
- What changed:
  The descriptor payload lane now has a follow-up patch set for conduit/frame
  rollout.
- What remains:
  Implement the payload interfaces, record fields, and manager publication
  updates, then validate the focused descriptor surface.
