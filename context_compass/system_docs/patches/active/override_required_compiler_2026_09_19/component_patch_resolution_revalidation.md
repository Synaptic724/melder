# Component Patch: Rebuild resolution after structural selection changes

<!-- BEGIN ENTRY: Structural rerun invalidates conduit-local resolution -->
## Evidence and Boundary
The selector watcher correctly gates structural state. Meld reruns phases 1-4 but accepts the old
conduit-local valid verdict, so it can invoke a stale constructor plan after provider selection changes.
Repair the existing validity handoff; this is not the S4 supplied-value/direct-meld enforcement work.

## Before and After
After a successful structural rerun, use the existing _force_resolution_revalidation seam before
checking conduit-local validity. The ordinary root/spell selection logic then forces phases 5-11
through the existing path. Expose an optional reason argument on that private helper: old contract
callers retain contract_unvalidated, structural callers use structure_changed.

## Ownership and Concurrency
No new state or cache layer. Reuse the existing per-spell lock and ConduitResolutionState setters.
Structural errors still fail before resolution work; no-op when no conduit-local state exists,
because its existing missing-state path already forces compilation.

## Validation
Cache-disabled False-to-True notch and new-provider transitions rebuild and inject the selected provider.
Retain existing Meld structural/contract/gating tests. S4 still owns required-input checks, nested branch
execution, direct capability refusal and compiled-cache hydration behavior.
<!-- END ENTRY: Structural rerun invalidates conduit-local resolution -->
