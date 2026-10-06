"""
Promote the per_frame_spell_worlds test surface (A 0.2.8213, B 0.2.8214) into tests_components.md.

Usage: python apply_docs_tests.py <repository root>
Every anchor must match exactly once; nothing is written unless all do. The C1 core set must equal the union of the
catalogs' Key Files lists afterwards, or nothing is written.
"""
import datetime
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from apply_support import ApplySession

ROOT = sys.argv[1]
DOC = "context_compass/system_docs/tests_components.md"
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
s = ApplySession(ROOT)

UNIT_NEW = "tests/unit/melder/crystallizer/crystal_loader_system/test_restore_spell_id_regime.py"
COMPONENT_NEW = "tests/component/melder/aether/test_aether_spell_id_regime_property_component.py"
TWIN = "tests/integration/melder/crystallizer/test_crystallizer_aether_twin_integration.py"
INTEGRATION_NEW = "tests/integration/melder/crystallizer/test_restore_per_frame_spell_worlds_integration.py"

# Aether/Nexus/Rift unit cluster: the reload lane.
s.insert_after(
    DOC,
    "- the value snapshot the four root configurations expose (`get_configuration_dictionary()`, 0.2.8212): exact\n"
    "  properties, independence, equality, lifecycle states and the cleaned refusal\n",
    "- the Aether reload lane carrying the spell-id regime (0.2.8213): a recorded per-frame regime reloads frozen,\n"
    "  an absent one keeps the default and is reported missing\n",
)

# Crystallizer unit cluster.
s.insert_after(
    DOC,
    "- synthetic modules that materialize, import nested package graphs, re-execute\n"
    "  updated source on reload, allow a benign import cycle and surface a bad one\n",
    "- per-frame spell worlds (0.2.8213-0.2.8214): the crystal's custody key (the bare id by default,\n"
    "  \"<id>@<frame>\" per frame, the key statics, the facade reading the regime); two frames' copies coexisting in\n"
    "  the record, with lookups, activity, removal, segment payloads and index grafts addressing one copy; the facade\n"
    "  verbs needing the frame under per-frame ids and ignoring it otherwise; the retarget re-key; the impact read by\n"
    "  payload id; restore stage 1 (install, both shortfalls, the missing key, the refusal) and per-Book translation\n",
)
s.insert_after(
    DOC,
    "- `tests/unit/melder/crystallizer/test_synthetic_module.py`\n",
    f"- `{UNIT_NEW}` (2026-09-30)\n",
)

# Aether component cluster.
s.insert_after(
    DOC,
    "- root configuration guards: Aether's sealed spell-id regime refusing another regime once a frame exists\n"
    "  (0.2.8209), and an active Nexus refusing another configuration until deactivated (0.2.8210)\n",
    "- the spell-id regime in force (`Aether.process_wide_unique_spell_ids`, 0.2.8213): process-wide on a fresh\n"
    "  Aether, the installed configuration's value before the first frame, the sealed value after it (frozen\n"
    "  defaults when no configuration was installed), and the cleaned refusal\n",
)
s.insert_after(
    DOC,
    "- `tests/component/melder/aether/test_nexus_active_reconfiguration_guard_component.py` (active Nexus, 2026-09-30)\n",
    f"- `{COMPONENT_NEW}` (regime in force, 2026-09-30)\n",
)

# Crystallizer integration cluster.
s.insert_after(
    DOC,
    "- restores into live worlds: a world whose first frame sealed the Aether regime (0.2.8209), and a live active\n"
    "  Nexus replaced by the recorded policy through deactivate-first, recorded \"disabled\" included (0.2.8210)\n",
    "- per-frame spell worlds (0.2.8213-0.2.8214): the Aether twin recording the regime through configuration\n"
    "  activation and the utility re-emission; one class bound in two frames restoring both tenants under per-frame\n"
    "  ids; distinct classes restoring per-frame; a process-wide world keeping bare custody keys; a process-wide host\n"
    "  refusing a same-class per-frame record; removal in one frame keeping the other frame's custody\n",
)
s.insert_after(
    DOC,
    "- `tests/integration/melder/crystallizer/test_restore_over_active_nexus_integration.py` (2026-09-30)\n",
    f"- `{TWIN}` (2026-09-30)\n"
    f"- `{INTEGRATION_NEW}` (2026-09-30)\n",
)

# Mock crystallizer harnesses: the spell double's frame.
s.insert_after(
    DOC,
    "- provide deterministic spell-crystal and synthetic-module harness data for\n"
    "  crystallizer unit/component/integration graph cases\n",
    "- the harness spell double carries `aetheric_frame = \"default\"`, which SpellCrystal reads for its custody key\n"
    "  (0.2.8214)\n",
)

ENTRY = r"- path: `{0}`\n  start_line: 1\n  end_line: \d+\n  loc: \d+\n  verified_at: \S+\n(?:  note: .*\n)?"


def measured(path: str) -> str:
    """Return one freshly measured code-map entry for a file on disk."""
    loc = len((pathlib.Path(ROOT) / path).read_bytes().decode("utf-8").splitlines())
    return f"- path: `{path}`\n  start_line: 1\n  end_line: {loc}\n  loc: {loc}\n  verified_at: {NOW}\n"


def find_entry(path: str) -> str:
    """Return the one code-map entry block for `path` (with its note line, when present)."""
    matches = re.findall(ENTRY.format(re.escape(path)), s._load(DOC))
    if len(matches) != 1:
        raise AssertionError(f"code map entry for {path}: {len(matches)} matches")
    return matches[0]


def remeasure(path: str) -> None:
    """Rewrite one entry's range, loc and verified_at, keeping its note."""
    block = find_entry(path)
    note = block.split("  verified_at: ", 1)[1].split("\n", 1)[1]
    s.replace(DOC, block, measured(path) + note)


def add_after(anchor_path: str, path: str) -> None:
    """Insert a measured entry for `path` right after the entry of `anchor_path`."""
    s.insert_after(DOC, find_entry(anchor_path), measured(path))


for touched in (
        "tests/mocks/crystallizer/spell_crystal_harness.py",
        "tests/unit/melder/crystallizer/test_spell_crystal.py",
        "tests/unit/melder/crystallizer/test_crystallizer.py",
):
    remeasure(touched)
add_after("tests/unit/melder/crystallizer/test_synthetic_module.py", UNIT_NEW)
add_after("tests/component/melder/aether/test_nexus_active_reconfiguration_guard_component.py", COMPONENT_NEW)
add_after("tests/integration/melder/crystallizer/test_restore_over_active_nexus_integration.py", TWIN)
add_after(TWIN, INTEGRATION_NEW)

# Two catalog key files the core set had missed before this pass (measured here so the set is the union again).
text = s._load(DOC)
code_map = text[text.index("## C1 Code Map (Core)"):text.index("## Diagrams")]
catalog = text[:text.index("## C1 Code Map (Core)")]
key_files = set()
for block in re.findall(r"Key Files \(C1\):\n((?:- .*\n|  .*\n)+)", catalog):
    key_files.update(re.findall(r"^- `([^`]+)`", block, re.M))
listed = set(re.findall(r"^- path: `([^`]+)`", code_map, re.M))
missing = sorted(key_files - listed)
if listed - key_files:
    raise AssertionError(f"code map lists non-key files: {sorted(listed - key_files)}")
last_entry = re.findall(r"- path: `[^`]+`\n  start_line: 1\n  end_line: \d+\n  loc: \d+\n  verified_at: \S+\n(?:  note: .*\n)?",
                        code_map)[-1]
s.insert_after(DOC, last_entry, "".join(measured(path) for path in missing))
total = len(key_files)
count_line = re.search(r"above - (\d+) paths - and nothing else\.", s._load(DOC))
s.replace(DOC, count_line.group(0), f"above - {total} paths - and nothing else.")

# Handoff summary.
s.replace(
    DOC,
    "## Context / Handoff Summary\n\n2026-09-30 root configuration guards (0.2.8209-0.2.8212):",
    "## Context / Handoff Summary\n\n"
    "2026-09-30 per-frame spell worlds (0.2.8213-0.2.8214): three new files - the regime-in-force read (component),\n"
    "restore stage 1's regime branches and per-Book translation (unit), and per-frame worlds recorded and restored in\n"
    "fresh worlds (integration) - plus the regime rows in the existing Aether twin integration file. New rows in the\n"
    "reload-lane, persistence profile and system, record-sink, spell-crystal, impact and retarget unit files; seven\n"
    "custody stubs gained `custody_key` (the profile stub also takes a frame) and two spell doubles `aetheric_frame`,\n"
    f"which the record now reads. The C1 core set gains the four key files and {len(missing)} catalog key files it had\n"
    f"missed before this pass, so it is the union again ({total} paths); touched extents are measured.\n"
    "\n"
    "2026-09-30 root configuration guards (0.2.8209-0.2.8212):",
)

long_lines = s.long_added_lines()
if long_lines:
    raise SystemExit("long added lines:\n" + "\n".join(long_lines))
final = s._load(DOC)
final_map = final[final.index("## C1 Code Map (Core)"):final.index("## Diagrams")]
if len(set(re.findall(r"^- path: `([^`]+)`", final_map, re.M))) != total:
    raise SystemExit("core set is not the key-file union after the edit")
for written in s.write():
    print("wrote", written, "core set", total, "added missing", missing)
