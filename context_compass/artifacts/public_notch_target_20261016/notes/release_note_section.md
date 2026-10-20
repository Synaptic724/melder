## `notch_spell` takes the version's id, and refuses a version that is not the index's

`Conduit.notch_spell` makes one version of a spell index the active one - the notch in stage -> notch -> meld. Until
0.2.8249 it took only the version's `Spell`, and no public call returns the `Spell` of a staged version:
`bind_inactive` returns an id, and `get_spell_by_id` / `find_spell_by_id` answer a staged (parked) id with the
index's active version, so a notch to what they return changed nothing. From 0.2.8249 `notch_spell` takes the id
`bind` or `bind_inactive` returned:

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
```

- Name the version by `spell_id=` or by `spell=`, exactly one: both or neither raise `ValueError`, and a `spell_id`
  that is not a string, or a string passed as `spell`, raises `TypeError`.
- The id is resolved inside the call to the exact version the conduit's Spellbook owns, active or parked.
- The version is checked before the notch starts and again inside its transaction: it must be a version the
  conduit's Spellbook owns and a member of `spell_index`. Otherwise a `ValueError` names the version and the remedy -
  "notch_spell: version '<id>' is not owned by this conduit's Spellbook. Notch it through the conduit of the
  Spellbook that owns it, or stage the class on this index with bind_inactive(spell_index=...), which returns the id
  to pass." or "notch_spell: version '<id>' belongs to another SpellIndex, not the one passed. Pass that version's
  own index - conduit.get_spell_by_id('<id>').spell_index - or move the version onto this index with
  add_to_spell_index first." A refused notch changes nothing.
- Until 0.2.8249 nothing checked the version, and three wrong targets damaged the Spellbook. A version staged on
  another index of the same Spellbook was accepted and corrupted both indexes: a meld of this index's old version
  raised `KeyError`, and a meld of the moved version `RuntimeError` ("Cannot build CreationContext before
  spell_codegen_creation exists."). Another index's active version, or another Spellbook's version, raised
  `RuntimeError` ("Owned spell_id not parked for reactivation") after this index's active version had already been
  parked, so the index had no active version until a notch back. Each now raises the `ValueError` above and leaves
  both indexes as they were.
- A notch to the `Spell` that `get_spell_by_id` or `find_spell_by_id` returns for a parked id is still a no-op: it
  is the active version. Name a parked version by its id.
- `notch_spell` returns the now-active `Spell`, as before.

What stays the same: `spell=` with a version the Spellbook owns (now checked the same way), a notch to the active
version (it changes nothing), the answers of `get_spell_by_id` and `find_spell_by_id`, borrowers following a notch,
and the signatures of `add_to_spell_index` and `remove_from_spell_index`.

