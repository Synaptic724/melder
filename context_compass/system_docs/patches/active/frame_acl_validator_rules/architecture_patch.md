# architecture_patch

## Metadata
- Patch ID: frame_acl_validator_rules
- Status: draft
- Owner: codex
- Created: 2026-04-06T00:11:45Z
- Updated: 2026-04-06T00:11:45Z

## Patch Scope and Non-Goals
- Objective:
  Implement rule-aware typed ACL validator checks:
  - typed child config validation
  - ruleset-family operation validation
  - supported spell payload floor validation
- Non-goals:
  - descriptor-backed selector validation
  - payload/member existence validation
  - compiled access surface

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| frame_acl_validator | modify | move beyond frame-name-only validation | typed config layer |
| validator tests | modify | assert rule-aware validation behavior | frame_acl_validator |

## Cross-Component Invariants
- validator remains scoped to structural/config validation in this slice
- no descriptor-backed selector or member lookup yet
- container install path continues to validate before insert

## Context / Handoff Summary
- What changed:
  The ACL lane now has a bounded validator-enhancement patch set.
- What remains:
  Implement the rule-aware checks and validate the focused ACL tests.
