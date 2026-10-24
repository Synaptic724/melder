"""Apply melder_1's 0.2.8267 edits to src_architecture.md (STORY-2026-10-24-remove_many_child_holder_ownership).

Usage: python apply_src_architecture_20261024.py <path to src_architecture.md> <verified_at timestamp>
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
new_lines_report = []


def exact(old, new, count=1):
    global doc
    assert doc.count(old) == count, (doc.count(old), old[:90])
    doc = doc.replace(old, new)
    new_lines_report.append(new)


def span(start, end, new, must):
    global doc
    assert doc.count(start) == 1, ("start", doc.count(start), start[:90])
    i = doc.index(start)
    j = doc.index(end, i) + len(end)
    old = doc[i:j]
    for word in must:
        assert word in old, ("missing", word, old[:200])
    doc = doc[:i] + new + doc[j:]
    new_lines_report.append(new)


# E1 Runtime Model: the moved-holder example goes; a holder with a disposed many is pending work.
span(
    "So a defect is structure that is wrong or stuck",
    "pending work for the agent, not a defect.\n",
    "So a defect is structure that is wrong or stuck: a record that names the wrong owner, so the wrong teardown disposes\n"
    "an object (a cluster's shared object recorded in its leader's store), or state an agent cannot get past (a torn-down\n"
    "root still recorded in its cluster). An object that still references something its owner has since disposed - after\n"
    "a transfer, a contract change or a teardown, or a holder whose `many` dependency the scope that built it disposed - is\n"
    "pending work for the agent, not a defect.\n",
    ["a moved holder's `many` children left in the old"],
)

# E2 Meld Resolution step 4.
exact(
    "   A slotted site's disposal-bearing `many` children are registered in that site's store, with the\n"
    "   holder's owner, not in the meld's innermost scope (0.2.8235).\n",
    "   Every disposal-bearing `many` registers in the meld's innermost scope - the spellspace store, else the\n"
    "   melding conduit's - also one built inside a slotted site's first build: a `many` belongs to the scope that\n"
    "   built it, not to the holder it is passed to (0.2.8267; 0.2.8235-0.2.8265 registered it with the holder's\n"
    "   owner).\n",
)

# E3 Transfer sequence.
span(
    "   - With `move_creations=True` (the default since 0.2.8239) moves the source store's instances of every index\n",
    "     resolved. A transfer disposes nothing.\n",
    "   - With `move_creations=True` (the default since 0.2.8239) moves the source store's instances of every index\n"
    "     member into the target's store - a holder alone: the `many` objects built for it stay in the store that\n"
    "     recorded them (0.2.8267) - and a managed version's pool with its idle objects and count; with `False` takes\n"
    "     the active member's instances (its pool among them) out of the source store, neither moved nor disposed.\n"
    "     Lineage instances stay where they were resolved. A transfer disposes nothing.\n",
    ["a holder's adopted `many` children with it (0.2.8238)"],
)

# E4 New first operational invariant.
INVARIANT = (
    "- A `many` belongs to the scope that built it (2026-10-24, 0.2.8267;\n"
    "  STORY-2026-10-24-remove_many_child_holder_ownership, on the owner's decision, chat 2026-10-24: \"lets rip it out\n"
    "  because it should behave like autofac not mysteriously cleanup transient objects\"): every disposal-bearing `many` a\n"
    "  site plan builds - a `many` root, the `many` child of a `many`, or one built inside a slotted holder's first build\n"
    "  (`_miss{i}`) - registers through `many_store`, the meld's innermost scope (the spellspace store, else the melding\n"
    "  conduit's); a function that registers one selects that store first (`_many_store_prologue`: the plan at its top, a\n"
    "  miss after its unresolved-input check), and a `many` without disposal methods is recorded nowhere. Nothing records a\n"
    "  child with the holder it was passed to: a store keeps two disposal shapes, a unique's `(object, methods)` tuple - a\n"
    "  slotted holder's included - and a `ManyDisposalBucket` per `many` key. So cleaning up a holder - a purge of it or its\n"
    "  store's end - runs only the holder's own disposal methods, and what the holder does with what it holds is its own\n"
    "  dispose rule's business (as in Autofac, where a component is disposed by the scope that resolved it and nothing\n"
    "  cascades from an object to its dependencies). The scope that built a child disposes it when that scope ends, even\n"
    "  while the holder lives on - a lesser's pool return, a spellspace exit, a borrowing root's or a cluster member's\n"
    "  teardown - and raises a failing child's disposal there; a lost cold race's children stay in the loser's innermost\n"
    "  scope like any `many`; a `many` purge or live-creation probe of the child's spell counts every child its scope\n"
    "  recorded; an ownership transfer moves a holder's entry and leaves its children where they were recorded\n"
    "  (`include_dependencies` moves the child's spell, and its bucket, too). Removed: the 0.2.8235 placement (a miss\n"
    "  registered its children in `c{i}`, the store its holder is published to) and the 0.2.8238 holder record\n"
    "  (`HolderDisposalEntry`, `Creations.adopt_children` and the adoption line a miss emitted after publishing the\n"
    "  holder). Not changed: managed pools' recorded children (a leasing miss appends them to `kids{i}` and the pool\n"
    "  adopts them with the object), the opt-in singleton specializer's decline of graphs that feed a `many` step into a\n"
    "  non-`many` step (its straight-line body would build a holder's `many` on every warm call), direct `many` melds, warm\n"
    "  `_site_plan_executor` bodies (only misses change) and the cache and record formats: plans are emitted at hydration\n"
    "  from manifest rows, and extract/restore rows are an in-memory handoff whose holder rows no longer carry a\n"
    "  `children` list. Locks: the children are built before the holder's build lock and `register_many` stays the store\n"
    "  lock's leaf call, as before; no lock or lock-order edge is added.\n"
    "  EVIDENCE: `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:SitePlanEmission._emit_context`,\n"
    "  `SitePlanEmission._emit_many`, `SitePlanEmission._emit_miss`, `SitePlanEmission._many_store_prologue` and\n"
    "  `src/melder/aether/conduit/creations/creations.py:Creations.register_many`, `Creations._dispose_disposable_registry`,\n"
    "  `Creations._dispose_entry`, `Creations.purge`, `Creations.extract_spell_creations`,\n"
    "  `Creations.restore_spell_creations`.\n"
)
exact("## Operational Invariants\n- Cache saves are best-effort", "## Operational Invariants\n" + INVARIANT + "- Cache saves are best-effort")

# E5 Transfer-default invariant.
exact(
    "  restores them into the target's - a `unique` stays one object and a holder's adopted children travel in its row -\n",
    "  restores them into the target's - a `unique` stays one object; a holder's row carries the holder alone (0.2.8267) -\n",
)

# E6 Holder records: REMOVED.
span(
    "- Holder records (2026-10-14, 0.2.8238): a slotted holder's disposal-bearing `many` children are recorded with the\n",
    "shared_assets/site_plan_lowering.py:SitePlanEmission._emit_miss`.\n",
    "- Holder records (2026-10-14, 0.2.8238; REMOVED at 0.2.8267 by the first entry above): right after a miss published a\n"
    "  slotted holder it called `Creations.adopt_children`, which moved the holder's disposal-bearing `many` children out\n"
    "  of their spells' buckets into the holder's `HolderDisposalEntry`, so purging the holder disposed them after it, an\n"
    "  ownership move carried them in the holder's row and a `many` purge or probe of the child's spell skipped them.\n"
    "  Nothing survives: the record, the verb, the adoption line and the holder branches of disposal, purge, extract and\n"
    "  restore are gone, and a holder's disposal value is its own `(object, methods)` tuple again.\n"
    "  EVIDENCE: `src/melder/aether/conduit/creations/creations.py:Creations._dispose_entry` and\n"
    "  `Creations.extract_spell_creations`.\n",
    ["HolderDisposalEntry", "adopt_children", "byte-identical"],
)

# E7 Holder-owned many children: REMOVED; the specializer's decline survives.
span(
    "- Holder-owned many children (2026-10-14, 0.2.8235): a disposal-bearing `many` child built for a slotted holder is\n",
    "generalized_hydrator.py:_install_specializing_door`.\n",
    "- Holder-owned many children (2026-10-14, 0.2.8235; REMOVED at 0.2.8267 by the first entry above): a disposal-bearing\n"
    "  `many` child built for a slotted holder was registered in the store that owned the holder (the site's `c{i}`), not in\n"
    "  the meld's innermost scope, so a lesser, spellspace, borrowing root or cluster member that first melded the holder\n"
    "  did not dispose it when it ended. What survives: the opt-in singleton specializer, whose straight-line body would\n"
    "  build a captured holder's `many` child on every warm meld, declines graphs in which a `many` step feeds a non-`many`\n"
    "  step and keeps the plain door; the child is needed only in the holder's first build.\n"
    "  EVIDENCE: `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:rows_feed_many_into_non_many_step`\n"
    "  and `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:_install_specializing_door`.\n",
    ["c{i}", "Through 0.2.8234"],
)

# E8/E9 The two old failure modes go; two Breaking entries lead the list.
span(
    "- Purging a holder disposes the `many` children built for it, after it, and raises their disposal failures with its\n",
    "`Creations.extract_spell_creations`.\n",
    "",
    ["0.2.8238", "Creations.purge"],
)
span(
    "- A disposal-bearing `many` child of a slotted holder is no longer disposed while its holder is still in use (fixed\n",
    "test_conduit_component_many_child_disposed_with_its_holder.py`.\n",
    "",
    ["0.2.8235", "SitePlanEmission._emit_context"],
)
FAILURES = (
    "- Breaking (0.2.8267): a scope that builds a holder's disposal-bearing `many` dependency disposes it when that scope\n"
    "  ends, even while the holder lives on - the behaviour through 0.2.8234, on the owner's decision. A `unique` holder\n"
    "  first melded through a lesser, in a root spellspace or in a lesser's spellspace (also as the dependency of a\n"
    "  per-conduit consumer melded in a lesser, and by an override meld through a lesser), a `unique_per_conduit` holder\n"
    "  first melded in a spellspace, a lineage holder first melded through a lesser or in a root spellspace, a borrowed\n"
    "  `unique` first melded by its borrower and a cluster holder first melded by a member each keep handing out the\n"
    "  `many` object that scope disposed when it ended (pool return, spellspace exit, borrower or member teardown);\n"
    "  0.2.8235-0.2.8265 recorded it with the holder's owner instead. That is the holder's business: meld the holder first\n"
    "  in the scope it lives in, so that scope builds its `many` and disposes it when it ends, or leave the dependency\n"
    "  without disposal methods (no per-bind or Book disposal names it has) and let the holder's own disposal close it.\n"
    "  EVIDENCE: `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:SitePlanEmission._emit_context`\n"
    "  and `tests/component/melder/aether/conduit/test_conduit_component_many_child_belongs_to_the_scope_that_built_it.py`.\n"
    "- Breaking (0.2.8267): cleaning up a slotted holder runs only the holder's own disposal methods. A purge of the holder\n"
    "  no longer disposes the `many` objects built for it, or raises their disposal failures with its own\n"
    "  (0.2.8238-0.2.8265 did both): they are disposed when the store that recorded them ends, and their failures are\n"
    "  raised there. An ownership move carries the holder alone; its `many` objects stay in the store that built them,\n"
    "  which disposes them when it ends (0.2.8238-0.2.8265 moved them in the holder's row). A `many` purge or\n"
    "  live-creation probe of the child's spell counts every child its store recorded, a live holder's included (it\n"
    "  skipped them).\n"
    "  EVIDENCE: `src/melder/aether/conduit/creations/creations.py:Creations.purge`, `Creations.extract_spell_creations` and\n"
    "  `tests/integration/melder/conduit/test_conduit_integration_holder_cleanup_leaves_its_many_children.py`.\n"
)
exact("## Failure Modes and Error Paths\n- Fixed in 0.2.8266:", "## Failure Modes and Error Paths\n" + FAILURES + "- Fixed in 0.2.8266:")

# E10/E11 Guardrail counts.
exact(
    "  alongside `MANIFEST_VERSION`, `BUILT_FOR_VERSION` and `MANIFEST_ENTRY_COUNT` (630 at\n"
    "  0.2.8257: `SpellCodeDigest` and `BindingManifest` joined; 628 at 0.2.8246: the managed-spell classes\n"
    "  joined at 0.2.8242-0.2.8244; 620 at 0.2.8216). The TRUTH is the COMMITTED manifest\n"
    "  `_bind_guard/manifest/bind_guard_manifest.py`; the loader hydrates it through a `.meldercache`\n",
    "  alongside `MANIFEST_VERSION`, `BUILT_FOR_VERSION` and `MANIFEST_ENTRY_COUNT` (629 at\n"
    "  0.2.8267: `HolderDisposalEntry` left; 630 at 0.2.8257: `SpellCodeDigest` and `BindingManifest` joined; 628 at\n"
    "  0.2.8246: the managed-spell classes joined at 0.2.8242-0.2.8244; 620 at 0.2.8216). The TRUTH is the COMMITTED\n"
    "  manifest `_bind_guard/manifest/bind_guard_manifest.py`; the loader hydrates it through a `.meldercache`\n",
)
exact("the real manifest (630 entries at 0.2.8257) begin refusing", "the real manifest (629 entries at 0.2.8267) begin refusing")

# E12 C1 code map.
exact(
    "  end_line: 652\n  loc: 652\n  verified_at: 2026-10-18T20:24:47Z\n"
    "  note: GENERATED DURABLE BUILD ASSET holding `ENTRIES`; committed, do not\n    edit by hand.\n"
    "    630 entries at 0.2.8257 (`SpellCodeDigest`, `BindingManifest`), measured on this landing's rebuild output.\n",
    f"  end_line: 651\n  loc: 651\n  verified_at: {stamp}\n"
    "  note: GENERATED DURABLE BUILD ASSET holding `ENTRIES`; committed, do not\n    edit by hand.\n"
    "    629 entries at 0.2.8267 (`HolderDisposalEntry` left; 630 at 0.2.8257), measured on this landing's rebuild output.\n",
)
exact(
    "  end_line: 2121\n  loc: 2121\n  verified_at: 2026-10-16T11:03:50Z\n"
    "  note: key-set plan lowering: site graph from steps, placement, emission, call shape; an automatic world's `unique`\n"
    "    sites read their owner store as a plan constant (0.2.8221); a shared site's `many` children register in that\n"
    "    site's store (0.2.8235) and its miss records them with the holder (`adopt_children`, 0.2.8238); the managed site\n"
    "    kinds - leasing and fresh, the inline pop, the reserve-first miss, the lease return (0.2.8245); the missing-pool\n"
    "    message without the pre-conjure staging cause (0.2.8248).\n",
    f"  end_line: 2105\n  loc: 2105\n  verified_at: {stamp}\n"
    "  note: key-set plan lowering: site graph from steps, placement, emission, call shape; an automatic world's `unique`\n"
    "    sites read their owner store as a plan constant (0.2.8221); the managed site kinds - leasing and fresh, the\n"
    "    inline pop, the reserve-first miss, the lease return (0.2.8245); the missing-pool message without the\n"
    "    pre-conjure staging cause (0.2.8248); every disposal-bearing `many` child registers in the meld's innermost\n"
    "    scope, a shared site's miss selecting it after its unresolved-input check, and nothing records it with the\n"
    "    holder (0.2.8267; 0.2.8235-0.2.8265 registered it in the site's store and, from 0.2.8238, with the holder).\n",
)
exact(
    "  end_line: 7907\n  loc: 7907\n  verified_at: 2026-10-19T13:16:16Z\n  note: conduit lifecycle and meld facade;",
    f"  end_line: 7909\n  loc: 7909\n  verified_at: {stamp}\n  note: conduit lifecycle and meld facade;",
)
exact(
    "    is refused with nothing moved (0.2.8262).\n- path: `src/melder/aether/conduit/conduit_pool.py`",
    "    is refused with nothing moved (0.2.8262). `transfer_spell_ownership`'s docstring says a moved holder's `many`\n"
    "    objects stay in the store that recorded them (0.2.8267).\n- path: `src/melder/aether/conduit/conduit_pool.py`",
)
exact(
    "  end_line: 2223\n  loc: 2223\n  verified_at: 2026-10-17T23:03:04Z\n  note: ownership transfer;",
    f"  end_line: 2225\n  loc: 2225\n  verified_at: {stamp}\n  note: ownership transfer;",
)
exact(
    "    explicit index step from a spell_id (0.2.8253).\n\nResolution and creations:",
    "    explicit index step from a spell_id (0.2.8253); `_move_creations` says a holder's row carries the holder alone\n"
    "    (0.2.8267).\n\nResolution and creations:",
)
exact(
    "  end_line: 1880\n  loc: 1880\n  verified_at: 2026-10-18T01:42:03Z\n"
    "  note: instance registry; `ManyDisposalBucket` and `register_many` (0.2.8216); `HolderDisposalEntry` and\n"
    "    `adopt_children` (0.2.8238); the managed pool map, `ensure_managed_quantity`, `discard_managed_quantity`, pools\n"
    "    cleaned first, the `managed` row (0.2.8243-0.2.8246); `ensure_managed_quantity` rebinds a found pool after the\n"
    "    store lock (0.2.8254).\n",
    f"  end_line: 1680\n  loc: 1680\n  verified_at: {stamp}\n"
    "  note: instance registry; `ManyDisposalBucket` and `register_many` (0.2.8216); the managed pool map,\n"
    "    `ensure_managed_quantity`, `discard_managed_quantity`, pools cleaned first, the `managed` row\n"
    "    (0.2.8243-0.2.8246); `ensure_managed_quantity` rebinds a found pool after the store lock (0.2.8254); the holder\n"
    "    record of 0.2.8238 (`HolderDisposalEntry`, `adopt_children`) is removed and a slotted holder's entry is its own\n"
    "    `(object, methods)` tuple again (0.2.8267).\n",
)

# E13 Numeric citations into conduit.py past transfer_spell_ownership (def at 4273) moved two lines.
shifted = []


def _shift(match):
    numbers = re.sub(r"\d+", lambda n: str(int(n.group(0)) + 2) if int(n.group(0)) >= 4273 else n.group(0), match.group(2))
    shifted.append((match.group(2), numbers))
    return match.group(1) + numbers


doc = re.sub(r"(src/melder/aether/conduit/conduit\.py:)(\d+(?:(?:, | ?- ?)\d+)*)", _shift, doc)
assert len(shifted) == 10, shifted

# E14 Handoff summary entry.
HANDOFF = (
    "2026-10-24 a `many` belongs to the scope that built it (0.2.8267;\n"
    "STORY-2026-10-24-remove_many_child_holder_ownership, on the owner's decision \"lets rip it out because it should\n"
    "behave like autofac not mysteriously cleanup transient objects\"): a disposal-bearing `many` built for a slotted\n"
    "holder is recorded and disposed by the meld's innermost scope, like any `many`, and cleaning up a holder runs only\n"
    "its own disposal methods; the 0.2.8235 placement and the 0.2.8238 holder record (`HolderDisposalEntry`,\n"
    "`adopt_children`) are removed. A new first operational invariant, the meld and transfer sequences, the Runtime\n"
    "Model's defect example, two Breaking failure modes in place of the 0.2.8235 fix and the 0.2.8238 purge entry, the\n"
    "two removed invariants (marked REMOVED; the specializer's decline is kept), the transfer-default invariant, the\n"
    "guardrail's bind-guard count (629) and the code map (five files remeasured) carry it; the component map carries the\n"
    "per-component contracts. Numeric citations into conduit.py past `transfer_spell_ownership` moved two lines with its\n"
    "docstring and were remapped.\n\n"
)
exact("## Context / Handoff Summary\n\n2026-10-24 cache saves are best-effort", "## Context / Handoff Summary\n\n" + HANDOFF + "2026-10-24 cache saves are best-effort")

for block in new_lines_report + [HANDOFF]:
    for line in block.split("\n"):
        if len(line) > 120 and "EVIDENCE" not in line and not line.lstrip().startswith(("`src/", "and `src/")):
            print("LONG", len(line), line[:100])
print("conduit.py citations shifted:", shifted)
assert path.read_bytes() == raw, "src_architecture.md changed while the edits were prepared"
path.write_bytes(doc.encode("utf-8"))
print("wrote", path, len(doc.split("\n")) - 1, "lines")
