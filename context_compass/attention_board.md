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
| scoped_creation_purge | in_progress | implementation | codex | updater_0 | none | Add regressions and implement native scoped purge. | Meld owns scope authority; Creations owns locked retirement. | Feature tests and generated assets pass. | tickets/tasks/2026-09-20_implement_scoped_creation_purge_task.md | 2026-09-20T22:06:15Z | REQUIRED |
| purge_scope_discovery | review | handoff | codex | updater_0 | none | Owner reviews the bounded Meld-to-Creations purge plan. | Authority matrix and 38 passing characterization checks. | Owner directs implementation. | tickets/tasks/2026-09-20_discover_purge_scope_ownership_task.md | 2026-09-20T21:43:07Z | REQUIRED |
| bind_lifecycle_hooks_planning | review | handoff | codex | updater_0 | none | Owner reviews the three bind-time lifecycle stages. | Draft epic preserves reference checks, Spell edits and post-bind callbacks. | Owner selects further discovery or implementation. | tickets/epics/2026-09-20_bind_lifecycle_hooks_and_reference_strategies_epic.md | 2026-09-20T08:04:19Z | REQUIRED |
| release_0_2_37_to_0_2_43 | review | handoff | codex | updater_0 | none | Owner reviews the 0.2.43 release document. | Verified release date, completed-work map and migration notes. | Owner accepts draft or requests revisions. | tickets/tasks/2026-09-20_prepare_0_2_37_to_0_2_42_release_document_task.md | 2026-09-20T07:54:22Z | REQUIRED |
| benchmark_spell_id_lookup | review | handoff | codex | updater_0 | none | Owner reviews keyword migration and separate setup finding. | 134 ID selectors corrected; original gauntlet and scoped checks pass. | Owner accepts repair or directs distinct setup follow-up. | tickets/tasks/2026-09-19_repair_benchmark_spell_id_lookup_task.md | 2026-09-20T01:15:40Z | REQUIRED |
| purge_scope_planning | review | handoff | codex | updater_0 | none | Owner reviews the completed epic/build-only pass. | Epic drafted; source and repository assets verified. | Owner accepts planning/build delivery. | tickets/tasks/2026-09-19_draft_purge_epic_and_refresh_assets_task.md | 2026-09-20T21:43:07Z | REQUIRED |
| readme_status_badges | review | handoff | codex | codex_1 | none | Owner reviews or promotes README/reporting changes. | Approved tagline, badges and current asset proofs. | Owner accepts implementation and hosted result. | tickets/tasks/2026-09-06_readme_status_badges_task.md | 2026-09-06T15:38:07Z | REQUIRED |
| embed_melder_banner | review | handoff | codex | codex_1 | none | Owner reviews final README integration. | Local banner source and public fallback validated. | Owner accepts ticket closure. | tickets/tasks/2026-09-06_embed_melder_banner_task.md | 2026-09-06T14:27:09Z | REQUIRED |
| stateful_application_recovery | ready | handoff | user | unassigned | none | Discuss one stateful recovery scenario. | Native replay coverage and partial/assisted recovery opportunities preserved. | Owner selects recovery contracts before implementation. | tickets/epics/2026-09-07_stateful_application_recovery_epic.md | 2026-09-07T19:17:55Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| workflows_responsibility_transfer | done | workflows_0 | tickets/tasks/completed/2026-09-20_transfer_workflows_1_responsibility_task.md | Succession and approved cleanup complete; twelve archive hashes verified. | 2026-09-20T22:34:55Z |
| 2026-09-06_ci_validation_stage_design_task | done | workflows_0 | tickets/tasks/completed/2026-09-06_ci_validation_stage_design_task.md | Owner-authorized completion; artifact disposition verified. | 2026-09-20T22:13:38Z |
| 2026-09-08_reproducible_uv_environment_task | done | workflows_0 | tickets/tasks/completed/2026-09-08_reproducible_uv_environment_task.md | Owner-authorized completion; artifact disposition verified. | 2026-09-20T22:13:38Z |
| 2026-09-13_sync_owner_uv_environment_task | done | workflows_0 | tickets/tasks/completed/2026-09-13_sync_owner_uv_environment_task.md | Owner-authorized completion; artifact disposition verified. | 2026-09-20T22:13:38Z |
| 2026-09-19_document_positional_meld_calls_task | done | workflows_0 | tickets/tasks/completed/2026-09-19_document_positional_meld_calls_task.md | Owner-authorized completion; artifact disposition verified. | 2026-09-20T22:13:38Z |
| 2026-09-20_teach_meld_string_names_task | done | workflows_0 | tickets/tasks/completed/2026-09-20_teach_meld_string_names_task.md | Owner-authorized completion; artifact disposition verified. | 2026-09-20T22:13:38Z |
| 2026-09-19_fix_feature_turn_in_failures_task | done | updater_0 | tickets/tasks/completed/2026-09-19_fix_feature_turn_in_failures_task.md | Owner turn-in; feature and reported repairs accepted; evidence retained. | 2026-09-20T00:25:59Z |
| 2026-09-19_discoverable_non_resolvable_registrations_epic | done | updater_0 | tickets/epics/completed/2026-09-19_discoverable_non_resolvable_registrations_epic.md | Owner turn-in; feature and reported repairs accepted; evidence retained. | 2026-09-20T00:25:59Z |
| 2026-09-19_discoverable_registration_contract_discovery_story | done | updater_0 | tickets/stories/completed/2026-09-19_discoverable_registration_contract_discovery_story.md | Owner turn-in; feature and reported repairs accepted; evidence retained. | 2026-09-20T00:25:59Z |
| 2026-09-19_discoverable_registration_modifier_story | done | updater_0 | tickets/stories/completed/2026-09-19_discoverable_registration_modifier_story.md | Owner turn-in; feature and reported repairs accepted; evidence retained. | 2026-09-20T00:25:59Z |
| 2026-09-19_caller_supplied_socket_compiler_story | done | updater_0 | tickets/stories/completed/2026-09-19_caller_supplied_socket_compiler_story.md | Owner turn-in; feature and reported repairs accepted; evidence retained. | 2026-09-20T00:25:59Z |
| 2026-09-19_discoverable_resolution_runtime_story | done | updater_0 | tickets/stories/completed/2026-09-19_discoverable_resolution_runtime_story.md | Owner turn-in; feature and reported repairs accepted; evidence retained. | 2026-09-20T00:25:59Z |
<!-- END USER-DEFINED: closed_anchors -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
### Active Attention Details
- scoped_creation_purge: SWITCH_TRIGGER is completed validation and documentation/build evidence.
  RESUME_HIERARCHY: tickets/epics/2026-09-19_scope_aware_creation_purge_epic.md ->
  tickets/tasks/2026-09-20_implement_scoped_creation_purge_task.md.
- purge_scope_discovery: SWITCH_TRIGGER is owner direction to implement the reviewed plan.
  RESUME_HIERARCHY: tickets/epics/2026-09-19_scope_aware_creation_purge_epic.md ->
  tickets/tasks/2026-09-20_discover_purge_scope_ownership_task.md.
- bind_lifecycle_hooks_planning: SWITCH_TRIGGER is owner direction after reviewing the draft; no implementation yet.
  RESUME_HIERARCHY: tickets/epics/2026-09-20_bind_lifecycle_hooks_and_reference_strategies_epic.md.
- release_0_2_37_to_0_2_43: SWITCH_TRIGGER is owner acceptance or requested edits to the release draft.
  RESUME_HIERARCHY: tickets/tasks/2026-09-20_prepare_0_2_37_to_0_2_42_release_document_task.md.
- benchmark_spell_id_lookup: SWITCH_TRIGGER is owner review or direction on the separate shared-gauntlet setup failure.
  RESUME_HIERARCHY: tickets/tasks/2026-09-19_repair_benchmark_spell_id_lookup_task.md.
- purge_scope_planning: SWITCH_TRIGGER is owner acceptance of the completed planning/build pass.
  RESUME_HIERARCHY: tickets/epics/2026-09-19_scope_aware_creation_purge_epic.md ->
  tickets/tasks/2026-09-19_draft_purge_epic_and_refresh_assets_task.md.
- readme_status_badges: SWITCH_TRIGGER is owner acceptance or first hosted coverage failure evidence.
  RESUME_HIERARCHY: tickets/tasks/2026-09-06_readme_status_badges_task.md.
- embed_melder_banner: SWITCH_TRIGGER is owner acceptance or a requested presentation adjustment.
  RESUME_HIERARCHY: tickets/tasks/2026-09-06_embed_melder_banner_task.md.
- stateful_application_recovery: SWITCH_TRIGGER is owner selection of a concrete stateful recovery scenario.
  RESUME_HIERARCHY: tickets/epics/2026-09-07_stateful_application_recovery_epic.md -> linked source investigation and related scope/identity work.
<!-- END USER-DEFINED: notes -->
