"""Hand edits, batch 12: the ward contract vocabulary, the crystals, the Nexus views, two errors (melder_1, 2026-10-18).

Each occurrence read in its class or method and classified. Permissions are bound on each spell and a Detail
carries the permission granted for one spell_id, so the ward vocabulary's "lineage" is the spell: permissions.py,
policies.py, contract_types.py and detail_reason.py say spell, and contract.py's maps hold Details per spell_id and
IndexDetails per SpellIndex (an index link follows the index's selected spell); its source tagging records root
spell ids (`Detail.sources`). The contract crystal's index-detail rows are SpellIndex subscriptions; the
SpellIndexCrystal records which parked members sit in which SpellIndex; a cluster's shares are root SpellIndex ids
per owner (`shared_spells` rows of {owner_conduit_id, index_id}). The Nexus views' "lineage" is a spell index id
(the ACL's `spell_index_id` sets, `list_index_ids`, `describe_index_groups`). SpellbookValidationError's gating
warning holds a spell's SpellIndex state gated (Phase 4 sets it through `get_by_index_id`); SpellSpaceScopeError's
"lineages" are spells bound `unique_per_spell_space`. Not edited, mixed line endings: frame_viewer.py 3637 and 6486
and view_spell.py 854, 1731 and 1732 (all SpellIndex meaning; the ViewFrame and ViewSpell docstrings they mirror
already say "spell index"). Kept (diagnostic codes): "lineage_conduit_conflict", "root_lineage_conflict",
"root_lineage_mismatch". Kept (conduit scope tree): the conduit crystal's role and lineage_ancestors, the
crystallizer's "lineage changes" to quiesce during a live restore, conduit_hierarchy, persistence_crystal,
persistence_profile, the conduit descriptor payload's and record's lineage depth and root, the frame descriptor
manager, the views' conduit-record lineage grouping and root lineage, and the static viewer's lesser lineage. Kept
(neither meaning): the ACL configuration chain's revision lineage, and IDBuilder's and ULID_Factory's dotted
ownership-chain ("lineage") ids.
"""
W = "src/melder/aether/conduit/conduit_ward/"
PERM = W + "permissions/permissions.py"
POL = W + "policies/policies.py"
CON = W + "contract/contract.py"
CT = W + "contract/contract_types/contract_types.py"
DR = W + "contract/detail_reason.py"
CRY = "src/melder/crystallizer/crystals/"
NX = "src/melder/nexus/"
ERR = "src/melder/utilities/custom_exceptions/"

EDITS = [
    # permissions.py
    (PERM, 5, "    Capability ceiling for a spell lineage in ward-local and contracted views.", [
        "    Capability ceiling for a spell in ward-local and contracted views.",
    ]),
    (PERM, 12, "      that lineage", [
        "      that spell",
    ]),
    (PERM, 15, "    ward logic deliberately never escalates a contracted lineage beyond the", [
        "    ward logic deliberately never escalates a contracted spell beyond the",
    ]),
    (PERM, 19, "      the lineage may be resolved and inspected through a contract, but it", [
        "      the spell may be resolved and inspected through a contract, but it",
    ]),
    (PERM, 24, "      the lineage may participate in creation-capable dependency resolution and", [
        "      the spell may participate in creation-capable dependency resolution and",
    ]),
    (PERM, 28, "      the lineage should not be contractable in normal flows. The ward treats", [
        "      the spell should not be contractable in normal flows. The ward treats",
    ]),
    (PERM, 37, "        The PER-LINEAGE half of the ward vocabulary, paired with `Policies`", [
        "        The PER-SPELL half of the ward vocabulary, paired with `Policies`",
    ]),
    (PERM, 39, "        is the load-bearing invariant: a contracted lineage is never granted", [
        "        is the load-bearing invariant: a contracted spell is never granted",
    ]),
    (PERM, 49, "        the lineage cannot act as a creation-capable dependency when work", [
        "        the spell cannot act as a creation-capable dependency when work",
    ]),
    (PERM, 54, "        lineages, and a `read`-only default would make the cluster inert.", [
        "        spells, and a `read`-only default would make the cluster inert.",
    ]),
    (PERM, 59,
     "        access: public. Capability ceiling for a lineage: read (resolve/inspect only), create", [
         "        access: public. Capability ceiling for a spell: read (resolve/inspect only), create",
     ]),
    # policies.py
    (POL, 12, "    - whether it may accept inbound borrowed lineages", [
        "    - whether it may accept inbound borrowed spells",
    ]),
    (POL, 27, "          expose local lineages without requiring per-spell whitelist flags and", [
        "          expose local spells without requiring per-spell whitelist flags and",
    ]),
    (POL, 47, "        `Permissions` is the PER-LINEAGE ceiling (what a peer may do with a", [
        "        `Permissions` is the PER-SPELL ceiling (what a peer may do with a",
    ]),
    (POL, 51, "        lineage's own permission allows the capability.", [
        "        spell's own permission allows the capability.",
    ]),
    (POL, 60, "        it lets a lineage marked `Permissions.block` pass the ward gate. That", [
        "        it lets a spell marked `Permissions.block` pass the ward gate. That",
    ]),
    # contract.py
    (CON, 24, "    which lineages are shared and with what permissions. Each side can grant", [
        "    which spells and spell indexes are shared and with what permissions. Each side can grant",
    ]),
    (CON, 30, "        - lineage-aware source tagging used by dependency-linked rollback", [
        "        - root-spell source tagging used by dependency-linked rollback",
    ]),
    (CON, 71, "        a `SpellIndex`, so the borrower follows the lineage HEAD rather than a", [
        "        a `SpellIndex`, so the borrower follows the index's selected spell rather than a",
    ]),
    (CON, 121, "        # Index-link details: per-ward maps of index_id -> IndexDetail (lineage", [
        "        # Index-link details: per-ward maps of index_id -> IndexDetail (SpellIndex",
    ]),
    (CON, 274, "            # Merge sources if this lineage already exists with the same permissions.", [
        "            # Merge sources if this spell_id already has a Detail with the same permissions.",
    ]),
    # contract_types.py
    (CT, 9, "    map describing which spell lineages it exposed or borrowed in that", [
        "    map describing which spells it exposed or borrowed in that",
    ]),
    (CT, 13, "    This matters during reconciliation and rollback because the same lineage", [
        "    This matters during reconciliation and rollback because the same spell",
    ]),
    (CT, 17, "      the owning ward is the source of the lineage. This detail records a", [
        "      the owning ward is the source of the spell. This detail records a",
    ]),
    (CT, 21, "      the owning ward is the borrower. This detail records a lineage that came", [
        "      the owning ward is the borrower. This detail records a spell that came",
    ]),
    (CT, 39, "        lineage appears as `initiated` on the granting side and `received` on", [
        "        spell appears as `initiated` on the granting side and `received` on",
    ]),
    # detail_reason.py
    (DR, 7, "    The ward uses this enum to distinguish directly shared lineages from", [
        "    The ward uses this enum to distinguish directly shared spells from",
    ]),
    (DR, 26, '        does it exist" for every lineage inside a contract.', [
        '        does it exist" for every Detail inside a contract.',
    ]),
    # contract_crystal.py
    (CRY + "contract_crystal.py", 12, "        which conduits are linked, which spells/lineages are shared into", [
        "        which conduits are linked, which spells and spell indexes are shared into",
    ]),
    (CRY + "contract_crystal.py", 21,
     "        its peer; index-detail rows describe lineage subscriptions. The two", [
         "        its peer; index-detail rows describe SpellIndex subscriptions. The two",
     ]),
    (CRY + "contract_crystal.py", 50,
     "        RELATIONSHIP: which conduits are linked and which spells/lineages are", [
         "        RELATIONSHIP: which conduits are linked and which spells and spell indexes are",
     ]),
    (CRY + "contract_crystal.py", 112, "                Plain-dict projections of ward A's lineage subscriptions.", [
        "                Plain-dict projections of ward A's SpellIndex subscriptions.",
    ]),
    (CRY + "contract_crystal.py", 114, "                Plain-dict projections of ward B's lineage subscriptions.", [
        "                Plain-dict projections of ward B's SpellIndex subscriptions.",
    ]),
    # spell_index_crystal.py
    (CRY + "spell_index_crystal.py", 12, "        (which parked members ride which lineage, and which member is", [
        "        (which parked members sit in which SpellIndex, and which member is",
    ]),
    (CRY + "spell_index_crystal.py", 14, "        regroup staged members onto the right lineage and transfer of", [
        "        regroup staged members onto the right SpellIndex and transfer of",
    ]),
    (CRY + "spell_index_crystal.py", 48,
     "        index-owned GROUPING state: which parked members ride which lineage and", [
         "        index-owned GROUPING state: which parked members sit in which SpellIndex and",
     ]),
    (CRY + "spell_index_crystal.py", 50,
     "        the right lineage, and transfer-of-ownership uses it to re-anchor a moved", [
         "        the right SpellIndex, and transfer-of-ownership uses it to re-anchor a moved",
     ]),
    # cluster_crystal.py
    (CRY + "cluster_crystal.py", 12, "        contracts): named member groups with shared lineage roots and an", [
        "        contracts): named member groups with shared root spell indexes and an",
    ]),
    (CRY + "cluster_crystal.py", 47,
     "        (`ContractCrystal`), clusters are named member groups with shared lineage", [
         "        (`ContractCrystal`), clusters are named member groups with shared root spell",
     ]),
    (CRY + "cluster_crystal.py", 48,
     "        roots and an optional elected leader. This twin records membership,", [
         "        indexes and an optional elected leader. This twin records membership,",
     ]),
    # crystallizer.py
    ("src/melder/crystallizer/crystallizer.py", 1225,
     "            both sides' spell Details and lineage subscriptions - into", [
         "            both sides' spell Details and SpellIndex subscriptions - into",
     ]),
    # Nexus views and ACL
    (NX + "rift/frame_viewer/view_multiframe.py", 1477,
     "            - Groups by spell INDEX id, so each group is one version LINEAGE rather than", [
         "            - Groups by spell INDEX id, so each group is one SpellIndex's versions rather than",
     ]),
    (NX + "rift/frame_viewer/view_multiframe.py", 2405, "              one lineage.", [
        "              one SpellIndex.",
    ]),
    (NX + "rift/frame_viewer/view_frame.py", 1434,
     "              Deduplicate yourself if you want distinct lineages.", [
         "              Deduplicate yourself if you want distinct spell indexes.",
     ]),
    (NX + "acl/frame_acl_compiled_access_surface.py", 483,
     "            Tuple[str, ...]: Visible stable spell lineage ids.", [
         "            Tuple[str, ...]: Visible stable SpellIndex ids.",
     ]),
    (NX + "acl/frame_acl_compiled_access_surface.py", 505, "            Tuple[str, ...]: Enabled spell lineage ids.", [
        "            Tuple[str, ...]: Enabled SpellIndex ids.",
    ]),
    (NX + "acl/frame_acl_compiler.py", 408, "              runtime consumers can target lineages directly.", [
        "              runtime consumers can target spell indexes directly.",
    ]),
    # errors
    (ERR + "spellbook_validation_error.py", 37,
     "        counted here, except one that holds a spell's lineage gated (a lost", [
         "        counted here, except one that holds a spell's SpellIndex gated (a lost",
     ]),
    (ERR + "spellbook_validation_error.py", 65, "          lineage is gated, so they are its reason (2026-10-16).", [
        "          SpellIndex is gated, so they are its reason (2026-10-16).",
    ]),
    (ERR + "spellbook_validation_error.py", 142,
     "    # Phase-4 warnings that hold a lineage `gated` (`CompilerPhase4.run`): a spell refused only because of one lists", [
         "    # Phase-4 warnings that hold a SpellIndex `gated` (`CompilerPhase4.run`): a spell refused only because of one lists",
     ]),
    (ERR + "spell_space_scope_error.py", 23,
     "        REFUSES `unique_per_spell_space` lineages rather than inventing a scope,", [
         "        REFUSES `unique_per_spell_space` spells rather than inventing a scope,",
     ]),
]
