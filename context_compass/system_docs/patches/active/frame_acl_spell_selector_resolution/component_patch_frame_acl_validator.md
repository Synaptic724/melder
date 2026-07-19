# Component Patch: FrameACLValidator

## Before
- validates config shape
- validates profile-driven floors
- validates descriptor record contracts
- does not validate authored spell selectors

## After
- validates authored spell selector conditions against descriptor truth
- rejects missing or ambiguous selector resolution
- keeps record-contract and payload-floor validation intact

## Interface Deltas
- spell rules with selector conditions become semantically validated instead of
  generic condition bags only

## State / Failure Deltas
- missing spell selector target is a hard error
- ambiguous spell selector target is a hard error
