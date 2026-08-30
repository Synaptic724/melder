# Patch Architecture: Rift Creation Targeting Primary Space Split

## Metadata
- Patch ID: `rift_creation_targeting_primary_space_split`
- Status: active
- Updated: 2026-04-08T11:35:38Z

## Objective
Split Rift lifecycle into:
- bare Rift creation
- primary space programming from `space_type`
- later explicit frame targeting that refreshes the viewer

## Core Decision
- `RiftConfiguration` keeps `space_type` but loses `target_frame_name`.
- `Nexus.create_rift(...)` creates a bare Rift and no longer selects a target frame.
- `Rift` creates its primary concrete space from the chosen `space_type`.
- Frame targeting becomes a separate Rift action.
- Successful targeting refreshes the attached viewer from descriptor + current ACL state.

## Non-Goals
- ACL authoring redesign
- viewer redesign
- broad multi-space rewrite unless required by the first cut
