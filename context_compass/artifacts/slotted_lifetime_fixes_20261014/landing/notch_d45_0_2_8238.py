"""D4/D5 notch, release-note entry and user-doc wording (0.2.8237 -> 0.2.8238). Run: python <this file> <tree root>."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import edit_tool

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
VERSION = str(ROOT / "src/melder/__version__.py")
NOTE = str(ROOT / "release_docs/next_version_release.md")
SCOPES = str(ROOT / "docs/intermediate/scopes.md")
OWNERSHIP = str(ROOT / "docs/intermediate/ownership.md")

print("version", edit_tool.apply(VERSION, [('__version__ = "0.2.8237"\n', '__version__ = "0.2.8238"\n')]))
print("note", edit_tool.apply(NOTE, [
    ("# Melder 0.2.8237\n", "# Melder 0.2.8238\n"),
    (
        """A `many` dependency that declares disposal methods and is built for a longer-lived object - a `unique`,
`unique_per_conduit`, `unique_per_conduit_lineage` or `unique_per_conduit_cluster` spell - now belongs to whatever
owns that object, and its disposal methods run when that owner is cleaned up. Until 0.2.8234 it was recorded with the
scope that happened to build the holder first: when a lesser conduit, a spellspace, a borrowing root or a cluster
member built the holder and then ended, Melder ran the dependency's disposal methods while the holder - kept by the
root, the conduit, the lineage root or the cluster - went on handing out the disposed object.
""",
        """A `many` dependency that declares disposal methods and is built for a longer-lived object - a `unique`,
`unique_per_conduit`, `unique_per_spell_space`, `unique_per_conduit_lineage` or `unique_per_conduit_cluster` spell -
now belongs to that object: it is disposed when the object's owner is cleaned up, it is disposed right after the
object when the object is purged, and it moves with the object to another root. Until 0.2.8234 it was recorded with
the scope that happened to build the holder first: when a lesser conduit, a spellspace, a borrowing root or a cluster
member built the holder and then ended, Melder ran the dependency's disposal methods while the holder - kept by the
root, the conduit, the lineage root or the cluster - went on handing out the disposed object. Until 0.2.8237 purging
the holder disposed the holder alone, leaving its dependencies registered and open until their scope ended (one more
for every purge-and-meld cycle), and `transfer_spell_ownership(..., move_creations=True)` moved the holder and left
its dependencies with the old root, whose teardown disposed them while the new owner kept serving the holder.
""",
    ),
    (
        """assert not repository.connection.closed          # 0.2.8234 closed it when the request scope ended
assert root.meld("Repository") is repository
root.cleanup()                                    # closes it with the root that owns the repository
```

What stays the same: a `many` spell melded directly, and the `many` dependencies of a `many` spell, are still
recorded with the scope that melds them (the spellspace, else the conduit), so a lesser conduit or a spellspace still
disposes the transients it built for itself; a `unique_per_spell_space` object was never affected. Purging an object
still disposes only that object. `has_live_creation` and `purge` for the `many` spell now find such a dependency at
the holder's owner instead of at the scope that first built the holder. Warm melds run exactly the code they ran
before.
""",
        """assert not repository.connection.closed          # 0.2.8234 closed it when the request scope ended
assert root.meld("Repository") is repository

root.purge("Repository")                          # disposes the repository, then its connection
assert repository.connection.closed               # 0.2.8237 left it open, registered, until root.cleanup()
```

A dependency that belongs to an object is no longer one of its `many` spell's own entries: `purge` and
`has_live_creation` for that spell count only the instances no object holds, so purging the spell never disposes a
dependency a live object still uses. Purging the object raises the dependencies' disposal failures together with its
own, after the object is retired, and the object is disposed before its dependencies, as at teardown.

What stays the same: a `many` spell melded directly, and the `many` dependencies of a `many` spell, are still
recorded with the scope that melds them (the spellspace, else the conduit), so a lesser conduit or a spellspace still
disposes the transients it built for itself. `purge` still returns the number of the target's own entries it removed.
Warm melds run exactly the code they ran before.
""",
    ),
]))
print("scopes", edit_tool.apply(SCOPES, [
    (
        """A spell space always stays within its own creations. It cannot purge objects
belonging to its conduit, lineage root, or cluster leader.
""",
        """A spell space always stays within its own creations. It cannot purge objects
belonging to its conduit, lineage root, or cluster.
""",
    ),
    (
        """object remains referenced by its registration, so purging its store entry does
not unbind it or turn it into a factory.
""",
        """object remains referenced by its registration, so purging its store entry does
not unbind it or turn it into a factory.

A `many` dependency with configured disposal that was built for a longer-lived
object belongs to that object: purging the object disposes the dependency too,
right after the object. Purging the dependency's own binding removes only the
instances that no object holds.
""",
    ),
]))
print("ownership", edit_tool.apply(OWNERSHIP, [(
    """a report. The saved lesson requests `move_creations=True`, inspects the report,
and resolves from the new home. Read that report when diagnosing a transfer;
sharing and moving ownership have different lifecycle consequences.
""",
    """a report. The saved lesson requests `move_creations=True`, inspects the report,
and resolves from the new home. Moved objects bring the `many` dependencies with
configured disposal that were built for them. Read that report when diagnosing a
transfer; sharing and moving ownership have different lifecycle consequences.
""",
)]))
