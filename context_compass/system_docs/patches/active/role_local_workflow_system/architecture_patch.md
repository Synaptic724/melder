# Architecture Patch: Role-Local Workflow System

## Patch Scope and Non-Goals
Scope:
- add role-local `WORKFLOWS.MD`
- add role-local `workflows/` folders
- add simple and advanced workflow templates
- update class/profile creation guidance
- add the first real workflow catalog under `general`

Non-goals:
- no top-level workflow registry
- no concrete workflow definitions by default
- no runtime code changes

## Changed-Components Matrix
| Component | Current gap | Required delta |
|---|---|---|
| role folders | no workflow manifest/folder convention | add `WORKFLOWS.MD` and `workflows/` |
| templates | no workflow templates | add simple and advanced templates |
| profile guide | no workflow guidance | document role-local workflow support |
| general workflow catalog | only one starter workflow exists | add the requested active and on-demand workflow set |

## Interface and Boundary Deltas
- actual workflows live in role-local `workflows/`
- role-local manifest is `WORKFLOWS.MD`
- templates remain top-level only
- workflows are user-generated and user-approved only

## Cross-Component Invariants
- no top-level workflow registry
- workflows are role-bound
- templates are global scaffolding only

## Migration/Rollout Order
1. create workflow state
2. create patch docs
3. add manifests/folders
4. add templates
5. add the first workflow catalog under `general`
6. update guide
7. reread and summarize

## Validation Expectations and Evidence Plan
- selected roles have `WORKFLOWS.MD`
- selected roles have `workflows/` folders
- templates exist
- `general/WORKFLOWS.MD` reflects active vs on-demand workflows
- guide docs reflect the new model
