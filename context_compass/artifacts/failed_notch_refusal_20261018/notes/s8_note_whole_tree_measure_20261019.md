- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The whole tree passes on the mirror with the S8 rollback, the GIL off and on: 0 failed in all seven shards,
    14,620 passed in each mode - unit 9,702, component 2,403, integration spellbook 678, aether 836 (S8's 14
    integration tests among them), conduit 353, the rest 398, experiments and misc 250 - beside the skips, xfails
    and xpasses those shards always carry. The mirror is 0.2.8260 as the git index holds spellbook.py and
    conduit.py, the worktree's spellbook_validation_error.py and change_control_manager.py, and the repository's
    tests, with the S8 edits applied by apply_s8_rollback.py. Method: Python 3.14.7t, `-X gil=0` and `-X gil=1`
    with PYTHON_GIL to match, one pytest run per shard. Caveat: melder_0's S3 tests (untracked, only in the
    repository) are not in the mirror; the tree is run again once S8 is applied onto S3.
  EVIDENCE:
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_unit_gil0.txt:1-137
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_unit_gil1.txt:1-145
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_component_gil0.txt:1-35
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_component_gil1.txt:1-43
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_integ_spellbook_gil0.txt:1-11
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_integ_spellbook_gil1.txt:1-19
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_integ_aether_gil0.txt:1-13
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_integ_aether_gil1.txt:1-21
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_integ_conduit_gil0.txt:1-6
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_integ_conduit_gil1.txt:1-14
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_integ_rest_gil0.txt:1-7
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_integ_rest_gil1.txt:1-15
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_exp_and_misc_gil0.txt:1-5
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_exp_and_misc_gil1.txt:1-13
  IMPACT: The rollback breaks nothing outside S8's own 25 tests; what remains before the repository is the
    documentation ritual on the error file, the probes on the mirror, and melder_0's hand-over after S3.
  NEXT: Finish the documentation ritual on the mirror diff (spellbook_validation_error.py), then re-run the S8
    probes on the mirror with the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
