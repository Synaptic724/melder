# Architecture Patch: Frame ACL Set Compatibility Validator

## Patch Scope and Non-Goals
Scope:
- add a second validator for full ACL bundle compatibility
- keep the existing child/type validator in place
- wire the new validator into the frame ACL container

Non-goals:
- target-aware command selectors
- static/capability runtime execution
- frontend actionable projection

## Changed-Components Matrix
| component | change |
|---|---|
| `FrameACLSetCompatibilityReport` | new warning/error report object |
| `FrameACLSetCompatibilityValidator` | new cross-set validator |
| `FrameACLContainer` | owns the new validator and runs it beside the existing validator |

## Interface and Boundary Deltas
- `FrameACLContainer` MUST own:
  - one child/type validator
  - one set-compatibility validator
- compatibility validation MUST operate on the selected `FrameACLConfiguration`
  bundle as a unit
- child validation and set compatibility validation MUST remain separate

## Cross-Component Invariants
- one container per frame remains the shell
- one selected named bundle per frame remains the selection seam
- compatibility warnings/errors MUST NOT replace child schema validation
- view-only visibility without command permission MAY warn, but must not fail by
  default in the first cut

## Migration / Rollout Order
1. add compatibility report object
2. add compatibility validator
3. wire container ownership and invocation
4. add focused tests

## Rollback Strategy
- if the compatibility rules are too noisy, keep the report type and dial the
  first-cut rules back rather than removing the validator shell

## Validation Expectations and Evidence Plan
- focused unit coverage over:
  - report object
  - compatibility validator
  - container wiring
- evidence target:
  - new report file
  - new validator file
  - updated container/tests

## Ticket Coverage Map
- story:
  - `tickets/stories/2026-04-11_extend_frame_acl_bundle_with_command_configuration_story.md`
- task:
  - `tickets/tasks/2026-04-11_add_frame_acl_set_compatibility_validator_task.md`

## Unknowns and Decision Requests
- UNKNOWN: exact first-cut warning set that is useful without being noisy
