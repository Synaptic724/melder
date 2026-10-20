Scratch evidence of the 0.2.8231 landing (melder_1, 2026-10-11). Ticket:
context_compass/tickets/tasks/2026-10-11_prove_and_fix_cross_object_lock_gaps_task.md

Landed change set (applied to the working tree after the scratch runs; byte-identical to the cand tree):
  apply_0_2_8231.py        src edits: ward emissions and contract reads (a)/(b) and the listing deadlock, cleanup_spell
                           through Spellbook._dispose_spell, Spellbook._find_contracted_spell_by_id by key, the Aether
                           frame view and the AethericFrame probes (c), spells_in_index one update per Book set (c2)
  apply_test_updates.py    existing unit tests whose assertions pinned changed behaviour (the kept frame lock; the
                           contract listing resolving through the Book)
  install_new_tests.py     copies newtests/*.py into tests/ with their neighbours' line endings (CRLF)
  land_docs_0_2_8231.py    src_architecture and src_components (the release note was edited separately)
  src_0.2.8231.diff, tests_0.2.8231.diff   cand against the 0.2.8230 working tree (base)
  run_part.sh              full-tree chunk runner (TMPDIR on /tmp)
  patch_docs_v1/           the first-cut patch docs, before the v2/v3 design (Note 12)
  runs/                    new tests red on base / green on cand (gil 0 and 1), repeats, the base deadlock run,
                           full tree on cand (summary_full_cand_0_2_8231_v3_gil0.txt; the v2 summary is history),
                           graph extract/accept/assemble logs

Cut history: v1 snapshotted the frame registry per bind; v2 (owner direction: no per-call snapshot where an O(1) read
exists) published a frame view, keyed the contract reads and fixed the listing deadlock; v3 made the frame probes O(1)
per index without dead guards and copied each Book's id set in one call (Note 10).
