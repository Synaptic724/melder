# component_patch_acl_profiles_package

## Purpose
Move the reusable ACL profile catalog into a real `acl/profiles/` package.

## Before
- rules, rulesets, builder, and named profiles live inline in one file

## After
- rules/rulesets live in dedicated modules
- view/codegen profiles live in dedicated modules
- named `safe` / `hybrid` / `permissive` profiles are explicit modules/objects
- profile builder has a dedicated module

## Validation Focus
- package layout
- imports
- named profile visibility
