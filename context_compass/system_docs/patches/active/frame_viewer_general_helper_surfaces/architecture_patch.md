# Patch Architecture: Frame Viewer General Helper Surfaces

## Metadata
- Patch ID: `frame_viewer_general_helper_surfaces`
- Status: active
- Updated: 2026-04-06T20:28:20Z

## Objective
Reorganize the viewer-method layer so the single `general`
`FrameViewerProfile` composes three helper-object surfaces:
- `view_frame`
- `view_conduit`
- `view_spell`

## Core Decision
- Keep one profile per frame.
- Package the general profile under `profiles/general/`.
- Put frame-, conduit-, and spell-scoped helper behavior in separate
  cleanup-aware helper objects.
- Compose those helper objects inside `general_profile.py`.
- Keep the helpers bound by reference to the same descriptor + ACL state as the
  profile.

## Non-Goals
- multiple new seeded viewer profiles
- codegen execution
- snapshot/view layer revival
