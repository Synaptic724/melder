# Component Patch: FrameACLCommandConfiguration

## Component Purpose and Boundary In Current Architecture
New typed ACL child that represents command/action permissions distinct from
view visibility and codegen validation policy.

## Before / After Behavior Summary
Before:
- no typed command config exists
- command permission ideas are forced into view/codegen discussion only

After:
- command policy has its own typed object and JSON round-trip
- the object can be validated independently

## Interface Deltas
- new runtime class:
  - `FrameACLCommandConfiguration`
- expected responsibilities:
  - profile identity/version
  - detached command override rulesets
  - serialization/cloning/cleanup

## State and Lifecycle Deltas
- owns detached rulesets and cleans them on cleanup
- uses a lock because grouped cleanup/replacement mutates multiple owned fields

## Failure Mode Deltas
- invalid profile identity or bad ruleset types fail fast with `ValueError` /
  `TypeError`

## Dependency and Ordering Constraints
- must exist before `FrameACLConfiguration` can carry it
- must be available before validator/builder changes compile

## Validation Expectations
- unit coverage for:
  - default construction
  - JSON round-trip
  - clone
  - cleanup/idempotent lifecycle shape

## Unknowns and Open Decisions
- exact profile defaults for the first cut remain open but must be explicit
