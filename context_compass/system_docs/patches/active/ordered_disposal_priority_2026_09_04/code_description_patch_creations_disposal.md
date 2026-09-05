# Code-description patch: Creations reference lifetime

## Trigger justification
The same Spell list may be held by compiler namespaces, multiple creation entries, and an
in-memory ownership-transfer payload. Teardown must not empty another holder's policy.

## Control flow
1. Registration retains the supplied list when disposal is enabled; omitted names get an empty list.
2. Extraction detaches raw objects and attaches the existing method-list reference to each row.
3. Restoration retains each row's list in the destination entry.
4. Existing cleanup detaches registries, traverses keys/buckets in reverse, and invokes names
   in their stored order. It releases registry entries, not the shared names' contents.
5. Generalized manifest inline registration writes entries directly and must follow the same
   reference rule. Its two emitted list copies are removed without altering locks or routing.

## Edge/error behavior and rollback
Preserve empty/disabled paths, duplicate-key errors, restore shape errors, and failure aggregation.
Revert only these reference substitutions if a real transfer/ownership conflict emerges.

## Invariants and idempotency
No additional matching, configuration lookup, reflection probe, lock, or copied inner list.
Cleanup remains idempotent; clear/reset remain reusable under their current locking contracts.

## Non-goals
No invocation-loop rewrite, stronger chronology across interleaved keys, or persistent replay changes.

## Validation focus
Observe actual calls and reference identity through registration, extract/restore, reusable
clearing, and compiled runtime families. Existing failure and reverse-order tests remain authoritative.
