- DATETIME: {ts}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The four S8 probes, re-run on the mirror (0.2.8260 plus the rollback), show the refusal with nothing
    moved, the same with the GIL off and on (only the GIL-mode warning differs). N2: `notch_spell` to SelfMade
    raises SpellbookValidationError whose first line is "notch_spell refused: 'SelfMade' (spell_id 83717df2...)
    failed its structural check, so the notch did not happen; 'English' (spell_id 677a47a3...) is still the active
    version of the index.", the SELF_DEPENDENCY report under it; afterwards the lender selects English, SelfMade is
    parked, the borrower holds English active and SelfMade parked, and the lender melds English by address and by
    spell_id. N1 (French, sound) moves owner and borrower as before; N3 (a notch back to English after N2) changes
    nothing. The ambiguous-provider version (TimedGreeter) is refused the same way with its AMBIGUOUS_PROVIDER
    report, and the borrower's Speaker melds "hello". The lineage probe: after the refusal the lineage reads
    English with no dependencies and the borrower's meld of Speaker is ok. The documentation ritual on the error
    file changed only its words and one annotation: the docstrings name `Spellbook._notch_spell` as the caller
    that passes a preface, and `_check_preface` takes `object` (the value it narrows), not `Any`; the edit set
    (apply_s8_rollback.py) reproduces the mirror byte for byte from the index's spellbook.py and conduit.py and
    the worktree's other files, and the custom-exception unit tests plus S8's integration file pass, 63 in each
    GIL mode.
  EVIDENCE:
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_notch_commit_s8_mirror_gil0.txt:1-34
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_notch_commit_s8_mirror_gil1.txt:1-38
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_notch_two_reasons_s8_mirror_gil0.txt:1-30
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_notch_two_reasons_s8_mirror_gil1.txt:1-38
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_switch_plain_s8_mirror_gil0.txt:1-13
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_switch_plain_s8_mirror_gil1.txt:1-17
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/dbg_refused_notch_lineage_dependencies_s8_mirror_gil0.txt:1-7
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/dbg_refused_notch_lineage_dependencies_s8_mirror_gil1.txt:1-11
  - context_compass/artifacts/failed_notch_refusal_20261018/scripts/s8_error_doc_ritual_20261019.py:1-73
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/s8_after_ritual_gil0.txt:1-2
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/s8_after_ritual_gil1.txt:1-10
  IMPACT: The exit gate's probe criteria hold on the mirror; S8 waits only for melder_0's hand-over of
    spellbook.py and conduit.py after S3 lands, then the repository edits, the tree again, docs, notch, rebuild.
  NEXT: Draft the system-document edits for S8 (src_architecture, src_components, tests docs) in the lane while
    melder_0 lands S3; re-read the mailbox between work units.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
