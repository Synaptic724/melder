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

## Register where the code lives

Use [Declarative binding by module](module-registration.md) for `scan_bind` and
`book.scan(...)`. Scanning and explicit binding can populate the same book before
conjure. The collection download preserves the local modules needed by the lessons.
