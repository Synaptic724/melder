# Component patch: Cached plan compatibility

<!-- BEGIN ENTRY: "CachingSystem default-precedence version" -->
## Before and after
Version-7 bundles may contain inferred dependencies for parameters with ordinary Python defaults.
The bind signature does not change with this compiler-policy fix, so SHA lookup alone cannot expire them.
Add version 8, ordinary_defaults_are_plain, to the existing CACHE_VERSION_HISTORY.

## Contract
- Existing version comparison rejects older bundles and initializes an empty in-memory cache.
- Existing build/stage/emit behavior regenerates valid version-8 plans.
- Payload structure, Python tag checking and per-frame/conduit file ownership remain unchanged.
- No change to Crystallizer records or binding SHA schema.

## Validation
Update the existing version-history integration contract to include version 8. Existing normalization
rejects every other version automatically. No new replay tests or invalidation mechanism are needed.
Target: src/melder/utilities/caching_system/caching_system.py and scoped cache tests.
<!-- END ENTRY: "CachingSystem default-precedence version" -->
