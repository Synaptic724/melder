# component_patch_frame_acl_builder

## Purpose
Rework the frame-local ACL builder so draft/edit/commit flows use typed applied
configuration objects instead of raw JSON strings.

## Before
- builder drafts a JSON string
- commit path parses/stores JSON through the config object

## After
- builder drafts a typed `FrameACLConfiguration`
- commit path finalizes and installs the typed config object
- profile application can attach a reusable ACL profile cleanly

## Validation Focus
- begin change
- apply profile / modify typed draft
- commit/discard behavior
