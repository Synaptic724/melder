# Component patch: Spell context lifecycle
<!-- BEGIN ENTRY: Spell context lifecycle -->
## Boundary
Spell owns the context and CounterSwitch; the frame controller indexes the stable CreationGate.
## Before and after
Before: context retirement resets idle, factory failures strand pending, gate is reached through
the context being retired. After: Spell retains the index-gate reference before publication and a
failed-build cause. Writer fencing supplies input lifetime; CounterSwitch still elects cold leaders.
## Interface and state deltas
Add private gate/failure fields with deterministic initialization and explicit cleanup. Clear the
failed cause when a real invalidation/rebuild begins. A ready context continues to return directly.
Factory exceptions record failure and reset the pending latch so followers can report the failure.
## Failure and ordering
No silent success or fake ready state. Original producer failure propagates; followers report the
failed publication with its cause. Forced/cached replacement drains readers before cleaning old context.
## Validation
Cold and warm factory contracts, multiple leaders/followers, build exception, explicit retry/rebuild,
cached context with absent codegen, and cleanable lifecycle. CounterSwitch file remains unchanged.
## Open verification
Legacy test doubles must model the real new fields; do not add owned-code introspection fallbacks.
<!-- END ENTRY: Spell context lifecycle -->
