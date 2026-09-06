# Component patch: Compiler rebuild ownership
<!-- BEGIN ENTRY: Compiler rebuild ownership -->
## Boundary
Phase 5 replaces artifacts over a dependency scope; orchestration owns sequencing through phase 11.
## Before and after
Before: foundations and plans are separate scheduler runs and readers can build between them.
After: a rare writer scope spans the complete operation, including context publication or failure.
## Interface deltas
Add a read-only Phase-5 scope resolver based on the same adjacency/visibility rules used by run_local.
Guard target, deferred and live conduit-wide rebuild entrypoints. Preserve scheduler labels and result
shapes. Initial unpublished objects need no dynamic reader gate; no automatic warm read is changed.
## State/lifecycle/failure
Hold ordered shared index transition locks across freeze/drain/rebuild. Phase workers only write
under their enclosing producer's authority. Publish contexts from completed inputs before reopen.
Dependencies invalidated without a target plan are marked resolution-required and rebuilt on demand.
On exception, preserve its cause for unpublished affected contexts and unwind gate ownership.
## Ordering constraints
No new gate acquisition in a phase worker when the orchestrating thread holds that gate lock.
Existing Spell root locks are not repurposed as a per-meld reader mutex. Changes to lock ordering
must be justified against actual call paths and exercised under controlled overlap tests.
## Validation
Original cluster case, shared dependencies, independent scope progress, deferred/cache paths,
phase failure/cancellation and teardown. Preserve original error/diagnostic contracts.
## Open verification
Conjure/cache publication and structural invalidation must be audited alongside local revalidation.
<!-- END ENTRY: Compiler rebuild ownership -->
