"""Refresh the bounded admission descriptors with canonical merge and explicit authored deltas."""

import json
import sys
from pathlib import Path


def main() -> None:
    """Refresh four mechanical records without replacing existing authored edges or semantic stamps."""
    root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(root))
    from context_compass.tools.system_documents.python.extract_graph import (
        extract,
        merge,
    )

    paths = (
        "melder/aether/conduit/meld/meld.py",
        "melder/aether/conduit/meld/conduit_meld.py",
        "melder/aether/conduit/meld/spellspace_meld.py",
        "melder/__init__.py",
    )
    for relative in paths:
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
            if relative == "melder/__init__.py":
                continue
            statement = (
                "provides the common non-resolvable-registration error without restricting observational lookup"
                if node["label"] in ("Meld", "meld")
                else "refuses immutable non-resolvable registrations before normal resolution and reuse-only access"
            )
            responsibilities = node.setdefault("responsibilities", [])
            if statement not in responsibilities:
                responsibilities.append(statement)
            if node["label"] == "ConduitMeld":
                node["owns_state"] = []
            elif node["label"] == "conduit_meld":
                node["responsibilities"] = [
                    "route the caller-conduit creations store through the shared Meld surface"
                    if item == "own the caller-conduit creations store" else item
                    for item in responsibilities
                ]
            elif node["label"] == "SpellSpaceMeld":
                node["owns_state"] = ["_spellspace", "_spellspace_id", "_owner_conduit_id"]
        path.write_text(json.dumps(merged, indent=1) + "\n", encoding="utf-8", newline="\n")
        sys.stdout.write(f"{relative}: {len(notes)} extraction notices\n")
        for note in notes:
            sys.stdout.write(f"  {note}\n")


if __name__ == "__main__":
    main()
