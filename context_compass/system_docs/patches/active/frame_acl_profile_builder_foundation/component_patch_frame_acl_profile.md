# component_patch_frame_acl_profile

## Purpose
Replace the generic reusable ACL profile layer with typed rulesets,
view/codegen profile objects, and a composed `FrameACLProfile`.

## Before
- `ViewACLDetails` and `CodegenACLDetails` are generic JSON-holder objects
- `FrameACLProfile` is a named strategy registry over those holders

## After
- typed ACL rules and rulesets exist
- typed view/codegen profile objects exist
- `FrameACLProfile` composes one selected view profile and one selected
  codegen profile

## Validation Focus
- default profile seeding
- typed rule/ruleset ownership
- composed profile behavior
