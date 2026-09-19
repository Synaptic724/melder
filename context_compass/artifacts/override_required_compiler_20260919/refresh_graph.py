"""Refresh S3 mechanical descriptors while preserving authored edges and unrelated work."""

import json
import sys
from pathlib import Path


def main() -> None:
    """Use canonical extraction/merge for the bounded compiler and revalidation source set."""
    root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(root))
    from context_compass.tools.system_documents.python.extract_graph import (
        extract,
        merge,
    )

    paths = (
        "melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py",
        "melder/aether/conduit/meld/meld.py",
        "melder/aether/spellbook/spellbook_creation_system.py",
        "melder/aether/spellbook/spell_compiler/dag/socket_kind.py",
        "melder/aether/spellbook/spell_compiler/topology/spell_local_topology.py",
        "melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py",
        "melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py",
        "melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py",
        "melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py",
        "melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py",
        "melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py",
        "melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py",
        "melder/aether/spellbook/spell_compiler/validation/strategies/required_holes_strategy.py",
        "melder/aether/spellbook/spell_compiler/validation/strategies/binding_resolution_cycle_strategy.py",
        "melder/aether/spellbook/spell_compiler/validation/strategies/annotation_shape_guard_strategy.py",
        "melder/aether/spellbook/spell_compiler/validation/strategies/parameter_policy_strategy.py",
        "melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py",
        "melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_injection_analysis.py",
        "melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py",
        "melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py",
        "melder/aether/spellbook/spell_compiler/codegen_planner/data/many_only_codegen_plan.py",
        "melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py",
    )
    for relative in paths:
        path = root / "context_compass/system_docs/graph" / Path(relative).with_suffix(".json")
        previous = json.loads(path.read_text(encoding="utf-8"))
        current = extract(root / "src" / relative, root / "src")
        if current is None:
            raise RuntimeError(f"Cannot parse {relative}; stop without guessing.")
        prior_edges = {(edge["from"], edge["to_label"]): edge for edge in previous["edges_out"]}
        # This patch changes no base classes. Preserve the canonical cross-file
        # relation classification and refuse an unexpected inheritance change.
        for edge in current["edges_out"]:
            prior = prior_edges.get((edge["from"], edge["to_label"]))
            if prior is None:
                raise RuntimeError(f"New inheritance in {relative}; run complete extraction.")
            edge["relation"] = prior["relation"]
            if "to" in prior:
                edge["to"] = prior["to"]
        merged, notes = merge(current, previous)
        path.write_text(json.dumps(merged, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(relative)
        for note in notes:
            if "NEW" in note or "ORPHAN" in note:
                print(f"  {note}")


if __name__ == "__main__":
    main()
