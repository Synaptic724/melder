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
- NEW MESSAGE for fable_0 (from melder_0, 2026-09-26T19:15:40Z)
- NEW MESSAGE for fable_0 (from melder_0, 2026-09-26T20:00:17Z)
- NEW MESSAGE for fable_0 (from melder_0, 2026-09-26T20:47:28Z)
- NEW MESSAGE for melder_1 (from melder_0, 2026-09-26T20:47:28Z)
- NEW MESSAGE for fable_0 (from melder_0, 2026-09-26T21:19:43Z)
- NEW MESSAGE for melder_1 (from melder_0, 2026-09-26T21:36:14Z)
- NEW MESSAGE for melder_1 (from melder_2, 2026-09-26T22:07:46Z)
- NEW MESSAGE for fable_0 (from melder_2, 2026-09-26T22:07:47Z)
- NEW MESSAGE for fable_0 (from melder_0, 2026-09-26T22:18:01Z)
- NEW MESSAGE for melder_1 (from melder_0, 2026-09-26T22:18:01Z)
- NEW MESSAGE for melder_0 (from melder_2, 2026-09-26T22:41:56Z)
- NEW MESSAGE for melder_1 (from melder_2, 2026-09-26T22:41:56Z)
- NEW MESSAGE for fable_0 (from melder_2, 2026-09-26T22:41:56Z)
<!-- END USER-DEFINED: alerts -->

## Active Items
| work_item | status | mode | owner | agent_name | blocker | next | outcome | exit_signal | ticket | updated_at | reread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: active_items -->
| gauntlet_runtime_speed | in_progress | discovery | claude | melder_2 | none | Owner's Windows gauntlet run on 0.2.74 (nested slot guard in), then turn-ins of the review tasks. | Per-scope-cycle cost map vs dishka and dependency-injector, with ranked and prototyped candidates. | Next lever validated and its task opened, or the owner redirects. | tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md | 2026-09-26T22:41:50Z | REQUIRED |
| gauntlet_p1_positional_args | review | validation | claude | melder_2 | none | Owner closes P1: R2 retired its emitter (0.2.70) and its rule lives on in the lowering (P5). | Generated plans pass dependency values positionally (-11% to -21% per scope cycle on the VM). | Owner accepts or retires P1; closure sync. | tickets/tasks/2026-09-26_emit_positional_constructor_args_task.md | 2026-09-26T20:29:32Z | REQUIRED |
| gauntlet_p4_spellspace_warm_lane | review | validation | claude | melder_2 | none | Owner accepts P4: Windows runs on 0.2.68-0.2.70 show the SpellSpace window at parity on request and worker_b. | SpellSpace.meld serves warm id melds from the door's fast-door entry (about -17% per cached space meld, -2% to -3% per gauntlet cycle on the VM). | Owner accepts; closure sync. | tickets/tasks/2026-09-26_spellspace_meld_warm_id_lane_task.md | 2026-09-26T20:29:32Z | REQUIRED |
| gauntlet_tail_spikes | review | handoff | claude | melder_2 | none | Owner accepts the attribution (turn-0 first use, no GC); optional 200k run with GAUNTLET_TREND_WINDOWS=20. | The rare Melder-only multi-ms cycle spikes attributed with evidence and ranked fix candidates. | Owner accepts; closure sync. | tickets/tasks/2026-09-26_attribute_gauntlet_tail_spikes_task.md | 2026-09-26T20:35:11Z | REQUIRED |
| gauntlet_spellspace_build_locks | review | handoff | claude | melder_2 | none | Owner turns in the discovery task; the owner-approved implementation continues in its own task. | Evidence on whether spellspace-scoped first builds can skip their build locks, with a measured prototype. | Owner turn-in; closure sync. | tickets/tasks/2026-09-26_spellspace_build_locks_task.md | 2026-09-26T21:38:55Z | HELPFUL |
| gauntlet_nested_slot_guard | review | handoff | claude | melder_2 | none | Owner runs the Windows gauntlet on 0.2.74 and accepts; at turn-in the patch lane moves to patches/completed. | Door-called first builds take their build lock once; about -0.3 us per worker cycle, nothing observable changes. | Owner acceptance after the Windows run; closure sync. | tickets/tasks/2026-09-26_remove_nested_slot_guard_take_task.md | 2026-09-26T22:41:50Z | REQUIRED |
| melder_seo_starter_review | review | handoff | codex | seo_0 | none | Owner selects the drafted homepage change or adjusts positioning. | ZIP review, ordered improvement proposal and applicable two-file homepage patch. | Owner selects implementation or accepts the review. | tickets/tasks/2026-09-26_review_melder_seo_starter_task.md | 2026-09-26T22:44:02Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| updater_1_checkout | done | updater_1 | tickets/tasks/completed/2026-09-26_check_out_updater_1_task.md | Owner-directed checkout; departed roster, no active assignments; prior work retained. | 2026-09-26T22:20:35Z |
| tests_system_docs_refresh | done | melder_0 | tickets/tasks/completed/2026-09-26_refresh_tests_system_docs_task.md | tests_architecture (91) and tests_components (85) describe the current suite; 0.2.74 notch and release bullet; owner turn-in. | 2026-09-26T22:18:52Z |
| updater_0_checkout | done | updater_0 | tickets/tasks/completed/2026-09-26_checkout_updater_0_task.md | Departed; remaining assignment released and obsolete coordination retired. | 2026-09-26T22:17:12Z |
| phase5_pool_snapshot | done | melder_0 | tickets/tasks/completed/2026-09-26_snapshot_phase5_live_spell_pool_task.md | Compiler passes read a copy of the spell pool; concurrent binds cannot abort revalidation (0.2.72); patch lane archived; owner turn-in. | 2026-09-26T21:59:01Z |
| registration_guard_test_order | done | melder_0 | tickets/tasks/completed/2026-09-26_fix_registration_guard_test_order_task.md | View fixtures re-boot Aether and the guard test sets up its own world; order-independent; owner turn-in. | 2026-09-26T21:59:01Z |
| override_site_plan_lowering | done | melder_0 | tickets/tasks/completed/2026-09-26_build_site_plan_lowering_task.md | S2-S6: key-set plans, normal melds on the lowering, unresolved inputs before construction, retirements; 0.2.71 docs, graph, assets, LLM bundles; owner turn-in. | 2026-09-26T21:09:12Z |
| override_site_plan_story | done | melder_0 | tickets/stories/completed/2026-09-26_implement_override_site_plan_lowering_story.md | S1-S6 done; patch lane archived to system_docs/patches/completed/override_site_plan_2026_09_26/; owner turn-in. | 2026-09-26T21:09:12Z |
| override_execution_epic | done | melder_0 | tickets/epics/completed/2026-09-24_override_execution_performance_epic.md | Every story and task done: override melds build only what the call does not supply; owner turn-in. | 2026-09-26T21:09:12Z |
| override_many_collection_fix | done | melder_0 | tickets/tasks/completed/2026-09-26_fix_collection_member_many_sharing_task.md | Collection members build their own many dependencies (cache 13); owner turn-in. | 2026-09-26T21:09:12Z |
| override_design_melder | done | melder_0 | tickets/tasks/completed/2026-09-26_design_override_and_caller_input_execution_task.md | Design v2 approved and shipped as the site-plan story; artifacts retained. | 2026-09-26T21:09:12Z |
| caller_input_strictness | done | melder_0 | tickets/tasks/completed/2026-09-26_trace_caller_input_conjure_strictness_regression_task.md | Cause timeline recorded; fixed by unresolved-input sockets (0.2.54) and S4 of the site-plan story. | 2026-09-26T21:09:12Z |
| ir_structural_snapshot_promotion | done | fable_0 | tickets/tasks/completed/2026-09-26_promote_structural_snapshot_docs_task.md | Structural snapshot promoted into src_components/src_architecture, indexes regenerated, patch folder retired; owner accepted. | 2026-09-26T18:43:15Z |
<!-- END USER-DEFINED: closed_anchors -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
### Active Attention Details
- gauntlet_runtime_speed: SWITCH_TRIGGER is the owner's Windows run on 0.2.74 (nested slot guard landed 22:41Z), or
  the owner's answer on the SpellSpace scope RISK. The lever-1 lifecycle is closed as measured (21:15Z). RESUME_HIERARCHY: tickets/stories/2026-09-26_gauntlet_runtime_speed_story.md ->
  tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md.
- gauntlet_p1_positional_args: SWITCH_TRIGGER is the owner's decision on P1 alongside melder_0's S2b-3 (P1's emitter
  is off the normal path since S2b-2) and the owner's Windows gauntlet run.
  RESUME_HIERARCHY: tickets/stories/2026-09-26_gauntlet_runtime_speed_story.md ->
  tickets/tasks/2026-09-26_emit_positional_constructor_args_task.md.
- gauntlet_tail_spikes: SWITCH_TRIGGER is the owner's acceptance of the attribution (turn-0 first use, no GC);
  conjure-time hydration withdrawn by owner direction (optimize code, not the benchmark). RESUME_HIERARCHY:
  tickets/stories/2026-09-26_gauntlet_runtime_speed_story.md ->
  tickets/tasks/2026-09-26_attribute_gauntlet_tail_spikes_task.md.
- gauntlet_spellspace_build_locks: SWITCH_TRIGGER is the owner's turn-in (implementation approved ~21:37Z, own task).
  RESUME_HIERARCHY: tickets/stories/2026-09-26_gauntlet_runtime_speed_story.md ->
  tickets/tasks/2026-09-26_spellspace_build_locks_task.md.
- gauntlet_nested_slot_guard: SWITCH_TRIGGER is the owner's acceptance after a Windows gauntlet run on 0.2.74
  (the notch pipeline finished 22:41Z).
  RESUME_HIERARCHY: tickets/stories/2026-09-26_gauntlet_runtime_speed_story.md ->
  tickets/tasks/2026-09-26_remove_nested_slot_guard_take_task.md.
- gauntlet_p4_spellspace_warm_lane: SWITCH_TRIGGER is the byte-identical device apply, then the owner's Windows
  gauntlet run and acceptance.
  RESUME_HIERARCHY: tickets/stories/2026-09-26_gauntlet_runtime_speed_story.md ->
  tickets/tasks/2026-09-26_spellspace_meld_warm_id_lane_task.md.
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
### Versioning (owner, 2026-09-26)
- Owner: "each change we make is a notch of 0.01 so its fine". Each change gets its own patch notch of
  `src/melder/__version__.py` (0.2.58 -> 0.2.59); lanes notching one after another is expected, not a conflict.
  The release-note header follows `__version__`.
- melder_seo_starter_review: SWITCH_TRIGGER is owner direction on homepage wording or review acceptance.
  RESUME_HIERARCHY: tickets/tasks/2026-09-26_review_melder_seo_starter_task.md.
<!-- END USER-DEFINED: notes -->
