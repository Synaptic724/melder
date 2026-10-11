Run logs of the find_spell_by_id race investigation (melder_1, 2026-10-10). Trees, all scratch git-archive
exports of 3d184cac (0.2.8228) under /tmp/cc_lookup on the device VM - never the repository:

  head      exactly 3d184cac.
  cand      3d184cac + proposal/variant_r1a_dict_copy.diff (dict.copy() snapshot). When cand_* logs,
            bench_gil0/1.log and contended_throughput.log were taken this file was named proposed_patch_r1.diff,
            which is what their headers say. Measured, then NOT recommended.
  cand_b    cand with the snapshot line changed to list(self._spells.items()) (probe only; its runs were printed,
            not saved - contended_copy_vs_list.log repeats the comparison with cand_r1).
  cand_r1   3d184cac + proposal/proposed_patch_r1.diff (the recommended R1: list(items()) snapshot).
  cand_c    cand_r1 with a keys-only snapshot and one .get on a hit (variant R1c; bench_variant_keys_gil0.log,
            contended_throughput_r1.log).

Diagnostics versions: head_gil0/1.log and head_repeat_10x_per_gil.log ran v1 (11 tests); head_v2_* ran v2 (13 tests,
kept as diagnostics/history/test_find_spell_by_id_race_v2.py); *_v3_* and v3_repeat_10x.log run the current file.

Index
  head_v3_gil0/1.log, cand_v3_gil0/1.log, cand_r1_v3_gil0/1.log   one verbose run per tree and GIL mode
  v3_repeat_10x.log (head, cand), cand_r1_v3_repeat_10x.log        determinism, 10 runs per tree and GIL mode
  stress_{head,cand,cand_r1}_gil0/1.log                            uninstrumented stress (supplementary)
  dict_skip_probe.log, dict_snapshot_probe.log                     plain-dict probes (mode d; snapshot forms)
  bench_gil0/1.log (head vs cand), bench_r1_gil0/1.log (head vs cand_r1), bench_variant_keys_gil0.log
  contended_throughput.log (head vs cand), contended_throughput_r1.log (head, cand_r1, cand_c),
  contended_copy_vs_list.log (head, cand, cand_r1), contended_writer_check_gil0.log (head vs cand_r1, 6 pairs)
  suite_dirs_head_vs_r1.log                                        existing suites, head vs cand_r1

R4/R5 review (Notes 14-21): every later run, script and diagnostic lives under ../r4/ - start at ../r4/README.txt.
