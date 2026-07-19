# Architecture Patch: Projection-Driven Codegen ACL Validation Profiles

## Objective
Make `CodegenSystem` validation consume the selected `CodegenProjection`
directly so imports, dangerous builtins, dunder/reflection posture, and the
namespace contract are driven by the existing codegen ACL family.

## Non-Goals
- no second execution-policy authority
- no fake Python sandbox
- no viewer/command ACL redesign

## Changed Components
- codegen ACL reusable profiles
- frame ACL validator
- frame ACL compiler
- compiled access surface
- codegen validator strategies
- codegen namespace contract

## Invariants
- `CodegenProjection` remains the source of truth
- permissive stays broadly usable for real work
- normal Python work patterns remain available by default
- import/builtin/meta controls are profile-driven

## Interface Deltas
- compiled access surface gains codegen validation answers
- codegen namespace moves to `viewer`, `command`, `workstation`, `codegen`

## Migration Order
1. extend codegen ACL rule vocabulary
2. validate the new rule vocabulary
3. compile validator-facing codegen answers
4. consume those answers in validator/namespace
5. update tests

## Rollback
- remove new compiled-surface fields
- revert validator strategies to the prior static behavior
- restore old namespace contract if needed
