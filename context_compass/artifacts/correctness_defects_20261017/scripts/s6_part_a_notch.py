"""S6 part A: notch 0.2.8253 -> 0.2.8254 and write its release-note entry.

Run from the repository root:  python context_compass/artifacts/correctness_defects_20261017/scripts/s6_part_a_notch.py [--dry-run]
The managed spells were added in this running note (0.2.8241-0.2.8248), so the change lands in that section, where
the note said the opposite ("Each option is part of a managed spell's id"), not in a second section on the subject
(special_instructions/agent_contribution_guide.md). The example was run as written (probes/probe_release_note_s6.py).
"""
import pathlib
import sys

DRY = "--dry-run" in sys.argv
VERSION = pathlib.Path("src/melder/__version__.py")
NOTE = pathlib.Path("release_docs/next_version_release.md")


def sub(text: str, old: str, new: str) -> str:
    """Replace `old` with `new`, refusing unless `old` occurs exactly once."""
    count = text.count(old)
    assert count == 1, (old[:80], count)
    return text.replace(old, new)


version = VERSION.read_text(encoding="utf-8")
version = sub(version, '__version__ = "0.2.8253"\n', '__version__ = "0.2.8254"\n')

note = NOTE.read_text(encoding="utf-8")
note = sub(note, "# Melder 0.2.8253\n", "# Melder 0.2.8254\n")
note = sub(
    note,
    "(`Conduit.managed_spell_meld` included) and 0.2.8246 its pools in an ownership transfer.\n",
    "(`Conduit.managed_spell_meld` included), 0.2.8246 its pools in an ownership transfer, and 0.2.8254 took its four\n"
    "settings out of its spell_id.\n",
)
note = sub(
    note,
    "- Each option is part of a managed spell's id: the same class bound with other options is a different spell\n"
    "  version (park it with `bind_inactive` and `notch_spell` to it, as with any version).\n",
    """- The four options are settings of the one spell, not part of its spell_id (0.2.8254): one class bound managed at one
  address with one list of disposal methods has one spell_id whatever its mode, limit, timeout or reset methods.
  Staging it again with other settings (`bind_inactive` on its index) is refused as the same spell - `RuntimeError`
  "Spell ID collision detected. ..." - and nothing is registered. A version that differs in more than its settings
  (another class, binding name or disposal methods) is a version of its own, as before.
- To change a managed spell's settings, dispose it and bind it again. The spell_id stays, and the pool the earlier
  binding left takes the new settings with its idle objects and its count, so an object leased before goes back to
  it. The rebind destroys nothing: every object alive stays alive and counted, even above a lower limit, and the
  pool settles to the new limit as objects are released; a lease waiting in a `queue` pool checks the new settings.

```python
sid = book.bind(spell=Parser, existence="managed_spell_quantity",
                managed_spell_mode="limited_quantity", managed_spell_limit=1)
root = book.conjure(dynamic=True, name="parsers")

parser = root.meld(spell_id=sid)
root.cleanup_spell(spell=root.get_spell_by_spell_id(sid))   # the pool stays, with the parser out
assert root.bind(spell=Parser, existence="managed_spell_quantity",
                 managed_spell_mode="limited_quantity", managed_spell_limit=2) == sid   # the same spell
second = root.meld(spell_id=sid)                  # limit 2 now: a second parser
md.ReleaseManagedSpell().release(parser)          # back to the same pool, counted
```

- Builds 0.2.8242-0.2.8253 hashed the four settings into the spell_id, so a managed spell bound by one of them has
  another spell_id from 0.2.8254 on (no other spell's id moves). A Crystallizer record made by one of them restores
  through `bind`, which gives each managed spell its new spell_id. Under process-wide spell ids (the default), one
  managed class bound at one address in two frames now has one spell_id whatever its settings, so the second binding
  is refused as a duplicate, as for any other class: at its `bind` once the first frame's Spellbook is conjured
  ("Spell ID collision detected. ..."), otherwise at its `conjure()` ("Conjure refused: ... already registered").
""",
)
note = sub(
    note,
    "- Compiled plans cached before managed spells existed are retired: the creation cache moves to generation 21\n"
    "  (0.2.8248). Every release change already makes the first `conjure()` after an upgrade compile cold, so nothing\n"
    "  else changes.\n",
    "- Compiled plans cached by earlier builds are retired: the creation cache moves to generation 21 (0.2.8248), which\n"
    "  retires the bundles written before managed spells existed, and to 22 (0.2.8254), which retires those written while\n"
    "  the settings were part of the spell_id. Every release change already makes the first `conjure()` after an upgrade\n"
    "  compile cold, so nothing else changes.\n",
)
note = sub(
    note,
    "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8253.\n",
    "- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph\n"
    "  describe a managed spell's settings as settings of the one spell: the fingerprint without them, the pool taking\n"
    "  new settings on a rebind under its spell_id, and the creation cache's generation 22; `ManagedSpellMode` and the\n"
    "  bind fingerprint's docstrings say the same, and the code-map extents of the changed files are remeasured.\n"
    "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8254.\n",
)
too_long = [line for line in note.splitlines() if len(line) > 120]
assert not too_long, too_long
if DRY:
    print("dry run: ok")
else:
    VERSION.write_text(version, encoding="utf-8")
    NOTE.write_text(note, encoding="utf-8")
    print("wrote", VERSION, "and", NOTE)
