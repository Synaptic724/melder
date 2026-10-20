"""Hand edits, batch 02: spellbook/spell.py and spellbook/spellbook.py (melder_1, 2026-10-18).

Each line that called a SpellIndex (or its member set) a lineage, rewritten by hand in its sentence. A lineage is a
conduit scope tree; a SpellIndex organizes spells and selects one of them. SpellSystemStates keeps one state per
SpellIndex (keyed by the index id), so "the lineage state" there is the SpellIndex's state. Every occurrence in these
two files means the SpellIndex; none is a scope tree. One neighbouring line (spellbook.py 4030) changes with its
sentence so its pronoun names the spell, not the index.
"""
S = "src/melder/aether/spellbook/spell.py"
B = "src/melder/aether/spellbook/spellbook.py"

EDITS = [
    # spell.py - class docstring.
    (S, 77, "    - Wraps exactly one registered spell target plus its `SpellIndex`", [
        "    - Wraps exactly one registered spell target plus its `SpellIndex`, the",
    ]),
    (S, 78, "      lineage/version record.", [
        "      index that organizes this spell with the other members and selects one.",
    ]),
    (S, 215, "        (paired with its `SpellIndex` lineage/version record) from a user target;", [
        "        (paired with the `SpellIndex` that organizes it) from a user target;",
    ]),
    (S, 217, "        registers the lineage into `SpellSystemStates`. Downstream, the SpellCompiler", [
        "        registers its SpellIndex into `SpellSystemStates`. Downstream, the SpellCompiler",
    ]),
    # spell.py - __init__ Args.
    (S, 341, "            spell_index (SpellIndex): Lineage/version tracker for this spell.", [
        "            spell_index (SpellIndex): The SpellIndex this spell is organized under (it selects one member).",
    ]),
    # spell.py - _add_owned_conduit's helper: the CreationGate is the spell index's gate.
    (S, 1027, "                spell-lineage gate operations.", [
        "                spell-index gate operations.",
    ]),
    # spell.py - invalidate_spell: SpellSystemStates.mark_structural_change(self.spell_index, ...).
    (S, 1613, "            2. lineage/control-plane invalidation", [
        "            2. control-plane invalidation of its SpellIndex",
    ]),
    (S, 1614, "               - mark the lineage structurally gated in `SpellSystemStates`", [
        "               - mark its SpellIndex structurally gated in `SpellSystemStates`",
    ]),
    (S, 1634, "                Optional structural change reason to record in the lineage", [
        "                Optional structural change reason to record in its SpellIndex's",
    ]),
    # spell.py - system_state: get_by_index_id(self.spell_index.id).
    (S, 1766, "        Return the SpellSystemState instance associated with this spell's lineage.", [
        "        Return the SpellSystemState instance associated with this spell's SpellIndex.",
    ]),
    (S, 1772, "            - Mutation and contract operations can ask for the current lineage state.", [
        "            - Mutation and contract operations can ask for the current state of its SpellIndex.",
    ]),
    (S, 1775, "            - Returns `None` when SpellSystemStates are unavailable or the lineage is", [
        "            - Returns `None` when SpellSystemStates are unavailable or the SpellIndex is",
    ]),
    (S, 1780, "                The state object for this spell's lineage, if available.", [
        "                The state object for this spell's SpellIndex, if available.",
    ]),

    # spellbook.py - class AGENT_PURPOSE: the Conduit owns the SpellIndex the verbs move members of.
    (B, 174, "        lineage, and Spellbook applies the membership change because it owns the index", [
        "        SpellIndex, and Spellbook applies the membership change because it owns the index",
    ]),
    # spellbook.py - _ensure_contracted_active.
    (B, 1838, '        eager "follow" used when an owner notches an index-linked lineage to a', [
        '        eager "follow" used when an owner notches a SpellIndex this borrower holds through an',
    ]),
    (B, 1839, "        version this borrower has not seen:", [
        "        index link to a version this borrower has not seen:",
    ]),
    # spellbook.py - find_spell_by_spell_id: a transfer migrates every member of the index.
    (B, 2079, "              the whole lineage.", [
        "              every version of the index.",
    ]),
    # spellbook.py - get_spell_permissions(spell_index): reads _find_spell(spell_index), the index's active spell.
    (B, 2134, "        Read the capability ceiling recorded for one LOCAL spell lineage.", [
        "        Read the capability ceiling recorded for the active spell of one LOCAL SpellIndex.",
    ]),
    (B, 2137, "            Report what this Spellbook is willing to expose for a lineage it OWNS, which is", [
        "            Report what this Spellbook is willing to expose for a SpellIndex it OWNS, which is",
    ]),
    (B, 2141, "            - LOCAL ONLY. Contracted (borrowed) lineages are not searched, so a lineage", [
        "            - LOCAL ONLY. Contracted (borrowed) indexes are not searched, so a SpellIndex",
    ]),
    (B, 2155, "                Lineage handle whose owning spell should be read.", [
        "                The SpellIndex whose active spell's permissions are read.",
    ]),
    # spellbook.py - find_spell_index.
    (B, 2335, "        Resolve the lineage (`SpellIndex`) behind one logical spell address.", [
        "        Resolve the `SpellIndex` behind one logical spell address.",
    ]),
    (B, 2339, "            durable lineage handle, so callers can follow the lineage rather than pinning", [
        "            durable SpellIndex, so callers can follow its selected spell rather than pinning",
    ]),
    (B, 2344, "              A borrowed lineage is therefore resolvable through the borrower's own book.", [
        "              A borrowed SpellIndex is therefore resolvable through the borrower's own book.",
    ]),
    (B, 2361, "                The lineage handle for the addressed spell. The returned index is the", [
        "                The SpellIndex of the addressed spell. The returned index is the",
    ]),
    (B, 2363, "                owner notches, which is the intended way to follow a lineage.", [
        "                owner notches, which is the intended way to follow the index's selected spell.",
    ]),
    # spellbook.py - find_spell_key.
    (B, 2483, "            - Use `find_spell_index(...)` instead when you want the lineage itself; that is", [
        "            - Use `find_spell_index(...)` instead when you want the SpellIndex itself; that is",
    ]),
    # spellbook.py - _get_conduit_by_spell_id Raises: the spell's index is between owners during a transfer.
    (B, 2714, "                another frame, its owner cleaned, or a lineage between owners while an ownership", [
        "                another frame, its owner cleaned, or its SpellIndex between owners while an ownership",
    ]),
    # spellbook.py - _find_contracted_spell_by_id (behaviour unchanged; the open finding is the owner's).
    (B, 3060, "            lineage's active copy in `_contracted_spells` - single-key reads, no copy. Only a version this", [
        "            index's active copy in `_contracted_spells` - single-key reads, no copy. Only a version this",
    ]),
    (B, 3077, "        # Still O(1): a parked borrowed copy's index keys its lineage's active copy.", [
        "        # Still O(1): a parked borrowed copy's index keys that index's active copy.",
    ]),
    # spellbook.py - _add_inactive_contracted_spell.
    (B, 3263, "        off resolution (unmeldable) until the owner notches the lineage and the", [
        "        off resolution (unmeldable) until the owner notches the SpellIndex and the",
    ]),
    (B, 3289, "            # Existence: track every member id of the lineage, matching the active", [
        "            # Existence: track every member id of the SpellIndex, matching the active",
    ]),
    # spellbook.py - _notch_spell / _apply_notch (SpellSystemStates is keyed by index id).
    (B, 3871, "        threaded into the spell-owned invalidation so the lineage -- and its", [
        "        threaded into the spell-owned invalidation so the SpellIndex -- and its",
    ]),
    (B, 3940, "            6. Mark every lineage downstream of this one for revalidation", [
        "            6. Mark every SpellIndex downstream of this one for revalidation",
    ]),
    (B, 4007, "        # D2: everything downstream of the notched lineage - its dependents by registry edge, in any Book, and the", [
        "        # D2: everything downstream of the notched SpellIndex - its dependents by registry edge, in any Book, and the",
    ]),
    (B, 4029, "        # Mark the promoted lineage structurally changed (the walk above marked its", [
        "        # Mark the promoted spell's SpellIndex structurally changed (the walk above marked its",
    ]),
    (B, 4030, "        # dependents) and clear its stale CreationContext. invalidate_spell also sets", [
        "        # dependents) and clear the spell's stale CreationContext. invalidate_spell also sets",
    ]),
    # spellbook.py - cleanup_spell.
    (B, 4368, "        lineage are flagged dirty (and dependents are rechecked) while the index", [
        "        SpellIndex are flagged dirty (and dependents are rechecked) while the index",
    ]),
    (B, 4381, "              context is cleared and the lineage is marked structurally changed so", [
        "              context is cleared and its SpellIndex is marked structurally changed so",
    ]),
    (B, 4515, "            # CLEAN UP. Only an ACTIVE spell is invalidated first: flag it + its lineage", [
        "            # CLEAN UP. Only an ACTIVE spell is invalidated first: flag it + its SpellIndex",
    ]),
]
