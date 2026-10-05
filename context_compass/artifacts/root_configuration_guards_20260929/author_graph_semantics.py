"""Author the graph semantics for the nodes the root configuration guards changed (melder_0, 2026-09-30).
Appends one responsibility per node (the prose was re-read against the source first) and writes the descriptor
the way extract_graph.py does (json indent=1, LF, trailing newline). Accepting (re-stamping) is a separate
graph_walker --accept call. Usage: python author_graph_semantics.py <graph_descriptor_root>"""
import json
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
ADDITIONS = {
    ("melder/aether/aether.json", "melder.aether.aether.Aether"): [
        "answers non-creating frame lookups (find_frame, get_frame, list_frame_names)",
        "seals the spell-id regime at the first frame and refuses configure/activate of a configuration with "
        "a different process_wide_unique_spell_ids while frames exist",
    ],
    ("melder/aether/aether_configuration.json", "melder.aether.aether_configuration.AetherConfiguration"): [
        "exposes a lock-guarded value snapshot of its properties (get_configuration_dictionary) for host-side "
        "policy comparison",
    ],
    ("melder/crystallizer/configuration/crystallizer_configuration.json",
     "melder.crystallizer.configuration.crystallizer_configuration.CrystallizerConfiguration"): [
        "exposes a lock-guarded value snapshot of its properties (get_configuration_dictionary)",
    ],
    ("melder/mutation_research/mutation_configuration.json",
     "melder.mutation_research.mutation_configuration.MutationResearchConfiguration"): [
        "exposes a lock-guarded value snapshot of its properties (get_configuration_dictionary)",
    ],
    ("melder/nexus/configuration/nexus_configuration.json",
     "melder.nexus.configuration.nexus_configuration.NexusConfiguration"): [
        "exposes a lock-guarded value snapshot of its properties (get_configuration_dictionary)",
    ],
    ("melder/nexus/nexus.json", "melder.nexus.nexus.Nexus"): [
        "keeps its installed policy while active: configure, and activate with another configuration, refuse "
        "until deactivate",
    ],
    ("melder/aether/spellbook/spellbook.json", "melder.aether.spellbook.spellbook.Spellbook"): [
        "refuses the recorded-world configuration discipline on the predicted conjure mode before settling the "
        "frame posture, and re-checks it on the settled mode inside the transaction window",
    ],
    ("melder/crystallizer/crystal_loader_system/restore_engine.json",
     "melder.crystallizer.crystal_loader_system.restore_engine.RestoreEngine"): [
        "deactivates an already-active live Nexus (as it does MutationResearch) before activating the reloaded "
        "Nexus configuration",
    ],
}
for (rel, node_id), phrases in ADDITIONS.items():
    path = ROOT / rel
    descriptor = json.loads(path.read_text(encoding="utf-8"))
    node = descriptor["nodes"][node_id]
    responsibilities = list(node.get("responsibilities") or [])
    for phrase in phrases:
        if phrase not in responsibilities:
            responsibilities.append(phrase)
    node["responsibilities"] = responsibilities
    path.write_text(json.dumps(descriptor, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("authored", node_id, len(responsibilities))
