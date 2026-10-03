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
| flat_warm_body | in_progress | implementation | claude | fable_0 | none | Green on the working copy (red on the tree); land on the tree: apply, notch 0.2.8221, release note, docs, graph, patch docs archived, assets and bundles last, post-landing shards. | S9 (site/store constants) and S11 (live key objects) certified on the five shapes; if they win, emitted with tests, docs and a notch; S2a parked. | Harness verdict recorded (ship or DECISION_REQUEST), then landed and in review. | tickets/tasks/2026-10-03_certify_and_implement_site_store_constants_task.md | 2026-10-03T22:08:45Z | REQUIRED |
| gauntlet_runtime_speed | in_progress | discovery | claude | melder_2 | none | Owner decides whether an open lever (thread-affine pools, one-lock anonymous link, single-check fast door) is worth a task. | Per-scope-cycle cost map vs dishka and dependency-injector, with ranked and prototyped candidates. | Next lever validated and its task opened, or the owner redirects. | tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md | 2026-09-26T23:01:16Z | REQUIRED |
| defect_hunting_spellbook | in_progress | discovery | opencode | muse_0 | none | Slice spellbook component sections then read the surface behind each claim. | Contradiction list with evidence; meaty issues flagged apart from polish. | Sweep list triaged or owner redirects to conduit/meld or arch diffs. | tickets/tasks/2026-09-27_spellbook_sweep_task.md | 2026-09-27T15:56:49Z | REQUIRED |
| defect_hunting_fixes_1 | in_progress | implementation | opencode | muse_0 | none | Re-slice each target fresh then repair findings 1-8 in order. | Corrected blocks with verified ranges; index check clean. | Batch repaired with gates passing or owner redirects scope. | tickets/tasks/2026-09-27_sweep_fixes_batch_1_task.md | 2026-09-27T16:07:16Z | REQUIRED |
| rebind_after_first_meld_acceptance | review | handoff | user | fable_1 | owner-owed: work package C | Owner installs the 0.2.8219 build in priv_commandops and reruns the unchanged five-case selection (test_native_rebind_probe.py + the Actions replacement regression); on 5 passes the epic and story close. | Consumer acceptance of the rebind-after-first-meld repair on the delivered build. | Owner reports 5 passes (epic closes) or a failure (a new task opens). | tickets/epics/2026-10-03_rebind_after_first_meld_epic.md | 2026-10-03T21:08:00Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| departed_agent_roster_cleanup | done | tester_0 | tickets/tasks/completed/2026-08-02_departed_agent_roster_cleanup_task.md | helper_f/mediator_0 retired, 14 tickets UNASSIGNED, board pruned; closed by owner directive with its three DECISION_REQUESTs unruled (bind-guard benchmark status, boot-melds epic, six unrecorded suite runs). Next: none. | 2026-10-03T19:01:36Z |
| stale_source_docstrings | done | UNASSIGNED (ex helper_f) | tickets/tasks/completed/2026-08-02_stale_source_docstrings_task.md | Three stale names corrected and the manifest regenerated; closed by owner directive. Next: the three Conduit 'which admits' docstrings (conduit.py:5321/5404/5482) are still false - a src change for a future ticket. | 2026-10-03T19:01:36Z |
| graph_authored_edge_drift | done | aether_0 | tickets/tasks/completed/2026-08-03_graph_authored_edge_drift_task.md | Two dead authored edges fixed at the descriptor level, graph reassembled, walker blind spot recorded; closed by owner directive. Next: 21 SEMANTICS_STALE nodes remain an unclaimed re-authoring lane. | 2026-10-03T19:01:36Z |
| understand_nexus_crystallizer_spellbook | done | updater_0 (departed) | tickets/tasks/completed/2026-09-19_understand_nexus_crystallizer_spellbook_task.md | Source-grounded orientation and the discoverable-registration proposal that became its own (completed) epic; two component-map caveats recorded. Closed by owner directive. Next: none. | 2026-10-03T19:01:36Z |
| codegen_strategy_certification_harness | done | fable_0 | tickets/stories/completed/2026-09-28_codegen_strategy_certification_harness_story.md | Harness + table delivered 2026-09-30 (S1, S8, S2a certified; S5/S6/S2b conditional; S4 not); drove the static/PGO epic split. Story and build task turned in by owner directive. Next: the static epic's S8 lane (fable_0). | 2026-10-03T19:01:36Z |
| real_world_gauntlet_ci | done | command_0 | tickets/tasks/completed/2026-10-03_real_world_gauntlet_ci_task.md | Gauntlet in CI on dev-to-preprod only, GIL-off child, arbitrary thread counts and iteration list, 279+71 checks green, bundles OK; accepted by owner directive. Next: the owner's hosted three-OS matrix. | 2026-10-03T19:01:36Z |
| build_codegen_strategy_certification_harness | done | fable_0 | tickets/tasks/completed/2026-09-30_build_codegen_strategy_certification_harness_task.md | The harness build task behind the certification story; artifacts retained. Turned in by owner directive. Next: none. | 2026-10-03T19:01:36Z |
| rebind_after_first_meld | done | fable_1 | tickets/tasks/completed/2026-10-03_repair_rebind_after_first_meld_task.md | Repair landed at 0.2.8219 (verdict retirement on unregister/register), 37 regressions, docs/graph/assets current; reproduce task (tickets/tasks/completed/2026-10-03_reproduce_rebind_after_first_meld_task.md) closed in the same pass. Turned in by owner directive. Next: work package C (owner). | 2026-10-03T21:08:00Z |
| turn_in_review_tickets | done | fable_1 | tickets/tasks/completed/2026-10-03_turn_in_review_tickets_task.md | 13 review tickets closed and both boards synced on the owner's rule; open items carried in their summaries. Turned in by owner directive. Next: none. | 2026-10-03T21:08:00Z |
| executor_cache_world_stamp | done | fable_0 | tickets/tasks/completed/2026-10-03_require_world_stamp_for_executor_cache_full_hit_task.md | Executor full hit requires the recorded world stamp (generation 19, 0.2.8220); the stale-executor defect fixed with unit/integration/component regressions; the surplus full hit retired. Turned in by owner directive; suites and gauntlet Not run. Next: none. | 2026-10-03T21:22:15Z |
| annotation_address_matching | done | fable_0 | tickets/tasks/completed/2026-10-03_resolve_annotations_by_address_key_task.md | Phase 3 matches annotations by address key at 0.2.8218 (existing objects by class; string/object parity; generation 18). Turned in by owner directive; suites Not run. Next: the Autofac-strict tightening is not wanted. | 2026-10-03T21:22:15Z |
| static_codegen_strategies | done | fable_0 | tickets/stories/completed/2026-10-01_lazy_instance_results_story.md | S8 lazy instance_results shipped at 0.2.8217 (plan -26..-32% on dict-mode roots, generation 17); story and task turned in by owner directive; gauntlet Not run. Next: S2a (with S9/S11) on the owner's word. | 2026-10-03T21:22:15Z |
<!-- END USER-DEFINED: closed_anchors -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
### Active Attention Details

- flat_warm_body: SWITCH_TRIGGER is the harness verdict (S9/S11 within noise -> DECISION_REQUEST), or the
  landing and turn-in; then the door lane story opens (audit first). The PGO epic stays queued with no row
  (owner: ignore it). RESUME_HIERARCHY: tickets/epics/2026-10-01_static_codegen_and_door_strategies_epic.md ->
  tickets/stories/2026-10-03_flat_warm_body_constants_story.md ->
  tickets/tasks/2026-10-03_certify_and_implement_site_store_constants_task.md.
- gauntlet_runtime_speed: SWITCH_TRIGGER is the owner's pick among the open levers, or the owner's
  answer on the SpellSpace scope RISK; P1, P4, the tail, build locks and nested slot guard are turned in. The lever-1 lifecycle is closed as measured (21:15Z). RESUME_HIERARCHY: tickets/stories/2026-09-26_gauntlet_runtime_speed_story.md ->
  tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md.
- rebind_after_first_meld_acceptance: SWITCH_TRIGGER is the owner's report of work package C (5 passes on
  the delivered 0.2.8219 build in priv_commandops -> epic and story close; a failure -> a new repair task).
  Both engineering tasks are closed; nothing is owed by an agent until that report. RESUME_HIERARCHY:
  tickets/epics/2026-10-03_rebind_after_first_meld_epic.md ->
  tickets/stories/2026-10-03_rebind_after_first_meld_repair_story.md
  (evidence: tickets/tasks/completed/2026-10-03_repair_rebind_after_first_meld_task.md).
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
