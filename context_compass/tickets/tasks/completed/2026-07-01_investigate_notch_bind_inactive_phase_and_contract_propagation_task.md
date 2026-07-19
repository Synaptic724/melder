

# Task: Investigate bind_inactive/notch phase gap and index-contract propagation

- Completed: 2026-07-01T22:42:59Z
- Summary: Root-caused the 10 last-failed tests (M1-M5 notch/meld disarm, C1-C3 contract
  bookkeeping, D1-D3 drift, B scan). Landed the user-directed notch transaction-commit
  mirror of bind (strategy stages the promoted member's binding key; structural commit
  validator participation {BIND, NOTCH} with a durable phase-5-blueprint filter; seam is
  swap-only with bind-parity flags + gated per-conduit verdicts), the end_transaction
  nested-clear fix (scan staged-set collapse), and the phase5-root artifact-None guard.
  User-run 3.14t: lane fully green; remaining 2 failures ticketed to fable_0
  (config-flag required-property regression). Status: done, user-accepted.


## Metadata
- Task ID: TASK-2026-07-01-investigate-notch-bind-inactive-phase-and-contract-propagation
- Story: none (standalone investigation task)
- Status: done
- Owner: cowork
- Agent Name: melder_0
- Priority: p1
- Created: 2026-07-01T21:33:58Z
- Updated: 2026-07-01T21:33:58Z

## Objective
Produce an evidence-backed root-cause map (no fixes) for two suspected defect clusters:
1) inactive-bind/notch activation does not run the same phase set (1-7, plus meld revalidation
   arming) that active bind's transaction commit performs in dynamic mode post-conjure;
2) index-contract propagation on remove-from-index and notch may not reduce/update borrower
   contracts correctly. Map the 10 currently failing tests onto these clusters or classify them
   as test drift.

## Ticket Contract
- ENTRY_GATE: this ticket routed from attention_board.md active row (melder_0); user directive
  2026-07-01 (investigate only, no fixes).
- EXECUTION_BOUNDARY: read-only investigation. Files: spellbook.py, bind.py, scan.py, spell.py,
  conduit.py, conduit_ward.py, meld.py, conduit_meld.py, spell_compiler_system.py,
  notch/bind/add_to_index/remove_from_index transaction strategies, failing tests, and recent
  tickets/notes from mediator_builder_0, general_0, codex_0. No src or test edits.
- DEPENDENCIES: tickets/epics/2026-06-30_index_link_contract_epic.md;
  tickets/epics/2026-06-14_spellindex_genuine_index_operations_epic.md;
  tickets/tasks/2026-07-01_investigate_conduit_scan_phase4_validation_gap_task.md (codex_0,
  overlapping scan/phase-4 gap - coordinate, do not duplicate).
- EXIT_GATE: notes contain evidenced root-cause claims (or explicit UNKNOWNs) for each failure
  cluster plus a proposed solution outline awaiting user decision.
- FAILURE_ESCALATION: CONFLICT note if source contradicts the epics' landed models; BLOCKER if
  required evidence is unreachable.

## Scope Boundaries
- In scope: root-cause mapping of the 10 last-failed tests; bind vs bind_inactive vs notch
  phase/revalidation behavior; index-contract add/remove/notch propagation via ConduitWard.
- Out of scope: any code or test fix; doc patches; new tests.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user directed immediate investigation after certification.

## Steps / Checklist
- [ ] Read recent notes from mediator_builder_0 / general_0 / codex_0 lanes for landed changes.
- [ ] Trace bind (dynamic, post-conjure) transaction commit: which phases run, what arms meld
      revalidation.
- [ ] Trace bind_inactive and notch commit paths; diff against active-bind behavior.
- [ ] Trace index-contract propagation: add_spell_to_contract (index), remove_from_index, notch,
      and guard errors on member uncontract.
- [ ] Map each of the 10 failing tests to a cluster (product defect vs test drift).
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document` (implement/validate out of scope).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Evidence-backed root-cause map in `## Notes` + summary for user decision.

## Files / Paths Impacted
- None (read-only investigation).

## Validation
- Not run.
- Recommended commands:
  - `pytest tests --last-failed -q` (user-run, 3.14t)

## Risks / Rollback Notes
- Read-only; no rollback surface. Risk: stale conclusions if other agents land further changes
  mid-investigation.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-07-01T21:33:58Z
  TYPE: DECISION
  CLAIM: Investigation scope spans >5 files (spellbook/bind/scan/spell/conduit/ward/meld/
    strategies/compiler_system + tests). Expansion gate satisfied by explicit user directive
    naming these subsystems; treating scope as user-approved.
  EVIDENCE:
  - codex/context_compass/config/context_compass_config.yaml:95-95
  IMPACT: Allows multi-file trace without a second confirmation round-trip.
  NEXT: Read recent lane notes from general_0/mediator_builder_0/codex_0 tickets.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-07-01T21:33:58Z
  TYPE: FACT
  CLAIM: User-run 3.14t last-failed pass shows 10 failures in 4 apparent clusters:
    (A) notch-activated spell cannot meld - CreationContextBuilder.build raises
    "Cannot build CreationContext before spell_codegen_creation exists" (3 tests);
    (B) post-conjure scan-bound spells have validation_result_phase4 None (2 tests, overlaps
    codex_0 lane); (C) contracted-spell removal bookkeeping raises
    "Contracted spell_id not found for removal" via _unregister_contracted_spell_id (1 test)
    plus 2 unit tests hitting new `idx._cleaned` direct access on Dummy indexes (test drift
    suspected); (D) one mediator-mock unit test missing new get_session_for_identity (test
    drift suspected) and one experimentation test where _get_resolution_validity dereferences
    spell._compiler_artifact when None.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:51-51
  - src/melder/aether/spellbook/spellbook.py:2767-2767
  - src/melder/aether/spellbook/spellbook.py:2808-2808
  - src/melder/aether/spellbook/spellbook.py:3606-3606
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:656-656
  IMPACT: Clusters A/B match the user's phase-gap hypothesis; C matches the contract-propagation
    hypothesis; D is likely test/mocks drift but needs source confirmation.
  NEXT: Read general_0's index_link_contract epic notes for the landed contract model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-01T21:38:00Z
  TYPE: FACT
  CLAIM: Consumed prior-lane truth. general_0's index_link_contract epic documents the landed
    contract model (index_id-keyed IndexDetail, per-member spell Details, notch fan-out via
    _emit_index_notch, member_added/removed emission both sides, removal/add guards via
    _find_governing_index_link). codex_0's scan lane already root-caused cluster B: nested
    Spellbook.begin_transaction(BIND) unconditionally ran _prepare_bind_transaction_state(),
    clearing _pending_structural_spells, so commit-time structural validation only covered the
    last staged spell; codex_0 landed an outermost-only fix (spellbook.py:3531-3546 region,
    adds mediator.get_session_for_identity call at ~:3606) but pytest validation was blocked at
    collection by an unrelated NameError in frame_descriptor.py:153.
  EVIDENCE:
  - codex/context_compass/tickets/epics/2026-06-30_index_link_contract_epic.md:227-328
  - codex/context_compass/tickets/tasks/2026-07-01_investigate_conduit_scan_phase4_validation_gap_task.md:156-193
  IMPACT: Cluster B ownership stays with codex_0; user's still-failing scan tests mean their fix
    is incomplete or the staged-set collapse persists - verify current source. Unit-test mediator
    mock lacking get_session_for_identity (spellbook.py:3606) is drift from codex_0's fix.
  NEXT: Read _apply_notch/_bind_inactive/phase-runner source (done in same pass; note follows).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-01T21:38:00Z
  TYPE: FACT
  CLAIM: Notch/bind_inactive phase model as implemented. _bind_inactive (spellbook.py:4028-4198)
    stages the spell inside a self-opened bind window but stages NO binding key and runs NO
    phases (deliberate: spell is inert/unmeldable until notch). _apply_notch
    (spellbook.py:3064-3165) after the swap: register_index -> gated+dirty;
    invalidate_spell(change_reason) (comment: also sets resolution_required=True); then ONLY IF
    validation_result_phase4 is None OR validation_result_phase6 is None runs
    _run_post_conjure_structural_phases([spell]) (phases 1-4) and sets
    resolution_required=False. A notch-back member (both results non-None from conjure) skips
    that branch entirely - "left on the lazy resolution path". Phases 5-11 are NEVER run
    eagerly by notch; the design bet is meld-time lazy revalidation finishes 5-11.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4094-4194
  - src/melder/aether/spellbook/spellbook.py:3107-3165
  - src/melder/aether/spellbook/spellbook.py:5398-5421
  IMPACT: The 3 failing notch tests die at meld -> CreationContextBuilder.build with
    _spell_codegen_creation None, i.e. the lazy 5-11 rerun did NOT trigger for the notched-back
    spell even though notch relies on it. Root-cause candidates: (a) meld's
    _get_resolution_validity returns a stale valid for the re-activated id; (b) whatever
    cleaned the phase-11 payload (deactivation/invalidate) does not also flip the per-conduit
    resolution validity that meld checks.
  NEXT: Read Spell.invalidate_spell/_cleanup_creation_context, then meld.py validity gates
    (_ensure_resolution_resolvable/_get_resolution_validity) to find which gate lets the stale
    spell through.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-01T21:47:00Z
  TYPE: FACT
  CLAIM: Meld rebuild-lane topology (the crux). ConduitMeld.meld gates ALL lazy compile work
    behind two flags: (1) `if self._spellbook._spellbook_validation_requ