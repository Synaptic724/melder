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
- NEW MESSAGE for melder_1 (from workflows_0, 2026-09-28T09:43:41Z)
- NEW MESSAGE for melder_2 (from workflows_0, 2026-09-28T09:43:41Z)
- NEW MESSAGE for muse_0 (from workflows_0, 2026-09-28T09:43:41Z)
- NEW MESSAGE for melder_1 (from workflows_0, 2026-09-28T08:24:12Z)
- NEW MESSAGE for melder_2 (from workflows_0, 2026-09-28T08:24:12Z)
- NEW MESSAGE for muse_0 (from workflows_0, 2026-09-28T08:24:12Z)
- NEW MESSAGE for melder_1 (from melder_0, 2026-09-26T19:15:40Z)
- NEW MESSAGE for melder_1 (from melder_0, 2026-09-26T20:47:28Z)
- NEW MESSAGE for melder_1 (from melder_0, 2026-09-26T21:36:14Z)
- NEW MESSAGE for melder_1 (from melder_2, 2026-09-26T22:07:46Z)
- NEW MESSAGE for melder_1 (from melder_0, 2026-09-26T22:18:01Z)
- NEW MESSAGE for melder_1 (from melder_2, 2026-09-26T22:41:56Z)
- NEW MESSAGE for melder_1 (from melder_0, 2026-09-27T11:40:40Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-27T11:40:40Z)
- NEW MESSAGE for melder_1 (from melder_0, 2026-09-27T13:25:25Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-27T13:25:25Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-27T20:29:26Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-27T21:49:53Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-27T21:49:53Z)
- NEW MESSAGE for melder_1 (from fable_0, 2026-09-27T22:06:50Z)
- NEW MESSAGE for melder_2 (from fable_0, 2026-09-27T22:06:50Z)
- NEW MESSAGE for muse_0 (from fable_0, 2026-09-27T22:06:50Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-27T23:08:51Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-27T23:08:51Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-28T00:15:29Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-28T00:15:29Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-28T00:24:01Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-28T00:24:01Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-28T00:24:01Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-28T00:37:34Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-28T00:37:34Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-28T01:00:46Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-28T01:00:46Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-28T01:10:20Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-28T01:10:20Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-28T01:11:37Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-28T01:11:37Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-28T08:40:12Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-28T08:40:12Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-29T21:28:19Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-29T21:28:19Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-29T21:34:35Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-29T21:34:35Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-29T22:29:43Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-29T22:29:43Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-29T23:41:45Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-29T23:41:45Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T00:05:25Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T00:05:25Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T00:24:49Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T00:24:49Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T10:44:26Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T10:44:26Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T12:27:27Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T12:39:23Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T12:52:02Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T15:49:07Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T15:49:07Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T17:19:01Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T17:19:01Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T18:23:27Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T18:23:27Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T18:48:41Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T18:48:41Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T18:58:51Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T18:58:51Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T19:31:23Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T19:31:23Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T19:46:23Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T19:46:23Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T20:21:52Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T20:21:52Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T21:18:29Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T21:18:29Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-10-01T10:15:59Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-10-01T10:15:59Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-10-01T10:47:49Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-10-01T10:47:49Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-10-01T10:56:27Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-10-01T10:56:27Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-10-01T11:10:44Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-10-01T11:10:44Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-10-01T11:26:16Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-10-01T11:26:16Z)
<!-- END USER-DEFINED: alerts -->

## Active Items
| work_item | status | mode | owner | agent_name | blocker | next | outcome | exit_signal | ticket | updated_at | reread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: active_items -->
| gauntlet_runtime_speed | in_progress | discovery | claude | melder_2 | none | Owner decides whether an open lever (thread-affine pools, one-lock anonymous link, single-check fast door) is worth a task. | Per-scope-cycle cost map vs dishka and dependency-injector, with ranked and prototyped candidates. | Next lever validated and its task opened, or the owner redirects. | tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md | 2026-09-26T23:01:16Z | REQUIRED |
| defect_hunting_spellbook | in_progress | discovery | opencode | muse_0 | none | Slice spellbook component sections then read the surface behind each claim. | Contradiction list with evidence; meaty issues flagged apart from polish. | Sweep list triaged or owner redirects to conduit/meld or arch diffs. | tickets/tasks/2026-09-27_spellbook_sweep_task.md | 2026-09-27T15:56:49Z | REQUIRED |
| defect_hunting_fixes_1 | in_progress | implementation | opencode | muse_0 | none | Re-slice each target fresh then repair findings 1-8 in order. | Corrected blocks with verified ranges; index check clean. | Batch repaired with gates passing or owner redirects scope. | tickets/tasks/2026-09-27_sweep_fixes_batch_1_task.md | 2026-09-27T16:07:16Z | REQUIRED |
| shallow_thread_scaling_ci | review | handoff | claude | melder_1 | none | Owner: stage both sides of the rename and the new workflow, run the hosted three-OS job, and accept or redirect. | The thread-scaling benchmark runs on dev-to-preprod PRs beside the two gauntlets and must succeed for merge-ready. | Contracts run or reported Not run, bundles current, and the owner accepts or redirects. | tickets/tasks/2026-10-04_add_shallow_thread_scaling_to_preprod_benchmarks_task.md | 2026-10-04T12:52:00Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| executor_cache_world_stamp | done | fable_0 | tickets/tasks/completed/2026-10-03_require_world_stamp_for_executor_cache_full_hit_task.md | Executor full hit requires the recorded world stamp (generation 19, 0.2.8220); the stale-executor defect fixed with unit/integration/component regressions; the surplus full hit retired. Turned in by owner directive; suites and gauntlet Not run. Next: none. | 2026-10-03T21:22:15Z |
| annotation_address_matching | done | fable_0 | tickets/tasks/completed/2026-10-03_resolve_annotations_by_address_key_task.md | Phase 3 matches annotations by address key at 0.2.8218 (existing objects by class; string/object parity; generation 18). Turned in by owner directive; suites Not run. Next: the Autofac-strict tightening is not wanted. | 2026-10-03T21:22:15Z |
| static_codegen_strategies | done | fable_0 | tickets/stories/completed/2026-10-01_lazy_instance_results_story.md | S8 lazy instance_results shipped at 0.2.8217 (plan -26..-32% on dict-mode roots, generation 17); story and task turned in by owner directive; gauntlet Not run. Next: S2a (with S9/S11) on the owner's word. | 2026-10-03T21:22:15Z |
| flat_warm_body | done | fable_0 | tickets/tasks/completed/2026-10-03_certify_and_implement_site_store_constants_task.md | S9 owner-store constants landed at 0.2.8221 (plan -7..-17% on roots with unique providers; dynamic plans byte-identical; no generation bump); S11 already true. Turned in by owner directive; suites and gauntlet Not run. Next: none. | 2026-10-04T00:13:33Z |
| flat_warm_body_story | done | fable_0 | tickets/stories/completed/2026-10-03_flat_warm_body_constants_story.md | The S9/S11 story behind the task; S2a parked. Turned in by owner directive. Next: none. | 2026-10-04T00:13:33Z |
| static_codegen_and_door_strategies | done | fable_0 | tickets/epics/completed/2026-10-01_static_codegen_and_door_strategies_epic.md | S1, S8 and S9 shipped (0.2.8216/0.2.8217/0.2.8221); S4 dropped, S2a parked; the door lane (D1-D5) not reached, its story parked in the backlog. Closed by owner directive; gauntlet ranking Not run. Next: the door lane under a new epic on the owner's word. | 2026-10-04T00:13:33Z |
| reproduce_annotation_category_collision | done | fable_1 | tickets/tasks/completed/2026-10-03_reproduce_annotation_category_collision_task.md | Melder-only reproduction on 0.2.8221 (2 failed / 2 passed), the matcher read, the 441-frame survey, three options and the owner's DECISION (kind rule + concrete-class refusal). Closed by owner directive. Next: none. | 2026-10-04T12:05:00Z |
| annotation_kind_matching | done | fable_1 | tickets/tasks/completed/2026-10-04_repair_annotation_kind_matching_task.md | Landed at 0.2.8222 (notched from 0.2.8221): spellframe kind recorded on the binding, concrete-class frames refused (Breaking), kind-aware Phase 3, crystal frame kind (record 4.1.0), generation 20; 18 files swept, regressions added; docs/graph/assets current. Closed by owner directive; the four tiers after the final regressions Not run (owner-owed). Next: the owner's tier run and the Actions acceptance (story row). | 2026-10-04T12:05:00Z |
| annotation_type_vs_category_matching_story | done | fable_1 | tickets/stories/completed/2026-10-03_annotation_type_vs_category_matching_story.md | Kind-matching repair landed at 0.2.8222; owner's Windows tiers green except the fixed-name cache temp race (backlog task). Turned in by owner directive; the Actions acceptance on a delivered build was not reported (owner). Next: none. | 2026-10-04T12:20:00Z |
| annotation_category_provider_collision | done | fable_1 | tickets/epics/completed/2026-10-03_annotation_category_provider_collision_epic.md | A type annotation never reads a same-named category as its provider set (0.2.8222); story and tasks completed. Closed by owner directive; consumer acceptance not reported (owner). Next: none. | 2026-10-04T12:20:00Z |
| rebind_after_first_meld_story | done | fable_1 | tickets/stories/completed/2026-10-03_rebind_after_first_meld_repair_story.md | Repair at 0.2.8219 with both tasks completed; turned in by owner directive, work package C not reported (owner). Next: none. | 2026-10-04T12:20:00Z |
| rebind_after_first_meld_epic | done | fable_1 | tickets/epics/completed/2026-10-03_rebind_after_first_meld_epic.md | Verdict retirement on unregister/register (0.2.8219); closed by owner directive, work package C not reported (owner). Next: none. | 2026-10-04T12:20:00Z |
<!-- END USER-DEFINED: closed_anchors -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
### Active Attention Details

- gauntlet_runtime_speed: SWITCH_TRIGGER is the owner's pick among the open levers, or the owner's
  answer on the SpellSpace scope RISK; P1, P4, the tail, build locks and nested slot guard are turned in. The lever-1 lifecycle is closed as measured (21:15Z). RESUME_HIERARCHY: tickets/stories/2026-09-26_gauntlet_runtime_speed_story.md ->
  tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md.
- shallow_thread_scaling_ci: SWITCH_TRIGGER is the owner's acceptance of the dev-to-preprod thread-scaling job
  (the hosted three-OS run is the owner's) or an owner redirect. RESUME_HIERARCHY:
  tickets/tasks/2026-10-04_add_shallow_thread_scaling_to_preprod_benchmarks_task.md.
### Notch notice (fable_1, 2026-10-04)
- fable_1 landed 0.2.8222 (annotation matching by kind; caching_system.py generation 20 `annotation_kind_matching`).
  Notch above it if you land after. Previous notches by this agent: 0.2.8219.
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
### Versioning and releases (owner, 2026-09-27)
- Superseded the 2026-09-26 "0.01 per change" note: the rule is now 0.0001 per honest change to `src/`
  (not per ticket), written as four decimal digits in the third segment (`0.2.82` -> `0.2.8201`), releases at
  `xx00`. The full
  rule set, the running release note and the rebuild-last order live in
  `special_instructions/agent_contribution_guide.md`, which onboarding sweeps in.
<!-- END USER-DEFINED: notes -->
