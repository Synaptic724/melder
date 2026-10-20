- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The fix proven in /tmp copies of the 0.2.8256 src, one edit at a time, applied by the lane's script
    (`apply_s4.py --edits`; the copies differ from the tree in those files only); all three probes run, GIL off, and
    with all three edits GIL on too (equal apart from the warning). A - `_apply_remove_from_index` registers the
    minted index under the spell's owner, frame lock alone after the Book lock: M2 and M3 found, both lookups
    answer, the grant is accepted, M4b and M5b refused, M7's transfer accepted; but V2 reads French "active in
    index2" while the Book holds it parked (the minted index selects its parked member; activation takes a notch,
    the owner's S10 ruling), and M6 leaves the dead root a registry entry (1 index) and an id-set entry, so
    `find_index_for_spell` and `find_conduit_id_for_spell` answer the dead root. A+B - the root's teardown
    (`_unregister_conduit_spells_from_aether`) also unregisters each parked version's index: M6 clean; V2 still
    "active". A+B+C - `_locate_live_membership` calls a version active only when the index selects it and the
    frame's lineage registry tracks it as that index's current version (`get_by_index_id(index.id)
    .current_spell_id`): every case right - V2 parked, V3 active, M1-M7 as above. The preview diff is 161 lines;
    re-run on the final preview, the A+B+C outputs are byte-equal to the recorded ones.
  EVIDENCE:
  - context_compass/artifacts/minted_index_registry_20261018/scripts/apply_s4.py:1-235
  - context_compass/artifacts/minted_index_registry_20261018/runs/s4_preview_0_2_8256.diff:1-161
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_A_probe_minted_index_fix_cases_gil0.txt:1-30
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_A_probe_research_residency_moves_0_2_8256_gil0.txt:1-13
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_AB_probe_minted_index_fix_cases_gil0.txt:1-30
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_AB_probe_research_residency_moves_0_2_8256_gil0.txt:1-13
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_ABC_probe_minted_index_fix_cases_gil0.txt:1-30
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_ABC_probe_minted_index_fix_cases_gil1.txt:1-34
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_ABC_probe_minted_index_registry_0_2_8256_gil0.txt:1-26
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_ABC_probe_minted_index_registry_0_2_8256_gil1.txt:1-30
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_ABC_probe_research_residency_moves_0_2_8256_gil0.txt:1-13
  - context_compass/artifacts/minted_index_registry_20261018/runs/prototype_ABC_probe_research_residency_moves_0_2_8256_gil1.txt:1-17
  IMPACT: The seam's registration alone (A) fixes the lookups but makes residency wrong in a new way and leaves a
    torn-down root in the registry; A+B+C is the smallest set with every case right. B sits outside the story's
    EXECUTION_BOUNDARY in spellbook.py (the root's teardown) and C in mutation_research.py (DECISION_REQUEST note).
  NEXT: The owner's word on the three edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
