# component_patch_frame_link_contract

## Purpose
Make `FrameLinkContract` represent the effective compiled contract rather than a
generic placeholder.

## Before
- placeholder fields only
- no direct link to compiled ACL output

## After
- frame-link contract can be created from compiled access output
- allowed kinds/commands/metadata come from the compiled surface

## Validation Focus
- contract construction from compiled output
- lightweight consumer-facing shape
