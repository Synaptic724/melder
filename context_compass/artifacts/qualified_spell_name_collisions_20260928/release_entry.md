## Fixed: same-named classes can use distinct spell addresses

Two classes named `Repo` can now share a Spellbook when their spellframes or binding names differ.
Previously both registrations succeeded, but `conjure()` rejected them with `DUPLICATE_SPELL_NAME`,
even though its error advised adding those same qualifiers.

```python
book.bind(spell=users.Repo, spellframe="users", existence="many")
book.bind(spell=orders.Repo, spellframe="orders", existence="many")
root = book.conjure()
users_repo = root.meld(spellframe="users")
orders_repo = root.meld(spellframe="orders")
```

Phase 4 now checks the normalized `(frame_key, binding_key)` used by registration and resolution.
This also permits qualified same-named definitions with `resolvable=False` and qualified contracted
bindings. A genuine shared address still produces a collision; its diagnostic retains the
`DUPLICATE_SPELL_NAME` code and names the normalized address. Discoverable definitions retain their
address ownership and direct-meld refusal. Bare-class lookup semantics are unchanged.
