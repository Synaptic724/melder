"""
Promote the 0.2.8208 host read surface tests into tests_components.md.

Usage: python apply_docs_tests.py <repository root>
Every anchor must match exactly once; nothing is written unless all do. The C1 core set must equal the union of
the catalogs' Key Files lists afterwards, or nothing is written. Tier counts were re-counted for this pass and
match the document (unit 468/471, component 149/151, integration 149/156, 766 in all), so none changes.
"""
import datetime
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from apply_support import ApplySession
from c1_support import ENTRY, measured

ROOT = sys.argv[1]
DOC = "context_compass/system_docs/tests_components.md"
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
s = ApplySession(ROOT)

UNIT_NEW = "tests/unit/melder/aether/test_configuration_read_accessors.py"
INTEGRATION_NEW = "tests/integration/melder/aether/test_aether_frame_lookups.py"

s.replace(DOC, "- Updated: 2026-09-30\n", "- Updated: 2026-10-01\n")

# Aether/Nexus/Rift unit cluster: the configuration read accessors.
s.insert_after(
    DOC,
    "- the Aether reload lane carrying the spell-id regime (0.2.8213): a recorded per-frame regime reloads frozen,\n"
    "  an absent one keeps the default and is reported missing\n",
    "- the configuration read accessors (0.2.8208): `SpellbookConfiguration.aether_frame` (\"default\" when omitted,\n"
    "  a named frame round-trips) and `frozen` (False until `freeze()` or `finalize()`), the posture's `frozen`\n"
    "  (its builders refuse once it reads True), reads that change nothing, and the cleaned refusal\n",
)
s.insert_after(
    DOC,
    "- `tests/unit/melder/aether/test_root_configuration_value_snapshots.py` (root configuration snapshots, 2026-09-30)\n",
    f"- `{UNIT_NEW}` (configuration read accessors, 2026-09-29)\n",
)

# Aether integration cluster: the frame lookups and the frame/conduit reads.
s.replace(
    DOC,
    "  (0.2.79 regression for named lessers looking absent from Aether)\n"
    "Key Files (C1):\n",
    "  (0.2.79 regression for named lessers looking absent from Aether)\n"
    "- Aether's frame lookups (0.2.8208): on a fresh world no lookup creates a frame or installs or freezes the\n"
    "  configuration; a Spellbook's frame is found as the same object; the listing follows creation order and is a\n"
    "  snapshot; a cleaned frame is absent everywhere; the not-found message and its ERROR log line; non-string and\n"
    "  cleaned-Aether refusals; listing and lookups while other threads create and clean frames; the frame's shared\n"
    "  configuration (None without sharing, the bound object with it, the one the next Book adopts) and\n"
    "  `Conduit.spellbook` for roots, lessers, a torn-down root and an upgraded lesser\n"
    "Key Files (C1):\n",
)
s.replace(
    DOC,
    "- `tests/integration/melder/aether/test_aether_named_lesser_lookup.py`\n"
    "\n### Subcomponent: Crystallizer Integration Cluster\n",
    "- `tests/integration/melder/aether/test_aether_named_lesser_lookup.py`\n"
    f"- `{INTEGRATION_NEW}` (frame lookups and read accessors, 2026-09-29)\n"
    "\n### Subcomponent: Crystallizer Integration Cluster\n",
)


def find_entry(path: str) -> str:
    """Return the one code-map entry block for `path` (with its note, when present)."""
    matches = [m.group(0) for m in re.finditer(ENTRY.format(re.escape(path)), s._load(DOC))]
    if len(matches) != 1:
        raise AssertionError(f"code map entry for {path}: {len(matches)} matches")
    return matches[0]


s.insert_after(DOC, find_entry("tests/unit/melder/aether/test_root_configuration_value_snapshots.py"),
               measured(ROOT, UNIT_NEW, NOW, None))
s.insert_after(DOC, find_entry("tests/integration/melder/aether/test_aether_named_lesser_lookup.py"),
               measured(ROOT, INTEGRATION_NEW, NOW, None))

# Information Sources.
s.replace(
    DOC,
    "- `tests/integration/melder/aether/test_aether_named_lesser_lookup.py`\n"
    "- direct filesystem inventory of `tests/`\n",
    "- `tests/integration/melder/aether/test_aether_named_lesser_lookup.py`\n"
    f"- `{INTEGRATION_NEW}`\n"
    f"- `{UNIT_NEW}`\n"
    "- direct filesystem inventory of `tests/`\n",
)

text = s._load(DOC)
code_map = text[text.index("\n## C1 Code Map (Core)\n"):text.index("\n## Diagrams\n")]
catalog = text[:text.index("\n## C1 Code Map (Core)\n")]
key_files = set()
for block in re.findall(r"Key Files \(C1\):\n((?:- .*\n|  .*\n)+)", catalog):
    key_files.update(re.findall(r"^- `([^`]+)`", block, re.M))
listed = set(re.findall(r"^- path: `([^`]+)`", code_map, re.M))
if key_files != listed:
    raise SystemExit(f"core set differs from the key-file union: missing {sorted(key_files - listed)}, "
                     f"extra {sorted(listed - key_files)}")
total = len(key_files)
count_line = re.search(r"above - (\d+) paths - and nothing else\.", text)
s.replace(DOC, count_line.group(0), f"above - {total} paths - and nothing else.")

s.replace(
    DOC,
    "## Context / Handoff Summary\n\n2026-09-30 injected dependencies (0.2.8215):",
    "## Context / Handoff Summary\n\n"
    "2026-10-01 frame lookups and read accessors (0.2.8208, documented now): the two files that landed with them\n"
    "join their clusters - the noncreating frame lookups with the frame and conduit reads (integration) and the\n"
    f"configuration read accessors (unit) - and the C1 core set ({total} paths). Tier counts re-counted, unchanged.\n"
    "\n"
    "2026-09-30 injected dependencies (0.2.8215):",
)

long_lines = s.long_added_lines()
if long_lines:
    raise SystemExit("long added lines:\n" + "\n".join(long_lines))
for written in s.write():
    print("wrote", written, "core set", total, NOW)
