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
| many_child_ownership_epic | in_progress | handoff | claude | melder_1 | none | Ask the owner whether to close the epic on his removal decision. | The owner's removal decision recorded and carried out at 0.2.8267; the epic closed on his word. | The owner closes the epic or redirects. | tickets/epics/2026-10-20_reassess_many_child_disposal_ownership_epic.md | 2026-10-24T22:06:33Z | HELPFUL |
| pypi_provenance_epic | blocked | handoff | claude | melder_2 | S3's promotion with its RC run, the owner's PyPI publisher (D2) and the first attested final release, and S6's keep-or-drop | At the first final release that carries S3, read Release / provenance first; then the owner retires PYPI_API_TOKEN (S4). | Every Melder file on TestPyPI and PyPI carries verified PEP 740 provenance, both upload tokens retired, S6 decided. | The owner shares the hosted runs and accepts the epic, or redirects. | tickets/epics/2026-10-24_pypi_provenance_attestations_epic.md | 2026-10-25T08:27:53Z | REQUIRED |
| dependency_watchers_epic | ready | discovery | claude | melder_1 | none | S1 - the watcher and announcer matrix (the probe-and-purge lane landed at 0.2.8269). | Why a waiting consumer misses its provider, mapped for every watcher and announcer; then the fixes on the owner's word. | S1's matrix and the fix options are on the epic for the owner, or he redirects. | tickets/epics/2026-10-25_dependency_watchers_listen_for_names_epic.md | 2026-10-25T08:22:32Z | REQUIRED |
| index_binding_risks_epic | ready | discovery | claude | melder_1 | none | Parked on the owner's word (2026-10-25): every open label documented; investigations wait for his go, GAP-1 first. | What can break around one binding per index - GAP-1 first - investigated and decided on the owner's word. | Every label has a verdict on the epic, or the owner redirects. | tickets/epics/2026-10-25_index_binding_risks_and_gaps_epic.md | 2026-10-25T14:58:20Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Active Attention Details
<!-- BEGIN USER-DEFINED: active_attention_details -->
- WORK_ITEM: correctness_defects
  SWITCH_TRIGGER: Every planned area swept and its defects filed as stories, or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-17_correctness_defects_epic.md
- WORK_ITEM: many_child_ownership_epic
  SWITCH_TRIGGER: The owner closes the epic or redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-20_reassess_many_child_disposal_ownership_epic.md
- WORK_ITEM: pypi_provenance_epic
  SWITCH_TRIGGER: The owner shares the hosted runs and accepts the epic, or redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-24_pypi_provenance_attestations_epic.md
- WORK_ITEM: dependency_watchers_epic
  SWITCH_TRIGGER: S1's matrix and the fix options are on the epic for the owner, or he redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-25_dependency_watchers_listen_for_names_epic.md
- WORK_ITEM: index_binding_risks_epic
  SWITCH_TRIGGER: Every label has a verdict on the epic, or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-25_index_binding_risks_and_gaps_epic.md
<!-- END USER-DEFINED: active_attention_details -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| creations_many_disposal_docstrings | done | melder_3 | tickets/tasks/completed/2026-10-25_creations_many_disposal_docstrings_task.md | Notched 0.2.8268: the creations.py `many` disposal docstrings state the store since 0.2.8257; src_components, both code maps and the graph follow; two rebind outcomes to the owner (S3); rebuild after closure. | 2026-10-25T02:36:15Z |
| pypi_provenance_release | done | melder_2 | tickets/stories/completed/2026-10-25_pypi_trusted_publishing_and_provenance_story.md | PyPI by Trusted Publishing with attestations; Release / provenance checks every released file after the upload; no upload token in any workflow; the users' check documented; no notch; hosted Not run; rebuild after closure. | 2026-10-25T03:20:31Z |
| probe_purge_every_version | done | melder_1 | tickets/stories/completed/2026-10-25_probe_and_purge_reach_every_version_story.md | Notched 0.2.8269: purge and the live-creation probes reach any version by its spell_id, active or parked, owned or borrowed; purge refuses a unique version with no owner store; rebuild after closure. | 2026-10-25T08:22:32Z |
| codegen_open_file_d10 | done | melder_0 | tickets/tasks/completed/2026-10-10_deny_file_access_under_safe_codegen_task.md | Notched 0.2.8270: `open` refused under safe, hybrid and precision and the no-projection default; `pathlib` a permissive-only root (the owner's B); every profile's file posture pinned; rebuild after closure. | 2026-10-25T08:44:04Z |
| rebind_live_store_tests | done | melder_3 | tickets/tasks/completed/2026-10-25_rebind_while_old_objects_are_alive_tests_task.md | Component tests prove the two rebind defects as strict xfails with six controls, the GIL off and on; the tests pair records them; no notch; closed into the owner's fix (row creations_store_slots), whose end-of-pass rebuild covers it. | 2026-10-25T10:39:44Z |
| codegen_dynamic_import_d11 | done | melder_0 | tickets/tasks/completed/2026-10-10_enforce_import_policy_on_dynamic_imports_task.md | Notched 0.2.8271: dynamic imports answer to the codegen import gate - a `__import__` call or reference refused wherever an import list applies (A) and the runtime `__import__` wrapped to check each root (B); import statements of allowed roots still run, full_access unconstrained; the four strict xfails pass plus five cases; rebuild after closure. | 2026-10-25T10:52:15Z |
| codegen_materialize_d20 | done | melder_0 | tickets/tasks/completed/2026-10-10_refuse_materializing_over_live_modules_task.md | Notched 0.2.8272: materialize_codegen refuses loaded, core, stdlib and installed names under every profile; `materialize_modules` rules narrow; room builtins; failed materializes leave sys.modules as found; rebuild after closure. | 2026-10-25T12:11:19Z |
| codegen_room_policy_epic | done | melder_0 | tickets/epics/completed/2026-10-25_codegen_room_policy_defects_epic.md | D-10, D-11 and D-20 closed at 0.2.8270-0.2.8272 on the owner's decisions; each Breaking change in the running note. | 2026-10-25T12:11:19Z |
| notch_signature_s2 | done | melder_1 | tickets/stories/completed/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md | Notched 0.2.8273: every version of a SpellIndex is bound the way its first version was; staging and moves refuse another binding, a notch a held address; records below 5.0.0 refused; rebuild after closure. | 2026-10-25T12:26:46Z |
| creations_store_slots | done | melder_3 | tickets/stories/completed/2026-10-25_creations_store_slots_by_binding_story.md | Notched 0.2.8274: a Creations store files each binding's objects in its own slot (`Spell.store_key`) on one shelf per spell_id; S1-S9 fixed, purge and the probes cover every binding, cache generation 25; the asset and bundle rebuild not run, on the owner's word. | 2026-10-25T14:05:41Z |
| notch_fanout_race | done | melder_0 | tickets/tasks/completed/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md | Notched 0.2.8275: a lender's notch moves its borrowers inside its frozen window (borrowers sealed and frozen), a failed fan-out undoes it; race 0 of 20; xfail deleted; rebuild after closure. | 2026-10-25T14:24:32Z |
| notch_fanout_epic | done | melder_0 | tickets/epics/completed/2026-10-25_notch_fanout_inflight_melds_epic.md | The borrower-meld-vs-notch race closed at 0.2.8275 (design 2). | 2026-10-25T14:24:32Z |
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
