"""Hand edits, batch 05: conduit_ward/transfer/transfer_of_ownership.py (melder_1, 2026-10-18).

A transfer moves a spell's whole SpellIndex (every member, active and parked) to another owner, and its
SpellSystemStates bookkeeping is per index; the docstrings and comments called that index a lineage. Kept: the
`unique_per_conduit_lineage` comment at 416-424 and "the lesser lineage" at 852 (the conduit scope tree); the
identifiers `_mark_lineage_disabled`, `_mark_lineage_dirty`, `_conduit_has_impacted_lineage` and `impacted_lineages`
(404, 739, 792, 795, 807, 865, 870, 873, 884, 892, 897, 901, 2080, 2104); and the RuntimeError text at 921 ("Failed to
register lineage for transfer disable.") - runtime strings are listed for the owner, not changed in this pass.
"""
T = "src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py"

EDITS = [
    # Class docstring.
    (T, 42, "    Control-plane helper that migrates a spell lineage between conduit owners.", [
        "    Control-plane helper that migrates a spell's SpellIndex between conduit owners.",
    ]),
    (T, 51, "    - `preflight()` performs a read-only inventory of the lineage, its", [
        "    - `preflight()` performs a read-only inventory of the SpellIndex, its",
    ]),
    (T, 55, "      lineage, flipping the canonical registry/spellbook ownership under lock,", [
        "      SpellIndex, flipping the canonical registry/spellbook ownership under lock,",
    ]),
    (T, 61, "    - Transfer moves canonical lineage ownership plus conduit-owned runtime", [
        "    - Transfer moves canonical SpellIndex ownership plus conduit-owned runtime",
    ]),
    (T, 64, "    - If a spellspace-scoped lineage is transferred while an old source", [
        "    - If the SpellIndex of a spellspace-scoped spell is transferred while an old source",
    ]),
    (T, 97, "        `ConduitWard` grants and revokes access to a lineage someone else owns;", [
        "        `ConduitWard` grants and revokes access to a spell or SpellIndex someone else owns;",
    ]),
    (T, 105, "        then does `execute()` disable the lineage, flip ownership under guard,", [
        "        then does `execute()` disable the SpellIndex, flip ownership under guard,",
    ]),
    (T, 123, "        access: internal. Control-plane helper that migrates a spell lineage between conduit", [
        "        access: internal. Control-plane helper that migrates a spell's SpellIndex between conduit",
    ]),
    # __init__.
    (T, 167, "        whether owned dependencies move with the root lineage, whether existing", [
        "        whether owned dependencies move with the root spell, whether existing",
    ]),
    (T, 168, "        shares are force-unshared or repointed, and whether impacted lineages", [
        "        shares are force-unshared or repointed, and whether impacted indexes",
    ]),
    (T, 173, "            source_conduit: Conduit that currently owns the root lineage.", [
        "            source_conduit: Conduit that currently owns the spell's SpellIndex.",
    ]),
    (T, 176, "                lineage to move.", [
        "                SpellIndex to move.",
    ]),
    (T, 177, "            move_creations: When true, move the lineage's instances from the", [
        "            move_creations: When true, move the index members' instances from the",
    ]),
    (T, 184, "            include_dependencies: When true, transfer owned dependency lineages", [
        "            include_dependencies: When true, transfer the owned dependencies' indexes",
    ]),
    (T, 189, "            invalidate_after_transfer: When true, leave the moved lineage and", [
        "            invalidate_after_transfer: When true, leave the moved SpellIndex and",
    ]),
    (T, 193, "                lineages dirty so stale downstream state is not reused.", [
        "                indexes dirty so stale downstream state is not reused.",
    ]),
    # preflight / execute.
    (T, 290, "        Build a read-only transfer plan for the requested lineage.", [
        "        Build a read-only transfer plan for the requested SpellIndex.",
    ]),
    (T, 374, "        1. disable the lineage so callers cannot resolve it mid-transfer", [
        "        1. disable the SpellIndex so callers cannot resolve it mid-transfer",
    ]),
    (T, 379, "        5. leave the lineage gated/dirty or simply re-enable it according to", [
        "        5. leave the SpellIndex gated/dirty or simply re-enable it according to",
    ]),
    (T, 388, "        runtime view, the lineage is lifted back to a safe gated state, and the", [
        "        runtime view, the SpellIndex is lifted back to a safe gated state, and the",
    ]),
    (T, 443, "            # After successful transfer, move lineage back to gated/dirty so validation can clear it.", [
        "            # After successful transfer, move the SpellIndex back to gated/dirty so validation can clear it.",
    ]),
    # _require_dynamic_environment / _resolve_spell / _enumerate_borrowers / _deps_resolvable_on_target.
    (T, 517, "        the move depends on runtime contract teardown/repointing and lineage", [
        "        the move depends on runtime contract teardown/repointing and SpellIndex",
    ]),
    (T, 534, "        so it can inspect ownership, dependencies, creations, and lineage", [
        "        so it can inspect ownership, dependencies, creations, and SpellIndex",
    ]),
    (T, 596, "        Enumerate downstream runtime surfaces currently borrowing this lineage.", [
        "        Enumerate downstream runtime surfaces currently borrowing this spell or its SpellIndex.",
    ]),
    (T, 702, "        ids, the root lineage would arrive in a knowingly broken state.", [
        "        ids, the moved SpellIndex would arrive in a knowingly broken state.",
    ]),
    # _mark_lineage_dirty (name kept).
    (T, 741, "        Record a structural-change gate for one lineage in `SpellSystemStates`.", [
        "        Record a structural-change gate for one SpellIndex in `SpellSystemStates`.",
    ]),
    (T, 744, "        hard-disabling the lineage, it marks the lineage as structurally changed", [
        "        hard-disabling the SpellIndex, it marks the SpellIndex as structurally changed",
    ]),
    (T, 745, "        so later spell-crafter phases rerun before callers trust the lineage", [
        "        so later spell-crafter phases rerun before callers trust the SpellIndex",
    ]),
    (T, 749, "            spell_index: Lineage whose spell-system state should be marked dirty.", [
        "            spell_index: SpellIndex whose spell-system state should be marked dirty.",
    ]),
    # _gate_transfer_impacts / _collect_impacted_conduit_ids / _conduit_has_impacted_lineage (names kept).
    (T, 772, "        Dirty the moved lineage and every conduit that may now see changed", [
        "        Dirty the moved SpellIndex and every conduit that may now see changed",
    ]),
    (T, 775, "        The root lineage itself is structurally changed by the ownership flip,", [
        "        The moved SpellIndex itself is structurally changed by the ownership flip,",
    ]),
    (T, 778, "        lineage may all need to rerun later spell-crafter phases before their", [
        "        SpellIndex may all need to rerun later spell-crafter phases before their",
    ]),
    (T, 820, "          of the impacted lineages", [
        "          of the impacted indexes",
    ]),
    # The first "lineage" is the sweep for impacted indexes; "the lesser lineage" is the scope tree and stays.
    (T, 852, "        # lineage sweep never needs the lesser lineage (owner ruling, 2026-09-27).", [
        "        # impacted-index sweep never needs the lesser lineage (owner ruling, 2026-09-27).",
    ]),
    (T, 876, "        Check whether a conduit currently holds any lineage in the impacted", [
        "        Check whether a conduit currently holds any SpellIndex in the impacted",
    ]),
    # _mark_lineage_disabled (name kept).
    (T, 903, "        Hard-disable the lineage while the ownership flip is actively in flight.", [
        "        Hard-disable the SpellIndex while the ownership flip is actively in flight.",
    ]),
    (T, 906, "        successful move. During the critical transfer window the lineage should", [
        "        successful move. During the critical transfer window the SpellIndex should",
    ]),
    (T, 912, "            spell_index: Lineage being moved between conduit owners.", [
        "            spell_index: SpellIndex being moved between conduit owners.",
    ]),
    # _rollback_spellbook_move.
    (T, 989, "        partially moved target-side entries, restores lineage ownership pointers", [
        "        partially moved target-side entries, restores the index's ownership pointers",
    ]),
    (T, 996, "        the lineage after the failed move.", [
        "        the SpellIndex after the failed move.",
    ]),
    (T, 1000, "            src_book: Original owner spellbook that should regain the lineage.", [
        "            src_book: Original owner spellbook that should regain the SpellIndex.",
    ]),
    (T, 1002, "                lineage.", [
        "                SpellIndex.",
    ]),
    # Creations rollback / snapshot / registry probes.
    (T, 1131, "        target-side creations for the lineage, then restores the original", [
        "        target-side creations for the index's members, then restores the original",
    ]),
    (T, 1154, "        Capture the minimal transfer-recovery snapshot for this lineage.", [
        "        Capture the minimal transfer-recovery snapshot for this SpellIndex.",
    ]),
    (T, 1175, "        Check whether Aether already records this lineage under the conduit.", [
        "        Check whether Aether already records this SpellIndex under the conduit.",
    ]),
    (T, 1184, "            spell_index: Lineage key to look for in that registry.", [
        "            spell_index: SpellIndex key to look for in that registry.",
    ]),
    (T, 1186, "            bool: `True` when the lineage is already registered for the conduit.", [
        "            bool: `True` when the SpellIndex is already registered for the conduit.",
    ]),
    (T, 1215, "            bool: `True` when the spellbook currently contains the lineage.", [
        "            bool: `True` when the spellbook currently contains the SpellIndex.",
    ]),
    (T, 1328, "        lineage was exposed through any conduit clusters before transfer began.", [
        "        SpellIndex was exposed through any conduit clusters before transfer began.",
    ]),
    # _lift_disable.
    (T, 1390, '        The method does not "return to normal" blindly. It converts the lineage', [
        '        The method does not "return to normal" blindly. It converts the SpellIndex',
    ]),
    (T, 1394, "          lineage is trusted again, or", [
        "          SpellIndex is trusted again, or",
    ]),
    (T, 1399, "        lineage no longer looks mid-flight to downstream readers.", [
        "        SpellIndex no longer looks mid-flight to downstream readers.",
    ]),
    (T, 1402, "            spell_index: Lineage leaving the hard-disabled transfer state.", [
        "            spell_index: SpellIndex leaving the hard-disabled transfer state.",
    ]),
    (T, 1403, "            gated: Whether the lineage should remain blocked behind validation", [
        "            gated: Whether the SpellIndex should remain blocked behind validation",
    ]),
    # _flip_registry_and_spellbooks.
    (T, 1437, "        the lineage.", [
        "        the SpellIndex.",
    ]),
    (T, 1443, "        - spellbook-local ownership maps and lineage/risk registrations", [
        "        - spellbook-local ownership maps and SpellIndex/risk registrations",
    ]),
    # _move_creations / _migrate_inactive_members / _restamp.
    (T, 1562, "        the new owner build its own, it extracts the lineage's creation payload", [
        "        the new owner build its own, it extracts the index members' creation payload",
    ]),
    (T, 1581, "        # Migrate creations for every member of the lineage (active + inactive),", [
        "        # Migrate creations for every member of the SpellIndex (active + inactive),",
    ]),
    (T, 1637, "        Carry the lineage's INACTIVE members to the target spellbook.", [
        "        Carry the SpellIndex's INACTIVE members to the target spellbook.",
    ]),
    (T, 1639, "        Transfer of ownership moves an index (lineage). `_flip_registry_and_spellbooks`", [
        "        Transfer of ownership moves a whole SpellIndex. `_flip_registry_and_spellbooks`",
    ]),
    (T, 1782, "            Make the owner stamp follow the lineage both ways (2026-10-15): the", [
        "            Make the owner stamp follow the SpellIndex both ways (2026-10-15): the",
    ]),
    (T, 1838, "            - A removed pool is cleaned. It is empty: the lineage is disabled for", [
        "            - A removed pool is cleaned. It is empty: the SpellIndex is disabled for",
    ]),
    # _unshare_everywhere.
    (T, 1859, "        is enabled. After the root lineage changes owners, peers that used to", [
        "        is enabled. After the moved SpellIndex changes owners, peers that used to",
    ]),
    # Dependencies.
    (T, 2028, "        Transfer source-owned dependency lineages alongside the root lineage.", [
        "        Transfer the source-owned dependencies' indexes alongside the root spell's SpellIndex.",
    ]),
    (T, 2077, "                # Mark dependency lineage dirty if requested", [
        "                # Mark the dependency's SpellIndex dirty if requested",
    ]),
    (T, 2086, "        Leave dependencies in place but force their lineages back through", [
        "        Leave dependencies in place but force their indexes back through",
    ]),
    (T, 2091, "        lineages, it marks them dirty so downstream runtime state is not", [
        "        indexes, it marks them dirty so downstream runtime state is not",
    ]),
    (T, 2095, "            deps: Dependency spell ids whose lineages should be marked dirty.", [
        "            deps: Dependency spell ids whose indexes should be marked dirty.",
    ]),
    # Change intent and incidents.
    (T, 2116, "        surrounding governance layer that a lineage is about to undergo an", [
        "        surrounding governance layer that a SpellIndex is about to undergo an",
    ]),
    (T, 2125, "            summary: Preflight payload that describes the lineage, endpoints,", [
        "            summary: Preflight payload that describes the SpellIndex, endpoints,",
    ]),
    (T, 2161, "            spell_index: Lineage whose pending transfer record should be", [
        "            spell_index: SpellIndex whose pending transfer record should be",
    ]),
    (T, 2176, "        transfer first tries to restore a coherent lineage state; this helper", [
        "        transfer first tries to restore a coherent SpellIndex state; this helper",
    ]),
    (T, 2183, "                lineage and participants.", [
        "                SpellIndex and participants.",
    ]),
]
