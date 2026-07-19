# architecture_patch

## Metadata
- Patch ID: frame_acl_compiled_access_surface
- Status: draft
- Owner: codex
- Created: 2026-04-06T00:15:58Z
- Updated: 2026-04-06T00:15:58Z

## Patch Scope and Non-Goals
- Objective:
  Implement the first compiled ACL access surface:
  - compiled access surface object
  - compiler over payload-backed descriptor records
  - `FrameLinkContract` shaping from compiled output
- Non-goals:
  - full viewer implementation
  - live event/update wiring
  - codegen executor integration

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| acl compiler | add/modify | compile typed ACL config against descriptor payloads | typed config + validator |
| compiled access surface | add | hold derived consumer-facing access answers | compiler |
| frame_link_contract | modify | consume compiled output instead of placeholder-only fields | compiled surface |

## Cross-Component Invariants
- compiler consumes descriptor truth; it does not mutate descriptor state
- compiled output remains derived/consumer-facing, not raw config
- `FrameLinkContract` represents effective contract after ACL evaluation

## Context / Handoff Summary
- What changed:
  The ACL lane now has a bounded patch set for compiled access output.
- What remains:
  Implement the compiler/surface and align the frame-link contract.
