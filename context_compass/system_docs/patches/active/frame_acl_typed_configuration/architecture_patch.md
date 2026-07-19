# architecture_patch

## Metadata
- Patch ID: frame_acl_typed_configuration
- Status: draft
- Owner: codex
- Created: 2026-04-05T23:51:00Z
- Updated: 2026-04-05T23:51:00Z

## Patch Scope and Non-Goals
- Objective:
  Implement typed frame-local ACL configuration objects:
  - `FrameACLViewConfiguration`
  - `FrameACLCodegenConfiguration`
  - typed root `FrameACLConfiguration`
  - builder rewrite off raw JSON strings
- Non-goals:
  - descriptor-backed validator rewrite
  - compiled access surface
  - viewer integration

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| frame_acl_configuration | modify | replace raw JSON root with typed configuration objects | ACL design task |
| frame_acl_builder | modify | edit typed configuration objects instead of strings | frame_acl_configuration |
| ACL config tests | modify | align tests to typed configuration/builder semantics | configuration, builder |

## Cross-Component Invariants
- configuration chain/history ownership remains intact
- builder still owns one draft session at a time
- reusable ACL profile catalog remains separate from applied frame config

## Context / Handoff Summary
- What changed:
  The ACL lane now has a bounded patch set for typed applied configuration.
- What remains:
  Implement the typed config classes and builder rewrite, then validate the
  focused ACL config tests.
