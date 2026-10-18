"""Hand edits, batch 11: the compiler and system phases, the control plane, the frame (melder_1, 2026-10-18).

Each occurrence read in its method and classified. SpellIndex meaning (rewritten): a SpellSystemNode's `lineage_id`
is its SpellIndex's id (Phase 5 fills it from `SpellSystemState.spell_index_id`); a blueprint's `root_lineage_id` is
the root spell's SpellIndex id (LineageAlignmentStrategy compares the two); SpellSystemStates, SpellSystemState,
SpellState and the structural snapshot keep state per SpellIndex (`get_by_index_id`); Phase 4 gates that state;
change control keys pending changes by `spell_index.id`; an incident's `spell_index_id`; the frame's registries of
spell indexes; `with_permissions` stages one spell's permissions; a SpellContract's consumer spell revalidates.
SpellSystemValidationSystem records per-conduit resolution validity (its own Contract says global structural
validity is not modified), so its "lineage validity" lines now say that. Kept (identifiers, slot names, runtime
messages, data keys): `lineage_id`, `_lineage_id`, `root_lineage_id`, "lineage_id must not be None.",
"phase5_root_lineage_id", `Meld._ensure_lineage_resolvable`. Not edited: compiler_phase_5.py 280 ("Resolves
lineage ids from SpellSystemStates.", SpellIndex meaning) - the file has mixed line endings. Kept (conduit scope
tree): the `unique_per_conduit_lineage` routes and stores (generalized/solo compilers, site plan lowering, lane
plan, manifests, artifact processor, matrix), the conduit lineage gates of the notch, index-move, transfer and
cluster-leader strategies and the mediator, `conduit_lineage_gate_ops`, the lesser lineage in aether.py and
conduit_cloud.py, conduit_pool, cluster_creations, spell_space, conduit_state, creation_context, existence,
creation_gate and the spellbinder's "Scoped to Lineage".
"""
SYS = "src/melder/aether/spellbook/spell_compiler/system/"
PH = "src/melder/aether/spellbook/spell_compiler/phases/"
DEV = "src/melder/aether/aetheric_frame/dev_ops/"
SSS = DEV + "spell_system_states/"
CCM = DEV + "change_control_manager/change_control_manager.py"
SNAP = "src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py"
BP = "src/melder/aether/spellbook/spell_compiler/blueprints/root_resolution_blueprint.py"
GEN = ("src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/"
       "generalized_manifest_no_overrides_compiler.py")
CPP = "src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py"
INC = DEV + "incident_manager/"
FRAME = "src/melder/aether/aetheric_frame/aetheric_frame.py"

EDITS = [
    # spell_system_node.py
    (SYS + "spell_system_node.py", 16,
     "    This does *not* replace SpellSystemStates (which are lineage/ DevOps-centric).", [
         "    This does *not* replace SpellSystemStates (which hold DevOps state per SpellIndex).",
     ]),
    (SYS + "spell_system_node.py", 21, "        * lineage_id – lineage ULID (SpellIndex.id).", [
        "        * lineage_id – the ULID of its SpellIndex (SpellIndex.id).",
    ]),
    (SYS + "spell_system_node.py", 117, '        """Return the lineage ULID associated with this system node."""', [
        '        """Return the ULID of the SpellIndex this system node\'s spell sits in."""',
    ]),
    # spell_system_root_blueprint_builder.py
    (SYS + "spell_system_root_blueprint_builder.py", 104,
     "                root_lineage_id=None,          # lineages can be threaded later if needed", [
         "                root_lineage_id=None,          # SpellIndex ids can be threaded later if needed",
     ]),
    (SYS + "spell_system_root_blueprint_builder.py", 165,
     "            root_lineage_id=None,          # lineages can be threaded later if needed", [
         "            root_lineage_id=None,          # SpellIndex ids can be threaded later if needed",
     ]),
    # spell_system_validation_system.py
    (SYS + "spell_system_validation_system.py", 55,
     "        Aggregate system-level validation diagnostics and update lineage validity", [
         "        Aggregate system-level validation diagnostics and update per-conduit resolution validity",
     ]),
    (SYS + "spell_system_validation_system.py", 118,
     "        Run system-level validation and update per-lineage validity.", [
         "        Run system-level validation and record per-conduit resolution validity.",
     ]),
    # root_resolution_blueprint.py
    (BP, 27, "        - `root_lineage_id` is optional lineage metadata for DevOps/change-", [
        "        - `root_lineage_id` is the root spell's optional SpellIndex id, for DevOps/change-",
    ]),
    (BP, 58, "                Optional lineage id for DevOps/change-control consumers.", [
        "                Optional SpellIndex id of the root spell, for DevOps/change-control consumers.",
    ]),
    (BP, 148, "        Return the optional lineage id for the root spell.", [
        "        Return the optional SpellIndex id for the root spell.",
    ]),
    # compiler phases
    (PH + "compiler_phase_3.py", 602, "        # matches through multiple pool entries (version lineages), the scan", [
        "        # matches through multiple pool entries (several of its versions), the scan",
    ]),
    (PH + "compiler_phase_4.py", 153, "        # Update global structural validity for this lineage.", [
        "        # Update global structural validity for this spell's SpellIndex.",
    ]),
    (PH + "compiler_phase_4.py", 158,
     "                    # First-fail semantics: validation errors make the lineage invalid.", [
         "                    # First-fail semantics: validation errors make the SpellIndex state invalid.",
     ]),
    # structural_snapshot.py
    (SNAP, 57, "          registered `SpellLocalTopology`, the lineage `SpellSystemState`", [
        "          registered `SpellLocalTopology`, the SpellIndex's `SpellSystemState`",
    ]),
    (SNAP, 365, "              the lineage state and the registered local topology; returns", [
        "              the SpellIndex's state and the registered local topology; returns",
    ]),
    (SNAP, 370, "            - `phase4.validity` is the lineage validity name and", [
        "            - `phase4.validity` is the SpellIndex state's validity name and",
    ]),
    (SNAP, 378, "                Frame registry holding the lineage state and topology.", [
        "                Frame registry holding the SpellIndex state and topology.",
    ]),
    (SNAP, 644, "            - A spell whose lineage state is missing raises RuntimeError (it", [
        "            - A spell whose SpellIndex state is missing raises RuntimeError (it",
    ]),
    (SNAP, 662, "                When an owned spell has no lineage state.", [
        "                When an owned spell has no SpellIndex state.",
    ]),
    # generalized_manifest_no_overrides_compiler.py: the Guard Policy names teardown's index unregister
    (GEN, 1278, "          clear only on teardown paths already blocked by lineage/validity", [
        "          clear only on teardown paths already blocked by SpellIndex-unregister/validity",
    ]),
    # contract_provider_presence_strategy.py
    (CPP, 37, "          one warning Phase 4 gates a lineage on, so SpellbookValidationError", [
        "          one warning Phase 4 gates a SpellIndex on, so SpellbookValidationError",
    ]),
    # spell_system_state.py
    (SSS + "spell_system_state.py", 67, "        the lineage is unregistered.", [
        "        the SpellIndex is unregistered.",
    ]),
    (SSS + "spell_system_state.py", 73, "        The per-lineage row of the control tower. Its per-conduit counterpart", [
        "        The per-SpellIndex row of the control tower. Its per-conduit counterpart",
    ]),
    (SSS + "spell_system_state.py", 89, "        change time instead of revalidating every lineage in the frame.", [
        "        change time instead of revalidating every SpellIndex in the frame.",
    ]),
    (SSS + "spell_system_state.py", 309,
     "            published set of flagged lineages (`non_resolvable_index_ids`) in", [
         "            published set of flagged spell indexes (`non_resolvable_index_ids`) in",
     ]),
    (SSS + "spell_system_state.py", 515,
     "            the gate publishes nothing, and the conduits holding the lineage would", [
         "            the gate publishes nothing, and the conduits holding the SpellIndex would",
     ]),
    (SSS + "spell_system_state.py", 518, "            The registry calls this so every conduit holding the lineage", [
        "            The registry calls this so every conduit holding the SpellIndex",
    ]),
    # spell_state.py
    (SSS + "spell_state.py", 20,
     "      sets it when the lineage's selected version was bound resolvable=False and", [
         "      sets it when the SpellIndex's selected version was bound resolvable=False and",
     ]),
    (SSS + "spell_state.py", 23,
     "      validity; its one reader is RiskManager, which leaves a flagged lineage's", [
         "      validity; its one reader is RiskManager, which leaves a flagged SpellIndex's",
     ]),
    (SSS + "spell_state.py", 42,
     "        contract, mutation, and ops concerns genuinely overlap on one lineage.", [
         "        contract, mutation, and ops concerns genuinely overlap on one SpellIndex.",
     ]),
    # conduit_resolution_state.py
    (SSS + "conduit_resolution_state.py", 105,
     "        same lineage can be perfectly resolvable in one conduit and gated in", [
         "        same spell can be perfectly resolvable in one conduit and gated in",
     ]),
    (SSS + "conduit_resolution_state.py", 578,
     "              scope, not of verdict: lineage membership in the risk model is", [
         "              scope, not of verdict: SpellIndex membership in the risk model is",
     ]),
    (SSS + "conduit_resolution_state.py", 583,
     "              lineage again (a peer that resolved the id through a contract).", [
         "              SpellIndex again (a peer that resolved the id through a contract).",
     ]),
    # spell_validity.py
    (SSS + "spell_validity.py", 66,
     "        lineage starts `unknown`, and `Meld._ensure_lineage_resolvable` reruns", [
         "        SpellIndex starts `unknown`, and `Meld._ensure_lineage_resolvable` reruns",
     ]),
    # change_control_manager.py
    (CCM, 66, "        Provide DevOps-facing bookkeeping for spell lineages, dirty roots, and", [
        "        Provide DevOps-facing bookkeeping for spell indexes, dirty roots, and",
    ]),
    (CCM, 1127, "        Record a pending change for a spell lineage.", [
        "        Record a pending change for a SpellIndex.",
    ]),
    (CCM, 1130, "            Track DevOps/AI-visible metadata for a SpellIndex lineage.", [
        "            Track DevOps/AI-visible metadata for a SpellIndex.",
    ]),
    (CCM, 1133, "            - Last-write-wins for duplicate lineage ids.", [
        "            - Last-write-wins for duplicate SpellIndex ids.",
    ]),
    (CCM, 1136, "                The SpellIndex for the lineage being tracked.", [
        "                The SpellIndex being tracked.",
    ]),
    (CCM, 1171, "        Return a snapshot of pending change metadata for a lineage.", [
        "        Return a snapshot of pending change metadata for a SpellIndex.",
    ]),
    (CCM, 1179, "                SpellIndex id of the lineage to query.", [
        "                Id of the SpellIndex to query.",
    ]),
    (CCM, 1206, "            Provide a tooling-friendly snapshot of all pending lineage changes.", [
        "            Provide a tooling-friendly snapshot of all pending SpellIndex changes.",
    ]),
    (CCM, 1229, "        Clear pending-change metadata for a lineage.", [
        "        Clear pending-change metadata for a SpellIndex.",
    ]),
    # incidents
    (INC + "incident.py", 27, "    - `spell_index_id`: optional lineage id primarily associated with the", [
        "    - `spell_index_id`: optional SpellIndex id primarily associated with the",
    ]),
    (INC + "incident.py", 124, "            spell_index_id: Optional lineage id primarily associated with the", [
        "            spell_index_id: Optional SpellIndex id primarily associated with the",
    ]),
    (INC + "incident.py", 230, "        Return the lineage id primarily associated with the incident, if any.", [
        "        Return the SpellIndex id primarily associated with the incident, if any.",
    ]),
    (INC + "incident.py", 232, "        This is the incident's main lineage anchor, not a derived search over", [
        "        This is the incident's main SpellIndex anchor, not a derived search over",
    ]),
    (INC + "incident_manager.py", 187, "            spell_index_id: Optional lineage id the incident is tied to.", [
        "            spell_index_id: Optional SpellIndex id the incident is tied to.",
    ]),
    (INC + "incident_manager.py", 244, "            spell_index_id: Optional lineage-id filter.", [
        "            spell_index_id: Optional SpellIndex-id filter.",
    ]),
    # aetheric_frame.py
    (FRAME, 41, "      - Owns the version registry for all `SpellIndex` lineages in this frame.", [
        "      - Owns the version registry for every `SpellIndex` in this frame.",
    ]),
    (FRAME, 84, "        conduits, clusters, and spell lineages without collision, which is why", [
        "        conduits, clusters, and spells without collision, which is why",
    ]),
    (FRAME, 197, "        # Per-frame graph + dirtiness registry for all spell lineages.", [
        "        # Per-frame graph + dirtiness registry for all spell indexes.",
    ]),
    (FRAME, 489, "          - lineage graph topology,", [
        "          - SpellIndex graph topology,",
    ]),
    (FRAME, 949, "          - Returns `None` for empty ids or when no matching lineage is found.", [
        "          - Returns `None` for empty ids or when no matching SpellIndex is found.",
    ]),
    (FRAME, 1018, "            Optional[SpellIndex]: The index whose lineage holds `spell_id` while the", [
        "            Optional[SpellIndex]: The index whose members hold `spell_id` while the",
    ]),
    (FRAME, 1294, "            str | None: Owning conduit id, or `None` when no lineage in this", [
        "            str | None: Owning conduit id, or `None` when no SpellIndex in this",
    ]),
    # aether.py: the frame's registries of spell indexes and selected spell_ids
    ("src/melder/aether/aether.py", 2554, "        conduits register and unregister their lineages).", [
        "        conduits register and unregister their spell indexes).",
    ]),
    # spellbinder.py: the pending registration's permissions
    ("src/melder/aether/spellbook/spellbinder.py", 635, "                ceiling for this lineage.", [
        "                ceiling for this spell.",
    ]),
    # spell_contract.py: the consumer spell revalidates
    ("src/melder/aether/conduit/meld/contracts/spell_contract.py", 56,
     "    can satisfy the contract and trigger revalidation of the reporting lineage.", [
         "    can satisfy the contract and trigger revalidation of the reporting spell.",
     ]),
    ("src/melder/aether/conduit/meld/contracts/spell_contract.py", 98,
     "        lineage re-runs its resolution phases against the now-satisfied edge.", [
         "        spell re-runs its resolution phases against the now-satisfied edge.",
     ]),
]
