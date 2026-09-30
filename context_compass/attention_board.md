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
- NEW MESSAGE for fable_0 (from workflows_0, 2026-09-28T09:43:41Z)
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
- NEW MESSAGE for fable_0 (from melder_0, 2026-09-29T21:28:19Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-29T21:28:19Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-29T21:28:19Z)
- NEW MESSAGE for fable_0 (from melder_0, 2026-09-29T21:34:35Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-29T21:34:35Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-29T21:34:35Z)
- NEW MESSAGE for fable_0 (from melder_0, 2026-09-29T22:29:43Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-29T22:29:43Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-29T22:29:43Z)
- NEW MESSAGE for fable_0 (from melder_0, 2026-09-29T23:41:45Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-29T23:41:45Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-29T23:41:45Z)
- NEW MESSAGE for fable_0 (from melder_0, 2026-09-30T00:05:25Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T00:05:25Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T00:05:25Z)
- NEW MESSAGE for fable_0 (from melder_0, 2026-09-30T00:24:49Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T00:24:49Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T00:24:49Z)
- NEW MESSAGE for fable_0 (from melder_0, 2026-09-30T10:44:26Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T10:44:26Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T10:44:26Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T12:27:27Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T12:39:23Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-30T12:52:02Z)
<!-- END USER-DEFINED: alerts -->

## Active Items
| work_item | status | mode | owner | agent_name | blocker | next | outcome | exit_signal | ticket | updated_at | reread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: active_items -->
| gauntlet_runtime_speed | in_progress | discovery | claude | melder_2 | none | Owner decides whether an open lever (thread-affine pools, one-lock anonymous link, single-check fast door) is worth a task. | Per-scope-cycle cost map vs dishka and dependency-injector, with ranked and prototyped candidates. | Next lever validated and its task opened, or the owner redirects. | tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md | 2026-09-26T23:01:16Z | REQUIRED |
| defect_hunting_spellbook | in_progress | discovery | opencode | muse_0 | none | Slice spellbook component sections then read the surface behind each claim. | Contradiction list with evidence; meaty issues flagged apart from polish. | Sweep list triaged or owner redirects to conduit/meld or arch diffs. | tickets/tasks/2026-09-27_spellbook_sweep_task.md | 2026-09-27T15:56:49Z | REQUIRED |
| defect_hunting_fixes_1 | in_progress | implementation | opencode | muse_0 | none | Re-slice each target fresh then repair findings 1-8 in order. | Corrected blocks with verified ranges; index check clean. | Batch repaired with gates passing or owner redirects scope. | tickets/tasks/2026-09-27_sweep_fixes_batch_1_task.md | 2026-09-27T16:07:16Z | REQUIRED |
| melderops_root_config | review | handoff | claude | melder_0 | none | Owner accepts the per-root answer; the fixes chosen (all: F1-F6, M1-M4) are in review in both repositories. | Per-root answer: what MelderOps asks and what Melder does when the root is already set. | Answer delivered with evidence; owner accepts. | tickets/tasks/2026-09-29_investigate_melderops_root_configuration_collisions_task.md | 2026-09-30T10:44:26Z | REQUIRED |
| melder_root_guards | review | handoff | claude | melder_0 | none | Owner reviews M1-M4 and the 0.2.8212 wheel, then accepts or redirects. | Honest, guarded root configuration for hosts (M1-M4), notched and wheel-built. | M1-M4 green under tests, docs/assets current, owner accepts. | tickets/tasks/2026-09-29_guard_melder_roots_for_host_collisions_task.md | 2026-09-30T10:44:26Z | REQUIRED |
| gauntlet_order_dependence | review | handoff | claude | melder_0 | none | Owner reviews the one-process-per-library gauntlet (optionally on Windows with REAL_WORLD_GAUNTLET_ROUNDS=3), then accepts or redirects. | Order-independent shared gauntlet: every library measured in a fresh process; old layout reproducible. | Owner accepts; turn-in. | tickets/tasks/2026-09-30_investigate_gauntlet_order_dependence_task.md | 2026-09-30T12:52:02Z | REQUIRED |
| melder_gauntlet_gains | review | handoff | claude | melder_0 | none | Owner confirms dropping option A (Windows: 8-11% slower per scope cycle) and closes the lane. | Ranked levers for the remaining loop gap; option A measured (a loss on Windows). | Owner closes; turn-in. | tickets/tasks/2026-09-30_map_remaining_melder_gauntlet_gains_task.md | 2026-09-30T15:15:54Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| host_read_surface | done | melder_0 | tickets/tasks/completed/2026-09-29_implement_frame_lookups_and_read_accessors_task.md | Aether.find_frame/get_frame/list_frame_names and four read accessors, 27 tests, notched 0.2.8208, release note; epic and story closed by owner directive; system docs parked in a backlog task; LLM bundles stale (rebuild waived). Next: none. | 2026-09-29T22:29:43Z |
| melderops_wheel_0_2_8208 | done | melder_0 | tickets/tasks/completed/2026-09-29_build_0_2_8208_wheel_into_melderops_env_task.md | Wheel 0.2.8208 built (verify_wheel, smoke OK) and installed in priv_commandops/.venv314 (RECORD-verified; old files in .venv314/_to_delete/); MelderOps floor melder>=0.2.8208; VM MelderOps env passes 265 melder_setup tests. Next: none. | 2026-09-29T22:29:43Z |
| transaction_session_cleanup_race | done | workflows_0 | tickets/tasks/completed/2026-09-28_investigate_transaction_session_cleanup_race_task.md | Unsupported simultaneous-destruction assertions retired; owned teardown/idempotence/cleaned guards covered; 189 tests pass, runtime unchanged; asset/LLM checks OK. Next: none. | 2026-09-28T11:34:15Z |
| document_publication_race | done | workflows_0 | tickets/tasks/completed/2026-09-28_fix_system_document_lazy_publication_race_task.md | Ready marker after key map; 8 red regressions fixed, 128 tests and 200 contention runs pass; notched 0.2.8207; asset/LLM checks OK. Next: none. | 2026-09-28T09:50:15Z |
| owner_assets_rebuild | done | workflows_0 | tickets/tasks/completed/2026-09-28_rebuild_assets_after_owner_changes_task.md | Package assets rebuilt; all asset and LLM bundle checks OK. Next: none. | 2026-09-28T09:01:49Z |
| melder_wheel | done | workflows_0 | tickets/tasks/completed/2026-09-28_build_melder_wheel_task.md | Built wheel and installed Melder 0.2.8206 in priv_commandops/.venv314; archive and isolated import verified. Next: none. | 2026-09-28T08:54:31Z |
| probe_portability_followups | done | melder_0 | tickets/tasks/completed/2026-09-28_finish_probe_and_doc_portability_followups_task.md | ConduitMeld docstrings name each lifetime's store; src_architecture/src_components name no tooling path (both checks 0); ConduitMeld node accepted; notched 0.2.8205; waived rebuild covered by 0.2.8206 (asset/LLM checks OK). Next: none. | 2026-09-28T08:39:36Z |
| qualified_spell_name_collisions | done | workflows_0 | tickets/tasks/completed/2026-09-28_investigate_qualified_spell_name_collisions_task.md | Canonical-address validation; 35 red checks to 147 passing, 2 pre-existing XPASS; docs/release promoted, notched 0.2.8206; asset and LLM checks OK. Next: none. | 2026-09-28T08:31:05Z |
| spellspace_probe_many | done | melder_0 | tickets/tasks/completed/2026-09-28_count_space_held_many_in_spellspace_live_creation_probe_task.md | SpellSpace door's live-creation probe reads `many` from the space's own store ("spellspace_many", space id); 3 tests red then green; off the meld path; notched 0.2.8204, docs/graph/assets/bundles current. Next: none. | 2026-09-28T01:00:27Z |
| scope_exit_dispose | done | melder_0 | tickets/tasks/completed/2026-09-27_make_with_dispose_scopes_and_finish_pool_returns_task.md | `with conduit:` disposes (Breaking), enter_lesser_conduit, finish-then-raise exits, children-first pool return, idempotent soft cleanup, SpellSpace lease flag; no hot-path cost; notched 0.2.8203, docs/graph/assets/bundles current. Next: none. | 2026-09-28T00:20:59Z |
| scope_exit_cleanup | done | melder_0 | tickets/tasks/completed/2026-09-27_investigate_scope_exit_and_pool_return_cleanup_task.md | Scope-exit and pool-return path map with probes (P1-P10); every gap fixed in scope_exit_dispose (0.2.8203). Next: none. | 2026-09-28T00:20:59Z |
| pgo_strategy_exploration | done | fable_0 | tickets/stories/completed/2026-09-27_pgo_strategy_exploration_story.md | PGO proper ~6 ns per creation on Melder shapes; the door fold landed (0.2.8201); executor-hold dropped; opt-in specializer -14% wide8 / +20% chain8 measured. Next: the probe-selected styles story under the epic. | 2026-09-27T22:34:08Z |
<!-- END USER-DEFINED: closed_anchors -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
### Active Attention Details

- gauntlet_runtime_speed: SWITCH_TRIGGER is the owner's pick among the open levers, or the owner's
  answer on the SpellSpace scope RISK; P1, P4, the tail, build locks and nested slot guard are turned in. The lever-1 lifecycle is closed as measured (21:15Z). RESUME_HIERARCHY: tickets/stories/2026-09-26_gauntlet_runtime_speed_story.md ->
  tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md.
- melder_root_guards: SWITCH_TRIGGER is the owner's acceptance - M1-M4 landed, 0.2.8212 rebuilt and its wheel
  installed in MelderOps' environments (priv_commandops tickets/epics/2026-09-29_melder_host_configuration_collisions_epic.md).
  RESUME_HIERARCHY: tickets/tasks/2026-09-29_guard_melder_roots_for_host_collisions_task.md.
- melderops_root_config: SWITCH_TRIGGER is the owner's acceptance and fix selection (answer delivered 23:13Z);
  read-only in both repositories.
  RESUME_HIERARCHY: tickets/tasks/2026-09-29_investigate_melderops_root_configuration_collisions_task.md.
- gauntlet_order_dependence: SWITCH_TRIGGER is the owner's acceptance of option 1 as built (landed 12:51Z,
  checks OK); melder_0 stays the only writer of the gauntlet runner, test_real_world_gauntlet.py,
  test_real_world_gauntlet_isolation.py and benchmarks.md until turn-in (M0-123/M0-124).
  RESUME_HIERARCHY: tickets/tasks/2026-09-30_investigate_gauntlet_order_dependence_task.md.
- melder_gauntlet_gains: SWITCH_TRIGGER is the owner's word on closing; option A measured a loss on
  Windows (8-11% slower per scope cycle), drop recommended. src/ untouched.
  RESUME_HIERARCHY: tickets/tasks/2026-09-30_map_remaining_melder_gauntlet_gains_task.md.
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
