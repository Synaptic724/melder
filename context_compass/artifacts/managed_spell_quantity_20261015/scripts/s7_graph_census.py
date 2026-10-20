"""S7 graph census: per-node states now and at the 0.2.8240 commit (HEAD).

Usage: python s7_graph_census.py <descriptors now> <src now> <descriptors extracted against HEAD src>
       <HEAD src> <out file>

A descriptor whose source file is absent from its tree (stranded) contributes no nodes.

Both trees carry the same authored fields and stamps (the extractor keeps them); only
`span_sha256` differs, recomputed from each source tree. A node AUTHORED against HEAD's
source and SEMANTICS_STALE now was moved by this lane's diff; a node already stale at HEAD
is pre-existing debt. Read-only: writes only the report file.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "context_compass" / "tools"
                       / "system_documents" / "python"))
import graph_walker  # the package's walker, imported from its tools folder (added to sys.path above)


def node_states(root: pathlib.Path, src_root: pathlib.Path) -> dict:
    out = {}
    stranded = {p for p, _, _ in graph_walker.stranded_descriptors(graph_walker.load(root), src_root)}
    for path, d in graph_walker.load(root).items():
        if path in stranded:
            continue
        source = d.get("source", "")
        for nid, node in d.get("nodes", {}).items():
            state = graph_walker.state_of(node)
            unverified = state == "SEMANTICS_STALE" and graph_walker.STAMP not in node
            out[nid] = (state, unverified, source, node.get("kind", ""))
        for nid in d.get("nodes_retired", {}):
            out[nid] = ("RETIRED", False, source, "")
    return out


def main() -> None:
    now = node_states(pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]))
    head = node_states(pathlib.Path(sys.argv[3]), pathlib.Path(sys.argv[4]))
    lines = []
    groups = {}
    for nid, (state, unverified, source, kind) in sorted(now.items(), key=lambda kv: (kv[1][2], kv[0])):
        hstate = head.get(nid, ("ABSENT", False, "", ""))[0]
        if state == "AUTHORED":
            continue
        if state == "UNSEMANTIC":
            key = "UNSEMANTIC_NEW" if hstate == "ABSENT" else "UNSEMANTIC_PRE"
        elif state == "RETIRED":
            key = "RETIRED"
        elif hstate == "AUTHORED":
            key = "STALE_BY_LANE"
        elif unverified:
            key = "STALE_PRE_UNVERIFIED"
        else:
            key = "STALE_PRE_MOVED"
        groups.setdefault(key, []).append((nid, source, kind, hstate))
    for key in ("UNSEMANTIC_NEW", "UNSEMANTIC_PRE", "STALE_BY_LANE", "STALE_PRE_MOVED",
                "STALE_PRE_UNVERIFIED", "RETIRED"):
        rows = groups.get(key, [])
        lines.append(f"## {key}: {len(rows)}")
        for nid, source, kind, hstate in rows:
            lines.append(f"{nid}\t{kind}\t{source}\thead={hstate}")
        lines.append("")
    pathlib.Path(sys.argv[5]).write_text("\n".join(lines), encoding="utf-8")
    for key in ("UNSEMANTIC_NEW", "UNSEMANTIC_PRE", "STALE_BY_LANE", "STALE_PRE_MOVED",
                "STALE_PRE_UNVERIFIED", "RETIRED"):
        print(key, len(groups.get(key, [])))


if __name__ == "__main__":
    main()
