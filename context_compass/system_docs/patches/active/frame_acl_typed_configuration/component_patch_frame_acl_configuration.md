# component_patch_frame_acl_configuration

## Purpose
Replace raw JSON-string ACL configuration storage with typed applied
configuration objects.

## Before
- `FrameACLConfiguration` stores one normalized JSON payload string
- `view_acl` and `codegen_acl` exist only as JSON object keys

## After
- `FrameACLConfiguration` owns typed child config objects
- root chain metadata stays intact
- configuration remains serializable for persistence

## Validation Focus
- typed default construction
- typed copy-forward behavior
- serialization consistency
