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
| correctness_defects | in_progress | handoff | claude | melder_1 | none | S2 landed at 0.2.8273 and is turned in; the stuck consumer is its own epic (row dependency_watchers_epic); S5, S11 and the recorded-world finding wait for the owner. | Defects where Melder's structure is wrong or stuck, a story each with a reproducer; the rest recorded as checked. | Every planned area swept and its defects filed as stories, or the owner redirects. | tickets/epics/2026-10-17_correctness_defects_epic.md | 2026-10-25T12:26:46Z | REQUIRED |
| dependency_watchers_epic | ready | handoff | claude | melder_0 | none | The key split moved to row spellframe_hides_class_epic (the owner's option B); S1's other misses (H1/H2, D1, G4, E1, P1a) wait for his word, one at a time. | Why a waiting consumer misses its provider, mapped for every watcher and announcer; then the fixes on the owner's word. | S1's matrix and the fix options are on the epic for the owner, or he redirects. | tickets/stories/2026-10-25_map_dependency_watchers_and_announcers_story.md | 2026-11-07T10:03:26Z | REQUIRED |
| spellframe_hides_class_epic | ready | implementation | claude | melder_0 | none | T2 done as 0.2.8278 (uncommitted; commit on the owner's word); next T3 part (b): pin both duplicate-address shapes on every path and fix the stale example probe; then T3(a). | Class lookups agree with the class meld door - a spellframe or a binding name hides a class (Autofac) - plus the owner's Phase 4 check. | The rule and the check landed and accepted, or the owner redirects. | tickets/tasks/2026-11-07_spellframe_ambiguity_validation_check_task.md | 2026-11-07T15:06:23Z | REQUIRED |
| license_metadata_to_apache | in_progress | implementation | claude | melder_0 | none | Bring NOTICE, pyproject, __license__.py and its test, both READMEs to Apache-2.0; release-note line, notch 0.2.8279; graph descriptor; rebuild last. | Every license statement agrees with the owner's Apache-2.0 LICENSE. | No AGPL statement outside history; checks OK, or the owner redirects. | tickets/tasks/2026-11-07_license_metadata_to_apache_task.md | 2026-11-07T15:31:12Z | REQUIRED |
| dependabot_ci_requirements | in_progress | implementation | claude | melder_0 | none | Read .github/ci_cd/README.md, then bump the provenance pins (PyJWT, urllib3, pyasn1, dnspython, cryptography) and setuptools through each file's tooling; validate. | The 26 open Dependabot alerts' pins at or above their patched versions. | Every named pin bumped and tests/unit/github_workflows green, or the owner redirects. | tickets/tasks/2026-11-07_dependabot_ci_requirements_task.md | 2026-11-07T15:31:12Z | REQUIRED |
| index_binding_risks_epic | ready | discovery | claude | melder_1 | none | Parked on the owner's word (2026-10-25): every open label documented; investigations wait for his go, GAP-1 first. | What can break around one binding per index - GAP-1 first - investigated and decided on the owner's word. | Every label has a verdict on the epic, or the owner redirects. | tickets/epics/2026-10-25_index_binding_risks_and_gaps_epic.md | 2026-10-25T14:58:20Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Active Attention Details
<!-- BEGIN USER-DEFINED: active_attention_details -->
- WORK_ITEM: correctness_defects
  SWITCH_TRIGGER: Every planned area swept and its defects filed as stories, or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-17_correctness_defects_epic.md
- WORK_ITEM: dependency_watchers_epic
  SWITCH_TRIGGER: S1's matrix and the fix options are on the epic for the owner, or he redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-25_dependency_watchers_listen_for_names_epic.md
    - tickets/stories/2026-10-25_map_dependency_watchers_and_announcers_story.md
- WORK_ITEM: license_metadata_to_apache
  SWITCH_TRIGGER: No AGPL statement outside history; checks OK, or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/tasks/2026-11-07_license_metadata_to_apache_task.md
- WORK_ITEM: dependabot_ci_requirements
  SWITCH_TRIGGER: Every named pin bumped and tests/unit/github_workflows green, or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/tasks/2026-11-07_dependabot_ci_requirements_task.md
- WORK_ITEM: index_binding_risks_epic
  SWITCH_TRIGGER: Every label has a verdict on the epic, or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-25_index_binding_risks_and_gaps_epic.md
- WORK_ITEM: spellframe_hides_class_epic
  SWITCH_TRIGGER: The rule and the check landed and accepted, or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-11-07_spellframe_hides_the_concrete_class_epic.md
    - tickets/tasks/2026-11-07_spellframe_ambiguity_validation_check_task.md
<!-- END USER-DEFINED: active_attention_details -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| many_child_ownership_epic | done | melder_1 | tickets/epics/completed/2026-10-20_reassess_many_child_disposal_ownership_epic.md | Closed on the owner's word 2026-11-07 (by melder_0): the holder-ownership removal landed at 0.2.8267. | 2026-11-07T07:54:24Z |
| pypi_provenance_epic | done | melder_2 | tickets/epics/completed/2026-10-24_pypi_provenance_attestations_epic.md | Closed on the owner's word 2026-11-07 (by melder_0; melder_2 finished it): Trusted Publishing with PEP 740 provenance for TestPyPI and PyPI; the owner-owed steps stay his. | 2026-11-07T07:54:24Z |
| board_cleanup_20261107 | done | melder_0 | tickets/tasks/completed/2026-11-07_strip_old_board_state_task.md | Boards stripped to live state on the owner's word (55 KB -> 26 KB); two epics closed done on his picks; finished tickets' artifact rows dropped, files kept. | 2026-11-07T07:54:59Z |
| readme_stars_badge_gh191 | done | melder_0 | tickets/tasks/completed/2026-11-07_readme_stars_badge_gh191_task.md | README stars badge in the social style linking to stargazers (GitHub #191); one line, no notch; running-note line added. | 2026-11-07T08:03:29Z |
| spellframe_epic_t1_inventory | done | melder_0 | tickets/tasks/completed/2026-11-07_inventory_class_resolution_of_framed_spells_task.md | T1 of the spellframe epic: Phase 3's change list, 106 tests in 20 files, the owner's E1-E3 on Autofac's model; read-only, no notch. | 2026-11-07T11:57:30Z |
| spellframe_epic_t2_class_lookup | done | melder_0 | tickets/tasks/completed/2026-11-07_class_annotation_selects_only_bare_spells_task.md | T2: a class lookup reaches only a bare spell (Autofac); notched 0.2.8278, release note Breaking; 106 tests + C4 moved to the new rule; cache gen 26; uncommitted. | 2026-11-07T15:06:23Z |
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
