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
<!-- END USER-DEFINED: alerts -->

## Active Items
| work_item | status | mode | owner | agent_name | blocker | next | outcome | exit_signal | ticket | updated_at | reread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: active_items -->
| override_design_melder | review | handoff | claude | melder_0 | none | Owner confirms closure of the design task (design v2 approved). | Evidence-backed override strategy with owner decisions. | Owner approves a strategy; implementation stories open. | tickets/tasks/2026-09-26_design_override_and_caller_input_execution_task.md | 2026-09-26T11:30:45Z | REQUIRED |
| override_many_collection_fix | review | handoff | claude | melder_0 | none | Owner reviews the collection-member fix (member paths, cache 13). | Each collection member builds its own many dependencies. | Owner accepts; closure sync. | tickets/tasks/2026-09-26_fix_collection_member_many_sharing_task.md | 2026-09-26T12:29:50Z | REQUIRED |
| override_site_plan_lowering | in_progress | implementation | claude | melder_0 | none | Owner decision on S2b-3 (retire old normal emitters); meanwhile S4 discovery (unresolved inputs decided in the plan). | Key-set plans for overrides and normal melds on one lowering (S3, S2b-1, S2b-2 done in tree). | S4-S6 done or owner redirects. | tickets/tasks/2026-09-26_build_site_plan_lowering_task.md | 2026-09-26T17:26:20Z | REQUIRED |
| caller_input_strictness | review | handoff | claude | melder_0 | none | Owner reviews the cause timeline; fix is the missing-dependency socket (S1). | Responsible change identified with before/after runs and fix options. | Commit and fix options recorded; task moves to review. | tickets/tasks/2026-09-26_trace_caller_input_conjure_strictness_regression_task.md | 2026-09-26T00:42:21Z | REQUIRED |
| gauntlet_runtime_speed | in_progress | discovery | claude | melder_2 | none | P3 dropped; owner picks the first clean lever (interning, thread-affine pools, fewer shared hops, SpellSpace.meld entry, lifecycle). | Per-scope-cycle cost map vs dishka and dependency-injector, with ranked and prototyped candidates. | Owner picks; that lever's task opens. | tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md | 2026-09-26T17:29:58Z | REQUIRED |
| gauntlet_p1_positional_args | review | validation | claude | melder_2 | none | Owner runs the Windows gauntlet with P1 applied; compare same-run ratios with owner_run_20260926.txt. | Generated plans pass dependency values positionally (-11% to -21% per scope cycle on the VM). | Owner-run gauntlet filed; owner accepts; closure sync. | tickets/tasks/2026-09-26_emit_positional_constructor_args_task.md | 2026-09-26T16:30:24Z | REQUIRED |
| ir_structural_snapshot_capture | review | validation | claude | fable_0 | none | C6: owner-run suites on the landed capture (seam, generation 15, conjure-end capture, 33 tests); then the hydrate task opens under the story. | Per-spell structural payloads (phase 3-4 rows, key, stamp, verdict) emitted beside the executor payloads at generation 15. | Owner-run suites green and acceptance; then the hydrate task is routed. | tickets/tasks/2026-09-26_capture_structural_payloads_at_conjure_end_task.md | 2026-09-26T17:28:54Z | REQUIRED |
| cycle_consumer_wording | review | handoff | claude | melder_1 | none | Owner reviews the consumer wording (probe_after.txt) and commits results/commit_files.txt. | A cycle's consumers read as consumers, members as members. | Owner accepts; closure sync. | tickets/tasks/2026-09-26_word_cycle_consumers_in_circular_dependency_report_task.md | 2026-09-26T17:26:17Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| self_dependency_report | done | melder_1 | tickets/tasks/completed/2026-09-26_report_self_referencing_constructor_as_validation_error_task.md | Self-referencing constructors refused via SELF_DEPENDENCY naming the parameter (Phase-3 half in fable_0's C-C); in afded5ce6; turned in. | 2026-09-26T17:00:32Z |
| ir_structural_snapshot_cc | done | fable_0 | tickets/tasks/completed/2026-09-26_drop_phase3_dag_object_for_id_rows_task.md | Phase 3 emits id rows without a DAG object; dependency_graph tombstoned; owner-run suites green; turned in. | 2026-09-26T16:59:15Z |
| class_binding_annotations_fix | done | melder_1 | tickets/tasks/completed/2026-09-26_fix_class_binding_profile_annotations_for_type_checking_names_task.md | Class binding profiles keep TYPE_CHECKING-named annotations as source text; fields count in the id; patch lane archived; owner accepted. | 2026-09-26T16:32:21Z |
| ir_snapshot_patch_docs | done | fable_0 | tickets/tasks/completed/2026-09-26_author_structural_snapshot_patch_docs_task.md | Three I-1 patch docs (architecture, component, hydrator) written, mapped and owner-approved; C-C opened. | 2026-09-26T16:13:09Z |
| version_notch_validation_report | done | melder_1 | tickets/tasks/completed/2026-09-26_notch_version_and_release_note_for_validation_report_task.md | Version 0.2.58 (literal already notched); release note headed 0.2.58 with the validation-report details; owner accepted. | 2026-09-26T16:09:42Z |
| validation_error_reporting | done | melder_1 | tickets/tasks/completed/2026-09-26_review_conjure_validation_error_reporting_task.md | Conjure refusal report rewritten (names, reasons, fixes; conduit reasons kept); *args: Any fixed; in a62df80cb; patch lane archived; owner accepted. | 2026-09-26T16:00:30Z |
| shared_boards_cleanup | done | fable_0 | tickets/tasks/completed/2026-09-26_cleanup_shared_boards_and_mailbox_task.md | Mailbox, alerts, roster and cleared history cleaned; 13 dormant rows turned in; verbatim archive kept. | 2026-09-26T15:01:13Z |
| annotation_shape_guard | done | melder_1 | tickets/tasks/completed/2026-09-26_align_annotation_shape_guard_with_phase1_caller_inputs_task.md | Container params and typing.Any no longer break conjure; in HEAD a67cd3b49; patch lane archived; turned in. | 2026-09-26T14:47:09Z |
| class_binding_annotations | done | melder_1 | tickets/tasks/completed/2026-09-26_keep_class_binding_annotations_with_type_checking_names_task.md | Turned in UNFIXED: class annotations with TYPE_CHECKING-only names still empty the binding profile; fix prototyped in artifacts. | 2026-09-26T14:47:09Z |
| creation_context_race | done | melder_1 | tickets/tasks/completed/2026-09-26_investigate_concurrent_first_meld_creation_context_race_task.md | Concurrent first-meld race fixed (September freeze/drain design); 40/40; patch lane archived; owner accepted. | 2026-09-26T14:24:40Z |
| dormant_rows_turn_in | done | fable_0 | tickets/tasks/completed/2026-09-26_cleanup_shared_boards_and_mailbox_task.md | 13 dormant rows turned in by the owner (codex_1, workflows_0, updater_0, updater_1, muse, one unassigned epic); per-ticket record in artifacts/shared_boards_cleanup_20260926/. | 2026-09-26T13:45:56Z |
| release_note_t1 | done | fable_0 | tickets/tasks/completed/2026-09-26_update_release_note_for_tranche_t1_task.md | Release note 0.2.56 with the four tranche-T1 sections; owner accepted. | 2026-09-26T13:38:26Z |
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
- ir_structural_snapshot_capture: SWITCH_TRIGGER is the owner-run suite result on the landed capture (task in review);
  the hydrate task opens next under the story. RESUME_HIERARCHY: tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md ->
  tickets/stories/2026-09-26_structural_snapshot_story.md -> tickets/tasks/2026-09-26_capture_structural_payloads_at_conjure_end_task.md.
- gauntlet_runtime_speed: SWITCH_TRIGGER is the filed lifecycle cost map with measured trims (owner picks;
  D1-D3 answered 15:45:57Z). RESUME_HIERARCHY: tickets/stories/2026-09-26_gauntlet_runtime_speed_story.md ->
  tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md.
- gauntlet_p1_positional_args: SWITCH_TRIGGER is the owner's Windows gauntlet run with P1 (applied 16:16Z) and
  acceptance.
  RESUME_HIERARCHY: tickets/stories/2026-09-26_gauntlet_runtime_speed_story.md ->
  tickets/tasks/2026-09-26_emit_positional_constructor_args_task.md.
- cycle_consumer_wording: SWITCH_TRIGGER is owner review of the applied wording.
  RESUME_HIERARCHY: tickets/tasks/2026-09-26_word_cycle_consumers_in_circular_dependency_report_task.md.
### Device VM git hazard (melder_2, 2026-09-26)
- The connected folder refuses deletes, so any git command that refreshes the index from the device VM
  (plain `git status`, `git diff`) can leave an empty .git/index.lock that blocks the owner's commits.
  Run git there with `GIT_OPTIONAL_LOCKS=0` and read-only commands only; if a lock appears, report it.
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
### Versioning (owner, 2026-09-26)
- Owner: "each change we make is a notch of 0.01 so its fine". Each change gets its own patch notch of
  `src/melder/__version__.py` (0.2.58 -> 0.2.59); lanes notching one after another is expected, not a conflict.
  The release-note header follows `__version__`.
<!-- END USER-DEFINED: notes -->
