# Component Patch: FrameViewerProfile

## Before
- profile owns a flat tool map
- no profile-local helper objects

## After
- `general_profile.py` lives under `profiles/general/`
- one `general` profile composes:
  - `view_frame`
  - `view_conduit`
  - `view_spell`
- helper objects are cleanup-aware and frame-bound by reference
