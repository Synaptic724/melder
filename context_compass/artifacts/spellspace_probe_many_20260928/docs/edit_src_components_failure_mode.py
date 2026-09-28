"""Second promotion pass (2026-09-28): correct the Meld Resolution Runtime failure mode for a spellspace-request
spell on the conduit door, which contradicted the new "Live-creation probe scope" paragraph, and name the
correction in the handoff paragraph.

Usage (from context_compass/): python <this>. Idempotent: an edit already applied is skipped; otherwise its
anchor must match once. The file is LF.
"""
import pathlib

PATH = pathlib.Path("system_docs/src_components.md")
EDITS = [
    (
        "- `SpellSpaceScopeError` for `unique_per_spell_space` without an active\n"
        "  spellspace. Raised by `SpellSpaceThreadState`\n"
        "  (`src/melder/aether/conduit/spell_space/spell_space_thread_state.py:245`),\n"
        "  not by this component.\n",
        "- RuntimeError(\"<spell> must be built from a spellspace.\") when a spellspace-request spell (a\n"
        "  `unique_per_spell_space` lineage) reaches the conduit door: `ConduitMeld.meld`, `meld_existing_spell` and\n"
        "  `describe_live_creation_status` refuse it before any lookup of stored objects. CORRECTED 2026-09-28: this\n"
        "  said SpellSpaceScopeError from `SpellSpaceThreadState`, which raises only on stack corruption at a managed\n"
        "  exit (see Creations and SpellSpace, Failure Modes).\n"
        "  EVIDENCE: `src/melder/aether/conduit/meld/conduit_meld.py:ConduitMeld.meld`,\n"
        "  `ConduitMeld.meld_existing_spell` and `ConduitMeld.describe_live_creation_status`.\n",
    ),
    (
        "mode is removed and spellspace_meld.py remeasured.\n"
        "\n"
        "2026-09-27 scope exits (0.2.8203):",
        "mode is removed and spellspace_meld.py remeasured. The Meld Resolution Runtime failure mode for a\n"
        "spellspace-request spell on the conduit door is corrected: RuntimeError, not SpellSpaceScopeError.\n"
        "\n"
        "2026-09-27 scope exits (0.2.8203):",
    ),
]
text = PATH.read_bytes().decode("utf-8")
for old, new in EDITS:
    if new in text:
        print("already applied:", new.splitlines()[0][:60])
        continue
    assert text.count(old) == 1, (old[:60], text.count(old))
    text = text.replace(old, new)
    for line in new.splitlines():
        assert len(line) <= 120, line
    print("applied:", new.splitlines()[0][:60])
PATH.write_bytes(text.encode("utf-8"))
