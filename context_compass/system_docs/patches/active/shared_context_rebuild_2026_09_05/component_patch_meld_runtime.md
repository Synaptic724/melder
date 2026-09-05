# Component patch: Meld admitted context acquisition
<!-- BEGIN ENTRY: Meld admitted context acquisition -->
## Boundary
ConduitMeld and SpellSpaceMeld share lookup/validation but own their current storage semantics.
## Before and after
Before: both doors retrieve a context, then context.execute acquires its index ticket. After:
their shared dynamic execution helper acquires the existing index ticket before retrieving the
current context and directly executes its current door slots while holding that ticket.
## Interface deltas
One private dynamic helper handles no-hooks instance returns and hooks tuple returns. Public calls,
storage routing, hooks and automatic-mode fast doors remain unchanged. Standalone context execution
keeps its existing compatibility methods; production dynamic doors do not double-admit through them.
## State and failure ordering
Perform validation before admission. If a dependency was deferred while admission was parked,
release the ticket, run the existing validation/deferred path, then reacquire. This is an input-generation
recheck, not identity-resolution probing. All executor/context failures release exactly one held ticket.
## Validation
Original controlled gap, both doors, hooks/overrides, acquired reader lifetime, admission race,
automatic fast-door tests and dynamic ticket counts. Measure costs rather than claiming zero overhead.
## Open verification
Nested callback and concurrent cleanup behavior remain required qualification gates.
<!-- END ENTRY: Meld admitted context acquisition -->
