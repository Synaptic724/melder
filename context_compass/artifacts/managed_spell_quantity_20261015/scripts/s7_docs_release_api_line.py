"""S7 D5: the release note's line for the docs site's API reference (applied after s7_docs_api.py).

Extends the scopes-guide bullet of "Packaging and documentation" with the four root exports `docs/api.toml` now
selects. Replaces one exact block of the LF file once; a second run refuses.
Run from the repository root: python <this file>
"""
import pathlib

p = pathlib.Path("release_docs/next_version_release.md")
t = p.read_bytes().decode("utf-8")
old = ("- The scopes guide (`docs/intermediate/scopes.md`) lists `managed_spell_quantity` in its purge table (a conduit's\n"
       "  purge returns 0, a spell space refuses it), and the glossary defines a managed spell.\n")
new = ("- The scopes guide (`docs/intermediate/scopes.md`) lists `managed_spell_quantity` in its purge table (a conduit's\n"
       "  purge returns 0, a spell space refuses it), and the glossary defines a managed spell. The documentation site's\n"
       "  API reference lists the four new root exports - `ManagedSpellMode`, `ReleaseManagedSpell` and `ManagedSpellLease`\n"
       "  with the lifetime types, `ManagedSpellExhaustedError` with the public errors; since 0.2.8244 the site build had\n"
       "  refused the root's export list without them.\n")
if t.count(old) != 1:
    raise SystemExit(f"the old bullet occurs {t.count(old)} times (expected 1); nothing written")
p.write_bytes(t.replace(old, new).encode("utf-8"))
print("release note: API reference line added")
