# Public graduation and normal ownership

<!-- BEGIN ENTRY: "Conduit graduation attachment" -->
## Before and after
The old public upgrade discarded its freshly allocated Book, continued using the former root's
Book and copied its resolution verdicts. Ward conversion cleared only one direction of the parent
relationship. Consequently registration, Bind callbacks and teardown crossed normal-root boundaries.

The public upgrade now selects an independent Book through the ordinary constructor, prepares this
same Conduit as a normal root and calls Spellbook._conjure_existing_conduit. The new Book starts empty;
its ordinary phases use the preserved conduit ID. No registry, contract or old root verdict transfers.
Existing conduit and Space stores remain responsible for their retained instances and disposal data.

## Interfaces
Conduit.upgrade_to_normal(name, *, configuration=None, hooks=None) keeps its None return. Configuration
uses ordinary selection: fresh defaults locally, canonical frame-owned policy in shared mode. An
explicit different shared object is rejected. Reusing the former Book's locally owned configuration
is rejected rather than creating two cleanup owners. The optional hooks mapping adds local runtime
hooks after normal activation; configured lifecycle callbacks participate in conjure itself.

## Ownership and order
- Conduit prepares status, root ID, independent ConduitPool/ClusterCreations, reciprocal ward detach
  and gate membership. Spellbook owns conjure and attachment, not the Conduit.
- The old root no longer has the graduated conduit in its ward's child map. Either normal root may
  clean up first without retiring the other's Book or new bindings.
- Meld and retained local Space doors use the new lookup maps and clear input/fast-door caches.
  Book, Conduit and Space hook setup comes from selected configuration; former local overlays vanish.
- Bind tuples are captured once at new Book construction. Default runtime events use the None key,
  with exact Book event lists taking precedence. No callback objects are serialized.
- Book constructor identity publication occurs only after configuration and registries initialize,
  so rejected configuration selection leaves no registered partial Book.

## Failure and concurrency
Preflight validates dynamic/lesser/attached/childless status, name, hook payload and configuration type.
The existing creation gate drains before structural locks. Parent ward lock precedes target locks
while detaching or undoing preparation. No changes are made to ordinary Meld hot paths.

The owner must quiesce concurrent lineage mutation/teardown and scope acquisition, and return managed
Spaces held on other threads. Their stacks are thread-local and cannot be enumerated here. Registered
manual Spaces, idle pooled Spaces and current-thread managed Spaces are rebound during attachment.

Before attachment, failure restores lesser status, borrowed root resources, ward relations and gate
membership, then cleans the failed new Book. Shared configuration is never cleaned by that Book.
After attachment, errors retain ordinary conjure's caller-owned cleanup semantics. Lifecycle callback
errors keep the established logged/suppressed behavior; external callback effects are not rolled back.

## Validation and migration
The 32 initial ownership regressions become passing tests. Healthy-upgrade and invalid-hook tests move
from fabricated preset-factory mocks to real component boundaries. Old creation tests retain storage
and disposal assertions but now reject old-ID lookup. Old seed-state tests verify the empty Book has
no resolution state and a later new binding compiles only new-root verdicts.
Generated assets and canonical document/index promotion remain held for source approval.
<!-- END ENTRY: "Conduit graduation attachment" -->
