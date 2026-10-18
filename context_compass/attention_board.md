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
- NEW MESSAGE for melder_2 (from workflows_0, 2026-09-28T09:43:41Z)
- NEW MESSAGE for muse_0 (from workflows_0, 2026-09-28T09:43:41Z)
- NEW MESSAGE for melder_2 (from workflows_0, 2026-09-28T08:24:12Z)
- NEW MESSAGE for muse_0 (from workflows_0, 2026-09-28T08:24:12Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-27T11:40:40Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-27T13:25:25Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-27T20:29:26Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-27T21:49:53Z)
- NEW MESSAGE for melder_2 (from melder_0, 2026-09-27T21:49:53Z)
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
- NEW MESSAGE for melder_1 (from melder_0, 2026-10-18T15:01:53Z)
<!-- END USER-DEFINED: alerts -->

## Active Items
| work_item | status | mode | owner | agent_name | blocker | next | outcome | exit_signal | ticket | updated_at | reread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: active_items -->
| gauntlet_runtime_speed | in_progress | discovery | claude | melder_2 | none | Owner decides whether an open lever (thread-affine pools, one-lock anonymous link, single-check fast door) is worth a task. | Per-scope-cycle cost map vs dishka and dependency-injector, with ranked and prototyped candidates. | Next lever validated and its task opened, or the owner redirects. | tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md | 2026-09-26T23:01:16Z | REQUIRED |
| defect_hunting_spellbook | in_progress | discovery | opencode | muse_0 | none | Slice spellbook component sections then read the surface behind each claim. | Contradiction list with evidence; meaty issues flagged apart from polish. | Sweep list triaged or owner redirects to conduit/meld or arch diffs. | tickets/tasks/2026-09-27_spellbook_sweep_task.md | 2026-09-27T15:56:49Z | REQUIRED |
| defect_hunting_fixes_1 | in_progress | implementation | opencode | muse_0 | none | Re-slice each target fresh then repair findings 1-8 in order. | Corrected blocks with verified ranges; index check clean. | Batch repaired with gates passing or owner redirects scope. | tickets/tasks/2026-09-27_sweep_fixes_batch_1_task.md | 2026-09-27T16:07:16Z | REQUIRED |
| correctness_defects | in_progress | handoff | claude | melder_0 | none | Keep the record current as melder_1 fixes S9, then S4 and S7; S8 waits for the owner (M1-33). | Defects where Melder's structure is wrong or stuck, a story each with a reproducer; the rest recorded as checked. | Every planned area swept and its defects filed as stories, or the owner redirects. | tickets/epics/2026-10-17_correctness_defects_epic.md | 2026-10-18T14:14:10Z | REQUIRED |
| spell_identity_is_the_code | in_progress | implementation | claude | melder_0 | none | Land S1 with S2's cache keys on the owner's word: patches, the blast-radius run, the landing pass. | A spell_id that is the object's code; the bind signature a manifest with its own hash that revalidates; one object, one spell. | S1-S5 land with notches, docs and the rebuild (S6 parked), or the owner redirects. | tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md | 2026-10-18T15:01:53Z | REQUIRED |
| spell_id_code_hash | in_progress | implementation | claude | melder_0 | none | Update S1's patches for decision B and strict uniqueness; then the blast-radius run in a /tmp mirror. | The spell_id is the SHA256 of the registered object's code - its bases, class-level values and an object's data included; docstrings and comments out. | S1 lands with S2 (tests, docs, notch, rebuild), or the owner redirects. | tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md | 2026-10-18T15:01:53Z | REQUIRED |
| binding_manifest_hash | in_progress | discovery | claude | melder_0 | none | Inventory the spell_id-keyed caches and stores; write S2's component patch. | The bind signature a binding manifest with its own SHA256, in the creation cache's keys beside the spell_id. | S2 lands with S1 (tests, docs, notch, rebuild), or the owner redirects. | tickets/stories/2026-10-18_binding_manifest_hash_story.md | 2026-10-18T15:01:53Z | REQUIRED |
| failed_notch_refusal | blocked | handoff | claude | melder_1 | the owner's hold (chat 2026-10-18) | The owner's word to resume S8 (the edit list and its refinement). | A notch whose incoming version fails its commit check is refused with nothing moved; lender and borrowers stay on the outgoing version. | The fix lands with tests, docs, notch and rebuild, or the owner redirects. | tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md | 2026-10-18T13:40:43Z | REQUIRED |
| direct_cleanup_refusal | in_progress | discovery | claude | melder_1 | none | The owner's pick for removing an index's active version (S9's STRATEGY_DISCUSSION note); then the patch. | Removing an index's active version never strands its parked versions; what it does instead is the owner's pick. | The fix lands with tests, docs, notch and rebuild, or the owner redirects. | tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md | 2026-10-18T14:25:49Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Active Attention Details
<!-- BEGIN USER-DEFINED: active_attention_details -->
- WORK_ITEM: correctness_defects
  SWITCH_TRIGGER: Every planned area swept and its defects filed as stories, or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-17_correctness_defects_epic.md
- WORK_ITEM: spell_identity_is_the_code
  SWITCH_TRIGGER: S1-S5 land with notches, docs and the rebuild (S6 parked), or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md
- WORK_ITEM: spell_id_code_hash
  SWITCH_TRIGGER: S1 lands with S2 (tests, docs, notch, rebuild), or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md
    - tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md
- WORK_ITEM: binding_manifest_hash
  SWITCH_TRIGGER: S2 lands with S1 (tests, docs, notch, rebuild), or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md
    - tickets/stories/2026-10-18_binding_manifest_hash_story.md
- WORK_ITEM: failed_notch_refusal
  SWITCH_TRIGGER: The fix lands with tests, docs, notch and rebuild, or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-17_correctness_defects_epic.md
    - tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md
- WORK_ITEM: direct_cleanup_refusal
  SWITCH_TRIGGER: The fix lands with tests, docs, notch and rebuild, or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-17_correctness_defects_epic.md
    - tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md
<!-- END USER-DEFINED: active_attention_details -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| meld_contract_scan_trace | done | melder_1 | tickets/tasks/completed/2026-10-15_trace_meld_contract_scan_gate_task.md | Investigation only: the meld gate's contract scan and the flag that admits it traced and measured; successor TASK-2026-10-15-make_meld_state_checks_follow_spell_state. | 2026-10-15T18:46:58Z |
| managed_ownership_transfer | done | melder_0 | tickets/stories/completed/2026-10-15_managed_ownership_transfer_story.md | Landed 0.2.8246 (S6 of EPIC-2026-10-14-managed_spell_quantity: the owner stamp follows a transfer's lineage both ways, `discard_managed_quantity`). Next: S7 docs. | 2026-10-15T21:00:54Z |
| non_resolvable_book_flag | done | melder_1 | tickets/tasks/completed/2026-10-15_make_meld_state_checks_follow_spell_state_task.md | Landed 0.2.8247 (a resolvable=False lineage no longer holds its Book's validation flag); owner accepted. Next: rule 2 in TASK-2026-10-16-recheck_contract_consumers_when_provider_changes. | 2026-10-16T09:36:46Z |
| managed_docs_release | done | melder_0 | tickets/stories/completed/2026-10-15_managed_docs_release_story.md | Documentation, no notch (S7 of EPIC-2026-10-14-managed_spell_quantity: system docs, graph, README, release note, benchmarks); owner accepted. Next: none. | 2026-10-16T12:17:31Z |
| parked_versions_wired_at_conjure | done | melder_0 | tickets/stories/completed/2026-10-16_parked_versions_wired_at_conjure_story.md | Landed 0.2.8248 (S8: conjure wires the versions staged before it; cache generation 21); owner accepted. Next: none. | 2026-10-16T12:17:31Z |
| managed_spell_quantity | done | melder_0 | tickets/epics/completed/2026-10-14_managed_spell_quantity_epic.md | Epic accepted by the owner (S1-S8, 0.2.8241-0.2.8248). Next: TASK-2026-10-16-public_notch_target_for_staged_versions. | 2026-10-16T12:17:31Z |
| public_notch_target | done | melder_0 | tickets/tasks/completed/2026-10-16_public_notch_target_for_staged_versions_task.md | Landed 0.2.8249 (`notch_spell` by spell_id with its target checked; on the owner's extension `add_to_spell_index` / `remove_from_spell_index` by spell_id too). Rebuilt last, both checks OK. Next: none; conduit.py released to melder_1. | 2026-10-16T16:06:21Z |
| stamp_test_aether | done | melder_0 | tickets/tasks/completed/2026-10-16_stamp_test_boots_its_own_aether_task.md | Tests only, no notch: the managed stamp test installs a fresh Aether per test and passes after the frame tests (GIL off and on). Next: its tests_components entry rides the wording lane. | 2026-10-16T20:23:39Z |
| spell_id_wording | done | melder_0 | tickets/tasks/completed/2026-10-16_spell_id_wording_near_spell_index_task.md | Landed 0.2.8252 ("version id" named as the spell_id in 214 lines of 113 files). Turned in on the owner's word. Next: TASK-2026-10-17-spell_id_wording_in_held_files (backlog) after melder_1's release. | 2026-10-17T20:49:39Z |
| minted_index_selection | done | melder_0 | tickets/stories/completed/2026-10-17_minted_index_selects_its_parked_version_story.md | Withdrawn on the owner's ruling, no source change (not a defect: moving a version is the agent's call; activation takes a notch). Next: none; the graft side stays in STORY-2026-10-17-restore_drops_separated_parked_version. | 2026-10-17T23:25:30Z |
| meld_contract_scan | done | melder_1 | tickets/tasks/completed/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md | Landed 0.2.8250 (rule 2), 0.2.8251 (removal fix), 0.2.8253 (exact spell_id lookups) and 0.2.8255 (docstrings and comments call a SpellIndex a SpellIndex; renames withdrawn by the owner); turned in on the owner's "Land + close". Next: none; held files back to melder_0 (M1-28). | 2026-10-18T11:45:56Z |
| managed_settings_spell_id | done | melder_0 | tickets/stories/completed/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md | Landed 0.2.8254 (part A: the four managed settings left the spell_id); turned in on the owner's identity direction, part B superseded. Next: EPIC-2026-10-18-spell_identity_is_the_code. | 2026-10-18T11:45:58Z |
<!-- END USER-DEFINED: closed_anchors -->

## Notes
<!-- BEGIN USER-DEFINED: notes -->
### Active Attention Details

- gauntlet_runtime_speed: SWITCH_TRIGGER is the owner's pick among the open levers, or the owner's
  answer on the SpellSpace scope RISK; P1, P4, the tail, build locks and nested slot guard are turned in. The lever-1 lifecycle is closed as measured (21:15Z). RESUME_HIERARCHY: tickets/stories/2026-09-26_gauntlet_runtime_speed_story.md ->
  tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md.
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
### Notch notice (melder_1, 2026-10-14)
- melder_1 landed 0.2.8235 (a slotted holder's disposal-bearing `many` children register in the holder's store,
  not the meld's innermost scope; the opt-in singleton specializer declines graphs that feed a `many` step into
  a non-`many` step). Notch above it if you land after.
- melder_1 landed 0.2.8236 (a root's teardown leaves its cluster; the cloud's leave unshares the leaver's roots;
  the cloud finds a conduit's cluster through the frame's membership index). Notch above it if you land after.
- melder_1 landed 0.2.8237 (a cluster owns its team store: `unique_per_conduit_cluster` objects survive leader
  changes, die with the cluster, and `delete_cluster` raises their disposal failures). Notch above it if you land after.
- melder_1 landed 0.2.8238 (a slotted holder's disposal-bearing `many` children are recorded with the holder: purging
  the holder disposes them, an ownership move carries them, a `many` purge of their spell leaves them). Notch above it
  if you land after.
- melder_1 landed 0.2.8239 (`transfer_spell_ownership` defaults to `move_creations=True`: the source's objects for
  the spell move with it and a transfer disposes nothing). Notch above it if you land after.
- melder_1 landed 0.2.8240 (docstring and docs only: `transfer_spell_ownership` says a transfer hands over
  stewardship, not a working setup, and `include_dependencies` moves the direct dependencies). Notch above it if
  you land after.
### Notch notice (melder_0, 2026-10-15)
- melder_0 landed 0.2.8241 (`Existence.managed_spell_quantity` declared: the matrix, the "managed" route family
  and Phase 6 rank 0; S1 of EPIC-2026-10-14-managed_spell_quantity). Notch above it if you land after.
- melder_0 landed 0.2.8242 (the four `managed_spell_*` bind options, `ManagedSpellMode`, the Spell fields, the
  managed-only id part, RecordVersion 4.2.0 with restore/graft replay; S2). Notch above it if you land after.
- melder_0 landed 0.2.8243 (the managed pool `ManagedSpellQuantity` in the owning root's Creations,
  `ManagedSpellExhaustedError`, the probes' managed answer and purge 0; S3). Notch above it if you land after.
- melder_0 landed 0.2.8244 (`ReleaseManagedSpell`, the Aether-owned registry that gives managed objects back,
  `ManagedSpellLease` and four package-root exports; S4). Notch above it if you land after.
- melder_0 landed 0.2.8245 (managed objects leased through the emitted plans and doors - direct melds and
  injections - and `Conduit.managed_spell_meld`; S5). Notch above it if you land after.
- melder_0 landed 0.2.8246 (an ownership transfer stamps every version onto the new owner and a failed one stamps
  them back, discarding the empty pools its stamps composed; `Creations.discard_managed_quantity`; S6). Notch above
  it if you land after.
### Notch notice (melder_1, 2026-10-16)
- melder_1 landed 0.2.8247 (a lineage whose selected version was bound resolvable=False carries
  `SpellState.non_resolvable` and no longer holds its Book's validation flag up; `register_index(resolvable=...)`
  at bind, notch and the transfer flip and rollback). Notch above it if you land after.
- melder_1 landed 0.2.8250 (a satisfied SpellContract is not checked on every meld: the borrower Book's
  contracted-map mutators and a notch's downstream walk mark contract consumers and dependents for revalidation,
  the meld refreshes their stale dependencies before a plan compiles, a lost provider is named with its remedy, and
  a notch back reactivates a parked version grant;
  TASK-2026-10-16-recheck_contract_consumers_when_provider_changes). Notch above it if you land after.
- melder_1 landed 0.2.8251 (`Spellbook._remove_contracted_spell` removes exactly the copy of the spell_id it is
  given - the active copy only when it is that version, else the parked copy - so an index unlink after a notch
  completes in any member order; TASK-2026-10-16-recheck_contract_consumers_when_provider_changes). Notch above it
  if you land after.
### Notch notice (melder_0, 2026-10-16)
- melder_0 landed 0.2.8248 (conjure wires the versions staged with `bind_inactive` before it, so they meld after a
  notch; creation cache generation 21; S8 of EPIC-2026-10-14-managed_spell_quantity). Notch above it if you land
  after.
- melder_0 landed 0.2.8249 (`Conduit.notch_spell` takes `spell_id=` - the spell_id `bind` or `bind_inactive`
  returned - beside `spell=`, exactly one, and checks its target before and inside its transaction; on the owner's
  extension `add_to_spell_index` and `remove_from_spell_index` take `spell_id=` too;
  TASK-2026-10-16-public_notch_target_for_staged_versions). Notch above it if you land after.
### Notch notice (melder_1, 2026-10-17)
- melder_1 landed 0.2.8253 (a spell_id lookup answers the spell it names: `Spellbook.find_spell_by_spell_id` and
  `Conduit.get_spell_by_spell_id`, renamed from `find_spell_by_id` / `get_spell_by_id` with no alias, return the
  active or parked version the spell_id names, and the Rift rooms' command is renamed with them;
  TASK-2026-10-16-recheck_contract_consumers_when_provider_changes). Notch above it if you land after.
### Notch notice (melder_0, 2026-10-18)
- melder_0 landed 0.2.8254 (a managed spell's four settings - mode, limit, queue timeout, reset names - are not part
  of its spell_id; a rebind under the same spell_id gives its pool the new settings; creation cache generation 22;
  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool, part A). Notch above it if you land after.
### Notch notice (melder_1, 2026-10-18)
- melder_1 landed 0.2.8255 (docstrings and comments call a SpellIndex a SpellIndex; lineage stays for the conduit
  scope tree; nothing renamed; TASK-2026-10-16-recheck_contract_consumers_when_provider_changes). Notch above it if
  you land after.
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
