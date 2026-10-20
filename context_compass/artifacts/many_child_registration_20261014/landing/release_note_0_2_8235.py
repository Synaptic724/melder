"""
Notch 0.2.8235 and add its entry to release_docs/next_version_release.md (both CRLF, kept CRLF).
(TASK-2026-10-14-fix_many_child_follows_holder)

Run from the repository root: python release_note_0_2_8235.py
"""
import pathlib

SECTION = '''## A `many` dependency is disposed with the object that holds it

A `many` dependency that declares disposal methods and is built for a longer-lived object - a `unique`,
`unique_per_conduit`, `unique_per_conduit_lineage` or `unique_per_conduit_cluster` spell - now belongs to whatever
owns that object, and its disposal methods run when that owner is cleaned up. Until 0.2.8234 it was recorded with the
scope that happened to build the holder first: when a lesser conduit, a spellspace, a borrowing root or a cluster
member built the holder and then ended, Melder ran the dependency's disposal methods while the holder - kept by the
root, the conduit, the lineage root or the cluster leader - went on handing out the disposed object.

```python
class Connection:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class Repository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection


book = md.Spellbook()
book.bind(spell=Connection, existence="many", disposal_method_names=["close"])
book.bind(spell=Repository, existence="unique")
root = book.conjure()

with root.enter_lesser_conduit() as request:
    repository = request.meld("Repository")      # first built inside the request scope

assert not repository.connection.closed          # 0.2.8234 closed it when the request scope ended
assert root.meld("Repository") is repository
root.cleanup()                                    # closes it with the root that owns the repository
```

What stays the same: a `many` spell melded directly, and the `many` dependencies of a `many` spell, are still
recorded with the scope that melds them (the spellspace, else the conduit), so a lesser conduit or a spellspace still
disposes the transients it built for itself; a `unique_per_spell_space` object was never affected. Purging an object
still disposes only that object. `has_live_creation` and `purge` for the `many` spell now find such a dependency at
the holder's owner instead of at the scope that first built the holder. Warm melds run exactly the code they ran
before.

With `generalized_singleton_specialization_enabled` (opt-in, off by default), a root whose graph passes a `many`
dependency to a longer-lived object is no longer specialized: the specialized path built and recorded a new
dependency on every warm meld, which the stored holder never used.

'''

BULLET = (
    "- The packaged system documents describe where a `many` dependency built for a longer-lived object is recorded (with\n"
    "  the holder's owner), the store selection and live-creation probe that follow, and the specializer's eligibility.\n"
)


def main() -> int:
    note = pathlib.Path("release_docs/next_version_release.md")
    raw = note.read_bytes().decode("utf-8")
    assert raw.count("\r\n") == raw.count("\n")
    text = raw.replace("\r\n", "\n")
    assert text.startswith("# Melder 0.2.8234\n\n**Unreleased**\n")
    text = text.replace("# Melder 0.2.8234\n", "# Melder 0.2.8235\n", 1)
    anchor = "## Packaging and documentation\n"
    assert text.count(anchor) == 1
    text = text.replace(anchor, SECTION + anchor)
    rebuild = "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8234.\n"
    assert text.count(rebuild) == 1
    text = text.replace(rebuild, BULLET + rebuild.replace("0.2.8234", "0.2.8235"))
    note.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))

    version = pathlib.Path("src/melder/__version__.py")
    vraw = version.read_bytes().decode("utf-8")
    assert vraw.count("\r\n") == vraw.count("\n")
    old = '__version__ = "0.2.8234"'
    assert vraw.count(old) == 1
    version.write_bytes(vraw.replace(old, '__version__ = "0.2.8235"').encode("utf-8"))
    print("notched 0.2.8235; release note lines", text.count("\n"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
