# Component Patch: Role-Local Workflow Manifests

## Purpose
Define the role-local manifest and folder convention for workflows.

## Before/After
Before:
- no role-local workflow manifest or folder convention

After:
- selected roles have `WORKFLOWS.MD`
- selected roles have `workflows/`

## Key Rules
- actual workflows stay role-local
- `WORKFLOWS.MD` is lightweight and inheritance-aware
- no top-level workflow registry
