# Component Patch: StaticCommandSystem

## Before
- static specialized spell runtime retrieval to live-only behavior
- there was no explicit create-path spell activation helper on the shared
  command surface

## After
- static keeps the shared spell activation vocabulary visible
- static explicitly denies `meld(...)`
- static may allow `meld_existing_spell(...)` because it is reuse-only and
  consistent with the room's live-only posture

## Contract
- static never creates a spell through the shared command surface
- explicit create-path activation is denied by room-owned behavior, not by
  deleting the method from the vocabulary
