"""
Internal FrameViewer model package.

Purpose:
    Hold the placeholder view/viewer objects used by the Rift-side frame
    surface model.

Responsibilities:
    - Keep the package boundary stable while the HLD is still settling.
    - Avoid export wiring; concrete imports should use explicit module paths.

Endgame:
    This package will eventually hold the filtered per-frame views and the
    final query/strategy consumer object that agents use to understand the
    frame surface.
"""
