r4/ - review of the reviewer's Book-lock design (R4) and the adapted repair R5 (melder_1, 2026-10-10).
Ticket Notes 14-20. Proposal: ../proposal/repair_proposal_r5.md and ../proposal/proposed_patch_r5.diff.

Trees (scratch exports of 3d184cac under /tmp/cc_lookup on the device VM, never the repository):
  head       3d184cac (src + tests);           full_head  3d184cac, full git archive (for the full test tree)
  cand_r1    + proposal/proposed_patch_r1.diff (R1)
  cand_r4    + R4 literal (scripts/apply_r4_literal.py; r4_literal.diff)
  cand_r4b   + reader lock around a one-call snapshot only (scripts/apply_r4b_brief_reader_lock.py)
  cand_r4p   R4' = cand_r4 + phase 4 reading _spell_id_pool (scripts/make_variants.py)
  cand_r5    + proposal/proposed_patch_r5.diff (scripts/apply_r5.py);  full_r5f  the same on full_head
  cand_nc1   R5 without the snapshot;  cand_nc2  R5 without the cleanup-safe probe;
  cand_nc3   R4's reader lock without the publication lock (all three from scripts/make_variants.py)

Files
  spells_access_inventory.txt                      every _spells site, the lock each mutation holds (Note 14)
  r4_literal.diff                                  R4 as applied for the measurements
  diagnostics/test_lookup_fair_matrix.py           the 17-test fair matrix (Note 18)
  diagnostics/probe_conjure_hook_foreign_lookup.py the conduit-hook foreign lookup probe (Note 16)
  diagnostics/opposite_transfer_watchdog.py        opposite transfers, forced rollback, watchdog (Note 20)
  diagnostics/probe_bind_failure_after_publication.py  bind failing after publication (lock release, state)
  runs/r4_literal_ambiguous_conjure_gil0.log       R4: PhaseTimeoutError after 60 s (Note 15)
  runs/r4b_ambiguous_conjure_gil0.log              R4b: the same
  runs/head_ambiguous_conjure_and_late_bind_gil0.log, r1_ambiguous_conjure_gil0.log,
  runs/r4_literal_ambiguous_late_bind_gil0.log      the passing comparisons
  runs/r5_ambiguity_files_gil0.log, r4p_ambiguity_files_gil0.log   the three ambiguity test files
  runs/probe_conjure_hook_foreign_lookup.log       head, R4, R4b, R1 x gil 0/1
  runs/matrix/<tree>_gil<g>_rep<r>.log, runs/matrix_table.txt      fair matrix, 3 reps x 2 GIL modes (rep4: final R5)
  runs/r5_v3_diagnostics_gil0/1.log                the original 13 forced diagnostics on R5
  runs/suites/summary_full_tree_gil0.txt (+ logs)  full test tree, head vs final R5; r5_first_wording/ earlier R5 text
  runs/suites/summary_r4p_caller_dirs_gil0.txt     R4' on the caller directories
  runs/bench_<tree>_gil<g>.log, bench_table_gil0/1.txt             single-thread lookup cost
  runs/contended_r5_r4p_gil0/1.log, contended_readers_only_gil0.log contended throughput
  runs/opposite_transfer_gil<g>_fail<k>.log, opposite_transfer_table.txt
  runs/probe_bind_failure_after_publication.log
  scripts/                                          apply and variant scripts, run_matrix.sh, matrix_table.py,
                                                    run_chunk.sh
