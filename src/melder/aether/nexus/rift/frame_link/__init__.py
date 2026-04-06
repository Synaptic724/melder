"""
Internal FrameLink model package.

Purpose:
    Hold the placeholder frame-surface link objects used by the Rift-side
    query/display model.

Responsibilities:
    - Keep the package boundary stable while the HLD is still settling.
    - Avoid export wiring; concrete imports should use explicit module paths.

Endgame:
    This package will eventually hold the canonical link objects that connect
    a `Rift`/`FrameViewer` to Nexus-owned frame-surface representations.
"""
