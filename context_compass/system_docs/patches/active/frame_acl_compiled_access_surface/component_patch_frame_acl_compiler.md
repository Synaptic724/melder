# component_patch_frame_acl_compiler

## Purpose
Compile typed ACL configuration over payload-backed descriptor records into a
derived access surface.

## Before
- ACL system stops at typed config + validator
- no effective access output exists for downstream consumers

## After
- compiler consumes frame/conduit/spell payload-backed records
- compiler emits a consumer-facing access surface

## Validation Focus
- payload-backed record consumption
- derived access output
- no descriptor mutation
