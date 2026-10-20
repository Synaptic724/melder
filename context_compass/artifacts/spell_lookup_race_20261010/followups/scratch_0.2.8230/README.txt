Scratch evidence of the 0.2.8230 landing (melder_1, 2026-10-11). Ticket:
context_compass/tickets/tasks/2026-10-11_close_remaining_spell_map_races_task.md

Landed change set (applied to the working tree after the scratch runs):
  apply_0_2_8230.py        src edits: items 1-2 (spell-map walks, has_spell/probe, details) and the item-3 docstrings
  apply_test_updates.py    existing unit tests whose stubs modelled the old walks
  install_new_tests.py     copies newtests/*.py into tests/ with their neighbours' line endings
  land_docs_0_2_8230.py    src_architecture, src_components and the running release note
  build_0_2_8230_script.py how apply_0_2_8230.py was cut from the first cut (below)
  src_0.2.8230.diff, tests_0.2.8230.diff   scratch tree (cand) against the 0.2.8229 working tree (base)
  run_part.sh              full-tree chunk runner (TMPDIR on /tmp)
  runs/                    new tests red on base / green on cand (gil 0 and 1), full tree on cand, graph logs

Superseded first cut (kept as history): apply_followups.py returned None from the Conduit spell lookups
(Aether._find_conduit_by_spell_id); the owner chose to keep the ValueError and document it (ticket Note 11).
runs/updated_unit_files_cand_gil0.log is that first cut's run of the updated unit files (563 passed, including
three test_aether.py tests that were dropped with it).
