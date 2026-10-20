"""S7 D5: the user-facing documentation of managed spells.

Edits the README's lifetimes and teardown sections, the docs curriculum entry built from the lifetimes section, the
scopes guide's purge table, the glossary and the release note's packaging lines. Each edit replaces one exact block
(asserted to occur exactly once) and writes it with the line ending the file uses there (README, curriculum, scopes
and glossary: CRLF; the release note: LF). Without --apply it reports the matches and writes nothing; a second
--apply refuses, because the old blocks are gone.
Run from the repository root: python <this file> [--apply]
"""
import pathlib
import sys

README_LIFETIMES_OLD = """## 🟢 Six Lifetimes, Not Three
<sub>**Beginner.** Pick how long things live.</sub>

| | Existence | One instance per | Use it for |
|:--|:---|:---|:---|
| 🟢 | `unique` | Process (frame) | Config, pools, caches |
| 🟢 | `unique_per_conduit` | Scope | Request / session state |
| 🟢 | `many` | Nothing — new every meld | Stateless workers, DTOs |
| 🟡 | `unique_per_conduit_lineage` | A scope **and its children** | Shared context down a tree |
| 🟡 | `unique_per_spell_space` | A request-local space | Ephemeral request scoping |
| 🟠 | `unique_per_conduit_cluster` | A named group of scopes | Cross-scope coordination |

**The first three are the beginner set** — they cover most systems and need
nothing but a static conjure. The last three arrive with the features that give
them meaning: lineage and spell spaces once you have nested scopes, clusters
once conduits link into groups.
"""

README_LIFETIMES_NEW = """## 🟢 Seven Lifetimes, Not Three
<sub>**Beginner.** Pick how long things live.</sub>

| | Existence | One instance per | Use it for |
|:--|:---|:---|:---|
| 🟢 | `unique` | Process (frame) | Config, pools, caches |
| 🟢 | `unique_per_conduit` | Scope | Request / session state |
| 🟢 | `many` | Nothing — new every meld | Stateless workers, DTOs |
| 🟡 | `unique_per_conduit_lineage` | A scope **and its children** | Shared context down a tree |
| 🟡 | `unique_per_spell_space` | A request-local space | Ephemeral request scoping |
| 🟡 | `managed_spell_quantity` | Nothing — leased from a pool the root keeps | Costly objects reused across holders |
| 🟠 | `unique_per_conduit_cluster` | A named group of scopes | Cross-scope coordination |

**The first three are the beginner set** — they cover most systems and need
nothing but a static conjure. The rest arrive with the need that gives them
meaning: lineage and spell spaces once you have nested scopes, managed pools
once an object costs more to build than to lend, clusters once conduits link
into groups.

A managed spell's objects are **leased**. A meld, or an injection into a
constructor, takes an idle object from the pool the owning root keeps, or
builds one; the holder gives it back when it is done:

```python
book = md.Spellbook()
book.bind(
    spell=ChannelLogger,
    existence="managed_spell_quantity",
    managed_spell_mode="limited_quantity",   # elastic (default) | limited_quantity | queue
    managed_spell_limit=8,                   # at most 8 alive at once
    managed_spell_reset_methods=["flush"],   # run on every release, in order
    disposal_method_names=["close"],         # run only when the pool destroys one
)
conduit = book.conjure()

logger = conduit.meld(ChannelLogger)         # an idle logger, or a new one
md.ReleaseManagedSpell().release(logger)     # flushed, then back in the pool

with conduit.managed_spell_meld(ChannelLogger) as logger:   # the same logger, leased again
    logger.write("ready")                                   # and given back when the block ends
```

`elastic` never refuses: it keeps up to `managed_spell_limit` idle objects (256
by default) and lets a burst's extras go once demand falls, like Melder's own
pools. `limited_quantity` raises `ManagedSpellExhaustedError` when every object
is out, and `queue` first waits up to `managed_spell_timeout_seconds` for a
release. A holder keeps what it leased until it releases it; the root's teardown
disposes the idle objects, never one that is still out.
"""

README_TEARDOWN_OLD = """Cleanup retains its existing reverse key/bucket traversal within each store. A failing
method stops that object's remaining method calls; cleanup continues with other
objects and aggregates failures into an `ExceptionGroup`.
"""

README_TEARDOWN_NEW = """Within each store, objects are disposed newest first, so a dependency outlives the
objects built on it. A failing method does not stop the others: every declared
method of every object runs, each failure is chained from what the method raised,
and they are raised together as one `ExceptionGroup` once the scope has ended.
A `managed_spell_quantity` object is disposed only when its pool destroys it — an
`elastic` trim, a reset that raises, or the root's teardown — never on release.
"""

CURRICULUM_OLD = """description = "Choose among Melder's six object lifetimes and follow examples of shared, scoped, and freshly constructed Python objects."
level = "beginner"
readme = "🟢 Six Lifetimes, Not Three"
"""

CURRICULUM_NEW = """description = "Choose among Melder's seven object lifetimes and follow examples of shared, scoped, and freshly constructed Python objects."
level = "beginner"
readme = "🟢 Seven Lifetimes, Not Three"
"""

SCOPES_OLD = """| `unique` | The spell's owning conduit |

A spell space always stays within its own creations. It cannot purge objects
belonging to its conduit, lineage root, or cluster.
"""

SCOPES_NEW = """| `unique` | The spell's owning conduit |
| `managed_spell_quantity` | No one: a conduit's purge returns `0`, and a spell space refuses it |

A spell space always stays within its own creations. It cannot purge objects
belonging to its conduit, lineage root, or cluster.

A managed spell's pool is not purged. Give its objects back with
`ReleaseManagedSpell().release(obj)`; the pool disposes idle objects when it
trims them and when the root that owns it is torn down.
"""

GLOSSARY_OLD = """   Existence
      The instance reuse and lifetime policy selected for a bound spell.

   Meld
"""

GLOSSARY_NEW = """   Existence
      The instance reuse and lifetime policy selected for a bound spell.

   Managed spell
      A spell bound with the ``managed_spell_quantity`` existence. Meld leases its objects from
      a pool the owning root keeps; ``ReleaseManagedSpell`` gives them back for reuse.

   Meld
"""

RELEASE_OLD = """- The internal-bind guard manifest holds 628 entries at 0.2.8244 (622 at 0.2.8227): `HolderDisposalEntry`, the
"""

RELEASE_NEW = """- The README's lifetimes section is "Seven Lifetimes, Not Three": it adds `managed_spell_quantity` with an example
  of a lease and its release, and the docs chapter built from that section follows the new heading. The teardown
  section no longer says that a failing disposal method stops that object's remaining methods: every declared
  method runs, and the failures are raised together once the scope has ended (the behaviour since 0.2.80 and
  0.2.8203).
- The scopes guide (`docs/intermediate/scopes.md`) lists `managed_spell_quantity` in its purge table (a conduit's
  purge returns 0, a spell space refuses it), and the glossary defines a managed spell.
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) describe managed spells: the
  member and its Phase 6 rank, the bind options and their record, the pool in the owning root's creations,
  `ReleaseManagedSpell` and the lease, leasing through compiled melds and `managed_spell_meld`, and pools in an
  ownership transfer. The packaged graph describes the five new modules; the code-map extents of the changed files
  are remeasured, and line citations that had drifted since 0.2.8235 point at their code again.
- The internal-bind guard manifest holds 628 entries at 0.2.8244 (622 at 0.2.8227): `HolderDisposalEntry`, the
"""

EDITS = (
    ("README.md", "\r\n", README_LIFETIMES_OLD, README_LIFETIMES_NEW),
    ("README.md", "\r\n", README_TEARDOWN_OLD, README_TEARDOWN_NEW),
    ("docs/curriculum.toml", "\r\n", CURRICULUM_OLD, CURRICULUM_NEW),
    ("docs/intermediate/scopes.md", "\r\n", SCOPES_OLD, SCOPES_NEW),
    ("docs/reference/glossary.md", "\r\n", GLOSSARY_OLD, GLOSSARY_NEW),
    ("release_docs/next_version_release.md", "\n", RELEASE_OLD, RELEASE_NEW),
)


def main() -> None:
    """Check every edit against the files, then apply them all or none."""
    apply = "--apply" in sys.argv[1:]
    texts = {}
    for path, eol, old, new in EDITS:
        if path not in texts:
            texts[path] = pathlib.Path(path).read_bytes().decode("utf-8")
        old_eol = old.replace("\n", eol)
        count = texts[path].count(old_eol)
        if count != 1:
            raise SystemExit(f"{path}: the old block occurs {count} times (expected 1); nothing written")
        texts[path] = texts[path].replace(old_eol, new.replace("\n", eol))
        print(f"{path}: matched ({len(old.splitlines())} -> {len(new.splitlines())} lines, eol {eol!r})")
    if not apply:
        print("dry run: nothing written (pass --apply)")
        return
    for path, text in texts.items():
        pathlib.Path(path).write_bytes(text.encode("utf-8"))
        print(f"wrote {path}")


main()
