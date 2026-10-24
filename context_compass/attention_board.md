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
<!-- END USER-DEFINED: alerts -->

## Active Items
| work_item | status | mode | owner | agent_name | blocker | next | outcome | exit_signal | ticket | updated_at | reread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: active_items -->
| correctness_defects | in_progress | handoff | claude | melder_1 | none | S1, S8 and S3 are turned in and the pass is rebuilt for 0.2.8263; S2 and S5 follow on the owner's word; S11 waits for the owner. | Defects where Melder's structure is wrong or stuck, a story each with a reproducer; the rest recorded as checked. | Every planned area swept and its defects filed as stories, or the owner redirects. | tickets/epics/2026-10-17_correctness_defects_epic.md | 2026-10-19T14:25:39Z | REQUIRED |
| src_architecture_to_spec | in_progress | discovery | claude | melder_3 | none | On melder_1's turn-in NOTICE: E0 baseline, rerun the dry run (script ready, clean), apply, re-index, gates, rebuild if last. | src_architecture to its spec, about 1,000 lines lighter, component detail in src_components, both rebuilt. | Story 1 turned in with its gates passed and the rebuild checked, or the owner redirects. | tickets/stories/2026-10-24_src_architecture_trim_to_spec_story.md | 2026-10-24T21:46:32Z | REQUIRED |
| many_child_ownership_epic | in_progress | handoff | claude | melder_1 | none | Ask the owner whether to close the epic on his removal decision. | The owner's removal decision recorded and carried out at 0.2.8267; the epic closed on his word. | The owner closes the epic or redirects. | tickets/epics/2026-10-20_reassess_many_child_disposal_ownership_epic.md | 2026-10-24T22:06:33Z | HELPFUL |
<!-- END USER-DEFINED: active_items -->

## Active Attention Details
<!-- BEGIN USER-DEFINED: active_attention_details -->
- WORK_ITEM: correctness_defects
  SWITCH_TRIGGER: Every planned area swept and its defects filed as stories, or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-17_correctness_defects_epic.md
- WORK_ITEM: src_architecture_to_spec
  SWITCH_TRIGGER: Story 1 turned in with its gates passed and the rebuild checked, or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-24_src_architecture_to_spec_epic.md
    - tickets/stories/2026-10-24_src_architecture_trim_to_spec_story.md
- WORK_ITEM: many_child_ownership_epic
  SWITCH_TRIGGER: The owner closes the epic or redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-20_reassess_many_child_disposal_ownership_epic.md
<!-- END USER-DEFINED: active_attention_details -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| public_readme_review | done | expert_1 | tickets/tasks/completed/2026-10-20_review_public_readme_clarity_task.md | Closed unfinished on the owner's word in the 2026-10-24 cleanup. | 2026-10-24T18:28:20Z |
| gauntlet_runtime_speed | done | melder_2 | tickets/tasks/completed/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md | Closed unfinished on the owner's word in the 2026-10-24 cleanup. | 2026-10-24T18:28:20Z |
| defect_hunting_spellbook | done | muse_0 | tickets/tasks/completed/2026-09-27_spellbook_sweep_task.md | Closed unfinished on the owner's word in the 2026-10-24 cleanup. | 2026-10-24T18:28:20Z |
| defect_hunting_fixes_1 | done | muse_0 | tickets/tasks/completed/2026-09-27_sweep_fixes_batch_1_task.md | Closed unfinished on the owner's word in the 2026-10-24 cleanup. | 2026-10-24T18:28:20Z |
| board_cleanup | done | melder_1 | tickets/tasks/completed/2026-10-24_strip_old_board_and_artifact_state_task.md | Boards stripped to live state; 26 old tickets closed, old artifacts and patch docs deleted (owner). | 2026-10-24T18:35:08Z |
| ci_python_315 | done | melder_2 | tickets/tasks/completed/2026-10-24_ci_python_315_and_release_test_rerun_task.md | 3.14.9/3.15.0/3.15.1 cells and no publication test rerun, in the owner's checkout; commit and bundle rebuild follow the concurrent landings. | 2026-10-24T20:35:02Z |
| cache_write_failure | done | melder_0 | tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md | Notched 0.2.8266: a cache save the OS refuses no longer fails a meld; three follow-ups in backlog; rebuild after closure. | 2026-10-24T21:32:03Z |
| cache_temp_file | done | melder_2 | tickets/tasks/completed/2026-10-04_per_process_conjure_cache_temp_file_task.md | Superseded by 0.2.8266's per-writer temp file; closed on the owner's word (ci_lane_loose_ends). | 2026-10-24T21:57:09Z |
| shared_gauntlet_config_order | done | melder_2 | tickets/tasks/completed/2026-09-22_shared_gauntlet_configuration_order_followup_task.md | Obsolete since f1cd22a22; the lane-parity guard passes with the GIL off and on; closed on the owner's word. | 2026-10-24T21:57:09Z |
| ci_lane_loose_ends | done | melder_2 | tickets/tasks/completed/2026-10-24_ci_lane_loose_ends_task.md | Melder says it depends on pip; pip pinned in the speed manifest, docs lock and both probes (pip check); two backlog tickets closed; rebuild at melder_1's landing. | 2026-10-24T21:59:15Z |
| many_child_ownership_removal | done | melder_1 | tickets/stories/completed/2026-10-24_remove_many_child_holder_ownership_story.md | Notched 0.2.8267: a `many` belongs to the scope that built it, the holder record removed; rebuild after closure; the epic waits for the owner. | 2026-10-24T22:06:33Z |
<!-- END USER-DEFINED: closed_anchors -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
### Standing notes (compacted 2026-10-24 on the owner's word; the older notes are in git history)
- Device VM git: the connected folder refuses deletes, so a git command that refreshes the index (plain `git status`,
  `git diff`) can leave an empty .git/index.lock that blocks the owner's commits. Use `GIT_OPTIONAL_LOCKS=0` and
  read-only git there; report a lock if one appears.
- Device VM Python: bare `python3` is CPython 3.10; load a 3.14 interpreter in every device command.
- Device VM disk: `/sessions` is full; run tests with `TMPDIR` under /tmp and delete scratch trees when a lane lands.
- Mailbox IDs: melder_0 sends `M0-<seq>`, melder_1 `M1-<seq>`; the ID leads CLAIM and a reply cites it.
<!-- END USER-DEFINED: notes -->
