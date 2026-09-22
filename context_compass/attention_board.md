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
| upgrade_normal_review | in_progress | discovery | codex | updater_1 | none | Trace graduation imports, ownership and rollback. | Source-backed complexity review and simplification recommendations. | Review delivered to owner. | tickets/tasks/2026-09-22_review_upgrade_to_normal_complexity_task.md | 2026-09-22T22:54:06Z | REQUIRED |
| named_lesser_plan_refresh | review | handoff | codex | updater_0 | none | Review publication ordering and live-load coordination. | Deep implementation trace and regression matrix. | First runtime patch has explicit concurrency contracts. | tickets/tasks/2026-09-22_refresh_named_lesser_conduit_plan_task.md | 2026-09-22T21:16:32Z | REQUIRED |
| graduation_packaged_assets | blocked | handoff | codex | updater_0 | Owner build-asset hold. | Wait for packaged generation authorization. | Preserve completed source while packaging stays queued. | Owner releases build hold. | tickets/tasks/2026-09-22_refresh_graduation_packaged_assets_when_approved_task.md | 2026-09-22T14:41:23Z | REQUIRED |
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
| epic_version_notches | done | updater_0 | tickets/tasks/completed/2026-09-22_correct_epic_version_baseline_task.md | Corrected to 0.2.47: baseline 0.2.43 plus four epics; assets held. | 2026-09-22T20:11:00Z |
| pool_hook_epic | done | updater_0 | tickets/epics/completed/2026-09-21_runtime_hook_lifecycle_and_adjustment_epic.md | Owner turn-in; evidence retained, packaging held separately. | 2026-09-22T19:50:34Z |
| pooled_hook_discovery | done | updater_0 | tickets/tasks/completed/2026-09-22_investigate_pooled_conduit_hook_reset_task.md | Owner turn-in; evidence retained, packaging held separately. | 2026-09-22T19:50:34Z |
| local_hook_tracking | done | updater_0 | tickets/tasks/completed/2026-09-22_add_local_hook_setters_and_tracking_task.md | Owner turn-in; evidence retained, packaging held separately. | 2026-09-22T19:50:34Z |
| release_0_2_37_to_0_2_43 | done | updater_0 | tickets/tasks/completed/2026-09-20_prepare_0_2_37_to_0_2_42_release_document_task.md | Owner turn-in; evidence retained, packaging held separately. | 2026-09-22T19:50:34Z |
| benchmark_spell_id_lookup | done | updater_0 | tickets/tasks/completed/2026-09-19_repair_benchmark_spell_id_lookup_task.md | Owner turn-in; evidence retained, packaging held separately. | 2026-09-22T19:50:34Z |
| bind_hooks_epic | done | updater_0 | tickets/epics/completed/2026-09-20_bind_lifecycle_hooks_and_reference_strategies_epic.md | Owner turn-in; evidence retained, packaging held separately. | 2026-09-22T18:47:41Z |
| bind_hooks_discovery | done | updater_0 | tickets/tasks/completed/2026-09-21_investigate_bind_lifecycle_hooks_task.md | Owner turn-in; evidence retained, packaging held separately. | 2026-09-22T18:47:41Z |
| bind_hooks_implementation | done | updater_0 | tickets/tasks/completed/2026-09-21_implement_bind_lifecycle_hooks_task.md | Owner turn-in; evidence retained, packaging held separately. | 2026-09-22T18:47:41Z |
| bind_hook_examples | done | updater_0 | tickets/tasks/completed/2026-09-22_add_bind_hook_intermediate_and_expert_examples_task.md | Owner turn-in; evidence retained, packaging held separately. | 2026-09-22T18:47:41Z |
| next_version_release | done | updater_0 | tickets/tasks/completed/2026-09-21_draft_next_version_release_task.md | Draft extended with graduation; source version 0.2.45; assets held. | 2026-09-22T15:13:55Z |
| graduated_conduit_epic | done | updater_0 | tickets/epics/completed/2026-09-22_graduated_conduit_spellbook_ownership_and_configuration_epic.md | Independent Book and hooks; shared policy verified; packaging held separately. | 2026-09-22T14:41:23Z |
<!-- END USER-DEFINED: closed_anchors -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
### Active Attention Details
- upgrade_normal_review: SWITCH_TRIGGER is delivered review or owner-directed implementation scope.
  RESUME_HIERARCHY: tickets/tasks/2026-09-22_review_upgrade_to_normal_complexity_task.md.
- named_lesser_plan_refresh: SWITCH_TRIGGER is an agreed named-lifecycle concurrency contract for the first runtime patch.
  RESUME_HIERARCHY: tickets/epics/2026-09-06_named_lesser_conduit_discovery_epic.md -> tickets/tasks/2026-09-22_refresh_named_lesser_conduit_plan_task.md.
- graduation_packaged_assets: SWITCH_TRIGGER is owner approval of packaged build generation.
  RESUME_HIERARCHY: tickets/tasks/2026-09-22_refresh_graduation_packaged_assets_when_approved_task.md.
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
