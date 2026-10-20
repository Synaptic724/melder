"""D2 notch, release-note entry and user-doc wording (0.2.8236 -> 0.2.8237). Run from the repository root."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import edit_tool

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
VERSION = str(ROOT / "src/melder/__version__.py")
NOTE = str(ROOT / "release_docs/next_version_release.md")
GUIDE = str(ROOT / "docs/advanced/clusters.md")
EXAMPLE = str(ROOT / "UX_and_AIX_experiences/02_intermediate/25_clusters_unique_per_cluster.py")

print("version", edit_tool.apply(VERSION, [('__version__ = "0.2.8236"\n', '__version__ = "0.2.8237"\n')]))
print("note", edit_tool.apply(NOTE, [
    ("# Melder 0.2.8236\n", "# Melder 0.2.8237\n"),
    (
        """scope that happened to build the holder first: when a lesser conduit, a spellspace, a borrowing root or a cluster
member built the holder and then ended, Melder ran the dependency's disposal methods while the holder - kept by the
root, the conduit, the lineage root or the cluster leader - went on handing out the disposed object.
""",
        """scope that happened to build the holder first: when a lesser conduit, a spellspace, a borrowing root or a cluster
member built the holder and then ended, Melder ran the dependency's disposal methods while the holder - kept by the
root, the conduit, the lineage root or the cluster - went on handing out the disposed object.
""",
    ),
    (
        "## Packaging and documentation\n",
        """## A cluster's shared object belongs to the cluster, not to its leader

A `unique_per_conduit_cluster` object now lives in the cluster's own store for as long as the cluster exists. Electing
a leader serves it to every member; a leader leaving the cluster or being torn down keeps it; the next leader serves
the same object; and deleting the cluster, or tearing its frame down, disposes it once. Until 0.2.8236 the object
lived in the elected leader conduit's own store: after a leader change the next election built a second object, and
tearing the old leader down disposed the first one while members' objects still used it. Deleting a cluster disposed
nothing.

```python
workers.elect_leader(leader.id)
bus = member.meld("ClusterBus")
cloud.remove_conduit_from_cluster(leader, "workers")
workers.elect_leader(member.id)
assert member.meld("ClusterBus") is bus      # 0.2.8236 built a second bus
leader.cleanup()                              # 0.2.8236 closed the first bus here
cloud.delete_cluster("workers")               # closes the bus, once
```

`delete_cluster()` now raises an `ExceptionGroup` of the cluster objects' disposal failures, after the cluster is
deleted; frame teardown logs them and keeps going.

What stays the same: a cluster still needs an elected leader before its object can be melded, only the elected leader
can purge it, and `describe_live_creation_status()` still reports `"cluster_leader"` as its `storage_scope_kind`.

## Packaging and documentation
""",
    ),
]))
print("guide", edit_tool.apply(GUIDE, [(
    """Leader election matters: the shared creations store belongs to the elected leader.
Membership alone does not establish that store. Links matter too: the sharing
contracts use the relationship between the conduits.
""",
    """Leader election matters: the shared creations store belongs to the cluster, and it is
served only while a leader is elected. Membership alone does not serve it. A leader
change keeps the shared object, and deleting the cluster disposes it. Links matter
too: the sharing contracts use the relationship between the conduits.
""",
)]))
print("example", edit_tool.apply(EXAMPLE, [
    (
        """    # ELECT THE LEADER before more members join: the cluster's shared
    # store belongs to the elected leader, and joins auto-share against
    # the armed cluster - then the rest falls into place.
""",
        """    # ELECT THE LEADER before more members join: the cluster's shared
    # store belongs to the cluster and is served while a leader is elected,
    # and joins auto-share against the armed cluster - then the rest falls
    # into place.
""",
    ),
    (
        """    assert bus_a is bus_b, "cluster members must share the elected leader's bus"
""",
        """    assert bus_a is bus_b, "cluster members must share the cluster's bus"
""",
    ),
]))
