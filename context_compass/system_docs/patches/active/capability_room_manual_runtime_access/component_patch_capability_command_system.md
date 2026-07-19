# Component Patch: CapabilityCommandSystem

## Before
- raw runtime-object access was fully denied

## After
- capability allows the shared broad command/runtime surface

## Contract
- capability no longer denies raw runtime-object getters
- capability still does not add codegen behavior
- lower Melder runtime still enforces frame/system-state legality
