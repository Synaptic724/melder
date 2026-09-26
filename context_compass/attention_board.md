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
- NEW MESSAGE for updater_1 (from fable_0, 2026-09-26T09:08:43Z)
- NEW MESSAGE for melder_1 (from melder_0, 2026-09-26T09:35:35Z)
- NEW MESSAGE for fable_0 (from melder_0, 2026-09-26T09:38:26Z)
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
| ir_phase_survey_1_4 | review | handoff | claude | fable_0 | none | Owner reviews driver.md, phase_01-04.md and structural_driver.md. | Driver and phases 1-4 recorded from source with classified object holds. | Owner accepts tranche-1 records or redirects scope. | tickets/tasks/2026-09-25_survey_compiler_phases_1_to_4_task.md | 2026-09-26T01:07:48Z | REQUIRED |
| ir_phase_survey_5_7 | review | handoff | claude | fable_0 | none | Owner reviews phase_05-07.md and resolution_driver.md. | Phases 5-7 and the full-hit load path recorded from source (D1, D2, D6). | Owner accepts tranche-2 records or redirects scope. | tickets/tasks/2026-09-26_survey_compiler_phases_5_to_7_task.md | 2026-09-26T07:23:22Z | REQUIRED |
| ir_phase_survey_seam | review | handoff | claude | fable_0 | none | Owner reviews the survey records (summary.md first); no design decisions are asked in this lane. | Cache mechanics, key composition, invalidation surface and summary.md (D3, D4, D5; D1-D6 consolidated). | Owner accepts the records (Milestone 1, closure sync) or redirects scope. | tickets/tasks/2026-09-26_survey_structural_snapshot_seam_task.md | 2026-09-26T07:38:41Z | REQUIRED |
| ir_phase_cost_model | review | handoff | claude | fable_0 | none | Owner reviews cost_model.md (counted rows, measured rows, owner-run command). | Per-stage cost model for phases 1-11 with two owner-run measurement sources. | Owner accepts the cost model or redirects scope. | tickets/tasks/2026-09-26_model_phase_pipeline_costs_task.md | 2026-09-26T08:13:27Z | REQUIRED |
| ir_phase_improvement_plan | review | handoff | claude | fable_0 | none | Owner confirms closure of the plan story (T1 decided: C-H + C-A; C-B deferred). | Thirteen ranked candidates; T1 decided by the owner. | Owner confirms acceptance; closure sync follows. | tickets/tasks/2026-09-26_rank_phase_improvement_candidates_task.md | 2026-09-26T09:08:28Z | REQUIRED |
| sig_determinism_phase8 | in_progress | implementation | claude | fable_0 | none | U2: leaf CodegenSignature module + facade delegations; then U3 tests. | One signature implementation, determinism test, phase-8 pool digest. | Both code tasks in review with owner-run suites green. | tickets/tasks/2026-09-26_unify_codegen_signature_serializer_task.md | 2026-09-26T09:29:36Z | REQUIRED |
| conjure_validation_warnings | review | handoff | claude | melder_0 | none | Owner reviews the flag, tests, docs and rebuilt assets. | Opt-in Spellbook.conjure(validation_warnings=False); default silent, True logs grouped Phase-4 warnings. | Owner accepts; patch docs archived and task closed. | tickets/tasks/2026-09-26_add_conjure_validation_warnings_flag_task.md | 2026-09-26T09:38:26Z | REQUIRED |
| override_design_melder | in_progress | discovery | claude | melder_0 | none | Paused for conjure_validation_warnings; resume with the executor/targeting split probe. | Evidence-backed override strategy with owner decisions. | Owner approves a strategy; implementation stories open. | tickets/tasks/2026-09-26_design_override_and_caller_input_execution_task.md | 2026-09-26T09:09:11Z | REQUIRED |
| caller_input_strictness | review | handoff | claude | melder_0 | none | Owner reviews the cause timeline; fix is the missing-dependency socket (S1). | Responsible change identified with before/after runs and fix options. | Commit and fix options recorded; task moves to review. | tickets/tasks/2026-09-26_trace_caller_input_conjure_strictness_regression_task.md | 2026-09-26T00:42:21Z | REQUIRED |
| inspect_signature_nameerror | blocked | handoff | claude | melder_1 | annotation audit first (owner) | Fold the audit findings in, then apply the approved src edits. | Tested fix for TYPE_CHECKING-annotation NameErrors, docs and rebuilt assets. | Audit reported, then fix applied with tests and assets. | tickets/tasks/2026-09-26_fix_inspect_signature_nameerror_on_type_checking_annotations_task.md | 2026-09-26T09:17:15Z | REQUIRED |
| inspect_annotation_audit | review | handoff | claude | melder_1 | none | Owner reviews findings, confirms fixes and tool placement. | Every never-evaluable annotation in src/melder located with file:line. | Owner confirms fix set and tool placement, or redirects. | tickets/tasks/2026-09-26_build_annotation_integrity_audit_tool_task.md | 2026-09-26T09:23:31Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| unresolved_input_sockets_story | done | melder_0 | tickets/stories/completed/2026-09-26_unresolved_input_sockets_story.md | S1 shipped: unresolved inputs supplied at meld; follow-ups listed in the task. | 2026-09-26T08:54:37Z |
| missing_dependency_sockets | done | melder_0 | tickets/tasks/completed/2026-09-26_implement_missing_dependency_sockets_task.md | Steps 1-6 done; 3.14t/GIL qualified; patch lane archived. | 2026-09-26T08:54:37Z |
| version_assets_0_2_54 | done | melder_0 | tickets/tasks/completed/2026-09-26_bump_version_rebuild_assets_for_unresolved_inputs_task.md | 0.2.54; assets and LLM bundles rebuilt and checked; release note detailed. | 2026-09-26T08:54:37Z |
| melder_long_run_epic | done | melder_1 | tickets/epics/completed/2026-09-26_melder_long_run_throughput_truth_epic.md | No leak; harness attributed and fixed; lanes isolated. | 2026-09-26T08:32:04Z |
| gauntlet_harness_fix | done | melder_1 | tickets/tasks/completed/2026-09-26_fix_gauntlet_sample_storage_and_melder_lane_isolation_task.md | array('q') storage; Melder lane parity-guarded. | 2026-09-26T08:32:04Z |
| melder_long_run_attribution | done | melder_1 | tickets/tasks/completed/2026-09-26_measure_melder_long_run_attribution_task.md | 2x2 controls: harness retention, not Melder. | 2026-09-26T08:32:04Z |
| melder_long_run_growth | done | melder_1 | tickets/tasks/completed/2026-09-26_investigate_melder_long_run_growth_task.md | No retained growth; guard tests added. | 2026-09-26T08:32:04Z |
| version_notch_0_2_53 | done | melder_0 | tickets/tasks/completed/2026-09-26_bump_version_for_deadlock_fix_task.md | Version and next-release header at 0.2.53; asset rebuild held. | 2026-09-26T00:11:19Z |
| override_contract_story | done | melder_0, melder_1 | tickets/stories/completed/2026-09-25_verify_override_writer_and_contract_story.md | Deadlock fixed; contract verified; items 4a/5c chosen; open items carried. | 2026-09-26T00:15:00Z |
| override_contract_verify | done | melder_1 | tickets/tasks/completed/2026-09-25_verify_override_behavior_contract_task.md | Items 1-8 verified with regression matrix; owner-directed turn-in. | 2026-09-26T00:12:00Z |
| creation_slot_guards_impl | done | melder_0 | tickets/tasks/completed/2026-09-25_implement_creation_slot_build_guards_task.md | Per-slot build guards; deadlock fixed; docs, graph and release note updated. | 2026-09-25T23:47:39Z |
| deadlock_regression_tests | done | melder_0 | tickets/tasks/completed/2026-09-25_add_meld_lock_order_deadlock_regression_tests_task.md | 12 lock-order cases must complete (3.14t and GIL). | 2026-09-25T23:47:39Z |
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
- ir_phase_survey_5_7: SWITCH_TRIGGER is accepted tranche-2 records (phases 5-7 plus the full-hit load path) or an owner scope redirect.
  RESUME_HIERARCHY: tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md ->
  tickets/stories/2026-09-25_ir_phase_pipeline_survey_story.md ->
  tickets/tasks/2026-09-26_survey_compiler_phases_5_to_7_task.md. Strategy and recovery protocol:
  the epic's Context / Handoff Summary, section DISCOVERY STRATEGY AND RECOVERY (2026-09-26).
- ir_phase_survey_seam: SWITCH_TRIGGER is summary.md with D1-D6 accepted by the owner, or an owner scope redirect.
  RESUME_HIERARCHY: tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md ->
  tickets/stories/2026-09-25_ir_phase_pipeline_survey_story.md ->
  tickets/tasks/2026-09-26_survey_structural_snapshot_seam_task.md. Strategy and recovery protocol:
  the epic's Context / Handoff Summary, section DISCOVERY STRATEGY AND RECOVERY (2026-09-26).
- ir_phase_cost_model: SWITCH_TRIGGER is owner acceptance of cost_model.md (task 1 in review) or an owner scope redirect.
  RESUME_HIERARCHY: tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md ->
  tickets/stories/2026-09-26_phase_pipeline_improvement_plan_story.md ->
  tickets/tasks/2026-09-26_model_phase_pipeline_costs_task.md.
- ir_phase_improvement_plan: SWITCH_TRIGGER is owner closure confirmation of the plan story (tranche decided 2026-09-26).
  RESUME_HIERARCHY: tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md ->
  tickets/stories/2026-09-26_phase_pipeline_improvement_plan_story.md ->
  tickets/tasks/2026-09-26_rank_phase_improvement_candidates_task.md. Fact base: artifacts/ir_phase_improvement_20260926/cost_model.md
  and artifacts/ir_phase_survey_20260925/summary.md.
- sig_determinism_phase8: SWITCH_TRIGGER is owner confirmation of each Propose -> Confirm message, then suites green owner-run.
  RESUME_HIERARCHY: tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md ->
  tickets/stories/2026-09-26_signature_determinism_and_phase8_digest_story.md ->
  tickets/tasks/2026-09-26_unify_codegen_signature_serializer_task.md (then
  tickets/tasks/2026-09-26_hoist_phase8_pool_digest_task.md). Patch docs:
  system_docs/patches/active/codegen_signature_determinism_2026_09_26/.
- ir_phase_survey_1_4: SWITCH_TRIGGER is owner acceptance of the tranche-1 records (task in review) or an owner scope redirect.
  RESUME_HIERARCHY: tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md ->
  tickets/stories/2026-09-25_ir_phase_pipeline_survey_story.md ->
  tickets/tasks/2026-09-25_survey_compiler_phases_1_to_4_task.md. Successors (ready, not routed):
  tickets/tasks/2026-09-26_survey_compiler_phases_5_to_7_task.md ->
  tickets/tasks/2026-09-26_survey_structural_snapshot_seam_task.md. Strategy and recovery protocol:
  the epic's Context / Handoff Summary, section DISCOVERY STRATEGY AND RECOVERY (2026-09-26).
- conjure_validation_warnings: SWITCH_TRIGGER is owner acceptance (then patch-doc archive and closure).
  RESUME_HIERARCHY: tickets/tasks/2026-09-26_add_conjure_validation_warnings_flag_task.md. Patch docs:
  system_docs/patches/active/conjure_validation_warnings_2026_09_26/.
- override_design_melder: SWITCH_TRIGGER is the design artifact plus owner decision requests.
  RESUME_HIERARCHY: tickets/epics/2026-09-24_override_execution_performance_epic.md ->
  tickets/tasks/2026-09-26_design_override_and_caller_input_execution_task.md.
- caller_input_strictness: SWITCH_TRIGGER is the responsible commit plus before/after runs.
  RESUME_HIERARCHY: tickets/tasks/2026-09-26_trace_caller_input_conjure_strictness_regression_task.md.
- inspect_signature_nameerror: SWITCH_TRIGGER is the annotation audit's findings (owner redirect), then the fix applied.
  RESUME_HIERARCHY: tickets/tasks/2026-09-26_fix_inspect_signature_nameerror_on_type_checking_annotations_task.md.
- inspect_annotation_audit: SWITCH_TRIGGER is the audit run over src/melder with findings recorded, or an owner redirect.
  RESUME_HIERARCHY: tickets/tasks/2026-09-26_build_annotation_integrity_audit_tool_task.md.
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
