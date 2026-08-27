# Component Patch: StaticCommandSystem

## Before
- static mode blanket-denies raw spell runtime-object getters

## After
- static mode keeps the same spell getter names
- those getters now return a spell runtime object only when it already has a
  live creation
- no creation path is entered

## Interface Deltas
- no new public command methods
- existing spell getters gain live-only behavior in static mode

## State / Failure Deltas
- static spell access now distinguishes:
  - published and live
  - published but not live
  instead of treating both as the same blanket denial
