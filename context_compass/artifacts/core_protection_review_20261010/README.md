# Evidence pack: core-protection review hand-back (2026-10-10)

Ticket: `tickets/tasks/completed/2026-10-08_review_core_protection_fork_aware_updates_task.md` (its "Hand-back"
section is the narrative; this folder is the evidence). Agent: melder_1. The companion lane of the same request,
scan_bind_option_parity, has its own pack in `../scan_bind_option_parity_20261010/`; both lanes were verified on one
tree, so the whole-tree runs below cover both.

## Revision
- HEAD `66939dfe84e41e51f41f4bc4461ad1690907e909` on `codex_features2`, plus the working-tree delta listed in
  `tree/tree_delta.txt`: content compared with line endings normalized; 1747 tracked files differ from HEAD only by
  CRLF endings and are counted, not listed. `release_docs/0.2.8227.md` is staged in the index by the owner (the
  0.2.8227 note's rename after tagging) and is not part of this request.
- src/ and tests/ did not change after the final verification began (2026-10-10T12:53Z). The closing rebuild
  (13:46Z) rewrote no generated file: all 46 asset and bundle files kept their bytes.
- Nothing committed or pushed.

## Environment
- `env/env.txt`: Ubuntu 22.04.5 LTS VM, Linux 6.8.0; CPython 3.14.7 free-threading build (Py_GIL_DISABLED 1) run with
  `-X gil=0`, so `sys._is_gil_enabled()` is False; pytest 9.1.1; Melder 0.2.8228 from this tree (not installed).
- `env/installed_distributions.txt`: iniconfig 2.3.0, packaging 26.3, pluggy 1.6.0, Pygments 2.21.0, pytest 9.1.1,
  PyYAML 6.0.3.

## Runs
Every run: `python -X gil=0 -m pytest -q -p no:cacheprovider -rsxX <paths>` from the repository root, with
`PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX` and `TMPDIR` outside the repository (`runs/run_one.sh`; the first
batch used `runs/run_final.sh`). Each `runs/<name>.txt` holds the command, start and end times, the pytest output with
every skip, xfail and xpass reason, and the exit code; `runs/<name>.xml` is its junit report.

| run | scope | result |
| --- | --- | --- |
| v3_unit_tier | tests/unit | 9020 passed, 3 skipped, 7 xfailed |
| v4_component_spellbook | tests/component/melder/spellbook | 799 passed |
| v9_component_other | tests/component/melder/{aether,crystallizer,mutation_research,utilities} | 1502 passed, 23 skipped, 1 xfailed |
| v5_integration_spellbook | tests/integration/melder/spellbook | 613 passed, 2 skipped, 2 xpassed |
| v6a-v6e2 (7 runs) | tests/integration/melder/crystallizer, split by file and node id (`runs/*_ids_*.txt`) | 273 passed, 3 xfailed |
| v7_integration_mutation_research | tests/integration/melder/mutation_research | 67 passed |
| v8_integration_aether | tests/integration/melder/aether | 785 passed, 5 xfailed |
| v10_integration_conduit | tests/integration/melder/conduit | 275 passed |
| v11_integration_live_sim_multithreading | tests/integration/melder/{live_sim,multithreading} | 55 passed, 1 xfailed |
| v12_experimentation | tests/experimentation | 250 passed, 4 skipped |
| **tree** | **the 16 runs above partition tests/** | **13,639 passed, 32 skipped, 17 xfailed, 2 xpassed, 0 failed** |
| v1_scan_focused | the scan_bind focused set (7 files) | 409 passed |
| v2_review_suite | this review's five files | 28 passed, 5 xfailed |
| v3a_unit_spellbook | tests/unit/melder/spellbook | 2343 passed |
| v13_post_rebuild | llm_support, build_assets, registration guard, public surface, version, system documents | 291 passed, 1 skipped |
| v14_review_suite_post | this review's five files, after the closure | 28 passed, 5 xfailed |
| v15_scan_focused_post | the scan_bind focused set, after the closure | 409 passed |

`runs/results_table.md` holds the first batch with each run's full path list. Windows tiers and hosted CI: Not run
(owner).

## Skips, xfails and xpasses
`runs/skips_xfails.md` lists every one with its reason. The five strict xfails of this review are the open defects
(D-10: `test_safe_profile_refuses_writing_files`; D-11: four `test_hybrid_refuses_dynamic_imports_of_its_denied_roots`
cases); every other skip, xfail and xpass is pre-existing and unrelated to this request.

## Diffs and manifests
- `diffs/review_authored.diff`: the five review test files against HEAD (all new).
- `diffs/tests_components_review_part.diff`: this review's part of tests_components (the state after scan_bind, 09:49Z,
  to the final file); the baseline was checked against the preservation multiset taken at 11:44Z.
- `file_manifest.md`: SHA256 of the final bytes of every authored and generated file of this lane. Generated files are
  listed, not diffed.
- `tools/make_diffs.py` regenerates both packs' diffs and manifests; `tools/tree_delta.py` regenerates the tree delta.
  Both use read-only git (`GIT_OPTIONAL_LOCKS=0`).

## Probes (reproducers)
Each probe runs in its own process against a scratch copy of `src` and `tests` (put both on `PYTHONPATH`), writes
only under the scratch path it is given, and restores what it replaces before it exits. Outputs were recorded on this
tree at 2026-10-10T13:33Z; the VM home is written as `~`.

| probe | backs | output |
| --- | --- | --- |
| `probes/codegen_probe.py <out dir> <bind.py>` | D-10 (`open` under all five postures) and the import gate (Note 10) | `codegen_probe_output.txt` |
| `probes/codegen_probe2.py` | D-11 (`__import__` under hybrid, precision, permissive; refused under safe) (Note 11) | `codegen_probe2_output.txt` |
| `probes/probe_materialize.py` | D-20 (core, new melder.*, stdlib and installed names materialized) (Note 20) | `probe_materialize_output.txt` |
| `probes/probe_materialize_fail.py` | D-20 (originals lost on a failed materialize and on cleanup) (Note 20) | `probe_materialize_fail_output.txt` |
| `probes/probe_custody.py <new dir>` | contract C1-C2 evidence: links, hard links, native and nested-env files, provenance, stat cache, path comparison (Note 19) | `probe_custody_output.txt` |
| `probes/d3_probe.py` | F2 and D3: a nested `.venv` classified as user source (Note 8) | `d3_probe_output.txt` |

`d3_probe.py` runs from a project directory holding a `.venv` made with `python -m venv --without-pip .venv`: copy
`d3_world/venv_site_packages/*` into that venv's site-packages and `d3_world/src/` to `src/`, then run the venv's
python with `PYTHONPATH=<copy>/src:<project>/src`.

## Not kept
- Two crystallizer runs killed at the device's 180 s call limit before they finished; their split reruns (v6a-v6e2)
  are kept.
- The probes' scratch worlds under /tmp.

## Open defects
D-10, D-11 and D-20 stay open until fixed and verified, each in its own draft backlog ticket:
`tickets/tasks/backlog/2026-10-10_deny_file_access_under_safe_codegen_task.md`,
`tickets/tasks/backlog/2026-10-10_enforce_import_policy_on_dynamic_imports_task.md` and
`tickets/tasks/backlog/2026-10-10_refuse_materializing_over_live_modules_task.md`.
