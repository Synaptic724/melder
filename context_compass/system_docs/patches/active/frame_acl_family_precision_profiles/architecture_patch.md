# Architecture Patch: ACL Family Precision Profiles And Validator Strategies

## Objective
Add command base profiles, family-local `precision.py` profile assets, and
validator-owned profile strategies so the ACL runtime validates and compiles
`base + precision + overrides` per family instead of hardcoding profile-name
special cases inside the validators.

## Non-Goals
- no fourth top-level ACL configuration family
- no room/runtime command ACL enforcement in this patch
- no broader upper-layer validator redesign beyond profile strategy pairing

## Changed Components
- `FrameACLViewConfiguration`
- `FrameACLCommandConfiguration`
- `FrameACLCodegenConfiguration`
- `FrameACLProfileBuilder`
- `FrameACLValidator`
- `FrameACLSetCompatibilityValidator`
- `FrameACLCompiler`
- ACL profile asset tree under `configurations/profiles/`

## Invariants
- selected ACL family chains remain:
  - view
  - command
  - codegen
- each family config resolves:
  - one base profile
  - zero or one precision profile
  - local override rulesets
- validators own validation-strategy registration and execution
- compatibility/compiler merge order is:
  - base profile
  - precision profile
  - overrides

## Interface Deltas
- command gains reusable profile assets like view/codegen
- family configs gain precision-profile identity fields
- profile builder resolves command and precision assets
- validators stop relying on inline profile-name special cases

## Migration Order
1. add command profile family and precision asset skeletons
2. extend family configs with precision-profile identity
3. extend profile builder registries
4. add validator-owned strategy registry and family strategies
5. move hardcoded profile checks into strategies
6. update compatibility/compiler merge logic
7. update focused tests

## Rollback
Rollback is code-level only for this patch. Do not keep a half-hybrid state
where some profile semantics live in strategies and some remain hardcoded.

## Ticket Coverage Matrix
- task: `tickets/tasks/2026-04-11_implement_acl_family_precision_profiles_and_validator_strategies_task.md`
