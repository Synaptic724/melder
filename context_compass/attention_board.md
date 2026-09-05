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
- NEW MESSAGE for codex_1 (from codex_2, 2026-09-05T14:18:48Z)
<!-- END USER-DEFINED: alerts -->

## Active Items
| work_item | status | mode | owner | agent_name | blocker | next | outcome | exit_signal | ticket | updated_at | reread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: active_items -->
| release_candidate_testpypi | review | handoff | codex | workflows_1 | Hosted/OIDC run awaits owner rollout. | Owner commits the test-isolation repair and promotes when ready. | 263 focused tests pass from both repo root and tests/. | Owner verifies the IDE repair and hosted candidate run. | tickets/tasks/2026-09-05_release_candidate_testpypi_workflow_task.md | 2026-09-05T13:41:13Z | REQUIRED |
| readthedocs_documentation | review | handoff | codex | codex_2 | none | Owner commits and pushes the three regenerated other-corpus files. | Both branch and exact CI merge inputs match the rebuilt manifest. | New hosted CI run passes the repository-asset check. | tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md | 2026-09-05T15:54:53Z | REQUIRED |
| first_public_release_notes | review | handoff | cowork | codex_1 | none | Review and commit the PyPI-portable README links plus selective LLM other-corpus regeneration. | All README repository routes use absolute GitHub prod links and generated proofs pass. | Owner confirms the public routes and accepts the release-documentation change. | tickets/tasks/2026-08-30_craft_first_public_release_notes_task.md | 2026-09-01T00:56:59Z | REQUIRED |
| regenerate_0_2_0_release_assets | review | handoff | cowork | codex_1 | none | Review the eight-file generated diff, then commit and push through the normal branch lane. | Version 0.2.0 generated assets pass both exact CI checks. | Owner confirms acceptance for ticket closure. | tickets/tasks/2026-08-30_regenerate_0_2_0_release_assets_task.md | 2026-08-30T22:47:20Z | REQUIRED |
| llm_support_compilation_pipeline | review | handoff | cowork | codex_1 | none | Review generated LLM assets and separated workflow gates; confirm acceptance. | Deterministic three-corpus LLM assets and separated src/repo asset workflows. | Owner confirms acceptance for story/task closure and artifact promotion. | tickets/tasks/2026-08-30_implement_llm_support_compilation_pipeline_task.md | 2026-08-30T22:32:04Z | REQUIRED |
| human_meld_identity_api | review | handoff | cowork | codex_1 | none | Review the final human/name/ID/override contract and confirm acceptance. | Public Meld calls use short `override=` while internal execution semantics stay unchanged. | Owner confirms acceptance for ticket closure and patch-artifact disposition. | tickets/tasks/2026-08-30_meld_spell_reference_ergonomics_task.md | 2026-08-30T21:31:49Z | REQUIRED |
| upgrade_python_publish_workflow | review | handoff | cowork | codex_1 | none | Review and commit the token-authenticated publish workflow, then promote it to prod. | `PYPI_API_TOKEN` upload wiring validated with no credential committed. | GitHub release workflow publishes from current prod HEAD and owner confirms acceptance. | tickets/tasks/2026-08-30_upgrade_python_publish_workflow_task.md | 2026-08-31T01:01:03Z | REQUIRED |
| sanitize_publication_history | review | handoff | cowork | codex_1 | none | Review committed sanitation result; do not push. | Sanitized local history preserving source and canonical tickets. | Owner confirms acceptance for ticket closure. | tickets/tasks/2026-08-29_sanitize_publication_history_task.md | 2026-08-30T00:13:00Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| 2026-09-02_ordered_live_spell_disposal_epic | done | codex_1 | tickets/epics/completed/2026-09-02_ordered_live_spell_disposal_epic.md | Owner accepted; ordered-disposal program completed. | 2026-09-05T14:22:02Z |
| 2026-09-04_ordered_disposal_persistence_story | done | codex_1 | tickets/stories/completed/2026-09-04_ordered_disposal_persistence_story.md | Owner accepted; ordered-disposal program completed. | 2026-09-05T14:22:02Z |
| 2026-09-04_ordered_disposal_runtime_story | done | codex_1 | tickets/stories/completed/2026-09-04_ordered_disposal_runtime_story.md | Owner accepted; ordered-disposal program completed. | 2026-09-05T14:22:02Z |
| 2026-09-04_ordered_disposal_binding_story | done | codex_1 | tickets/stories/completed/2026-09-04_ordered_disposal_binding_story.md | Owner accepted; ordered-disposal program completed. | 2026-09-05T14:22:02Z |
| 2026-09-04_ordered_disposal_end_to_end_validation_task | done | codex_1 | tickets/tasks/completed/2026-09-04_ordered_disposal_end_to_end_validation_task.md | Owner accepted; ordered-disposal program completed. | 2026-09-05T14:22:02Z |
| 2026-09-04_ordered_disposal_docs_assets_task | done | codex_1 | tickets/tasks/completed/2026-09-04_ordered_disposal_docs_assets_task.md | Owner accepted; ordered-disposal program completed. | 2026-09-05T14:22:02Z |
| 2026-09-04_ordered_disposal_crystal_replay_task | done | codex_1 | tickets/tasks/completed/2026-09-04_ordered_disposal_crystal_replay_task.md | Owner accepted; ordered-disposal program completed. | 2026-09-05T14:22:02Z |
| 2026-09-04_ordered_disposal_creations_task | done | codex_1 | tickets/tasks/completed/2026-09-04_ordered_disposal_creations_task.md | Owner accepted; ordered-disposal program completed. | 2026-09-05T14:22:02Z |
| 2026-09-04_ordered_disposal_compiler_propagation_task | done | codex_1 | tickets/tasks/completed/2026-09-04_ordered_disposal_compiler_propagation_task.md | Owner accepted; ordered-disposal program completed. | 2026-09-05T14:22:02Z |
| 2026-09-04_disposal_configuration_roundtrip_task | done | codex_1 | tickets/tasks/completed/2026-09-04_disposal_configuration_roundtrip_task.md | Owner accepted; ordered-disposal program completed. | 2026-09-05T14:22:02Z |
| 2026-09-04_ordered_disposal_bind_and_spell_task | done | codex_1 | tickets/tasks/completed/2026-09-04_ordered_disposal_bind_and_spell_task.md | Owner accepted; ordered-disposal program completed. | 2026-09-05T14:22:02Z |
| 2026-09-04_disposal_priority_configuration_task | done | codex_1 | tickets/tasks/completed/2026-09-04_disposal_priority_configuration_task.md | Owner accepted; ordered-disposal program completed. | 2026-09-05T14:22:02Z |
<!-- END USER-DEFINED: closed_anchors -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
<!-- END USER-DEFINED: notes -->
