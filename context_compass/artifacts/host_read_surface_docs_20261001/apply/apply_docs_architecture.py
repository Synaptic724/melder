"""
Promote the 0.2.8208 host read surface into src_architecture.md and remap the stale citations this pass owns.

Usage: python apply_docs_architecture.py <repository root>
Every anchor must match exactly once; nothing is written unless all do.
"""
import datetime
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from apply_support import ApplySession
from c1_support import measured, remeasure

ROOT = sys.argv[1]
DOC = "context_compass/system_docs/src_architecture.md"
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
s = ApplySession(ROOT)

s.replace(DOC, "- Updated: 2026-09-30\n", "- Updated: 2026-10-01\n")

# System Boundary and External Interfaces: the new public reads.
s.insert_after(
    DOC,
    "  ...), and `ConduitCloud.list_conduits()` lists one frame's named scopes (0.2.79).\n",
    "- `Aether.find_frame(name)`, `Aether.get_frame(name)` and `Aether.list_frame_names()` (0.2.8208) find frames\n"
    "  without creating one: the live frame or None, the live frame or ValueError, and the live names in the order\n"
    "  they were created. Five reads let a host compare configuration facts without private access:\n"
    "  `AethericFrame.shared_spellbook_configuration`, `AethericFrameConfiguration.frozen`,\n"
    "  `SpellbookConfiguration.frozen`, `SpellbookConfiguration.aether_frame` and `Conduit.spellbook`.\n",
)

# Operational Invariants: the lookup contract, placed by date before the 2026-09-28 entries.
s.insert_before(
    DOC,
    "- Shared document-view initialization (2026-09-28): a non-None section tuple signals a complete index,\n",
    "- Frame lookups never create a frame (2026-09-29, 0.2.8208). `find_frame`, `get_frame` and `list_frame_names`\n"
    "  read the frame registry and nothing else: an absent frame - \"default\" included - is None (ValueError from\n"
    "  `get_frame`), no plane claim is taken, and the Aether configuration is neither installed nor frozen. Every\n"
    "  other frame-scoped call (the conduit lookups, `get_conduit_cloud`) resolves \"default\" through the lazy\n"
    "  creation path, so on a world with no frames it creates \"default\", seals the spell-id regime and freezes the\n"
    "  Aether configuration. Only `_ensure_frame` and `_create_frame` create frames. A lookup takes no Aether lock -\n"
    "  one `dict.get`, or one `dict.copy()` for the listing - which keeps it off the Aether -> Nexus lock order that\n"
    "  detaching a cleaned frame takes; a frame that reads `cleaned` but is not yet detached counts as absent; the\n"
    "  reference is borrowed with no lease, so its owner may clean it at any time and a later frame may reuse the\n"
    "  name (compare with `is`). The five accessors read state that already exists: the two `frozen` flags under\n"
    "  their object's lock, `shared_spellbook_configuration` only while the posture shares the rich configuration\n"
    "  (None before a Book binds one), `aether_frame` as fixed at construction and `Conduit.spellbook` borrowed.\n"
    "  None adds a lock, a lock-order edge or meld-path work.\n"
    "  EVIDENCE: `src/melder/aether/aether.py:Aether.find_frame`, `Aether.get_frame`, `Aether.list_frame_names`,\n"
    "  `Aether._find_registered_frame`, `Aether.get_conduit_cloud`, `Aether._collapse_configuration_on_first_frame`,\n"
    "  `Aether._detach_cleaned_frame` and\n"
    "  `src/melder/aether/aetheric_frame/aetheric_frame.py:AethericFrame.shared_spellbook_configuration`.\n",
)

# Failure Modes and Error Paths.
s.insert_after(
    DOC,
    "  EVIDENCE: `src/melder/aether/aether.py:Aether._resolve_lookup_frame` and `Aether.get_conduit_by_name`.\n",
    "- `Aether.get_frame(name)` raises ValueError when no live frame has the name; the message starts \"Aetheric frame\n"
    "  '<name>' does not exist.\" and says that constructing a Spellbook for that frame creates it and that\n"
    "  `find_frame` tests for it without raising. `find_frame` and `get_frame` raise TypeError naming the call for a\n"
    "  non-string name, and every lookup and accessor raises RuntimeError once its object is cleaned (0.2.8208).\n"
    "  EVIDENCE: `src/melder/aether/aether.py:Aether.get_frame` and `Aether._find_registered_frame`.\n",
)

# Diagrams: Frame Lookups, placed beside Conduit Lookup Coverage.
s.insert_before(
    DOC,
    "### Scope Exit and Pool Return\n",
    "### Frame Lookups\n"
    "```text\n"
    "find_frame(name) | get_frame(name) -> _find_registered_frame -> registry dict.get\n"
    "    live frame -> borrowed frame | absent or cleaned -> None (get_frame: ValueError)\n"
    "list_frame_names() -> registry dict.copy() -> live names, creation order\n"
    "(no lock, no plane claim, no frame created, no regime sealed)\n"
    "Spellbook(...), conduit lookups, get_conduit_cloud -> _ensure_frame -> creates \"default\" when absent\n"
    "```\n"
    "\n"
    "```mermaid\n"
    "flowchart LR\n"
    "  H[Host] -->|find_frame / get_frame| G[Registry: one dict.get]\n"
    "  H -->|list_frame_names| L[Registry copy: live names in creation order]\n"
    "  G --> Q{Live frame?}\n"
    "  Q -->|yes| B[Borrowed frame, no lease]\n"
    "  Q -->|no| N[None, or ValueError from get_frame]\n"
    "  O[Spellbook, conduit lookups, get_conduit_cloud] --> E[_ensure_frame: creates when absent]\n"
    "  E -.->|first frame only| S[Seals the regime, freezes the Aether configuration]\n"
    "```\n"
    "\n",
)

# Citations the 0.2.8208 insertions moved (conduit.py +29 from 1910, aetheric_frame.py +35 from 591).
for old, new in (
    ("  - src/melder/aether/conduit/conduit.py:5280, 5352 (`notch_spell`; starts the transaction)\n",
     "  - src/melder/aether/conduit/conduit.py:5309, 5381 (`notch_spell`; starts the transaction)\n"),
    ("  - src/melder/aether/conduit/conduit.py:5370, 5425 (`add_to_spell_index`; starts it)\n",
     "  - src/melder/aether/conduit/conduit.py:5399, 5454 (`add_to_spell_index`; starts it)\n"),
    ("  - src/melder/aether/conduit/conduit.py:5448, 5496 (`remove_from_spell_index`; starts it)\n",
     "  - src/melder/aether/conduit/conduit.py:5477, 5525 (`remove_from_spell_index`; starts it)\n"),
    ("  - src/melder/aether/conduit/conduit.py:5229-5231 (the check and the raise -\n",
     "  - src/melder/aether/conduit/conduit.py:5258-5260 (the check and the raise -\n"),
    ("  - src/melder/aether/aetheric_frame/aetheric_frame.py:691-752\n",
     "  - src/melder/aether/aetheric_frame/aetheric_frame.py:726-787\n"),
    ("     EVIDENCE: src/melder/aether/aether.py:174-250\n",
     "     EVIDENCE: src/melder/aether/aether.py:175-251\n"),
):
    s.replace(DOC, old, new)

# The Aether singleton invariant: stale citations, and teardown is not identity-checked (cleanup's finally, BUG-149).
s.replace(
    DOC,
    "  free-threaded interpreter yields one object rather than a race. Teardown is\n"
    "  the mirror image and is IDENTITY-CHECKED, not unconditional: the singleton\n"
    "  bookkeeping is only cleared when `Aether._instance is self`, so cleaning a\n"
    "  stale instance cannot unseat the live one. Construction failure rolls the\n"
    "  bookkeeping back for the same reason. The explicit reset exists so a test can\n"
    "  get a fresh world; it is the only supported way to do so.\n"
    "  EVIDENCE:\n"
    "  - src/melder/aether/aether.py:100 (`_instance` class slot)\n"
    "  - src/melder/aether/aether.py:114-118 (double-checked construction)\n"
    "  - src/melder/aether/aether.py:201 (identity-checked teardown)\n",
    "  free-threaded interpreter yields one object rather than a race. Construction\n"
    "  failure rolls the bookkeeping back under the class lock, IDENTITY-CHECKED: the\n"
    "  slot is cleared only when `Aether._instance is self`. Teardown is not:\n"
    "  `cleanup()` resets `_instance` and `_initialized` in a `finally` whatever its\n"
    "  children raised (BUG-149), so a failed teardown never leaves the cleaned\n"
    "  instance published. A stale instance cannot unseat a live successor because\n"
    "  its `cleanup()` returns at the `_cleaned` check before that reset (corrected\n"
    "  2026-10-01: this said teardown was identity-checked). The explicit reset\n"
    "  exists so a test can get a fresh world; it is the only supported way to do so.\n"
    "  EVIDENCE:\n"
    "  - src/melder/aether/aether.py:116 (`_instance` class slot)\n"
    "  - src/melder/aether/aether.py:130-134 (double-checked construction)\n"
    "  - src/melder/aether/aether.py:245-251 (identity-checked rollback when construction fails)\n"
    "  - src/melder/aether/aether.py:278-282, 323-332 (cleanup's `_cleaned` return; the unconditional reset)\n",
)

# C1 Code Map: the five files this pass describes, remeasured; the posture module joins the map.
remeasure(s, DOC, ROOT, "src/melder/aether/aether.py", NOW,
          "  note: global singleton, frame registry and the noncreating frame lookups (0.2.8208).\n")
remeasure(s, DOC, ROOT, "src/melder/aether/aetheric_frame/aetheric_frame.py", NOW)
remeasure(s, DOC, ROOT, "src/melder/aether/conduit/conduit.py", NOW)
remeasure(s, DOC, ROOT, "src/melder/aether/spellbook/configuration/spellbook_configuration.py", NOW)
s.insert_after(
    DOC,
    "  note: automatic vs dynamic.\n",
    measured(ROOT, "src/melder/aether/aetheric_frame/aetheric_frame_configuration.py", NOW,
             "  note: narrow frame posture (system state, AR flags, sharing); `frozen` marks a settled world.\n"),
)

# Information Sources.
s.insert_after(
    DOC,
    "- `src/melder/aether/aetheric_frame/aetheric_frame.py`\n",
    "- `src/melder/aether/aetheric_frame/aetheric_frame_configuration.py`\n",
)

# Context / Handoff Summary.
s.replace(
    DOC,
    "## Context / Handoff Summary\n\n2026-09-30 injected dependencies (0.2.8215):",
    "## Context / Handoff Summary\n\n"
    "2026-10-01 frame lookups and read accessors (0.2.8208, documented now): the boundary list, the operational\n"
    "invariants, the failure modes, a Frame Lookups diagram and the code map carry `Aether.find_frame` /\n"
    "`get_frame` / `list_frame_names`, which never create a frame, and the five read accessors; the component map\n"
    "carries the per-component contracts. The thirteen line citations the 0.2.8208 insertions moved, and every\n"
    "stale citation into aether.py (three of them moved by the 0.2.8213 insertion), point at their code again. The\n"
    "Aether singleton invariant now says what teardown does: it resets unconditionally, and only a failed\n"
    "construction checks identity. Citations into other files were not audited in this pass.\n"
    "\n"
    "2026-09-30 injected dependencies (0.2.8215):",
)

long_lines = s.long_added_lines()
if long_lines:
    raise SystemExit("long added lines:\n" + "\n".join(long_lines))
for written in s.write():
    print("wrote", written, NOW)
