# component_patch_spell_space

## Metadata
- Patch ID: spellspace_meld_abc_split
- Component: spell_space
- Status: draft
- Owner: codex
- Created: 2026-05-30T10:46:42Z
- Updated: 2026-05-30T10:46:42Z

## Before
- `SpellSpace` still types and owns a generic `Meld` reference.

## After
- `SpellSpace` owns concrete `SpellSpaceMeld`.
- `SpellSpaceMeld` receives spellspace-local creations plus owner-conduit
  creations for split routing.

## Interface Deltas
- `SpellSpace` constructor wiring changes.
- `SpellSpacePool` construction path changes if needed to supply the concrete
  meld object.

## State / Failure Deltas
- State delta:
  - spellspace front door becomes explicit.

## Dependency / Ordering Notes
- Must land after meld base/subclass attr split.
- Must remain consistent with `Conduit` constructor rewiring.

## Validation Expectations
- `py_compile` on:
  - `src/melder/aether/conduit/spell_space/spell_space.py`
  - `src/melder/aether/conduit/spell_space/spell_space_pool.py`
