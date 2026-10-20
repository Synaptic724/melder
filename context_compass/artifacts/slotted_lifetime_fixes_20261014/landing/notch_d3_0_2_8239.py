"""D3 notch, release-note entry and user-doc wording (0.2.8238 -> 0.2.8239). Run: python <this file> <tree root>.

Owner ruling 2026-10-14 (EPIC-2026-10-14-slotted_lifetime_ownership_fixes, Decision Log "transfer default"):
`transfer_spell_ownership` defaults to `move_creations=True`; a transfer disposes nothing.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import edit_tool

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
VERSION = str(ROOT / "src/melder/__version__.py")
NOTE = str(ROOT / "release_docs/next_version_release.md")
OWNERSHIP = str(ROOT / "docs/intermediate/ownership.md")

SECTION = '''## An ownership transfer brings the spell's objects with it by default

**Breaking change:** `Conduit.transfer_spell_ownership()` now defaults to `move_creations=True`: the objects the old
owner's creations hold for the transferred spell, for every version of it, move into the new owner's creations. A
`unique` spell therefore stays one object - the new owner serves the instance the old owner's consumers already hold,
and disposes it once, when the new owner is cleaned up. Until 0.2.8238 the default was `False`, which took the old
owner's objects for the spell's active version out of its creations and neither moved nor disposed them: the new
owner built a second instance of a `unique` spell while the old owner's consumers kept the first, and nothing ever ran
the first one's disposal methods.

```python
class Tool:
    def close(self) -> None: ...


class Worker:
    def __init__(self, tool: Tool) -> None:
        self.tool = tool


book = md.Spellbook()
tool_id = book.bind(spell=Tool, existence="unique", disposal_method_names=["close"])
book.bind(spell=Worker, existence="unique_per_conduit")
owner = book.conjure(dynamic=True, name="owner")
target = md.Spellbook().conjure(dynamic=True, name="target")

worker = owner.meld("Worker")
owner.transfer_spell_ownership(spell=tool_id, target_conduit=target)
assert target.meld("Tool") is worker.tool     # 0.2.8238 built a second Tool here
owner.cleanup()                                # leaves the Tool open: the target owns it now
target.cleanup()                               # closes it, once
```

To keep the old behaviour, pass `move_creations=False`; the transfer report's `options` show the value used.

What stays the same: a transfer disposes nothing. With `move_creations=False` the old owner's objects for the spell's
active version are taken out of its creations, neither moved nor disposed, and the new owner builds its own; objects
of parked versions stay in the old owner's creations. A moved object replaces whatever the new owner's creations
already hold for the same spell - for example a `unique_per_conduit` object it melded while borrowing the spell - and
the replaced object is not disposed. `unique_per_conduit_lineage` objects stay with the lineage that resolved them,
and spellspace and cluster objects are not kept in a conduit's creations, so `move_creations` does not reach them.
Everything else a transfer does is unchanged: stewardship of every version of the spell moves, borrowers are unshared
or repointed, and owned dependencies move only with `include_dependencies=True`.

## Packaging and documentation
'''

print("version", edit_tool.apply(VERSION, [('__version__ = "0.2.8238"\n', '__version__ = "0.2.8239"\n')]))
print("note", edit_tool.apply(NOTE, [
    ("# Melder 0.2.8238\n", "# Melder 0.2.8239\n"),
    ("## Packaging and documentation\n", SECTION),
]))
print("ownership", edit_tool.apply(OWNERSHIP, [(
    """`transfer_spell_ownership(...)` moves stewardship to the target conduit and returns
a report. The saved lesson requests `move_creations=True`, inspects the report,
and resolves from the new home. Moved objects bring the `many` dependencies with
configured disposal that were built for them. Read that report when diagnosing a
transfer; sharing and moving ownership have different lifecycle consequences.
""",
    """`transfer_spell_ownership(...)` moves stewardship to the target conduit and returns
a report. By default (`move_creations=True`, since 0.2.8239) the objects the old
owner's creations hold for the spell move with it: a `unique` stays one object,
served by the new owner and disposed when the new owner is cleaned up, and moved
objects bring the `many` dependencies with configured disposal that were built
for them. With `move_creations=False` those objects leave the old owner's
creations without being moved or disposed, and the new owner builds its own. A
transfer disposes nothing. The saved lesson requests `move_creations=True`,
inspects the report, and resolves from the new home. Read that report when
diagnosing a transfer; sharing and moving ownership have different lifecycle
consequences.
""",
)]))
