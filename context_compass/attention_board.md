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
- NEW MESSAGE for updater_0 (from melder_0, 2026-09-26T11:30:45Z)
- NEW MESSAGE for updater_1 (from melder_0, 2026-09-26T11:30:45Z)
- NEW MESSAGE for updater_0 (from fable_0, 2026-09-26T11:50:16Z)
- NEW MESSAGE for updater_1 (from fable_0, 2026-09-26T11:50:16Z)
- NEW MESSAGE for updater_1 (from fable_0, 2026-09-26T12:46:34Z)
- NEW MESSAGE for melder_0 (from fable_0, 2026-09-26T13:18:22Z)
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
| override_design_melder | review | handoff | claude | melder_0 | none | Owner confirms closure of the design task (design v2 approved). | Evidence-backed override strategy with owner decisions. | Owner approves a strategy; implementation stories open. | tickets/tasks/2026-09-26_design_override_and_caller_input_execution_task.md | 2026-09-26T11:30:45Z | REQUIRED |
| override_many_collection_fix | review | handoff | claude | melder_0 | none | Owner reviews the collection-member fix (member paths, cache 13). | Each collection member builds its own many dependencies. | Owner accepts; closure sync. | tickets/tasks/2026-09-26_fix_collection_member_many_sharing_task.md | 2026-09-26T12:29:50Z | REQUIRED |
| override_site_plan_lowering | in_progress | implementation | claude | melder_0 | none | Write site_plan_lowering.py and site_plan_override_runtime.py, then wire the many_only sites. | Key-set plans for overrides (S3) with the normal lane parity-gated (S2). | S3a modules wired at four sites, tests green on 3.14t and GIL, measured. | tickets/tasks/2026-09-26_build_site_plan_lowering_task.md | 2026-09-26T12:43:58Z | REQUIRED |
| caller_input_strictness | review | handoff | claude | melder_0 | none | Owner reviews the cause timeline; fix is the missing-dependency socket (S1). | Responsible change identified with before/after runs and fix options. | Commit and fix options recorded; task moves to review. | tickets/tasks/2026-09-26_trace_caller_input_conjure_strictness_regression_task.md | 2026-09-26T00:42:21Z | REQUIRED |
| class_binding_annotations | ready | handoff | claude | melder_1 | none | On resume: raise the DECISION_REQUEST (validated one-line fallback). | Evidence-backed fix proposal for dropped class annotations. | Owner approves a plan or redirects. | tickets/tasks/2026-09-26_keep_class_binding_annotations_with_type_checking_names_task.md | 2026-09-26T11:56:25Z | REQUIRED |
| annotation_shape_guard | review | handoff | claude | melder_1 | none | Owner commits, runs suites, accepts or redirects. | Container parameters are caller inputs; conjure no longer refuses them. | Owner acceptance; closure sync and patch archive follow. | tickets/tasks/2026-09-26_align_annotation_shape_guard_with_phase1_caller_inputs_task.md | 2026-09-26T12:23:14Z | REQUIRED |
| creation_context_race | in_progress | discovery | claude | melder_1 | none | Owner chooses: finish the September freeze/drain design, or the measured lock-plus-release change. | Root cause of the concurrent first-meld CreationContext flake with an approved fix. | Owner approves a direction or redirects. | tickets/tasks/2026-09-26_investigate_concurrent_first_meld_creation_context_race_task.md | 2026-09-26T13:17:29Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| sig_determinism_phase8_story | done | fable_0 | tickets/stories/completed/2026-09-26_signature_determinism_and_phase8_digest_story.md | Tranche T1 (one signature leaf, phase-8 digest, live contract operands); docs promoted; owner accepted. | 2026-09-26T13:14:31Z |
| contract_override_operands | done | fable_0 | tickets/tasks/completed/2026-09-26_live_contract_override_operands_task.md | override rename; refs in rows; live hydration; identity across a cache hit (owner-run); gate retired. | 2026-09-26T13:14:31Z |
| sig_determinism_phase8 | done | fable_0 | tickets/tasks/completed/2026-09-26_hoist_phase8_pool_digest_task.md | Pool digest once per pass; None-first skip; M7 -34% at N=300 (owner-run). | 2026-09-26T13:14:31Z |
| sig_serializer_unify | done | fable_0 | tickets/tasks/completed/2026-09-26_unify_codegen_signature_serializer_task.md | One CodegenSignature leaf; byte-compatible freeze; determinism test green owner-run. | 2026-09-26T13:14:31Z |
| override_site_plan_s1 | done | melder_0 | tickets/tasks/completed/2026-09-26_build_site_graph_and_override_key_resolver_task.md | Site graph, key resolver, oracle; 31 tests; owner accepted. | 2026-09-26T12:13:26Z |
| release_0_2_55_melder_1 | done | melder_1 | tickets/tasks/completed/2026-09-26_notch_version_and_release_note_for_spell_id_and_annotation_fixes_task.md | Version 0.2.55; release note carries stable spell ids, cache gen 12, TYPE_CHECKING fix; assets deferred. | 2026-09-26T11:51:52Z |
| function_spell_ids | done | melder_1 | tickets/tasks/completed/2026-09-26_stabilize_function_spell_ids_across_processes_task.md | Address-free bind fingerprints; cache bundle rebuilt per non-full-hit conjure (gen 12); owner suites green. | 2026-09-26T11:31:13Z |
| conjure_validation_warnings | done | melder_0 | tickets/tasks/completed/2026-09-26_add_conjure_validation_warnings_flag_task.md | Opt-in conjure(validation_warnings=True) grouped report; default silent; patch archived. | 2026-09-26T10:12:55Z |
| inspect_signature_nameerror | done | melder_1 | tickets/tasks/completed/2026-09-26_fix_inspect_signature_nameerror_on_type_checking_annotations_task.md | FORWARDREF reads + SignatureReflection; suites green; docs, graph, assets current. | 2026-09-26T10:12:17Z |
| inspect_annotation_audit | done | melder_1 | tickets/tasks/completed/2026-09-26_build_annotation_integrity_audit_tool_task.md | Audit findings fixed; kept as test guard test_annotation_integrity.py. | 2026-09-26T10:12:17Z |
| unresolved_input_sockets_story | done | melder_0 | tickets/stories/completed/2026-09-26_unresolved_input_sockets_story.md | S1 shipped: unresolved inputs supplied at meld; follow-ups listed in the task. | 2026-09-26T08:54:37Z |
| missing_dependency_sockets | done | melder_0 | tickets/tasks/completed/2026-09-26_implement_missing_dependency_sockets_task.md | Steps 1-6 done; 3.14t/GIL qualified; patch lane archived. | 2026-09-26T08:54:37Z |
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
- ir_phase_survey_1_4: SWITCH_TRIGGER is owner acceptance of the tranche-1 records (task in review) or an owner scope redirect.
  RESUME_HIERARCHY: tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md ->
  tickets/stories/2026-09-25_ir_phase_pipeline_survey_story.md ->
  tickets/tasks/2026-09-25_survey_compiler_phases_1_to_4_task.md. Successors (ready, not routed):
  tickets/tasks/2026-09-26_survey_compiler_phases_5_to_7_task.md ->
  tickets/tasks/2026-09-26_survey_structural_snapshot_seam_task.md. Strategy and recovery protocol:
  the epic's Context / Handoff Summary, section DISCOVERY STRATEGY AND RECOVERY (2026-09-26).
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
- class_binding_annotations: SWITCH_TRIGGER is an owner decision on the fix proposal.
  RESUME_HIERARCHY: tickets/tasks/2026-09-26_keep_class_binding_annotations_with_type_checking_names_task.md.
- annotation_shape_guard: SWITCH_TRIGGER is owner acceptance (suites on the owner machine) or a redirect.
  RESUME_HIERARCHY: tickets/tasks/2026-09-26_align_annotation_shape_guard_with_phase1_caller_inputs_task.md.
- creation_context_race: SWITCH_TRIGGER is an evidenced root cause plus an owner decision on the fix.
  RESUME_HIERARCHY: tickets/tasks/2026-09-26_investigate_concurrent_first_meld_creation_context_race_task.md.
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
