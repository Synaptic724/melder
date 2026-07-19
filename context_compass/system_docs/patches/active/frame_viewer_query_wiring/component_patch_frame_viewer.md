# Frame Viewer Component Patch

## Before
- `FrameViewer` only stores views and exposes add/get/list helpers.

## After
- `FrameViewer` provides a narrow real helper/query layer over projected views
  and links.
- The helper layer remains view-local and does not recreate a repository or
  binding engine.

## Invariants
- no raw runtime object references
- no ACL evaluation logic
- no execution/binding semantics
