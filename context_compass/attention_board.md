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
- NEW MESSAGE for codex_1 (from workflows_1, 2026-09-06T18:41:11Z)
- NEW MESSAGE for codex_1 (from workflows_1, 2026-09-06T17:41:58Z)
<!-- END USER-DEFINED: alerts -->

## Active Items
| work_item | status | mode | owner | agent_name | blocker | next | outcome | exit_signal | ticket | updated_at | reread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: active_items -->
| document_positional_meld_calls | review | handoff | codex | workflows_1 | none | Owner reviews and promotes documentation corrections. | 150 replacements; docs build and publication audit pass. | Owner accepts documentation update. | tickets/tasks/2026-09-19_document_positional_meld_calls_task.md | 2026-09-19T21:56:08Z | REQUIRED |
| discoverable_non_resolvable_registrations | in_progress | validation | codex | updater_0 | none | Verify overrides with ordinary constructor errors. | Correct runtime values, then Nexus and crystal replay. | Runtime compatibility passes and S5/S6 route is active. | tickets/tasks/2026-09-19_enforce_required_override_execution_task.md | 2026-09-19T22:21:52Z | REQUIRED |
| sync_owner_uv_environment | review | handoff | codex | workflows_1 | none | Owner resumes development and restarts editor Ruff. | Melder 0.2.40 and locked tools on existing no-GIL Python. | Owner accepts verified environment sync. | tickets/tasks/2026-09-13_sync_owner_uv_environment_task.md | 2026-09-13T20:48:32Z | REQUIRED |
| reproducible_uv_environment | review | handoff | codex | workflows_1 | none | Owner reviews and commits locked setup and CI. | Reproducible dependencies with the no-GIL matrix preserved. | Owner accepts changes and checks the hosted matrix. | tickets/tasks/2026-09-08_reproducible_uv_environment_task.md | 2026-09-08T11:26:20Z | REQUIRED |
| readme_status_badges | review | handoff | codex | codex_1 | none | Owner reviews or promotes README/reporting changes. | Approved tagline, badges and current asset proofs. | Owner accepts implementation and hosted result. | tickets/tasks/2026-09-06_readme_status_badges_task.md | 2026-09-06T15:38:07Z | REQUIRED |
| embed_melder_banner | review | handoff | codex | codex_1 | none | Owner reviews final README integration. | Local banner source and public fallback validated. | Owner accepts ticket closure. | tickets/tasks/2026-09-06_embed_melder_banner_task.md | 2026-09-06T14:27:09Z | REQUIRED |
| ci_validation_stage_design | review | handoff | codex | workflows_1 | none | Owner promotes partial-rerun coverage correction. | Complete same-run coverage without repeated tests. | Owner accepts corrected reporting in a fresh run. | tickets/tasks/2026-09-06_ci_validation_stage_design_task.md | 2026-09-06T18:58:09Z | REQUIRED |
| stateful_application_recovery | ready | handoff | user | unassigned | none | Discuss one stateful recovery scenario. | Native replay coverage and partial/assisted recovery opportunities preserved. | Owner selects recovery contracts before implementation. | tickets/epics/2026-09-07_stateful_application_recovery_epic.md | 2026-09-07T19:17:55Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| turn_in_updater_0_work | done | updater_0 | tickets/tasks/completed/2026-09-19_turn_in_updater_0_work_task.md | 14 delivered records closed; object proposals backlogged; evidence retained. | 2026-09-19T14:55:42Z |
| 2026-09-13_provider_artifact_ownership_and_existing_instance_planning_epic | done | updater_0 | tickets/epics/completed/2026-09-13_provider_artifact_ownership_and_existing_instance_planning_epic.md | Owner turn-in; delivered scope accepted, deferred object ideas backlogged. | 2026-09-19T14:53:20Z |
| 2026-09-19_existing_instance_protocol_admission_story | done | updater_0 | tickets/stories/completed/2026-09-19_existing_instance_protocol_admission_story.md | Owner turn-in; delivered scope accepted, deferred object ideas backlogged. | 2026-09-19T14:53:20Z |
| 2026-09-13_provider_artifact_ownership_story | done | updater_0 | tickets/stories/completed/2026-09-13_provider_artifact_ownership_story.md | Owner turn-in; delivered scope accepted, deferred object ideas backlogged. | 2026-09-19T14:53:20Z |
| 2026-09-13_existing_instance_planning_story | done | updater_0 | tickets/stories/completed/2026-09-13_existing_instance_planning_story.md | Owner turn-in; delivered scope accepted, deferred object ideas backlogged. | 2026-09-19T14:53:20Z |
| 2026-09-19_repair_existing_instance_protocol_admission_task | done | updater_0 | tickets/tasks/completed/2026-09-19_repair_existing_instance_protocol_admission_task.md | Owner turn-in; delivered scope accepted, deferred object ideas backlogged. | 2026-09-19T14:53:20Z |
| 2026-09-19_investigate_existing_instance_protocol_validation_task | done | updater_0 | tickets/tasks/completed/2026-09-19_investigate_existing_instance_protocol_validation_task.md | Owner turn-in; delivered scope accepted, deferred object ideas backlogged. | 2026-09-19T14:53:20Z |
| 2026-09-13_repair_provider_artifact_ownership_task | done | updater_0 | tickets/tasks/completed/2026-09-13_repair_provider_artifact_ownership_task.md | Owner turn-in; delivered scope accepted, deferred object ideas backlogged. | 2026-09-19T14:53:20Z |
| 2026-09-13_repair_existing_instance_planning_task | done | updater_0 | tickets/tasks/completed/2026-09-13_repair_existing_instance_planning_task.md | Owner turn-in; delivered scope accepted, deferred object ideas backlogged. | 2026-09-19T14:53:20Z |
| 2026-09-13_compare_existing_object_ownership_di_task | done | updater_0 | tickets/tasks/completed/2026-09-13_compare_existing_object_ownership_di_task.md | Owner turn-in; delivered scope accepted, deferred object ideas backlogged. | 2026-09-19T14:53:20Z |
| 2026-09-13_build_commandops_local_wheel_task | done | updater_0 | tickets/tasks/completed/2026-09-13_build_commandops_local_wheel_task.md | Owner turn-in; delivered scope accepted, deferred object ideas backlogged. | 2026-09-19T14:53:20Z |
| 2026-09-13_optional_dependency_default_resolution_test_task | done | updater_0 | tickets/tasks/completed/2026-09-13_optional_dependency_default_resolution_test_task.md | Owner turn-in; delivered scope accepted, deferred object ideas backlogged. | 2026-09-19T14:53:20Z |
<!-- END USER-DEFINED: closed_anchors -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
### Active Attention Details
- document_positional_meld_calls: SWITCH_TRIGGER is owner acceptance or new documentation failure evidence.
  RESUME_HIERARCHY: tickets/tasks/2026-09-19_document_positional_meld_calls_task.md.
- discoverable_non_resolvable_registrations: SWITCH_TRIGGER is verified runtime compatibility and S5/S6 continuation.
  RESUME_HIERARCHY: tickets/epics/2026-09-19_discoverable_non_resolvable_registrations_epic.md ->
  tickets/stories/2026-09-19_discoverable_resolution_runtime_story.md ->
  tickets/tasks/2026-09-19_enforce_required_override_execution_task.md.
- sync_owner_uv_environment: SWITCH_TRIGGER is owner acceptance or new environment failure evidence.
  RESUME_HIERARCHY: tickets/tasks/2026-09-13_sync_owner_uv_environment_task.md.
- reproducible_uv_environment: SWITCH_TRIGGER is owner acceptance or new hosted matrix failure evidence.
  RESUME_HIERARCHY: tickets/tasks/2026-09-08_reproducible_uv_environment_task.md.
- readme_status_badges: SWITCH_TRIGGER is owner acceptance or first hosted coverage failure evidence.
  RESUME_HIERARCHY: tickets/tasks/2026-09-06_readme_status_badges_task.md.
- embed_melder_banner: SWITCH_TRIGGER is owner acceptance or a requested presentation adjustment.
  RESUME_HIERARCHY: tickets/tasks/2026-09-06_embed_melder_banner_task.md.
- ci_validation_stage_design: SWITCH_TRIGGER is owner acceptance or new hosted failure evidence.
  RESUME_HIERARCHY: tickets/tasks/2026-09-06_ci_validation_stage_design_task.md.
- stateful_application_recovery: SWITCH_TRIGGER is owner selection of a concrete stateful recovery scenario.
  RESUME_HIERARCHY: tickets/epics/2026-09-07_stateful_application_recovery_epic.md -> linked source investigation and related scope/identity work.
<!-- END USER-DEFINED: notes -->
