"""Hand edits, batch 04: conduit/conduit.py (melder_1, 2026-10-18).

conduit.py uses "lineage" mostly for the conduit scope tree, and those stay: the lesser lineage the ward tears down,
the lineage root and its `unique_per_conduit_lineage` store, the shared lineage hooks, the gate controller's lineage
rebinding (`_set_creation_gate_controller_for_lineage`, `conduit_lineage_gate_ops`), the recorded lineage
ancestors, enable/disable meld "for this conduit lineage", and every "Root conduit is not set for this lineage."
error (69 lines). The 28 lines below mean a SpellIndex (or, at 7397 and 7460, a root spell and one granted spell)
and are rewritten by hand.
"""
C = "src/melder/aether/conduit/conduit.py"

EDITS = [
    # _add_spells_to_aether.
    (C, 3112, "        Adds this Conduit's local spell lineages (SpellIndex keys) into the shared", [
        "        Adds this Conduit's local spell indexes (SpellIndex keys) into the shared",
    ]),
    # get_conduit_by_spell_id / get_spell_by_spell_id Raises: the spell's index is between owners.
    (C, 3153, "                another frame, its owner cleaned, or a lineage between owners while an", [
        "                another frame, its owner cleaned, or its SpellIndex between owners while an",
    ]),
    (C, 3232, "                another frame, its owner cleaned, or a lineage between owners while an", [
        "                another frame, its owner cleaned, or its SpellIndex between owners while an",
    ]),
    # get_spell_by_index_id.
    (C, 3250, "        Retrieve a spell object by its stable SpellIndex lineage id.", [
        "        Retrieve a spell object by the stable id of its SpellIndex.",
    ]),
    (C, 3253, "            Expose the Spellbook-owned stable-lineage lookup path on the", [
        "            Expose the Spellbook-owned SpellIndex lookup path on the",
    ]),
    (C, 3258, "            - Resolves by SPELL INDEX id, so it addresses a whole version LINEAGE", [
        "            - Resolves by SPELL INDEX id, so it addresses a whole SpellIndex",
    ]),
    (C, 3259, "              rather than one version - the spell you get back is the lineage's", [
        "              rather than one version - the spell you get back is the index's",
    ]),
    (C, 3266, "                Stable SpellIndex lineage id (ULID) to resolve.", [
        "                Stable SpellIndex id (ULID) to resolve.",
    ]),
    # find_spell_id.
    (C, 3352, "          1) Spellbook.find_spell_index(...) to locate the SpellIndex lineage.", [
        "          1) Spellbook.find_spell_index(...) to locate the SpellIndex.",
    ]),
    (C, 3354, "          3) Returns spell.spell_id (the current head version for that lineage).", [
        "          3) Returns spell.spell_id (the version that SpellIndex selects now).",
    ]),
    # get_spell_permissions: the old lookup went through the index.
    (C, 4198, "              permissions THAT spell was bound with. Until 0.2.8253 it matched by lineage,", [
        "              permissions THAT spell was bound with. Until 0.2.8253 it matched by SpellIndex,",
    ]),
    # transfer_spell_ownership.
    (C, 4290, "            - The whole lineage moves: the spell's index, with its active and", [
        "            - The spell's whole SpellIndex moves: the index, with its active and",
    ]),
    (C, 4344, "            invalidate_after_transfer: If True, mark lineage dirty after transfer.", [
        "            invalidate_after_transfer: If True, mark the moved SpellIndex dirty after transfer.",
    ]),
    (C, 4345, "            mark_dependencies_dirty: If True, mark dependency lineages dirty (even if not moved).", [
        "            mark_dependencies_dirty: If True, mark the dependencies' indexes dirty (even if not moved).",
    ]),
    # _transfer_spell_ownership_preflight / _transfer helpers' Args.
    (C, 4419, "                Spell object, spell id string, or SpellIndex-like lineage", [
        "                Spell object, spell id string, or SpellIndex",
    ]),
    (C, 4426, "                Whether owned dependency lineages should also transfer.", [
        "                Whether the owned dependencies' indexes should also transfer.",
    ]),
    (C, 4431, "                Whether the moved lineage should remain gated/dirty afterward.", [
        "                Whether the moved SpellIndex should remain gated/dirty afterward.",
    ]),
    (C, 4529, "                Whether owned dependency lineages should also transfer.", [
        "                Whether the owned dependencies' indexes should also transfer.",
    ]),
    (C, 4533, "                Whether the moved lineage should remain gated/dirty afterward.", [
        "                Whether the moved SpellIndex should remain gated/dirty afterward.",
    ]),
    # notch_spell.
    (C, 5682, "              remove anything. The previous member stays in the lineage, parked, and a", [
        "              remove anything. The previous member stays in the index, parked, and a",
    ]),
    (C, 5784, "            # Index-link receivers follow the lineage: move their subscription head", [
        "            # Index-link receivers follow the index's selected spell: move their subscription head",
    ]),
    # add_to_spell_index.
    (C, 6024, "            Move a staged (parked) spell into another index's lineage, ahead of a notch to", [
        "            Move a staged (parked) spell into another SpellIndex, ahead of a notch to",
    ]),
    (C, 6037, "            - Adds a version to the lineage WITHOUT making it active - selection is a", [
        "            - Adds a version to the index WITHOUT making it active - selection is a",
    ]),
    (C, 6092, "        # Capture the source lineage BEFORE the move: the seam repoints", [
        "        # Capture the source index BEFORE the move: the seam repoints",
    ]),
    # remove_from_spell_index.
    (C, 6137, "            Take a staged (parked) spell out of an index's lineage, into an index of its", [
        "            Take a staged (parked) spell out of its SpellIndex, into an index of its",
    ]),
    # cleanup_spell.
    (C, 6261, "        # A destroyed index-linked lineage must be dropped on its receivers so they", [
        "        # A destroyed SpellIndex shared by index link must be dropped on its receivers so they",
    ]),
    # _remove_root_from_contracts: root_spell_id names a root spell, not a scope root.
    (C, 7397, "                Lineage root whose contracted details should be untracked across", [
        "                The root spell whose contracted details should be untracked across",
    ]),
    # add_spell_to_contract_with_dependencies: `spell` is one version.
    (C, 7460, "                The spell or lineage to grant across the existing contract.", [
        "                The spell (one version) to grant across the existing contract.",
    ]),
]
