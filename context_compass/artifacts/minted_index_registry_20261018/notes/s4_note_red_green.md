- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The regression tests, written to the PLAN note, red on 0.2.8256 and green with A-D (Python 3.14.7t, the same
    with the GIL off and on). New integration file, 12 cases: the version found by spell_id parked and notched
    active, granted by spell_id parked and active (the borrower's copy parked or active as on the lender),
    transferred by spell_id, a second bind of its spell_id refused (another Book of the frame, conjured or not; a
    Book of another frame, conjured or not), registered under its root until the root's teardown, then gone and
    bindable anew, moved back with no registered index left behind (a control), and read by residency parked, then
    active. Residency unit file: two frame doubles now track the selected id as bind and a notch register it, and one
    new case reads a selected version no lineage tracks as parked. In the repository: 11 failed, 1 passed (the
    control); the unit file 1 failed (the new case), 37 passed. In a /tmp mirror of the repository with A-D applied
    by the lane's script (byte-equal to the preview's files): both files 50 passed; the whole tree by shards - unit
    9648 passed, 3 skipped, 7 xfailed; component 2396 passed, 23 skipped, 1 xfailed; integration spellbook 669
    passed, 2 skipped, 2 xpassed; aether 823 passed, 5 xfailed; conduit 353 passed, 1 xpassed; crystallizer,
    multithreading, mutation_research and live_sim 398 passed, 4 xfailed; experimentation, experiments, tests and
    mocks 250 passed, 4 skipped - the only failures the 18 red tests held for
    STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers (7 unit, 11 integration), as at 0.2.8256. Probes at
    A-D: M1-M7 and V1-V4 byte-equal to the A+B+C prototype runs; new probe G1-G3 - a grant by spell_id of French in
    its own index gives a parked copy while French is parked and an active one once notched (the tree raises "not
    found in any conduit" for both).
  EVIDENCE:
  - tests/integration/melder/spellbook/test_separated_version_is_known_to_its_frame_integration.py:1-411
  - tests/unit/melder/mutation_research/test_mutation_research_root.py:361-403
  - tests/unit/melder/mutation_research/test_mutation_research_root.py:444-553
  - context_compass/artifacts/minted_index_registry_20261018/runs/red_tests_0_2_8256_gil0.txt:1-48
  - context_compass/artifacts/minted_index_registry_20261018/runs/red_tests_0_2_8256_gil1.txt:1-56
  - context_compass/artifacts/minted_index_registry_20261018/runs/red_unit_residency_0_2_8256_gil0.txt:1-10
  - context_compass/artifacts/minted_index_registry_20261018/runs/red_unit_residency_0_2_8256_gil1.txt:1-18
  - context_compass/artifacts/minted_index_registry_20261018/runs/full_tree_abcd/green_tests_gil0.txt:1-2
  - context_compass/artifacts/minted_index_registry_20261018/runs/full_tree_abcd/green_tests_gil1.txt:1-10
  - context_compass/artifacts/minted_index_registry_20261018/runs/full_tree_abcd/unit_gil0.txt:1-168
  - context_compass/artifacts/minted_index_registry_20261018/runs/full_tree_abcd/integ_aether_gil0.txt:1-71
  - context_compass/artifacts/minted_index_registry_20261018/probes/probe_minted_index_grants.py:1-106
  - context_compass/artifacts/minted_index_registry_20261018/runs/abcd_probe_minted_index_grants_gil0.txt:1-6
  - context_compass/artifacts/minted_index_registry_20261018/runs/abcd_probe_minted_index_fix_cases_gil0.txt:1-30
  IMPACT: The fix is proven red to green on the repository's own tests, with nothing else in the tree moving. The new
    tests stay red in the repository until A-D land with spellbook.py and spell.py back (M1-40); S1 and S2 land
    first, so the tests and the four anchors are re-checked on that tree (the collision message the rebind case
    matches, the seams' text).
  NEXT: melder_0's handover after S1 and S2 land; then re-check the anchors and apply A-D.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
