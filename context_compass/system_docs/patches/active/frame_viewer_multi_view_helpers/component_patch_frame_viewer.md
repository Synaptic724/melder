# Frame Viewer Component Patch

## Before
- `FrameViewer` only exposed basic list/filter/get helpers.

## After
- `FrameViewer` exposes richer deterministic helpers for:
  - grouped links by frame
  - grouped links by kind
  - filtered display-name lists
  - count helpers
  - frame summary/description helpers

## Invariants
- no search DSL
- no raw object access
- no mutation of source views
