"""Apply melder_1's 0.2.8267 edits to src_components.md (STORY-2026-10-24-remove_many_child_holder_ownership).

Usage: python apply_src_components_20261024.py <path to src_components.md> <verified_at timestamp>
Every edit is anchored on text and asserts a single match; the file is written only if it is unchanged since read.
"""
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
stamp = sys.argv[2]
raw = path.read_bytes()
doc = raw.decode("utf-8")
assert "\r\n" not in doc
report = []


def exact(old, new, count=1):
    global doc
    assert doc.count(old) == count, (doc.count(old), old[:90])
    doc = doc.replace(old, new)
    report.append(new)


def span(start, end, new, must):
    global doc
    assert doc.count(start) == 1, ("start", doc.count(start), start[:90])
    i = doc.index(start)
    j = doc.index(end, i) + len(end)
    old = doc[i:j]
    for word in must:
        assert word in old, ("missing", word, old[:200])
    doc = doc[:i] + new + doc[j:]
    report.append(new)


# C1 Creations and SpellSpace: the many registration trim's emitted line.
exact(
    "`many_store.register_many(sidN, vN, dmN)` in the site plan (`c{i}.register_many(...)` for a shared site's child\n"
    "since 0.2.8235; see Component: SpellCompiler and Validation Pipeline, \"Holder-owned many children\"),\n",
    "`many_store.register_many(sidN, vN, dmN)` in the site plan, a shared site's child included (0.2.8267; it went\n"
    "through `c{i}` from 0.2.8235 to 0.2.8265; see Component: SpellCompiler and Validation Pipeline, \"Child registration\"),\n",
)

# C2 Live-creation probe scope.
exact(
    "store, missing what the space held and counting what the conduit held. Since 0.2.8235 a `many` built as a\n"
    "shared site's child is stored with that site (the holder's owner), so the probe counts it there - the root\n"
    "for a `unique` holder, the conduit for a per-conduit holder melded in its space, the lineage root, the\n"
    "cluster's team store - and not at the lesser or space that melded the holder first. Since 0.2.8238 such a\n"
    "child is recorded with its holder (`HolderDisposalEntry`), so a `many` probe of the child's spell counts only\n"
    "children no holder adopted.\n",
    "store, missing what the space held and counting what the conduit held. A `many` built as a shared site's child is\n"
    "stored in the innermost scope like any `many` (0.2.8267), so the probe of the child's spell counts it in the lesser\n"
    "or space that melded the holder first, every child that scope recorded; from 0.2.8235 to 0.2.8265 it was stored\n"
    "with the holder's owner and, from 0.2.8238, recorded with the holder and left out of the count.\n",
)

# C3 Meld Resolution Runtime: store selection.
exact(
    "  scope's (the space's through a SpellSpace door, else the conduit's) when it is the root or a `many` root's\n"
    "  child, and its holder's store when a shared site needs it (0.2.8235: a slotted holder's `many` children belong\n"
    "  to the holder's owner; 0.2.8238: recorded with the holder); a `many` without disposal methods is not stored.\n",
    "  scope's (the space's through a SpellSpace door, else the conduit's) wherever it is built - the root, a `many`\n"
    "  root's child or a shared site's child (0.2.8267; from 0.2.8235 to 0.2.8265 a slotted holder's children went to\n"
    "  the holder's store and, from 0.2.8238, into its holder record); a `many` without disposal methods is not stored.\n",
)

# C4 SpellCompiler: the emission bullet.
exact(
    "  a stored instance keeps today's \"already exists\" refusal (P2). Disposal-bearing many sites at the top level\n"
    "  register in the innermost scope store through `many_store.register_many(sidN, vN, dmN)` (0.2.8216; the\n"
    "  positional hot verb of Creations and SpellSpace); one placed inside `_miss{i}` registers in `c{i}` (0.2.8235,\n"
    "  next bullet). Every registration passes the Spell's live `disposal_method_names` list.\n",
    "  a stored instance keeps today's \"already exists\" refusal (P2). Disposal-bearing many sites register in the\n"
    "  innermost scope store through `many_store.register_many(sidN, vN, dmN)` (0.2.8216; the positional hot verb of\n"
    "  Creations and SpellSpace), at the top level and inside `_miss{i}` alike (0.2.8267, next bullet). Every\n"
    "  registration passes the Spell's live `disposal_method_names` list.\n",
)

# C5 SpellCompiler: one Child registration bullet replaces Holder records and Holder-owned many children.
span(
    "- Holder records (2026-10-14, 0.2.8238): right after a miss publishes holder i, under its build lock, it emits\n",
    "generalized_hydrator.py:_install_specializing_door`.\n",
    "- Child registration (2026-10-24, 0.2.8267; STORY-2026-10-24-remove_many_child_holder_ownership, on the owner's\n"
    "  decision: \"it should behave like autofac not mysteriously cleanup transient objects\"): a disposal-bearing many step\n"
    "  registers through `many_store`, the meld's innermost scope, wherever it is placed. `SitePlanEmission._emit_context`\n"
    "  returns whether a step it emitted registers there, and the function it emits into selects the store first\n"
    "  (`_many_store_prologue`: the plan at its top; a shared site's `_miss{i}` after its unresolved-input check, before\n"
    "  its children); a leasing managed miss appends its children to `kids{i}` instead and never reads `many_store`. So a\n"
    "  `many` belongs to the scope that built it: nothing records it with the holder it was passed to, a holder's purge or\n"
    "  store end runs only the holder's own disposal methods, and the scope that built a child - a lesser's pool return, a\n"
    "  spellspace exit, a borrowing root's or a cluster member's teardown - disposes it when it ends, even while the\n"
    "  holder lives on; a losing thread's children in a cold race stay in its own innermost scope like any `many`.\n"
    "  Children are still built before the site's guard and `register_many` is the same leaf call, so lock order and\n"
    "  construction order are unchanged and every `_site_plan_executor` body (the warm path) is byte-identical; plans are\n"
    "  emitted at hydration from manifest rows, so no cache generation moves. Removed: from 0.2.8235 to 0.2.8265 a miss\n"
    "  passed `c{i}` - the store the site is published to - to `_emit_many`, so a slotted holder's children were recorded\n"
    "  with whatever owned the holder, and from 0.2.8238 it emitted `c{i}.adopt_children(sid{i}, v{i}, ((sidK, vK),\n"
    "  ...))` after publishing the holder, moving them into the holder's `HolderDisposalEntry`. Kept: the opt-in singleton\n"
    "  specializer, whose straight-line body builds every non-captured step on every warm call, declines a graph in which\n"
    "  a `many` row feeds a non-`many` row (`rows_feed_many_into_non_many_step`, checked in `_install_specializing_door`\n"
    "  after the zero-capture check) and keeps the plain door - a holder's `many` is needed only in the holder's first\n"
    "  build; other graphs specialize as before.\n"
    "  EVIDENCE: `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:SitePlanEmission._emit_context`,\n"
    "  `SitePlanEmission._emit_many`, `SitePlanEmission._emit_miss`, `SitePlanEmission._many_store_prologue`,\n"
    "  `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:rows_feed_many_into_non_many_step`\n"
    "  and `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:_install_specializing_door`.\n",
    ["adopt_children", "- Holder-owned many children (2026-10-14, 0.2.8235)", "byte-identical"],
)

# C6 Registration Refusal: the internal-bind count.
exact(
    "  630-entry manifest (0.2.8257) start refusing binds mid-suite with no signal. Preserve\n",
    "  629-entry manifest (0.2.8267) start refusing binds mid-suite with no signal. Preserve\n",
)
exact(
    "  `MANIFEST_ENTRY_COUNT` (630 at 0.2.8257; 619 at 0.2.8215).\n",
    "  `MANIFEST_ENTRY_COUNT` (629 at 0.2.8267, `HolderDisposalEntry` left; 630 at 0.2.8257; 619 at 0.2.8215).\n",
)

# C7 Ownership Transfer.
span(
    "- `move_creations=True`: `_move_creations` extracts every index member's entries from the source root's store and\n",
    "  entries stay. Lineage instances are skipped either way. Nothing is disposed.\n",
    "- `move_creations=True`: `_move_creations` extracts every index member's entries from the source root's store and\n"
    "  restores them into the target's - a `unique` stays one object, and a holder's row carries the holder alone, its\n"
    "  `many` objects staying in the store that recorded them (0.2.8267) - replacing, undisposed, whatever the target held\n"
    "  under that id. `False`: `_teardown_creations` takes the active member's entries out of the source store and keeps\n"
    "  them only for the transfer's rollback; parked members' entries stay. Lineage instances are skipped either way.\n"
    "  Nothing is disposed.\n",
    ["adopted `many` children"],
)

# C8 Creations Disposal Pipeline.
span(
    "- Holder records (0.2.8238): `Creations.adopt_children` moves a just-published slotted holder's disposal-bearing\n",
    "  extract/restore rows carry the children.\n",
    "- A slotted holder is an ordinary unique entry (0.2.8267): its disposal and its purge run only its own methods; the\n"
    "  `many` objects built for it stay in their spells' buckets in the store that recorded them - the meld's innermost\n"
    "  scope - and are disposed when that store ends, and a `many` purge or probe of their spell counts them. From\n"
    "  0.2.8238 to 0.2.8265 `Creations.adopt_children` moved them into the holder's `HolderDisposalEntry`, disposed them\n"
    "  with the holder and carried them in its extract/restore row.\n",
    ["_dispose_holder_entry"],
)
exact(
    "  list (0.2.8216); unique keys keep their `(object, methods)` tuple.\n"
    "- `HolderDisposalEntry` per slotted holder that adopted children (0.2.8238), in place of its tuple.\n",
    "  list (0.2.8216); unique keys keep their `(object, methods)` tuple, a slotted holder's included (the\n"
    "  `HolderDisposalEntry` of 0.2.8238-0.2.8265 is removed).\n",
)

# C9 Flow: Transfer Spell Ownership.
exact(
    "     since 0.2.8239; holder rows carry their adopted children) or takes the active member's out (`False`);\n"
    "     disposes nothing; adjusts contracts/clusters.\n",
    "     since 0.2.8239; a holder's row carries the holder alone since 0.2.8267) or takes the active member's out\n"
    "     (`False`); disposes nothing; adjusts contracts/clusters.\n",
)

# C10 C1 code map extents.
for name, old_end, new_end, old_stamp in (
        ("src/melder/aether/conduit/conduit.py", 7907, 7909, "2026-10-19T13:16:16Z"),
        ("src/melder/aether/conduit/creations/creations.py", 1880, 1680, "2026-10-18T01:43:29Z"),
        ("src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py", 2223, 2225, "2026-10-17T23:12:45Z"),
        ("src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py", 650, 651, "2026-10-15T21:40:35Z"),
        ("src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py",
         2121, 2105, "2026-10-16T11:09:31Z"),
):
    exact(
        f"- path: `{name}`\n  start_line: 1\n  end_line: {old_end}\n  loc: {old_end}\n  verified_at: {old_stamp}\n",
        f"- path: `{name}`\n  start_line: 1\n  end_line: {new_end}\n  loc: {new_end}\n  verified_at: {stamp}\n",
    )

# C11 Numeric citations into conduit.py past transfer_spell_ownership (def at 4273) moved two lines.
shifted = []


def _shift(match):
    numbers = re.sub(r"\d+", lambda n: str(int(n.group(0)) + 2) if int(n.group(0)) >= 4273 else n.group(0), match.group(2))
    shifted.append((match.group(2), numbers))
    return match.group(1) + numbers


doc = re.sub(r"(src/melder/aether/conduit/conduit\.py:)(\d+(?:(?:, | ?- ?)\d+)*)", _shift, doc)
assert len(shifted) == 7, shifted

# C12 creations.py citations (stale before this lane) point at the methods they describe.
exact(
    "  EVIDENCE: src/melder/aether/conduit/creations/creations.py:376-468.\n",
    "  EVIDENCE: src/melder/aether/conduit/creations/creations.py:420-514.\n",
)
exact(
    "  - src/melder/aether/conduit/creations/creations.py:119-134\n"
    "  - src/melder/aether/conduit/creations/creations.py:277-293\n"
    "  - src/melder/aether/conduit/creations/creations.py:295-374\n",
    "  - src/melder/aether/conduit/creations/creations.py:264-337\n"
    "  - src/melder/aether/conduit/creations/creations.py:339-387\n"
    "  - src/melder/aether/conduit/creations/creations.py:390-418\n",
)

# C13 Handoff summary entry.
HANDOFF = (
    "2026-10-24 a `many` belongs to the scope that built it (0.2.8267;\n"
    "STORY-2026-10-24-remove_many_child_holder_ownership): Creations and SpellSpace (the emitted-line note of the many\n"
    "registration trim, the live-creation probe paragraph), Meld Resolution Runtime (the store selection), SpellCompiler\n"
    "and Validation Pipeline (the emission bullet, and one Child registration bullet in place of Holder records and\n"
    "Holder-owned many children), Ownership Transfer, the Creations Disposal Pipeline (a slotted holder is an ordinary\n"
    "unique entry; `HolderDisposalEntry` removed), the transfer flow and the internal-bind count (629) say a `many`\n"
    "belongs to the scope that built it and a holder's cleanup runs only its own disposal. The code map remeasures\n"
    "conduit.py, creations.py, transfer_of_ownership.py, site_plan_lowering.py and the bind-guard manifest. Numeric\n"
    "citations into conduit.py past `transfer_spell_ownership` moved two lines and were remapped; the creations.py\n"
    "citations of the disposal order and of failure aggregation, stale before this lane, point at\n"
    "`_dispose_many_creations` and `_dispose_disposable_registry`, and at `cleanup`, `_attempt_cleanup` and\n"
    "`_describe_for_disposal_error` again.\n\n"
)
exact("## Context / Handoff Summary\n\n2026-10-24 cache saves are best-effort", "## Context / Handoff Summary\n\n" + HANDOFF + "2026-10-24 cache saves are best-effort")

for block in report + [HANDOFF]:
    for line in block.split("\n"):
        if len(line) > 120 and "EVIDENCE" not in line and not line.lstrip().startswith(("`src/", "and `src/")):
            print("LONG", len(line), line[:100])
print("conduit.py citations shifted:", shifted)
assert path.read_bytes() == raw, "src_components.md changed while the edits were prepared"
path.write_bytes(doc.encode("utf-8"))
print("wrote", path, len(doc.split("\n")) - 1, "lines")
