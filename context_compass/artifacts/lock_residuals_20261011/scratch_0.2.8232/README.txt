Scratch evidence of the 0.2.8232 landing (melder_1, 2026-10-11). Ticket:
context_compass/tickets/tasks/2026-10-11_close_lock_residuals_and_evaluate_mediator_admission_task.md (Notes 2-7)

Landed change set (copied into the working tree from /tmp/cc_res/cand; byte-identical):
  apply_0_2_8232.py           src edits: find_contracted_spell and Conduit.inspect_spell lock-free with a one-call copy (A, D),
                              Spellbook.inspect_spell lock scope and frame-walk copy (B, D), the in-flight disposal mark in
                              _dispose_spell with its field and cleanup (C), the corrected nesting comment (F)
  newtests/                   tests/component/melder/aether/conduit/test_conduit_component_lock_residuals.py (CRLF in the tree)
  land_docs_0_2_8232.py       src_architecture and src_components (invariant, failure mode, component rules, code map, handoff)
  remap_citations_0_2_8232.py keeps every path:line citation into the two changed files pointing where it pointed before
                              (several were already stale at 0.2.8231; they stay as they were, ticket Note 7)
  graph_semantics_0_2_8232.py the Spellbook and Conduit node responsibilities; then graph_walker --accept and assemble
  src_0.2.8232.diff, tests_0.2.8232.diff   against the 0.2.8231 working tree (/tmp/cc_res/base)
  run_part.sh                 full-tree chunk runner (TMPDIR on /tmp)
  bench_0_2_8232.py, claim_overhead_micro.py   cost of the three changed calls and of the disposal mark alone
  runs/                       new tests red on base / green on cand (gil 0 and 1), 20 repeats, full tree on cand, benchmarks,
                              graph extract/accept/assemble logs, post-landing suites on the working tree
The residual stress and its base/cand logs are one level up (residual_stress.py, runs/).
