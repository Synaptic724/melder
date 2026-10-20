- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Validated with A-D on the 0.2.8258 tree (Python 3.14.7t; the /tmp mirror byte-equal to the repository's
    src/ and tests/; the same counts with the GIL off and on). The S4 tests: 50 passed. The whole tree by shards:
    unit 9691 passed, 3 skipped, 7 xfailed; component 2403 passed, 23 skipped, 1 xfailed; integration spellbook 670
    passed, 2 skipped, 2 xpassed; aether 823 passed, 5 xfailed; conduit 353 passed (its open notch-race test,
    marked intermittent, xfailed in one run and xpassed in the others); crystallizer, multithreading,
    mutation_research and live_sim 398 passed, 4 xfailed; experimentation, experiments, tests and mocks 250 passed,
    4 skipped - the only failures the 18 red tests held for
    STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers (7 unit, 11 integration), as at 0.2.8256. Probes on
    the repository: M1-M3, V1-V4 and G1-G3 byte-equal to the A-D runs at 0.2.8256; M4-M7 equal but for its eight
    refusals, which now carry S1's wording ("Spell ID collision detected: this object is already registered as
    spell_id ...") and are refused all the same. The release note's example: every assert holds, GIL off and on.
  EVIDENCE:
  - context_compass/artifacts/minted_index_registry_20261018/runs/full_tree_0_2_8259/unit_gil0.txt:1-168
  - context_compass/artifacts/minted_index_registry_20261018/runs/full_tree_0_2_8259/unit_gil1.txt:1-176
  - context_compass/artifacts/minted_index_registry_20261018/runs/full_tree_0_2_8259/integ_aether_gil0.txt:1-71
  - context_compass/artifacts/minted_index_registry_20261018/runs/full_tree_0_2_8259/integ_aether_gil1.txt:1-79
  - context_compass/artifacts/minted_index_registry_20261018/runs/full_tree_0_2_8259/integ_conduit_gil0.txt:1-6
  - context_compass/artifacts/minted_index_registry_20261018/runs/full_tree_0_2_8259/integ_rest_gil1.txt:1-15
  - context_compass/artifacts/minted_index_registry_20261018/runs/landed_0_2_8259_probe_minted_index_fix_cases_gil0.txt:1-30
  - context_compass/artifacts/minted_index_registry_20261018/runs/landed_0_2_8259_probe_minted_index_registry_0_2_8256_gil0.txt:1-26
  - context_compass/artifacts/minted_index_registry_20261018/runs/landed_0_2_8259_probe_research_residency_moves_0_2_8256_gil0.txt:1-13
  - context_compass/artifacts/minted_index_registry_20261018/runs/landed_0_2_8259_probe_minted_index_grants_gil0.txt:1-6
  - context_compass/artifacts/minted_index_registry_20261018/runs/release_note_block_s4_landed_0_2_8259.txt:1-2
  IMPACT: The exit gate's tests and probes hold on the landed tree; what remains is documentation, the notch, the
    closure and the rebuild.
  NEXT: The system documents (land_s4_docs.py, the citation remap, the four indexes), then the graph.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
