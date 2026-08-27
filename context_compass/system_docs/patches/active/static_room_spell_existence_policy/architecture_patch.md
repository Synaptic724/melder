# Static Room Spell Existence Policy Architecture Patch

## Objective
Align static viewer and static command on unsupported spell existences.

## Non-Goals
- No capability work.
- No descriptor publication redesign.
- No broader viewer redesign.

## Changed Components
- `StaticFrameViewer`
- `StaticCommandSystem`

## Boundary Contract
- Static room does not expose `Existence.many`.
- Static room does not expose `Existence.unique_per_spell_space`.
- Static viewer and static command must enforce the same existence policy.

## Migration Order
1. Patch static viewer filtering.
2. Patch static command filtering.
3. Update focused tests.
