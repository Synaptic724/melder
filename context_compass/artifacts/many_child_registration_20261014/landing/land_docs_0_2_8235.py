"""
Land the 0.2.8235 system-document changes (TASK-2026-10-14-fix_many_child_follows_holder).

Edits src_architecture.md and src_components.md with anchored replacements: every anchor must match exactly once,
both documents stay LF. Regenerate both indexes afterwards (index_document.py, then --check).

Run from the repository root: python land_docs_0_2_8235.py <verified_at UTC timestamp>
"""
import pathlib
import sys

SPL = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py"
GMC = (
    "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/"
    "generalized_manifest_no_overrides_compiler.py"
)
GHY = (
    "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/"
    "generalized_hydrator.py"
)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    assert count == 1, (label, count)
    return text.replace(old, new)


def insert_after_once(text: str, anchor: str, addition: str, label: str) -> str:
    return replace_once(text, anchor, anchor + addition, label)


def architecture(text: str, stamp: str) -> str:
    text = replace_once(text, "- Updated: 2026-10-12\n", "- Updated: 2026-10-14\n", "arch metadata")
    text = insert_after_once(
        text,
        "   The door takes that lock once: for a per-conduit or SpellSpace root, the normal site plan it calls\n"
        "   does not take the root's lock again (0.2.73).\n",
        "   A slotted site's disposal-bearing `many` children are registered in that site's store, with the\n"
        "   holder's owner, not in the meld's innermost scope (0.2.8235).\n",
        "arch meld sequence",
    )
    text = insert_after_once(
        text,
        "## Operational Invariants\n",
        "- Holder-owned many children (2026-10-14, 0.2.8235): a disposal-bearing `many` child built for a slotted holder is\n"
        "  recorded in, and disposed with, the store that owns the holder - the Spell owner's for `unique`, the conduit's for\n"
        "  `unique_per_conduit`, the space's for `unique_per_spell_space`, the lineage root's, the elected cluster leader's.\n"
        "  The site plan builds such a child only inside its holder's first build (`_miss{i}`) and registers it in that\n"
        "  site's store `c{i}`; a `many` root and its own `many` children still register in the meld's innermost scope (the\n"
        "  spellspace store, else the melding conduit's). Through 0.2.8234 every child registered in the innermost scope,\n"
        "  so a lesser's pool return, a spellspace exit, or a borrowing root's or cluster member's teardown ran its disposal\n"
        "  while the holder, owned elsewhere, kept handing it out. Children are built before the site's build lock and\n"
        "  `register_many` stays a leaf, so no lock or lock-order edge is added and every warm `_site_plan_executor` body\n"
        "  is unchanged; a lost cold race's children stay in the holder's store until it is disposed. Purge semantics are\n"
        "  unchanged: purging a holder disposes the holder only, and a `many` purge or live-creation probe finds the\n"
        "  children at the holder's owner. The opt-in singleton specializer, whose straight-line body would rebuild a\n"
        "  captured holder's child on every warm meld, declines graphs in which a `many` step feeds a non-`many` step and\n"
        "  keeps the plain door. Plans are emitted at hydration from manifest rows, so no cache generation or record\n"
        "  format moves.\n"
        f"  EVIDENCE: `{SPL}:SitePlanEmission._emit_context`,\n"
        "  `SitePlanEmission._emit_many`, `SitePlanEmission._emit_miss`,\n"
        f"  `{GMC}:rows_feed_many_into_non_many_step`\n"
        f"  and `{GHY}:_install_specializing_door`.\n",
        "arch invariant",
    )
    text = insert_after_once(
        text,
        "## Failure Modes and Error Paths\n",
        "- A disposal-bearing `many` child of a slotted holder is no longer disposed while its holder is still in use (fixed\n"
        "  in 0.2.8235). A `unique` holder first melded through a lesser, in a root spellspace or in a lesser's spellspace\n"
        "  (also as the dependency of a per-conduit consumer melded in a lesser, and by an override meld through a lesser),\n"
        "  a `unique_per_conduit` holder first melded in a spellspace, a lineage holder first melded through a lesser or in\n"
        "  a root spellspace, a borrowed `unique` first melded by its borrower and a cluster holder first melded by a member\n"
        "  each had the child's disposal methods run when that scope ended (pool return, spellspace exit, borrower or member\n"
        "  teardown), and the holder kept returning the disposed child. The child is now disposed when the holder's\n"
        "  owner's store is.\n"
        f"  EVIDENCE: `{SPL}:SitePlanEmission._emit_context`\n"
        "  and `tests/component/melder/aether/conduit/test_conduit_component_many_child_disposed_with_its_holder.py`.\n",
        "arch failure mode",
    )
    text = replace_once(
        text,
        f"- path: `{SPL}`\n"
        "  start_line: 1\n"
        "  end_line: 1588\n"
        "  loc: 1588\n"
        "  verified_at: 2026-10-03T22:12:00Z\n"
        "  note: key-set plan lowering: site graph from steps, placement, emission, call shape; an automatic\n"
        "    world's `unique` sites read their owner store as a plan constant (0.2.8221).\n",
        f"- path: `{SPL}`\n"
        "  start_line: 1\n"
        "  end_line: 1640\n"
        "  loc: 1640\n"
        f"  verified_at: {stamp}\n"
        "  note: key-set plan lowering: site graph from steps, placement, emission, call shape; an automatic\n"
        "    world's `unique` sites read their owner store as a plan constant (0.2.8221); a shared site's\n"
        "    `many` children register in that site's store (0.2.8235).\n",
        "arch code map",
    )
    text = insert_after_once(
        text,
        f"- `{GHY}`\n",
        f"- `{GMC}`\n",
        "arch sources",
    )
    text = insert_after_once(
        text,
        "## Context / Handoff Summary\n\n",
        "2026-10-14 holder-owned many children (0.2.8235): a slotted holder's disposal-bearing `many` children register in\n"
        "the holder's store (the site's `c{i}`) instead of the meld's innermost scope, so a lesser, spellspace, borrower or\n"
        "cluster member that first melded the holder no longer disposes them under it; the opt-in specializer declines\n"
        "graphs that feed a `many` step into a non-`many` step. The meld sequence, the operational invariants, the failure\n"
        "modes, the code map and the sources carry it; the component map carries the emission rule, the store selection\n"
        "and the live-creation probe.\n\n",
        "arch handoff",
    )
    return text


def components(text: str, stamp: str) -> str:
    text = replace_once(text, "- Updated: 2026-10-12\n", "- Updated: 2026-10-14\n", "comp metadata")
    text = replace_once(
        text,
        "`many_store.register_many(sidN, vN, dmN)` in the site plan, `many_creations.register_many(spell_id, instance,\n"
        "disposal_methods)` in the solo templates and `creations_i.register_many(...)` in the specializer; cache\n"
        "generation 16 (`many_registration_per_key_methods`) retires executors emitted with the old keyword call.\n",
        "`many_store.register_many(sidN, vN, dmN)` in the site plan (`c{i}.register_many(...)` for a shared site's child\n"
        "since 0.2.8235; see Component: SpellCompiler and Validation Pipeline, \"Holder-owned many children\"),\n"
        "`many_creations.register_many(spell_id, instance, disposal_methods)` in the solo templates and\n"
        "`creations_i.register_many(...)` in the specializer; cache generation 16 (`many_registration_per_key_methods`)\n"
        "retires executors emitted with the old keyword call.\n",
        "comp trim line",
    )
    text = replace_once(
        text,
        "disposal-bearing `many` is stored - in the innermost scope - so a `many` without disposal methods probes\n"
        "as 0. CORRECTED 2026-09-28: the SpellSpace door read `many` from the owner conduit's store, missing what\n"
        "the space held and counting what the conduit held.\n"
        "EVIDENCE: `src/melder/aether/conduit/meld/spellspace_meld.py:SpellSpaceMeld._describe_spell_live_creation_status`,\n"
        "`src/melder/aether/conduit/meld/conduit_meld.py:ConduitMeld._describe_spell_live_creation_status` and\n"
        f"`{SPL}:SitePlanEmission._many_store_prologue`.\n",
        "disposal-bearing `many` is stored - in the innermost scope - so a `many` without disposal methods probes\n"
        "as 0. CORRECTED 2026-09-28: the SpellSpace door read `many` from the owner conduit's store, missing what\n"
        "the space held and counting what the conduit held. Since 0.2.8235 a `many` built as a shared site's child is\n"
        "stored with that site (the holder's owner), so the probe counts it there - the root for a `unique` holder, the\n"
        "conduit for a per-conduit holder melded in its space, the lineage root, the cluster leader - and not at the\n"
        "lesser or space that melded the holder first.\n"
        "EVIDENCE: `src/melder/aether/conduit/meld/spellspace_meld.py:SpellSpaceMeld._describe_spell_live_creation_status`,\n"
        "`src/melder/aether/conduit/meld/conduit_meld.py:ConduitMeld._describe_spell_live_creation_status`,\n"
        f"`{SPL}:SitePlanEmission._many_store_prologue`\n"
        "and `SitePlanEmission._emit_context`.\n",
        "comp probe",
    )
    text = replace_once(
        text,
        "  `unique_per_conduit` the (owner) conduit's store; `unique_per_spell_space` the space's; a disposal-bearing\n"
        "  `many` the innermost scope's (the space's through a SpellSpace door, else the conduit's), and a `many`\n"
        "  without disposal methods is not stored. The old text put cluster and lineage in `spell._owner_creations`\n"
        "  and every per-conduit lifetime in \"caller creations\".\n"
        "  EVIDENCE: `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/"
        "solo_no_overrides_codegen_creation_compiler.py:_build_source`.\n",
        "  `unique_per_conduit` the (owner) conduit's store; `unique_per_spell_space` the space's; a disposal-bearing\n"
        "  `many` the innermost scope's (the space's through a SpellSpace door, else the conduit's) when it is the root\n"
        "  or a `many` root's child, and its holder's store when a shared site needs it (0.2.8235: a slotted holder's\n"
        "  `many` children belong to the holder's owner); a `many` without disposal methods is not stored. The old\n"
        "  text put cluster and lineage in `spell._owner_creations` and every per-conduit lifetime in \"caller creations\".\n"
        "  EVIDENCE: `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/"
        "solo_no_overrides_codegen_creation_compiler.py:_build_source`\n"
        f"  and `{SPL}:SitePlanEmission._emit_context`.\n",
        "comp store selection",
    )
    text = replace_once(
        text,
        "  a stored instance keeps today's \"already exists\" refusal (P2). Disposal-bearing many sites register in the\n"
        "  innermost scope store through `many_store.register_many(sidN, vN, dmN)` (0.2.8216; the positional hot verb\n"
        "  of Creations and SpellSpace), and every registration passes the Spell's live `disposal_method_names` list.\n",
        "  a stored instance keeps today's \"already exists\" refusal (P2). Disposal-bearing many sites at the top level\n"
        "  register in the innermost scope store through `many_store.register_many(sidN, vN, dmN)` (0.2.8216; the\n"
        "  positional hot verb of Creations and SpellSpace); one placed inside `_miss{i}` registers in `c{i}` (0.2.8235,\n"
        "  next bullet). Every registration passes the Spell's live `disposal_method_names` list.\n"
        "- Holder-owned many children (2026-10-14, 0.2.8235): a disposal-bearing many step registers in the store that owns\n"
        "  its context. `SitePlanEmission._emit_context(context, ...)` passes `many_store` to `_emit_many` at the top\n"
        "  level, where the plan prologue (`_many_store_prologue`) points it at the meld's innermost scope, and `c{i}`\n"
        "  inside shared site i's miss - the store the site is published to: the Spell owner's for `unique`, the\n"
        "  conduit's for `unique_per_conduit`, the space's for `unique_per_spell_space`, the lineage root's, the elected\n"
        "  leader's. So a slotted holder's `many` children are recorded with whatever owns the holder and disposed with\n"
        "  that store, never by a lesser's pool return, a spellspace exit or a borrowing root's teardown that happened to\n"
        "  meld the holder first (through 0.2.8234 they went to the innermost scope, whose end ran their disposal under a\n"
        "  live holder; `unique_per_spell_space` holders, whose store is that scope, were not affected). A miss emits no\n"
        "  prologue. Children are still built before the site's guard and `register_many` is the same leaf call, so lock\n"
        "  order and construction order are unchanged and every `_site_plan_executor` body (the warm path) is\n"
        "  byte-identical; a losing thread's children in a cold race stay in the holder's store until it is disposed.\n"
        "  Plans are emitted at hydration from manifest rows, so no cache generation moves. The opt-in singleton\n"
        "  specializer, whose straight-line body builds every non-captured step on every warm call, declines a graph in\n"
        "  which a `many` row feeds a non-`many` row (`rows_feed_many_into_non_many_step`, checked in\n"
        "  `_install_specializing_door` after the zero-capture check) and keeps the plain door; other graphs specialize\n"
        "  as before.\n"
        f"  EVIDENCE: `{SPL}:SitePlanEmission._emit_context`,\n"
        "  `SitePlanEmission._emit_many`, `SitePlanEmission._emit_miss`,\n"
        f"  `{GMC}:rows_feed_many_into_non_many_step`\n"
        f"  and `{GHY}:_install_specializing_door`.\n",
        "comp emission",
    )
    text = replace_once(
        text,
        f"- path: `{SPL}`\n"
        "  start_line: 1\n"
        "  end_line: 1588\n"
        "  loc: 1588\n"
        "  verified_at: 2026-10-03T22:12:00Z\n",
        f"- path: `{SPL}`\n"
        "  start_line: 1\n"
        "  end_line: 1640\n"
        "  loc: 1640\n"
        f"  verified_at: {stamp}\n",
        "comp code map",
    )
    text = insert_after_once(
        text,
        "## Context / Handoff Summary\n\n",
        "2026-10-14 holder-owned many children (0.2.8235): the SpellCompiler component carries the rule (a slotted holder's\n"
        "`many` children register in the holder's store, and the opt-in specializer declines graphs that feed a `many` step\n"
        "into a non-`many` step); Meld Resolution Runtime carries the store selection and the live-creation probe that follow\n"
        "from it; Creations and SpellSpace points the trim entry's emitted line at it; the code map extent of\n"
        "site_plan_lowering.py is remeasured.\n\n",
        "comp handoff",
    )
    return text


def main() -> int:
    stamp = sys.argv[1]
    docs = pathlib.Path("context_compass/system_docs")
    for name, edit in (("src_architecture.md", architecture), ("src_components.md", components)):
        path = docs / name
        raw = path.read_bytes()
        assert b"\r" not in raw, name
        text = edit(raw.decode("utf-8"), stamp)
        path.write_bytes(text.encode("utf-8"))
        long_lines = [
            (number, len(line)) for number, line in enumerate(text.split("\n"), 1)
            if len(line) > 120 and "`src/" not in line and "src/melder" not in line
        ]
        print(name, "lines", text.count("\n"), "long prose lines", long_lines[:10])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
