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
- NEW MESSAGE for melder_3 (from melder_2, 2026-10-25T03:22:43Z)
<!-- END USER-DEFINED: alerts -->

## Active Items
| work_item | status | mode | owner | agent_name | blocker | next | outcome | exit_signal | ticket | updated_at | reread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: active_items -->
| correctness_defects | in_progress | handoff | claude | melder_1 | none | S2's (A) has the owner's go (row notch_signature_s2); the stuck consumer is its own epic (row dependency_watchers_epic); S5, S11 and the recorded-world finding wait for the owner. | Defects where Melder's structure is wrong or stuck, a story each with a reproducer; the rest recorded as checked. | Every planned area swept and its defects filed as stories, or the owner redirects. | tickets/epics/2026-10-17_correctness_defects_epic.md | 2026-10-25T02:47:38Z | REQUIRED |
| notch_signature_s2 | in_progress | handoff | claude | melder_1 | none | The owner's calls 1-2 and the rename rule (DECISION note of 2026-10-25T02:47:38Z); then the Requirements rewritten and patch docs, after the probe-and-purge lane. | The owner's option (A) researched - every signature check and every meld identity mapped - and a fix plan for his review. | The research is on the story and the owner has reviewed it, or he redirects. | tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md | 2026-10-25T02:47:38Z | REQUIRED |
| many_child_ownership_epic | in_progress | handoff | claude | melder_1 | none | Ask the owner whether to close the epic on his removal decision. | The owner's removal decision recorded and carried out at 0.2.8267; the epic closed on his word. | The owner closes the epic or redirects. | tickets/epics/2026-10-20_reassess_many_child_disposal_ownership_epic.md | 2026-10-24T22:06:33Z | HELPFUL |
| pypi_provenance_epic | blocked | handoff | claude | melder_2 | the owner's TestPyPI and PyPI Trusted Publishers (D2), his first RC run and first attested release, and S6's keep-or-drop | On the owner's run links or logs, read RC / provenance or Release / provenance first; then S4 (both tokens retired) and S6 on his word. | Every Melder file on TestPyPI and PyPI carries verified PEP 740 provenance, both upload tokens retired, S6 decided. | The owner shares the hosted runs and accepts the epic, or redirects. | tickets/epics/2026-10-24_pypi_provenance_attestations_epic.md | 2026-10-25T03:20:31Z | REQUIRED |
| codegen_open_file_d10 | in_progress | implementation | claude | melder_0 | none | Option B: move pathlib to the permissive extras, flip the hybrid row and its docs, rerun; then the graph, notch, release note, closure and the rebuild last. | `open` denied under safe, hybrid and precision and every profile's file posture pinned by tests, landed with its notch, release-note entry and rebuild. | The task closes with its acceptance criteria met and the rebuild checked, or the owner redirects. | tickets/tasks/2026-10-10_deny_file_access_under_safe_codegen_task.md | 2026-10-25T08:05:21Z | REQUIRED |
| codegen_dynamic_import_d11 | blocked | handoff | claude | melder_0 | D-10 lands first (tranche order D-10, D-11, D-20) | melder_0 starts it after D-10 lands; the owner's go of 2026-10-25 stands. | D-11 re-measured on 0.2.8267, its mechanism read and options A and B costed for the owner. | The owner chooses A, B or both, or redirects. | tickets/tasks/2026-10-10_enforce_import_policy_on_dynamic_imports_task.md | 2026-10-25T02:02:27Z | REQUIRED |
| codegen_materialize_d20 | blocked | handoff | claude | melder_0 | D-10 lands first (tranche order D-10, D-11, D-20) | melder_0 starts it after D-10 lands; the owner's go of 2026-10-25 stands. | D-20 re-measured on 0.2.8267, its mechanism read and the namespace and builtins questions put to the owner. | The owner answers both questions, or redirects. | tickets/tasks/2026-10-10_refuse_materializing_over_live_modules_task.md | 2026-10-25T02:02:27Z | REQUIRED |
| notch_fanout_race | in_progress | handoff | claude | melder_0 | none | The owner chooses the design (2 recommended) and assigns an implementer; melder_0 departed 2026-10-25. | The race re-measured on 0.2.8267 and in one Book, its mechanism read and the two designs costed for the owner. | The owner chooses the design, or redirects. | tickets/tasks/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md | 2026-10-25T01:46:18Z | REQUIRED |
| probe_purge_every_version | in_progress | implementation | claude | melder_1 | none | Run the related suites the GIL off and on, then the docs, the notch, the release note, closure and the rebuild. | purge and has_live_creation reach any version the conduit can see by its spell_id, landed with tests, notch, release note and rebuild. | The story turned in with its tests green and the rebuild checked, or the owner redirects. | tickets/stories/2026-10-25_probe_and_purge_reach_every_version_story.md | 2026-10-25T03:22:38Z | REQUIRED |
| dependency_watchers_epic | ready | discovery | claude | melder_1 | none | S1 - the watcher and announcer matrix - after the probe-and-purge lane lands. | Why a waiting consumer misses its provider, mapped for every watcher and announcer; then the fixes on the owner's word. | S1's matrix and the fix options are on the epic for the owner, or he redirects. | tickets/epics/2026-10-25_dependency_watchers_listen_for_names_epic.md | 2026-10-25T02:47:38Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Active Attention Details
<!-- BEGIN USER-DEFINED: active_attention_details -->
- WORK_ITEM: correctness_defects
  SWITCH_TRIGGER: Every planned area swept and its defects filed as stories, or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-17_correctness_defects_epic.md
- WORK_ITEM: notch_signature_s2
  SWITCH_TRIGGER: The research is on the story and the owner has reviewed it, or he redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-17_correctness_defects_epic.md
    - tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md
- WORK_ITEM: many_child_ownership_epic
  SWITCH_TRIGGER: The owner closes the epic or redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-20_reassess_many_child_disposal_ownership_epic.md
- WORK_ITEM: pypi_provenance_epic
  SWITCH_TRIGGER: The owner shares the hosted runs and accepts the epic, or redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-24_pypi_provenance_attestations_epic.md
- WORK_ITEM: codegen_open_file_d10
  SWITCH_TRIGGER: The task closes with its acceptance criteria met and the rebuild checked, or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-25_codegen_room_policy_defects_epic.md
    - tickets/tasks/2026-10-10_deny_file_access_under_safe_codegen_task.md
- WORK_ITEM: codegen_dynamic_import_d11
  SWITCH_TRIGGER: The owner chooses A, B or both, or redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-25_codegen_room_policy_defects_epic.md
    - tickets/tasks/2026-10-10_enforce_import_policy_on_dynamic_imports_task.md
- WORK_ITEM: codegen_materialize_d20
  SWITCH_TRIGGER: The owner answers both questions, or redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-25_codegen_room_policy_defects_epic.md
    - tickets/tasks/2026-10-10_refuse_materializing_over_live_modules_task.md
- WORK_ITEM: notch_fanout_race
  SWITCH_TRIGGER: The owner chooses the design, or redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-25_notch_fanout_inflight_melds_epic.md
    - tickets/tasks/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md
- WORK_ITEM: probe_purge_every_version
  SWITCH_TRIGGER: The story turned in with its tests green and the rebuild checked, or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/stories/2026-10-25_probe_and_purge_reach_every_version_story.md
- WORK_ITEM: dependency_watchers_epic
  SWITCH_TRIGGER: S1's matrix and the fix options are on the epic for the owner, or he redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-25_dependency_watchers_listen_for_names_epic.md
<!-- END USER-DEFINED: active_attention_details -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| cache_temp_file | done | melder_2 | tickets/tasks/completed/2026-10-04_per_process_conjure_cache_temp_file_task.md | Superseded by 0.2.8266's per-writer temp file; closed on the owner's word (ci_lane_loose_ends). | 2026-10-24T21:57:09Z |
| shared_gauntlet_config_order | done | melder_2 | tickets/tasks/completed/2026-09-22_shared_gauntlet_configuration_order_followup_task.md | Obsolete since f1cd22a22; the lane-parity guard passes with the GIL off and on; closed on the owner's word. | 2026-10-24T21:57:09Z |
| ci_lane_loose_ends | done | melder_2 | tickets/tasks/completed/2026-10-24_ci_lane_loose_ends_task.md | Melder says it depends on pip; pip pinned in the speed manifest, docs lock and both probes (pip check); two backlog tickets closed; rebuild at melder_1's landing. | 2026-10-24T21:59:15Z |
| many_child_ownership_removal | done | melder_1 | tickets/stories/completed/2026-10-24_remove_many_child_holder_ownership_story.md | Notched 0.2.8267: a `many` belongs to the scope that built it, the holder record removed; rebuild after closure; the epic waits for the owner. | 2026-10-24T22:06:33Z |
| src_architecture_to_spec | done | melder_3 | tickets/stories/completed/2026-10-24_src_architecture_trim_to_spec_story.md | src_architecture to its spec: 5,739 -> 4,784 lines, the 17 sections in order, no tooling paths; component mechanics and the MR inventory in src_components; rebuild after closure. | 2026-10-24T22:39:52Z |
| release_note_0_2_8265_cut | done | melder_1 | tickets/tasks/completed/2026-10-24_cut_release_note_0_2_8265_task.md | release_docs/0.2.8265.md holds the 0.2.8265 notes as released; the running note keeps 0.2.8266-0.2.8267; rebuild after closure. | 2026-10-24T22:53:33Z |
| windows_held_bundle_test | done | melder_0 | tickets/tasks/completed/2026-10-24_windows_held_cache_bundle_test_task.md | Windows-only test of the 0.2.8266 cache save: 4 passed on the owner's machine, the GIL off and on, [WinError 5] on every refusal; tests only. | 2026-10-24T23:03:28Z |
| testpypi_provenance | done | melder_2 | tickets/stories/completed/2026-10-24_testpypi_trusted_publishing_and_provenance_story.md | TestPyPI by Trusted Publishing with attestations; RC / provenance checks every file in five layers before install; no notch; hosted Not run; rebuild after closure. | 2026-10-25T00:39:21Z |
| src_components_to_spec | done | melder_3 | tickets/stories/completed/2026-10-24_src_components_to_spec_story.md | src_components to its spec: 12,642 -> 11,874 lines, history out, stale claims fixed, the MR inventory folded, core = the C3 Key Files union; rubric 84.5 (B); rebuild after closure. | 2026-10-25T01:12:33Z |
| src_architecture_to_spec_epic | done | melder_3 | tickets/epics/completed/2026-10-24_src_architecture_to_spec_epic.md | Both documents at their specs: src_architecture 5,739 -> 4,784 lines (81, B), src_components 12,642 -> 11,874 (84.5, B); assets and bundles rebuilt at v0.2.8267, both `--check` OK. | 2026-10-25T01:34:36Z |
| creations_many_disposal_docstrings | done | melder_3 | tickets/tasks/completed/2026-10-25_creations_many_disposal_docstrings_task.md | Notched 0.2.8268: the creations.py `many` disposal docstrings state the store since 0.2.8257; src_components, both code maps and the graph follow; two rebind outcomes to the owner (S3); rebuild after closure. | 2026-10-25T02:36:15Z |
| pypi_provenance_release | done | melder_2 | tickets/stories/completed/2026-10-25_pypi_trusted_publishing_and_provenance_story.md | PyPI by Trusted Publishing with attestations; Release / provenance checks every released file after the upload; no upload token in any workflow; the users' check documented; no notch; hosted Not run; rebuild after closure. | 2026-10-25T03:20:31Z |
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
