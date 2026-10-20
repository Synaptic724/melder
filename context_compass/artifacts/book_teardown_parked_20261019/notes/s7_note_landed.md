- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The edit is in the repository as the PLAN note maps it (apply_s7.py, edits A-C, notch text 0.2.8260;
    spellbook.py 7858 -> 7903 lines; `__version__` stays 0.2.8259 until the turn-in's notch). The S7 tests pass there,
    8 passed with the GIL off and on. The whole tree in the VM mirror, seven shards with the GIL off and on: every
    test passes except S8's 18 red tests, held with the story (7 in test_spellbook_validation_error_preface.py, 11 in
    test_notch_refused_at_commit_integration.py), failing as on 0.2.8259; integration/spellbook reads 678 passed.
    Probe T1-T5 on the landed tree is byte-equal to the prototype's run: T2 and T3 fixed (French, the shared index
    and the minted index cleaned; `French.cleanup()` returns), T1, T4 and T5 unchanged.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:405-422
  - src/melder/aether/spellbook/spellbook.py:559-645
  - context_compass/artifacts/book_teardown_parked_20261019/runs/apply_s7_repo_0_2_8260.txt:1-2
  - context_compass/artifacts/book_teardown_parked_20261019/runs/green_s7_repo_0_2_8260_gil0.txt:1-2
  - context_compass/artifacts/book_teardown_parked_20261019/runs/green_s7_repo_0_2_8260_gil1.txt:1-10
  - context_compass/artifacts/book_teardown_parked_20261019/runs/full_tree_0_2_8260/unit_gil0.txt:1-168
  - context_compass/artifacts/book_teardown_parked_20261019/runs/full_tree_0_2_8260/integ_aether_gil0.txt:1-71
  - context_compass/artifacts/book_teardown_parked_20261019/runs/full_tree_0_2_8260/integ_spellbook_gil0.txt:1-11
  - context_compass/artifacts/book_teardown_parked_20261019/runs/landed_0_2_8260_probe_book_teardown_parked_gil0.txt:1-30
  - context_compass/artifacts/book_teardown_parked_20261019/runs/landed_0_2_8260_probe_book_teardown_parked_gil1.txt:1-34
  IMPACT: The EXIT_GATE's probe and test conditions are met; the documents, the graph, the notch, the release note,
    the closure and the rebuild remain.
  NEXT: The system documents (citation remap first, then the anchored edits and the indexes).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
