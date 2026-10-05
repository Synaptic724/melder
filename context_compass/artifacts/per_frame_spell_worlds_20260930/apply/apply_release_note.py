"""
Add the per_frame_spell_worlds entries (A 0.2.8213, B 0.2.8214) to the running release note.

Usage: python apply_release_note.py <repository root>
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from apply_support import ApplySession

s = ApplySession(sys.argv[1])
NOTE = "release_docs/next_version_release.md"

s.replace(NOTE, "# Melder 0.2.8212\n", "# Melder 0.2.8214\n")
s.insert_before(
    NOTE,
    "## Packaging and documentation\n",
    "## A restore brings back the spell-id regime it recorded\n"
    "\n"
    "With an active Crystallizer, the Aether record now carries `process_wide_unique_spell_ids`, and a restore installs\n"
    "it before it creates any frame, so a world recorded under per-frame spell ids (`process_wide_unique_spell_ids=False`)\n"
    "comes back under per-frame ids. Before, the record held only the logger policy and every restored world ran\n"
    "process-wide spell ids: binding the same class into a second tenant frame - which the recorded world allowed - was\n"
    "refused as a spell-id collision.\n"
    "\n"
    "When the restoring process has already fixed its regime - the host configured the Aether, or a frame exists - and it\n"
    "differs from the recorded one, the restore keeps the live regime and says so in its report: a shortfall on\n"
    "`(\"aether\", \"process_wide_unique_spell_ids\")` with the reason\n"
    "`recorded_per_frame_ids_restored_under_process_wide_ids` (or `recorded_process_wide_ids_restored_under_per_frame_ids`).\n"
    "A record written before this version carries no regime: it restores process-wide as before, and the report lists\n"
    "the key as missing.\n"
    "\n"
    "The new read-only `Aether.process_wide_unique_spell_ids` says which regime is in force - the sealed value once a\n"
    "frame exists, before that the installed configuration's value, otherwise `True`:\n"
    "\n"
    "```python\n"
    "from melder import Aether\n"
    "\n"
    "Aether().process_wide_unique_spell_ids   # True until a per-frame configuration is installed\n"
    "```\n"
    "\n"
    "What stays the same: process-wide worlds record and restore exactly as before, and a restore never changes the\n"
    "regime of a live world.\n"
    "\n"
    "## Fixed: a class bound in several frames keeps every frame's binding when recorded\n"
    "\n"
    "Under per-frame spell ids one class can be bound in several frames - the multi-tenant shape - and each frame's\n"
    "binding has the same spell id. The Crystallizer kept one spell record per spell id, so recording such a world kept\n"
    "only the last frame's binding, and a restore reported `complete` while the other frames came back without the\n"
    "class. Records now keep one spell crystal per frame under per-frame ids, and a restore rebuilds each frame's\n"
    "binding, index selection, parked members and contract grants in that frame's own Spellbook.\n"
    "\n"
    "Restoring such a record into a process that already runs process-wide ids (a configured Aether or a live frame)\n"
    "now fails before anything is built - `RuntimeError: restore failed at stage 'aether_configuration'`, chained from\n"
    "an error that names both regimes and the fix - instead of quietly rebuilding one frame's copy.\n"
    "\n"
    "**Breaking change:** records are stamped record version 4.0.0 (was 3.0.0), so an older Melder refuses them with its\n"
    "upgrade message instead of folding several frames' copies into one; records written by older versions still load.\n"
    "For worlds recorded under per-frame spell ids:\n"
    "\n"
    "- spell custody is keyed `\"<spell_id>@<frame>\"` instead of the bare spell id - in `checkpoint_replay_data(...)`\n"
    "  journals and payloads, formation records and the spells `analyze_impact(...)` lists; `spell_activity` and\n"
    "  `spell_removed` payloads carry both \"spell_id\" and \"custody_key\", and `describe_profile()` counts one spell\n"
    "  crystal per frame's copy;\n"
    "- `Crystallizer.emit_spell_removed(...)` and `emit_spell_activity(...)` take `frame_name`, required while recording\n"
    "  (`ValueError` without it); Melder's own call sites pass it;\n"
    "- `Crystallizer.get_spell_crystal(spell_id, frame_name=None)` answers the named frame's copy, and without a frame\n"
    "  the copy with the lowest key.\n"
    "\n"
    "To upgrade: code that reads per-frame records by spell id should match on a payload's \"id\" (or split a key at its\n"
    "first \"@\", which `SpellCrystal.spell_id_of_custody_key(...)` does), and pass `frame_name` when it calls the two emit\n"
    "verbs directly. Process-wide worlds keep bare spell-id keys and need no change. `SpellCrystal.frame_name` and\n"
    "`SpellCrystal.custody_key` are new.\n"
    "\n",
)
s.replace(
    NOTE,
    "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8212.\n",
    "- The packaged system documents describe the recorded spell-id regime, per-frame custody keys and the restore's\n"
    "  per-Book replay, and correct two stale claims in the restore detail: spell SHAs do translate when a receiving\n"
    "  policy changes them, and the record version is no longer 2.0.0.\n"
    "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8214.\n",
)
long_lines = s.long_added_lines()
if long_lines:
    raise SystemExit("long added lines:\n" + "\n".join(long_lines))
for written in s.write():
    print("wrote", written)
