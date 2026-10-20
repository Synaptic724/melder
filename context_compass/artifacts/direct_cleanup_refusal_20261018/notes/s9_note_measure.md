- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Green with the fix, the same with the GIL off and on (Python 3.14.7t). The S9 integration file: 9 passed in
    the repository (the 7 that were red now pass; the 2 sole-member controls still pass). Probe D1-D3 re-run at the
    fix: D1 `cleanup_spell(English)`, D2 `English.cleanup()` and D3 `cleanup_and_remove_spell(english_id)` are all
    refused - D2 and D3 with the Spellbook's message - and after each the index is live and selects English, both
    versions are uncleaned and found by the frame, and the borrower holds English active and French parked; a notch
    to French then works and the root's teardown cleans French. The whole tree in a /tmp mirror of 0.2.8255 with
    E1-E7 (the structural-parity tests need a deletable cache root): unit 9647 passed, 3 skipped, 7 xfailed;
    component 2396 passed, 23 skipped, 1 xfailed; integration spellbook 657 passed, 2 skipped, 2 xpassed; aether 823
    passed, 5 xfailed; conduit 353 passed, 1 xpassed; crystallizer, multithreading, mutation_research and live_sim
    398 passed, 4 xfailed; experimentation, experiments, tests and mocks 250 passed, 4 skipped. The only failures
    are the 18 red tests written for the held STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers (7 in
    test_spellbook_validation_error_preface.py, 11 in test_notch_refused_at_commit_integration.py), red on purpose
    until S8 lands; nothing else fails.
  EVIDENCE:
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/green_tests_0_2_8256_gil0.txt:1-2
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/green_tests_0_2_8256_gil1.txt:1-10
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/probe_direct_cleanup_active_member_at_fix_gil0.txt:1-49
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/probe_direct_cleanup_active_member_at_fix_gil1.txt:1-53
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/unit_gil0.txt:1-168
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/unit_gil1.txt:1-176
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/component_gil0.txt:1-35
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/component_gil1.txt:1-43
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/integ_spellbook_gil0.txt:1-11
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/integ_spellbook_gil1.txt:1-19
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/integ_aether_gil0.txt:1-71
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/integ_aether_gil1.txt:1-79
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/integ_conduit_gil0.txt:1-6
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/integ_conduit_gil1.txt:1-14
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/integ_rest_gil0.txt:1-7
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/integ_rest_gil1.txt:1-15
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/exp_and_misc_gil0.txt:1-5
  - context_compass/artifacts/direct_cleanup_refusal_20261018/runs/full_tree_0_2_8256/exp_and_misc_gil1.txt:1-13
  IMPACT: The EXIT_GATE's code and test parts are met (probe D2 and D3 refused as D1; a sole member still removed;
    regression tests green with the GIL off and on). Two empty logs of a background run that died with its call are
    under runs/full_tree_0_2_8256/_to_delete/ for the owner to delete.
  NEXT: The system documents with their indexes and the graph; then the notch, the release note, closure, rebuild.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
