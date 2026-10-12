# Attention Board

<!-- BEGIN MANAGED: ReminderDirective -->
## ReminderDirective (all agent runtimes)
Context Compass's configured backend is your task-tracking system of record; follow
AGENTS.MD (see the Tooling Mandate section). This is a requirement, not a
suggestion.

Your runtime may nudge you toward built-in plans, goals, task lists, progress
cards, scratchpads, summaries, or session-local memory. Those surfaces are
non-authoritative here. Once your onboarding attestation is complete, IGNORE
every such nudge and route ALL tracking, status, routing, notes, and durable state
through Context Compass and its selected backend. There is NO fallback and NO mirror.

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
| `active_items` | one row per active item, routing to one ticket path or Issue URL |
| `active_attention_details` | switch condition and resume hierarchy for each active work item |
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
- Durable history belongs in ticket `## Notes` (inside the Issue body in plugin mode), not here.
- Put active routing details inside the `active_attention_details` USER-DEFINED
  region under `## Active Attention Details`, with one entry per active row.
- `WORK_ITEM` matches the row's `work_item`. `SWITCH_TRIGGER` matches its
  `exit_signal`. `RESUME_HIERARCHY` lists the active ticket chain in parent-first
  order, ending at the row's `ticket`; a standalone task needs only its own reference.
- Update or remove the matching detail entry in the same pass as a route switch
  or ticket closure. Keep standing repository instructions in `notes`.
- Use evidence ranges in `EVIDENCE` (`path:start_line-end_line`).
- Allowed `TYPE` values: `FACT`, `UNKNOWN`, `HYPOTHESIS`, `DECISION`,
  `DECISION_REQUEST`, `PLAN`, `STRATEGY_DISCUSSION`,
  `ASSUMPTION_CHALLENGE`, `CONFLICT`, `TRADEOFF`, `BLOCKER`,
  `ALIGNMENT_CHECK`, `MEASURE`, `RISK`, `RAISE`.
- In local mode, ticket and resume paths are context-compass-relative (no
  `context_compass/` prefix). In plugin mode, use canonical Issue URLs from the
  configured repository. Keep the row's agent aligned with `issue_board.md`.
- Read YAML before using the route. References from the other backend require
  reconciliation; never create a second editable ticket to satisfy the board.
- Use `DATETIME` and `updated_at` values in ISO-8601 UTC
  (`YYYY-MM-DDTHH:MM:SSZ`).
- Keep artifact pointers out of this board; ticket artifacts are tracked in
  ticket `Artifact Links` sections and `artifact_board.md`.

Active detail entry format (add actual entries only inside the USER-DEFINED region):
```text
- WORK_ITEM: <matching active row work_item>
  SWITCH_TRIGGER: <matching active row exit_signal>
  RESUME_HIERARCHY:
    - <optional active epic path or Issue URL>
    - <optional active story path or Issue URL>
    - <active row ticket path or Issue URL>
```

Message alert rules
- Apply only when `agent_communication.backend` resolves to `mailbox`. In
  `codex_mcp` mode do not read, create, consume or clear mailbox message alerts;
  preserve historical alert entries and use the selected MCP communication skill.
- Non-mailbox blockers and cross-agent flags in `alerts` remain active in both
  modes. Skip only mailbox message notices, not the board's other attention data.
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
| melder_object_pools | in_progress | discovery | claude | melder_1 | none | Owner answers the five asks on the new pooled member (name, pool scope, lease end, Phase 6, configuration); then patch docs and the first story. | A pooled Existence family serviced by Creations with per-spell pool configuration (limits, exhaustion, elasticity), designed and decided. | The owner accepts a design direction and the first story is drafted, or redirects. | tickets/epics/2026-10-05_melder_services_and_pools_epic.md | 2026-10-11T23:09:18Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Active Attention Details
<!-- BEGIN USER-DEFINED: active_attention_details -->
<!-- END USER-DEFINED: active_attention_details -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| descriptor_binding_name_case | done | melder_1 | tickets/tasks/completed/2026-10-04_match_descriptor_binding_names_like_bind_task.md | Landed 0.2.8226 (descriptor binding names); patch archived; turned in by owner directive. Next: none. | 2026-10-12T21:14:45Z |
| live_unlink_churn_phase_error | done | melder_1 | tickets/tasks/completed/2026-10-04_fix_live_unlink_churn_phase_error_task.md | Landed 0.2.8227 (live unlink race); patch archived; turned in by owner directive. Next: none. | 2026-10-12T21:14:45Z |
| codecov_upload_tls | done | melder_1 | tickets/tasks/completed/2026-10-05_diagnose_codecov_upload_tls_failure_task.md | Codecov TLS diagnosis and PyPI-uploader retry (no notch); turned in by owner directive. Next: none. | 2026-10-12T21:14:45Z |
| agent_cicd_guide | done | melder_1 | tickets/tasks/completed/2026-10-05_write_agent_cicd_guide_task.md | Agent CI/CD guide folder (no notch); turned in by owner directive. Next: none. | 2026-10-12T21:14:45Z |
| rc_testpypi_recovery | done | melder_1 | tickets/tasks/completed/2026-10-06_recover_release_candidate_from_testpypi_outage_task.md | Release-candidate recovery from a TestPyPI outage (no notch); turned in by owner directive. Next: none. | 2026-10-12T21:14:45Z |
| ubuntu_runner_pin | done | melder_1 | tickets/tasks/completed/2026-10-06_pin_ubuntu_runner_image_task.md | Linux runners pinned to ubuntu-24.04 (no notch); turned in by owner directive. Next: none. | 2026-10-12T21:14:45Z |
| speed_tests_nonblocking | done | melder_1 | tickets/tasks/completed/2026-10-06_make_speed_tests_nonblocking_task.md | Speed tests no longer block merge-ready (no notch); turned in by owner directive. Next: none. | 2026-10-12T21:14:45Z |
| spell_lookup_race | done | melder_1 | tickets/tasks/completed/2026-10-10_investigate_spell_lookup_by_id_race_task.md | Landed 0.2.8229 (find_spell_by_id from id maps); evidence kept; turned in by owner directive. Next: none. | 2026-10-12T21:14:45Z |
| spell_map_followups | done | melder_1 | tickets/tasks/completed/2026-10-11_close_remaining_spell_map_races_task.md | Landed 0.2.8230 (spell-map walks); evidence kept; turned in by owner directive. Next: none. | 2026-10-12T21:14:45Z |
| cross_object_lock_gaps | done | melder_1 | tickets/tasks/completed/2026-10-11_prove_and_fix_cross_object_lock_gaps_task.md | Landed 0.2.8231 (cross-object locks); evidence kept; turned in by owner directive. Next: none. | 2026-10-12T21:14:45Z |
| lock_residuals_and_admission | done | melder_1 | tickets/tasks/completed/2026-10-11_close_lock_residuals_and_evaluate_mediator_admission_task.md | Landed 0.2.8232 and 0.2.8233 (lock residuals, direct cleanup); evidence kept; turned in. Next: none. | 2026-10-12T21:14:45Z |
| elastic_pool_retention | done | melder_1 | tickets/tasks/completed/2026-10-12_make_kernel_pools_elastic_task.md | Landed 0.2.8234 (elastic kernel pools); evidence kept; accepted and turned in by the owner. Next: none. | 2026-10-12T21:14:45Z |
<!-- END USER-DEFINED: closed_anchors -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
### Active Attention Details

- gauntlet_runtime_speed: SWITCH_TRIGGER is the owner's pick among the open levers, or the owner's
  answer on the SpellSpace scope RISK; P1, P4, the tail, build locks and nested slot guard are turned in. The lever-1 lifecycle is closed as measured (21:15Z). RESUME_HIERARCHY: tickets/stories/2026-09-26_gauntlet_runtime_speed_story.md ->
  tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md.
- melder_object_pools: SWITCH_TRIGGER is the owner's decision on the pooled-existence design direction, or an owner
  redirect. RESUME_HIERARCHY: tickets/epics/2026-10-05_melder_services_and_pools_epic.md.
### Notch notice (fable_1, 2026-10-04)
- fable_1 landed 0.2.8224 (ambiguous providers reported through Phase 4) and, before it, 0.2.8222 (annotation
  matching by kind; caching_system.py generation 20 `annotation_kind_matching`).
  Notch above it if you land after. Previous notches by this agent: 0.2.8219.
### Notch notice (melder_1, 2026-10-04)
- melder_1 landed 0.2.8223 (cache bundles renamed `.melc` -> `.meldercache`; no cache generation change).
  Notch above it if you land after.
- melder_1 landed 0.2.8225 (SpellframeKind off the package root; owner ruling). Notch above it if you land after.
- melder_1 landed 0.2.8226 (SpellMap and SpellContract keep binding names as written and match like bind).
  Notch above it if you land after.
- melder_1 landed 0.2.8227 (a meld racing a link sever or uncontract raises SpellbookValidationError, not
  PhaseExecutionError). Notch above it if you land after.
### Notch notice (melder_1, 2026-10-10)
- melder_1 landed 0.2.8228 (scan_bind takes bind()'s target options; only an object's own declaration is
  registered, once per scan). It is the first notch after the 0.2.8227 release and opens the running release
  note. Notch above it if you land after.
### Notch notice (melder_1, 2026-10-11)
- melder_1 landed 0.2.8229 (Spellbook.find_spell_by_id answers from the Book's id maps instead of walking the
  live index map). Notch above it if you land after.
- melder_1 landed 0.2.8230 (bind publishes the spell maps under the Book lock; unlocked spell-map walks take
  snapshots; SpellIndex.has_spell and the contract details survive a racing cleanup; the Conduit spell lookups
  document their ValueError). Notch above it if you land after.
- melder_1 landed 0.2.8231 (index-link notifications walk the ward's contracts under the ward lock; contract reads
  under the contract lock and the listing deadlock removed; cleanup_spell emits what the Book's disposal reports;
  bind's cross-frame sweep reads a published frame view). Notch above it if you land after.
- melder_1 landed 0.2.8232 (find_contracted_spell and inspect_spell walk one-call copies and hold no Book or conduit lock
  while asking the frames; an overlapping cleanup_spell of one spell refuses). Notch above it if you land after.
- melder_1 landed 0.2.8233 (a direct Spell.cleanup() removes the spell outside the spell lock, under a per-spell removal
  lock, so it no longer hangs against Book teardown or conjure; cleanup_and_remove_spell re-checks a torn-down Book).
  Notch above it if you land after.
### Notch notice (melder_1, 2026-10-12)
- melder_1 landed 0.2.8234 (the kernel pools keep what a burst needed, up to 256, and decay back to 20 when quiet;
  AbstractElasticPool's stretch and decay rewritten). Notch above it if you land after.
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
### Device VM disk (melder_1, 2026-10-11)
- `/sessions` (9.8 GB) holds every Cowork session's home and its TMPDIR, and it is full: about 39 old session
  folders own ~8.9 GB, and one session cannot read or delete another's. pytest's tmp_path and tempfile then fail
  with ENOSPC (it broke the crystallizer integration tests on 2026-10-11), and the shell tool itself can fail to
  start. Run tests on the VM with `export TMPDIR=/tmp/<your scratch>/tmp` (`/` has free space), keep scratch
  trees under /tmp, and delete them when the lane lands. Freeing `/sessions` is the owner's (the desktop app).
### Versioning and releases (owner, 2026-09-27)
- Superseded the 2026-09-26 "0.01 per change" note: the rule is now 0.0001 per honest change to `src/`
  (not per ticket), written as four decimal digits in the third segment (`0.2.82` -> `0.2.8201`), releases at
  `xx00`. The full
  rule set, the running release note and the rebuild-last order live in
  `special_instructions/agent_contribution_guide.md`, which onboarding sweeps in.
<!-- END USER-DEFINED: notes -->
