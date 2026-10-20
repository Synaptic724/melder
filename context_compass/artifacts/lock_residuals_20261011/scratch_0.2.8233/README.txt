Scratch evidence of the 0.2.8233 landing (melder_1, 2026-10-11). Ticket:
context_compass/tickets/tasks/2026-10-11_close_lock_residuals_and_evaluate_mediator_admission_task.md (Notes 9-16)

Landed change set (copied into the working tree from /tmp/cc_res/cand; byte-identical):
  apply_0_2_8233.py           src edits: Spell.cleanup decides under the spell lock and runs the Book removal outside it,
                              under a per-spell removal lock (`_direct_removal_route`, slot `_removal_lock`);
                              Spellbook.cleanup_and_remove_spell re-checks a Book torn down while it waits; the
                              cleanup_spell / _dispose_spell lock-order text corrected
  newtests/                   tests/component/melder/spellbook/test_spellbook_component_direct_spell_cleanup_lock_order.py
                              (CRLF in the tree)
  deadlock_probe.py           forces the old interleaving through public calls: HANG on 0.2.8232 against root teardown
                              and conjure (GIL off and on), completes on the cut (runs/deadlock_probe_gil*.log)
  remap_citations_0_2_8233.py keeps every path:line citation into spell.py and spellbook.py pointing where it pointed
  land_docs_0_2_8233.py       src_architecture and src_components (invariant, failure mode, component rules, code map,
                              handoff)
  graph_semantics_0_2_8233.py the Spell and Spellbook node lines (and Spell's `_removal_lock`); then graph_walker --accept
                              and assemble
  bench_0_2_8233.py           bind, direct cleanup, root teardown and warm meld cost, base vs cut, interleaved
  src_0.2.8233.diff           against the 0.2.8232 working tree (/tmp/cc_res/base)
  run_part.sh                 full-tree chunk runner (TMPDIR on /tmp)
  runs/                       new tests red on base / green on cand (gil 0 and 1), 20 repeats, full tree on cand,
                              benchmarks, deadlock probe, citation remap, index, graph extract/accept/assemble logs,
                              post-landing suites on the working tree, asset and llm_support build and check logs
