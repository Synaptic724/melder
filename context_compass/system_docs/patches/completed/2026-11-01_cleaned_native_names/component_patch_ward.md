# ConduitWard and Contracts contract
<!-- BEGIN ENTRY: "Ward terminal enum assignment" -->
## Purpose and boundary
One native ConduitWard.cleanup terminal-state assignment.
## Before and after
The original instance-based self._conduit_type.cleaned access fails after the rename.
Assign the already-imported canonical ConduitState.CLEANED explicitly.
## Interface and errors
No new public API or exception behavior; ordinary cleanup completes as before.
## State and lifecycle
Keep the double cleaned check, existing lock, contract/child cascade, state publication,
metadata/logger teardown and collected-child-failure ordering exactly as written.
## Failure delta
Three complete-module cleanup regressions now fail at the old member lookup; repair that
lookup only, without changing their assertions, fixtures or any disposal contract.
## Dependencies and order
C5 read the complete4063-line source at59e5b9ce and its indexed component/graph units.
Read/register this extension and map it before the one-line source edit.
## Validation and unknowns
Repeat the unchanged complete393-case affected run, preserving its3FAIL/390PASS causal result.
Check both class-qualified and instance-based remaining name uses; public cache proof remains
a separate unfinished criterion. No remaining Ward implementation unknown blocks this edit.
<!-- END ENTRY: "Ward terminal enum assignment" -->
