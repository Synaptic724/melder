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
| tickets/tasks/2026-09-22_implement_graduation_configuration_and_hook_ownership_task.md | system_docs/patches/active/graduation_configuration_2026_09_22/ | patch_contracts | in_progress | promote_to_documentation | Consume before source edits; promote after owner code review. | 2026-09-22T11:00:19Z | REQUIRED |
| tickets/tasks/2026-09-22_implement_graduation_configuration_and_hook_ownership_task.md | artifacts/graduation_configuration_20260922/ | implementation_evidence | in_progress | retain_as_reference | Record focused validation and unchanged-asset proof. | 2026-09-22T11:00:19Z | REQUIRED |
| tickets/tasks/2026-09-22_add_graduation_ownership_red_regressions_task.md | artifacts/graduation_ownership_regressions_20260922/ | regression_evidence | review | retain_as_reference | 32 red cases, 3 controls pass, final lint and 592 unchanged source hashes. | 2026-09-22T10:37:51Z | REQUIRED |
| tickets/tasks/2026-09-22_add_local_hook_setters_and_tracking_task.md | artifacts/local_hook_tracking_20260922/ | validation | ready | retain_as_reference | Read costs recorded; runtime tests await resumed API/flag implementation. | 2026-09-22T10:13:25Z | HELPFUL |
| tickets/tasks/backlog/2026-09-21_investigate_runtime_hook_clearing_task.md | artifacts/runtime_hook_discovery_20260921/ | discovery | backlog | retain_as_reference | Broad epic parked by owner; evidence retained for narrow pool-reset discovery or later reopening. | 2026-09-22T09:11:27Z | HELPFUL |
| tickets/tasks/2026-09-21_implement_bind_lifecycle_hooks_task.md | system_docs/patches/active/bind_lifecycle_hooks_2026_09_21/ | patch_contracts | review | promote_to_documentation | Source implemented; promotion/generators held for code approval. | 2026-09-21T11:45:14Z | REQUIRED |
| tickets/tasks/2026-09-21_implement_bind_lifecycle_hooks_task.md | artifacts/bind_hooks_implementation_20260921/ | validation | review | retain_as_reference | Book/Conduit review map, 729 passes, scoped lint and unchanged-asset proof. | 2026-09-21T12:10:10Z | REQUIRED |
| tickets/tasks/2026-09-21_investigate_bind_lifecycle_hooks_task.md | artifacts/bind_hooks_discovery_20260921/ | discovery | review | retain_as_reference | Full impact in epic; earlier 13 characterization checks and lint retained. | 2026-09-21T10:46:10Z | REQUIRED |
| tickets/epics/2026-09-20_bind_lifecycle_hooks_and_reference_strategies_epic.md | artifacts/bind_hooks_discovery_20260921/plan.md | implementation_plan | review | retain_as_reference | Core plan points to expanded recording, replay, cleanup and regression map. | 2026-09-21T10:46:10Z | REQUIRED |
| tickets/tasks/2026-09-20_prepare_0_2_37_to_0_2_42_release_document_task.md | artifacts/release_0_2_37_to_0_2_42_20260920/ | release_evidence | review | retain_as_reference | 0.2.43 draft references verified release, commit and completed-epic evidence. | 2026-09-20T07:54:22Z | HELPFUL |
| tickets/tasks/2026-09-19_repair_benchmark_spell_id_lookup_task.md | artifacts/benchmark_spell_id_repair_20260919/ | benchmark_compatibility | review | retain_as_reference | Safe codemod, passing checks and separate setup failure retained. | 2026-09-20T01:15:40Z | REQUIRED |
| tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md | artifacts/existing_object_di_comparison_20260913/comparison.md | deferred_design_reference | backlog | retain_as_reference | Parked by owner; resume only on explicit request. | 2026-09-19T14:53:20Z | HELPFUL |
| tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md | artifacts/existing_instance_planning_20260913/existing_object_disposal_blast_radius.md | deferred_design_reference | backlog | retain_as_reference | Parked by owner; resume only on explicit request. | 2026-09-19T14:53:20Z | HELPFUL |
| tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md | artifacts/existing_instance_planning_20260913/gap_analysis.md | deferred_design_reference | backlog | retain_as_reference | Parked by owner; resume only on explicit request. | 2026-09-19T14:53:20Z | HELPFUL |
| tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md | artifacts/existing_instance_planning_20260913/protocol_admission_red.xml | deferred_design_reference | backlog | retain_as_reference | Parked by owner; resume only on explicit request. | 2026-09-19T14:53:20Z | HELPFUL |
| tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md | artifacts/existing_instance_planning_20260913/frame_admission_characterization.log | deferred_design_reference | backlog | retain_as_reference | Parked by owner; resume only on explicit request. | 2026-09-19T14:53:20Z | HELPFUL |
| tickets/tasks/2026-09-06_readme_status_badges_task.md | artifacts/readme_badges_validation_20260906/ | validation_workspace | review | delete_on_close | 339 tests, lint, badge/config and asset validation passed. | 2026-09-06T14:55:32Z | HELPFUL |
| tickets/tasks/2026-09-06_readme_status_badges_task.md | system_docs/patches/active/readme_coverage_badges_2026_09_06/ | patch_docs | review | promote_to_documentation | Implemented token reporting; guide carries durable setup. | 2026-09-06T14:55:32Z | REQUIRED |
| tickets/tasks/2026-09-06_embed_melder_banner_task.md | artifacts/melder_banner_20260906/ | validation_screenshots | review | delete_on_close | Desktop/mobile layouts passed; owner review. | 2026-09-06T14:16:51Z | HELPFUL |
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
<!-- END USER-DEFINED: active_artifacts -->

## Recently Cleared Artifacts
| ticket | artifact_path | disposition | reason | closed_at |
| --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: cleared_artifacts -->
| tickets/tasks/completed/2026-09-21_add_intermediate_purge_example_task.md | artifacts/intermediate_purge_20260921/ | retain_as_reference | Completed lesson, runtime checks and publication/download evidence retained. | 2026-09-21T00:59:10Z |
| tickets/epics/completed/2026-09-19_scope_aware_creation_purge_epic.md | artifacts/purge_scope_discovery_20260920/plan.md | retain_as_reference | Owner-accepted purge delivery; evidence retained, promoted patch contracts archived with matching hashes. | 2026-09-21T00:37:37Z |
| tickets/tasks/completed/2026-09-20_implement_scoped_creation_purge_task.md | system_docs/patches/completed/scope_aware_purge_2026_09_20/ | promote_to_documentation | Owner-accepted purge delivery; evidence retained, promoted patch contracts archived with matching hashes. | 2026-09-21T00:37:37Z |
| tickets/tasks/completed/2026-09-20_implement_scoped_creation_purge_task.md | artifacts/purge_implementation_20260920/ | retain_as_reference | Owner-accepted purge delivery; evidence retained, promoted patch contracts archived with matching hashes. | 2026-09-21T00:37:37Z |
| tickets/tasks/completed/2026-09-20_discover_purge_scope_ownership_task.md | artifacts/purge_scope_discovery_20260920/ | retain_as_reference | Owner-accepted purge delivery; evidence retained, promoted patch contracts archived with matching hashes. | 2026-09-21T00:37:37Z |
| tickets/tasks/completed/2026-09-19_draft_purge_epic_and_refresh_assets_task.md | artifacts/purge_epic_assets_20260919/ | retain_as_reference | Owner-accepted purge delivery; evidence retained, promoted patch contracts archived with matching hashes. | 2026-09-21T00:37:37Z |
| tickets/tasks/completed/2026-09-21_cleanup_shared_context_compass_boards_task.md | artifacts/shared_boards_cleanup_20260921/ | retain_as_reference | Full retired board history and cleanup proof retained. | 2026-09-21T00:22:34Z |
| tickets/tasks/completed/2026-09-20_transfer_workflows_1_responsibility_task.md | artifacts/workflows_closeout_20260920/ | retain_as_reference | Owner-approved closeout receipts and procedures retained. | 2026-09-20T22:34:55Z |
| tickets/tasks/completed/2026-09-20_teach_meld_string_names_task.md | artifacts/meld_string_names_20260920/ | retain_as_reference | Completed delivery; dated evidence retained. | 2026-09-20T22:13:38Z |
| tickets/tasks/completed/2026-09-19_document_positional_meld_calls_task.md | artifacts/positional_meld_docs_20260919/ | retain_as_reference | Completed delivery; dated evidence retained. | 2026-09-20T22:13:38Z |
| tickets/tasks/completed/2026-09-13_sync_owner_uv_environment_task.md | artifacts/uv_environment_sync_20260913/ | retain_as_reference | Completed delivery; dated evidence retained. | 2026-09-20T22:13:38Z |
| tickets/tasks/completed/2026-09-19_fix_feature_turn_in_failures_task.md | system_docs/patches/completed/local_phase_cancellation_2026_09_19/ | promote_to_documentation | Durable deltas promoted; original patch contracts and indexes archived intact. | 2026-09-20T00:25:59Z |
| tickets/tasks/completed/2026-09-19_publish_and_replay_non_resolvable_definitions_task.md | artifacts/non_resolvable_graph_replay_20260919/ | retain_as_reference | Owner-authorized turn-in; validation and recorded limitations retained as reference. | 2026-09-20T00:25:59Z |
| tickets/tasks/completed/2026-09-19_enforce_required_override_execution_task.md | artifacts/required_override_execution_20260919/ | retain_as_reference | Owner-authorized turn-in; validation and recorded limitations retained as reference. | 2026-09-20T00:25:59Z |
| tickets/tasks/completed/2026-09-19_enforce_non_resolvable_runtime_admission_task.md | system_docs/patches/completed/non_resolvable_runtime_admission_2026_09_19/ | promote_to_documentation | Durable deltas promoted; original patch contracts and indexes archived intact. | 2026-09-20T00:25:59Z |
| tickets/tasks/completed/2026-09-19_implement_override_required_compiler_task.md | system_docs/patches/completed/override_required_compiler_2026_09_19/ | promote_to_documentation | Durable deltas promoted; original patch contracts and indexes archived intact. | 2026-09-20T00:25:59Z |
| tickets/tasks/completed/2026-09-19_implement_resolvable_registration_modifier_task.md | system_docs/patches/completed/discoverable_registration_modifier_2026_09_19/ | promote_to_documentation | Durable deltas promoted; original patch contracts and indexes archived intact. | 2026-09-20T00:25:59Z |
| tickets/tasks/completed/2026-09-19_turn_in_updater_0_work_task.md | artifacts/updater_0_turn_in_20260919/ | retain_as_reference | Owner-authorized closure manifest and verification; all code changes retained. | 2026-09-19T14:55:42Z |
<!-- END USER-DEFINED: cleared_artifacts -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
- Earlier cleared associations and historical notes are preserved in
  artifacts/shared_boards_cleanup_20260921/retired_board_history.md.
- This cleanup leaves one representative entry for each of twelve recent completed-ticket groups.
  The archive preserves all 214 original associations, including retained-reference history.
<!-- END USER-DEFINED: notes -->
