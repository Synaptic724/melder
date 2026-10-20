"""Hand edits, batch 10: conduit/conduit_cluster.py and the Phase 6 system validation strategies (melder_1, 2026-10-18).

conduit_cluster.py: members share their shareable root spells, recorded by SpellIndex (40, 1502); every other use is a
member root's conduit scope tree being drained or resolved (kept), and "conduit_lineage_gate_ops" is an identifier.
Phase 6: a SpellSystemIndex node's `lineage_id` is `SpellIndex.id` (spell_system_node.py), so the strategies' prose
means the SpellIndex. Kept: the identifiers and file/class names (`LineageAlignmentStrategy`, `lineage_id`,
`root_lineage_id`, `lineage_to_spell_ids`, ...), the diagnostic codes ("root_lineage_mismatch",
"lineage_conduit_conflict", "lineage_version_conflict", "root_lineage_conflict") and detail keys, and the
scope-ordering comment's "unique/lineage/conduit/cluster" (the existences).
"""
V = "src/melder/aether/spellbook/spell_compiler/system/validation/"
CL = "src/melder/aether/conduit/conduit_cluster.py"
REG_OLD = "            spell_system_states: SpellSystemStates registry for topology and lineage data."
REG_NEW = "            spell_system_states: SpellSystemStates registry for topology and SpellIndex state data."

EDITS = [
    (CL, 40, "    shareable root `SpellIndex` lineages to one another, so every member can", [
        "    shareable root spell indexes to one another, so every member can",
    ]),
    (CL, 1502, "                member ids, and shared-root lineage ids grouped by owner.", [
        "                member ids, and shared root SpellIndex ids grouped by owner.",
    ]),

    # lineage_alignment_strategy.py
    (V + "lineage_alignment_strategy.py", 32, "    Guard that root-blueprint lineage metadata agrees with the system index.", [
        "    Guard that root-blueprint SpellIndex metadata agrees with the system index.",
    ]),
    (V + "lineage_alignment_strategy.py", 34, "    Root blueprints are spell_id-rooted, but they can still carry lineage", [
        "    Root blueprints are spell_id-rooted, but they can still carry SpellIndex",
    ]),
    (V + "lineage_alignment_strategy.py", 36, "    the optional root-lineage ids embedded in the blueprints stay aligned with", [
        "    the optional root SpellIndex ids embedded in the blueprints stay aligned with",
    ]),
    (V + "lineage_alignment_strategy.py", 37, "    the lineage ids tracked on the corresponding `SpellSystemIndex` nodes.", [
        "    the SpellIndex ids (`lineage_id`) tracked on the corresponding `SpellSystemIndex` nodes.",
    ]),
    (V + "lineage_alignment_strategy.py", 40, "        - Emits `root_lineage_mismatch` when a root lineage id disagrees with", [
        "        - Emits `root_lineage_mismatch` when a root SpellIndex id disagrees with",
    ]),
    (V + "lineage_alignment_strategy.py", 42, "        - Skips checks when a blueprint intentionally lacks lineage metadata.", [
        "        - Skips checks when a blueprint intentionally lacks SpellIndex metadata.",
    ]),
    (V + "lineage_alignment_strategy.py", 59, "        Validate that blueprint root lineage ids match index lineage ids.", [
        "        Validate that blueprint root SpellIndex ids match the index nodes' SpellIndex ids.",
    ]),
    (V + "lineage_alignment_strategy.py", 62, "            Ensure the Phase-5 blueprint lineage metadata stays aligned with", [
        "            Ensure the Phase-5 blueprint SpellIndex metadata stays aligned with",
    ]),
    (V + "lineage_alignment_strategy.py", 63, "            the SpellSystemIndex lineage ids used for system tracking.", [
        "            the SpellSystemIndex nodes' SpellIndex ids used for system tracking.",
    ]),
    (V + "lineage_alignment_strategy.py", 65, "            - Emits root_lineage_mismatch when the lineage ids differ.", [
        "            - Emits root_lineage_mismatch when the SpellIndex ids differ.",
    ]),
    (V + "lineage_alignment_strategy.py", 66, "            - Omits diagnostics when root lineage metadata is absent.", [
        "            - Omits diagnostics when root SpellIndex metadata is absent.",
    ]),
    (V + "lineage_alignment_strategy.py", 73, REG_OLD, [REG_NEW]),

    # ownership_consistency_strategy.py
    (V + "ownership_consistency_strategy.py", 32, "    Guard that a lineage does not claim conflicting conduit ownership.", [
        "    Guard that a SpellIndex does not claim conflicting conduit ownership.",
    ]),
    (V + "ownership_consistency_strategy.py", 36, "    validation. A lineage that points at multiple concrete conduit owners at", [
        "    validation. A SpellIndex that points at multiple concrete conduit owners at",
    ]),
    (V + "ownership_consistency_strategy.py", 38, "    lineage id and checks whether the non-None owner set stays singular before", [
        "    SpellIndex id and checks whether the non-None owner set stays singular before",
    ]),
    (V + "ownership_consistency_strategy.py", 39, "    later validation or change-control logic treats that lineage as belonging to", [
        "    later validation or change-control logic treats that SpellIndex as belonging to",
    ]),
    (V + "ownership_consistency_strategy.py", 60, "            Catch lineages whose visible versions disagree about which conduit", [
        "            Catch spell indexes whose visible versions disagree about which conduit",
    ]),
    (V + "ownership_consistency_strategy.py", 69, "            - Emits one ERROR diagnostic per conflicting lineage and includes", [
        "            - Emits one ERROR diagnostic per conflicting SpellIndex and includes",
    ]),
    (V + "ownership_consistency_strategy.py", 78, REG_OLD, [REG_NEW]),

    # lineage_version_conflict_strategy.py
    (V + "lineage_version_conflict_strategy.py", 32, "    Guard that one root DAG does not mix multiple versions of the same lineage.", [
        "    Guard that one root DAG does not mix multiple versions of the same SpellIndex.",
    ]),
    (V + "lineage_version_conflict_strategy.py", 35, "    coherent runtime slice. If the same lineage appears multiple times under a", [
        "    coherent runtime slice. If the same SpellIndex appears multiple times under a",
    ]),
    (V + "lineage_version_conflict_strategy.py", 38, "    strategy checks the blueprint DAG against the index lineage map and turns", [
        "    strategy checks the blueprint DAG against the index's SpellIndex ids and turns",
    ]),
    (V + "lineage_version_conflict_strategy.py", 57, "        Validate that each root DAG contains at most one version per lineage.", [
        "        Validate that each root DAG contains at most one version per SpellIndex.",
    ]),
    (V + "lineage_version_conflict_strategy.py", 61, "            of the same logical spell lineage.", [
        "            of the same SpellIndex.",
    ]),
    (V + "lineage_version_conflict_strategy.py", 64, "              system index as the source of lineage identity.", [
        "              system index as the source of SpellIndex identity.",
    ]),
    (V + "lineage_version_conflict_strategy.py", 65, "            - Missing index nodes and lineage-less nodes are ignored here", [
        "            - Missing index nodes and nodes without a SpellIndex id are ignored here",
    ]),
    (V + "lineage_version_conflict_strategy.py", 67, "            - Emits one ERROR diagnostic per conflicting lineage within a root,", [
        "            - Emits one ERROR diagnostic per conflicting SpellIndex within a root,",
    ]),
    (V + "lineage_version_conflict_strategy.py", 77, REG_OLD, [REG_NEW]),

    # root_lineage_conflict_strategy.py
    (V + "root_lineage_conflict_strategy.py", 32, "    Guard that one lineage does not fan out into multiple structural roots.", [
        "    Guard that one SpellIndex does not fan out into multiple structural roots.",
    ]),
    (V + "root_lineage_conflict_strategy.py", 35, "    the frame. If multiple root spell ids map back to the same lineage, the", [
        "    the frame. If multiple root spell ids map back to the same SpellIndex, the",
    ]),
    (V + "root_lineage_conflict_strategy.py", 37, "    family at once. This strategy detects that root-lineage split before the", [
        "    family at once. This strategy detects that root SpellIndex split before the",
    ]),
    (V + "root_lineage_conflict_strategy.py", 56, "        Validate that each lineage maps to at most one root spell id.", [
        "        Validate that each SpellIndex maps to at most one root spell id.",
    ]),
    (V + "root_lineage_conflict_strategy.py", 60, "            for one logical spell lineage.", [
        "            for one SpellIndex.",
    ]),
    (V + "root_lineage_conflict_strategy.py", 62, "            - Uses blueprint keys as the root set and resolves lineage identity", [
        "            - Uses blueprint keys as the root set and resolves SpellIndex identity",
    ]),
    (V + "root_lineage_conflict_strategy.py", 64, "            - Missing index nodes and lineage-less roots are ignored here so", [
        "            - Missing index nodes and roots without a SpellIndex id are ignored here so",
    ]),
    (V + "root_lineage_conflict_strategy.py", 75, REG_OLD, [REG_NEW]),

    # contracted_version_drift_strategy.py
    (V + "contracted_version_drift_strategy.py", 31,
     "    Guard that the visible system index does not drift onto stale lineage versions.", [
         "    Guard that the visible system index does not drift onto stale versions of a SpellIndex.",
     ]),
    (V + "contracted_version_drift_strategy.py", 34,
     "    against the currently visible spell versions for each lineage. It is aimed", [
         "    against the currently visible spell versions for each SpellIndex. It is aimed",
     ]),
    (V + "contracted_version_drift_strategy.py", 54, "        Validate that index nodes align with visible lineage versions.", [
        "        Validate that index nodes align with the visible versions of each SpellIndex.",
    ]),
    (V + "contracted_version_drift_strategy.py", 58, "            spell_ids for a lineage visible in the spellbook.", [
        "            spell_ids for a SpellIndex visible in the spellbook.",
    ]),
    (V + "contracted_version_drift_strategy.py", 68, REG_OLD, [REG_NEW]),

    # identity_mixing_strategy.py
    (V + "identity_mixing_strategy.py", 31, "    Guard that dependency edges stay on spell_ids rather than lineage ids.", [
        "    Guard that dependency edges stay on spell_ids rather than SpellIndex ids.",
    ]),
    (V + "identity_mixing_strategy.py", 34, "    lineage ids are DevOps/control-plane identity. If a dependency edge starts", [
        "    SpellIndex ids are DevOps/control-plane identity. If a dependency edge starts",
    ]),
    (V + "identity_mixing_strategy.py", 35, "    pointing at lineage ids directly, later planning and resolution become", [
        "    pointing at SpellIndex ids directly, later planning and resolution become",
    ]),
    (V + "identity_mixing_strategy.py", 54, "        Validate that dependency ids are spell_ids, not lineage ids.", [
        "        Validate that dependency ids are spell_ids, not SpellIndex ids.",
    ]),
    (V + "identity_mixing_strategy.py", 57, "            Catch dependency edges that reference lineage ids directly, which", [
        "            Catch dependency edges that reference SpellIndex ids directly, which",
    ]),
    (V + "identity_mixing_strategy.py", 60, "            - Emits an error for each dependency id that matches a lineage id.", [
        "            - Emits an error for each dependency id that matches a SpellIndex id.",
    ]),
    (V + "identity_mixing_strategy.py", 67, REG_OLD, [REG_NEW]),

    # The other strategies: the shared Args line, and two sentences.
    (V + "visibility_gap_strategy.py", 70, REG_OLD, [REG_NEW]),
    (V + "topology_dependency_mismatch_strategy.py", 67, REG_OLD, [REG_NEW]),
    (V + "strategy_base.py", 67, "                SpellSystemStates registry for topology and lineage data.", [
        "                SpellSystemStates registry for topology and SpellIndex state data.",
    ]),
    (V + "root_viability_strategy.py", 71, REG_OLD, [REG_NEW]),
    (V + "root_scale_limit_strategy.py", 103, REG_OLD, [REG_NEW]),
    (V + "root_reachability_strategy.py", 68, REG_OLD, [REG_NEW]),
    (V + "root_coverage_strategy.py", 72, REG_OLD, [REG_NEW]),
    (V + "missing_phase4_strategy.py", 71, REG_OLD, [REG_NEW]),
    (V + "index_coverage_strategy.py", 69, REG_OLD, [REG_NEW]),
    (V + "graph_consistency_strategy.py", 73, REG_OLD, [REG_NEW]),
    (V + "dependency_type_sanity_strategy.py", 75, REG_OLD, [REG_NEW]),
    (V + "contract_graph_cycle_strategy.py", 69, REG_OLD, [REG_NEW]),
    (V + "index_dependency_sanity_strategy.py", 36, "    Before later strategies reason about reachability, lineage, or root", [
        "    Before later strategies reason about reachability, SpellIndex identity, or root",
    ]),
    (V + "index_dependency_sanity_strategy.py", 71, REG_OLD, [REG_NEW]),
    (V + "broken_spell_in_dag_strategy.py", 62, "              roots when its lineage is shared across those rooted DAGs.", [
        "              roots when that spell is shared across those rooted DAGs.",
    ]),
    (V + "broken_spell_in_dag_strategy.py", 69, REG_OLD, [REG_NEW]),
    (V + "scope_ordering_strategy.py", 70, REG_OLD, [REG_NEW]),
]
