# code_description_patch_frame_acl_configuration

## Trigger justification
This slice changes the applied ACL configuration model and the builder draft
flow that owns it.

## Control-flow description
1. chain still owns head/current/history metadata
2. `FrameACLConfiguration` stores typed view/codegen child config objects
3. builder drafts and commits typed configuration objects instead of raw JSON
4. container/chain ownership stays unchanged

## Validation focus points
- typed default construction
- typed draft/commit lifecycle
- serialization compatibility
