# Configuration and Bind initialization

<!-- BEGIN ENTRY: "Configuration initial hooks" -->
## Before and after
Before: configuration holds Conduit/Meld maps by Book ID; Bind always starts empty. Future Book IDs
cannot be named conveniently when preparing optional upgrade configuration.
After: optional None Book key supplies default runtime events. Per-Book event keys override the
corresponding defaults. Independent Bind seeds are an immutable three-tuple stored on configuration.

## API and ownership
add_bind_hooks(pre=None, activation=None, post=None) validates ordered callable sequences then appends.
clear_bind_hooks clears those defaults before freeze. get_bind_hooks returns the immutable callback
set; with_bind_hooks is the fluent append form. Book passes this set into Bind construction once.
Changing configuration defaults affects future Books only; existing Books use their own add/clear API.
No per-bind configuration read is added. Configuration cleanup releases its callback references.

Existing add_hook/with_hook accept explicit None for defaults; add_hooks/with_hooks allow omission.
Runtime getters retain old live-map behavior when no merge is needed. Combining default and specific
event maps makes a new dictionary while keeping callback lists borrowed from the frozen configuration.
The merged compatibility getter still returns copied lists. No global runtime-hook propagation added.

## Recording and validation
Effective default event names appear in the existing Book twin, without encoding callbacks.
Bind presence comes from the initialized Book registry. Tests cover default empty behavior, all Bind
stages, local/shared config, immutable per-Book isolation, freeze/cleanup, invalid batches, default
runtime events and per-Book precedence. Existing direct Book hook tests must remain compatible.
<!-- END ENTRY: "Configuration initial hooks" -->
