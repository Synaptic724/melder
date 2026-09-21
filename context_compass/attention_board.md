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
<!-- END USER-DEFINED: alerts -->

## Active Items
| work_item | status | mode | owner | agent_name | blocker | next | outcome | exit_signal | ticket | updated_at | reread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: active_items -->
| next_version_release | review | handoff | codex | updater_0 | none | Owner reviews or extends the next-version release draft. | Purge inputs, modes, scope and disposal documented. | Owner selects further release work. | tickets/tasks/2026-09-21_draft_next_version_release_task.md | 2026-09-21T00:33:00Z | REQUIRED |
| bind_lifecycle_hooks | review | handoff | codex | updater_0 | none | Owner reviews the full impact map and selects implementation. | Recording, replay, cleanup and all affected owners mapped. | Owner selects the implementation tranche. | tickets/tasks/2026-09-21_investigate_bind_lifecycle_hooks_task.md | 2026-09-21T10:46:10Z | REQUIRED |
| release_0_2_37_to_0_2_43 | review | handoff | codex | updater_0 | none | Owner reviews the 0.2.43 release document. | Verified release date, completed-work map and migration notes. | Owner accepts draft or requests revisions. | tickets/tasks/2026-09-20_prepare_0_2_37_to_0_2_42_release_document_task.md | 2026-09-20T07:54:22Z | REQUIRED |
| benchmark_spell_id_lookup | review | handoff | codex | updater_0 | none | Owner reviews keyword migration and separate setup finding. | 134 ID selectors corrected; original gauntlet and scoped checks pass. | Owner accepts repair or directs distinct setup follow-up. | tickets/tasks/2026-09-19_repair_benchmark_spell_id_lookup_task.md | 2026-09-20T01:15:40Z | REQUIRED |
| readme_status_badges | review | handoff | codex | codex_1 | none | Owner reviews or promotes README/reporting changes. | Approved tagline, badges and current asset proofs. | Owner accepts implementation and hosted result. | tickets/tasks/2026-09-06_readme_status_badges_task.md | 2026-09-06T15:38:07Z | REQUIRED |
| embed_melder_banner | review | handoff | codex | codex_1 | none | Owner reviews final README integration. | Local banner source and public fallback validated. | Owner accepts ticket closure. | tickets/tasks/2026-09-06_embed_melder_banner_task.md | 2026-09-06T14:27:09Z | REQUIRED |
| stateful_application_recovery | ready | handoff | user | unassigned | none | Discuss one stateful recovery scenario. | Native replay coverage and partial/assisted recovery opportunities preserved. | Owner selects recovery contracts before implementation. | tickets/epics/2026-09-07_stateful_application_recovery_epic.md | 2026-09-07T19:17:55Z | REQUIRED |
| mediator_wiring_probe | in_progress | discovery | opencode | muse | none | Ask owner what remains before this lane is done. | Doc patches plus verified indexes stand; closeout only on explicit checkout. | Owner states remaining work or requests checkout. | tickets/tasks/2026-09-20_investigate_mediator_wiring_task.md | 2026-09-21T00:11:00Z | REQUIRED |
| components_sliced_audit | in_progress | discovery | opencode | muse | none | Verify indexes then slice front matter plus first C3 component. | Per-component notes plus closing contradiction list with evidence. | C3 pass complete with dispositions or owner redirects scope. | tickets/tasks/2026-09-21_systematic_components_audit_task.md | 2026-09-21T00:16:57Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| intermediate_purge_example | done | workflows_0 | tickets/tasks/completed/2026-09-21_add_intermediate_purge_example_task.md | Lesson 39 added; 38 examples, 39 docs tests, strict HTML and fidelity checks pass. | 2026-09-21T00:59:10Z |
| scoped_creation_purge_epic | done | updater_0 | tickets/epics/completed/2026-09-19_scope_aware_creation_purge_epic.md | Owner accepted turn-in; documentation/assets verified and evidence retained. | 2026-09-21T00:37:37Z |
| scoped_creation_purge | done | updater_0 | tickets/tasks/completed/2026-09-20_implement_scoped_creation_purge_task.md | Owner accepted turn-in; documentation/assets verified and evidence retained. | 2026-09-21T00:37:37Z |
| purge_scope_discovery | done | updater_0 | tickets/tasks/completed/2026-09-20_discover_purge_scope_ownership_task.md | Owner accepted turn-in; documentation/assets verified and evidence retained. | 2026-09-21T00:37:37Z |
| purge_scope_planning | done | updater_0 | tickets/tasks/completed/2026-09-19_draft_purge_epic_and_refresh_assets_task.md | Owner accepted turn-in; documentation/assets verified and evidence retained. | 2026-09-21T00:37:37Z |
| shared_board_cleanup | done | workflows_0 | tickets/tasks/completed/2026-09-21_cleanup_shared_context_compass_boards_task.md | Departed entries and obsolete notices retired; history archived; live work preserved. | 2026-09-21T00:22:34Z |
| workflows_responsibility_transfer | done | workflows_0 | tickets/tasks/completed/2026-09-20_transfer_workflows_1_responsibility_task.md | Succession and approved cleanup complete; twelve archive hashes verified. | 2026-09-20T22:34:55Z |
| 2026-09-06_ci_validation_stage_design_task | done | workflows_0 | tickets/tasks/completed/2026-09-06_ci_validation_stage_design_task.md | Owner-authorized completion; artifact disposition verified. | 2026-09-20T22:13:38Z |
| 2026-09-08_reproducible_uv_environment_task | done | workflows_0 | tickets/tasks/completed/2026-09-08_reproducible_uv_environment_task.md | Owner-authorized completion; artifact disposition verified. | 2026-09-20T22:13:38Z |
| 2026-09-13_sync_owner_uv_environment_task | done | workflows_0 | tickets/tasks/completed/2026-09-13_sync_owner_uv_environment_task.md | Owner-authorized completion; artifact disposition verified. | 2026-09-20T22:13:38Z |
| 2026-09-19_document_positional_meld_calls_task | done | workflows_0 | tickets/tasks/completed/2026-09-19_document_positional_meld_calls_task.md | Owner-authorized completion; artifact disposition verified. | 2026-09-20T22:13:38Z |
| 2026-09-20_teach_meld_string_names_task | done | workflows_0 | tickets/tasks/completed/2026-09-20_teach_meld_string_names_task.md | Owner-authorized completion; artifact disposition verified. | 2026-09-20T22:13:38Z |
<!-- END USER-DEFINED: closed_anchors -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
### Active Attention Details
- next_version_release: SWITCH_TRIGGER is draft completion and owner review.
  RESUME_HIERARCHY: tickets/tasks/2026-09-21_draft_next_version_release_task.md.
- bind_lifecycle_hooks: SWITCH_TRIGGER is owner selection of implementation after the expanded impact review.
  RESUME_HIERARCHY: tickets/epics/2026-09-20_bind_lifecycle_hooks_and_reference_strategies_epic.md ->
  tickets/tasks/2026-09-21_investigate_bind_lifecycle_hooks_task.md.
- release_0_2_37_to_0_2_43: SWITCH_TRIGGER is owner acceptance or requested edits to the release draft.
  RESUME_HIERARCHY: tickets/tasks/2026-09-20_prepare_0_2_37_to_0_2_42_release_document_task.md.
- benchmark_spell_id_lookup: SWITCH_TRIGGER is owner review or direction on the separate shared-gauntlet setup failure.
  RESUME_HIERARCHY: tickets/tasks/2026-09-19_repair_benchmark_spell_id_lookup_task.md.
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
<!-- END USER-DEFINED: notes -->
