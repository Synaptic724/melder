# architecture_patch

## Metadata
- Patch ID: frame_acl_profile_builder_foundation
- Status: draft
- Owner: codex
- Created: 2026-04-05T22:48:24Z
- Updated: 2026-04-05T22:48:24Z

## Patch Scope and Non-Goals
- Objective:
  Implement the ACL profile-builder foundation:
  - typed ACL rules and rulesets
  - typed view/codegen ACL profile objects
  - composed `FrameACLProfile`
  - manager-owned profile builder/library with default registration
- Non-goals:
  - full `FrameACLConfiguration` typed-root migration
  - validator rewrite against descriptor payloads
  - compiled access-surface implementation
  - viewer integration

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| frame_acl_profile | modify | replace generic reusable profile layer with typed rules/profiles/composition | ACL design task |
| frame_acl_manager | modify | own the new profile builder/library | frame_acl_profile |
| ACL profile tests | modify | align tests to typed profile/builder model | frame_acl_profile, frame_acl_manager |

## Cross-Component Invariants
- `FrameACLManager` remains the owner of the reusable ACL profile registry.
- view and codegen profiles stay separate
- default view/codegen profiles are seeded immediately
- current frame container/chain shell remains intact in this slice

## Context / Handoff Summary
- What changed:
  The ACL lane now has a bounded implementation patch set for the profile
  builder foundation.
- What remains:
  Implement the typed profile layer and manager ownership, then validate the
  focused ACL profile tests.
