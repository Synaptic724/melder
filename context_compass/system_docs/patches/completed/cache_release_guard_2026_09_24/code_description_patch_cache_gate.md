# Code contract: Release check at cache admission

<!-- BEGIN ENTRY: Header load and emit flow -->
## Trigger and invariants
The new release admission gate needs explicit legacy/malformed input behavior. Loading or
re-emitting a compatible envelope is repeatable; no application side effects are rolled back.

## Control flow
1. Initialize an empty envelope with CURRENT_VERSION, canonical melder_version and interpreter tag.
2. Load the existing path through marshal when present.
3. Validate the existing schema generation plus exact melder_version and interpreter tag.
4. Validate existing conduit/payload rules and preserve all accepted header fields.
5. On failure, existing _load_or_initialize_from_disk logs and uses a fresh empty envelope.
6. Normal conjure sees a miss, compiles and stages fresh payloads; existing emit persists the header.

## Edge semantics
- Missing field: cold; do not infer an old bundle's release.
- Different release, including downgrade or prerelease: cold by exact comparison.
- Malformed field: cannot equal the canonical nonempty release string, so cold.
- Same release: unchanged warm-cache path if other checks pass.
- Disabled caching: unchanged; no utility/load work is introduced.
- Read/write failure: unchanged existing behavior; writes stay atomic.
- Process-local version replacement is not runtime hot reload; tests simulate a new cache lifetime.

## Non-goals
No recursive deletion, new field probing, signature changes, compiler rewrite, per-meld guard,
new version-provider framework or persisted-record migration.

## Implementation/validation mapping
- Canonical import and empty-header field -> emitted-version assertion and import smoke check.
- Normalization field/check -> populated valid control plus wrong/missing/malformed cases.
- Writer field -> load, modify, emit and reload without dropping the stamp.
- History generation -> current-generation acceptance and every older generation rejected.
- Existing cold-cache flow -> unchanged IDs rebuild for a new release and then reuse next time.
<!-- END ENTRY: Header load and emit flow -->
