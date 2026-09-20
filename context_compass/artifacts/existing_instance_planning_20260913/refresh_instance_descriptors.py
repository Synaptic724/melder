"""Refresh only the two existing-instance scanner descriptors with the canonical extractor."""

import json
import sys
from pathlib import Path


def main() -> None:
    """Preserve authored fields and unrelated descriptors while refreshing scanner source facts."""
    repository = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repository))
    from context_compass.tools.system_documents.python import extract_graph

    source_root = repository / "src"
    descriptor_root = repository / "context_compass/system_docs/graph"
    paths = (
        "melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py",
        "melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py",
    )
    for relative in paths:
        target = descriptor_root / Path(relative).with_suffix(".json")
        old = json.loads(target.read_text(encoding="utf-8"))
        fresh = extract_graph.extract(source_root / relative, source_root)
        if fresh is None:
            raise RuntimeError(f"Could not parse {relative}")
        if fresh["nodes"].keys() != old["nodes"].keys():
            raise RuntimeError(f"Unexpected node-set change in {relative}")
        for edge in fresh["edges_out"]:
            edge_target = fresh["imports"].get(edge["to_label"])
            if edge_target is None:
                raise RuntimeError(f"Unresolved base edge in {relative}: {edge}")
            edge["to"] = edge_target
        merged, notes = extract_graph.merge(fresh, old)
        target.write_text(json.dumps(merged, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(f"REFRESHED {relative}; {len(notes)} semantic notices for explicit review")


if __name__ == "__main__":
    main()
