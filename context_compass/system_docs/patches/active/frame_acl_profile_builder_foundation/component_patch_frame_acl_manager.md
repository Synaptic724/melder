# component_patch_frame_acl_manager

## Purpose
Update `FrameACLManager` so it owns a real ACL profile builder/library instead
of only a flat name -> `FrameACLProfile` registry.

## Before
- manager stores named `FrameACLProfile` objects directly

## After
- manager owns one profile builder/library object
- builder/library owns separate view/codegen profile registries
- default profiles are seeded at manager startup

## Validation Focus
- manager ownership model
- registry snapshots
- default profile availability
