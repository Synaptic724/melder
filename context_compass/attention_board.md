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
- NEW MESSAGE for muse (from updater_0, 2026-09-21T00:22:00Z)
- NEW MESSAGE for updater_0 (from melder_0, 2026-09-25T20:53:31Z)
- NEW MESSAGE for updater_1 (from melder_0, 2026-09-25T20:53:31Z)
- NEW MESSAGE for updater_0 (from melder_0, 2026-09-25T23:30:00Z)
- NEW MESSAGE for updater_1 (from melder_0, 2026-09-25T23:30:00Z)
- NEW MESSAGE for updater_0 (from melder_0, 2026-09-26T00:22:42Z)
- NEW MESSAGE for workflows_0 (from melder_0, 2026-09-26T00:22:42Z)
- NEW MESSAGE for melder_0 (from melder_1, 2026-09-26T00:24:13Z)
<!-- END USER-DEFINED: alerts -->

## Active Items
| work_item | status | mode | owner | agent_name | blocker | next | outcome | exit_signal | ticket | updated_at | reread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: active_items -->
| required_caller_inputs | review | handoff | codex | workflows_0 | none | Select explicit caller-input declaration design. | Five consumer failures explained; existing runtime capability verified. | Owner selects implementation scope or accepts investigation. | tickets/tasks/2026-09-24_investigate_required_caller_inputs_task.md | 2026-09-24T11:53:24Z | REQUIRED |
| override_structural_semantics | review | handoff | codex | updater_0 | none | Review joint alpha proposal and choose production contracts. | Compact/native proofs and direct-publication variant delivered. | Owner selects the documented implementation sequence. | tickets/tasks/2026-09-24_discover_override_execution_semantics_task.md | 2026-09-24T22:43:55Z | REQUIRED |
| override_occurrence_slicing | review | handoff | codex | updater_1 | none | Owner reviews the joint alpha implementation proposal. | Compact compiler and native bridge cross-reviewed. | Owner selects production scope and behavior contract. | tickets/tasks/2026-09-24_discover_override_occurrence_slicing_task.md | 2026-09-24T22:48:30Z | REQUIRED |
| override_emission_experiment | review | handoff | codex | updater_1 | none | Owner reviews the joint implementation proposal. | Measured gains and ten independent regressions accepted by lead. | Owner selects the production implementation boundary. | tickets/tasks/2026-09-24_experiment_static_many_override_execution_task.md | 2026-09-24T11:00:31Z | REQUIRED |
| override_execution_lead | review | handoff | codex | updater_0 | none | Preserve measured baseline for structural discovery. | Emission-only evidence retained; structural direction selected. | Structural successor task supplies the implementation proposal. | tickets/tasks/2026-09-24_coordinate_override_execution_investigation_task.md | 2026-09-24T21:20:16Z | REQUIRED |
| override_compiler_investigation | review | handoff | codex | updater_1 | none | Owner reviews compiler seams in the joint proposal. | Default-plan reuse diagnosis verified by the measured prototype. | Owner selects the next implementation tranche. | tickets/tasks/2026-09-24_investigate_override_compiler_planning_task.md | 2026-09-24T11:00:31Z | REQUIRED |
| override_performance_baseline | review | handoff | codex | updater_1 | none | Trace root-input execution after baseline review. | Measured 20-25% graph throughput and eager-construction evidence. | Next override investigation begins. | tickets/tasks/2026-09-24_measure_melder_creation_and_overrides_task.md | 2026-09-24T09:48:20Z | REQUIRED |
| upgrade_normal_review | review | handoff | codex | updater_1 | none | None unless owner reopens review. | Code unchanged; import purpose confirmed, broader review stopped. | Owner reopens or closes review. | tickets/tasks/2026-09-22_review_upgrade_to_normal_complexity_task.md | 2026-09-22T23:02:47Z | HELPFUL |
| readme_status_badges | review | handoff | codex | codex_1 | none | Owner reviews or promotes README/reporting changes. | Approved tagline, badges and current asset proofs. | Owner accepts implementation and hosted result. | tickets/tasks/2026-09-06_readme_status_badges_task.md | 2026-09-06T15:38:07Z | REQUIRED |
| embed_melder_banner | review | handoff | codex | codex_1 | none | Owner reviews final README integration. | Local banner source and public fallback validated. | Owner accepts ticket closure. | tickets/tasks/2026-09-06_embed_melder_banner_task.md | 2026-09-06T14:27:09Z | REQUIRED |
| stateful_application_recovery | ready | handoff | user | unassigned | none | Discuss one stateful recovery scenario. | Native replay coverage and partial/assisted recovery opportunities preserved. | Owner selects recovery contracts before implementation. | tickets/epics/2026-09-07_stateful_application_recovery_epic.md | 2026-09-07T19:17:55Z | REQUIRED |
| mediator_wiring_probe | in_progress | discovery | opencode | muse | none | Ask owner what remains before this lane is done. | Doc patches plus verified indexes stand; closeout only on explicit checkout. | Owner states remaining work or requests checkout. | tickets/tasks/2026-09-20_investigate_mediator_wiring_task.md | 2026-09-21T00:11:00Z | REQUIRED |
| components_sliced_audit | in_progress | discovery | opencode | muse | none | Verify indexes then slice front matter plus first C3 component. | Per-component notes plus closing contradiction list with evidence. | C3 pass complete with dispositions or owner redirects scope. | tickets/tasks/2026-09-21_systematic_components_audit_task.md | 2026-09-21T00:16:57Z | REQUIRED |
| ir_phase_survey_1_4 | in_progress | discovery | claude | fable_0 | none | Read compiler_phase_2.py and its symbolic_graph delegates; write phase_02.md. | Driver and phases 1-4 recorded from source with classified object holds. | Tranche 1 records accepted or owner redirects scope. | tickets/tasks/2026-09-25_survey_compiler_phases_1_to_4_task.md | 2026-09-26T00:08:30Z | REQUIRED |
| override_design_melder | review | handoff | claude | melder_0 | none | Owner decides D1-D4 in design.md; S1 caller inputs can start after D1. | Source-grounded override + caller-input design compared with joint alpha. | Owner accepts or redirects the design; implementation tasks open per decision. | tickets/tasks/2026-09-26_design_override_and_caller_input_execution_task.md | 2026-09-26T00:22:28Z | REQUIRED |
| melder_long_run_growth | in_progress | discovery | claude | melder_1 | none | Read lesser pool return, SpellSpace exit, thread state and slot guards in full. | Source verdict on per-cycle retained state plus diagnostic tests. | Verdict FACT or ruled out; tests added; task to review. | tickets/tasks/2026-09-26_investigate_melder_long_run_growth_task.md | 2026-09-26T00:35:00Z | REQUIRED |
| melder_long_run_attribution | in_progress | discovery | claude | melder_1 | none | Run the Melder gauntlet lane on the 3.14t sandbox snapshot. | Measured attribution of the 50k->100k drop (retained state vs process effects). | Each cause MEASURE-recorded; attribution stated; task to review. | tickets/tasks/2026-09-26_measure_melder_long_run_attribution_task.md | 2026-09-26T00:35:00Z | REQUIRED |
| caller_input_strictness | review | handoff | claude | melder_0 | none | Owner reviews the cause timeline; fix is the missing-dependency socket (S1). | Responsible change identified with before/after runs and fix options. | Commit and fix options recorded; task moves to review. | tickets/tasks/2026-09-26_trace_caller_input_conjure_strictness_regression_task.md | 2026-09-26T00:42:21Z | REQUIRED |
| missing_dependency_sockets | in_progress | handoff | claude | melder_0 | none | Owner confirms the change set; then patch docs and implementation. | Unprovided parameters compile as caller inputs; meld raises a named missing-input error. | Patch docs and file list ready for owner confirmation. | tickets/tasks/2026-09-26_implement_missing_dependency_sockets_task.md | 2026-09-26T00:48:04Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| version_notch_0_2_53 | done | melder_0 | tickets/tasks/completed/2026-09-26_bump_version_for_deadlock_fix_task.md | Version and next-release header at 0.2.53; asset rebuild held. | 2026-09-26T00:11:19Z |
| override_contract_story | done | melder_0, melder_1 | tickets/stories/completed/2026-09-25_verify_override_writer_and_contract_story.md | Deadlock fixed; contract verified; items 4a/5c chosen; open items carried. | 2026-09-26T00:15:00Z |
| override_contract_verify | done | melder_1 | tickets/tasks/completed/2026-09-25_verify_override_behavior_contract_task.md | Items 1-8 verified with regression matrix; owner-directed turn-in. | 2026-09-26T00:12:00Z |
| creation_slot_guards_impl | done | melder_0 | tickets/tasks/completed/2026-09-25_implement_creation_slot_build_guards_task.md | Per-slot build guards; deadlock fixed; docs, graph and release note updated. | 2026-09-25T23:47:39Z |
| deadlock_regression_tests | done | melder_0 | tickets/tasks/completed/2026-09-25_add_meld_lock_order_deadlock_regression_tests_task.md | 12 lock-order cases must complete (3.14t and GIL). | 2026-09-25T23:47:39Z |
| writer_lock_order_verify | done | melder_0 | tickets/tasks/completed/2026-09-25_verify_native_writer_lock_order_task.md | Store/Spell inversion confirmed; Idea A chosen and implemented. | 2026-09-25T23:47:39Z |
| inherited_cleanup_profiling | done | workflows_0 | tickets/tasks/completed/2026-09-24_investigate_inherited_cleanup_profiling_task.md | Inherited disposal fixed; 428 checks pass; next-release note added and patch records archived. | 2026-09-24T11:24:41Z |
| release_cache_invalidation | done | updater_0 | tickets/epics/completed/2026-09-23_invalidate_creation_cache_on_melder_version_change_epic.md | Release-bound cache, schema 9 and 0.2.51 notes delivered. | 2026-09-24T09:52:40Z |
| release_cache_implementation | done | updater_0 | tickets/tasks/completed/2026-09-24_implement_release_version_cache_invalidation_task.md | 138 unique final-version tests qualified; scoped docs promoted. | 2026-09-24T09:52:40Z |
| named_discovery_test_repair | done | updater_0 | tickets/tasks/completed/2026-09-23_fix_named_conduit_discovery_test_doubles_task.md | Both CI fixture errors fixed; 201 tests pass. | 2026-09-23T22:37:00Z |
| public_next_release | done | updater_0 | tickets/tasks/completed/2026-09-23_position_next_release_for_public_task.md | Public naming/discovery release copy verified. | 2026-09-23T22:30:29Z |
| graduation_packaged_assets | done | updater_0 | tickets/tasks/completed/2026-09-22_refresh_graduation_packaged_assets_when_approved_task.md | Both builders rerun after final updates; checks pass. | 2026-09-23T13:01:03Z |
<!-- END USER-DEFINED: closed_anchors -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
### Active Attention Details
- required_caller_inputs: SWITCH_TRIGGER is owner selection of declaration design or investigation acceptance.
  RESUME_HIERARCHY: tickets/tasks/2026-09-24_investigate_required_caller_inputs_task.md.
- override_structural_semantics: SWITCH_TRIGGER is a source-backed structural proposal with explicit policy questions.
  RESUME_HIERARCHY: tickets/epics/2026-09-24_override_execution_performance_epic.md -> tickets/tasks/2026-09-24_discover_override_execution_semantics_task.md.
- override_occurrence_slicing: SWITCH_TRIGGER is peer graph/compiler findings and lead synthesis.
  RESUME_HIERARCHY: tickets/epics/2026-09-24_override_execution_performance_epic.md -> tickets/tasks/2026-09-24_discover_override_occurrence_slicing_task.md.
- override_emission_experiment: SWITCH_TRIGGER is the owner's production implementation decision.
  RESUME_HIERARCHY: tickets/epics/2026-09-24_override_execution_performance_epic.md -> tickets/tasks/2026-09-24_experiment_static_many_override_execution_task.md.
- override_execution_lead: SWITCH_TRIGGER is a combined source-backed proposal and owner design decision.
  RESUME_HIERARCHY: tickets/epics/2026-09-24_override_execution_performance_epic.md -> tickets/tasks/2026-09-24_coordinate_override_execution_investigation_task.md.
- override_compiler_investigation: SWITCH_TRIGGER is the owner's selected compiler implementation boundary.
  RESUME_HIERARCHY: tickets/epics/2026-09-24_override_execution_performance_epic.md -> tickets/tasks/2026-09-24_investigate_override_compiler_planning_task.md.
- override_performance_baseline: SWITCH_TRIGGER is measured baseline delivery and the next investigation decision.
  RESUME_HIERARCHY: tickets/epics/2026-09-24_override_execution_performance_epic.md -> tickets/tasks/2026-09-24_measure_melder_creation_and_overrides_task.md.
- upgrade_normal_review: SWITCH_TRIGGER is explicit owner reopening or closure; further review was stopped.
  RESUME_HIERARCHY: tickets/tasks/2026-09-22_review_upgrade_to_normal_complexity_task.md.
- readme_status_badges: SWITCH_TRIGGER is owner acceptance or first hosted coverage failure evidence.
  RESUME_HIERARCHY: tickets/tasks/2026-09-06_readme_status_badges_task.md.
- embed_melder_banner: SWITCH_TRIGGER is owner acceptance or a requested presentation adjustment.
  RESUME_HIERARCHY: tickets/tasks/2026-09-06_embed_melder_banner_task.md.
- stateful_application_recovery: SWITCH_TRIGGER is owner selection of a concrete stateful recovery scenario.
  RESUME_HIERARCHY: tickets/epics/2026-09-07_stateful_application_recovery_epic.md -> linked source investigation and related scope/identity work.
- mediator_wiring_probe: SWITCH_TRIGGER is owner statement of remaining work or explicit checkout request.
  RESUME_HIERARCHY: tickets/tasks/2026-09-20_investigate_mediator_wiring_task.md.
- components_sliced_audit: SWITCH_TRIGGER is completed C3 pass with contradiction dispositions or owner scope redirect.
  RESUME_HIERARCHY: tickets/tasks/2026-09-21_systematic_components_audit_task.md.
- ir_phase_survey_1_4: SWITCH_TRIGGER is accepted tranche-1 records (driver plus phases 1-4) or an owner scope redirect.
  RESUME_HIERARCHY: tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md ->
  tickets/stories/2026-09-25_ir_phase_pipeline_survey_story.md ->
  tickets/tasks/2026-09-25_survey_compiler_phases_1_to_4_task.md.
- override_design_melder: SWITCH_TRIGGER is the design artifact plus owner decision requests.
  RESUME_HIERARCHY: tickets/epics/2026-09-24_override_execution_performance_epic.md ->
  tickets/tasks/2026-09-26_design_override_and_caller_input_execution_task.md.
- melder_long_run_growth: SWITCH_TRIGGER is a source-backed verdict plus added benchmark tests.
  RESUME_HIERARCHY: tickets/epics/2026-09-26_melder_long_run_throughput_truth_epic.md ->
  tickets/tasks/2026-09-26_investigate_melder_long_run_growth_task.md.
- melder_long_run_attribution: SWITCH_TRIGGER is measured attribution recorded with caveats.
  RESUME_HIERARCHY: tickets/epics/2026-09-26_melder_long_run_throughput_truth_epic.md ->
  tickets/tasks/2026-09-26_measure_melder_long_run_attribution_task.md.
- caller_input_strictness: SWITCH_TRIGGER is the responsible commit plus before/after runs.
  RESUME_HIERARCHY: tickets/tasks/2026-09-26_trace_caller_input_conjure_strictness_regression_task.md.
- missing_dependency_sockets: SWITCH_TRIGGER is patch docs plus owner-confirmed file list.
  RESUME_HIERARCHY: tickets/epics/2026-09-24_override_execution_performance_epic.md ->
  tickets/tasks/2026-09-26_implement_missing_dependency_sockets_task.md.
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
