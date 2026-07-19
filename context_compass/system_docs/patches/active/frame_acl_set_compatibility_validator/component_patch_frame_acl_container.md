# Component Patch: FrameACLContainer

## Component Purpose and Boundary In Current Architecture
Frame-local shell that owns ACL chain/history, builder state, and validators
for one frame.

## Before / After Behavior Summary
Before:
- owns one child/type validator only

After:
- owns one child/type validator
- owns one set-compatibility validator

## Interface Deltas
- container exposes the new compatibility validator
- install/register paths run compatibility validation after child validation

## State and Lifecycle Deltas
- cleanup must cascade through the new validator
- container now owns one extra validator object per frame

## Failure Mode Deltas
- named bundle install/register may now fail on compatibility-report errors

## Dependency and Ordering Constraints
- child/type validation should run first
- compatibility validation should run second
- `"default"` syncing behavior must remain unchanged

## Validation Expectations
- focused tests for:
  - validator ownership
  - cleanup cascade
  - compatibility validation invocation on install/register

## Unknowns and Open Decisions
- none for the first container-wiring cut
