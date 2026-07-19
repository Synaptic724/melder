# component_patch_frame_acl_manager

## Purpose
Rewire manager/Nexus profile imports to the new ACL profiles package.

## Before
- manager imports from the monolithic inline ACL profile module

## After
- manager imports from the real `acl/profiles/` package
- manager behavior stays the same

## Validation Focus
- import correctness
- no manager behavior regression
