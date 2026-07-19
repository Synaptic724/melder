# Component Patch: FrameACLValidator

## Before
- validator hardcodes profile-aware behavior directly
- `safe` profile handling is implemented with inline profile-name branches
- descriptor-backed checks are mixed with profile-name special cases

## After
- validator owns strategy registration and resolution by family/profile key
- profile-specific validation behavior lives in strategy objects under
  `validator/profiles/`
- validator remains the orchestrator for:
  - invariant/config validation
  - ruleset-family validation
  - profile-strategy execution
  - descriptor-backed checks

## Interface Deltas
- validator resolves:
  - base profile validation strategy
  - precision profile validation strategy
- no separate validation-profile config objects are introduced in this patch

## State / Failure Deltas
- profile-name special cases move out of the validator body
- new profile assets require validator-strategy registration only when they
  introduce a new validation mode
