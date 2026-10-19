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
- NEW MESSAGE for melder_1 (from expert_1, 2026-10-19T22:26:52Z)
- NEW MESSAGE for muse_0 (from workflows_0, 2026-09-28T09:43:41Z)
- NEW MESSAGE for muse_0 (from workflows_0, 2026-09-28T08:24:12Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-27T20:29:26Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-27T21:49:53Z)
- NEW MESSAGE for muse_0 (from fable_0, 2026-09-27T22:06:50Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-27T23:08:51Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-28T00:15:29Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-28T00:24:01Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-28T00:37:34Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-28T01:00:46Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-28T01:10:20Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-28T01:11:37Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-28T08:40:12Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-29T21:28:19Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-29T21:34:35Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-29T22:29:43Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-29T23:41:45Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T00:05:25Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T00:24:49Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T10:44:26Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T15:49:07Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T17:19:01Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T18:23:27Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T18:48:41Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T18:58:51Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T19:31:23Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T19:46:23Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T20:21:52Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-09-30T21:18:29Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-10-01T10:15:59Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-10-01T10:47:49Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-10-01T10:56:27Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-10-01T11:10:44Z)
- NEW MESSAGE for muse_0 (from melder_0, 2026-10-01T11:26:16Z)
<!-- END USER-DEFINED: alerts -->

## Active Items
| work_item | status | mode | owner | agent_name | blocker | next | outcome | exit_signal | ticket | updated_at | reread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: active_items -->
| gauntlet_runtime_speed | in_progress | discovery | claude | melder_2 | none | Owner decides whether an open lever (thread-affine pools, one-lock anonymous link, single-check fast door) is worth a task. | Per-scope-cycle cost map vs dishka and dependency-injector, with ranked and prototyped candidates. | Next lever validated and its task opened, or the owner redirects. | tickets/tasks/2026-09-26_measure_gauntlet_scope_cycle_costs_task.md | 2026-09-26T23:01:16Z | REQUIRED |
| defect_hunting_spellbook | in_progress | discovery | opencode | muse_0 | none | Slice spellbook component sections then read the surface behind each claim. | Contradiction list with evidence; meaty issues flagged apart from polish. | Sweep list triaged or owner redirects to conduit/meld or arch diffs. | tickets/tasks/2026-09-27_spellbook_sweep_task.md | 2026-09-27T15:56:49Z | REQUIRED |
| defect_hunting_fixes_1 | in_progress | implementation | opencode | muse_0 | none | Re-slice each target fresh then repair findings 1-8 in order. | Corrected blocks with verified ranges; index check clean. | Batch repaired with gates passing or owner redirects scope. | tickets/tasks/2026-09-27_sweep_fixes_batch_1_task.md | 2026-09-27T16:07:16Z | REQUIRED |
| correctness_defects | in_progress | handoff | claude | melder_1 | none | S1, S8 and S3 are turned in and the pass is rebuilt for 0.2.8263; S2 and S5 follow on the owner's word; S11 waits for the owner. | Defects where Melder's structure is wrong or stuck, a story each with a reproducer; the rest recorded as checked. | Every planned area swept and its defects filed as stories, or the owner redirects. | tickets/epics/2026-10-17_correctness_defects_epic.md | 2026-10-19T14:25:39Z | REQUIRED |
<!-- END USER-DEFINED: active_items -->

## Active Attention Details
<!-- BEGIN USER-DEFINED: active_attention_details -->
- WORK_ITEM: correctness_defects
  SWITCH_TRIGGER: Every planned area swept and its defects filed as stories, or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/epics/2026-10-17_correctness_defects_epic.md
<!-- END USER-DEFINED: active_attention_details -->

## Recently Closed Anchors
| work_item | status | agent_name | ticket | note | closed_at |
| --- | --- | --- | --- | --- | --- |
<!-- BEGIN USER-DEFINED: closed_anchors -->
| managed_spell_mode_failures | done | expert_1 | tickets/tasks/completed/2026-10-19_fix_managed_spell_mode_test_failures_task.md | Landed 0.2.8264: runtime enum import restores Spell constructor/mock reflection; all 51 reported cases pass, 14393 runtime passes and 274 post-notch passes; assets checked. | 2026-10-19T22:35:14Z |
| spell_identity_is_the_code | done | melder_0 | tickets/epics/completed/2026-10-18_spell_identity_is_the_code_epic.md | Turned in on the owner's word: S1 (0.2.8257) and S2 (0.2.8258) landed; S3-S5 parked in the backlog with S6; the leftovers packaged by melder_1's 0.2.8259 rebuild. Next: S3-S6 on the owner's word. | 2026-10-19T00:49:20Z |
| binding_manifest_hash | done | melder_0 | tickets/stories/completed/2026-10-18_binding_manifest_hash_story.md | Landed 0.2.8258 (S2: the binding manifest and its hash in the caches and the record). Next: S3-S5 under the epic. | 2026-10-18T23:31:15Z |
| managed_spell_sphinx_docs | done | melder_2 | tickets/stories/completed/2026-10-18_managed_spell_sphinx_docs_story.md | S3 of EPIC-2026-10-18-managed_spell_examples_and_docs: Sphinx chapter docs/intermediate/managed-spells.md (docs checks green, 313 pages) and one release-note bullet; no src change; the lane's rebuild waived by the owner. Next: none. | 2026-10-18T23:08:20Z |
| managed_spell_examples_and_docs | done | melder_2 | tickets/epics/completed/2026-10-18_managed_spell_examples_and_docs_epic.md | Epic closed on the owner's directive: S1 lifecycle map, S2 lessons 42-48 and 34 probes (green on 3.14t), S3 chapter and release note; no src change, no notch; rebuild waived (melder_0's rebuild carries it). Next: none (the owner answered: a root's teardown cleans only what it holds). | 2026-10-18T23:08:20Z |
| root_teardown_docs | done | melder_2 | tickets/tasks/completed/2026-10-18_document_root_teardown_cleans_only_what_it_holds_task.md | Documentation only, no src change: src_architecture and src_components state the owner's rule that a root's teardown cleans only what it holds and today's order (its "open with the owner" framing corrected by TASK-2026-10-19-correct_root_teardown_docs_wording). Next: none. | 2026-10-19T00:15:30Z |
| minted_index_registry | done | melder_1 | tickets/stories/completed/2026-10-17_minted_index_missing_from_frame_registry_story.md | Landed 0.2.8259 (S4 of EPIC-2026-10-17-correctness_defects: the index remove_from_spell_index mints is registered with the frame as bind registers its new one, unregistered at the root's teardown; residency reads its version parked). Next: S7 with melder_1; spellbook.py and spell.py back to melder_0 (M1-42). | 2026-10-19T00:21:48Z |
| root_teardown_wording | done | melder_2 | tickets/tasks/completed/2026-10-19_correct_root_teardown_docs_wording_task.md | Documentation only, no src change: after the owner's review both documents say a root's teardown cleans what it holds (the children of out objects included) and that a raising disposal method is reported; the "open with the owner" framing is gone. Next: none. | 2026-10-19T00:43:26Z |
| book_teardown_parked | done | melder_1 | tickets/stories/completed/2026-10-17_book_teardown_leaves_parked_versions_uncleaned_story.md | Landed 0.2.8260 (S7 of EPIC-2026-10-17-correctness_defects: a Spellbook's teardown retires its parked versions and cleans the indexes only they hold). Next: S8 on the owner's word; spellbook.py and spell.py back to melder_0 (M1-44). | 2026-10-19T01:32:05Z |
| failed_notch_refusal | done | melder_1 | tickets/stories/completed/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md | Landed 0.2.8262 (S8 of EPIC-2026-10-17-correctness_defects: a notch whose incoming version fails its structural check is refused with nothing moved, its borrowers untouched). Next: S3's turn-in, then small fixes; the rebuild last. | 2026-10-19T13:24:30Z |
| parked_cleanup_contracts | done | melder_0, melder_1 | tickets/stories/completed/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md | Landed 0.2.8261 by melder_0 (S3 of EPIC-2026-10-17-correctness_defects: every cleanup_spell door takes a version out of every contract first); turned in by melder_1 on the owner's word. Next: small fixes; the rebuild last. | 2026-10-19T13:26:06Z |
| staged_signature_claims | done | melder_1 | tickets/stories/completed/2026-10-17_staged_version_releases_active_signature_story.md | Landed 0.2.8263 (S1 of EPIC-2026-10-17-correctness_defects: staging, an index move back and a lone parked disposal keep the active spell's binding signature). Next: S2 and S5 on the owner's word. | 2026-10-19T14:25:39Z |
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
- melder_0 landed 0.2.8257 (a spell_id is the SHA256 of the registered object's code, nothing from the bind call;
  one object is one spell; S1 of EPIC-2026-10-18-spell_identity_is_the_code) and 0.2.8258 (the binding manifest and
  its hash in both cache tiers and the SpellCrystal, record 4.3.0, creation cache generation 23; S2). Notch above it
  if you land after.
### Notch notice (melder_1, 2026-10-18)
- melder_1 landed 0.2.8255 (docstrings and comments call a SpellIndex a SpellIndex; lineage stays for the conduit
  scope tree; nothing renamed; TASK-2026-10-16-recheck_contract_consumers_when_provider_changes). Notch above it if
  you land after.
- melder_1 landed 0.2.8256 (`Spellbook.cleanup_and_remove_spell` and a direct `Spell.cleanup()` refuse the active
  version of an index that holds parked versions, as `cleanup_spell` does, all three naming the remedies;
  STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions). Notch above it if you land after.
- melder_1 landed 0.2.8259 (the index `remove_from_spell_index` mints is registered with the frame as `bind` registers
  the index it creates and leaves with its root; residency reads its version parked until a notch;
  STORY-2026-10-17-minted_index_missing_from_frame_registry). Notch above it if you land after.
### Notch notice (melder_1, 2026-10-19)
- melder_1 landed 0.2.8260 (a Spellbook's teardown retires its parked versions and cleans the indexes only they hold;
  STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned). Notch above it if you land after.
### Notch notice (melder_0, 2026-10-19)
- melder_0 landed 0.2.8261 (`cleanup_spell` takes a version out of every contract of its Book's root conduit
  - index links and version grants - before it disposes it, and the Spellbook's own door goes through the
  root conduit; STORY-2026-10-17-parked_cleanup_leaves_borrower_copies). No rebuild, on the owner's word:
  melder_1's S8 landing rebuilds for both. Notch above it if you land after.
### Notch notice (melder_1, 2026-10-19, S8)
- melder_1 landed 0.2.8262 (a notch whose incoming version fails its structural check is refused with nothing moved
  and its borrowers untouched; `SpellbookValidationError` takes a one-line `preface`;
  STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers). Notch above it if you land after.
### Notch notice (melder_1, 2026-10-19, S1)
- melder_1 landed 0.2.8263 (staging, an index move back and a lone parked disposal keep the active spell's
  binding signature: `_destroy_spell_index` drops only its own route and releases only the departing member's
  claim; STORY-2026-10-17-staged_version_releases_active_signature). Notch above it if you land after.
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
