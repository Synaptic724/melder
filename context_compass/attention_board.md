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
| gauntlet_runtime_speed | in_progress | discovery | claude | melder_2 | none | Owner decides whether an open lever (thread-affine pools, one-lock anonymous link, single-check fast door) is worth a task. | Per-scope-cycle cost map vs dishka and dependency-injector, with ranked and prototyped candidates. | Next lever validated and its task opened, or the owner redirects. | tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md | 2026-09-26T23:01:16Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| sphinx_homepage_heading | done | seo_0 | tickets/tasks/completed/2026-09-27_replace_homepage_slogan_task.md | Descriptive Python runtime heading; prior fragment preserved; 301-page build/site/SEO checks pass. Next: none. | 2026-09-27T01:29:33Z |
| melder_seo_starter_review | done | seo_0 | tickets/tasks/completed/2026-09-26_review_melder_seo_starter_task.md | Inspected the starter and live Sphinx site; corrected the plan and retained the existing homepage. Next: none. | 2026-09-27T00:30:31Z |
| sphinx_build_blockers | done | seo_0 | tickets/tasks/completed/2026-09-26_repair_docs_build_blockers_task.md | Fixed UnresolvedInputError selection and shortened 20 archive paths with byte-preserving Windows checkout verification. Next: none. | 2026-09-27T00:30:31Z |
| sphinx_metadata_links | done | seo_0 | tickets/tasks/completed/2026-09-26_apply_sphinx_metadata_and_links_task.md | Added nine descriptions, a short title suffix and the local configuration link while preserving existing content. Next: none. | 2026-09-27T00:30:31Z |
| sphinx_seo_checks | done | seo_0 | tickets/tasks/completed/2026-09-26_integrate_sphinx_seo_checks_task.md | Integrated SEO checks and preserved the lesson anchor; 60 docs tests, 29 workflow tests and real HTML checks pass. Next: none. | 2026-09-27T00:30:31Z |
| sphinx_build_repair_story | done | seo_0 | tickets/stories/completed/2026-09-26_repair_documentation_builds_story.md | Accepted the verified API-selection and Windows archive-path repairs. Next: none. | 2026-09-27T00:30:31Z |
| sphinx_discoverability_story | done | seo_0 | tickets/stories/completed/2026-09-26_refine_sphinx_discoverability_story.md | Accepted metadata, local linking and publication checks; RTD-managed crawler files retained. Next: none. | 2026-09-27T00:30:31Z |
| sphinx_publication_quality | done | seo_0 | tickets/epics/completed/2026-09-26_sphinx_publication_quality_epic.md | Delivered build repairs and bounded SEO improvements at 0.2.77; owner accepted turn-in before the final asset rebuild. Next: none. | 2026-09-27T00:30:31Z |
| gauntlet_nested_slot_guard | done | melder_2 | tickets/tasks/completed/2026-09-26_remove_nested_slot_guard_take_task.md | Door-held first builds take their build lock once (0.2.73); VM -3.3%/-3.6% per worker cycle; docs, graph, assets and LLM bundles at 0.2.74; owner run 0.919x dishka; owner turn-in. | 2026-09-26T23:01:16Z |
| gauntlet_spellspace_build_locks | done | melder_2 | tickets/tasks/completed/2026-09-26_spellspace_build_locks_task.md | Spellspace confinement does not cover foreign-thread melds; the nested take was the safe win (own task); a lock-free path needs a thread rule; owner turn-in. | 2026-09-26T23:01:16Z |
| gauntlet_p4_spellspace_warm_lane | done | melder_2 | tickets/tasks/completed/2026-09-26_spellspace_meld_warm_id_lane_task.md | SpellSpace.meld warm id lane (0.2.68): about -17% per cached space meld; SpellSpace window at parity in the owner's runs; owner turn-in. | 2026-09-26T23:01:16Z |
| gauntlet_p1_positional_args | done | melder_2 | tickets/tasks/completed/2026-09-26_emit_positional_constructor_args_task.md | Positional constructor args applied (16:16Z); superseded on the normal path by the site-plan lowering (P5 keeps the rule); owner turn-in. | 2026-09-26T23:01:16Z |
<!-- END USER-DEFINED: closed_anchors -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
### Active Attention Details

- gauntlet_runtime_speed: SWITCH_TRIGGER is the owner's pick among the open levers, or the owner's
  answer on the SpellSpace scope RISK; P1, P4, the tail, build locks and nested slot guard are turned in. The lever-1 lifecycle is closed as measured (21:15Z). RESUME_HIERARCHY: tickets/stories/2026-09-26_gauntlet_runtime_speed_story.md ->
  tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md.
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
<!-- END USER-DEFINED: notes -->
