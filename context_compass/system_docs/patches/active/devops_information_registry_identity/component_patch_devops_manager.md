# component_patch_devops_manager

## Metadata
- Patch ID: devops_information_registry_identity
- Component: DevOpsManager
- Status: draft
- Owner: codex
- Created: 2026-05-22T22:08:36Z
- Updated: 2026-05-22T22:08:36Z

## Component Purpose and Boundary
- Current boundary:
  - `DevOpsManager` owns incidents, change control, risk, creation gates, and
    spell-system-state exposure.
- Target boundary:
  - `DevOpsManager` also owns the frame-local information registry.

## Before/After Behavior Summary
- Before:
  - no single topology/identity registry exists under the frame root.
- After:
  - `DevOpsManager` exposes the registry as a first-class borrowed subsystem.

## Interface Deltas
- Inputs:
  - none beyond existing constructor
- Outputs:
  - new `devops_information_registry` accessor
- Error semantics:
  - cleaned manager drops registry like the other owned subsystems

## State and Lifecycle Deltas
- Owned state changes:
  - add `_devops_information_registry` as a borrowed frame-owned reference
- Lifecycle/cleanup changes:
  - cleanup drops the registry reference but does not own registry teardown

## Failure Mode Deltas
- New failure mode:
  - none
- Removed failure mode:
  - none
- Changed failure mode:
  - none

## Dependency and Ordering Constraints
1. Registry must be created by `AethericFrame` before manager init.
2. Cleanup order must leave registry teardown with the frame, not the manager.

## Validation Expectations
- Test/validation item 1:
  - reread final manager init/cleanup/accessor flow
- Evidence target 1:
  - touched source file

## Unknowns and Open Decisions
- UNKNOWN:
  - whether future managers besides transaction mediation will consume the
    registry directly
- DECISION_REQUEST:
  - none

## Context / Handoff Summary
- What changed:
  - manager ownership boundary expands to include the registry
- Remaining risks:
  - downstream users are not wired yet
- Next entrypoint:
  - implementation files
