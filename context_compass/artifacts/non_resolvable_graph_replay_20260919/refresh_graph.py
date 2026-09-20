"""Refresh only the graph/replay feature's mechanical descriptors and scoped authored deltas."""

import json
import sys
from pathlib import Path


def main() -> None:
    """Use canonical extraction/merge while preserving existing curated edges and semantic stamps."""
    root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(root))
    from context_compass.tools.system_documents.python.extract_graph import (
        extract,
        merge,
    )

    additions = {
        "melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py":
            "republishes enabled late-compiled Nexus records after local topology is available",
        "melder/nexus/frame_descriptor_manager.py":
            "publishes native resolution capability and value-only selected dependency, supplied-reference and base links",
        "melder/nexus/rift/frame_viewer/view_spell.py":
            "describes incoming and outgoing registered relationships while filtering hidden endpoints and sections",
        "melder/nexus/rift/frame_viewer/frame_viewer.py":
            "delegates registered relationship navigation to the current ACL-filtered spell viewer",
        "melder/crystallizer/crystals/spell_crystal.py":
            "captures native per-version resolution capability as a detached replay value",
        "melder/crystallizer/crystal_loader_system/restore_engine.py":
            "forwards recorded resolution capability through active and staged binding with legacy True defaults",
        "melder/crystallizer/crystal_loader_system/graft_runner.py":
            "preserves each member resolution capability through selected, parked and merged graft bindings",
        "melder/crystallizer/persistence/record_version.py":
            "uses record major 2 so older readers cannot silently ignore non-resolvable policy",
    }
    for relative, statement in additions.items():
        path = root / "context_compass/system_docs/graph" / Path(relative).with_suffix(".json")
        previous = json.loads(path.read_text(encoding="utf-8"))
        current = extract(root / "src" / relative, root / "src")
        if current is None:
            raise RuntimeError(f"Cannot parse {relative}.")
        prior_edges = {(edge["from"], edge["to_label"]): edge for edge in previous["edges_out"]}
        for edge in current["edges_out"]:
            prior = prior_edges.get((edge["from"], edge["to_label"]))
            if prior is None:
                raise RuntimeError(f"Unexpected inheritance change in {relative}.")
            edge["relation"] = prior["relation"]
            if "to" in prior:
                edge["to"] = prior["to"]
        merged, notes = merge(current, previous)
        for node in merged["nodes"].values():
            if node["label"] == "RestoreReport":
                continue
            responsibilities = node.setdefault("responsibilities", [])
            if statement not in responsibilities:
                responsibilities.append(statement)
            if node["label"] == "RecordVersion":
                node["role"] = node["role"].replace("1.0.0", "2.0.0")
        path.write_text(json.dumps(merged, indent=1) + "\n", encoding="utf-8", newline="\n")
        sys.stdout.write(f"{relative}: {len(notes)} extraction notices\n")
        for note in notes:
            sys.stdout.write(f"  {note}\n")


if __name__ == "__main__":
    main()
