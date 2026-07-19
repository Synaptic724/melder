# component_patch_creation_context

## Metadata
- Patch ID: spellspace_meld_abc_split
- Component: creation_context
- Status: draft
- Owner: codex
- Created: 2026-05-30T11:08:16Z
- Updated: 2026-05-30T11:08:16Z

## Before
- Spellspace route generation still assumes caller-creations exposes:
  - `get_active_spellspace()`
  - `get_spellspace_creation(...)`
  - spellspace bucket indirection

## After
- Spellspace route generation treats the caller creations object for the
  spellspace route as the direct spellspace-owned store.

## Interface Deltas
- `creation_context_codegen.py`
  - spellspace route emitted source reads/reuses/registers directly against the
    passed spellspace store surface.

## State / Failure Deltas
- State delta:
  - spellspace route no longer depends on active spellspace lookup for direct
    spellspace-owned storage access.

## Dependency / Ordering Notes
- Land before or with Phase 12 helper changes so emitted and helper semantics match.

## Validation Expectations
- `py_compile` on:
  - `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
