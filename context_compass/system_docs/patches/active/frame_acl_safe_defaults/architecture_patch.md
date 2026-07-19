# architecture_patch

## Metadata
- Patch ID: frame_acl_safe_defaults
- Status: draft
- Owner: codex
- Created: 2026-04-05T23:45:34Z
- Updated: 2026-04-05T23:45:34Z

## Patch Scope and Non-Goals
- Objective:
  Implement safe default reusable ACL profile content:
  - non-empty default view rulesets
  - non-empty default codegen rulesets
  - ACL profile version metadata
- Non-goals:
  - typed `FrameACLConfiguration`
  - validator rewrite against descriptor payloads
  - AST/codegen validation engine
  - compiled access-surface implementation

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| frame_acl_profile | modify | encode curated default rules and profile version metadata | ACL profile builder foundation |
| ACL profile tests | modify | assert safe default rule content and version semantics | frame_acl_profile |

## Cross-Component Invariants
- default profiles must remain restrictive
- default codegen rules must bias toward query/bind over mutation/actuation
- manager/container/chain shell remains unchanged in this slice

## Context / Handoff Summary
- What changed:
  The ACL lane now has a bounded patch set for safe default profile content.
- What remains:
  Implement the default rules and validate the focused ACL profile tests.
