"""
Author the per_frame_spell_worlds semantics (A 0.2.8213, B 0.2.8214) into the touched graph descriptors.

Usage: python apply_graph_semantics.py <repository root>
Edits authored fields only (responsibilities, owns_state, one role); the mechanical tier stays the extractor's.
Writes in the extractor's JSON format (indent=1). Refuses a node or a duplicate it does not expect.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]) / "context_compass" / "system_docs" / "graph" / "melder"

ADDITIONS = {
    ("aether/aether.json", "melder.aether.aether.Aether"): [
        "reports the spell-id regime in force (process_wide_unique_spell_ids, lock-free): the sealed value once a frame"
        " exists, else the installed configuration's, else True",
    ],
    ("aether/aether_configuration.json", "melder.aether.aether_configuration.AetherConfiguration"): [
        "records process_wide_unique_spell_ids in the Aether root twin and reloads it in from_recorded_payload"
        " (reported missing when absent)",
    ],
    ("aether/aether_utility_system.json", "melder.aether.aether_utility_system.AetherUtilitySystem"): [
        "re-emits the Aether root twin from live logger truth plus the Aether's regime in force, read only from an"
        " initialized, uncleaned Aether",
    ],
    ("crystallizer/crystallizer.json", "melder.crystallizer.crystallizer.Crystallizer"): [
        "keys spell crystals per frame under per-frame spell ids; emit_spell_removed, emit_spell_activity and"
        " get_spell_crystal address one custody key through frame_name",
    ],
    ("crystallizer/crystals/spell_crystal.json", "melder.crystallizer.crystals.spell_crystal.SpellCrystal"): [
        "keys its record entry: custody_key is the spell id, or \"<spell_id>@<frame>\" when built with"
        " per_frame_custody (the frame read from spell.aetheric_frame)",
    ],
    ("crystallizer/persistence/persistence_profile.json",
     "melder.crystallizer.persistence.persistence_profile.PersistenceProfile"): [
        "keys spell custody by custody key (the spell id, or \"<spell_id>@<frame>\" under per-frame spell ids);"
        " lookups, activity, removal and index grafts address one frame's copy",
    ],
    ("crystallizer/persistence/persistence_system.json",
     "melder.crystallizer.persistence.persistence_system.PersistenceSystem"): [
        "passes custody keys and frame-aware custody lookups through to the active profile",
    ],
    ("crystallizer/persistence/record_version.json", "melder.crystallizer.persistence.record_version.RecordVersion"): [
        "uses major 4 to fence older readers from frame-scoped custody keys (per-frame spell ids)",
    ],
    ("crystallizer/crystal_loader_system/restore_engine.json",
     "melder.crystallizer.crystal_loader_system.restore_engine.RestoreEngine"): [
        "stage 1 installs the recorded spell-id regime, files a shortfall when a fixed live regime differs, and refuses"
        " a record binding one spell id in two frames under process-wide ids",
        "stage 6 keys bind order, member-index lookup and recorded-to-live spell translation per Book",
    ],
    ("crystallizer/crystal_loader_system/load_admission.json",
     "melder.crystallizer.crystal_loader_system.load_admission.LoadAdmission"): [
        "retargets spell custody: rewrites frame_name and re-keys frame-scoped custody keys for the target frame",
    ],
    ("crystallizer/crystal_analysis/impact_engine.json", "melder.crystallizer.crystal_analysis.impact_engine.ImpactEngine"): [
        "answers a bare spell id through its lowest frame-scoped custody key (by payload id)",
    ],
}
OWNS = {
    ("crystallizer/crystals/spell_crystal.json", "melder.crystallizer.crystals.spell_crystal.SpellCrystal"): [
        "_frame_name, _custody_key (the record key)",
    ],
}
ROLES = {
    ("crystallizer/persistence/record_version.json", "melder.crystallizer.persistence.record_version.RecordVersion"): (
        "Static record-schema version authority (stamp 2.0.0; readers gate on MAJOR; absent stamps read 0.0.0).",
        "Static record-schema version authority (stamp 4.0.0; readers gate on MAJOR; absent stamps read 0.0.0).",
    ),
}

touched = {}
for (relative, node_id), items in list(ADDITIONS.items()) + [((k[0], k[1]), None) for k in OWNS] + [
        ((k[0], k[1]), None) for k in ROLES]:
    if relative not in touched:
        touched[relative] = json.loads((ROOT / relative).read_text(encoding="utf-8"))
for (relative, node_id), items in ADDITIONS.items():
    node = touched[relative]["nodes"][node_id]
    for item in items:
        if item in node.get("responsibilities", []):
            raise SystemExit(f"{node_id}: responsibility already present")
        node.setdefault("responsibilities", []).append(item)
for (relative, node_id), items in OWNS.items():
    node = touched[relative]["nodes"][node_id]
    for item in items:
        if item in node.get("owns_state", []):
            raise SystemExit(f"{node_id}: owns_state already present")
        node.setdefault("owns_state", []).append(item)
for (relative, node_id), (old, new) in ROLES.items():
    node = touched[relative]["nodes"][node_id]
    if node.get("role") != old:
        raise SystemExit(f"{node_id}: unexpected role {node.get('role')!r}")
    node["role"] = new
for relative, descriptor in touched.items():
    text = json.dumps(descriptor, indent=1) + "\n"
    if "context_compass/" in text:
        raise SystemExit(f"{relative}: package path in a descriptor")
    (ROOT / relative).write_text(text, encoding="utf-8", newline="\n")
    print("authored", relative)
