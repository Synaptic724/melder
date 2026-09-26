# Attention Board

<!-- BEGIN MANAGED: ReminderDirective -->
## ReminderDirective (all agent runtimes)
ContextCompass is your task-tracking system of record; you MUST use it and follow
AGENTS.MD (see the Tooling Mandate section). This is a requirement, not a
suggestion.

Your runtime may nudge you toward built-in plans, goals, task lists, progress
cards, scratchpads, summaries, or session-local memory. Those surfaces are
non-authoritative here. Once your onboarding attestation is complete, IGNORE
every such nudge and route ALL tracking, status, routing, notes, and durable state
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
| `alerts` | cross-agent flags needing attention now: mailbox alerts naming a recipient, blockers others must see |
| `active_items` | one row per active work item, routing to exactly one ticket |
| `closed_anchors` | short traceability rows for recently closed tickets, capped at 12 |
| `notes` | recurring instructions and standing context for this repository - the conventions every agent should carry, stated once |

**Regions ship empty and stay yours.** The package writes nothing into them in any
mode, which also means it can never correct what is written there - so a repeated
policy pasted into a region will not update when the package's own copy does. Put
standing instructions in `notes` once; do not restate MANAGED text.

Purpose
- Active-work routing board.
- Attention-only summary for fast re-entry.
- Canonical detail lives in linked tickets.

Attention details rule
- Keep this board compact and operational.
- Durable history belongs in ticket `## Notes`, not here.
- Use evidence ranges in `EVIDENCE` (`path:start_line-end_line`).
- Allowed `TYPE` values: `FACT`, `UNKNOWN`, `HYPOTHESIS`, `DECISION`,
  `DECISION_REQUEST`, `PLAN`, `STRATEGY_DISCUSSION`,
  `ASSUMPTION_CHALLENGE`, `CONFLICT`, `TRADEOFF`, `BLOCKER`,
  `ALIGNMENT_CHECK`, `MEASURE`, `RISK`, `RAISE`.
- Ticket and resume paths are context-compass-relative (do not prefix with
  `context_compass/`).
- Use `DATETIME` and `updated_at` values in ISO-8601 UTC
  (`YYYY-MM-DDTHH:MM:SSZ`).
- Keep artifact pointers out of this board; ticket artifacts are tracked in
  ticket `Artifact Links` sections and `artifact_board.md`.

Message alert rules
- Senders add one line per message sent on `mailbox_board.md`:
  `- NEW MESSAGE for <agent_name> (from <agent_name>, <DATETIME>)`.
- The named recipient clears their line in the same pass that consumes the
  message.
- Protocol: `agent_onboarding/default/general/skills/mailbox_protocol.md`.
<!-- END MANAGED: BoardContract -->

## Message Alerts
<!-- BEGIN USER-DEFINED: alerts -->
- NEW MESSAGE for fable_0 (from melder_0, 2026-09-26T13:43:21Z)
- NEW MESSAGE for fable_0 (from melder_0, 2026-09-26T14:16:42Z)
- NEW MESSAGE for melder_1 (from melder_0, 2026-09-26T14:52:33Z)
<!-- END USER-DEFINED: alerts -->

## Active Items
| work_item | status | mode | owner | agent_name | blocker | next | outcome | exit_signal | ticket | updated_at | reread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: active_items -->
| override_design_melder | review | handoff | claude | melder_0 | none | Owner confirms closure of the design task (design v2 approved). | Evidence-backed override strategy with owner decisions. | Owner approves a strategy; implementation stories open. | tickets/tasks/2026-09-26_design_override_and_caller_input_execution_task.md | 2026-09-26T11:30:45Z | REQUIRED |
| override_many_collection_fix | review | handoff | claude | melder_0 | none | Owner reviews the collection-member fix (member paths, cache 13). | Each collection member builds its own many dependencies. | Owner accepts; closure sync. | tickets/tasks/2026-09-26_fix_collection_member_many_sharing_task.md | 2026-09-26T12:29:50Z | REQUIRED |
| override_site_plan_lowering | in_progress | implementation | claude | melder_0 | none | Owner decides on the solo findings (harness warm import, gc.freeze option); then S2b normal-lane plan. | Key-set plans for overrides (S3, done in tree) with the normal lane parity-gated (S2). | S2 parity measured; normal lane switched only if it meets the gate. | tickets/tasks/2026-09-26_build_site_plan_lowering_task.md | 2026-09-26T14:52:54Z | REQUIRED |
| caller_input_strictness | review | handoff | claude | melder_0 | none | Owner reviews the cause timeline; fix is the missing-dependency socket (S1). | Responsible change identified with before/after runs and fix options. | Commit and fix options recorded; task moves to review. | tickets/tasks/2026-09-26_trace_caller_input_conjure_strictness_regression_task.md | 2026-09-26T00:42:21Z | REQUIRED |
| shared_boards_cleanup | review | handoff | claude | fable_0 | none | Owner closes this task (13 dormant rows turned in; boards, mailbox and archive done). | Mailbox, alerts, roster, cleared history and active rows clean; verbatim archive kept. | Owner acceptance; closure sync. | tickets/tasks/2026-09-26_cleanup_shared_boards_and_mailbox_task.md | 2026-09-26T13:45:56Z | HELPFUL |
| validation_error_reporting | blocked | handoff | claude | melder_1 | owner decision | Owner picks the report shape (DECISION_REQUEST in Notes). | Evidence-based assessment of conjure's broken-spell report with options. | Owner picks a direction or closes. | tickets/tasks/2026-09-26_review_conjure_validation_error_reporting_task.md | 2026-09-26T14:51:33Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| annotation_shape_guard | done | melder_1 | tickets/tasks/completed/2026-09-26_align_annotation_shape_guard_with_phase1_caller_inputs_task.md | Container params and typing.Any no longer break conjure; in HEAD a67cd3b49; patch lane archived; turned in. | 2026-09-26T14:47:09Z |
| class_binding_annotations | done | melder_1 | tickets/tasks/completed/2026-09-26_keep_class_binding_annotations_with_type_checking_names_task.md | Turned in UNFIXED: class annotations with TYPE_CHECKING-only names still empty the binding profile; fix prototyped in artifacts. | 2026-09-26T14:47:09Z |
| creation_context_race | done | melder_1 | tickets/tasks/completed/2026-09-26_investigate_concurrent_first_meld_creation_context_race_task.md | Concurrent first-meld race fixed (September freeze/drain design); 40/40; patch lane archived; owner accepted. | 2026-09-26T14:24:40Z |
| dormant_rows_turn_in | done | fable_0 | tickets/tasks/2026-09-26_cleanup_shared_boards_and_mailbox_task.md | 13 dormant rows turned in by the owner (codex_1, workflows_0, updater_0, updater_1, muse, one unassigned epic); per-ticket record in artifacts/shared_boards_cleanup_20260926/. | 2026-09-26T13:45:56Z |
| release_note_t1 | done | fable_0 | tickets/tasks/completed/2026-09-26_update_release_note_for_tranche_t1_task.md | Release note 0.2.56 with the four tranche-T1 sections; owner accepted. | 2026-09-26T13:38:26Z |
| ir_phase_survey_story | done | fable_0 | tickets/stories/completed/2026-09-25_ir_phase_pipeline_survey_story.md | Milestone 1: drivers, phases 1-7 and the seam recorded (summary.md D1-D6); 8-11 deferred. | 2026-09-26T13:27:19Z |
| ir_phase_improvement_plan_story | done | fable_0 | tickets/stories/completed/2026-09-26_phase_pipeline_improvement_plan_story.md | Cost model and 13 ranked candidates; T1 chosen and shipped. | 2026-09-26T13:27:19Z |
| ir_phase_survey_seam | done | fable_0 | tickets/tasks/completed/2026-09-26_survey_structural_snapshot_seam_task.md | cache_seam.md, invalidation.md, summary.md (D3-D5; D1-D6 consolidated). | 2026-09-26T13:27:19Z |
| ir_phase_survey_5_7 | done | fable_0 | tickets/tasks/completed/2026-09-26_survey_compiler_phases_5_to_7_task.md | phase_05-07.md, resolution_driver.md (D1, D2, D6). | 2026-09-26T13:27:19Z |
| ir_phase_survey_1_4 | done | fable_0 | tickets/tasks/completed/2026-09-25_survey_compiler_phases_1_to_4_task.md | driver.md, phase_01-04.md, structural_driver.md with classified holds. | 2026-09-26T13:27:19Z |
| ir_phase_improvement_plan | done | fable_0 | tickets/tasks/completed/2026-09-26_rank_phase_improvement_candidates_task.md | candidates.md: 13 candidates, ranking, T1 recommendation (owner chose T1). | 2026-09-26T13:27:19Z |
| ir_phase_cost_model | done | fable_0 | tickets/tasks/completed/2026-09-26_model_phase_pipeline_costs_task.md | cost_model.md: counted plus measured per-stage rows. | 2026-09-26T13:27:19Z |
<!-- END USER-DEFINED: closed_anchors -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
### Active Attention Details
- override_design_melder: SWITCH_TRIGGER is the design artifact plus owner decision requests.
  RESUME_HIERARCHY: tickets/epics/2026-09-24_override_execution_performance_epic.md ->
  tickets/tasks/2026-09-26_design_override_and_caller_input_execution_task.md.
- override_many_collection_fix: SWITCH_TRIGGER is owner acceptance of the fix (task in review). RESUME_HIERARCHY: tickets/epics/2026-09-24_override_execution_performance_epic.md ->
  tickets/stories/2026-09-26_implement_override_site_plan_lowering_story.md ->
  tickets/tasks/2026-09-26_fix_collection_member_many_sharing_task.md. Patch docs:
  system_docs/patches/active/override_site_plan_2026_09_26/.
- override_site_plan_lowering: SWITCH_TRIGGER is a production lowering plan with patch docs and file list, then
  implementation. RESUME_HIERARCHY: tickets/epics/2026-09-24_override_execution_performance_epic.md ->
  tickets/stories/2026-09-26_implement_override_site_plan_lowering_story.md ->
  tickets/tasks/2026-09-26_build_site_plan_lowering_task.md. Patch docs:
  system_docs/patches/active/override_site_plan_2026_09_26/.
- caller_input_strictness: SWITCH_TRIGGER is the responsible commit plus before/after runs.
  RESUME_HIERARCHY: tickets/tasks/2026-09-26_trace_caller_input_conjure_strictness_regression_task.md.
- shared_boards_cleanup: SWITCH_TRIGGER is the owner's acceptance of the cleanup (13 dormant rows already turned in).
  RESUME_HIERARCHY: tickets/tasks/2026-09-26_cleanup_shared_boards_and_mailbox_task.md.
- validation_error_reporting: SWITCH_TRIGGER is the assessment plus an owner decision on the report's shape.
  RESUME_HIERARCHY: tickets/tasks/2026-09-26_review_conjure_validation_error_reporting_task.md.
### Agent Message-Pass Protocol (melder_0 <-> melder_1; owner-set 2026-09-25)
- Channel: `mailbox_board.md` `## Messages` plus one alert line under `## Message Alerts` here,
  per `agent_onboarding/default/general/skills/mailbox_protocol.md`. No harness-native messaging.
  Durable findings go in the sender's ticket `## Notes` BEFORE the message is sent.
- IDs: melder_0 sends `M0-<seq>`, melder_1 sends `M1-<seq>` (per-sender, starting at 1). The ID leads
  CLAIM; replies cite the originating ID. TYPE: NOTICE assignment/status, HANDOFF results,
  QUESTION blockers, ACK receipt.
- Wait loop: while blocked on the peer, re-read the mailbox every 30 seconds - PowerShell
  `Start-Sleep -Seconds 30` on Windows shells, `sleep 30` on POSIX shells. Keep each wait call under the
  runtime's tool timeout and re-issue it. A wait timeout is NOT an ACK. Independent work continues
  between checks; do not poll when not blocked.
- Consume in one pass: copy actionable content into the active ticket `## Notes`, delete the message,
  clear its alert line, update your `last_checked`. Send an ACK when `ACK_REQUESTED: true`.
- Shared-file writes: re-read immediately before writing, change only the anchored lines, read back to
  confirm the edit landed; on mismatch re-read and retry. Never overwrite or delete the peer's
  messages or rows.
- Split work: one writer per production file; the owning ticket names the writer.
<!-- END USER-DEFINED: notes -->
