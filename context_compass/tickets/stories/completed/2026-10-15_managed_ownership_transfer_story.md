# Story: managed_ownership_transfer - pools travel with an ownership transfer, back on rollback

- Completed: 2026-10-15T21:00:54Z
- Summary: landed 0.2.8246 - the owner stamp follows an ownership transfer's lineage both ways: the flip and the
  parked-member migration stamp through `_restamp` (the stamp-back registered first, a composed pool's discard in a
  `finally`), and `Creations.discard_managed_quantity` takes back an empty pool a stamp composed; pools move as the
  rows S3 and S4 built. U9 settled (a notch never re-stamps). Whole tree green in both GIL modes. Release-note
  sections "An ownership transfer brings the spell's objects with it by default" and
  "`Existence.managed_spell_quantity`: objects leased from a root-owned pool and released back" extended.

## Metadata
- Story ID: STORY-2026-10-15-managed_ownership_transfer
- Epic: EPIC-2026-10-14-managed_spell_quantity (tickets/epics/2026-10-14_managed_spell_quantity_epic.md); story 6 of 7
- Status: done
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-15T09:29:51Z
- Updated: 2026-10-15T21:00:54Z

## User Narrative
As an agent handing a managed spell to another root, I want its pool to move with it - idle objects, recorded children
and count - the same way `move_creations` moves every other record, so that the new owner keeps leasing the same
objects.

## Value / MRP Alignment
The owner: "you gotta add transfer of ownership for it too thats important". Transfer mechanics are reused, not
rewritten: the pool is one more row, and the registry follows the stores.

## Ticket Contract
- ENTRY_GATE: S5 closed;
  system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_managed_ownership_transfer.md written
  and linked; U9 answered from source; the mapping note recorded.
- EXECUTION_BOUNDARY: src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py (and Creations if the
  row handling needs a change), their tests and an integration test.
- DEPENDENCIES: S3-S5.
- EXIT_GATE: its tests green under `-X gil=0` and `-X gil=1`; the touched modules' existing suites green; one notch
  taken from `__version__` at landing with the running release note's managed section extended; the epic's Build
  Specification updated with what this story settled; story closed (completed folder, board sync)
- FAILURE_ESCALATION: DECISION_REQUEST if a change would alter an existing member's behaviour, an existing spell id or
  record, or the frame -> conduit -> Book lock order; CONFLICT when the source contradicts the epic's Build
  Specification (fix the spec first); BLOCKER when a gate cannot be met

## Requirements (Functional)
- B8 as written: move, no move, rollback, parked members; a release after the move reaches the moved pool; a notch
  after a transfer dispenses from the right store (U9).

## Requirements (Non-Functional)
- A transfer disposes nothing.
- No new lock or lock-order edge.

## Scope Boundaries
- In scope: pools through transfer and the notch check.
- Out of scope: any change to how other records move.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: acceptance criteria met with red-then-green tests in both GIL modes, the probe's B, D, E, F and G
  fixed, the transfer suites and the whole tree green in both modes; notched 0.2.8246 (delegated routine closure
  under the owner's go-ahead).
- prior: ready -> in_progress (2026-10-15T18:18:41Z): S5 landed and closed (0.2.8245, 2026-10-15T18:15:07Z); S6
  started with the transfer path and U9.
- prior: draft -> ready (2026-10-15T09:29:51Z): ready once S5 lands.

## Dependencies / Related Work
- EPIC-2026-10-14-managed_spell_quantity Build Specification B8; the transfer FACT note of 2026-10-15T08:55:25Z.

## Tasks (Implementation Checklist)
- [x] Read `_apply_notch` (U9), the flip and `_migrate_inactive_members` whole.
- [x] Component patch and mapping note.
- [x] Red tests: move, no move, rollback, parked members, releases.
- [x] Implement; green in both GIL modes; the transfer suites.
- [x] Notch, release note, epic spec update, close, board sync.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- After a move the target leases the source's idle objects and releases reach them.
- No move: the target starts empty, the old idle objects are undisposed; rollback restores the pool.

## Validation / Test Plan
- Transfer unit tests beside test_transfer_of_ownership.py; an integration test; both GIL modes.

## UX / API / Data Notes
- No new public surface.

## Risks / Mitigations
- The race between extract and restore -> documented (not-managed for that call).

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.
- [x] No `src/` edit before the component patch and the mapping note exist.

## Open Questions
- U9 answered (FACT note of 2026-10-15T18:43:16Z): a notch never re-stamps.
- For the owner: stamping versions staged before conjure (DECISION note, point 6); carried to the epic's Open
  Questions.

## Decision Log
- 2026-10-15T18:43:16Z (melder_0): the owner stamp follows the lineage both ways - parked members
  re-stamped, stamps rolled back, composed pools discarded (DECISION note).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/managed_spell_quantity_2026_10_15/architecture_patch.md
  - system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_managed_ownership_transfer.md
  - system_docs/patches/active/managed_spell_quantity_2026_10_15/code_description_patch_managed_ownership_transfer.md
  - artifacts/managed_spell_quantity_20261015/ (this story's runs and scripts)
- DISPOSITION: promote_to_documentation (patch docs); retain_as_reference (artifacts)
- CLEANUP_TRIGGER: patch docs promoted and archived at S7; artifacts retained

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - managed pools through ownership transfer
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose, design, implementation and tests of this story;
  created 2026-10-15T09:29:51Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-15T09:29:51Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Opened ready behind S5. Transfer seams on 0.2.8240: execute 367-507, rollback 1079-1104, `_move_creations`
    1512-1555, `_teardown_creations` 1557-1590, `_migrate_inactive_members` 1592-1635.
  EVIDENCE: src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:367-1635
  IMPACT: Names the read set.
  NEXT: Start after S5 closes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T18:18:41Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: S6 started on 0.2.8245. transfer_of_ownership.py is unchanged since 0.2.8240 (S1-S5 did not touch it); S3 and
    S4 already give a pool its `managed` extract/restore row and make the registry follow the store. Order: read
    transfer_of_ownership.py whole (execute, the flip, the inactive-member migration, the creation move, teardown
    and rollback), `_apply_notch` and `_reactivate_owned_spell` (U9), `Spell._add_owned_conduit` and Creations'
    managed rows; probe a managed transfer as it stands (move, no move, rollback, a notch after a transfer, a release
    after the move); then the S6 component patch and mapping note, red tests, the change, validation.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:334-351
  - context_compass/tickets/epics/2026-10-14_managed_spell_quantity_epic.md:1019-1050
  IMPACT: S6 may need few or no transfer edits: the patch is written after the probe shows what a transfer already
    does with a pool.
  NEXT: Read transfer_of_ownership.py whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T18:43:16Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: U9 answered: `_apply_notch` and `_reactivate_owned_spell` never re-stamp a member's owner; the promoted
    version keeps the stamp it had. A transfer re-stamps only the active member: the flip calls `_add_owned_conduit`
    with the target's store (for a managed version `ensure_managed_quantity` composes an empty target pool),
    `_migrate_inactive_members` moves the parked members' maps and `_owner_conduit_id` only, and neither rollback
    (`_rollback_spellbook_move`, `_rollback_inactive_members`) restores a stamp. The probe on 0.2.8245 (gil1): A
    (move, active only) and C (no move) work as designed. B - a version parked after conjure moves its pool to the
    target but keeps the source's store, so after a notch on the target its meld raises the missing-pool error.
    D - a failed moving transfer puts the pool back in the source while the spell keeps the target's store: the
    owner's meld raises missing-pool. E - a failed no-move transfer leaves the target an empty registered pool and
    the spell on the target's store: the owner's meld builds into the target's pool and a release by class raises
    "Session is managed by 2 pools". F - the same for `unique`: after a failed transfer the owner's meld builds a
    second object into the target's store. G - a `unique` version parked after conjure, moved and notched in on the
    target stores its object in the source's store. Every case is a record that names the wrong owner store.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3826-3966
  - src/melder/aether/spellbook/spellbook.py:1563-1621
  - src/melder/aether/spellbook/spell.py:1661-1717
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:367-507
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:936-1002
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1079-1104
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1383-1665
  - src/melder/aether/conduit/creations/creations.py:1116-1172
  - src/melder/aether/conduit/creations/creations.py:1476-1697
  - context_compass/artifacts/managed_spell_quantity_20261015/probes/probe_s6_managed_transfer.py:1-257
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s6_probe_managed_transfer_before_gil1.txt:1-41
  IMPACT: S6 is a stamping fix, not a row fix: rows already move and roll back (S3, S4); the owner stamp does not
    follow them. The same wrong stamp breaks `unique` (F, G), so the fix covers every existence.
  NEXT: Record the fix design (DECISION), then the component and code-description patches.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T18:43:16Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner stamp follows the lineage both ways. (1) The flip stamps through a helper that first registers
    the rollback stamping the active member back onto the source root, the way conjure stamps (the root's id, name,
    store, dynamic flag and gate controller, the Book's caching posture). (2) `_migrate_inactive_members` re-stamps
    every parked member that carries a stamp (`_owner_creations` set) onto the target the same way, each with its
    stamp-back; a version never stamped (staged before conjure) keeps today's behaviour. (3) A stamp that composed a
    pool the target store did not hold registers a rollback removing exactly that pool -
    `Creations.discard_managed_quantity(spell_id, pool)`, an identity-checked pop under the store lock, unregistered
    after it - and cleaning it; it is empty, because the lineage is disabled for the whole transfer, so nothing is
    disposed, and a pool the target already held is never touched. (4) Rows are unchanged: move takes every member's
    rows to the target (replacing the composed pools), no-move takes the active member's rows out and leaves parked
    rows in the source store; rollback runs in reverse, so rows go back before the stamps. (5) Locks: the stamps run
    under both conduit locks and outside the Book locks, as the flip's stamp already does (conduit -> spell -> store
    leaf -> registry leaf); rollbacks hold no conduit lock; no new edge. (6) Raised to the owner, not built here: a
    version staged with `bind_inactive` before conjure is never stamped (conjure stamps `_spells` only), so notching
    it in fails for every existence; the fix is to stamp parked members at conjure, outside this story.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1383-1665
  - src/melder/aether/conduit/creations/creations.py:1476-1697
  - src/melder/aether/spellbook/spellbook_creation_system.py:1331-1382
  - src/melder/aether/spellbook/spellbook.py:5285-5306
  IMPACT: Fixes B, D, E, F and G without touching how rows move; `_rollback_spellbook_move` and
    `_rollback_inactive_members` keep their signatures and bodies (their unit tests call them directly). Recorded for
    the patch: after a no-move transfer a parked managed version has a pool in each root (the source keeps its old one,
    as no-move keeps parked rows), so once that version is notched in, a release by class needs `conduit=`.
  NEXT: Write the S6 component and code-description patches and the mapping note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T18:45:39Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Entry gate met: the component and code-description patches are written and linked (architecture patch
    aligned: the TransferOfOwnership row, invariant 8, the interface deltas, coverage row 8). Mapping, patch section ->
    implementation -> validation:
    (1) component After 1 (the flip's stamp) -> `_stamp_owner`, `_restamp`, `_discard_composed_pool`; the flip's
    direct `_add_owned_conduit` call becomes `self._restamp(spell_obj)` -> unit: stamp-back registered before the
    stamp, discard registered only for a managed version whose pool the stamp composed; integration D, E, F.
    (2) component After 2 (parked members) -> `_migrate_inactive_members` calls `_restamp` for each moved member with
    `_owner_creations` set, after its map rollback -> unit: stamped re-stamped, unstamped skipped, rollback stamps
    back; integration B, G.
    (3) interface delta (discard) -> `Creations.discard_managed_quantity(spell_id, pool)` -> unit: identity,
    unregister, cleaned store, maps untouched, second call, concurrent calls.
    (4) code-description Rollback (order) -> no extra code (registration order) -> unit: the reverse-order trace;
    integration D, E.
    (5) state delta (no-move parked pools) -> behaviour as documented -> integration: no move with a parked managed
    version notched in: lease from the target's pool, release by class ambiguous, `conduit=` works.
    (6) validation -> the transfer suites (unit, component, integration) and the whole tree, both GIL modes.
  EVIDENCE:
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/component_patch_managed_ownership_transfer.md:1-80
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/code_description_patch_managed_ownership_transfer.md:1-53
  - context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15/architecture_patch.md:1-111
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1383-1665
  IMPACT: Every src edit of S6 maps to a patch section and a test; nothing in rows, locks or public surface changes.
  NEXT: Red tests: the unit file beside test_transfer_of_ownership.py, the discard tests, the integration file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T19:33:05Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Implemented as the patches say (scripts/s6_apply_src.py): `Creations.discard_managed_quantity` (identity
    check and pop under the store lock, unregister after it); TransferOfOwnership `_stamp_owner`, `_restamp` (stamp-back
    registered before the stamp, the composed pool's discard registered in a `finally`) and `_discard_composed_pool`;
    the flip's direct `_add_owned_conduit` call is now `self._restamp(spell_obj)`; `_migrate_inactive_members` re-stamps
    each moved member whose `_owner_creations` is set. Red first in both modes (31 failed, 11 passed of 42), then green
    in both (42 passed); the probe after the change shows B, D, E, F and G fixed and A, C unchanged. Targeted suites
    green in both modes: unit conduit_ward, test_conduit_dynamic and creations (846), the five transfer and managed
    component files (69; the structural-parity tests needed delete access, granted 2026-10-15T19:02Z), the ten
    transfer and managed integration files (135).
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:1200-1249
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1492-1499
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1588-1648
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1680-1802
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s6_red_gil0.txt:1-153
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s6_green_gil1.txt:1-10
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s6_probe_managed_transfer_after_gil1.txt:1-46
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s6_transfer_integration_gil1.txt:1-3
  IMPACT: The fix holds on the paths S6 touches; the whole tree is the remaining gate before the notch.
  NEXT: Run the whole tree in both GIL modes (resumable shards), then the notch and the release note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T20:48:33Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The whole tree is green in both GIL modes with the S6 change (runs/s6_validation_index.md): unit aether and
    spellbook 6981 passed (6951 at S5 plus the 30 S6 unit tests); the rest of the unit tree 2518 ids (2508 passed, 3
    skipped, 7 xfail, as S5); component 2411 ids (2387 passed, 23 skipped, 1 xfail, as S5); integration 2150 ids (2137
    passed - S5's 2125 plus the 12 S6 tests - 9 xfail, 2 xpass, 2 skipped, as S5); experimentation 254 ids (250
    passed, 4 skipped). Not run, by scope: an emission capture (S6 changes no codegen file, so no emitted plan can
    move) and a benchmark (S6 changes no meld path; a transfer is a cold control-plane operation). After the runs the
    Creations class docstring gained one line naming `discard_managed_quantity` (docstring only; the discard tests
    and the annotation guard re-run green).
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s6_validation_index.md:1-81
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s6_validation_index.py:1-77
  IMPACT: S6's exit gate is met: tests green in both modes and the touched modules' suites green. What remains is the
    turn-in: notch 0.2.8246, the release note, the epic's Build Specification, closure and board sync, rebuild last.
  NEXT: Notch 0.2.8246 and extend the running release note (transfer section and managed section).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: S6 - managed pools through ownership transfer (move, no move, rollback, parked members) and the notch (U9).
- State: done; landed 0.2.8246 (the FACT, DECISION, PLAN and MEASURE notes; runs/s6_validation_index.md; the probe
  before and after).
- Open for the owner: stamping versions staged with `bind_inactive` before conjure (DECISION note, point 6; the
  epic's Open Questions). Documented: after a no-move transfer a parked managed version notched in on the target
  needs `conduit=` for a release by class.
- Next: S7 (STORY-2026-10-15-managed_docs_release) - system docs, graph, tests docs, README, release note,
  benchmarks, patch promotion.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
