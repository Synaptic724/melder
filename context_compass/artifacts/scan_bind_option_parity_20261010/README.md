# Evidence pack: scan_bind_option_parity turn-in (2026-10-10)

Ticket: `tickets/tasks/completed/2026-10-08_restore_scan_bind_option_parity_task.md`, landed at Melder 0.2.8228 by
melder_1. Release note section: "`scan_bind` takes every option `bind` takes, and registers only what a module
declares" in `release_docs/next_version_release.md`.

## Revision and environment
The same tree and environment as the core-protection review's hand-back: HEAD
`66939dfe84e41e51f41f4bc4461ad1690907e909` on `codex_features2` plus the working-tree delta, CPython 3.14.7
free-threading build with `-X gil=0`, pytest 9.1.1. See `../core_protection_review_20261010/env/` and
`../core_protection_review_20261010/tree/tree_delta.txt`. Nothing committed or pushed.

## Contents
- `diffs/scan_bind_authored.diff`: every authored file of the lane against HEAD - `scan.py`, the `Spellbook.scan`
  docstring, `__version__.py`, README, the release note, src_architecture, src_components, the scan and spellbook
  graph descriptors, the two new test files and the three patch docs at their archived path
  (`system_docs/patches/completed/scan_bind_option_parity_2026_10_10/`).
- `diffs/tests_components_scan_bind_part.diff`: the lane's part of tests_components (HEAD to the state after this lane,
  09:49Z); the review lane's part is in the review's pack.
- `file_manifest.md`: SHA256 of the final bytes of every authored and generated file of the lane (indexes, the graph,
  build assets, llm_support src and other bundles). Generated files are listed, not diffed.
- `runs/`: v1 focused set (409 passed), v3a unit spellbook (2343 passed), v4 component spellbook (799 passed), v5
  integration spellbook (613 passed, 2 skipped, 2 xpassed) and v15, the focused set again after the closure (409
  passed). Commands, junit XML and the whole-tree runs are in the review's pack.

The red/green history is in the ticket: 54 of the 63 new tests failed on the old `scan.py` (Note 11) and all pass
after the change (Notes 13 and 18). Owner-owed: the commits ("Commit Grouping" A in the review ticket), the Windows
tiers and hosted CI (Not run).
