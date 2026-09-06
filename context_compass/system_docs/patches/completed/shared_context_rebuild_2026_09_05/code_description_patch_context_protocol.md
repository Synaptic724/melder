# Code-description patch: Shared context protocol
<!-- BEGIN ENTRY: Shared context protocol -->
## Trigger
Concurrency-sensitive publication, reader lifetime, failed leadership and overlapping producer scopes.
## Reader control flow
Resolve/validate using current public behavior. In dynamic mode, admit the stable Spell index gate.
If resolution became deferred while waiting, unregister before validation/rebuild and admit again.
Read readiness and the live context, build only through normal CounterSwitch election if necessary,
execute current context slots, and unregister in finally. Automatic doors remain unchanged.
## Writer control flow
Resolve the exact affected Spell set before invalidation. Borrow and deduplicate its dynamic gates,
acquire existing transition locks in increasing index-id order, remember only each prior enabled
posture (needed for restoration), freeze all, then drain. Run the normal phase sequence. Before
reopening, publish from available completed inputs; mark uncompiled affected dependencies deferred.
Release in reverse acquisition order. Scope storage is a held-resource ledger, not a runtime snapshot.
## Failure and rollback
An entry/drain failure releases every already acquired resource and propagates. A phase/publication
failure records its cause for unpublished contexts and wakes pending selectors; it never constructs
a pretend usable context. Cleanup and gate reopening are finally-owned, preserving earlier freezes.
Cold leader failure similarly aborts the latch and releases waiting followers before re-raising.
## Invariants
One dynamic ticket pair. No input retirement while an admitted reader/builder is using that input.
No generic CounterSwitch change. No global reader lock. Gate lifetime remains with its existing owner.
## Non-goals
No CI relaxation, hidden retry of identity candidates, defensive copies of runtime registries, or
unrelated public cleanup behavior redesign.
## Validation focus
Force the phase-5/phase-11 gap; hold an acquired reader across an attempted rebuild; force selected
builder failure; overlap dependency scopes; exercise cache/deferred/automatic/hook/override branches.
Do not claim nested/teardown safety or performance until the corresponding checks are recorded.
<!-- END ENTRY: Shared context protocol -->
