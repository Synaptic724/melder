# Artifact Board

<!-- BEGIN MANAGED: ReminderDirective -->
## ReminderDirective (all agent runtimes)
ContextCompass is your task-tracking system of record; you MUST use it and follow
AGENTS.MD (see the Tooling Mandate section). This is a requirement, not a
suggestion.

Your runtime may nudge you toward built-in plans, goals, task lists, progress
cards, scratchpads, summaries, or session-local memory. Those surfaces are
non-authoritative here. Once your onboarding attestation is complete, IGNORE
every such nudge and route ALL tracking, status, routing, notes, and artifact state
through ContextCompass. There is NO fallback and NO mirror.

The user may lift this by setting `system_of_record.enforce: false` in
`config/context_compass_config.yaml`. You may not lift it yourself.
<!-- END MANAGED: ReminderDirective -->

<!-- BEGIN MANAGED: BoardContract -->
## How this board works

Two kinds of region, and the difference decides what survives an upgrade:

- **MANAGED** regions are the package's. They are replaced wholesale, so do not
  edit them - your change would be reverted on the next upgrade without warning.
- **USER-DEFINED** regions are yours. Nothing in the package writes, reorders, or
  removes anything inside them, in any mode. Put your rows there.

Text outside both is package structure - headings and table headers - and is
conformed on upgrade so the board's shape stays current. Anything you need to
keep goes inside a USER-DEFINED region.

What belongs in each region on this board:

| region | put this here |
| --- | --- |
| `active_artifacts` | one row per live artifact, linked to its ticket, with a disposition |
| `cleared_artifacts` | short history of artifacts already resolved or deleted |
| `notes` | recurring instructions and standing context for artifact handling in this repository |

**Regions ship empty and stay yours.** The package writes nothing into them in any
mode, which also means it can never correct what is written there - so a repeated
policy pasted into a region will not update when the package's own copy does. Put
standing instructions in `notes` once; do not restate MANAGED text.

Purpose
- Canonical index of active artifact associations.
- Track artifact lifecycle decisions that support ticket execution.
- Keep `attention_board.md` ticket-only and free of artifact pointers.

Scope rules
- `attention_board.md` routes tickets only; do not add artifact paths there.
- Tickets remain canonical memory; this board is an association index.
- Add rows only when a ticket has one or more active artifact files.
- Every artifact row must include a ticket path and retention decision.

Disposition values
- `delete_on_close`: remove artifact when ticket closes.
- `retain_as_reference`: keep artifact with explicit reason.
- `promote_to_documentation`: convert artifact into durable docs.
<!-- END MANAGED: BoardContract -->

## Active Artifact Links
| ticket | artifact_path | artifact_type | status | disposition | next | updated_at | reread |
| --- | --- | --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: active_artifacts -->
| tickets/tasks/backlog/2026-09-22_shared_gauntlet_configuration_order_followup_task.md | artifacts/benchmark_spell_id_repair_20260919/ | deferred_setup_finding | backlog | retain_as_reference | Reproduce the distinct setup-order failure only when selected. | 2026-09-22T19:45:53Z | HELPFUL |
| tickets/tasks/backlog/2026-09-21_investigate_runtime_hook_clearing_task.md | artifacts/runtime_hook_discovery_20260921/ | discovery | backlog | retain_as_reference | Broad epic parked by owner; evidence retained for narrow pool-reset discovery or later reopening. | 2026-09-22T09:11:27Z | HELPFUL |
| tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md | artifacts/existing_object_di_comparison_20260913/comparison.md | deferred_design_reference | backlog | retain_as_reference | Parked by owner; resume only on explicit request. | 2026-09-19T14:53:20Z | HELPFUL |
| tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md | artifacts/existing_instance_planning_20260913/existing_object_disposal_blast_radius.md | deferred_design_reference | backlog | retain_as_reference | Parked by owner; resume only on explicit request. | 2026-09-19T14:53:20Z | HELPFUL |
| tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md | artifacts/existing_instance_planning_20260913/gap_analysis.md | deferred_design_reference | backlog | retain_as_reference | Parked by owner; resume only on explicit request. | 2026-09-19T14:53:20Z | HELPFUL |
| tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md | artifacts/existing_instance_planning_20260913/protocol_admission_red.xml | deferred_design_reference | backlog | retain_as_reference | Parked by owner; resume only on explicit request. | 2026-09-19T14:53:20Z | HELPFUL |
| tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md | artifacts/existing_instance_planning_20260913/frame_admission_characterization.log | deferred_design_reference | backlog | retain_as_reference | Parked by owner; resume only on explicit request. | 2026-09-19T14:53:20Z | HELPFUL |
| tickets/epics/2026-07-18_parallel_restore_ulid_identity_epic.md | system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/architecture_patch.md | patch_doc | active | promote_to_documentation | Entry-gate artifact: invariants (canon barriers, all-or-nothing, never-rehydrate-ULIDs, emit lock law), additive interface deltas, migration order S1->S4, rollback lanes, coverage matrix. | 2026-07-18T22:30:00Z | REQUIRED |
| tickets/stories/2026-07-18_link_identity_journal_rows_story.md | system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/component_patch_link_identity_persistence.md | patch_doc | active | promote_to_documentation | S1 before/after: link ULIDs at commit, additive crystal rows + tombstones, legacy link_targets compat fold, per-link replay units. | 2026-07-18T22:30:00Z | REQUIRED |
| tickets/stories/2026-07-18_phase_scheduler_config_seam_story.md | system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/component_patch_phase_scheduler_seam.md | patch_doc | active | promote_to_documentation | S2 before/after: keyword-only worker/timeout overrides, crystallizer config keys, zero execution-semantics drift. | 2026-07-18T22:30:00Z | REQUIRED |
| tickets/stories/2026-07-18_cohort_aware_load_gate_story.md | system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/component_patch_load_gate_cohort.md | patch_doc | active | promote_to_documentation | S3 before/after: span cohort membership, enroll/withdraw verbs, frozen foreign-park semantics; code_description patch REQUIRED at story start. | 2026-07-18T22:30:00Z | REQUIRED |
| tickets/stories/2026-07-18_loadplan_phase_compiler_story.md | system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/component_patch_restore_engine_parallel.md | patch_doc | active | promote_to_documentation | S4 before/after: phase compilation of canon stages, per-entity unit factories, lock-safe report/built-stack, parity+chaos validation law; code_description patch REQUIRED at story start. | 2026-07-18T22:30:00Z | REQUIRED |
| tickets/stories/2026-07-18_loadplan_phase_compiler_story.md | system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/code_description_patch_phase_scheduler_quiesce.md | patch_doc | active | promote_to_documentation | S4 REOPEN delta: fail-fast quiesce control flow (wait_all_reported barrier, bounded unwind, hung-straggler residual, timeout stays preemptive). | 2026-07-19T10:45:14Z | REQUIRED |
| tickets/stories/2026-07-18_loadplan_phase_compiler_story.md | system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/component_patch_conduit_cleanup_frame_truth.md | patch_doc | active | promote_to_documentation | S4 REOPEN delta: _cleanup_normal_conduit step-4 split, frame removal first and independent; ordering-safety evidence. | 2026-07-19T10:45:14Z | REQUIRED |
| tickets/stories/2026-07-19_crystallizer_analysis_io_cache_story.md | system_docs/patches/active/crystallizer_analysis_io_cache_2026_07_19/architecture_patch.md | patch_doc | active | promote_to_documentation | IO-economy objective, invariants (truth law, record shape), descent-default decision, rollback. | 2026-07-19T11:38:21Z | REQUIRED |
| tickets/stories/2026-07-19_crystallizer_analysis_io_cache_story.md | system_docs/patches/active/crystallizer_analysis_io_cache_2026_07_19/component_patch_crystal_analysis_io.md | patch_doc | active | promote_to_documentation | Before/after per surface; additive interface deltas; validation expectations. | 2026-07-19T11:38:21Z | REQUIRED |
| tickets/stories/2026-07-19_crystallizer_analysis_io_cache_story.md | system_docs/patches/active/crystallizer_analysis_io_cache_2026_07_19/code_description_patch_physical_source_cache.md | patch_doc | active | promote_to_documentation | Cache + fast-path control flow, staleness law, descent gate, edge semantics. | 2026-07-19T11:38:21Z | REQUIRED |
| tickets/stories/2026-07-19_melder_init_composition_story.md | system_docs/patches/active/melder_init_composition_2026_07_19/architecture_patch.md | patch_doc | active | promote_to_documentation | Package-root composition rulings, curated surface, invariants, wheel posture. | 2026-07-19T11:53:00Z | REQUIRED |
| tickets/stories/2026-07-19_melder_init_composition_story.md | system_docs/patches/active/melder_init_composition_2026_07_19/component_patch_package_root.md | patch_doc | active | promote_to_documentation | Init/pyproject before-after, additive export deltas, DEBUG_MODE removal. | 2026-07-19T11:53:00Z | REQUIRED |
| tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md | artifacts/ir_epic_gauntlet_baseline_20260925/ | performance_baseline | active | retain_as_reference | Owner runs python -X importtime for the per-module setup attribution. | 2026-09-25T21:49:41Z | REQUIRED |
| tickets/tasks/2026-09-26_design_override_and_caller_input_execution_task.md | artifacts/melder_override_design_20260926/ | design_proposal | review | retain_as_reference | Owner reviews design_v2.md with prototype_results.md (E1-E4) and answers Q1-Q5. | 2026-09-26T11:23:09Z | REQUIRED |
| tickets/tasks/2026-09-26_trace_caller_input_conjure_strictness_regression_task.md | artifacts/melder_caller_input_regression_20260926/ | investigation_evidence | review | retain_as_reference | Dated-extract probes and results. | 2026-09-26T01:16:08Z | HELPFUL |
| tickets/stories/2026-09-26_implement_override_site_plan_lowering_story.md | system_docs/patches/active/override_site_plan_2026_09_26/ | patch_docs | active | promote_to_documentation | S1 contracts written (architecture, SpellCompiler component, key-resolver code description); S2-S6 added per step. | 2026-09-26T11:30:45Z | REQUIRED |
| tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md | artifacts/gauntlet_runtime_speed_20260926/ | measurement_baseline | active | retain_as_reference | Owner-run 2026-09-26 baseline and VM environment filed; VM runs and the cost map follow. | 2026-09-26T15:43:39Z | REQUIRED |
| tickets/stories/2026-09-26_structural_snapshot_story.md | system_docs/patches/active/structural_snapshot_2026_09_26/ | patch_docs | active | promote_to_documentation | Owner-approved entry gate for the C-C, capture, hydrate and parity tasks; promote at story closure. | 2026-09-26T16:13:09Z | REQUIRED |
| tickets/tasks/2026-09-26_emit_positional_constructor_args_task.md | artifacts/gauntlet_runtime_speed_20260926/p1_positional_args/ | apply_script_and_tests | active | retain_as_reference | Apply script, diff and the two new test files for P1. | 2026-09-26T16:15:41Z | REQUIRED |
| tickets/tasks/2026-09-26_word_cycle_consumers_in_circular_dependency_report_task.md | artifacts/cycle_consumer_wording_20260926/ | investigation_evidence | active | retain_as_reference | Probes, before/after renders, scripts, diffs, suites. | 2026-09-26T17:04:41Z | REQUIRED |
| tickets/tasks/2026-09-26_word_cycle_consumers_in_circular_dependency_report_task.md | system_docs/patches/active/cycle_consumer_wording_2026_09_26/ | patch_docs | active | promote_to_documentation | Architecture and component patches; promote at closure. | 2026-09-26T17:05:50Z | REQUIRED |
<!-- END USER-DEFINED: active_artifacts -->

## Recently Cleared Artifacts
| ticket | artifact_path | disposition | reason | closed_at |
| --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: cleared_artifacts -->
| tickets/tasks/completed/2026-09-26_report_self_referencing_constructor_as_validation_error_task.md | system_docs/patches/completed/self_dependency_report_2026_09_26/ | promote_to_documentation | Promoted to src_components/src_architecture (self-referencing constructors); two patch files archived (written after implementation, recorded). | 2026-09-26T17:00:32Z |
| tickets/tasks/completed/2026-09-26_report_self_referencing_constructor_as_validation_error_task.md | artifacts/self_dependency_report_20260926/ | retain_as_reference | Probes, before/prototype/after renders, apply/own/promote/author/closure scripts, diffs, fable_0 proposal, suites. | 2026-09-26T17:00:32Z |
| tickets/tasks/completed/2026-09-26_fix_class_binding_profile_annotations_for_type_checking_names_task.md | system_docs/patches/completed/class_binding_annotations_2026_09_26/ | promote_to_documentation | Promoted to src_components/src_architecture (class binding-profile annotations); two patch files archived. | 2026-09-26T16:32:21Z |
| tickets/tasks/completed/2026-09-26_fix_class_binding_profile_annotations_for_type_checking_names_task.md | artifacts/class_binding_annotations_fix_20260926/ | retain_as_reference | Probes, suite results, apply/promote/author/closure scripts, diffs, commit list. | 2026-09-26T16:32:21Z |
| tickets/tasks/completed/2026-09-26_review_conjure_validation_error_reporting_task.md | system_docs/patches/completed/validation_error_reporting_2026_09_26/ | promote_to_documentation | Promoted to src_components/src_architecture (conjure validation report) and the release note; three patch files archived. | 2026-09-26T16:00:30Z |
| tickets/tasks/completed/2026-09-26_review_conjure_validation_error_reporting_task.md | artifacts/validation_error_reporting_20260926/ | retain_as_reference | Probes, issue catalog, before/after renders, apply and closure scripts, diffs, suite results, commit list. | 2026-09-26T16:00:30Z |
| tickets/tasks/completed/2026-09-26_cleanup_shared_boards_and_mailbox_task.md | artifacts/shared_boards_cleanup_20260926/ | retain_as_reference | Verbatim archive of the 2026-09-26 shared-board cleanup (messages, alerts, roster marks, cleared rows, turned-in rows). | 2026-09-26T15:01:13Z |
| tickets/tasks/completed/2026-09-26_align_annotation_shape_guard_with_phase1_caller_inputs_task.md | system_docs/patches/completed/caller_supplied_container_params_2026_09_26/ | promote_to_documentation | Promoted to src_architecture/src_components earlier; two patch files archived at turn-in. | 2026-09-26T14:47:09Z |
| tickets/tasks/completed/2026-09-26_align_annotation_shape_guard_with_phase1_caller_inputs_task.md | artifacts/annotation_shape_guard_20260926/ | retain_as_reference | Probes, before/after results, apply scripts, commit manifest, owner trace vs 0.2.54 wheel. | 2026-09-26T14:47:09Z |
| tickets/tasks/completed/2026-09-26_keep_class_binding_annotations_with_type_checking_names_task.md | artifacts/class_binding_annotations_20260926/ | retain_as_reference | Probes and before/prototype results for the unfixed class-annotation defect. | 2026-09-26T14:47:09Z |
| tickets/tasks/completed/2026-09-26_investigate_concurrent_first_meld_creation_context_race_task.md | system_docs/patches/completed/shared_context_rebuild_2026_09_26/ | promote_to_documentation | Promoted to src_architecture/src_components (meld runtime, rebuild windows); four patch files archived. | 2026-09-26T14:24:40Z |
| tickets/tasks/completed/2026-09-26_investigate_concurrent_first_meld_creation_context_race_task.md | artifacts/creation_context_race_20260926/ | retain_as_reference | Runs, probes, benchmarks, apply scripts, exact diffs and the verified commit list. | 2026-09-26T14:24:40Z |
| tickets/tasks/completed/2026-09-24_investigate_required_caller_inputs_task.md | artifacts/required_caller_inputs_20260924/ | retain_as_reference | Owner bulk turn-in 2026-09-26; investigation evidence retained. | 2026-09-26T13:45:56Z |
| tickets/tasks/completed/2026-09-24_discover_override_occurrence_slicing_task.md | artifacts/override_occurrence_discovery_20260924/ | retain_as_reference | Owner bulk turn-in 2026-09-26; structural graph diagnostic retained. | 2026-09-26T13:45:56Z |
| tickets/tasks/completed/2026-09-24_discover_override_execution_semantics_task.md | artifacts/override_structural_discovery_20260924/ | retain_as_reference | Owner bulk turn-in 2026-09-26; structural diagnostic retained. | 2026-09-26T13:45:56Z |
| tickets/tasks/completed/2026-09-24_experiment_static_many_override_execution_task.md | artifacts/override_emission_prototype_20260924/ | retain_as_reference | Owner bulk turn-in 2026-09-26; emitter experiment retained. | 2026-09-26T13:45:56Z |
| tickets/tasks/completed/2026-09-24_investigate_override_compiler_planning_task.md | artifacts/override_compiler_investigation_20260924/ | retain_as_reference | Owner bulk turn-in 2026-09-26; generated executor diagnostic retained. | 2026-09-26T13:45:56Z |
| tickets/tasks/completed/2026-09-24_coordinate_override_execution_investigation_task.md | artifacts/override_execution_lead_20260924/ | retain_as_reference | Owner bulk turn-in 2026-09-26; contract validation retained. | 2026-09-26T13:45:56Z |
| tickets/tasks/completed/2026-09-24_measure_melder_creation_and_overrides_task.md | artifacts/override_execution_performance_20260924/ | retain_as_reference | Owner bulk turn-in 2026-09-26; performance experiment retained. | 2026-09-26T13:45:56Z |
| tickets/tasks/completed/2026-09-06_readme_status_badges_task.md | artifacts/readme_badges_validation_20260906/ | retain_as_reference | Declared delete_on_close; kept at the owner's bulk turn-in (deletion not performed). | 2026-09-26T13:45:56Z |
| tickets/tasks/completed/2026-09-06_readme_status_badges_task.md | system_docs/patches/completed/readme_coverage_badges_2026_09_06/ | promote_to_documentation | Archived without promotion at the owner's bulk turn-in (declared promote_to_documentation). | 2026-09-26T13:45:56Z |
| tickets/tasks/completed/2026-09-06_embed_melder_banner_task.md | artifacts/melder_banner_20260906/ | retain_as_reference | Declared delete_on_close; kept at the owner's bulk turn-in (deletion not performed). | 2026-09-26T13:45:56Z |
| tickets/stories/completed/2026-09-25_ir_phase_pipeline_survey_story.md | artifacts/ir_phase_survey_20260925/ | retain_as_reference | Ten survey records plus summary.md (D1-D6); ground truth for the structural snapshot. | 2026-09-26T13:27:19Z |
| tickets/stories/completed/2026-09-26_phase_pipeline_improvement_plan_story.md | artifacts/ir_phase_improvement_20260926/ | retain_as_reference | cost_model.md and candidates.md; T1 chosen and shipped. | 2026-09-26T13:27:19Z |
| tickets/tasks/completed/2026-09-26_live_contract_override_operands_task.md | system_docs/patches/completed/live_contract_override_operands_2026_09_26/ | promote_to_documentation | Promoted to src_components/src_architecture (DI descriptors, SpellCompiler); three patch files archived. | 2026-09-26T13:14:31Z |
| tickets/tasks/completed/2026-09-26_author_signature_patch_docs_task.md | system_docs/patches/completed/codegen_signature_determinism_2026_09_26/ | promote_to_documentation | Promoted to src_components/src_architecture (SpellCompiler IR seams); two patch files archived. | 2026-09-26T13:14:31Z |
| tickets/stories/completed/2026-09-26_signature_determinism_and_phase8_digest_story.md | artifacts/codegen_signature_determinism_20260926/ | retain_as_reference | Measurement plan, M7 probe and results (M1/M2/M4/M5/M7 filed; M3/M6/M8 not run). | 2026-09-26T13:14:31Z |
| tickets/tasks/completed/2026-09-26_build_site_graph_and_override_key_resolver_task.md | artifacts/melder_override_design_20260926/s1_staging/ | retain_as_reference | Staged S1 sources, apply script and the conjure-cost probe. | 2026-09-26T12:13:26Z |
| tickets/tasks/completed/2026-09-26_stabilize_function_spell_ids_across_processes_task.md | system_docs/patches/completed/stable_callable_spell_ids_2026_09_26/ | promote_to_documentation | Promoted to src_architecture/src_components/tests_components and the graph; five patch files archived. | 2026-09-26T11:31:13Z |
| tickets/tasks/completed/2026-09-26_stabilize_function_spell_ids_across_processes_task.md | artifacts/function_spell_ids_20260926/ | retain_as_reference | Probes, before/after results, commit manifest and file list. | 2026-09-26T11:31:13Z |
| tickets/tasks/completed/2026-09-26_add_conjure_validation_warnings_flag_task.md | system_docs/patches/completed/conjure_validation_warnings_2026_09_26/ | promote_to_documentation | Promoted to src_architecture/src_components and release note; two patch files archived. | 2026-09-26T10:12:55Z |
| tickets/tasks/completed/2026-09-26_fix_inspect_signature_nameerror_on_type_checking_annotations_task.md | system_docs/patches/completed/type_checking_annotation_reflection_2026_09_26/ | promote_to_documentation | Promoted to src_architecture/src_components/tests_components and the graph; ten patch files archived. | 2026-09-26T10:12:17Z |
| tickets/tasks/completed/2026-09-26_fix_inspect_signature_nameerror_on_type_checking_annotations_task.md | artifacts/inspect_signature_nameerror_20260926/ | retain_as_reference | Probes, before/prototype results, commit manifest and device-tree suite results. | 2026-09-26T10:12:17Z |
| tickets/tasks/completed/2026-09-26_build_annotation_integrity_audit_tool_task.md | artifacts/annotation_integrity_audit_20260926/ | retain_as_reference | Audit tool, controls, src/melder findings and the 3.14.7t union truth table. | 2026-09-26T10:12:17Z |
| tickets/tasks/completed/2026-09-26_implement_missing_dependency_sockets_task.md | system_docs/patches/completed/unresolved_input_sockets_2026_09_26/ | promote_to_documentation | Promoted to src_architecture/src_components, graph, assets and release note; four patch files archived. | 2026-09-26T08:54:37Z |
| tickets/tasks/completed/2026-09-26_implement_missing_dependency_sockets_task.md | artifacts/missing_dependency_sockets_20260926/ | retain_as_reference | Probes and 3.14t results: steps 1-2, provider removal/rebind/disposal, CommandOps shapes. | 2026-09-26T08:54:37Z |
| tickets/epics/completed/2026-09-26_melder_long_run_throughput_truth_epic.md | artifacts/melder_long_run_growth_20260926/ | retain_as_reference | Evidence, probes, run logs and the applied harness patch; owner turn-in. | 2026-09-26T08:32:04Z |
| tickets/tasks/completed/2026-09-25_verify_override_behavior_contract_task.md | artifacts/melder_override_contract_20260925/regression_matrix.md | retain_as_reference | Contract test plan; items 4a/5c chosen; input to override implementation. | 2026-09-26T00:12:00Z |
<!-- END USER-DEFINED: cleared_artifacts -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
- Earlier cleared associations and historical notes are preserved in
  artifacts/shared_boards_cleanup_20260921/retired_board_history.md.
- This cleanup leaves one representative entry for each of twelve recent completed-ticket groups.
  The archive preserves all 214 original associations, including retained-reference history.
- 2026-09-26 cleanup (fable_0, owner-directed): the cleared-artifact history was compacted again to the rows
  closed on 2026-09-26; all 68 prior rows are preserved verbatim in
  artifacts/shared_boards_cleanup_20260926/retired_board_history.md.
<!-- END USER-DEFINED: notes -->
