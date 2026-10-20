"""Hand edits, batch 13: the SpellIndex lines in three files with mixed line endings (melder_1, 2026-10-18).

Applied with apply_line_edits_keep_endings.py on the owner's ruling ("Yes, keep each ending"): each line keeps its own
terminator. compiler_phase_5.py 280: `_build_system_index_for_snapshot` reads each spell's SpellIndex id from
SpellSystemStates (`.spell_index_id`). frame_viewer.py 3637 and 6486 are facades over ViewFrame and ViewSpell
methods whose docstrings already say "spell index" (the collision grouping by index id; the crosswalk's
`spell_index_id`). view_spell.py 854 and 1731-1732: a spell's index and the spells it organizes.
"""
PH5 = "src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py"
FV = "src/melder/nexus/rift/frame_viewer/frame_viewer.py"
VS = "src/melder/nexus/rift/frame_viewer/view_spell.py"

EDITS = [
    (PH5, 280, "            - Resolves lineage ids from SpellSystemStates.", [
        "            - Resolves each spell's SpellIndex id from SpellSystemStates.",
    ]),
    (FV, 3637, "            binding name, spell name, lineage, or spellframe.", [
        "            binding name, spell name, spell index, or spellframe.",
    ]),
    (FV, 6486, "            conduit, root conduit, peer conduits, spellbook, lineage, and", [
        "            conduit, root conduit, peer conduits, spellbook, spell index, and",
    ]),
    (VS, 854, "            - Describes the spell's INDEX, i.e. its version lineage, so it answers", [
        "            - Describes the spell's INDEX, the SpellIndex organizing its versions, so it answers",
    ]),
    (VS, 1731, "              a whole version lineage, this returns EVERY visible spell sharing that", [
        "              every version it organizes, this returns EVERY visible spell in that",
    ]),
    (VS, 1732, "              lineage, not one spell.", [
        "              index, not one spell.",
    ]),
]
