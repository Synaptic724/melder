# Patch: Release-bound creation-cache compatibility

<!-- BEGIN ENTRY: Cache release compatibility -->
## Objective and boundary
Persisted creation plans are reusable only by the exact Melder release that wrote them.
Keep schema generation and Python cache tag as independent gates. No change to public runtime APIs,
spell fingerprints, application lifetimes, compiler phases or Crystallizer durable records.

## Changed components
- CachingSystem: add melder_version to its existing envelope and reject mismatches before adoption.
- Existing cache tests: use actual .melc marshal files and demonstrate cold/warm behavior.
- Source descriptions/release metadata: document the compatibility rule; release 0.2.51.

## Invariants
- The canonical version comes directly from melder.__version__.
- Missing or differing release stamps produce the existing cold-cache reset.
- A valid release stamp survives normalization and subsequent emission.
- No release check enters ordinary meld, payload lookup or compiled execution.
- Cached application objects are not restored, cleared or transferred by this change.
- RecordVersion remains independent and unchanged.

## Interface and format delta
Creation-cache generation 9 adds required melder_version. Advancing the outer generation prevents
older generation-8 readers from ignoring the new field in a newer bundle.

## Migration and rollback
Add tests first; implement header creation/validation/emission; qualify existing cache paths;
promote source docs and public notes; bump package version; finish tracking; regenerate assets last.
Older bundles are cold without deletion. A rollback to generation 8 also treats generation 9 as cold.

## Coverage matrix
- Matching release and fresh emission: utility tests.
- Legacy/missing/mismatched metadata: utility and schema-history tests.
- Same IDs under changed release: runtime integration, automatic and dynamic.
- Existing asset policy and runtime unaffected: scoped asset/metadata checks and source comparison.

## Ticket coverage and remaining decisions
EPIC-2026-09-23-invalidate-creation-cache-on-melder-version-change is delivered by
TASK-2026-09-24-implement-release-version-cache-invalidation across regression, envelope and
qualification slices. No unresolved design decision remains for this bounded change.
<!-- END ENTRY: Cache release compatibility -->
