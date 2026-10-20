"""Hand edits, batch 03: conduit_ward/conduit_ward.py (melder_1, 2026-10-18).

The ward uses "lineage" in both meanings. Its lesser tree - parent pointer, root pointer, `_lesser_conduits`, the
"lesser lineage" its cleanup tears down, the "Root conduit is not set for this lineage." errors - is the conduit scope
tree and stays (lines 67, 69, 78, 178, 185, 190, 227, 255, 259, 284, 407, 556, 564, 1241, 1255). Every contract-side
use means a SpellIndex (or the spell a Detail grants) and is rewritten here by hand. The identifier `lineage_id`
(2738-2739, a SpellIndex id read with `get_by_index_id`) keeps its name; it is on the list for the owner.
"""
W = "src/melder/aether/conduit/conduit_ward/conduit_ward.py"

EDITS = [
    # Class docstring - Subsystem Context.
    (W, 114, "        `Permissions` bounds what each granted lineage allows, and", [
        "        `Permissions` bounds what each granted spell or SpellIndex allows, and",
    ]),
    (W, 117, "        operation wards cannot express - changing who OWNS a lineage rather", [
        "        operation wards cannot express - changing who OWNS a SpellIndex rather",
    ]),
    # _create_detail.
    (W, 1666, "        Factory for a lineage-aware Detail entry.", [
        "        Factory for a Detail entry: one granted spell and the SpellIndex it is organized under.",
    ]),
    (W, 1670, "            permissions (Permissions): The permissions applied to this lineage.", [
        "            permissions (Permissions): The permissions applied to this spell.",
    ]),
    # _add_spell_to_contract.
    (W, 1862, "        It contracts one version of the spell's SpellIndex lineage. The borrower", [
        "        It contracts one version, one member of the spell's SpellIndex. The borrower",
    ]),
    (W, 1863, "        holds a copy of that version: active while the version is the lineage's", [
        "        holds a copy of that version: active while the version is its index's",
    ]),
    (W, 1870, "        follows the lineage to every new version instead.", [
        "        follows the SpellIndex to every newly selected version instead.",
    ]),
    # _add_index_to_contract.
    (W, 2106, "        Link a whole SpellIndex (lineage) into the contract with `conduit` as an", [
        "        Link a whole SpellIndex into the contract with `conduit` as an",
    ]),
    (W, 2113, "            index: The owned lineage to share.", [
        "            index: The owned SpellIndex to share.",
    ]),
    (W, 2114, "            conduit / conduit_id: The owner conduit of the lineage (peer in the", [
        "            conduit / conduit_id: The owner conduit of the SpellIndex (peer in the",
    ]),
    (W, 2148, "        # owner conduit. Reuse the spell eligibility on the lineage's active head.", [
        "        # owner conduit. Reuse the spell eligibility on the index's selected spell.",
    ]),
    (W, 2206, "        # Map every member of the lineage as a per-member spell contract of the", [
        "        # Map every member of the SpellIndex as a per-member spell contract of the",
    ]),
    # _get_index_links.
    (W, 2279, "        through any of this ward's contracts. The owner uses this to emit lineage", [
        "        through any of this ward's contracts. The owner uses this to emit SpellIndex",
    ]),
    # _emit_index_notch.
    (W, 2331, "        Owner-side emission for a notch on an index-linked lineage. For every", [
        "        Owner-side emission for a notch of a SpellIndex shared by index link. For every",
    ]),
    (W, 2335, "        receivers follow the lineage. Version-anchored borrowers are handled", [
        "        receivers follow the index's selected spell. Version-anchored borrowers are handled",
    ]),
    (W, 2344, "            index: The notched lineage.", [
        "            index: The notched SpellIndex.",
    ]),
    # _emit_index_destroy.
    (W, 2393, "        Owner-side emission when an index-linked lineage is destroyed: for every", [
        "        Owner-side emission when a SpellIndex shared by index link is destroyed: for every",
    ]),
    (W, 2397, "        subscription to a dead lineage.", [
        "        subscription to a dead SpellIndex.",
    ]),
    (W, 2436, "        # Record: the destroyed lineage's subscriptions left these contracts.", [
        "        # Record: the destroyed index's subscriptions left these contracts.",
    ]),
    # _contract_member_spell.
    (W, 2453, "        contracted copy -- active if the member is the lineage's active head, parked", [
        "        contracted copy -- active if the member is the index's selected spell, parked",
    ]),
    # _emit_index_member_added / _emit_index_member_removed.
    (W, 2523, "        Owner-side emission when a member is added to an index-linked lineage: for", [
        "        Owner-side emission when a member is added to a SpellIndex shared by index link: for",
    ]),
    (W, 2528, "            index: The lineage that gained a member.", [
        "            index: The SpellIndex that gained a member.",
    ]),
    (W, 2561, "        Owner-side emission when a member leaves an index-linked lineage: for every", [
        "        Owner-side emission when a member leaves a SpellIndex shared by index link: for every",
    ]),
    (W, 2566, "            index_id: Stable id of the lineage that lost a member.", [
        "            index_id: Stable id of the SpellIndex that lost a member.",
    ]),
    # _remove_root_from_contracts: the source tag is a root spell's spell_id.
    (W, 2785, "        lineage. This helper removes one `root_spell_id` source from matching", [
        "        spell. This helper removes one `root_spell_id` source from matching",
    ]),
    # _link_spell_dependencies' walk.
    (W, 2925, "            Depth-first dependency contracting walk for one root lineage.", [
        "            Depth-first dependency contracting walk for one root spell.",
    ]),
    # Bulk wrappers.
    (W, 3157, "        applies the single-spell lineage-aware add path repeatedly and returns", [
        "        applies the single-spell, SpellIndex-aware add path repeatedly and returns",
    ]),
    (W, 3363, "        lineage/source-aware removal semantics and cleanup behavior as the", [
        "        SpellIndex- and source-aware removal semantics and cleanup behavior as the",
    ]),
    # _get_all_spells_in_contracts (an index question; resolving each row's index is right).
    (W, 3498, "              so if the lineage has mutated, we get the **current** spell object.", [
        "              so if the index's selected spell has moved, we get the **current** spell object.",
    ]),
    (W, 3504, "            - Returns the current visible version for each contracted lineage,", [
        "            - Returns the current visible version for each contracted SpellIndex,",
    ]),
    (W, 3539, "                        # lineage-based resolution", [
        "                        # SpellIndex-based resolution",
    ]),
    # _get_spell_in_contracts (behaviour described as it is today; the owner's open finding).
    (W, 3597, "        This now behaves in a lineage-aware way:", [
        "        This now resolves through each Detail's SpellIndex:",
    ]),
    (W, 3599, "            * spell_id may be ANY version SHA belonging to the lineage.", [
        "            * spell_id may be ANY version SHA in a contracted spell's SpellIndex.",
    ]),
    (W, 3612, "            lineage, not necessarily the historical version string the caller", [
        "            SpellIndex, not necessarily the historical version string the caller",
    ]),
    (W, 3631, "                    # O(1) first: the detail contracted for exactly this version. The lineage walk runs", [
        "                    # O(1) first: the detail contracted for exactly this version. The index walk runs",
    ]),
    (W, 3632, "                    # only when the id is another version of a contracted lineage; every detail whose index", [
        "                    # only when the id is another version in a contracted SpellIndex; every detail whose index",
    ]),
    # _transfer_spell_ownership Args (TransferOfOwnership gates the moved SpellIndex's state).
    (W, 3820, "            invalidate_after_transfer: If True, mark lineage dirty after transfer.", [
        "            invalidate_after_transfer: If True, mark the moved SpellIndex dirty after transfer.",
    ]),
    (W, 3821, "            mark_dependencies_dirty: If True, mark dependency lineages dirty (even if not moved).", [
        "            mark_dependencies_dirty: If True, mark the dependencies' indexes dirty (even if not moved).",
    ]),
]
