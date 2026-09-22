# Bind hook execution and failure contract

## Ordered operation
Book admits existing bind transaction, converts existing enum inputs, retains one Bind hook set and
passes it into Bind construction. Bind calls pre with the original reference, then runs native
admission/profile/fingerprint/Spell construction. Immediately afterward it runs activation on that
actual unpublished Spell and completes its profile. Book performs normal registration/publication,
then calls post with the same Spell and captured post sequence. The original spell_id return remains.

Inactive binding has the same construction path. Post sees the final target index and parked state.
Later promotion does not rerun this lifecycle. Scan and fluent wrappers reach the same Book methods.

## Snapshot and reentrancy
The callback registry is one immutable tuple of three immutable stage tuples. Retaining its reference
at bind entry is necessary for current-operation consistency when callbacks or other threads update
the registry. Updates assign a replacement under Bind's lock. No mutable-registry copy per bind.
User callbacks run outside the construction lock. Recursive binding uses the existing transaction
rules; callback recursion termination remains application responsibility.

## Errors and cleanup
HookExecutionError identifies pre_bind, bind_activation or post_bind and chains the original error.
Callback return values are ignored; rejection is exception-based. Stop the stage and later phases on
an exception. Activation failure sets Spell's existing local-teardown guard before cleanup, and cleans
only its new index; it must not enter Book's published-removal path. Never dispose a supplied object.
Post is a completed-registration notification, not a transaction commit hook: external effects and
already-published state have no new rollback guarantee. Native commit/abort and structural gates stand.

## Recording updates
Append/clear serializes registry changes and marker emission; the Book emission helper acquires no
Book map lock. Origin-bearing freeze uses current stage names. Replacements are whole Book twins,
not marker-only deltas. Missing restore callback code remains explicitly reported.

## Delivery hold
Runtime tests are permitted. No graph assembly, indexes, manifest generation or build runner until
owner code approval. Stale navigation indexes are bypassed with direct source reads, not regenerated.
