"""Promote spellspace_probe_many_2026_09_28 into system_docs/src_components.md (LF).

Usage (from context_compass/): python <this> <verified_at ISO-8601 UTC>. Every anchor must match once.
"""
import pathlib
import sys

VERIFIED_AT = sys.argv[1]
PATH = pathlib.Path("system_docs/src_components.md")

EDITS = [
    # 1. Creations and SpellSpace, Failure Modes: the known inaccuracy is fixed.
    (
        "- Known probe inaccuracy (2026-09-27): `SpellSpaceMeld._describe_spell_live_creation_status` reads `many`\n"
        "  from the owner conduit's store, but a disposal-bearing `many` melded through a space lives in the space's\n"
        "  own store, so a live-creation probe through a space can report 0 while the space holds one. Lifetimes\n"
        "  are unaffected.\n"
        "  EVIDENCE: `src/melder/aether/conduit/meld/spellspace_meld.py:SpellSpaceMeld._describe_spell_live_creation_status`.\n",
        "",
    ),
    # 2. Meld Resolution Runtime: probe scope paragraph after purge discovery.
    (
        "`src/melder/aether/conduit/meld/spellspace_meld.py:SpellSpaceMeld.purge`.\n"
        "\n"
        "Non-resolvable registration admission:\n",
        "`src/melder/aether/conduit/meld/spellspace_meld.py:SpellSpaceMeld.purge`.\n"
        "\n"
        "Live-creation probe scope (2026-09-28, 0.2.8204): each door's probe (`has_live_creation`,\n"
        "`describe_live_creation_status`) reads, per lifetime, the store its own meld registers into and its purge\n"
        "retires from, and never creates. ConduitMeld reads `many` (\"caller_conduit_many\") and `unique_per_conduit`\n"
        "(\"caller_conduit\") from its conduit store and refuses a spellspace-request spell. SpellSpaceMeld reads\n"
        "`many` (\"spellspace_many\") and `unique_per_spell_space` (\"spellspace\") from the space's store and\n"
        "`unique_per_conduit` (\"owner_conduit\") from the owner conduit's. Both read `unique` from the Spell owner's\n"
        "store, lineage from the lineage root and cluster from the elected leader (not live without one). Only a\n"
        "disposal-bearing `many` is stored - in the innermost scope - so a `many` without disposal methods probes\n"
        "as 0. CORRECTED 2026-09-28: the SpellSpace door read `many` from the owner conduit's store, missing what\n"
        "the space held and counting what the conduit held.\n"
        "EVIDENCE: `src/melder/aether/conduit/meld/spellspace_meld.py:SpellSpaceMeld._describe_spell_live_creation_status`,\n"
        "`src/melder/aether/conduit/meld/conduit_meld.py:ConduitMeld._describe_spell_live_creation_status` and\n"
        "`src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:SitePlanEmission._many_store_prologue`.\n"
        "\n"
        "Non-resolvable registration admission:\n",
    ),
    # 3. Meld Resolution Runtime, Responsibilities: store selection matched to the code.
    (
        "- Select creations container by Existence: shared lifetimes (unique, unique_per_conduit_cluster,\n"
        "  unique_per_conduit_lineage) use `spell._owner_creations`; per-conduit lifetimes\n"
        "  (unique_per_conduit, many, unique_per_spell_space) use caller creations.\n",
        "- Select the creations store by Existence (CORRECTED 2026-09-28): `unique` uses `spell._owner_creations`;\n"
        "  `unique_per_conduit_lineage` the lineage-root store and `unique_per_conduit_cluster` the elected leader's;\n"
        "  `unique_per_conduit` the (owner) conduit's store; `unique_per_spell_space` the space's; a disposal-bearing\n"
        "  `many` the innermost scope's (the space's through a SpellSpace door, else the conduit's), and a `many`\n"
        "  without disposal methods is not stored. The old text put cluster and lineage in `spell._owner_creations`\n"
        "  and every per-conduit lifetime in \"caller creations\".\n"
        "  EVIDENCE: `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:_build_source`.\n",
    ),
    # 4. Flow: the per-door read and the SpellSpace door.
    (
        "3. `Meld._describe_spell_live_creation_status(...)` inspects live runtime\n"
        "   storage only and returns presence/scope/count information without creating\n"
        "   anything.\n",
        "3. `Meld._describe_spell_live_creation_status(...)` inspects live runtime\n"
        "   storage only and returns presence/scope/count information without creating\n"
        "   anything.\n"
        "4. Each door reads the store its own meld writes (Meld Resolution Runtime, \"Live-creation probe scope\").\n"
        "   A SpellSpace has no public probe; its door (`SpellSpace._meld`, a SpellSpaceMeld) answers the same calls\n"
        "   for the space and reads `many` and `unique_per_spell_space` from the space's store (`many` since\n"
        "   2026-09-28).\n",
    ),
    # 5. C1: spellspace_meld.py remeasured.
    (
        "- path: `src/melder/aether/conduit/meld/spellspace_meld.py`\n"
        "  start_line: 1\n"
        "  end_line: 1031\n"
        "  loc: 1031\n"
        "  verified_at: 2026-09-27T23:41:28Z\n",
        "- path: `src/melder/aether/conduit/meld/spellspace_meld.py`\n"
        "  start_line: 1\n"
        "  end_line: 1045\n"
        "  loc: 1045\n"
        f"  verified_at: {VERIFIED_AT}\n",
    ),
    # 6. Handoff, newest first.
    (
        "## Context / Handoff Summary\n"
        "\n"
        "2026-09-27 scope exits (0.2.8203):",
        "## Context / Handoff Summary\n"
        "\n"
        "2026-09-28 SpellSpace probe (0.2.8204): the SpellSpace door's live-creation probe reads `many` from the\n"
        "space's own store, where every emitter registers a disposal-bearing `many` melded through a space and where\n"
        "the space's purge retires it; it reports \"spellspace_many\" with the space id. It used to read the owner\n"
        "conduit's store, missing what the space held and counting what the conduit held. Promoted into Meld\n"
        "Resolution Runtime (\"Live-creation probe scope\"; the store-selection responsibility corrected for `unique`,\n"
        "lineage and cluster too) and the probe flow; the Creations and SpellSpace \"Known probe inaccuracy\" failure\n"
        "mode is removed and spellspace_meld.py remeasured.\n"
        "\n"
        "2026-09-27 scope exits (0.2.8203):",
    ),
]

text = PATH.read_bytes().decode("utf-8")
assert "\r" not in text
for old, new in EDITS:
    assert text.count(old) == 1, (old[:70], text.count(old))
    text = text.replace(old, new)
for old, new in EDITS:
    for line in new.splitlines():
        if len(line) > 120:
            assert "`src/" in line and " " not in line.split("`src/", 1)[1].split("`", 1)[0], line
PATH.write_bytes(text.encode("utf-8"))
print("src_components promoted")
