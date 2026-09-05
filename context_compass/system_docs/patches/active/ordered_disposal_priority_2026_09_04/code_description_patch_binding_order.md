# Code-description patch: ordered binding metadata

## Trigger
Order composition affects stable bind identity and active/inactive registration semantics.

## Control flow
1. Inside each existing bind transaction, forward explicit names and configured names separately.
2. Forward the configuration's priority bool once per creation, not per Meld or disposal call.
3. Build the existing binding profile.
4. Allocate one result list. For non-class profiles return it empty.
5. Select the two input groups according to priority; skip an absent group.
6. Walk names in supplied order. Append only when present in profile.method_names and absent
   from the growing result. List membership is sufficient for these small method collections.
7. Feed the result to the existing SHA helper, then construct Spell with that same list.
8. Continue normal registration, staging, hooks, and emissions. No conjure-time recomposition.

## Edge / error and rollback semantics
Empty spell names do not disable book names. Missing names disappear before hashing.
Reordering retained names changes identity; changing only unmatched names does not.
Preserve existing exceptions, transaction cleanup, and index selection. No fallback signatures.

## Invariants and idempotency
Every new Spell gets independent resolved metadata; the first bind never owns later inputs.
Duplicates execute once at the position of the first retained occurrence.
Moving or sharing an existing Spell does not apply the recipient book's policy again.

## Non-goals
No compiler/Creations rewrite, new synchronization, inherited/factory matching expansion,
post-creation policy mutation, record migration, or compatibility layer.

## Validation focus
Real active/staged binds under both priorities, empty and duplicate groups, class-profile
filtering, exact list retention, same-input inspector parity, and fresh-process hashes.
