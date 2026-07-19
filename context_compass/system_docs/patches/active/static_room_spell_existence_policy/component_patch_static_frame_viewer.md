# Component Patch: StaticFrameViewer

## Before
- Static viewer filtered spells by liveness only.

## After
- Static viewer excludes:
  - `Existence.many`
  - `Existence.unique_per_spell_space`

## Contract
- A spell must be both live and static-supported to appear in static viewer
  spell-facing output.
