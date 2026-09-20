# Fluent registration and module scanning

Start with the [Beginner rhythm](../beginner/rhythm.md): registration still ends
with one conjure. `SpellBinder` gives each registration a fluent sentence. A
sentence chooses the object, lifetime, permissions, category, and name, then
`finalize()` applies it to the book. The binder can be reused for another sentence.

The full-chain lesson registers an HTTP client under `network` / `payments-api`
and a policy with a separate instance per conduit. Its assertions check the
client's configured values and the root/child policy identity difference.

## Bind options and constructor inputs

`with_kwargs(...)` supplies **registration parameters**. In the lesson it supplies
the disposal vocabulary. The client's `base_url` and `timeout` are supplied through
`meld(override=...)`. Keeping these channels distinct prevents configuration from
being attached to a registration while the constructor still receives its defaults.

Ordinary constructor defaults are honored even when a matching provider is registered.
`dependency: Optional[Service] = None` retains `None`, and `dependency: Service = chosen_service`
retains that exact instance. A default does not create an inferred dependency edge. This also applies
to collection defaults, `0`, `False`, and empty values.
An explicit `meld(override={"dependency": replacement})` still supplies a value in place of the default.

To request injection, omit the default (`dependency: Service`) or use an explicit `SpellMap` or
`SpellContract` descriptor. `Optional[Service]` without a default still requests inferred DI.

## Register a definition without making it resolvable

Use `resolvable=False` for an abstract base or helper that belongs in the registered graph but
must not be constructed or returned by Melder. Both `bind` and `bind_inactive` default to
`resolvable=True`; the choice belongs to each bound version.

```python
from melder import Spellbook

class ExternalService:
    pass

class Worker:
    def __init__(self, service: ExternalService) -> None:
        self.service = service

book = Spellbook()
definition_id = book.bind(spell=ExternalService, existence="unique", resolvable=False)
book.bind(spell=Worker, existence="many")
conduit = book.conjure()
try:
    service = ExternalService()
    worker = conduit.meld(Worker, override={"service": service})
    assert worker.service is service
finally:
    conduit.permanent_cleanup()
```

Directly melding `definition_id` raises `MeldExecutionError`. Its metadata remains inspectable.
Required constructor annotations retain the registered reference without an executable dependency.
Python reports omitted required arguments; Melder adds no separate argument preflight. Keep a
parameter genuinely required when you want Python to enforce supply, and use ordinary defaults only
for valid application fallbacks. An explicit DI descriptor default is not a required Python argument.

On a Rift-enabled frame, refresh the Rift's projections after external changes and use
`frame_viewer.describe_spell_relationships(source_id, frame_name=...)` to navigate visible dependencies,
supplied references and registered direct bases. Source IDs use `book.id:spell_id`. Existing research
commands provide source/history reads. Existing version rules still apply; method-body edits alone
do not mint a new binding version.

Crystallizer records and restores the flag, including parked members and index grafts. New durable
records use schema major 2 so older readers refuse rather than silently enabling a definition.
Legacy records without the flag retain ordinary resolvable behavior.

## Register where the code lives

Use [Declarative binding by module](module-registration.md) for `scan_bind` and
`book.scan(...)`. Scanning and explicit binding can populate the same book before
conjure. The collection download preserves the local modules needed by the lessons.
