# code_description_patch_frame_acl_profile_builder

## Trigger justification
This slice changes the reusable ACL profile control flow and manager ownership
model before typed frame configuration work begins.

## Control-flow description
1. manager constructs one ACL profile builder/library
2. builder seeds default view and codegen profiles
3. callers resolve or compose `FrameACLProfile` objects through that builder
4. frame configuration/container work remains unchanged in this slice

## Validation focus points
- default registration
- profile composition
- manager snapshot behavior
