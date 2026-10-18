# Blast radius of S1 + S2 (2026-10-18, melder_0)

A /tmp mirror of the repository at 0.2.8255 with the prototype code digest (decision B) as the spell_id and
S2's binding hash in the creation cache's structural key and world stamp (mirror/_br_digest.py and the two
diffs). The whole tree ran with the GIL off and on (runs/br2_*), against the unpatched baseline (runs/base_*);
runs/br_* is S1 alone (unit and component tiers). tally.py and tally_output.txt count it.

Result: 14542 tests ran per GIL mode; 126 failed, 25 of them in the baseline (melder_1's S8 and S9 red tests);
101 new failures, the same set with the GIL off and on; none is a Melder defect.

## One object registered twice - bind/bind_inactive collision (88)

The test registers one class (or one object) twice - under two binding names, two existences, two frames or
as a staged version - which strict uniqueness refuses at bind: "Spell ID collision detected". Rewrite: two
distinct classes (or subclasses) where the test needs two registrations; a refusal test where one object
registered twice is the point.

- tests/component/melder/aether/conduit/test_conduit_component_policy_reader.py::test_the_member_the_reader_returns_is_accepted_by_the_writer
- tests/component/melder/aether/test_configure_aether_frame_posture_component.py::test_codegen_rooms_need_both_knobs_and_the_door_now_supplies_both
- tests/component/melder/spellbook/test_bind_lifecycle_hooks.py::test_append_clear_and_register_again_preserves_order[activation]
- tests/component/melder/spellbook/test_bind_lifecycle_hooks.py::test_append_clear_and_register_again_preserves_order[post]
- tests/component/melder/spellbook/test_bind_lifecycle_hooks.py::test_append_clear_and_register_again_preserves_order[pre]
- tests/component/melder/spellbook/test_inherited_disposal_binding.py::test_inactive_binding_resolves_inherited_cleanup_before_fingerprinting
- tests/component/melder/spellbook/test_ordered_disposal_binding.py::test_each_binding_uses_its_own_explicit_names[False]
- tests/component/melder/spellbook/test_ordered_disposal_binding.py::test_each_binding_uses_its_own_explicit_names[True]
- tests/component/melder/spellbook/test_ordered_disposal_binding.py::test_staged_binding_preserves_its_own_order_and_index_selection[False-False]
- tests/component/melder/spellbook/test_ordered_disposal_binding.py::test_staged_binding_preserves_its_own_order_and_index_selection[False-True]
- tests/component/melder/spellbook/test_ordered_disposal_binding.py::test_staged_binding_preserves_its_own_order_and_index_selection[True-False]
- tests/component/melder/spellbook/test_ordered_disposal_binding.py::test_staged_binding_preserves_its_own_order_and_index_selection[True-True]
- tests/component/melder/spellbook/test_spellbook_component_resolvable_registration.py::test_fluent_capability_does_not_leak_to_next_registration[False]
- tests/component/melder/spellbook/test_spellbook_component_resolvable_registration.py::test_fluent_capability_does_not_leak_to_next_registration[True]
- tests/component/melder/spellbook/test_spellbook_component_resolvable_registration.py::test_inactive_bind_defaults_to_true_independently_of_selected_mode[False]
- tests/component/melder/spellbook/test_spellbook_component_resolvable_registration.py::test_inactive_bind_defaults_to_true_independently_of_selected_mode[True]
- tests/component/melder/spellbook/test_spellbook_component_resolvable_registration.py::test_parked_capability_is_per_version_and_does_not_change_selection[False-False]
- tests/component/melder/spellbook/test_spellbook_component_resolvable_registration.py::test_parked_capability_is_per_version_and_does_not_change_selection[False-True]
- tests/component/melder/spellbook/test_spellbook_component_resolvable_registration.py::test_parked_capability_is_per_version_and_does_not_change_selection[True-False]
- tests/component/melder/spellbook/test_spellbook_component_resolvable_registration.py::test_parked_capability_is_per_version_and_does_not_change_selection[True-True]
- tests/experimentation/test_borrower_provider_validation_experiment.py::test_characterize_provider_validation_boundary[2-meld_only]
- tests/experimentation/test_borrower_provider_validation_experiment.py::test_characterize_provider_validation_boundary[2-no_validation]
- tests/experimentation/test_borrower_provider_validation_experiment.py::test_characterize_provider_validation_boundary[2-resolution_only]
- tests/experimentation/test_borrower_provider_validation_experiment.py::test_characterize_provider_validation_boundary[2-structural_refresh]
- tests/integration/melder/aether/conduit/test_annotation_category_collision_integration.py::test_guard_two_providers_of_the_annotated_type_still_raise_ambiguity
- tests/integration/melder/aether/conduit/test_index_moves_by_spell_id_integration.py::test_index_move_refuses_another_books_spell_id[add_to_spell_index]
- tests/integration/melder/aether/conduit/test_index_moves_by_spell_id_integration.py::test_index_move_refuses_another_books_spell_id[remove_from_spell_index]
- tests/integration/melder/aether/conduit/test_notch_spell_by_id_integration.py::test_notch_refuses_a_version_another_book_owns_and_keeps_the_index_active
- tests/integration/melder/aether/test_aether_integration_cluster_membership_transactions.py::test_add_three_conduits_tracks_all_members
- tests/integration/melder/aether/test_aether_integration_cluster_membership_transactions.py::test_remove_conduit_drops_its_shared_root_entry
- tests/integration/melder/aether/test_aether_integration_cluster_membership_transactions.py::test_remove_one_of_three_keeps_the_rest
- tests/integration/melder/aether/test_aether_integration_cluster_membership_transactions.py::test_two_cluster_spell_conduits_each_register_a_shared_root
- tests/integration/melder/aether/test_aether_integration_cluster_transactions_concurrency.py::test_concurrent_joins_across_two_clusters_are_isolated
- tests/integration/melder/aether/test_aether_integration_cluster_transactions_concurrency.py::test_concurrent_joins_are_serialized_with_no_lost_members
- tests/integration/melder/aether/test_aether_integration_cluster_transactions_concurrency.py::test_concurrent_joins_register_all_shared_roots_without_deadlock
- tests/integration/melder/aether/test_aether_integration_cluster_transactions_concurrency.py::test_concurrent_joins_to_one_cluster_track_every_member
- tests/integration/melder/aether/test_aether_integration_cluster_transactions_concurrency.py::test_concurrent_leaves_empty_the_cluster
- tests/integration/melder/aether/test_aether_integration_cluster_transactions_concurrency.py::test_concurrent_mixed_join_and_leave_reach_consistent_state
- tests/integration/melder/aether/test_aether_integration_cluster_transactions_concurrency.py::test_concurrent_reads_during_membership_churn_never_crash
- tests/integration/melder/aether/test_non_resolvable_graph_replay.py::test_checkpoint_replay_preserves_false_and_reemits_it
- tests/integration/melder/aether/test_non_resolvable_graph_replay.py::test_graft_preserves_active_and_parked_capability
- tests/integration/melder/aether/test_non_resolvable_graph_replay.py::test_nexus_exposes_definition_reference_and_base_relationships
- tests/integration/melder/conduit/test_conduit_integration_managed_quantity_pool.py::test_a_post_conjure_bind_and_bind_inactive_each_get_their_pool
- tests/integration/melder/conduit/test_conduit_integration_managed_spell_quantity.py::test_roots_in_two_frames_dispense_from_their_own_pools
- tests/integration/melder/conduit/test_conduit_integration_managed_spell_quantity.py::test_two_binding_names_in_one_root_dispense_from_two_pools
- tests/integration/melder/conduit/test_conduit_integration_managed_transfer.py::test_a_failed_move_leaves_a_parked_version_with_the_owner
- tests/integration/melder/conduit/test_conduit_integration_managed_transfer.py::test_a_failed_transfer_without_a_move_leaves_a_parked_version_with_the_owner
- tests/integration/melder/conduit/test_conduit_integration_managed_transfer.py::test_a_move_leaves_no_pool_registered_under_the_owner
- tests/integration/melder/conduit/test_conduit_integration_managed_transfer.py::test_a_parked_unique_version_moved_and_notched_in_stores_its_object_in_the_target
- tests/integration/melder/conduit/test_conduit_integration_managed_transfer.py::test_a_parked_version_moved_and_notched_in_leases_from_its_moved_pool
- tests/integration/melder/conduit/test_conduit_integration_managed_transfer.py::test_no_move_with_a_parked_version_leases_from_the_target_after_a_notch
- tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py::test_a_notch_back_reactivates_a_version_grant_and_its_consumer_rebuilds_with_one_pass
- tests/integration/melder/conduit/test_conduit_integration_release_managed_spell.py::test_a_post_conjure_bind_registers_and_a_notch_moves_the_releases
- tests/integration/melder/conduit/test_conduit_integration_release_managed_spell.py::test_two_binding_names_in_one_root_need_a_spell_id
- tests/integration/melder/conduit/test_conduit_integration_release_managed_spell.py::test_two_roots_are_told_apart_by_conduit_including_a_lesser
- tests/integration/melder/crystallizer/test_managed_spell_options_record_integration.py::test_a_graft_rebinds_the_selected_and_parked_versions_with_their_options
- tests/integration/melder/crystallizer/test_managed_spell_options_record_integration.py::test_a_restore_rebinds_both_versions_with_their_options
- tests/integration/melder/crystallizer/test_managed_spell_options_record_integration.py::test_the_crystal_records_both_versions_options
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_cached_restore_preserves_order_and_actual_cleanup[False-False]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_cached_restore_preserves_order_and_actual_cleanup[False-True]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_cached_restore_preserves_order_and_actual_cleanup[True-False]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_cached_restore_preserves_order_and_actual_cleanup[True-True]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_crystal_and_json_preserve_distinct_member_orders[False]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_crystal_and_json_preserve_distinct_member_orders[True]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_graft_preserves_members_and_receiving_book_order[fresh-False-False]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_graft_preserves_members_and_receiving_book_order[fresh-False-True]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_graft_preserves_members_and_receiving_book_order[fresh-True-False]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_graft_preserves_members_and_receiving_book_order[fresh-True-True]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_graft_preserves_members_and_receiving_book_order[merge-False-False]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_graft_preserves_members_and_receiving_book_order[merge-False-True]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_graft_preserves_members_and_receiving_book_order[merge-True-False]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_graft_preserves_members_and_receiving_book_order[merge-True-True]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_graft_preserves_members_and_receiving_book_order[merge_adopt-False-False]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_graft_preserves_members_and_receiving_book_order[merge_adopt-False-True]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_graft_preserves_members_and_receiving_book_order[merge_adopt-True-False]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_graft_preserves_members_and_receiving_book_order[merge_adopt-True-True]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_merge_does_not_adopt_a_skipped_resident_selection[False]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_merge_does_not_adopt_a_skipped_resident_selection[True]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_restore_changed_ids_preserves_anchor_and_exact_selected_member[False]
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_restore_changed_ids_preserves_anchor_and_exact_selected_member[True]
- tests/integration/melder/spellbook/test_binding_name_case_parity_integration.py::test_capitalized_spellmap_binding_name_no_longer_fails_to_resolve[explicit-spell-lower]
- tests/integration/melder/spellbook/test_binding_name_case_parity_integration.py::test_capitalized_spellmap_binding_name_no_longer_fails_to_resolve[explicit-spell]
- tests/integration/melder/spellbook/test_binding_name_case_parity_integration.py::test_capitalized_spellmap_binding_name_no_longer_fails_to_resolve[lower]
- tests/integration/melder/spellbook/test_binding_name_case_parity_integration.py::test_capitalized_spellmap_binding_name_no_longer_fails_to_resolve[reported]
- tests/integration/melder/spellbook/test_binding_name_case_parity_integration.py::test_capitalized_spellmap_binding_name_no_longer_fails_to_resolve[upper-frame-and-name]
- tests/integration/melder/spellbook/test_managed_bind_options_integration.py::test_conduit_bind_and_bind_inactive_forward_the_options
- tests/integration/melder/spellbook/test_provider_artifact_ownership.py::test_provider_survives_repeated_borrower_validation_and_cleanup[2-2]
- tests/integration/melder/spellbook/test_spellbook_integration_resolution_contract_more.py::test_type_hint_di_ambiguous_concrete_class_raises

## One object registered twice - conjure integrity, another frame (1)

The same class bound in two frames' Books under process-wide spell ids: conjure refuses the second ("Conjure
refused: ... already registered"). Rewrite: two classes.

- tests/integration/melder/aether/test_aether_integration_frames.py::test_aether_conduit_cloud_isolated_by_frame

## S2 structural format and stamp pins (expected; S2 moves PAYLOAD_FORMAT to 2 and the stamp lines) (5)

- tests/unit/melder/spellbook/spell_compiler/structural_snapshot/test_structural_snapshot.py::test_build_payload_renders_phase3_and_phase4_rows_from_durable_state
- tests/unit/melder/spellbook/spell_compiler/structural_snapshot/test_structural_snapshot.py::test_structural_key_holds_format_id_and_sorted_refs
- tests/unit/melder/spellbook/spell_compiler/structural_snapshot/test_structural_snapshot.py::test_world_stamp_changes_with_pool_posture_or_borrowed_set
- tests/unit/melder/spellbook/spell_compiler/structural_snapshot/test_structural_snapshot.py::test_world_stamp_digests_sorted_pool_posture_and_borrowed_ids
- tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_capture.py::test_conjure_end_captures_a_structural_payload_per_owned_spell

## Bind.sha256_profile used as the oracle (the function is retired; the inspector and SpellCodeDigest replace it) (2)

- tests/unit/melder/spellbook/bind/test_bind_managed_spell_options.py::test_managed_settings_do_not_change_the_spell_id
- tests/unit/melder/spellbook/bind/test_bind_managed_spell_options.py::test_spell_id_inspector_matches_the_bind_fingerprint_for_a_managed_class

## A binding change is asserted to move the spell_id (premise reversed: the binding hash moves instead) (3)

- tests/component/melder/spellbook/test_ordered_disposal_binding.py::test_resolved_order_changes_sha_but_unmatched_names_do_not
- tests/integration/melder/spellbook/test_managed_bind_options_integration.py::test_a_managed_binding_changes_the_spell_id_and_its_settings_do_not
- tests/integration/melder/crystallizer/test_ordered_disposal_replay.py::test_changed_id_restore_regrants_contract_details

## Asserts the opposite of the owner's call 1 (a base-class change moves its subclasses' spell_ids) (1)

- tests/component/melder/spellbook/test_inherited_disposal_binding.py::test_unrequested_base_callable_does_not_change_binding_identity

## Refusal order and message (the collision refusal now precedes the frame claim's) (1)

- tests/component/melder/spellbook/test_spellbook_component_resolvable_registration.py::test_false_does_not_create_another_active_binding_slot

## S1 alone (runs/br_*, unit and component tiers)

With the code digest but no binding hash in the cache, 12 more tests failed in the component tier - 11 in
test_conduit_component_purge.py and one in test_conduit_component_spellspace_creations.py - and pass with
S2: their parametrizations bind one class under several existences, so one spell_id named several bindings
and a creation-cache bundle built for one binding was replayed for another (a purge returning 0, a `many`
meld returning one object, an existence's store missing). This is invariant 7 of the architecture patch:
S1 cannot land without S2's keys.

