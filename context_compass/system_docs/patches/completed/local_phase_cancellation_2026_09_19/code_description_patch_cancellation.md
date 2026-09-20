# Code Description Patch: Preserve cancellation scope at phase invocation

<!-- BEGIN ENTRY: Run-scoped local unit factory -->
## Trigger and Control Flow
Cancellation lifetime is concurrency-sensitive. The registration helper stores ordinary args and
whether the compiler accepts cancellation. During factory invocation it constructs keyword args
from the scheduler's current event and creates the UnitOfWork through the existing scheduler API.

## Error and Lifecycle Semantics
No retry, exception translation, signal reset, extra lock or disposal is added. The scheduler retains
exclusive signal ownership and its existing per-run lock/barriers. Calls without a cancellation
parameter receive no keyword arguments. A failing prior run and a cancelled current run stay distinct.

## Validation and Non-Goals
Recovery must pass on one and four workers after a real prior phase failure. Both local Phase-5 and
Phase-6 bodies must observe cancellation of their current run. Do not change the churn test's settled
success expectations or broaden into scheduler/lifecycle redesign.
<!-- END ENTRY: Run-scoped local unit factory -->
