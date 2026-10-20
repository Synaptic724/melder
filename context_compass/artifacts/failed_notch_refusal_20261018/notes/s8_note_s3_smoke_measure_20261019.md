- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: S8 goes onto S3 as S3 stands in the worktree (not yet notched; `__version__` reads 0.2.8260).
    `apply_s8_rollback.py <repository> --check` finds every edit's old text once in each of the five files and
    writes nothing (spellbook.py 7945 -> 8344 lines, conduit.py 7892 -> 7907; the error file, the CCM and the unit
    test as on 0.2.8260). On the mirror, re-synced from the worktree's src/ and tests/ (S3's edits and its two
    untracked tests included) with the S8 edits applied, S8's integration file, the custom-exception unit tests
    and S3's two new test files pass, 76 in each GIL mode. Method: Python 3.14.7t, `-X gil=0` and `-X gil=1` with
    PYTHON_GIL to match, one pytest run each. Caveat: S3 can still change before its notch, so the check and the
    whole tree run again on the repository after melder_0's hand-over.
  EVIDENCE:
  - context_compass/artifacts/failed_notch_refusal_20261018/scripts/apply_s8_rollback.py:1-746
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/s3s8_smoke_mirror_gil0.txt:1-3
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/s3s8_smoke_mirror_gil1.txt:1-11
  IMPACT: S3's hunks and S8's do not overlap; the landing needs no rework of the edit set, only the re-check on
    the tree melder_0 hands over.
  NEXT: Draft S8's system-document edits against the post-S3 text (land_s8_docs.py), reading the mailbox between
    work units.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
