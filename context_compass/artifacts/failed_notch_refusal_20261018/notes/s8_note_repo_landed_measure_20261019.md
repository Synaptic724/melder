- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: S8 is in the repository, on S3's landed tree (0.2.8261). `apply_s8_rollback.py <repository> --check`, then
    `--apply`, edited the five files (spellbook.py 7945 -> 8344 lines, conduit.py 7892 -> 7907, the error file 541
    CRLF, the CCM 1683 CRLF, the unit test 97), byte-identical to the mirror the whole tree ran on (its src/ and
    tests/ equal to the repository's, S3's 13 tests included). The whole tree there, GIL off and on, one pytest run
    per shard: unit 9,701 passed and 1 failed, component 2,406, integration spellbook 678, aether 846 (S3's 10 and
    S8's 14 among them), conduit 353, the rest 398, experiments and misc 250 - 14,632 passed in each mode. The one
    failure, `test_generated_build_assets_are_stamped_for_the_live_version`, reads build assets stamped 0.2.8260
    against package 0.2.8261: S3 notched without a rebuild, and this landing's rebuild clears it. On the repository
    itself: S8's and S3's test files with the custom-exception unit tests, 76 passed in each GIL mode, and the
    probes - N1-N3, the plain proof, the marks - print the refusal with nothing moved; only the GIL-mode warning
    differs between the modes.
  EVIDENCE:
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/apply_s8_repo_check_0_2_8261.txt:1-5
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/apply_s8_repo_apply_0_2_8261.txt:1-6
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_unit_gil0.txt:1-143
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_unit_gil1.txt:1-151
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_component_gil0.txt:1-35
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_component_gil1.txt:1-43
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_integ_spellbook_gil0.txt:1-11
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_integ_spellbook_gil1.txt:1-19
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_integ_aether_gil0.txt:1-13
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_integ_aether_gil1.txt:1-21
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_integ_conduit_gil0.txt:1-6
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_integ_conduit_gil1.txt:1-14
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_integ_rest_gil0.txt:1-7
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_integ_rest_gil1.txt:1-15
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_exp_and_misc_gil0.txt:1-5
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_exp_and_misc_gil1.txt:1-13
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/s8_s3_tests_repo_0_2_8261_gil0.txt:1-3
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/s8_s3_tests_repo_0_2_8261_gil1.txt:1-11
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_notch_commit_0_2_8255_repo_0_2_8261_gil0.txt:1-34
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_notch_commit_0_2_8255_repo_0_2_8261_gil1.txt:1-38
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_switch_plain_repo_0_2_8261_gil0.txt:1-13
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_switch_plain_repo_0_2_8261_gil1.txt:1-17
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_refused_notch_marks_repo_0_2_8261_gil0.txt:1-21
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_refused_notch_marks_repo_0_2_8261_gil1.txt:1-25
  IMPACT: S8's code is landed and validated on S3's tree; documents, the notch, the release note, the closures and
    the rebuild remain.
  NEXT: The system documents (land_s8_docs.py), the citation remap and the four indexes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
