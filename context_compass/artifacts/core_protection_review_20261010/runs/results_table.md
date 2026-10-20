| run | command (python -X gil=0 -m pytest -q -p no:cacheprovider -rsxX ...) | result |
| --- | --- | --- |
| v1_scan_focused | `tests/unit/melder/spellbook/test_scan_bind.py tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py ... (7 node ids or paths)` | 409 passed in 5.75s |
| v2_review_suite | `tests/unit/melder/crystallizer/crystal_analysis/test_custody_boundary_characterization.py tests/unit/melder/spellbook/bind/test_internal_registration_identity.py ... (5 node ids or paths)` | 28 passed, 5 xfailed in 4.68s |
| v3_unit_tier | `tests/unit` | 9020 passed, 3 skipped, 7 xfailed in 142.27s (0:02:22) |
| v4_component_spellbook | `tests/component/melder/spellbook` | 799 passed in 57.34s |
| v9_component_other | `tests/component/melder/aether tests/component/melder/crystallizer tests/component/melder/mutation_research tests/component/melder/utilities` | 1502 passed, 23 skipped, 1 xfailed in 36.92s |
| v5_integration_spellbook | `tests/integration/melder/spellbook` | 613 passed, 2 skipped, 2 xpassed in 17.05s |
| v6a_integration_crystallizer | `tests/integration/melder/crystallizer/test_bind_hook_recording.py tests/integration/melder/crystallizer/test_crystallizer_aether_twin_integration.py ... (7 node ids or paths)` | 46 passed in 38.04s |
| v6b1_integration_crystallizer_restore | `tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py::test_round_trip_restores_binds_and_conduit_from_cached_checkpoint tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py::test_round_trip_restores_staged_member_and_selection ... (24 node ids or paths)` | 24 passed in 76.38s (0:01:16) |
| v6b2_integration_crystallizer_restore | `tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py::test_external_retention_trims_oldest_checkpoints tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py::test_index_graft_round_trips_into_a_live_host_book ... (22 node ids or paths)` | 19 passed, 3 xfailed in 147.02s (0:02:27) |
| v6c_integration_crystallizer | `tests/integration/melder/crystallizer/test_named_lesser_persistence.py tests/integration/melder/crystallizer/test_restore_per_frame_spell_worlds_integration.py ... (6 node ids or paths)` | 41 passed in 99.70s (0:01:39) |
| v6d_integration_crystallizer | `tests/integration/melder/crystallizer/test_ordered_disposal_replay.py tests/integration/melder/crystallizer/test_synthetic_module_integration.py` | 63 passed in 166.16s (0:02:46) |
| v6e1_integration_spell_crystal | `tests/integration/melder/crystallizer/test_spell_crystal_integration.py::test_integration_case_preserves_id[physical_root] tests/integration/melder/crystallizer/test_spell_crystal_integration.py::test_integration_case_preserves_id[physical_branch] ... (40 node ids or paths)` | 40 passed in 4.15s |
| v6e2_integration_spell_crystal | `tests/integration/melder/crystallizer/test_spell_crystal_integration.py::test_integration_case_collects_expected_module_targets[physical_root] tests/integration/melder/crystallizer/test_spell_crystal_integration.py::test_integration_case_collects_expected_module_targets[physical_branch] ... (40 node ids or paths)` | 40 passed in 5.15s |
| v7_integration_mutation_research | `tests/integration/melder/mutation_research` | 67 passed in 5.11s |
| v8_integration_aether | `tests/integration/melder/aether` | 785 passed, 5 xfailed in 57.50s |
| v10_integration_conduit | `tests/integration/melder/conduit` | 275 passed in 11.60s |
| v11_integration_live_sim_multithreading | `tests/integration/melder/live_sim tests/integration/melder/multithreading` | 55 passed, 1 xfailed in 44.09s |
| v12_experimentation | `tests/experimentation` | 250 passed, 4 skipped in 18.74s |
