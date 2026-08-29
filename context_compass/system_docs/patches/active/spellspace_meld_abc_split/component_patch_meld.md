# component_patch_meld

## Metadata
- Patch ID: spellspace_meld_abc_split
- Component: meld
- Status: draft
- Owner: codex
- Created: 2026-05-30T10:46:42Z
- Updated: 2026-05-30T10:46:42Z

## Before
- `Meld` is a concrete class that owns both shared runtime logic and
  conduit-caller storage state.
- `ConduitMeld` and `SpellSpaceMeld` exist as mostly copied shells with no
  meaningful state split.

## After
- `Meld` is the abstract/shared runtime core.
- `ConduitMeld` owns conduit-caller attrs and conduit-front-door behavior.
- `SpellSpaceMeld` owns spellspace-caller attrs and spellspace-front-door
  behavior.

## Interface Deltas
- `Meld`:
  - becomes abstract
  - stops owning the generic `_creations` attr
- `ConduitMeld`:
  - owns conduit-specific creations attr(s)
- `SpellSpaceMeld`:
  - owns spellspace-specific creations attr(s) plus owner-conduit access

## State / Failure Deltas
- State delta:
  - caller-specific storage no longer lives on the abstract base.
- Failure delta:
  - any constructor still instantiating base `Meld` after the split is invalid.

## Dependency / Ordering Notes
- `meld.py` changes must land before `conduit.py` and `spell_space.py`
  rewiring.

## Validation Expectations
- `py_compile` on:
  - `src/melder/aether/conduit/meld/meld.py`
  - `src/melder/aether/conduit/meld/conduit_meld.py`
  - `src/melder/aether/conduit/meld/spellspace_meld.py`
