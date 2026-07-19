# Component Patch: FrameACLValidator

## Component Purpose and Boundary In Current Architecture
Frame-scoped validator that checks typed ACL configurations against frame
identity and descriptor/runtime contract rules.

## Before / After Behavior Summary
Before:
- validates view config
- validates codegen config

After:
- validates view config
- validates command config
- validates codegen config

## Interface Deltas
- add `_validate_command_configuration(...)`
- `validate_configuration(...)` MUST call the new command-config pass

## State and Lifecycle Deltas
- no new persistent state required in the first cut

## Failure Mode Deltas
- invalid command operations / ruleset shapes fail fast during validation
- frame-level bundle validation fails if command config is missing or invalid

## Dependency and Ordering Constraints
- command config type must exist before validator changes land
- validator whitelist must stay separate from view/codegen operation families

## Validation Expectations
- focused tests for:
  - valid command config passes
  - invalid command operations fail
  - full bundle validation includes the command layer

## Unknowns and Open Decisions
- exact operation whitelist is still the main open decision for the first cut
