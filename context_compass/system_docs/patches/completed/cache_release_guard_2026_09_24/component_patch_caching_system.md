# Component patch: CachingSystem envelope

<!-- BEGIN ENTRY: CachingSystem release stamp -->
## Before
The top-level marshal dictionary holds version, python, frame_name, conduit_name and spell_payloads.
CURRENT_VERSION is 8. Installed Melder release does not participate in acceptance.

## After
Import the canonical version module value; add melder_version when constructing an empty dictionary.
Normalization requires exact equality and carries the accepted field into its returned dictionary.
Emission persists the stored field. Add generation 9 to the documented compatibility history.

## Ownership and failure behavior
The field belongs to _cache_data. No new object, slot or cleanup duty. Existing RLock and atomic
write own mutation/emission. Existing loader error handling creates a fresh empty dictionary on
missing, malformed or mismatched release. Never stamp old payloads as a different release.

## Ordering
Reject an incompatible envelope before returning payloads to conjure classification. Keep
conjure, context publication, lazy hydration and write boundaries unchanged.

## Tests and docs
Correct tests that write unused JSON paths; validate real files and accepted populated controls.
Extend the schema-history fixture and automatic/dynamic runtime controls. Update the cache
descriptor and scoped compatibility prose after qualification.

## Remaining decisions
None. The component remains Book-owned and the failure path remains cold regeneration.
<!-- END ENTRY: CachingSystem release stamp -->
