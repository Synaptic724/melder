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
- Every artifact row must include a ticket reference and retention decision:
  a context-compass-relative path in local mode or Issue URL in plugin mode.

Disposition values
- `delete_on_close`: remove artifact when ticket closes.
- `retain_as_reference`: keep artifact with explicit reason.
- `promote_to_documentation`: convert artifact into durable docs.
<!-- END MANAGED: BoardContract -->

## Active Artifact Links
| ticket | artifact_path | artifact_type | status | disposition | next | updated_at | reread |
| --- | --- | --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: active_artifacts -->
| tickets/tasks/backlog/2026-09-27_probe_creation_context_design_task.md | artifacts/pgo_strategies_20260927/ | measurement_evidence | backlog | retain_as_reference | Parked by owner with the adaptive-creation-contexts epic; the proof (cache ledger, live shapes, registration split) and every run retained for a reopen. | 2026-09-28T00:57:27Z | HELPFUL |
| tickets/tasks/2026-10-10_deny_file_access_under_safe_codegen_task.md | artifacts/core_protection_review_20261010/probes/codegen_probe.py | defect_reproducer | active | retain_as_reference | D-10 reproducer with its recorded output (codegen_probe_output.txt); rerun on 0.2.8267 under EPIC-2026-10-25-codegen_room_policy_defects, the runs in artifacts/codegen_room_policy_20261025/runs/. | 2026-10-25T00:16:54Z | HELPFUL |
| tickets/tasks/2026-10-10_enforce_import_policy_on_dynamic_imports_task.md | artifacts/core_protection_review_20261010/probes/codegen_probe2.py | defect_reproducer | active | retain_as_reference | D-11 reproducer with its recorded output (codegen_probe2_output.txt); rerun on 0.2.8267 under EPIC-2026-10-25-codegen_room_policy_defects, the runs in artifacts/codegen_room_policy_20261025/runs/. | 2026-10-25T00:16:54Z | HELPFUL |
| tickets/tasks/2026-10-10_refuse_materializing_over_live_modules_task.md | artifacts/core_protection_review_20261010/probes/probe_materialize.py | defect_reproducer | active | retain_as_reference | D-20 reproducers (with probe_materialize_fail.py) and their recorded outputs; rerun on 0.2.8267 under EPIC-2026-10-25-codegen_room_policy_defects, the runs in artifacts/codegen_room_policy_20261025/runs/. | 2026-10-25T00:16:54Z | HELPFUL |
| tickets/tasks/backlog/2026-10-16_investigate_lent_consumer_provider_loss_task.md | artifacts/meld_contract_scan_20261015/probe_rule2_lent_consumer.py | defect_reproducer | backlog | retain_as_reference | The lent-consumer reproducer (L1 follow, L3 index unlink, L4 sever) with its runs (runs/probe_rule2_lent_consumer_gil0.txt, _gil1.txt); rerun on the current tree when the task is scheduled. | 2026-10-16T11:48:20Z | HELPFUL |
| tickets/tasks/backlog/2026-10-16_notch_seam_checks_incoming_before_parking_task.md | artifacts/public_notch_target_20261016/probes/probe_notch_target_today.py | defect_reproducer | backlog | retain_as_reference | Cases C4 and C5 (a notch whose incoming version is not parked for the index parks the outgoing one first) with their runs (runs/probe_notch_target_today_gil0.txt, _gil1.txt); rerun when the task is scheduled. | 2026-10-16T12:44:29Z | HELPFUL |
| tickets/tasks/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md | artifacts/meld_contract_scan_20261015/diag_race_kinds.py | defect_reproducer | active | retain_as_reference | The meld-vs-notch race classifier (kinds, first tracebacks, timelines) with probe_rule2_race_rate.py and their runs (runs/diag_race_kinds_*_gil0.txt, runs/probe_rule2_race_rate_*_gil*.txt); rerun on 0.2.8267 under EPIC-2026-10-25-notch_fanout_inflight_melds, the runs in artifacts/notch_fanout_race_20261025/runs/. | 2026-10-25T00:16:54Z | HELPFUL |
| tickets/tasks/backlog/2026-10-17_spell_id_wording_in_held_files_task.md | artifacts/spell_id_wording_20261016/ | investigation_evidence | backlog | retain_as_reference | The inventory with its supplement, the per-occurrence decisions, the audit, the scripts and runs; re-inventory the held files before applying. | 2026-10-17T20:49:39Z | REQUIRED |
| tickets/epics/2026-10-17_correctness_defects_epic.md | artifacts/correctness_defects_20261017/ | investigation_evidence | active | retain_as_reference | Probes, runs, notes and scripts of the correctness sweep; each confirmed defect's reproducer is rowed under its story too, and the three identity probes under EPIC-2026-10-18-spell_identity_is_the_code. | 2026-10-18T12:06:53Z | REQUIRED |
| tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md | artifacts/correctness_defects_20261017/probes/probe_signature_claims.py | defect_reproducer | active | retain_as_reference | Cases C5, C7 with their runs (runs/probe_signature_claims_gil0.txt, _gil1.txt); re-run at the fix. | 2026-10-17T20:24:15Z | HELPFUL |
| tickets/stories/2026-10-17_restore_drops_separated_parked_version_story.md | artifacts/correctness_defects_20261017/probes/probe_restore_staged_structure.py | defect_reproducer | ready | retain_as_reference | Cases R1-R3 with restore_targets.py and their runs (runs/probe_restore_staged_structure_gil0.txt, _gil1.txt); re-run at the fix. | 2026-10-17T20:36:54Z | HELPFUL |
| tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md | artifacts/correctness_defects_20261017/probes/probe_book_teardown_parked.py | defect_reproducer | active | retain_as_reference | Case T4 (the claim outlives the Book) with its runs (runs/probe_book_teardown_parked_gil0.txt, _gil1.txt); re-run at the fix. | 2026-10-17T21:13:35Z | HELPFUL |
| tickets/stories/2026-10-17_restore_drops_separated_parked_version_story.md | artifacts/correctness_defects_20261017/probes/probe_graft_parked_members.py | defect_reproducer | ready | retain_as_reference | Case G2 (the graft side: the separated version comes back active) with its runs (runs/probe_graft_parked_members_gil0.txt, _gil1.txt). | 2026-10-17T21:47:06Z | HELPFUL |
| tickets/stories/2026-10-19_notch_back_keeps_outgoing_dependencies_story.md | artifacts/failed_notch_refusal_20261018/probes/probe_notch_back_lineage_dependencies.py | defect_reproducer | ready | retain_as_reference | Cases H1-H4 (a notch back leaves the outgoing version's dependencies on the lineage; a borrower's consumer melding first is refused for good) with their runs on 0.2.8260 (runs/probe_notch_back_lineage_dependencies_0_2_8260_gil0.txt, _gil1.txt); re-run at the fix. | 2026-10-19T12:13:27Z | REQUIRED |
| tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md | artifacts/cache_write_failure_20261024/ | defect_reproducer | retained | retain_as_reference | The defect's reproducer (probes/probe_cache_emit_failure.py, cases A-D) with its runs on 0.2.8265 and at the fix (runs/probe_*, runs/f6_*), the regression tests' red runs and the lane's scripts; rerun the probe if the cache save path changes. | 2026-10-24T21:32:03Z | HELPFUL |
| tickets/tasks/completed/2026-10-24_windows_held_cache_bundle_test_task.md | artifacts/windows_held_bundle_20261024/ | test_harness | retained | retain_as_reference | The Linux emulation harness for the Windows-only held-bundle tests (scripts/) with the VM runs, the red runs on 0.2.8265 and the owner's Windows runs (runs/); rerun the harness if the cache save path changes. | 2026-10-24T23:03:28Z | HELPFUL |
| tickets/epics/2026-10-25_codegen_room_policy_defects_epic.md | artifacts/codegen_room_policy_20261025/ | investigation_evidence | active | retain_as_reference | The opening script of both epics (scripts/) and the 0.2.8267 reruns of D-10, D-11 and D-20 (runs/, as they land); disposition decided at closure. | 2026-10-25T00:16:54Z | HELPFUL |
| tickets/tasks/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md | artifacts/notch_fanout_race_20261025/ | investigation_evidence | active | retain_as_reference | The 0.2.8267 reruns of the race (runs/: the rate and kinds probes, the in-Book probe's 20- and 100-run captures), the in-Book probe (probes/) and this pass (scripts/); disposition decided at closure. | 2026-10-25T00:48:34Z | HELPFUL |
| tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md | artifacts/correctness_defects_20261017/probes/diag_notch_takes_other_books_address.py | defect_reproducer | active | retain_as_reference | The cross-Book case (a notch takes another Book's address; its teardown then frees it) with its run (runs/diag_notch_takes_other_books_address_0_2_8267.txt); re-run at the fix. | 2026-10-25T01:26:18Z | HELPFUL |
| tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md | artifacts/correctness_defects_20261017/probes/probe_how_melds_follow_a_notch.py | measurement_evidence | active | retain_as_reference | What follows a notch at one address and across two (runs/probe_how_melds_follow_a_notch_0_2_8267.txt); re-run at the fix. | 2026-10-25T01:26:18Z | HELPFUL |
| tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md | artifacts/correctness_defects_20261017/scripts/option_a_experiment/ | measurement_evidence | active | retain_as_reference | Option (A)'s scratch patches, the resumable test logger and runners, with runs/option_a_blast_radius_0_2_8267.txt (169 tests stage at another address); the fix's tests replace it. | 2026-10-25T01:26:18Z | REQUIRED |
| tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md | artifacts/correctness_defects_20261017/probes/probe_mixed_record_under_option_a.py | defect_reproducer | active | retain_as_reference | A record holding a mixed index replayed under (A) (runs/probe_mixed_record_under_option_a_0_2_8267.txt); re-run at the fix for the owner's call 1. | 2026-10-25T01:26:18Z | REQUIRED |
<!-- END USER-DEFINED: active_artifacts -->

## Recently Cleared Artifacts
| ticket | artifact_path | disposition | reason | closed_at |
| --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: cleared_artifacts -->
| tickets/tasks/completed/2026-10-24_strip_old_board_and_artifact_state_task.md | artifacts/ (55 entries), system_docs/patches/active/ (112 entries) | delete_on_close | Deleted on the owner's word: cited by no open ticket or live document; committed files are in git history. | 2026-10-24T18:35:08Z |
| tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md | system_docs/patches/completed/cache_save_best_effort_2026_10_24/ | promote_to_documentation | Promoted into src_architecture and src_components at 0.2.8266 (the task's Note 29); the folder moved from patches/active/ at closure. | 2026-10-24T21:32:03Z |
| tickets/stories/completed/2026-10-24_remove_many_child_holder_ownership_story.md | system_docs/patches/active/remove_many_child_holder_ownership_2026_10_24/ | promote_to_documentation | Merged into src_architecture and src_components at 0.2.8267 (the story's FACT note of 2026-10-24T21:50:43Z); the folder deleted at closure. | 2026-10-24T22:06:33Z |
| tickets/stories/completed/2026-10-24_remove_many_child_holder_ownership_story.md | artifacts/many_child_removal_20261024/ | delete_on_close | The red and green runs, the release-note claim runs and the edit scripts; deleted at closure (the committed files stay in git history). | 2026-10-24T22:06:33Z |
| tickets/stories/completed/2026-10-24_src_architecture_trim_to_spec_story.md | artifacts/src_architecture_to_spec_20261024/ | delete_on_close | The trim script (v2.1), its dry runs, the E0 baseline copies and the apply-run accounting; deleted at closure (the v1 script is in git 3bedd65bb; the accounting is in the story's Notes). | 2026-10-24T22:40:13Z |
| tickets/stories/completed/2026-10-24_src_components_to_spec_story.md | artifacts/src_components_to_spec_20261024/ | delete_on_close | The edit script (driver, library, five op modules), its dry runs, the E0 baseline copies and the apply log; deleted at closure (the accounting is in the story's Notes; the old text is in git 9f240166f). | 2026-10-25T01:12:33Z |
<!-- END USER-DEFINED: cleared_artifacts -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
<!-- END USER-DEFINED: notes -->
