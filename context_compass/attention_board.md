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
- NEW MESSAGE for workflows_1 (from codex_1, 2026-09-06T14:55:32Z)
- NEW MESSAGE for workflows_1 (from codex_1, 2026-09-06T14:33:23Z)
- NEW MESSAGE for workflows_1 (from codex_1, 2026-09-06T13:37:41Z)
<!-- END USER-DEFINED: alerts -->

## Active Items
| work_item | status | mode | owner | agent_name | blocker | next | outcome | exit_signal | ticket | updated_at | reread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: active_items -->
| readme_status_badges | review | handoff | codex | codex_1 | none | Owner reviews or promotes README/reporting changes. | Approved tagline, badges and current asset proofs. | Owner accepts implementation and hosted result. | tickets/tasks/2026-09-06_readme_status_badges_task.md | 2026-09-06T15:38:07Z | REQUIRED |
| embed_melder_banner | review | handoff | codex | codex_1 | none | Owner reviews final README integration. | Local banner source and public fallback validated. | Owner accepts ticket closure. | tickets/tasks/2026-09-06_embed_melder_banner_task.md | 2026-09-06T14:27:09Z | REQUIRED |
| ci_validation_stage_design | review | handoff | codex | workflows_1 | none | Owner reviews and promotes the workflow change. | Three full checkpoints with safe lightweight promotions. | Owner accepts implementation and hosted rollout. | tickets/tasks/2026-09-06_ci_validation_stage_design_task.md | 2026-09-06T10:45:04Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| turn_in_codex_1_tickets | done | codex_1 | tickets/tasks/completed/2026-09-06_turn_in_codex_1_tickets_task.md | All 17 assigned tickets turned in; rejected repair explicitly deferred; evidence retained. | 2026-09-06T10:04:39Z |
| 2026-09-04_readthedocs_documentation_epic | done | codex_2 | tickets/epics/completed/2026-09-04_readthedocs_documentation_epic.md | Owner accepted; evidence retained in the completed program. | 2026-09-06T09:52:54Z |
| 2026-09-04_rtd_advanced_curriculum_story | done | codex_2 | tickets/stories/completed/2026-09-04_rtd_advanced_curriculum_story.md | Owner accepted; evidence retained in the completed program. | 2026-09-06T09:52:54Z |
| 2026-09-04_rtd_beginner_curriculum_story | done | codex_2 | tickets/stories/completed/2026-09-04_rtd_beginner_curriculum_story.md | Owner accepted; evidence retained in the completed program. | 2026-09-06T09:52:54Z |
| 2026-09-04_rtd_build_and_hosting_story | done | codex_2 | tickets/stories/completed/2026-09-04_rtd_build_and_hosting_story.md | Owner accepted; evidence retained in the completed program. | 2026-09-06T09:52:54Z |
| 2026-09-04_rtd_example_catalog_story | done | codex_2 | tickets/stories/completed/2026-09-04_rtd_example_catalog_story.md | Owner accepted; evidence retained in the completed program. | 2026-09-06T09:52:54Z |
| 2026-09-04_rtd_expert_curriculum_story | done | codex_2 | tickets/stories/completed/2026-09-04_rtd_expert_curriculum_story.md | Owner accepted; evidence retained in the completed program. | 2026-09-06T09:52:54Z |
| 2026-09-04_rtd_intermediate_curriculum_story | done | codex_2 | tickets/stories/completed/2026-09-04_rtd_intermediate_curriculum_story.md | Owner accepted; evidence retained in the completed program. | 2026-09-06T09:52:54Z |
| 2026-09-04_rtd_navigation_and_site_shell_story | done | codex_2 | tickets/stories/completed/2026-09-04_rtd_navigation_and_site_shell_story.md | Owner accepted; evidence retained in the completed program. | 2026-09-06T09:52:54Z |
| 2026-09-04_rtd_quality_and_launch_story | done | codex_2 | tickets/stories/completed/2026-09-04_rtd_quality_and_launch_story.md | Owner accepted; evidence retained in the completed program. | 2026-09-06T09:52:54Z |
| 2026-09-04_rtd_reference_and_architecture_story | done | codex_2 | tickets/stories/completed/2026-09-04_rtd_reference_and_architecture_story.md | Owner accepted; evidence retained in the completed program. | 2026-09-06T09:52:54Z |
| 2026-09-04_readthedocs_sphinx_reference_discovery_task | done | codex_2 | tickets/tasks/completed/2026-09-04_readthedocs_sphinx_reference_discovery_task.md | Owner accepted; evidence retained in the completed program. | 2026-09-06T09:52:54Z |
<!-- END USER-DEFINED: closed_anchors -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
### Active Attention Details
- readme_status_badges: SWITCH_TRIGGER is owner acceptance or first hosted coverage failure evidence.
  RESUME_HIERARCHY: tickets/tasks/2026-09-06_readme_status_badges_task.md.
- embed_melder_banner: SWITCH_TRIGGER is owner acceptance or a requested presentation adjustment.
  RESUME_HIERARCHY: tickets/tasks/2026-09-06_embed_melder_banner_task.md.
- ci_validation_stage_design: SWITCH_TRIGGER is owner acceptance or new hosted failure evidence.
  RESUME_HIERARCHY: tickets/tasks/2026-09-06_ci_validation_stage_design_task.md.
<!-- END USER-DEFINED: notes -->
