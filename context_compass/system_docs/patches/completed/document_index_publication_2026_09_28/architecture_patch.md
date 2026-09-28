# Document index publication: architecture patch

## Scope and non-goals
Patch id: document_index_publication_2026_09_28. Correct first-use index publication in shared
SystemDocumentView objects. No changes to document content, runtime graph operations or cursor ownership.

## Changed components
Packaged Hardcopy Documents And Public Helper Exports: workflows_0 owns system_document_view.py.

## Interface and boundary deltas
Public signatures and returned section data remain unchanged. A reader must never receive a missing
key map from a completed lazy index. Index construction remains deferred and warm reads remain lock-free.

## Cross-component invariants
The section tuple is the existing readiness marker. Its companion key map must be constructed and
published first. Concurrent builders may publish equivalent immutable values; no partial state is ready.
Payload and adjacency already publish one completed reference and retain their existing behavior.

## Migration and rollback
Add deterministic red tests; fix publication order; run focused concurrency/query suites; promote docs
and graph; notch the live version, update release notes and rebuild assets. Revert this bounded change
if necessary; no persisted schema or public API migration is involved.

## Validation and ticket map
TASK-2026-09-28-fix-system-document-lazy-publication-race owns deterministic paused-constructor and
failed-constructor retry regressions, original contention tests and their free-threaded stress run.

## Unknowns
None blocking the publication-order fix; no claim about the unrelated CI coroutine warning.
