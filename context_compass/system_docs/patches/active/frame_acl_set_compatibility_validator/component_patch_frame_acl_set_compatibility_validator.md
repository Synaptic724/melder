# Component Patch: FrameACLSetCompatibilityValidator

## Component Purpose and Boundary In Current Architecture
Cross-set validator for one selected frame ACL bundle. It checks whether
`view_configuration`, `command_configuration`, and `codegen_configuration`
fit together coherently.

## Before / After Behavior Summary
Before:
- only child/type validation exists
- no explicit warning/error scan across the full bundle

After:
- full-bundle compatibility report exists
- suspicious or contradictory combinations can be surfaced centrally

## Interface Deltas
- new `FrameACLSetCompatibilityReport`
- new `FrameACLSetCompatibilityValidator`
- validator returns a report and may raise on report errors

## State and Lifecycle Deltas
- validator stores the last report for diagnostics
- report object is detached and read-mostly

## Failure Mode Deltas
- structurally contradictory bundle combinations may now fail fast
- suspicious-but-possible combinations surface as warnings only

## Dependency and Ordering Constraints
- depends on the existing typed bundle model
- should not own descriptor-level command validation in the first cut

## Validation Expectations
- focused tests for:
  - visible-but-not-actionable warning
  - actionable-but-hidden warning
  - structurally contradictory member-command without spell enable error

## Unknowns and Open Decisions
- exact warning/error severity for each mismatch family may evolve after
  target-aware command entries exist
