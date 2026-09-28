# Document index publication: component contract

## Purpose and boundary
SystemDocumentView lazily materializes the section tuple and exact-key map over immutable shipped rows.

## Before and after
Before, _sections becomes non-None while _by_key is absent. Another reader skips the loader and fails.
After, the complete MappingProxyType is assigned before _sections, which remains the completion marker.

## Interfaces and state
No new field, lock, public method or eager import. Preserve _sections, _by_key and _index's return shape.
Both public document views and inherited graph views use the same corrected base method.

## Failure behavior
If key-map construction raises, _sections stays None and a later access retries. Do not swallow the
original construction exception or return an empty map. Concurrent builders still produce equal data.

## Dependencies and ordering
Immutable index rows -> local section tuple -> completed key map -> ready section tuple -> public reads.
The existing _doc and _graph completion assignments and private reader cursors remain unchanged.

## Validation
Pause the first mapping construction and read through another thread; exact sections/text must match.
Inject one mapping-construction failure and verify a later public lookup retries successfully.
Retain the original simultaneous index/text/adjacency contention test and run related query suites.

## Open decisions
None; readiness-last ordering is the smallest correction consistent with current lock-free semantics.
