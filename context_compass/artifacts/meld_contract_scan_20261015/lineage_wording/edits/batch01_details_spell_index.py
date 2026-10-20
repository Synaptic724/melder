"""Hand edits, batch 01: contract/details.py and bind/spell_index.py (melder_1, 2026-10-18).

Each line that called a SpellIndex (or its member set) a lineage, rewritten by hand in its sentence. A lineage is a
conduit scope tree; a SpellIndex organizes spells and selects one of them.
"""
D = "src/melder/aether/conduit/conduit_ward/contract/details.py"
I = "src/melder/aether/spellbook/bind/spell_index.py"

EDITS = [
    (D, 18, "    A `Detail` records which lineage is being shared, which version was", [
        "    A `Detail` records which spell is being shared (the spell_id granted),",
        "    the SpellIndex that spell is organized under, and what permission",
        "    applies. It is direction-aware (via `contract_type`). It also carries",
        "    optional `sources`, which lets the ward",
    ]),
    (D, 19, "    present when the contract was created, and what permission applies.", []),
    (D, 20, "    It is lineage-aware (uses `SpellIndex`) and direction-aware (via", []),
    (D, 21, "    `contract_type`). It also carries optional `sources`, which lets the ward", []),
    (D, 26, "        spell_index (SpellIndex): Lineage identity for the contracted spell.", [
        "        spell_index (SpellIndex): The SpellIndex the contracted spell is organized under.",
    ]),
    (D, 53, "        lineage is granted or borrowed; users read contract state through ward", [
        "        spell is granted or borrowed; users read contract state through ward",
    ]),
    (D, 58, "        `IndexDetail`, which subscribes to a whole lineage instead. Its three", [
        "        `IndexDetail`, which subscribes to a whole SpellIndex instead. Its three",
    ]),
    (D, 64, "        `sources` is what makes dependency-linked rollback correct. One lineage", [
        "        `sources` is what makes dependency-linked rollback correct. One spell",
    ]),
    (D, 68, "        root would revoke a lineage another root still depends on.", [
        "        root would revoke a spell another root still depends on.",
    ]),
    (D, 103, "            spell_index: Lineage identifier for the contracted spell.", [
        "            spell_index: The SpellIndex the contracted spell is organized under.",
    ]),
    (D, 105, "            permissions: Permission granted to this lineage.", [
        "            permissions: Permission granted for this spell.",
    ]),
    (D, 116, "            `spell_index` remains the durable lineage anchor used for later", [
        "            `spell_index` records the SpellIndex that spell is organized under,",
    ]),
    (D, 117, "            current-head resolution.", [
        "            which later reads use to find the index's selected spell.",
    ]),
    (D, 163, "        Drops references to the lineage, version, permissions, and contract", [
        "        Drops references to the SpellIndex, spell id, permissions, and contract",
    ]),
    (D, 195, "        Check whether this lineage contains a specific version SHA.", [
        "        Check whether this row's SpellIndex contains a specific spell id.",
    ]),
    (D, 201, "            bool: True if the lineage advertises the version, else False; False once the", [
        "            bool: True if the SpellIndex holds that spell id, else False; False once the",
    ]),
    (D, 205, "            The index belongs to the Book that owns the lineage, which can clean it while", [
        "            The index belongs to the Book that owns its spells, which can clean it while",
    ]),
    (D, 219, "            detail when they transitively require the same contracted lineage.", [
        "            detail when they transitively require the same contracted spell.",
    ]),
    (D, 254, "    whole SpellIndex (lineage). It is identified by the index's stable id", [
        "    whole SpellIndex. It is identified by the index's stable id",
    ]),
    (D, 255, "    (`index_id`), and `selected_spell_id` tracks the lineage's CURRENT active", [
        "    (`index_id`), and `selected_spell_id` tracks the index's CURRENT selected",
    ]),
    (D, 256, "    member -- it is updated as the owner notches, so the contract surface never has", [
        "    spell -- it is updated as the owner notches, so the contract surface never has",
    ]),
    (D, 261, "        spell_index (SpellIndex): The contracted lineage (durable identity).", [
        "        spell_index (SpellIndex): The contracted SpellIndex (durable identity).",
    ]),
    (D, 262, "        selected_spell_id (str): The lineage's current active member id (mutable).", [
        "        selected_spell_id (str): The index's currently selected spell id (mutable).",
    ]),
    (D, 296, "        an owner can notch a lineage - repointing its active spell - and every", [
        "        an owner can notch a SpellIndex - repointing its selected spell - and every",
    ]),
    (D, 298, "        alternative, re-granting each borrowed lineage on every notch, would", [
        "        alternative, re-granting each borrowed SpellIndex on every notch, would",
    ]),
    (D, 336, "            spell_index: The contracted lineage (durable identity / map key source).", [
        "            spell_index: The contracted SpellIndex (durable identity / map key source).",
    ]),
    (D, 337, "            selected_spell_id: The lineage's active member id at creation time.", [
        "            selected_spell_id: The index's selected spell id at creation time.",
    ]),
    (D, 338, "            permissions: Permission granted to this lineage.", [
        "            permissions: Permission granted for this SpellIndex.",
    ]),
    (D, 391, "        Repoint the subscription to the lineage's new active member.", [
        "        Repoint the subscription to the index's newly selected spell.",
    ]),
    (D, 397, "            spell_id: The lineage's new active member id.", [
        "            spell_id: The index's newly selected spell id.",
    ]),
    (D, 431, "        Check whether the contracted lineage contains a specific version SHA.", [
        "        Check whether the contracted SpellIndex contains a specific spell id.",
    ]),
    (D, 437, "            bool: True if the lineage advertises the version, else False; False once the", [
        "            bool: True if the SpellIndex holds that spell id, else False; False once the",
    ]),
    (D, 441, "            The index belongs to the Book that owns the lineage, which can clean it while", [
        "            The index belongs to the Book that owns its spells, which can clean it while",
    ]),
    (I, 48, "        the index is the lineage. Version HISTORY belongs to MutationResearch,", [
        "        the index organizes versions and selects one of them. Version HISTORY",
    ]),
    (I, 49, "        not here.", [
        "        belongs to MutationResearch, not here.",
    ]),
    (I, 63, "        membership is lineage truth, distinct from any one spell's custody.", [
        "        membership is the index's own truth, distinct from any one spell's custody.",
    ]),
    (I, 71, "        access: public. The stable lineage identity (immutable ULID) pointing at a mutable", [
        "        access: public. The stable index identity (immutable ULID) pointing at a mutable",
    ]),
    (I, 183, "              MEMBER - parked in its Book - so the member set is the lineage", [
        "              MEMBER - parked in its Book - so the member set holds every version",
    ]),
    (I, 184, "              and the selected id only the current head. A lookup by spell_id", [
        "              and the selected id names only the selected one. A lookup by spell_id",
    ]),
    (I, 220, "            - Adds to the lineage WITHOUT changing the selected id, so it grows the", [
        "            - Adds to the index WITHOUT changing the selected id, so it grows the",
    ]),
    (I, 298, "            - Tests MEMBERSHIP OF THE LINEAGE, not equality with the selected id, so a", [
        "            - Tests MEMBERSHIP OF THE INDEX, not equality with the selected id, so a",
    ]),
    (I, 301, "              the lineage's selected head.", [
        "              the index's selected spell.",
    ]),
    (I, 340, "            - Same membership semantics as `has_spell` (the whole version", [
        "            - Same membership semantics as `has_spell` (every member",
    ]),
    (I, 341, "              lineage, not only the selected id) while the index is live.", [
        "              spell id, not only the selected id) while the index is live.",
    ]),
    (I, 374, "            - Tests SELECTION, not membership: a parked member of the lineage answers False.", [
        "            - Tests SELECTION, not membership: a parked member of the index answers False.",
    ]),
    (I, 482, "              key while its lineage evolves.", [
        "              key while its member set changes.",
    ]),
]
