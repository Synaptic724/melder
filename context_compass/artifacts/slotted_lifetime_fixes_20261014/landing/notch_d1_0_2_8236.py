"""D1 notch and release-note entry (0.2.8235 -> 0.2.8236). Run from the repository root."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import edit_tool

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
VERSION = str(ROOT / "src/melder/__version__.py")
NOTE = str(ROOT / "release_docs/next_version_release.md")

print("version", edit_tool.apply(VERSION, [('__version__ = "0.2.8235"\n', '__version__ = "0.2.8236"\n')]))
print("note", edit_tool.apply(NOTE, [
    ("# Melder 0.2.8235\n", "# Melder 0.2.8236\n"),
    (
        "## Packaging and documentation\n",
        """## A root that is torn down leaves its cluster, and leaving a cluster unshares its roots

A root conduit that is torn down - `cleanup()`, the end of a `with` block, or its frame's teardown - now leaves its
conduit cluster first, as `remove_conduit_from_cluster()` would. Until 0.2.8235 it stayed in the cluster as a member,
and as the leader when it led: `unelect_leader()` then failed part-way, `elect_leader()` refused because a leader was
still recorded, adding another conduit raised, and `delete_cluster()` removed the cluster and then raised before
cleaning it up. A torn-down leader now leaves the cluster with no leader, ready to elect another member.

```python
cloud = owner.get_conduit_cloud()
cloud.create_cluster("workers")
for root in (owner, leader, member):
    cloud.add_conduit_to_cluster(root, "workers")
workers = cloud.get_cluster("workers")
workers.elect_leader(leader.id)

leader.cleanup()                    # leaves "workers"; the cluster has no leader now
workers.elect_leader(member.id)     # 0.2.8235 refused: the torn-down leader was still recorded
cloud.delete_cluster("workers")     # 0.2.8235 removed the cluster, then raised before cleaning it up
```

`remove_conduit_from_cluster()` now also takes the leaving conduit's shared roots back from every remaining member,
and theirs from it. Until 0.2.8235 the leave dropped its record of what the conduit had shared before it unshared it,
so every remaining member kept the leaving conduit's roots in its contracts.

What stays the same: `remove_conduit_from_cluster()` still needs a dynamic frame with clusters enabled, a conduit
belongs to at most one cluster, and `get_clusters_for_conduit()` returns the same list - it now reads the frame's
membership index instead of walking every cluster.

## Packaging and documentation
""",
    ),
]))
