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
| static_codegen_strategies | review | handoff | claude | fable_0 | none | Owner runs the full-tree suites and the gauntlet on the tree (0.2.8216, A3) and turns S1 in; then the S8 task opens with its patch docs. | S1 (registration trim) landed at 0.2.8216: one append per disposal-bearing many creation, same disposal order and errors, docs/graph/assets current; plan -15..-34% and meld -7..-23% on the VM. | Owner turns S1 in (S8 next) or reports a red suite or gauntlet number. | tickets/tasks/2026-10-01_implement_many_registration_trim_task.md | 2026-10-02T18:01:21Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| system_doc_citation_audit | done | melder_0 | tickets/tasks/completed/2026-10-01_audit_remaining_system_document_citations_task.md | src_architecture and src_components: ten stale citations remapped, five confirmed, bind-guard count 619 at 0.2.8215, core set equals the Key Files union (13 entries added); assets rebuilt, both checks OK; no notch. Next: none. | 2026-10-01T11:25:53Z |
| host_read_surface_docs | done | melder_0 | tickets/tasks/completed/2026-09-29_promote_host_read_surface_into_system_docs_task.md | src_architecture, src_components, tests_components, scopes.md, the graph and the release note describe the 0.2.8208 frame lookups and read accessors; 13 shifted and all aether.py citations remapped; assets rebuilt in the VM mirror and copied back, LLM bundles rebuilt, both checks OK; no notch; follow-ups in tickets/tasks/backlog/2026-10-01_audit_remaining_system_document_citations_task.md. Next: none. | 2026-10-01T10:53:21Z |
| melderops_melder_unpin | done | melder_0 | tickets/tasks/completed/2026-09-30_unpin_melder_in_melderops_pyproject_task.md | MelderOps' pyproject requires melder with no version (was melder>=0.2.8212); its comment keeps the API history and says to install the melder_private dist/ wheel (PyPI's newest is 0.2.8207); command_0 told (M0-159). Next: none. | 2026-10-01T09:46:54Z |
| injected_dependency_direct_resolution | done | melder_0 | tickets/epics/completed/2026-09-30_injected_dependency_direct_resolution_epic.md | A dependency bound after conjure and first built by a consumer melds directly afterwards (option B, 0.2.8215); the unchanged MelderOps diagnostic passes on the installed wheel. Next: none. | 2026-09-30T21:18:29Z |
| injected_dependency_wheel_delivery | done | melder_0 | tickets/tasks/completed/2026-09-30_deliver_0_2_8215_wheel_and_revalidate_melderops_task.md | 0.2.8215 wheel verified and installed in .venv314 (0.2.8212 in _to_delete/) and the VM env; diagnostic 4/4 (red on 0.2.8212); MelderOps suite 6561/6573, 3 pre-existing timing failures. Next: none. | 2026-09-30T21:18:29Z |
| injected_provider_first_direct_meld | done | melder_0 | tickets/tasks/completed/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md | Option B landed and notched 0.2.8215: target-pass flags, the deferred lane's full pass; regressions red to green; docs, graph, release note, assets and bundles. Next: none. | 2026-09-30T21:18:29Z |
| injected_provider_reproduction | done | melder_0 | tickets/tasks/completed/2026-09-30_reproduce_injected_provider_direct_meld_task.md | Reproduced on bare Melder (no host, cache on or off, any scope or lifetime); cause: the consumer's target pass stamps the provider valid without its plan; the owner picked option B. Next: tickets/tasks/completed/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md. | 2026-09-30T19:07:02Z |
| per_frame_spell_worlds | done | melder_0 | tickets/tasks/completed/2026-09-30_record_and_restore_per_frame_spell_worlds_task.md | A: the Aether record carries the spell-id regime, restore stage 1 installs, reports or refuses it (0.2.8213); B: custody keyed per frame under per-frame ids, per-Book replay, RecordVersion 4.0.0 (0.2.8214); release note, docs, graph, assets and LLM bundles; patch docs archived. Next: none. | 2026-09-30T18:58:51Z |
| aether_record_spell_id_regime | done | melder_0 | tickets/tasks/completed/2026-09-30_investigate_aether_record_spell_id_regime_task.md | Two measured defects in recording per-frame worlds (regime missing from the Aether record; one frame's copy lost at record time); the owner picked A + B, landed with the per-frame task. Next: none. | 2026-09-30T18:58:51Z |
| gauntlet_order_dependence | done | melder_0 | tickets/tasks/completed/2026-09-30_investigate_gauntlet_order_dependence_task.md | The shared gauntlet measures each library in its own process (runner --lib, rotated rounds with medians; the old one-process layout kept); cause: thread start/exit residue under free-threading, 5-12% per later slot in the VM; 14 contract tests; benchmark-only; the owner's 30,000-iteration default kept. Next: none. | 2026-09-30T15:40:12Z |
| melder_root_guards | done | melder_0 | tickets/tasks/completed/2026-09-29_guard_melder_roots_for_host_collisions_task.md | M1-M4: sealed spell-id regime, active-Nexus guard (restore stage 4 deactivates first), a refused conjure leaves its frame unsettled, get_configuration_dictionary() on the four root configurations; notched 0.2.8209-0.2.8212, release note, docs, graph, assets, bundles and wheel; patch docs archived. Next: none (open follow-up: the Aether record lacks the spell-id regime). | 2026-09-30T15:40:12Z |
| melderops_root_config | done | melder_0 | tickets/tasks/completed/2026-09-29_investigate_melderops_root_configuration_collisions_task.md | Per-root collision answer with probes; the owner picked every fix (F1-F6 MelderOps, M1-M4 Melder), landed and turned in with it. Next: none. | 2026-09-30T15:40:12Z |
<!-- END USER-DEFINED: closed_anchors -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
### Active Attention Details

- gauntlet_runtime_speed: SWITCH_TRIGGER is the owner's pick among the open levers, or the owner's
  answer on the SpellSpace scope RISK; P1, P4, the tail, build locks and nested slot guard are turned in. The lever-1 lifecycle is closed as measured (21:15Z). RESUME_HIERARCHY: tickets/stories/2026-09-26_gauntlet_runtime_speed_story.md ->
  tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md.
- static_codegen_strategies: SWITCH_TRIGGER is the owner's turn-in of the landed S1 (then S8, S2a, the door
  harness), or a red owner-run suite/gauntlet on 0.2.8216. The PGO epic
  (tickets/epics/2026-09-27_adaptive_creation_contexts_epic.md) is queued behind this one with no row.
  RESUME_HIERARCHY:
  tickets/epics/2026-10-01_static_codegen_and_door_strategies_epic.md ->
  tickets/stories/2026-09-27_many_registration_trim_story.md ->
  tickets/tasks/2026-10-01_implement_many_registration_trim_task.md.
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
