"""Rewrite the 0.2.8249 release-note section for the owner's extension and the spell_id wording.

Run from the repository root. Replaces the section from its heading to the next `## ` heading, rewords the S8
example's comment and the two packaging bullets of this lane. Each edit must match exactly once.
"""
import pathlib

NOTE = pathlib.Path("release_docs/next_version_release.md")
OLD_HEADING = "## `notch_spell` takes the version's id, and refuses a version that is not the index's\n"
NEW_SECTION = '''## `notch_spell`, `add_to_spell_index` and `remove_from_spell_index` take a `spell_id`; a notch checks its target

`Conduit.notch_spell` makes one version of a spell index the active one - the notch in stage -> notch -> meld. Until
0.2.8249 it took only the version's `Spell`, and no public call returns the `Spell` of a staged version:
`bind_inactive` returns a spell_id, and `get_spell_by_id` / `find_spell_by_id` answer a staged (parked) spell_id
with the index's active version, so a notch to what they return changed nothing. `add_to_spell_index` and
`remove_from_spell_index` had the same gap, since they move only a parked version. From 0.2.8249 all three take the
spell_id `bind` or `bind_inactive` returned:

```python
class ReportService:
    def render(self) -> str:
        return "v1"


class ReportServiceV2:
    def render(self) -> str:
        return "v2"


book = md.Spellbook()
v1 = book.bind(spell=ReportService, existence="unique")
reports = book.conjure(dynamic=True, name="reports")
index = reports.get_spell_by_id(v1).spell_index

v2 = reports.bind_inactive(spell=ReportServiceV2, spell_index=index, existence="unique")
reports.notch_spell(spell_index=index, spell_id=v2)    # v2 is the active version now
assert reports.meld(spell_id=v2).render() == "v2"

reports.notch_spell(spell_index=index, spell_id=v1)    # and back to v1
assert reports.meld(spell_id=v1).render() == "v1"

reports.remove_from_spell_index(spell_id=v2, source_index=index)   # parked v2 gets an index of its own
reports.add_to_spell_index(spell_id=v2, target_index=index)        # and comes back; its emptied index goes
assert index.spells_in_index() == {v1, v2}
```

- Name the spell by `spell_id=` or by `spell=`, exactly one, on all three: both or neither raise `ValueError`, and a
  `spell_id` that is not a string, or a string passed as `spell`, raises `TypeError`.
- A `spell_id` is resolved inside the call to the exact spell the conduit's Spellbook owns, active or parked.
- A notch checks its target before it starts and again inside its transaction: the spell must be one the conduit's
  Spellbook owns and a member of `spell_index`. Otherwise a `ValueError` names its spell_id and the remedy -
  "notch_spell: spell_id '<id>' is not owned by this conduit's Spellbook. Notch it through the conduit of the
  Spellbook that owns it, or stage the class on this index with bind_inactive(spell_index=...), which returns the
  spell_id to pass." or "notch_spell: spell_id '<id>' belongs to another SpellIndex, not the one passed. Pass its
  own index - conduit.get_spell_by_id('<id>').spell_index - or move it onto this index with add_to_spell_index
  first." A refused notch changes nothing.
- The index moves refuse a `spell_id` the conduit's Spellbook does not own before anything starts, for example
  "add_to_spell_index: spell_id '<id>' is not owned by this conduit's Spellbook. Call add_to_spell_index through the
  conduit of the Spellbook that owns it." Past that, the Spellbook refuses as before (`RuntimeError`): an active
  spell (notch away from it first), a spell it does not own, a target index it does not own, and a spell that is not
  a member of the source index or is its only member (`cleanup_spell` disposes that).
- Until 0.2.8249 nothing checked a notch's target, and three wrong targets damaged the Spellbook. A version staged on
  another index of the same Spellbook was accepted and corrupted both indexes: a meld of this index's old version
  raised `KeyError`, and a meld of the moved version `RuntimeError` ("Cannot build CreationContext before
  spell_codegen_creation exists."). Another index's active version, or another Spellbook's version, raised
  `RuntimeError` ("Owned spell_id not parked for reactivation") after this index's active version had already been
  parked, so the index had no active version until a notch back. Each now raises the `ValueError` above and leaves
  both indexes as they were.
- A notch to the `Spell` that `get_spell_by_id` or `find_spell_by_id` returns for a parked spell_id is still a
  no-op: it is the active version. Name a parked version by its spell_id.
- The docstrings of the three verbs say the conduit admits their transaction (the two index moves said the
  Spellbook did), and `remove_from_spell_index`'s no longer says that removing the active version leaves the index
  selecting a non-member: the Spellbook refuses an active version, and always did.

What stays the same: `spell=` on all three (a notch's target is now checked the same way), a notch to the active
version (it changes nothing), what the three verbs return, the answers of `get_spell_by_id` and `find_spell_by_id`,
borrowers following a notch, and what the index moves do.

'''

EDITS = [
    ("reports.notch_spell(spell_index=index, spell_id=v2)   # by id since 0.2.8249 (next section)\n",
     "reports.notch_spell(spell_index=index, spell_id=v2)   # by spell_id since 0.2.8249 (next section)\n"),
    ("- The README's swap sketch (stage a version, notch to it, meld it, notch back) names the versions by id and runs\n"
     "  as written; the expert guide on governed change (`docs/expert/governed-change.md`) shows promotion as\n"
     "  `notch_spell(spell_index=..., spell_id=...)` and says a wrong target is refused, and the expert walkthrough on\n"
     "  notch-swapping a live object (lesson 17) swaps by id.\n",
     "- The README's swap sketch (stage a version, notch to it, meld it, notch back) names the versions by their spell_id\n"
     "  and runs as written; the expert guide on governed change (`docs/expert/governed-change.md`) shows promotion as\n"
     "  `notch_spell(spell_index=..., spell_id=...)`, says a wrong target is refused and that the index moves take\n"
     "  `spell_id=` too, and the expert walkthrough on notch-swapping a live object (lesson 17) swaps by spell_id.\n"),
    ("  describe the notch target - its two forms, the checks before and inside the transaction, the refusals - and\n"
     "  the corrected index-mutation sequence: the conduit starts the transaction, and the notch claims the Spellbook\n"
     "  exclusively.",
     "  describe the notch target - its two forms, the checks before and inside the transaction, the refusals - the\n"
     "  index moves' `spell_id=`, and the corrected index-mutation sequence: the conduit starts the transaction, and\n"
     "  the notch claims the Spellbook exclusively."),
]


def main() -> None:
    """Apply the section rewrite and the three edits; refuse unless each matches exactly once."""
    text = NOTE.read_text(encoding="utf-8")
    assert "\r\n" not in text
    assert text.count(OLD_HEADING) == 1
    start = text.index(OLD_HEADING)
    end = text.index("\n## Packaging and documentation\n", start) + 1
    text = text[:start] + NEW_SECTION + text[end:]
    for old, new in EDITS:
        assert text.count(old) == 1, old[:60]
        text = text.replace(old, new, 1)
    NOTE.write_text(text, encoding="utf-8")
    print("ok")


if __name__ == "__main__":
    main()
