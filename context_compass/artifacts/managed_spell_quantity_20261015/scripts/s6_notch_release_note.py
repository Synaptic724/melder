"""S6: take the notch 0.2.8245 -> 0.2.8246 and extend the running release note (transfer and managed sections).

Run from the repository root: python s6_notch_release_note.py
"""
import pathlib

VERSION = pathlib.Path("src/melder/__version__.py")
NOTE = pathlib.Path("release_docs/next_version_release.md")

version = VERSION.read_text(encoding="utf-8")
assert version.count('__version__ = "0.2.8245"') == 1, "version is not 0.2.8245 - another lane landed; re-read"
VERSION.write_text(version.replace('__version__ = "0.2.8245"', '__version__ = "0.2.8246"'), encoding="utf-8")

note = NOTE.read_text(encoding="utf-8")
edits = [
    ("# Melder 0.2.8245\n", "# Melder 0.2.8246\n"),
    (
        """What stays the same: a transfer disposes nothing. With `move_creations=False` the old owner's objects for the spell's
active version are taken out of its creations,""",
        """A transfer now moves each version's owner record both ways (0.2.8246). A spell version records the root that
owns it and the creations it builds into; until 0.2.8246 a transfer moved that record for the active version only,
and a failed transfer left it pointing at the new owner:

- A version parked before the transfer kept building into the old owner's creations: after `notch_spell` to it on
  the new owner, its `unique` object was stored in the old owner's creations, and a managed version raised "has no
  pool to lease from". Every parked version that carries an owner record now names the new owner.
- A transfer that failed after it moved the record left the active version on the new owner's creations, so the old
  owner's next meld built a second `unique` object there instead of returning its own (a managed spell raised "has
  no pool to lease from"). A failed transfer now puts every owner record back, and the old owner melds as before.
- A version staged with `bind_inactive` before `conjure` carries no owner record; a transfer moves it as before.

What stays the same: a transfer disposes nothing. With `move_creations=False` the old owner's objects for the spell's
active version are taken out of its creations,""",
    ),
    (
        """in the owning root, 0.2.8244 the way objects go back (`ReleaseManagedSpell`) and 0.2.8245 leasing through a meld
(`Conduit.managed_spell_meld` included); the rules for pools in an ownership transfer come next.
""",
        """in the owning root, 0.2.8244 the way objects go back (`ReleaseManagedSpell`), 0.2.8245 leasing through a meld
(`Conduit.managed_spell_meld` included) and 0.2.8246 its pools in an ownership transfer.
""",
    ),
    (
        """  an object built fresh by own-parameter overrides gives that object to the pool when it is released.

What stays the same: the six existing members keep their values, order and rules, and no other binding's spell
id, Spell values, record or compiled plan changes; a root store without managed spells disposes exactly as before.
""",
        """  an object built fresh by own-parameter overrides gives that object to the pool when it is released.

Pools follow an ownership transfer (0.2.8246). A pool is one more record of its spell version, so
`transfer_spell_ownership` treats it as it treats the others:

- With `move_creations=True` (the default) every version's pool moves to the new owner with its idle objects, its
  count and the `many` children recorded with its objects: the new owner leases the same objects, releases reach
  the moved pool, and `ReleaseManagedSpell().describe(cls)` names the new owner as `holding_conduit_id`.
- With `move_creations=False` the new owner leases from a new, empty pool, and the old pool's idle objects are
  neither moved nor disposed. A version parked at the time also gets a new pool in the new owner, while its old pool
  stays with the old owner until that root ends, as a parked version's other objects do; once that version is
  notched in on the new owner, a release by class finds two pools of the selected version and asks for `conduit=`
  (a lease's own `release()` is unaffected).
- A transfer that fails leaves every pool where it was, and the old owner keeps leasing from it.
- A release that runs while its spell is being transferred can find no pool for that moment and raises the
  not-managed `ValueError`; release again once the transfer has returned.

What stays the same: the six existing members keep their values, order and rules, and no other binding's spell
id, Spell values, record or compiled plan changes; a root store without managed spells disposes exactly as before.
""",
    ),
    (
        "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8245.\n",
        "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8246.\n",
    ),
]
for old, new in edits:
    assert note.count(old) == 1, old[:70]
    note = note.replace(old, new)
long = [line for line in note.splitlines() if len(line) > 120]
assert not long, long
NOTE.write_text(note, encoding="utf-8")
print("notched 0.2.8246; release note extended")
