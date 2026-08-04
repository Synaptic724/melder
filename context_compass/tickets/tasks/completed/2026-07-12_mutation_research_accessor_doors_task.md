

- Completed: 2026-07-12T11:05:00Z
- Summary: Owner-directed turn-in. Both borrowed MR accessor doors landed
  (Spellbook + Conduit: init bind, world-scoped read-only property, cleanup
  del + tombstone parity), conduit NOTE reversal recorded, 7-row component
  suite committed, C-docs synced. Validation rides the owner's in-flight
  3.14t tree run (agent status: Not run.). Graph edges (2 borrows) remain
  promotion debt for the next graph pass.

# Task: Add borrowed MutationResearch accessor doors to Spellbook and Conduit

## Metadata
- Task ID: TASK-2026-07-12-mutation-research-accessor-doors
- Story: none (standalone task)
- Status: done
- Owner: cowork
- Agent Name: mutation_0
- Priority: p2
- Created: 2026-07-12T08:50:49Z
- Updated: 2026-07-12T11:05:00Z

## Objective
Spellbook and Conduit each bind the Aether-hosted MutationResearch world root at init
(mirroring the `_crystallizer` pattern), expose it through one read-only public property,
and tear the reference down deterministically in cleanup. No verb forwarding, no new MR
behavior - the door returns the object, that is it.

## Ticket Contract
- ENTRY_GATE: active board row routes here; patch artifacts exist and are linked below;
  owner has explicitly confirmed the edit plan (Propose -> Confirm -> Implement).
- EXECUTION_BOUNDARY: `src/melder/aether/spellbook/spellbook.py`,
  `src/melder/aether/conduit/conduit.py`, new unit test file(s) under
  `tests/unit/melder/`, plus doc sync targets named in Files / Paths Impacted.
- DEPENDENCIES: owner ruling 2026-07-12 (this lane) reversing the 2026-07-06
  "conduits/frames carry no mutation dimension" ruling for conduit/spellbook only;
  frames remain out of the MR model.
- EXIT_GATE: both doors implemented with rank-5 docstrings; cleanup del in both
  teardown paths; unit tests written; owner runs the tree (agent reports "Not run.");
  doc sync deltas applied; owner acceptance walk.
- FAILURE_ESCALATION: DECISION_REQUEST if the eager-construction behavior deltas
  (R1/R2 in Notes) are unacceptable; BLOCKER if implementation reveals an
  unexpected lifecycle interaction with the restore engine or record seams.

## Scope Boundaries
- In scope:
  - `_mutation_research` slot + init binding + public property + cleanup on Spellbook.
  - Same four deltas on Conduit (binding borrowed from the owning Spellbook).
  - Update (never delete) the conduit.py:2947 deleted-door NOTE to record the reversal.
  - Unit tests for binding identity, lesser-conduit inheritance, cleanup, and the
    cleaned-root failure mode.
  - Doc sync: src_components.md + src_architecture.md lines that document the door
    as deleted / the no-mutation-dimension contract.
- Out of scope:
  - Frames (AethericFrame carries no MR dimension - ruling unchanged).
  - Any MR verb forwarding on the doors (rooms remain the mediated agent surface).
  - Refactoring the existing `_record_research_world_entry` /
    `_record_research_promotion` seams (they keep the non-constructing peek).
  - Graph regeneration (recorded as promotion debt at closure, melder_0 precedent).

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Owner confirmed the plan ("yeah implement it go ahead");
  both doors + component tests + C-doc sync implemented and committed; validation
  awaits the owner tree run (agent: "Not run.").

## Steps / Checklist
- [x] Owner confirms the edit plan (files/symbols below).
- [x] Implement Spellbook deltas (slot, TYPE_CHECKING import, init bind, property,
      cleanup del + tombstone parity).
- [x] Implement Conduit deltas (slot, TYPE_CHECKING import, init bind from spellbook,
      property at the old door site, cleanup del).
- [x] Update conduit.py deleted-door NOTE to record the 2026-07-12 reversal.
- [x] Write unit tests (contract rows in Validation).
- [x] Sync src_components.md / src_architecture.md deltas.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Two borrowed accessor doors (Spellbook.mutation_research, Conduit.mutation_research).
- Deterministic cleanup of both references.
- Unit test coverage for the new contract.
- Synced canonical docs + updated source NOTE.

## Files / Paths Impacted
- src/melder/aether/spellbook/spellbook.py
- src/melder/aether/conduit/conduit.py
- tests/unit/melder/ (new test file; exact placement resolved at implementation)
- codex/context_compass/system_docs/src_components.md
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/patches/active/mutation_research_accessor_doors_2026_07_12/

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder -q
  - pytest -q (owner full-tree run on 3.14t)
- Test contract rows (unit, pytest):
  - spellbook.mutation_research is Aether().mutation_research (identity).
  - conduit.mutation_research is spellbook.mutation_research (identity via conjure).
  - lesser conduit shares the same root object.
  - binding never activates the root (activated stays False; no journal entries).
  - post-cleanup property access raises via check_cleaned (spellbook and conduit).
  - MR root cleaned + live Aether -> Spellbook() raises RuntimeError (aether contract).

## Risks / Rollback Notes
- R1: eager binding constructs the (inactive) MR root in every world that creates a
  Spellbook; previously it was built only on first `Aether().mutation_research` touch.
  Cost is one thin registry object + one-time import chain at first Spellbook init.
- R2: NEW failure mode - a cleaned MR root with a live Aether makes every subsequent
  Spellbook() raise RuntimeError (aether.py:1602-1612 "cleanup never silently
  re-creates"). Fail-fast is contract-correct; owner accepts via plan confirm.
- Rollback: revert the two source files + tests; docs revert with them. No persisted
  state or record shape changes (crystallizer/MR record models untouched).

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No drive-by refactor of the record seams or frame surfaces while in the files.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/mutation_research_accessor_doors_2026_07_12/architecture_patch.md
  - system_docs/patches/active/mutation_research_accessor_doors_2026_07_12/component_patch_spellbook_and_conduit.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: durable deltas merged into canonical C-docs at ticket closure;
  patch dir then moves to patches/completed per the closure gates.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-07-12T08:50:49Z
  TYPE: FACT
  CLAIM: The crystallizer precedent on both units is a PRIVATE emit reference, not a
    public door; every use site is an emit verb and there is no public accessor.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:230-230
  - src/melder/aether/spellbook/spellbook.py:452-452
  - src/melder/aether/spellbook/spellbook.py:641-641
  - src/melder/aether/conduit/conduit.py:248-248
  - src/melder/aether/conduit/conduit.py:794-794
  IMPACT: The requested doors are crystallizer-parity binding/cleanup PLUS one public
    property delta; the property is what delivers "easily accessed".
  NEXT: Owner confirms property inclusion in the plan confirm.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-12T08:50:49Z
  TYPE: FACT
  CLAIM: Aether.mutation_research lazily constructs the root under the singleton lock
    and RAISES for a cleaned root ("cleanup never silently re-creates"); Spellbook
    reaches Aether via the class-level `Spellbook._aether` ClassVar.
  EVIDENCE:
  - src/melder/aether/aether.py:553-562
  - src/melder/aether/aether.py:1577-1614
  - src/melder/aether/spellbook/spellbook.py:118-118
  IMPACT: Eager init binding adds construct-at-first-Spellbook behavior (R1) and the
    cleaned-root RuntimeError at Spellbook construction (R2).
  NEXT: Surface R1/R2 in the owner plan confirm.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-12T08:50:49Z
  TYPE: DECISION
  CLAIM: Owner ruled 2026-07-12 (session) to reverse the 2026-07-06 no-door ruling for
    Spellbook and Conduit only: bind the world root at init like crystallizer, expose
    a get-the-object accessor, del on cleanup. Frames stay out of the MR model.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2947-2950
  - codex/context_compass/system_docs/src_components.md:597-599
  IMPACT: Documented component contract flips; canonical docs and the source NOTE must
    be synced in the same lane (staleness protocol).
  NEXT: Implement after owner confirms exact file/symbol plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-12T08:50:49Z
  TYPE: PLAN
  CLAIM: Exact edit plan - spellbook.py: `_mutation_research` slot beside
    `_crystallizer` (:160), TYPE_CHECKING MutationResearch import (:50 block), init
    bind `Spellbook._aether.mutation_research` after crystallizer bind (:230), public
    `mutation_research` property, `del` in _cleanup_components (:452 block) and `=
    None` tombstone in _cleanup_core (:641 block, mirroring crystallizer exactly);
    conduit.py: slot (:150), TYPE_CHECKING import (:66 block), init bind from
    `spellbook._mutation_research` (:248), property at the old door site (:2947),
    `del` in cleanup (:794). Seams untouched.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:155-161
  - src/melder/aether/conduit/conduit.py:145-151
  IMPACT: Smallest diff that satisfies the ruling; all other MR wiring unchanged.
  NEXT: Post plan to owner; implement on explicit confirm.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-12T09:35:00Z
  TYPE: FACT
  CLAIM: Implementation landed - both doors, tests, NOTE reversal, C-doc sync.
    Spellbook: slot :162, bind :238 (from `Spellbook._aether.mutation_research`),
    del :461, tombstone :651, property :5441-5469. Conduit: slot :152, bind :254
    (from spellbook), del :801, updated NOTE + property :2954-2991. Tests: 7
    component rows. Both files py_compile clean; CRLF convention preserved.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:238-238
  - src/melder/aether/conduit/conduit.py:254-254
  - tests/component/melder/aether/conduit/test_mutation_research_accessor_doors.py:1-160
  IMPACT: The owner-ruled reversal is code-real; tests target the exact contract.
  NEXT: Owner runs the 3.14t tree; on green, closure walk + graph promotion debt.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-12T09:35:00Z
  TYPE: RISK
  CLAIM: The device bridge served stale read replicas for re-staged files this
    session (writes ACK + disk stat shows post-edit sizes, content reads show
    pre-edit snapshots) - the recorded "replica rot" class. Write verification in
    this lane is therefore STAT-BASED (exact byte-size match to edited copies):
    spellbook 254903, conduit 238285, mailbox 10099 all match; board disk size
    23361 = my 21976 + concurrent agent traffic (row presence unverifiable by
    content read this session).
  EVIDENCE:
  - codex/context_compass/mailbox_board.md:120-131
  IMPACT: Content-read verification is unreliable until the bridge session
    resets; future same-session edits must merge from first-time stages only.
  NEXT: Owner git-diff confirms disk truth whenever convenient.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-12T09:35:00Z
  TYPE: MEASURE
  CLAIM: Validation status: Not run. Tests exist but were not executed by the
    agent; coverage not measured, not estimated.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_mutation_research_accessor_doors.py:70-160
  IMPACT: EXIT_GATE requires the owner run before closure.
  NEXT: Owner runs pytest on the 3.14t tree (component tests included).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Implemented and committed 2026-07-12: both accessor doors (spellbook.py, conduit.py),
7-row component test suite, conduit NOTE reversal, and C-doc sync (src_components.md,
src_architecture.md). Validation: Not run. - awaiting the owner 3.14t tree run. On
green: closure walk, patch-dir promotion to completed, board sync, and record the
readable-graph edges (2 borrows) as promotion debt. Session caveat: bridge content
reads were stale-replica this session; disk truth verified by stat byte-match.
