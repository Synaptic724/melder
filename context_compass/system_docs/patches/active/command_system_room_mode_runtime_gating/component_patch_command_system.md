# Component Patch: CommandSystem

## Before
- command ACL gates raw runtime-object getters by compiled ACL only
- room kind does not affect raw runtime-object exposure

## After
- raw runtime-object getters enforce both:
  - compiled command ACL
  - room-mode gating
- `static` and `capability` fail fast on raw runtime-object getters
- `dynamic` keeps the current ACL-gated runtime getter behavior

## Interface Deltas
- runtime-object getters raise earlier in `static` and `capability`
- descriptor/record getters remain unchanged

## State / Failure Deltas
- room-kind policy now becomes visible at the command-system boundary
- raw runtime-object access failures become explicit instead of silently
  depending only on ACL enablement
