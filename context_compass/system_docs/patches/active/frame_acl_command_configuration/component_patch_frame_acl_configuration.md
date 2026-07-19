# Component Patch: FrameACLConfiguration

## Component Purpose and Boundary In Current Architecture
Typed frame-local ACL bundle selected by named contract and owned inside one
frame ACL container.

## Before / After Behavior Summary
Before:
- bundle carries `view_configuration` and `codegen_configuration`

After:
- bundle carries `view_configuration`, `command_configuration`, and
  `codegen_configuration`

## Interface Deltas
- constructor gains `command_configuration`
- `create_default(...)` seeds a default command config
- JSON serialization includes `command_configuration`
- clone/from-json paths include `command_configuration`
- cleanup tears down the new child

## State and Lifecycle Deltas
- bundle owns one additional typed child and must clean it in dependency order

## Failure Mode Deltas
- construction should fail fast if `command_configuration` is missing or of the
  wrong type

## Dependency and Ordering Constraints
- must consume the new command-config class before validator/builder can use it

## Validation Expectations
- unit coverage for:
  - default creation includes command config
  - JSON round-trip preserves command config
  - clone preserves command config
  - cleanup tears down all three children

## Unknowns and Open Decisions
- none for the first bundle-extension cut
