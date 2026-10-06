"""
Promote the 0.2.8208 host read surface into src_components.md and remap the stale citations this pass owns.

Usage: python apply_docs_components.py <repository root>
Every anchor must match exactly once; nothing is written unless all do.
"""
import datetime
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from apply_support import ApplySession
from c1_support import measured, remeasure

ROOT = sys.argv[1]
DOC = "context_compass/system_docs/src_components.md"
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
s = ApplySession(ROOT)
AFC = "src/melder/aether/aetheric_frame/aetheric_frame_configuration.py"

s.replace(DOC, "- Updated: 2026-09-30\n", "- Updated: 2026-10-01\n")

# --- Component: Aether Singleton (Global Runtime) ---
s.insert_after(
    DOC,
    "- Report the spell-id regime in force through `process_wide_unique_spell_ids` (0.2.8213).\n",
    "- Answer noncreating frame lookups (0.2.8208): `find_frame(name)` returns the live frame or None,\n"
    "  `get_frame(name)` the live frame or ValueError, `list_frame_names()` the live names in creation order.\n",
)
s.insert_after(
    DOC,
    "  restore stage 1 reads it to tell whether a recorded regime can still be installed.\n"
    "  EVIDENCE: `src/melder/aether/aether.py:Aether.process_wide_unique_spell_ids`.\n",
    "- Frame lookups never create a frame (0.2.8208): `find_frame`, `get_frame` and `list_frame_names` read the\n"
    "  registry through `_find_registered_frame` or one registry copy and never reach `_get_existing_frame` or\n"
    "  `_ensure_frame`, so an absent frame - \"default\" included - is None (ValueError from `get_frame`), no\n"
    "  `FRAME_CREATE` claim is taken and the configuration is neither installed nor frozen. They take no Aether\n"
    "  lock (one `dict.get`; the listing copies the registry once), which keeps them off the Aether -> Nexus order\n"
    "  `_detach_cleaned_frame` holds; a frame that reads `cleaned` before its detach is absent; the reference is\n"
    "  borrowed and grants no lease. Every other frame-scoped call still resolves \"default\" through\n"
    "  `_get_existing_frame`, creating it when absent.\n"
    "  EVIDENCE: `src/melder/aether/aether.py:Aether.find_frame`, `Aether.get_frame`, `Aether.list_frame_names` and\n"
    "  `Aether._find_registered_frame`.\n",
)
s.insert_after(
    DOC,
    "- TypeError for invalid input types (e.g., non-string frame names, including every conduit lookup's frame).\n",
    "- ValueError from `get_frame` when no live frame has the name (\"Aetheric frame '<name>' does not exist.\", then\n"
    "  how to create the frame or test for it with `find_frame`); TypeError naming the call when `find_frame` or\n"
    "  `get_frame` receives a non-string name (0.2.8208).\n",
)
s.replace(
    DOC,
    "- `SafeLogger`, weighted almost entirely to failures: 19 `error` sites against a\n",
    "- `SafeLogger`, weighted almost entirely to failures: 21 `error` sites (recounted 2026-10-01) against a\n",
)

# --- Subcomponent: Aether Frame Registry ---
s.replace(
    DOC,
    "- Ensure and retrieve AethericFrames and bind configuration.\n"
    "Contract/Interface:\n"
    "- `_ensure_frame`, `_bind_configuration`, `_get_configuration`.\n"
    "Data Structures:\n"
    "- `_aetheric_frames` map and `_default_frame`.\n"
    "Concurrency/Threading:\n"
    "- Aether singleton class lock for instance creation and Aether instance lock for\n"
    "  frame registry operations.\n",
    "- Ensure, look up and list AethericFrames and bind configuration.\n"
    "Contract/Interface:\n"
    "- `_ensure_frame`, `_bind_configuration`, `_get_configuration`.\n"
    "- Creation: `_ensure_frame` (get-or-create, under a `FRAME_CREATE` plane claim unless one is already open on\n"
    "  the thread) and `_create_frame` (strict create, used for Nexus-managed frames) are the only creators;\n"
    "  `_get_existing_frame`, which the frame-scoped calls use, creates \"default\" lazily and requires a custom\n"
    "  frame to exist.\n"
    "- Lookup (0.2.8208): `find_frame(name)` -> the live frame or None, `get_frame(name)` -> the live frame or\n"
    "  ValueError, `list_frame_names()` -> the live names in creation order. `_find_registered_frame` validates\n"
    "  the name (TypeError) and reads the registry without creating anything.\n"
    "Data Structures:\n"
    "- `_aetheric_frames` map and `_default_frame`.\n"
    "Concurrency/Threading:\n"
    "- Aether singleton class lock for instance creation and Aether instance lock for\n"
    "  frame registry writes (creation, detach). The lookups read without a lock: one `dict.get`, or one\n"
    "  `dict.copy()` for the listing.\n",
)

# --- Component: AethericFrame Services ---
s.insert_after(
    DOC,
    "- Provide ConduitCluster for auto-sharing roots.\n",
    "- Expose the frame-wide shared rich Spellbook configuration as `shared_spellbook_configuration` (0.2.8208): the\n"
    "  configuration the first conjuring Book bound, while the posture's `shared_framewide_spellbook_configuration`\n"
    "  is True; None when sharing is off or before a Book binds one. It is the gate a Spellbook applies before\n"
    "  adopting a shared configuration, and the object stays frame-owned (the caller must not clean it).\n",
)
s.insert_after(
    DOC,
    "- One DevopsInformationRegistry, SpellSystemStates, and DevOpsManager per\n  frame.\n",
    "- The posture (`AethericFrameConfiguration`) reports `frozen` (0.2.8208): False while mutable, True once\n"
    "  `freeze()` has succeeded - the world's settlement point, after which every `with_*` builder refuses and\n"
    "  conjure inherits the settled mode. The read takes the posture's lock, which `freeze()` holds while it sets\n"
    "  the flag, and never freezes or validates.\n"
    "  EVIDENCE: `src/melder/aether/aetheric_frame/aetheric_frame.py:AethericFrame.shared_spellbook_configuration`\n"
    "  and `src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:AethericFrameConfiguration.frozen`.\n",
)
s.replace(
    DOC,
    "`src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:1984` (two frame",
    "`src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:2008` (two frame",
)
s.replace(
    DOC,
    "  - src/melder/aether/aetheric_frame/aetheric_frame.py:759-770\n",
    "  - src/melder/aether/aetheric_frame/aetheric_frame.py:794-805\n",
)
s.replace(
    DOC,
    "- `src/melder/aether/aetheric_frame/aetheric_frame.py`\n"
    "- `src/melder/aether/aetheric_frame/conduit_cloud.py`\n"
    "- `src/melder/aether/conduit/conduit_cluster.py`\n",
    "- `src/melder/aether/aetheric_frame/aetheric_frame.py`\n"
    f"- `{AFC}`\n"
    "- `src/melder/aether/aetheric_frame/conduit_cloud.py`\n"
    "- `src/melder/aether/conduit/conduit_cluster.py`\n",
)

# --- Component: Spellbook Configuration and System State ---
s.insert_after(
    DOC,
    "- Keep rich local policy separate from frame-owned automatic/dynamic posture.\n",
    "- Report its own state read-only (0.2.8208): `aether_frame`, the frame name fixed at construction (\"default\"\n"
    "  when omitted) that a Spellbook compares when it is handed a configuration and has no shared one to adopt,\n"
    "  and `frozen`, False until `freeze()` (or `finalize()` / `build()`) succeeds.\n",
)
s.insert_after(
    DOC,
    "  reason is written down.\n",
    "- `frozen` reads under the same `RLock`, which `freeze()` holds while it sets the flag; `aether_frame` is fixed\n"
    "  at construction and read without it (0.2.8208).\n"
    "  EVIDENCE: `src/melder/aether/spellbook/configuration/spellbook_configuration.py:SpellbookConfiguration.frozen`\n"
    "  and `SpellbookConfiguration.aether_frame`.\n",
)
s.replace(
    DOC,
    "  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:277-343\n",
    "  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:329-394\n",
)

# --- Component: Conduit Runtime (Normal and Lesser) ---
s.insert_after(
    DOC,
    "EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.bind` and `Conduit.bind_inactive`.\n",
    "\n"
    "Book read (0.2.8208): `spellbook` returns the Spellbook this conduit resolves through, borrowed - the conjuring\n"
    "Book for a root (whose `conduit` returns this root), the root's Book for a lesser, and the new Book after\n"
    "`upgrade_to_normal`. It reads `_spellbook` behind `check_cleaned()`: not on the meld path, no lock.\n"
    "EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.spellbook`.\n",
)
s.insert_after(
    DOC,
    "- A lesser conduit from `create_lesser_conduit(...)`, or `enter_lesser_conduit(...)` for a `with` block.\n",
    "- The Spellbook it resolves through, borrowed, from `spellbook` (0.2.8208).\n",
)
s.replace(
    DOC,
    "  EVIDENCE: src/melder/aether/conduit/conduit.py:5229-5231.\n",
    "  EVIDENCE: src/melder/aether/conduit/conduit.py:5258-5260.\n",
)

# --- The rest of the 13 citations the 0.2.8208 insertions moved ---
for old, new in (
    ("  - src/melder/aether/conduit/conduit.py:5329, 5405, 5485 (notch/add/remove",
     "  - src/melder/aether/conduit/conduit.py:5358, 5434, 5514 (notch/add/remove"),
    ("`src/melder/aether/conduit/conduit.py:5352`, then calls `Spellbook._notch_spell(...)`",
     "`src/melder/aether/conduit/conduit.py:5381`, then calls `Spellbook._notch_spell(...)`"),
    ("`src/melder/aether/conduit/conduit.py:5425`, then calls", "`src/melder/aether/conduit/conduit.py:5454`, then calls"),
    ("`remove_from_index` at `src/melder/aether/conduit/conduit.py:5496`, then calls",
     "`remove_from_index` at `src/melder/aether/conduit/conduit.py:5525`, then calls"),
    ("  - src/melder/aether/conduit/conduit.py:5280, 5370, 5448 (public verbs)",
     "  - src/melder/aether/conduit/conduit.py:5309, 5399, 5477 (public verbs)"),
    ("(`src/melder/aether/aetheric_frame/aetheric_frame.py:867`; resident member",
     "(`src/melder/aether/aetheric_frame/aetheric_frame.py:902`; resident member"),
):
    s.replace(DOC, old, new)

# --- Stale citations into aether.py (three moved by the 0.2.8213 insertion, the rest older) ---
for old, new in (
    ("  - src/melder/aether/aether.py:762-795\n  - src/melder/aether/aether.py:1288-1333\n",
     "  - src/melder/aether/aether.py:805-838\n  - src/melder/aether/aether.py:1331-1376\n"),
    ("- src/melder/aether/aether.py:209-222\n- src/melder/aether/aether.py:1288-1333\n",
     "- src/melder/aether/aether.py:209-222\n- src/melder/aether/aether.py:1331-1376\n"),
    ("through it; see `src/melder/aether/aether.py:222` and `:1243-1264`.)",
     "through it; see `src/melder/aether/aether.py:222` and `:1225-1249`.)"),
    ("(`src/melder/aether/aether.py:893` - AETHER owns", "(`src/melder/aether/aether.py:1187` - AETHER owns"),
    ("via `_ensure_default_frame` (`src/melder/aether/aether.py:323`), which now",
     "via `_ensure_default_frame` (`src/melder/aether/aether.py:385`), which now"),
):
    s.replace(DOC, old, new)

# --- Method-Level Call Flows: the frame lookup ---
s.insert_before(
    DOC,
    "### Flow: Purge a Target's Retained Creations\n",
    "### Flow: Aether Frame Lookup\n"
    "1. `Aether.find_frame(name)` and `Aether.get_frame(name)` call `_find_registered_frame(name, method_name)`:\n"
    "   `check_cleaned()`, TypeError naming the call unless `name` is a `str`, then `self._aetheric_frames.get(name)`;\n"
    "   a missing frame, or one whose `cleaned` reads True, is None.\n"
    "2. `find_frame` returns that; `get_frame` logs and raises ValueError (\"Aetheric frame '<name>' does not exist.\n"
    "   get_frame never creates a frame: ...\") when it is None.\n"
    "3. `Aether.list_frame_names()` runs `check_cleaned()`, takes one `self._aetheric_frames.copy()` and returns the\n"
    "   names whose frame is not `cleaned`, as a tuple in registration order.\n"
    "4. None of the three reaches `_get_existing_frame`, `_ensure_frame`, `_frame_creation_transaction` or\n"
    "   `_collapse_configuration_on_first_frame`, and none takes `Aether._lock` (0.2.8208).\n"
    "\n",
)

# --- C1 Code Map (Core) ---
remeasure(s, DOC, ROOT, "src/melder/aether/aether.py", NOW)
remeasure(s, DOC, ROOT, "src/melder/aether/aetheric_frame/aetheric_frame.py", NOW)
remeasure(s, DOC, ROOT, "src/melder/aether/conduit/conduit.py", NOW)
remeasure(s, DOC, ROOT, "src/melder/aether/spellbook/configuration/spellbook_configuration.py", NOW)
s.insert_before(
    DOC,
    "- path: `src/melder/aether/aetheric_frame/conduit_cloud.py`\n",
    measured(ROOT, AFC, NOW, "  note: frame posture; `frozen` reports settlement (0.2.8208).\n"),
)

# --- Information Sources ---
s.replace(
    DOC,
    "- `src/melder/aether/aetheric_frame/aetheric_frame.py`\n"
    "- `src/melder/aether/aetheric_frame/conduit_cloud.py`\n"
    "- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py`\n",
    "- `src/melder/aether/aetheric_frame/aetheric_frame.py`\n"
    f"- `{AFC}`\n"
    "- `src/melder/aether/aetheric_frame/conduit_cloud.py`\n"
    "- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py`\n",
)

# --- Context / Handoff Summary ---
s.replace(
    DOC,
    "## Context / Handoff Summary\n\n2026-09-30 injected dependencies (0.2.8215):",
    "## Context / Handoff Summary\n\n"
    "2026-10-01 frame lookups and read accessors (0.2.8208, documented now): the Aether Singleton entry and the Aether\n"
    "Frame Registry subcomponent carry `find_frame` / `get_frame` / `list_frame_names` (noncreating, lock-free,\n"
    "borrowed); AethericFrame Services carries `shared_spellbook_configuration` and the posture's `frozen` (its\n"
    "module joins the Key Files and the code map); Spellbook Configuration carries `aether_frame` and `frozen`;\n"
    "Conduit Runtime carries `spellbook`; a new Aether Frame Lookup flow. Remapped: the ten citations here that the\n"
    "0.2.8208 insertions moved, and six stale citations into aether.py (three moved by the 0.2.8213 insertion).\n"
    "Observability's error-site count is 21. Not done here: citations into other files, and the core set, which\n"
    "has drifted from the Key Files union (12 key files without an entry, 19 entries no Key Files list names).\n"
    "\n"
    "2026-09-30 injected dependencies (0.2.8215):",
)

long_lines = s.long_added_lines()
if long_lines:
    raise SystemExit("long added lines:\n" + "\n".join(long_lines))
for written in s.write():
    print("wrote", written, NOW)
