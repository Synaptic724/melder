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
- NEW MESSAGE for melder_1 (from melder_0, 2026-09-26T19:15:40Z)
- NEW MESSAGE for melder_1 (from melder_0, 2026-09-26T20:47:28Z)
- NEW MESSAGE for melder_1 (from melder_0, 2026-09-26T21:36:14Z)
- NEW MESSAGE for melder_1 (from melder_2, 2026-09-26T22:07:46Z)
- NEW MESSAGE for melder_1 (from melder_0, 2026-09-26T22:18:01Z)
- NEW MESSAGE for melder_1 (from melder_2, 2026-09-26T22:41:56Z)
- NEW MESSAGE for melder_1 (from melder_0, 2026-09-27T11:40:40Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-27T11:40:40Z)
- NEW MESSAGE for melder_1 (from melder_0, 2026-09-27T13:25:25Z)
- NEW MESSAGE for fable_0 (from melder_0, 2026-09-27T13:25:25Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-27T13:25:25Z)
<!-- END USER-DEFINED: alerts -->

## Active Items
| work_item | status | mode | owner | agent_name | blocker | next | outcome | exit_signal | ticket | updated_at | reread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: active_items -->
| gauntlet_runtime_speed | in_progress | discovery | claude | melder_2 | none | Owner decides whether an open lever (thread-affine pools, one-lock anonymous link, single-check fast door) is worth a task. | Per-scope-cycle cost map vs dishka and dependency-injector, with ranked and prototyped candidates. | Next lever validated and its task opened, or the owner redirects. | tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md | 2026-09-26T23:01:16Z | REQUIRED |
| creations_disposal_failures | review | handoff | claude | melder_0 | none | Owner reviews and accepts; the SpellSpace follow-up moved to scope_exit_cleanup. | Every declared disposal method runs and every failure is reported together; tests, docs, notch. | New tests red on 0.2.79 and green after; suites green; owner accepts. | tickets/tasks/2026-09-27_aggregate_creations_disposal_method_failures_task.md | 2026-09-27T13:54:57Z | REQUIRED |
| scope_exit_cleanup | review | handoff | claude | melder_0 | none | Owner discusses `with` as dispose and enter_lesser_conduit (STRATEGY_DISCUSSION note), then approves a build. | Evidence-backed map of where scope exit and pool return dispose objects and where they break the contract, with a proposed fix. | Owner reviews the findings and approves or redirects a fix lane. | tickets/tasks/2026-09-27_investigate_scope_exit_and_pool_return_cleanup_task.md | 2026-09-27T14:20:34Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| readme_roadmap | done | seo_0 | tickets/tasks/completed/2026-09-27_embed_readme_roadmap_task.md | Roadmap after the introduction, quick/full-size/detail links; browser and docs model verified. Next: none. | 2026-09-27T14:28:08Z |
| aether_conduit_lookup_api | done | melder_0 | tickets/epics/completed/2026-09-27_aether_conduit_lookup_api_epic.md | Epic, 11 stories and the implementation task turned in at 0.2.79: *_root_* renames, NAMED/LIVE Aether lookups, ConduitCloud.list_conduits; assets and LLM bundles rebuilt; whole tree green on 3.14t. Next: none. | 2026-09-27T13:03:47Z |
| conduit_name_lookup_lessers | done | melder_0 | tickets/tasks/completed/2026-09-27_trace_get_conduit_by_name_named_lesser_lookup_task.md | Cause and repro of the root-only name lookup (MF7); the fix shipped under the epic. Next: none. | 2026-09-27T13:03:47Z |
| creations_disposal_all_methods | done | melder_0 | tickets/tasks/completed/2026-08-07_creations_disposal_all_methods_task.md | Regression file green on 3.14t (GIL 0/1) and the GIL build, agent-run; per-method error aggregation left open. Next: none. | 2026-09-27T13:03:47Z |
| structural_snapshot_story | done | fable_0 | tickets/stories/completed/2026-09-26_structural_snapshot_story.md | I-1 shipped (generation 15; a warm conjure over an unchanged book skips phases 1-4); tasks 1-6 accepted on owner-run suites; measurement pass waived at turn-in. | 2026-09-27T12:38:12Z |
| gauntlet_dishka_scope_parity | done | fable_0 | tickets/tasks/completed/2026-09-27_dishka_scope_placement_and_parity_phase_task.md | Switchable dishka mapping, 54-assertion parity phase, environment line and the audit fixes landed; sweep waived; the default app mapping stands. | 2026-09-27T12:38:12Z |
| gauntlet_fairness_review | done | fable_0 | tickets/tasks/completed/2026-09-27_persistent_gauntlet_fairness_review_task.md | Harness symmetric; per-cycle work identical by constructor counts; disclosure fixes landed via the dishka/parity task. | 2026-09-27T12:38:12Z |
| ux_aix_harness_red_remediation | done | examples_0 | tickets/epics/completed/2026-08-01_ux_aix_harness_red_remediation_epic.md | Epic and its four parked child tasks closed by owner directive (2026-09-27); four findings implemented per the corrected handoff; harness pass not recorded. | 2026-09-27T10:47:06Z |
| ux_aix_expert_experience | done | examples_0 | tickets/epics/completed/2026-07-19_ux_aix_expert_experience_epic.md | Closed by owner directive (2026-09-27); lessons 01-32 and 42 probe rows authored; no agent-run green. | 2026-09-27T10:47:06Z |
| ux_aix_advanced_experience | done | examples_0 | tickets/epics/completed/2026-07-19_ux_aix_advanced_experience_epic.md | Closed by owner directive (2026-09-27); arcs A-E authored (18 lessons, 64 probe rows); last signal 61/64. | 2026-09-27T10:47:06Z |
| sphinx_homepage_heading | done | seo_0 | tickets/tasks/completed/2026-09-27_replace_homepage_slogan_task.md | Descriptive Python runtime heading; prior fragment preserved; 301-page build/site/SEO checks pass. Next: none. | 2026-09-27T01:29:33Z |
| melder_seo_starter_review | done | seo_0 | tickets/tasks/completed/2026-09-26_review_melder_seo_starter_task.md | Inspected the starter and live Sphinx site; corrected the plan and retained the existing homepage. Next: none. | 2026-09-27T00:30:31Z |
<!-- END USER-DEFINED: closed_anchors -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
### Active Attention Details


- gauntlet_runtime_speed: SWITCH_TRIGGER is the owner's pick among the open levers, or the owner's
  answer on the SpellSpace scope RISK; P1, P4, the tail, build locks and nested slot guard are turned in. The lever-1 lifecycle is closed as measured (21:15Z). RESUME_HIERARCHY: tickets/stories/2026-09-26_gauntlet_runtime_speed_story.md ->
  tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md.
- creations_disposal_failures: SWITCH_TRIGGER is the new tests green on the fix plus owner acceptance.
  RESUME_HIERARCHY: tickets/tasks/2026-09-27_aggregate_creations_disposal_method_failures_task.md.
- scope_exit_cleanup: SWITCH_TRIGGER is the owner's decision on the findings and proposed fix.
  RESUME_HIERARCHY: tickets/tasks/2026-09-27_investigate_scope_exit_and_pool_return_cleanup_task.md.
### Device VM git hazard (melder_2, 2026-09-26)
- The connected folder refuses deletes, so any git command that refreshes the index from the device VM
  (plain `git status`, `git diff`) can leave an empty .git/index.lock that blocks the owner's commits.
  Run git there with `GIT_OPTIONAL_LOCKS=0` and read-only commands only; if a lock appears, report it.
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
### Device VM Python (melder_0, 2026-09-27)
- Bare `python3` in the device VM is the system CPython 3.10 and cannot be repointed (read-only PATH dirs, no
  sudo). Load a 3.14 venv in every device command (for melder_0: `. ~/.melder_env`); the repository floor is 3.14.
### Versioning (owner, 2026-09-26)
- Owner: "each change we make is a notch of 0.01 so its fine". Each change gets its own patch notch of
  `src/melder/__version__.py` (0.2.58 -> 0.2.59); lanes notching one after another is expected, not a conflict.
  The release-note header follows `__version__`.
<!-- END USER-DEFINED: notes -->
