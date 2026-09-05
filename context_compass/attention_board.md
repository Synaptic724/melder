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
- NEW MESSAGE for codex_2 (from codex_1, 2026-09-05T13:03:07Z)
- NEW MESSAGE for workflows_1 (from codex_1, 2026-09-05T11:49:24Z)
<!-- END USER-DEFINED: alerts -->

## Active Items
| work_item | status | mode | owner | agent_name | blocker | next | outcome | exit_signal | ticket | updated_at | reread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: active_items -->
| release_candidate_testpypi | review | handoff | codex | workflows_1 | First hosted/OIDC run awaits owner rollout. | Owner commits reviewed workflows with current assets and promotes to release_candidate. | Slim TestPyPI workflow and pypitest environment locally verified. | Hosted candidate succeeds and owner accepts the result. | tickets/tasks/2026-09-05_release_candidate_testpypi_workflow_task.md | 2026-09-05T11:34:57Z | REQUIRED |
| readthedocs_documentation | in_progress | validation | codex | codex_2 | Hosted project access pending. | Finish catalog/search/offline audit and source qualification. | Complete local evidence with explicit hosted limitations. | S9 local checks and maintenance handoff are recorded. | tickets/tasks/2026-09-04_rtd_quality_audit_task.md | 2026-09-05T13:02:41Z | REQUIRED |
| ordered_spell_disposal_contract | in_progress | validation | codex | codex_1 | none | Run final CI runtime command and recheck assets. | Ordered disposal implementation and documentation complete. | Final executed evidence and owner handoff. | tickets/tasks/2026-09-04_ordered_disposal_end_to_end_validation_task.md | 2026-09-05T13:03:07Z | REQUIRED |
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
| branch_ci_release_validation | done | workflows_1 | tickets/tasks/completed/2026-09-04_implement_branch_ci_release_validation_task.md | CI foundation accepted; cleanup complete; owner rollout and later automation recorded. | 2026-09-05T10:12:21Z |
| github_branch_promotion_analysis | done | workflows_1 | tickets/tasks/completed/2026-09-04_github_branch_promotion_analysis_task.md | Workflow analysis and branch/candidate design accepted; foundation delivered by successor. | 2026-09-05T10:12:21Z |
| root_readme_documentation_routes | done | codex_1 | tickets/tasks/completed/2026-08-29_root_readme_documentation_routes_task.md | Compact architecture, examples, purpose-route, and hosted-docs pointers accepted. | 2026-08-29T18:41:47Z |
| architecture_and_design_documentation | done | codex_1 | tickets/epics/completed/2026-08-28_architecture_and_design_documentation_epic.md | Full public documentation program accepted and closed. | 2026-08-29T16:31:01Z |
| system_document_engineering_drawings | done | codex_1 | tickets/tasks/completed/2026-08-29_system_document_engineering_drawings_task.md | Seventeen validated SVG/Mermaid engineering pairs accepted. | 2026-08-29T16:31:01Z |
| architecture_docs_foundation | done | codex_1 | tickets/stories/completed/2026-08-28_architecture_docs_foundation_story.md | Foundation story accepted and closed. | 2026-08-29T16:31:01Z |
| architecture_docs_human_mrp | done | codex_1 | tickets/stories/completed/2026-08-28_architecture_docs_human_mrp_story.md | Human-facing MRP story accepted and closed. | 2026-08-29T16:31:01Z |
| architecture_docs_advanced_ceiling | done | codex_1 | tickets/stories/completed/2026-08-28_architecture_docs_advanced_ceiling_story.md | Advanced-ceiling story accepted and closed. | 2026-08-29T16:31:01Z |
| architecture_docs_foundation_task | done | codex_1 | tickets/tasks/completed/2026-08-28_architecture_docs_foundation_task.md | Tooling/render foundation validated and closed. | 2026-08-29T16:31:01Z |
| architecture_docs_human_mrp_task | done | codex_1 | tickets/tasks/completed/2026-08-28_architecture_docs_human_mrp_task.md | Human MRP implementation validated and closed. | 2026-08-29T16:31:01Z |
| architecture_docs_advanced_ceiling_task | done | codex_1 | tickets/tasks/completed/2026-08-28_architecture_docs_advanced_ceiling_task.md | Advanced implementation validated and closed. | 2026-08-29T16:31:01Z |
| llm_support_compilation_pipeline_discovery | done | codex_1 | tickets/tasks/completed/2026-08-30_llm_support_compilation_pipeline_discovery_task.md | Three-corpus indexed build design accepted and promoted to implementation. | 2026-08-30T22:07:25Z |
<!-- END USER-DEFINED: closed_anchors -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
<!-- END USER-DEFINED: notes -->
