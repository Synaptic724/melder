# architecture_patch

## Metadata
- Patch ID: frame_acl_profile_catalog_refactor
- Status: draft
- Owner: codex
- Created: 2026-04-06T00:11:45Z
- Updated: 2026-04-06T00:11:45Z

## Patch Scope and Non-Goals
- Objective:
  Refactor the ACL profile catalog into a real `acl/profiles/` package:
  - rules
  - rulesets
  - view/codegen profile classes
  - named `safe` / `hybrid` / `permissive` profile modules
  - profile builder
- Non-goals:
  - typed config changes
  - validator/compiler changes
  - viewer integration

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| acl/profiles package | add | make the profile catalog explicit and inspectable | current inline catalog |
| frame_acl_manager | modify | import from real profile package | acl/profiles package |
| nexus ACL profile facade | modify | import from real profile package | acl/profiles package |
| ACL profile tests | modify | align to the new package layout | acl/profiles package |

## Cross-Component Invariants
- rules/rulesets remain object-based, not JSON-based
- named profile catalog remains `safe` / `hybrid` / `permissive`
- manager still owns the builder and reusable profile registries

## Context / Handoff Summary
- What changed:
  The ACL lane now has a bounded package-refactor patch set for the profile
  catalog.
- What remains:
  Move the catalog into `acl/profiles/`, then validate the focused ACL tests.
