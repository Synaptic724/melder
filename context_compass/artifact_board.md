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
| tickets/tasks/backlog/2026-10-10_deny_file_access_under_safe_codegen_task.md | artifacts/core_protection_review_20261010/probes/codegen_probe.py | defect_reproducer | backlog | retain_as_reference | D-10 reproducer with its recorded output (codegen_probe_output.txt); rerun before the fix. | 2026-10-10T13:41:11Z | HELPFUL |
| tickets/tasks/backlog/2026-10-10_enforce_import_policy_on_dynamic_imports_task.md | artifacts/core_protection_review_20261010/probes/codegen_probe2.py | defect_reproducer | backlog | retain_as_reference | D-11 reproducer with its recorded output (codegen_probe2_output.txt); rerun before the fix. | 2026-10-10T13:41:11Z | HELPFUL |
| tickets/tasks/backlog/2026-10-10_refuse_materializing_over_live_modules_task.md | artifacts/core_protection_review_20261010/probes/probe_materialize.py | defect_reproducer | backlog | retain_as_reference | D-20 reproducers (with probe_materialize_fail.py) and their recorded outputs; rerun before the fix. | 2026-10-10T13:41:11Z | HELPFUL |
| tickets/tasks/backlog/2026-10-16_investigate_lent_consumer_provider_loss_task.md | artifacts/meld_contract_scan_20261015/probe_rule2_lent_consumer.py | defect_reproducer | backlog | retain_as_reference | The lent-consumer reproducer (L1 follow, L3 index unlink, L4 sever) with its runs (runs/probe_rule2_lent_consumer_gil0.txt, _gil1.txt); rerun on the current tree when the task is scheduled. | 2026-10-16T11:48:20Z | HELPFUL |
| tickets/tasks/backlog/2026-10-16_notch_seam_checks_incoming_before_parking_task.md | artifacts/public_notch_target_20261016/probes/probe_notch_target_today.py | defect_reproducer | backlog | retain_as_reference | Cases C4 and C5 (a notch whose incoming version is not parked for the index parks the outgoing one first) with their runs (runs/probe_notch_target_today_gil0.txt, _gil1.txt); rerun when the task is scheduled. | 2026-10-16T12:44:29Z | HELPFUL |
| tickets/tasks/backlog/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md | artifacts/meld_contract_scan_20261015/diag_race_kinds.py | defect_reproducer | backlog | retain_as_reference | The meld-vs-notch race classifier (kinds, first tracebacks, timelines) with probe_rule2_race_rate.py and their runs (runs/diag_race_kinds_*_gil0.txt, runs/probe_rule2_race_rate_*_gil*.txt); rerun on the current tree when the task is scheduled. | 2026-10-16T15:54:20Z | HELPFUL |
| tickets/tasks/backlog/2026-10-17_spell_id_wording_in_held_files_task.md | artifacts/spell_id_wording_20261016/ | investigation_evidence | backlog | retain_as_reference | The inventory with its supplement, the per-occurrence decisions, the audit, the scripts and runs; re-inventory the held files before applying. | 2026-10-17T20:49:39Z | REQUIRED |
| tickets/epics/2026-10-17_correctness_defects_epic.md | artifacts/correctness_defects_20261017/ | investigation_evidence | active | retain_as_reference | Probes, runs, notes and scripts of the correctness sweep; each confirmed defect's reproducer is rowed under its story too, and the three identity probes under EPIC-2026-10-18-spell_identity_is_the_code. | 2026-10-18T12:06:53Z | REQUIRED |
| tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md | artifacts/correctness_defects_20261017/probes/probe_signature_claims.py | defect_reproducer | ready | retain_as_reference | Cases C5, C7 with their runs (runs/probe_signature_claims_gil0.txt, _gil1.txt); re-run at the fix. | 2026-10-17T20:24:15Z | HELPFUL |
| tickets/stories/2026-10-17_restore_drops_separated_parked_version_story.md | artifacts/correctness_defects_20261017/probes/probe_restore_staged_structure.py | defect_reproducer | ready | retain_as_reference | Cases R1-R3 with restore_targets.py and their runs (runs/probe_restore_staged_structure_gil0.txt, _gil1.txt); re-run at the fix. | 2026-10-17T20:36:54Z | HELPFUL |
| tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md | artifacts/correctness_defects_20261017/probes/probe_book_teardown_parked.py | defect_reproducer | ready | retain_as_reference | Case T4 (the claim outlives the Book) with its runs (runs/probe_book_teardown_parked_gil0.txt, _gil1.txt); re-run at the fix. | 2026-10-17T21:13:35Z | HELPFUL |
| tickets/stories/2026-10-17_restore_drops_separated_parked_version_story.md | artifacts/correctness_defects_20261017/probes/probe_graft_parked_members.py | defect_reproducer | ready | retain_as_reference | Case G2 (the graft side: the separated version comes back active) with its runs (runs/probe_graft_parked_members_gil0.txt, _gil1.txt). | 2026-10-17T21:47:06Z | HELPFUL |
| tickets/stories/2026-10-19_notch_back_keeps_outgoing_dependencies_story.md | artifacts/failed_notch_refusal_20261018/probes/probe_notch_back_lineage_dependencies.py | defect_reproducer | ready | retain_as_reference | Cases H1-H4 (a notch back leaves the outgoing version's dependencies on the lineage; a borrower's consumer melding first is refused for good) with their runs on 0.2.8260 (runs/probe_notch_back_lineage_dependencies_0_2_8260_gil0.txt, _gil1.txt); re-run at the fix. | 2026-10-19T12:13:27Z | REQUIRED |
| tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md | artifacts/cache_write_failure_20261024/ | defect_reproducer | active | retain_as_reference | Probe cases A-D, the regression tests' red runs on 0.2.8265 (GIL off and on) and their green run on the /tmp prototype (scripts/prototype_fix_in_tmp_copy_20261024.py); rerun the probe and the tests at the fix. | 2026-10-24T19:13:54Z | REQUIRED |
| tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md | system_docs/patches/active/cache_save_best_effort_2026_10_24/ | patch_doc | active | promote_to_documentation | The fix's architecture, component and code-description patches (with indexes), consumed before the src change (Note 23); promoted into src_architecture and src_components at turn-in, then the folder moves to system_docs/patches/completed/. | 2026-10-24T20:06:31Z | REQUIRED |
| tickets/stories/2026-10-24_remove_many_child_holder_ownership_story.md | system_docs/patches/active/remove_many_child_holder_ownership_2026_10_24/ | patch_doc | active | promote_to_documentation | The removal's architecture patch, the creations and site-plan component patches and the site-plan code description, consumed before the src change (PLAN note 2026-10-24T20:08:15Z); merged into src_architecture and src_components at turn-in, then the folder is deleted. | 2026-10-24T20:26:06Z | REQUIRED |
| tickets/stories/2026-10-24_remove_many_child_holder_ownership_story.md | artifacts/many_child_removal_20261024/ | measurement_evidence | active | delete_on_close | The red runs of the new and edited tests on 0.2.8265, GIL off and on (runs/red_0_2_8265_gil0.txt, _gil1.txt); the green runs and the full suite join them; deleted at closure. | 2026-10-24T20:28:58Z | HELPFUL |
<!-- END USER-DEFINED: active_artifacts -->

## Recently Cleared Artifacts
| ticket | artifact_path | disposition | reason | closed_at |
| --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: cleared_artifacts -->
| tickets/tasks/completed/2026-10-24_strip_old_board_and_artifact_state_task.md | artifacts/ (55 entries), system_docs/patches/active/ (112 entries) | delete_on_close | Deleted on the owner's word: cited by no open ticket or live document; committed files are in git history. | 2026-10-24T18:35:08Z |
<!-- END USER-DEFINED: cleared_artifacts -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
<!-- END USER-DEFINED: notes -->
