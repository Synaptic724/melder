# Task: Investigate stored instances Melder drops without disposing them (transfer, contract invalidation)

## Metadata
- Task ID: TASK-2026-10-14-investigate_stored_instances_dropped_without_disposal
- Story: none - D3 of EPIC-2026-10-14-slotted_lifetime_ownership_fixes (opened by
  TASK-2026-10-14-audit_slotted_lifetime_ownership, done)
- Status: review
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-14T18:40:43Z
- Updated: 2026-10-15T00:07:24Z

## Objective
Two call sites retire stored instances with `Creations.extract_spell_creations`, which only extracts:
`TransferOfOwnership._teardown_creations` (the default `move_creations=False`, documented as tearing the
source-side state down) and `ConduitWard._invalidate_contract_consumers` (a changed contract clears its
SpellContract consumers' stored instances). Proven on 0.2.8235: a transferred disposal-bearing `unique` holder
is never disposed - `closes` stays 0 through both roots' teardowns while the target builds a new one (t3); a
lender's or a cluster leader's teardown drops the borrower's per-conduit consumer from its store and it is never
disposed either, though it still references the lender's disposed instance (b7, c1). Both helpers swallow every
exception, and the invalidation visits only the root's own store. Find every place that retires an instance
by extraction and lay out how each should dispose, for the owner's epic.

Rescoped by the owner (2026-10-14, Notes 21:17:51Z, 22:14:49Z and 23:00:25Z): Melder's infrastructure cleans up its
own state; the application objects it hands out are not policed and may stay pending for agents to manage. A transfer
disposes nothing. The public transfer verbs default to `move_creations=True` (landed as 0.2.8239), so a transferred
`unique` stays one object; `move_creations=False`, a move into a slot the target already fills (m1) and contract
invalidation (b7, l1, l2) keep their behaviour.

## Ticket Contract
- ENTRY_GATE: the epic's board row routes it; the reproducer is rerun on the current tree; red tests fail before
  any src edit; the epic's patch docs are written, linked and mapped.
- EXECUTION_BOUNDARY: the code paths below, the fix, its tests and docstrings (owner directive 2026-10-14: fix it
  under EPIC-2026-10-14-slotted_lifetime_ownership_fixes); system docs, release note and notch with the epic.
- DEPENDENCIES: TASK-2026-10-14-audit_slotted_lifetime_ownership (the probe and its runs);
  EPIC-2026-10-14-many_child_follows_holder (0.2.8235).
- EXIT_GATE: root cause recorded; red tests red before and green after the fix, GIL off and on; the probe case
  clean; no warm meld path change; the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST for every behaviour that is a design choice; BLOCKER if the reproducer no
  longer fails on the current tree (record it and stop).

## Scope Boundaries
- In scope: the defect named in the objective, its code paths and every caller that shares the cause.
- Out of scope: the fix itself; the other audit findings (their own tasks).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: opened from the audit with a reproducer that fails on 0.2.8235, GIL off and on (owner directive,
  chat 2026-10-14: "make a task to investigate it and then we'll turn it into an epic").
- from_state: ready
- to_state: in_progress
- transition_reason: the epic's tranche reached D3 (code re-read, fix shape recorded, 2026-10-14).
- from_state: in_progress
- to_state: review
- transition_reason: the transfer half landed as 0.2.8239 (default) and 0.2.8240 (handover docstring) with regression
  tests green GIL off and on; the invalidation half was ruled out by the owner (no change); the lane's full tree is
  green at 0.2.8240 and the change is promoted into the system docs; the owner accepts.


## Steps / Checklist
- [x] List every caller of `extract_spell_creations` and of any other removal without disposal; classify each as a
      move (restore follows) or a retirement (Notes 21:11:03Z, 21:12:38Z: the transfer teardown, the move into a
      filled slot, the invalidation and the lesser stores it never visits).
- [x] Transfer half: regression tests for the default transfer (t3, u2) red on 0.2.8238 and green on 0.2.8239,
      GIL off and on; landed as 0.2.8239 (the default flip and docstrings, per the owner's ruling).
- [x] Invalidation half: ruled by the owner (Notes 23:00:25Z): left as it is - b7, l1 and l2 are intended
      behaviour; no red tests, no fix.
- [x] Lay out options (Notes 19:23:31Z, 21:26:20Z, 21:31:40Z); the transfer options were ruled on, the
      dispose-on-transfer option withdrawn.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Root cause with evidence, red tests, and fix options for the owner's epic.

## Files / Paths Impacted
- `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
- `src/melder/aether/conduit/creations/creations.py`
- `src/melder/aether/conduit/conduit.py` (`transfer_spell_ownership` default and docstring, 0.2.8239)
- `tests/integration/melder/conduit/test_conduit_integration_transfer_ownership.py` (three tests, 0.2.8239)
- `docs/intermediate/ownership.md`, `release_docs/next_version_release.md`, `src/melder/__version__.py`

## Validation
- Reproducer run on 0.2.8235 (Python 3.14.7t, GIL off and on, identical): see Notes.
- 0.2.8239: the transfer tests red on 0.2.8238 and green after, the transfer and ownership suites (455) and ten
  aether, conduit, spellbook and crystallizer chunks green, GIL off and on; probes t3, u2, e1, e2 after the flip;
  the release example on the repo's src, GIL off and on (Notes 22:18:49Z, 22:34:30Z, 22:40:45Z).
- End of the epic's pass (0.2.8240): the full tree green GIL off and on, the audit probe's eleven cases, the
  emission diff and the warm-meld benchmarks (epic Notes 2026-10-14T23:39:45Z).
- Reproduce (from a tree root with src/ and tests/):
  `PYTHONPATH=src:. python context_compass/artifacts/slotted_lifetime_audit_20261014/probe_lifetime_owners.py t3 b7 c1`

## Risks / Rollback Notes
- Investigation only; nothing to roll back.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Board sync completed for successor routing or closure anchor update.

## Open Questions
- Answered (owner, 2026-10-14): the default transfer moves the source's instances
  (`move_creations=True`); a transfer disposes nothing.
- Answered (owner, 2026-10-14): contract invalidation stays as it is; the objects it lets go of stay
  pending for agents (Notes 23:00:25Z).

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/slotted_lifetime_audit_20261014/ (the probe and its runs, shared with the audit task)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decided when the owner's epic closes

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - retirement by extraction, with no disposal
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose and evidence; the whole ticket; initial revision
  2026-10-14T18:40:43Z; the reproducer is the audit's probe. The rule and the directive are the owner's.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-14T18:40:43Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Opened from TASK-2026-10-14-audit_slotted_lifetime_ownership with a reproducer: probe case(s)
    t3 b7 c1 fail the owner's rule on 0.2.8235 as described in the Objective, with identical output GIL off and
    on. The code paths below were read in full during the audit; the root-cause analysis, red tests and fix options
    are this task's work.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:361-505
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1546-1575
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2682-2737
  - src/melder/aether/conduit/creations/creations.py:1075-1137
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_lifetime_owners_all_gil0.txt:24-30
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_lifetime_owners_all_gil0.txt:60-68
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_lifetime_owners_all_gil0.txt:2-10
  - context_compass/artifacts/slotted_lifetime_audit_20261014/probe_lifetime_owners.py:1-608
  IMPACT: The defect is real on today's tree; the owner can turn this task into an epic.
  NEXT: Rerun the reproducer on the current tree, then read the paths in Steps and record the root cause.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T18:55:12Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner turned the audit's tasks into one fix lane and put it first ("all these need to be fixed
    go ahead and target all these fixes since you have context first"); this task is now the epic's D3
    and covers the fix as well as the investigation (Ticket Contract updated).
    Scope per the owner's transfer guidance: a transferred `many` spell's objects may stay with the source
    (`move_creations=False` leaves them in the source store, disposed when it ends) instead of being dropped; a
    unique kind's instance is moved, or disposed with its children, never left or dropped.
  EVIDENCE: context_compass/tickets/epics/2026-10-14_slotted_lifetime_ownership_fixes_epic.md:147-159
  IMPACT: Investigation, red tests and the fix land here; docs, notes and the notch go with the epic's pass.
  NEXT: Wait for the epic's tranche order (D6 verdict, patch docs), then rerun the reproducer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T19:23:31Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Root cause re-read and fix shape chosen. `TransferOfOwnership._teardown_creations` extracts the active
    member's entries from the source store for every existence and keeps them only for rollback, so they are never
    disposed; `ConduitWard._invalidate_contract_consumers` extracts each impacted consumer's entries, again for every
    existence, and drops them. Under the owner's transfer ruling (Decision Log 2026-10-14) the fix is per existence:
    `many` objects are left behind in the store that holds them (they are not cached, so a rebuild needs nothing
    retired; they are disposed when that scope ends), `unique` and `unique_per_conduit` entries are retired and
    disposed with their holder-owned children, lineage stays skipped, and cluster and spellspace entries are never in
    the source store. Transfer extracts as today (rollback restores the rows) and disposes the extracted rows only
    after the move succeeded, outside the TRANSFER_OWNERSHIP window, raising one ExceptionGroup after the transfer
    finished; invalidation disposes what it retires right away and logs disposal failures through the ward logger,
    because every call site runs inside a contract mutation that must complete (they already swallow its errors).
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:361-505
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1506-1575
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2682-2737
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1051-1233
  - src/melder/aether/conduit/conduit.py:4140-4210
  IMPACT: New Creations helpers (dispose extracted rows; retire a singleton entry with its children); transfer keeps
    its rollback; no lock is added under a ward or contract lock beyond today's store-lock extraction.
  NEXT: Record the holder-owned children representation (D4/D5) that the retirements dispose with the holder.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T20:30:57Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: RISK
  CLAIM: Interim state between the 0.2.8238 and 0.2.8239 notches: once a holder's children are recorded with the
    holder (0.2.8238), the two extracting retirements this task fixes - the default transfer teardown and contract
    invalidation - carry the children out of the store with the holder's row and drop them undisposed too, where on
    0.2.8237 the children stayed in their bucket and were disposed when the store ended. The window closes when
    0.2.8239 disposes every extracted row; both notches land in the same pass, before any hand-off or release.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1546-1575
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2682-2737
  - context_compass/system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/component_patch_creations.md:5-30
  IMPACT: 0.2.8238 must not be handed off alone; the D3 red tests (t3, b7, many left behind) also cover the children.
  NEXT: Land 0.2.8238, then write the D3 red tests including a holder with a child, and land 0.2.8239 in this pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T21:11:03Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Reproducer rerun on 0.2.8238 (identical GIL off and on): t3 still drops the transferred `unique` holder
    (closes 0 through the transfer and both teardowns; the target builds a new one); b7 still drops the borrower's
    per-conduit consumer at the lender's teardown (gone from the borrower store, closes 0 to the end); c1 shows no
    lifetime defect after D1/D2 (the cluster instance waits in the team store for the cluster's cleanup; the
    member's holder is disposed once, at the member's teardown). The code re-read for the fix found four more facts:
    (1) a transfer retires rows in a fixed order - the root's teardown in `execute` step 4, then each moved direct
    dependency's in `_transfer_owned_dependencies` - so the patch doc's "newest row first" would dispose a dependency
    before the root that holds it; retirement order is the right disposal order; (2) a completed sub-transfer is never
    rolled back, so after a later parent failure the root's rows are restored while the dependencies' rows would be
    disposed under the restored root; (3) `restore_spell_creations` pops whatever the target store holds for the key
    before restoring, so `_move_creations` would drop the target's own entry undisposed when the target already holds
    one (a `unique_per_conduit` spell it borrowed and melded) - UNKNOWN until probed; (4) the invalidation retires
    from the root's own store only, so a lesser's per-conduit consumer keeps its instance - UNKNOWN whether a lesser
    then serves it stale after a relink.
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_t3_b7_c1_0_2_8238_gil0.txt:1-25
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:361-502
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1506-1575
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1823-1860
  - src/melder/aether/conduit/creations/creations.py:1377-1474
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2682-2740
  IMPACT: The retired rows must keep their spell ids (a failed parent restores its completed sub-transfers' rows
    too) and are disposed in retirement order; the move path and the lesser stores are probed before the red tests.
  NEXT: Probe (3) the move into a target slot that already holds the target's own entry and (4) a lesser's consumer
    after sever and relink, on 0.2.8238.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T21:12:38Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Both UNKNOWNs of the previous note are real defects on 0.2.8238 (probe, identical GIL off and on). m1: a
    `move_creations=True` transfer of a `unique_per_conduit` spell into a target that borrowed and melded it replaces
    the target's own instance with the source's and drops it undisposed (closes 0 to the end, while the moved one is
    disposed once). l1: a sever retires the root's consumer (dropped, closes 0) but leaves the lesser's consumer in
    the lesser store, and after a relink the lesser serves that same consumer again. l2: when the lender is torn down
    (its resource disposed) and a second lender grants the spell, the lesser serves the old consumer whose dependency
    is already closed - the invalidation never reached the lesser's store.
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_d3_move_and_lesser_0_2_8238_gil0.txt:1-26
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/probes/probe_d3_move_and_lesser.py:1-232
  - src/melder/aether/conduit/creations/creations.py:1377-1474
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2682-2740
  IMPACT: Two more cases for the owner: the move replaces the target's own entry (m1), and the invalidation reaches
    only the root's store, so a lesser keeps its consumer (l1, l2). Both were later ruled intended behaviour.
  NEXT: Read the ward's lineage walk (the child map and its snapshot reads) to find the lessers' stores by key, then
    write the PLAN note and the red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T21:17:51Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: CONFLICT
  CLAIM: The owner (chat 2026-10-14, after the status report): "transfer doesn't dispose anything it literally moves
    assets over conditionally, otherwise it just leaves them there" and "uniques are managed differently since they
    are important". That conflicts with this task's transfer plan (the 19:23:31Z DECISION, the transfer patch docs:
    a default transfer retires and disposes `unique`/`unique_per_conduit` entries), and today's code does neither of
    the owner's two things: `_teardown_creations` extracts the active member's entries from the source store and keeps
    the rows only for rollback, so after a successful default transfer the instance is in no store and is never
    closed (t3). The plan would also have disposed a transferred existing-object spell (a `unique` bound instance).
    Only `unique_per_conduit_lineage` is left in place today. D3 src work is stopped; nothing in src changed for D3.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1546-1575
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:361-502
  - src/melder/aether/conduit/conduit.py:4217-4290
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_t3_b7_c1_0_2_8238_gil0.txt:10-16
  IMPACT: The transfer half of D3 changes direction (never dispose; leave or move per existence), the transfer patch
    docs are rewritten before any src edit, and the invalidation (b7, l2) and move-collision (m1) rules wait for the
    same ruling.
  NEXT: Ask the owner the per-existence rule for a default transfer, a move into a slot the target already fills, and
    what contract invalidation does with the consumer instances it retires.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T21:26:20Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Read at the owner's request (tests, docstrings, the Sphinx lesson, history), no change made. What they
    define: a transfer moves STEWARDSHIP of the whole index - the target melds it, the source no longer can, inactive
    members and (with `include_dependencies`) direct dependencies move, borrowers are unshared or repointed, lineage
    instances stay where they were resolved, spellspace instances are not preserved; existing instances move only
    with `move_creations=True` (lesson 23 and the docs page show only that path, with no instance melded before the
    transfer). The default path is pinned by one unit test with a placeholder existence: the source's entries are
    removed and the target receives none; the docstrings call it tearing the source side down. Since the first commit
    (87e1c3fa4, 2025-12-07) no version ever moved `unique` instances on the default path, and no test or doc says a
    unique always moves or that a transfer disposes anything. The owner's contract (uniques move no matter what, the
    rest only with `move_creations=True`, nothing disposed) therefore differs from the code in one place: the default
    path takes an existing unique out of the source store and puts it nowhere (t3).
  EVIDENCE:
  - UX_and_AIX_experiences/02_intermediate/23_transfer_of_ownership.py:1-58
  - docs/intermediate/ownership.md:14-20
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:1524-1601
  - tests/integration/melder/conduit/test_conduit_integration_lifecycle.py:386-523
  - tests/integration/melder/aether/conduit/test_index_transfer_ownership_integration.py:89-177
  - src/melder/aether/conduit/conduit.py:4217-4290
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1546-1575
  IMPACT: The transfer half of D3 is not "dispose on teardown" (dropped); if the owner adopts his contract it is a
    small default-path change (move uniques, leave the rest) plus clearer docstrings and docs.
  NEXT: Report to the owner and wait for his ruling; no src or test edits until then.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T21:31:40Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: For the owner's discussion of the right transfer path (probe on 0.2.8238, GIL off; no change made). u2: a
    constructed `unique` held by a source consumer, default transfer - the target's next meld builds a SECOND
    instance while the consumer keeps the first; the first is never disposed (closes 0), the second once: two live
    instances of one `unique` spell. Existing objects are different: Melder registers a bound instance without a
    disposal record and never disposes it, even with no transfer (e0); after a default transfer it is in no store but
    every meld still returns the bound object (e1), and `move_creations=True` puts it in the target store (e2). The
    existence routing the site plan uses: `unique` -> the spell owner's store (`_owner_creations`, repointed by the
    transfer), `unique_per_conduit` -> the melding conduit's store, `unique_per_conduit_lineage` -> the lineage
    root's store, `unique_per_conduit_cluster` -> the cluster's team store, `unique_per_spell_space` -> the
    spellspace's store, disposal-bearing `many` -> the innermost scope (or the holder's record). The `Existence`
    docstrings for the cluster ("stored in the owning conduit creations map") and spellspace ("versioned and
    resettable") modes are stale.
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_transfer_uniques_0_2_8238_gil0.txt:1-24
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/probes/probe_transfer_uniques.py:1-169
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1516-1550
  - src/melder/aether/spellbook/spellbook_creation_system.py:1332-1382
  - src/melder/aether/spellbook/existence/existence.py:3-121
  IMPACT: The default transfer of a constructed `unique` splits it into two instances (one orphaned, never
    disposed); that is the complication the owner named, and the reason to decide the default path for `unique`.
  NEXT: List the existence types for the owner with what transfer does to each, and discuss the path; no src edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T22:14:49Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Owner ruling after reading the transfer tests and docs together (chat 2026-10-14): "I think we set the
    move_creation=True by default isn't that the best play? that way we don't need to do much and update everything
    in docstrings", then "no we leave it alone and simply leave it default true, its up to the user to break their
    own shit". D3's transfer half is therefore: the public `transfer_spell_ownership(move_creations=...)` defaults to
    True (the ward's mirror too), so a transferred `unique` stays one object and the source's instances follow the
    spell; the docstrings and the docs page say plainly what each value does. `move_creations=False` keeps today's
    behaviour (the caller's choice), as does a move into a slot the target already fills (m1: documented, not
    changed). `TransferOfOwnership`'s own constructor default stays False (the conduit and the ward always pass the
    value; 119 unit tests construct it directly). The dispose-on-transfer plan (19:23:31Z) and the transfer
    retirement helpers are withdrawn. The invalidation half (b7, l2) waits for the owner's ruling.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:4217-4290
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:3760-3820
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:148-219
  IMPACT: 0.2.8239 is a default flip with docstrings, the docs page, regression tests and a Breaking release-note
    entry; no transfer logic changes.
  NEXT: Rewrite the transfer patch docs to this scope, then write the regression tests and run them on 0.2.8238.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T22:18:11Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch docs rescoped to the owner's ruling and read in order (architecture: D3 objective, invariants 5 and 8,
    interface deltas, migration order; component_patch_ownership_transfer rewritten; the transfer code description
    marked superseded; the creations and ward patches mark the invalidation pieces pending). Mapping for 0.2.8239:
    (1) architecture D3 + invariant 5 + the public default -> `Conduit.transfer_spell_ownership(move_creations=True)`
    and `ConduitWard._transfer_spell_ownership(move_creations=True)` -> red tests appended to
    test_conduit_integration_transfer_ownership.py: a default transfer keeps a `unique` one object (a source consumer
    and the target's meld share it, the report's options say True, closed 0 at the source's teardown and 1 at the
    target's) and moves a tracked `many` object (closed 0 then 1), plus an opt-out control (`False` builds anew);
    (2) component_patch_ownership_transfer docstrings -> the two verbs, the `TransferOfOwnership` class and
    constructor, `_move_creations`, `_teardown_creations` say what each value does (m1 documented) -> read back;
    (3) docs page -> docs/intermediate/ownership.md transfer section; (4) release note (Breaking, with the opt-out),
    notch, notch notice. Validation: red on 0.2.8238 GIL off and on, then the transfer suites and the aether,
    conduit, spellbook and crystallizer chunks on the scratch tree GIL off and on.
  EVIDENCE:
  - context_compass/system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/architecture_patch.md:1-106
  - context_compass/system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/component_patch_ownership_transfer.md:1-38
  - src/melder/aether/conduit/conduit.py:4217-4290
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:3760-3820
  IMPACT: The src change is two default values and docstrings; no transfer logic, lock or meld path changes.
  NEXT: Append the regression tests and run them on 0.2.8238, GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T22:18:49Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Red on 0.2.8238 (scratch tree, src unchanged), identical GIL off and on: of the three tests appended to the
    transfer integration module, the two default-transfer tests fail (the report's options say `move_creations`
    False; a tracked `many` object is closed 0 times through both teardowns) and the opt-out control passes, with the
    module's three existing tests green (2 failed, 4 passed).
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/red_d3_transfer_default_0_2_8238_gil0.txt:1-20
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/red_d3_transfer_default_0_2_8238_gil1.txt:1-15
  - tests/integration/melder/conduit/test_conduit_integration_transfer_ownership.py:156-288
  IMPACT: The entry gate for the 0.2.8239 src edit is met.
  NEXT: Flip the two defaults, rewrite the transfer docstrings, run the module and the transfer suites green.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T22:34:30Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Green on the scratch tree carrying the 0.2.8239 change (both public defaults flipped to
    `move_creations=True`, transfer docstrings rewritten, the three tests appended; the repo still at 0.2.8238),
    identical GIL off and on: the transfer and ownership suites 455 passed (the transfer integration module with its
    two formerly red default-transfer tests and the opt-out control, the holder-children, lifecycle, index-transfer
    and change-control integration modules, the transfer footprint and transaction component modules, the unit
    transfer package and the conduit ward and dynamic-conduit units); the int_conduit, int_aether, comp_aether,
    unit_aether, unit_sb, comp_sb, int_sb, unit_cryst, comp_cryst and int_cryst chunks passed with their 0.2.8238
    counts (xfail, skip and xpass unchanged). Probes after the flip (GIL off): t3 - the default transfer puts the
    `unique` holder in the target store, the target melds the same holder, it is closed 0 times at the source's
    teardown and once at the target's; u2 - the target melds the tool the source consumer holds, one object closed
    once; e1 passes `move_creations=False` explicitly, so it is now the opt-out (the bound object is in no store and
    every meld still returns it), e2 puts it in the target store; a bound existing object is never closed (e0).
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/d3_transfer_suites_0_2_8239_gil0.txt:1-6
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/d3_transfer_suites_0_2_8239_gil1.txt:1-6
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/d3_scratch_gil0.txt:1-10
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/d3_scratch_gil1.txt:1-10
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_t3_u2_e_0_2_8239_scratch_gil0.txt:1-30
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/probes/probe_transfer_uniques.py:81-149
  IMPACT: The exit evidence for 0.2.8239 is in; the change is two default values and docstrings, so no lock, meld
    path or transfer step changed. The invalidation half (b7, l1, l2) is untouched and waits for the owner's ruling.
  NEXT: Apply apply_d3_0_2_8239.py and tests_d3_0_2_8239.py to the repo, confirm src and the test module match the
    scratch tree byte for byte, then notch 0.2.8239.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T22:40:45Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: 0.2.8239 landed in the repository: apply_d3_0_2_8239.py (conduit 1, ward 2, transfer 4 edits) and
    tests_d3_0_2_8239.py (1) applied with no git lock present, and every .py file under src/ and tests/ is now
    byte-identical to the scratch tree that ran green (diff -rq, generated .meldercache files excluded); then the
    notch script took `__version__` from 0.2.8238 to 0.2.8239, renamed the running note's header, added its section
    "An ownership transfer brings the spell's objects with it by default" (Breaking, the opt-out, m1 and the unchanged
    rest) and rewrote the transfer paragraph of docs/intermediate/ownership.md (CRLF kept, no bare LF). The release
    example runs on the repo's src GIL off and on (the target melds the consumer's tool, closed 0 at the source's
    teardown and once at the target's; `move_creations=False` builds a second one that is never closed). Notch notice
    and board row updated. Slip: one `import melder` from the repo src without the pycache prefix wrote 13 .pyc files
    into src/**/__pycache__ (gitignored, regenerated on any source change; listed in the run folder), reported to the
    owner, not deleted.
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/landing/apply_d3_0_2_8239.py:1-197
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/landing/tests_d3_0_2_8239.py:1-154
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/landing/notch_d3_0_2_8239.py:1-88
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/landing/release_example_d3_0_2_8239.py:1-43
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/release_example_d3_0_2_8239_gil0.txt:1-4
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/release_example_d3_0_2_8239_gil1.txt:1-4
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/pyc_written_by_import_0_2_8239.txt:1-13
  - release_docs/next_version_release.md:256-299
  - docs/intermediate/ownership.md:14-26
  - context_compass/attention_board.md:199-199
  IMPACT: D3's transfer half is done (0.2.8239). Open: the invalidation half (b7, l1, l2) and the interim RISK on
    adopted children, both waiting for the owner's ruling; the end-of-pass promotion and the rebuild follow it.
  NEXT: Update this task's checklist, open questions and handoff summary, write the epic's synthesis note, then ask
    the owner how contract invalidation should treat the consumers it retires.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T23:00:25Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner ruled on contract invalidation (chat 2026-10-14): "no we leave it alone and simply leave it default
    true, its up to the user to break their own shit", then "objects are left as they are the agents can clean them up
    later ... theres nothing wrong with having agents fix the objects that are left pending, this is an agentic
    ecosystem its not a fucken normal program". Invalidation stays as it is: no src change, no further notch. b7 (a
    retired consumer leaves the root's store undisposed) and l1/l2 (a lesser keeps and serves its own consumer) are
    intended behaviour, not defects: objects Melder lets go of stay pending for agents to manage. The disposal rule this
    task opened with was my own paraphrase, never the owner's; it is withdrawn and erased at the owner's direction; the synaptic cleanup rule governs how Melder's own classes tear
    themselves down, not what happens to application objects. The interim RISK of 20:30:57Z closes the same way: an
    invalidated holder's adopted children leave with it.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2682-2740
  - context_compass/tickets/tasks/2026-10-14_investigate_stored_instances_dropped_without_disposal_task.md:26-30
  - context_compass/tickets/tasks/2026-10-14_investigate_stored_instances_dropped_without_disposal_task.md:211-227
  IMPACT: D3 is complete with 0.2.8239 alone; the patch docs' pending invalidation pieces are withdrawn, and the
    epic's exit gate counts b7, l1 and l2 as accepted behaviour.
  NEXT: Wait for the owner's go, then align the epic and patch docs to this ruling and finish the pass (full tree,
    system docs, rebuild) with no behaviour change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T23:27:17Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner accepted D4 as landed (0.2.8238: a holder's disposal-bearing `many` children move with it) and
    directed the transfer documentation (chat 2026-10-14): "people will need to understand that transfer of ownership
    will likely end in a broken state ... you transfer your tools you made over to another agent and they just need to
    register to all the dependencies so they can make their own version while you throw out the trash", then "update
    the documents too properly so you fully understand next time please go ahead and fix what you have to". Scope: the
    `transfer_spell_ownership` docstring (0.2.8240), the docs page and the release note say a transfer hands over
    stewardship, not a working setup, and how the receiver rebuilds; `src_architecture` gains the runtime model
    (correctness lives in the structure; generated objects are working material agents iterate on, leave pending and
    clean up; the infrastructure cleans its own state, not userland objects); then the epic's end-of-pass. D5 stays as
    landed unless the owner says otherwise.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:367-460
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1512-1585
  IMPACT: One more docstring notch in this pass; the system docs record the owner's model so a later agent does not
    re-impose a dispose-everything rule.
  NEXT: Probe the owner's scenario on the repo's src: A transfers a tool to B and tears down, B binds the dependencies
    and builds its own version; record what B sees at each step.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T23:28:48Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The owner's handover scenario, probed on the repo's src (0.2.8239, public API, identical GIL off and on). A
    binds Helper (`unique`), Conn (`many`, disposal) and Tool(helper, conn), melds Tool and transfers it to B with
    the default. h1 (no `include_dependencies`): B melds the moved tool and A no longer can (KeyError "No spell
    found"); A's teardown closes A's Helper (Conn moved with the tool, not closed), so B keeps serving the moved tool
    with a closed helper - the handover starts broken. B purges it (tool and its Conn closed once), and a meld without
    B's own registrations raises UnresolvedInputError naming each missing input ("Tool.helper expects Helper, but
    nothing registered provides it ... or bind a provider for Helper. Also not supplied: 'conn'."); after B binds Helper
    and Conn, its meld builds its own tool with a fresh helper and conn, and B's teardown closes each once. h2
    (`include_dependencies=True`): Helper and Conn move with the tool, A's teardown closes nothing, B keeps a working
    setup, and after a purge B rebuilds from the moved registrations.
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/probes/probe_transfer_handover.py:1-116
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_transfer_handover_0_2_8239_gil0.txt:1-28
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_transfer_handover_0_2_8239_gil1.txt:1-28
  IMPACT: The docs can state exactly what the receiver sees and how it recovers: the moved objects keep working until
    the old owner tears down; then the receiver purges, binds what it needs (the error names it) and melds its own
    version, or the sender passes include_dependencies=True to hand over the direct dependencies too.
  NEXT: Write the transfer docstring paragraph (0.2.8240), the docs page and the release-note addition from this run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T23:30:17Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: 0.2.8240 landed in the repository (docs_d3_0_2_8240.py, no git lock): the `transfer_spell_ownership`
    contract gains the handover paragraph (stewardship, not a working setup; the target can start out broken once this
    conduit tears down; it purges, binds what it needs - `UnresolvedInputError` names each missing input - and melds
    its own version) and `include_dependencies` says it moves the direct dependencies this conduit owns; `__version__`
    0.2.8239 -> 0.2.8240; the release note's transfer section and the ownership guide carry the same paragraph (CRLF
    kept, no bare LF). Docstring and docs only; no code path changed. The scratch tree was re-synced from the repo with
    rsync (caches excluded) and diff -rq finds no difference in src/ or tests/.
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/landing/docs_d3_0_2_8240.py:1-81
  - src/melder/aether/conduit/conduit.py:4241-4252
  - release_docs/next_version_release.md:291-297
  - docs/intermediate/ownership.md:28-36
  IMPACT: The transfer docs now match the owner's model and the probed behaviour; the pass's validation runs on a tree
    identical to the repository.
  NEXT: Run the full test tree on the scratch tree, GIL off then on, and record the counts.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T00:07:24Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Status to review. The audit probe at 0.2.8240 shows t3 moved by default (the holder in the target store, the
    target melding the same holder, closed once at the end) and b7 as the owner ruled it (the retired consumer is not
    disposed); the full tree is green GIL off and on; the system docs carry the transfer invariant, the handover
    sequence step, the two transfer failure modes and the runtime model that states the invalidation ruling.
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_lifetime_owners_all_0_2_8240_gil0.txt:23-29
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_lifetime_owners_all_0_2_8240_gil0.txt:59-67
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/full_tree_0_2_8240_gil0.txt:1-28
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/full_tree_0_2_8240_gil1.txt:1-20
  - context_compass/system_docs/src_architecture.md:522-548
  - context_compass/system_docs/src_architecture.md:826-842
  - context_compass/system_docs/src_architecture.md:959-973
  - context_compass/system_docs/src_architecture.md:1764-1774
  IMPACT: D3 waits only for the owner's acceptance; closure goes with the epic.
  NEXT: The owner accepts or redirects; then close with the epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
In review (2026-10-15). D3 is the transfer default: `transfer_spell_ownership` defaults to `move_creations=True`
(0.2.8239), so a transferred `unique` stays one object and the source's objects follow the spell; a transfer
disposes nothing; `move_creations=False` and a move into a filled slot (m1) are documented, not changed; the
docstring, the ownership guide and the release note say a transfer hands over stewardship, not a working setup
(0.2.8240; probe h1 and h2). Contract invalidation stays as it is by the owner's ruling (b7, l1, l2 intended).
Validated with the epic's pass; promoted into the system docs. Remaining: the owner's acceptance; commit and push
are the owner's.

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
