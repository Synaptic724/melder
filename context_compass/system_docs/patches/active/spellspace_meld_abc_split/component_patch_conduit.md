# component_patch_conduit

## Metadata
- Patch ID: spellspace_meld_abc_split
- Component: conduit
- Status: draft
- Owner: codex
- Created: 2026-05-30T10:46:42Z
- Updated: 2026-05-30T10:46:42Z

## Before
- `Conduit` constructs concrete `Meld` directly.

## After
- `Conduit` constructs concrete `ConduitMeld`.

## Interface Deltas
- Constructor wiring changes only:
  - meld object class
  - any shared state passed into spellspace creation later in the same patch

## State / Failure Deltas
- State delta:
  - conduit front door becomes explicit instead of implicit through base `Meld`.

## Dependency / Ordering Notes
- Must land after meld base/subclass attr split.

## Validation Expectations
- `py_compile` on:
  - `src/melder/aether/conduit/conduit.py`
