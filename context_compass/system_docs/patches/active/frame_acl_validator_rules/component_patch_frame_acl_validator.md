# component_patch_frame_acl_validator

## Purpose
Upgrade `FrameACLValidator` from frame-name-only checks to rule-aware typed ACL
configuration validation.

## Before
- validates only `FrameACLConfiguration` type
- validates only matching `frame_name`

## After
- validates typed child config objects
- validates allowed operations in each ruleset family
- validates supported spell payload floor values

## Validation Focus
- child config type validation
- rule-family operation validation
- payload floor validation
