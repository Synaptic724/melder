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
| sync_owner_uv_environment | review | handoff | codex | workflows_1 | none | Owner resumes development and restarts editor Ruff. | Melder 0.2.40 and locked tools on existing no-GIL Python. | Owner accepts verified environment sync. | tickets/tasks/2026-09-13_sync_owner_uv_environment_task.md | 2026-09-13T20:48:32Z | REQUIRED |
| provider_artifact_ownership | review | handoff | codex | updater_0 | none | Discuss ownership experiment results before source changes. | Eight observations; seven red regressions and six controls. | Owner selects repair after discussion. | tickets/tasks/2026-09-13_repair_provider_artifact_ownership_task.md | 2026-09-13T18:37:44Z | REQUIRED |
| existing_instance_planning | review | handoff | codex | updater_0 | Original Iris cleanup assertion fails. | Review injection fix and cleanup finding. | 140 native checks and generated assets pass. | Owner reviews; full downstream acceptance remains. | tickets/tasks/2026-09-13_repair_existing_instance_planning_task.md | 2026-09-13T21:11:38Z | REQUIRED |
| commandops_local_wheel | review | handoff | codex | updater_0 | none | Owner transfers verified 0.2.40 wheel into CommandOps. | Archive and isolated install smoke passed. | Owner accepts wheel; named lesser work later. | tickets/tasks/2026-09-13_build_commandops_local_wheel_task.md | 2026-09-13T16:42:22Z | REQUIRED |
| optional_dependency_resolution | review | handoff | codex | updater_0 | none | Owner reruns broader suite; capture thread traceback if it recurs. | Three fixtures corrected; 18 tests pass; thread failure unreproduced. | Owner accepts fixes or supplies another failure. | tickets/tasks/2026-09-13_optional_dependency_default_resolution_test_task.md | 2026-09-13T16:25:07Z | REQUIRED |
| named_binding_meld_lookup | review | handoff | codex | updater_0 | none | Owner reviews named and framed binding lookup results. | 25 tests pass across three lifecycle modes. | Owner accepts observed behavior or requests changes. | tickets/tasks/2026-09-13_named_binding_meld_lookup_test_task.md | 2026-09-13T12:09:53Z | REQUIRED |
| bind_conjure_order_speedtest | review | handoff | codex | updater_0 | none | Owner reviews cache results and completed Python upgrade. | Cache behavior measured on 3.14.7; profiler stall diagnosed. | Owner accepts evidence or selects another workload. | tickets/tasks/2026-09-12_bind_conjure_order_benchmark_task.md | 2026-09-12T21:18:31Z | REQUIRED |
| reproducible_uv_environment | review | handoff | codex | workflows_1 | none | Owner reviews and commits locked setup and CI. | Reproducible dependencies with the no-GIL matrix preserved. | Owner accepts changes and checks the hosted matrix. | tickets/tasks/2026-09-08_reproducible_uv_environment_task.md | 2026-09-08T11:26:20Z | REQUIRED |
| named_conduit_scope_design | review | handoff | codex | updater_0 | none | Review the twelve-phase map and remaining contract choices. | Source-backed implementation plan and difficulty assessment. | Owner selects contracts and authorizes implementation separately. | tickets/tasks/2026-09-07_named_conduit_implementation_map_task.md | 2026-09-07T17:22:45Z | REQUIRED |
| readme_status_badges | review | handoff | codex | codex_1 | none | Owner reviews or promotes README/reporting changes. | Approved tagline, badges and current asset proofs. | Owner accepts implementation and hosted result. | tickets/tasks/2026-09-06_readme_status_badges_task.md | 2026-09-06T15:38:07Z | REQUIRED |
| embed_melder_banner | review | handoff | codex | codex_1 | none | Owner reviews final README integration. | Local banner source and public fallback validated. | Owner accepts ticket closure. | tickets/tasks/2026-09-06_embed_melder_banner_task.md | 2026-09-06T14:27:09Z | REQUIRED |
| ci_validation_stage_design | review | handoff | codex | workflows_1 | none | Owner promotes partial-rerun coverage correction. | Complete same-run coverage without repeated tests. | Owner accepts corrected reporting in a fresh run. | tickets/tasks/2026-09-06_ci_validation_stage_design_task.md | 2026-09-06T18:58:09Z | REQUIRED |
| stateful_application_recovery | ready | handoff | user | unassigned | none | Discuss one stateful recovery scenario. | Native replay coverage and partial/assisted recovery opportunities preserved. | Owner selects recovery contracts before implementation. | tickets/epics/2026-09-07_stateful_application_recovery_epic.md | 2026-09-07T19:17:55Z | REQUIRED |
| provider_artifact_and_existing_instance_repair | in_progress | discovery | codex | updater_0 | none | Review both experiments with owner before production changes. | Native reproductions preserving real acceptance inputs. | Both repairs and downstream proofs accepted. | tickets/epics/2026-09-13_provider_artifact_ownership_and_existing_instance_planning_epic.md | 2026-09-13T18:09:51Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| deferred_annotation_acquisition | done | updater_0 | tickets/tasks/completed/2026-09-13_repair_deferred_annotation_acquisition_task.md | Owner accepted; 271 checks and generated assets pass. | 2026-09-13T20:42:12Z |
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
<!-- END USER-DEFINED: closed_anchors -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
### Active Attention Details
- sync_owner_uv_environment: SWITCH_TRIGGER is owner acceptance or new environment failure evidence.
  RESUME_HIERARCHY: tickets/tasks/2026-09-13_sync_owner_uv_environment_task.md.
- provider_artifact_ownership: SWITCH_TRIGGER is native ownership regression evidence; RESUME_HIERARCHY: tickets/tasks/2026-09-13_repair_provider_artifact_ownership_task.md.
- existing_instance_planning: SWITCH_TRIGGER is both iterators and original logger proof passing; RESUME_HIERARCHY: tickets/tasks/2026-09-13_repair_existing_instance_planning_task.md.
- commandops_local_wheel: SWITCH_TRIGGER is a verified wheel delivered to the owner.
  RESUME_HIERARCHY: tickets/tasks/2026-09-13_build_commandops_local_wheel_task.md.
- optional_dependency_resolution: SWITCH_TRIGGER is owner acceptance of the verified default-precedence patch.
  RESUME_HIERARCHY: tickets/tasks/2026-09-13_optional_dependency_default_resolution_test_task.md.
- named_binding_meld_lookup: SWITCH_TRIGGER is executed lookup/identity evidence.
  RESUME_HIERARCHY: tickets/tasks/2026-09-13_named_binding_meld_lookup_test_task.md.
- bind_conjure_order_speedtest: SWITCH_TRIGGER is completed repeated timing and correctness evidence.
  RESUME_HIERARCHY: tickets/tasks/2026-09-12_bind_conjure_order_benchmark_task.md.
- reproducible_uv_environment: SWITCH_TRIGGER is owner acceptance or new hosted matrix failure evidence.
  RESUME_HIERARCHY: tickets/tasks/2026-09-08_reproducible_uv_environment_task.md.
- named_conduit_scope_design: SWITCH_TRIGGER is the completed implementation map and owner contract decisions.
  RESUME_HIERARCHY: tickets/epics/2026-09-06_named_lesser_conduit_discovery_epic.md -> tickets/tasks/2026-09-07_named_conduit_implementation_map_task.md.
- readme_status_badges: SWITCH_TRIGGER is owner acceptance or first hosted coverage failure evidence.
  RESUME_HIERARCHY: tickets/tasks/2026-09-06_readme_status_badges_task.md.
- embed_melder_banner: SWITCH_TRIGGER is owner acceptance or a requested presentation adjustment.
  RESUME_HIERARCHY: tickets/tasks/2026-09-06_embed_melder_banner_task.md.
- ci_validation_stage_design: SWITCH_TRIGGER is owner acceptance or new hosted failure evidence.
  RESUME_HIERARCHY: tickets/tasks/2026-09-06_ci_validation_stage_design_task.md.
- stateful_application_recovery: SWITCH_TRIGGER is owner selection of a concrete stateful recovery scenario.
  RESUME_HIERARCHY: tickets/epics/2026-09-07_stateful_application_recovery_epic.md -> linked source investigation and related scope/identity work.
- provider_artifact_and_existing_instance_repair: SWITCH_TRIGGER is both native repairs with downstream acceptance.
  RESUME_HIERARCHY: tickets/epics/2026-09-13_provider_artifact_ownership_and_existing_instance_planning_epic.md.
<!-- END USER-DEFINED: notes -->
