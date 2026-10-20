# Story: failed_notch_keeps_switch_without_borrowers - a notch that fails its commit leaves no half-made switch

- Completed: 2026-10-19T13:24:30Z
- Summary: landed and notched 0.2.8262 - a notch whose incoming version fails its structural check is refused with
  nothing moved: `Spellbook._notch_spell` checks the version inside the notch window and, when the check
  fails, puts the structure back before it raises, so the lender and its borrowers stay on the outgoing
  version, which is left gated for revalidation; `SpellbookValidationError` takes a one-line `preface`. 25
  tests green with the GIL off and on, the whole tree as the MEASURE note records; release-note section "A
  notch whose new version fails its check is refused, and nothing moves"; system documents and graph; the
  rebuild comes last in this pass. Turned in on the owner's word (chat 2026-10-19: "turn in tickets that you
  can").

## Metadata
- Story ID: STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers
- Epic: EPIC-2026-10-17-correctness_defects
- Status: done
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-17T21:32:09Z
- Updated: 2026-10-19T13:24:30Z

## User Narrative
As an agent notching to a version I staged, I want a notch that raises to leave the structure the way the exception
says it is - the lender and every borrower on one version - so that a failed notch never leaves the lender on the
new version and its borrowers on the old one.

## Value / MRP Alignment
Which version an index selects, and that its borrowers follow a notch, are structure (owner rulings: a notch only
moves which version is active; borrowers follow). Today a notch whose commit validation fails raises
SpellbookValidationError after the switch was made and before the borrowers were told: the lender's index selects
the broken version, the borrowers keep the old one, and the lender can meld neither by address nor the old version
by its spell_id until someone notches back. The structure is wrong after an operation that reported failure.

## Ticket Contract
- ENTRY_GATE: the owner schedules the story and assigns an agent (the open question was answered on 2026-10-17;
  scheduled 2026-10-18, melder_1 assigned - DECISION note); conduit.py and spellbook.py are free since melder_1's
  turn-in (M1-28) and melder_0 writes the identity epic's files, so melder_1 claims each file it edits from
  melder_0 by message first; an active board row; patch docs for the notch's commit path (architecture,
  component and code-description: the change is in error and rollback semantics), approved by the owner.
- EXECUTION_BOUNDARY: `Conduit.notch_spell` (its commit) and what the refusal needs around the seam - a structural
  check of the incoming version before `_apply_notch` runs, or rollback actions that undo the seam when the commit
  fails (the patch picks); the stale docstring of `_stage_spell_for_structural_phases` (FACT note); regression
  tests; the system documents (the SpellIndex Mutation Entry sequence, a failure mode) with their indexes and the
  graph; the release note; one notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probe and its runs (Artifact Links);
  TASK-2026-10-16-notch_seam_checks_incoming_before_parking (the seam's own failure, inside the window);
  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (the frame claim an undo must give back).
- EXIT_GATE: probe N2 ends with the lender and its borrower on English, the staged version still parked, and the
  exception saying the notch did not happen; N1 unchanged and N3 ending as today, English on both sides; regression
  tests pass with the GIL off and on; docs, notch and the rebuild with both checks OK.
- FAILURE_ESCALATION: CONFLICT while conduit.py or spellbook.py is held, or if the seam task lands first with another
  order of checks.

## Requirements (Functional)
- A notch whose incoming version fails its structural check is refused with nothing moved (owner, 2026-10-17): the
  index still selects the outgoing version, the incoming one stays parked, the frame claim and the Nexus record name
  the outgoing version, the lender melds it by address and by spell_id, and the borrowers are untouched.
- The error says the notch did not happen, names the broken version with its validation errors, and says the
  outgoing version is still active.

## Requirements (Non-Functional)
- No new lock or lock-order edge; the warm meld path untouched. A notch whose commit succeeds pays nothing new
  beyond the refusal's check, which runs only for a version never compiled - the case the commit validator already
  compiles today.

## Scope Boundaries
- In scope: a notch whose transaction commit raises (phases 1-4 of a never-compiled incoming version failing in the
  change-control structural validator).
- Out of scope: a seam that raises inside the window (TASK-2026-10-16-notch_seam_checks_incoming_before_parking);
  melds in flight while a notch fans out (TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout); a
  bind whose commit fails (the same validator; not probed here).

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: landed at 0.2.8262 and turned in on the owner's word (chat 2026-10-19: "Yes do s8", then "turn
  in tickets that you can"; DECISION notes). Before that, blocked -> in_progress: the owner asked for proof that
  the half-switch happens (chat 2026-10-19; DECISION note of
  10:34:26Z), saw it (MEASURE notes) and gave the go for the fix: "it should roll back properly" (DECISION note of
  2026-10-19T11:07:22Z). Earlier: in_progress -> blocked on his hold (chat 2026-10-18: "Hold" on the edit list and its
  refinement; DECISION note). Before that: ready -> in_progress when he scheduled the story and assigned melder_1
  (DECISION note of 2026-10-18T12:30:17Z).

## Dependencies / Related Work
- TASK-2026-10-16-notch_seam_checks_incoming_before_parking (backlog): the same seam; a check moved ahead of the park
  there and a structural check ahead of the switch here would sit side by side.
- STORY-2026-10-17-notch_moves_signature_by_incoming_key_only: the seam's frame-claim step, which an undo reverses.

## Tasks (Implementation Checklist)
- [x] Task: the owner's answer on the open question (2026-10-17: refuse with nothing moved; DECISION note).
- [x] Task: patch docs for the notch's commit path; the owner's approval (2026-10-18; DECISION note).
- [x] Task: the fix with symptom-named regression tests (red on 0.2.8260, green at 0.2.8262; MEASURE notes), docs,
  notch and the rebuild last (the rebuild follows the closures of this pass, as the contribution guide orders).
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- With English active, a borrower index-linked to its index and a staged version whose structure is broken (a
  constructor that takes its own class): `notch_spell` to it raises, and afterwards the lender's index and the
  borrower both select English, the broken version is still parked, and the lender melds English by address and by
  its spell_id.
- A notch to a sound version (N1) behaves as today; after the refused notch a notch to English (N3) changes nothing.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_a_notch_refused_at_commit_leaves_the_old_version_active` and
  `test_a_notch_refused_at_commit_leaves_borrowers_on_the_lenders_version`; GIL off and on; the probe re-run. Run
  at the fix: 25 tests green with the GIL off and on and the probes re-run (MEASURE notes of 2026-10-19).

## UX / API / Data Notes
- Visible today: `notch_spell` raises SpellbookValidationError "Spellbook validation failed. Broken spells: <name>.",
  then the lender's `meld(spellframe=..., binding_name=...)` raises the same error and `meld(spell_id=<old>)` raises
  KeyError "[MELD] No spell found with spell_id: ..." while the borrower holds the old version active. After the fix
  the exception keeps its meaning - nothing moved - and the world keeps working.

## Risks / Mitigations
- An undo after the seam must reverse every step `_apply_notch` takes (park, promote, index pointer, frame claim,
  lineage registration and verdicts, Nexus record); a check before the seam needs none, but must run phases 1-4 on a
  version that is still parked - UNKNOWN until the patch reads the phase runner for a parked spell.
- The seam journals the promotion and emits the index crystal inside the window; under the refusal the research
  journal and the record must not keep a promotion that did not happen (a check before the switch writes none; an
  undo must reverse or supersede them).

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- When a notch's commit validation fails, should the notch (a) be refused with nothing moved - the incoming version
  checked before the switch, or the switch undone; the patch picks the mechanism - so the error means it did not
  happen (recommended: the structural validator fails "instead of accepting a broken staged mutation", and
  notch_spell's other refusals change nothing), or (b) stand, with the borrowers moved to the broken version before
  the error propagates?
  Answered (owner, 2026-10-17T22:12:58Z): (a) - "Yeah sure you can refuse it and throw and move on if you mean
  it couldn't notch"; it is that case: the incoming version failed its check, so the notch could not happen
  (DECISION note).

## Decision Log
- 2026-10-17T21:32:09Z: filed under EPIC-2026-10-17-correctness_defects from sweep A9 (Notes).
- 2026-10-17T22:12:58Z: the owner answered the open question - (a): refuse with nothing moved (DECISION note).
- 2026-10-18: the patch docs approved by the owner, then his hold on the edit list (DECISION notes).
- 2026-10-19T11:07:22Z: the owner's go - "it should roll back properly" (DECISION note).
- 2026-10-19T12:46:57Z: the owner's "Yes do s8" - land S8 on S3's tree, then turn it in (DECISION note).
- 2026-10-19T13:24:30Z: landed at 0.2.8262 and turned in (MEASURE and FACT notes).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/correctness_defects_20261017/probes/probe_failed_notch_commit.py (cases N1-N3)
  - artifacts/correctness_defects_20261017/runs/probe_failed_notch_commit_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_failed_notch_commit_gil1.txt
  - artifacts/correctness_defects_20261017/probes/probe_broken_late_bind.py (cases B2-B3: the bind precedent; FACT note)
  - artifacts/correctness_defects_20261017/runs/probe_broken_late_bind_gil0.txt
  - artifacts/correctness_defects_20261017/runs/probe_broken_late_bind_gil1.txt
  - artifacts/failed_notch_refusal_20261018/ (melder_1's lane: re-runs, scripts, notes)
  - system_docs/patches/completed/failed_notch_refusal_2026_10_18/ (architecture, 2 component, code-description;
    promoted at landing, archived at turn-in)
- DISPOSITION: retain_as_reference (the probes, their runs and the lane folder); promote_to_documentation (the
  patch)
- CLEANUP_TRIGGER: the probe was re-run at the fix and is kept as the defect's reproducer

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - a notch whose transaction commit fails after its seam ran
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose and evidence (the probe); filed 2026-10-17T21:32:09Z.
- Contributions: melder_1 (synaptic_python_developer) - the re-verification on 0.2.8255, the patch docs
  failed_notch_refusal_2026_10_18, the red tests and their runs (2026-10-18; Notes); the rollback in
  spellbook.py, the error's preface, the docstrings, the system documents, the graph prose and the release note
  (2026-10-19; Notes).
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none (self-checks only; closure on the owner's word, chat 2026-10-19)

## Notes
- DATETIME: 2026-10-17T21:32:09Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The defect, read whole and proven on 0.2.8252. `Conduit.notch_spell` runs the seam inside its transaction
    (`_notch_spell` -> `_apply_notch`: park the outgoing version and clean its creation context, promote the incoming
    one, repoint the index and the frame claim, emit the index crystal, journal the promotion, re-register the lineage
    gated, mark its dependents, publish the incoming version to Nexus, gate its verdicts), then calls
    `end_transaction(success=True)` outside its `try`. The commit runs the change-control commit validator: for a
    notch to a version never compiled, phases 1-4 (`_default_structural_validator`, which fails "instead of accepting
    a broken staged mutation"). When they fail, the orchestrator's abort hook is unset, the session holds no abort
    hook or rollback action (no caller of `register_rollback_action`, `register_abort_hook` or
    `ChangeControlManager.set_abort_hook` exists in src/melder), and the mediator re-raises: every change of the seam
    stays, and `notch_spell` exits before its borrower fan-out (`_deactivate_borrowed_spell`,
    `_activate_borrowed_spell`, `_emit_index_notch`). Probe N2 (English active, an index-linked borrower, SelfMade
    staged with a constructor that takes its own class): `notch_spell` raises SpellbookValidationError "Broken
    spells: SelfMade.", yet the lender's index selects SelfMade, active, with English parked; the borrower holds
    English active and SelfMade parked; the lender's meld by address raises that error and `meld(spell_id=English)`
    KeyError. N3: a notch back to English restores both sides. N1 (a sound version): owner and borrower follow.
    Identical with the GIL off and on.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5622-5759
  - src/melder/aether/spellbook/spellbook.py:3851-3904
  - src/melder/aether/spellbook/spellbook.py:3906-4061
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:1043-1091
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/orchestrator/orchestrator.py:452-530
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:562-586
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:614-641
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:783-835
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_session.py:463-526
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_failed_notch_commit.py:1-171
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_failed_notch_commit_gil0.txt:1-34
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_failed_notch_commit_gil1.txt:1-34
  IMPACT: After an operation that reported failure the lender selects the new version and its borrowers the old one,
    against "borrowers follow", and the lender cannot meld the index by address until a notch back.
  NEXT: The owner's answer on the open question, then patch docs for the notch's commit path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T21:41:15Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Evidence for the open question (sweep A11, probe B2-B3). A late `bind` whose commit validation fails keeps
    its spell registered and active with every meld refused - documented ("refused at that bind and at its melds",
    0.2.8224) - so option (b) has a precedent in bind. The difference: a failed late bind displaces nothing, while a
    failed notch displaces the working version (probe N2: the lender cannot meld the index by address afterwards),
    which is why (a) stays recommended. Whichever answer lands, `_stage_spell_for_structural_phases`'s docstring
    ("Notch does NOT stage ... runs the structural phases directly via `_run_post_conjure_structural_phases`") is
    stale: the validator runs phases 1-4 for a notch at its commit (its docstring, `_notch_spell`'s comment, probe
    N2), and the fix should correct it.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4937-4958
  - src/melder/aether/spellbook/spellbook.py:3851-3904
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:783-835
  - context_compass/system_docs/src_architecture.md:2490-2502
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_broken_late_bind_gil0.txt:9-37
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_failed_notch_commit_gil0.txt:10-18
  IMPACT: The owner has both precedents in front of him; the fix lane has one more line to correct.
  NEXT: The owner's answer on the open question.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-17T22:12:58Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The open question is answered (owner, chat 2026-10-17): "notch fails its commit validation, not sure what
    this means commit to the new spell? Yeah sure you can refuse it and throw and move on if you mean it couldn't
    notch that makes sense". It is that case: when a notch's transaction ends, Melder checks the incoming version's
    structure (phases 1-4, run only for a version never compiled), and a version that fails is broken, so the notch
    could not happen. The story takes answer (a): the notch is refused with nothing moved - the lender and every
    borrower stay on the outgoing version, the incoming one stays parked - and the error says so. Option (b) is out;
    the patch picks the mechanism (a check before the switch, or an undo of the seam). melder_0 confirms that meaning
    to the owner with probe N2 in the same reply; his word can still override.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:114-121
  - src/melder/aether/conduit/conduit.py:5622-5759
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:783-835
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_failed_notch_commit_gil0.txt:10-19
  IMPACT: The ENTRY_GATE's question is met; the requirements, acceptance and exit gate narrow to the refusal.
  NEXT: The owner's scheduling, after melder_1 releases conduit.py and spellbook.py; then patch docs for the notch's
    commit path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T12:30:17Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner scheduled this story (chat 2026-10-18). Asked the order between
    EPIC-2026-10-18-spell_identity_is_the_code and the correctness epic's ready stories, he chose "Parallel
    (Recommended)": melder_0 keeps the identity epic; melder_1 takes S8, S3, S9, S4 and S7 one at a time and claims
    spellbook.py by mailbox for each landing; S1, S2 and S5 wait for the identity epic. Then: "you can try and take
    on melder_0s stuff that we fully confirmed but go over them again before you make changes and let him know".
    This story goes first: of the five it is the one whose question the owner answered (refuse, nothing moved). It
    is re-verified on the current tree, and its commit path re-read whole, before any change; melder_0 is told
    (M1-30). The owner also confirmed this session is the only melder_1.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:895-928
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:345-355
  IMPACT: The ENTRY_GATE's scheduling and assignment are met. S3 carries an open question for the owner; S9, S4 and
    S7 carry none and no recorded confirmation, so each is re-verified, and confirmed with the owner, before it is
    taken.
  NEXT: Re-run probe N1-N3 on 0.2.8255 with the GIL off and on; re-read the notch commit path whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T12:35:59Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The defect holds on 0.2.8255, the current tree, re-verified before any change as the owner asked. melder_0's
    probe, copied with its one call renamed for 0.2.8253 (`find_spell_by_id` -> `find_spell_by_spell_id`; for an
    active spell_id both return the same Spell), ran on Python 3.14.7t with the GIL off and on; the output is
    byte-equal to his 0.2.8252 run apart from the GIL-mode warning. N1 (French, sound): owner and borrower follow. N2
    (SelfMade, SELF_DEPENDENCY): `notch_spell` raises SpellbookValidationError "Broken spells: SelfMade.", yet the
    lender's index selects SelfMade with English parked, the borrower keeps English active, the lender's meld by
    address raises that error and `meld(spell_id=English)` KeyError. N3: a notch back to English restores both sides.
  EVIDENCE:
  - context_compass/artifacts/failed_notch_refusal_20261018/probes/probe_failed_notch_commit_0_2_8255.py:1-175
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_notch_commit_0_2_8255_gil0.txt:1-34
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_notch_commit_0_2_8255_gil1.txt:1-38
  IMPACT: Nothing landed since 0.2.8252 changed the failure; the acceptance criteria stand as written.
  NEXT: Choose the mechanism from the commit path as read on 0.2.8255 (FACT note), then the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T12:35:59Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The commit path, re-read whole on 0.2.8255; melder_0's FACT note stands, with three precisions. (1) On
    `end_transaction(success=True)` the mediator runs the session's own commit pipeline (empty), then the strategy's
    commit delta (the notch strategy keeps the base one: fact stamps for the Book and every sealed conduit), then the
    orchestrator's commit: the CCM's structural validator - phases 1-4 for the index's now-active member when it has
    no Phase-4 result and no Phase-5 root blueprint; the CCM's general validator is never set - then its hooks, the
    dirty marker first. (2) When the validator raises, the orchestrator's abort hook (wired to the CCM dispatcher,
    whose own hook nothing sets) and the session's abort pipeline run - nothing in src/melder registers a session
    hook or rollback action - and `on_end` reopens the frozen gates: the seam's switch and the delta's fact stamps
    stay. (3) The validator checks the incoming version after the switch, while it is in `_spell_id_pool`; parked, it
    is not (the park pops it), and Phase 3 takes its candidates from a copy of that pool, so a check of the parked
    version before the switch would read another candidate set (SelfMade could not resolve to itself). The refusal
    has to undo the switch after the check and before the transaction ends, while the seal and gate freeze hold.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5650-5787
  - src/melder/aether/spellbook/spellbook.py:3856-4066
  - src/melder/aether/spellbook/spellbook.py:1500-1611
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:136-159
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:472-520
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:786-817
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:1043-1091
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transaction_strategy.py:169-240
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/orchestrator/orchestrator.py:452-587
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:240-244
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:744-835
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_session.py:409-526
  - src/melder/aether/spellbook/spellbook_creation_system.py:1586-1654
  IMPACT: The mechanism is an undo inside the window, not a check before the switch; the patch docs say where it
    runs and what it reverses (the seam's steps, the journal entry, the record and Nexus rows).
  NEXT: Draft the architecture, component and code-description patches for the notch's commit path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T12:46:22Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch docs drafted (failed_notch_refusal_2026_10_18; Artifact Links). Mechanism: `Spellbook._notch_spell`
    records the before-state, runs the seam, then runs phases 1-4 for a never-compiled incoming version inside the
    window (the commit validator's own test); on a broken verdict it reverts (`_revert_refused_notch`, new: the seam
    run toward the outgoing version with reason `mutation_rolled_back`, then the incoming key's Book lookup and frame
    claim set back; with no outgoing version - a minted index - park, unregister, Nexus record out), resets the
    refused version's Phase 1-4 artifacts and raises SpellbookValidationError with a new `preface` line saying the
    notch did not happen. The research journal entry moves after the check. Mapping, patch section -> step ->
    validation: architecture invariants and the notch component's After -> `_notch_spell`, `_apply_notch` minus the
    journal, `_revert_refused_notch`, the artifact reset -> component tests 1-5 and integration N1-N3, GIL off and
    on; the preface component -> `SpellbookValidationError.__init__(..., preface=None)` and its docstring -> unit
    tests (message unchanged without it, first line with it, TypeError for a non-str or empty one); docstrings
    (`Conduit.notch_spell`, the CCM validator, `_stage_spell_for_structural_phases`) -> the documentation ritual.
    No src edit before the owner approves the patch and melder_0 hands the files over.
  EVIDENCE:
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/architecture_patch.md:1-62
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/component_patch_spellbook_notch_refusal.md:1-54
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/component_patch_spellbook_validation_error_preface.md:1-21
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/code_description_patch_notch_refusal.md:1-35
  IMPACT: The ENTRY_GATE's patch docs exist; what remains before code is the owner's approval and the file claim.
  NEXT: Ask the owner to approve the patch docs; claim spellbook.py, conduit.py, spellbook_validation_error.py and
    change_control_manager.py from melder_0 once he does.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T12:48:25Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner approved the patch docs (chat 2026-10-18): asked "Do you approve the S8 patch docs (switch, check,
    undo inside the notch window)?", he answered "sure yeah thats fine but go over the things you want to change".
    So: each method the fix edits is re-read whole, and the exact edits listed, before the first edit; the files are
    claimed from melder_0 first (M1-31: spellbook.py, conduit.py, spellbook_validation_error.py,
    change_control_manager.py), and the red tests, which touch no held file, are written meanwhile.
  EVIDENCE: context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/architecture_patch.md:1-62
  IMPACT: The ENTRY_GATE is met except the file claim; no src edit before melder_0 answers M1-31.
  NEXT: Send M1-31; re-read the methods to change; write the red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T13:11:11Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The red tests are written (new files; no held file touched) and fail on 0.2.8255 for the defect's reasons,
    the same with the GIL off and on: 18 failed, 1 passed (the standing-notch journal control). Integration (13
    tests: probe N1-N3 and the patch's component expectations in one file): the index still selects SelfMade, its
    frame claim and Nexus record name SelfMade, a retry is a no-op, a claim taken for another address stays, a
    minted index keeps SelfMade active, English cannot meld, the journal keeps SelfMade's promotion, and a sound
    notch afterwards leaves the borrower two active copies. A symptom probe N2 did not show: the borrower's own
    consumer of the index (`Speaker(greeter: Greeter)`) fails its meld with SpellbookValidationError
    [DANGLING_DEPENDENCY] naming SelfMade, which the borrower holds parked - the failed notch breaks the borrower's
    consumers, not only the lender. Unit (5 tests): `preface` does not exist yet; the refusal tests match the
    refusal's own text, so today's "unexpected keyword argument 'preface'" TypeError cannot pass them.
  EVIDENCE:
  - tests/integration/melder/aether/conduit/test_notch_refused_at_commit_integration.py:1-503
  - tests/unit/melder/utilities/custom_exceptions/test_spellbook_validation_error_preface.py:1-90
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/red_tests_0_2_8255_gil0.txt:1-89
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/red_tests_0_2_8255_gil1.txt:1-97
  IMPACT: The patch mapping's validation step exists before the code; the acceptance gains "the borrower's consumer
    melds English after the refusal" at no extra code.
  NEXT: The owner's word on the exact edit list (one refinement, FACT note) and melder_0's answer to M1-31.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T13:11:11Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: One step of the patch's reversal undoes the refusal when the refused version shares the restored version's
    address - the usual case, probe N2's. Staging a version under the active version's key drops that key's frame
    claim and Book address lookup (STORY-2026-10-17-staged_version_releases_active_signature, C1, unfixed), so
    before the notch English holds neither. The reversal runs the seam toward English, whose promotion sets both to
    English again (`_reactivate_owned_spell` sets `_lookup_spells[key]`, `_apply_notch` calls `update_lookup`); the
    step "set the incoming key's lookup and claim back to their before-values" would then release both: English
    active but unclaimed and not meldable by address, against this story's acceptance ("the lender melds English by
    address"). Refinement for the code: set the refused version's key back only when it is not the restored
    version's key, or when there is no restored version (a minted index); a shared key is left to the reversal's
    promotion, as a notch back leaves it today. Asked of the owner with the edit list.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:1500-1622
  - src/melder/aether/spellbook/spellbook.py:3911-4066
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:307-336
  - context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:83-89
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/component_patch_spellbook_notch_refusal.md:24-30
  IMPACT: Without it the main acceptance test fails after the fix; with it a refused notch also leaves English's
    address claimed, which staging (S1) had dropped - the structure S1's own fix will keep in place.
  NEXT: The owner's OK on the refinement; then the patch docs updated to say it, before the code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-18T13:12:16Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-194 from melder_0 (13:07:47Z), consumed: it acknowledges M1-30 and M1-31 and releases the four files to
    melder_1 for S8 until it lands - spellbook.py, conduit.py, spellbook_validation_error.py and
    change_control_manager.py. The identity epic edits no src/ file before the owner approves its patches; after
    that its S1 needs spellbook.py only for `inspect_spell`'s stage-3 docstring and comment, and its S3 and S4 need
    spellbook.py and conduit.py. melder_0 claims a file back by message first and waits for S8's landing if S8 is
    still open; whoever lands second notches above the first.
  EVIDENCE: context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:359-381
  IMPACT: The ENTRY_GATE's file claim is met; the only gate left before the first src edit is the owner's word on
    the edit list (one refinement, FACT note).
  NEXT: Put the exact edit list, with the refinement, to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-18T13:38:59Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner put S8 on hold (chat 2026-10-18). Shown the exact edit list - `_notch_spell`'s in-window check,
    `_apply_notch` without the journal call, a new `_revert_refused_notch`, the refusal line, the error's `preface`,
    three docstrings - and the refinement (a shared address left to the reversal's promotion), he answered "Hold"
    to "Go ahead with the S8 edits as listed, including the refinement?", then asked what is next. No src edit is
    made for S8; the red tests, the patch docs and the lane's artifacts stay as they are, and the refinement is not
    written into the patch docs. melder_1 moves to S9 (the owner's order without S3, which has an open question)
    and tells melder_0 that the four files released for S8 (M0-194) can be claimed back while S8 waits.
  EVIDENCE: context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:83-89
  IMPACT: S8 is blocked on the owner's word; nothing in src/ changed for it, so no notch or rebuild is owed.
  NEXT: The owner's word to resume S8 (with or without the refinement); meanwhile S9's re-verification.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T10:34:26Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's answers (chat 2026-10-19), asked for every open item after S7 landed: the order is S1, S3,
    S2, S8, S5, all with melder_1, each landed and rebuilt before the next; the pace is "go straight through" -
    re-verify, fix, test, land, report after, stopping only for a real decision; the parked backlog is melder_1's
    pick, with "regression tests for everything so you can see if its actually a bug". On S8 he did not yet say
    go: shown the half-switch with this story's broken version (a constructor that takes its own class), he said
    it "looks like recursion" and asked for a test that proves the half-switch can happen. So the proof comes
    first, with a version that fails its check for an ordinary reason (two registered providers of its `Clock`
    parameter, AMBIGUOUS_PROVIDER), as a probe in plain words and a regression test; his word on the fix follows.
  EVIDENCE: context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:83-89
  IMPACT: S8 resumes for its proof only (no src edit); the fix waits for the owner's word after he sees it.
  NEXT: Write the probe and the regression test; run them on 0.2.8260 with the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T10:48:29Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The half-switch is not about recursion; proven on 0.2.8260 with the GIL off and on. A version broken for
    an ordinary reason - TimedGreeter, whose `clock: Clock` parameter has two registered providers (UtcClock,
    LocalClock) - is staged without error; `notch_spell` to it raises SpellbookValidationError
    [AMBIGUOUS_PROVIDER], and afterwards the lender's index selects TimedGreeter, `meld(spell_id=English)` raises
    KeyError, a meld by the greeter address raises KeyError (TimedGreeter staged at its own address) and the
    borrower's consumer `Speaker` is refused (SpellbookValidationError naming Speaker) - the state SelfMade
    leaves. Side by side, Melder gives each version its real reason at the notch and at every meld: SelfMade
    "depends on itself ... [SELF_DEPENDENCY]", TimedGreeter "... 2 registered spells provide it ...
    [AMBIGUOUS_PROVIDER]". The checks are right; the switch they follow is never undone. The owner asked for
    this proof (chat 2026-10-19: "make a test for this and prove this can happen because this looks like
    recursion"; "so your claiming melder doesn't catch a recursion loop in its checks?") and was shown it.
  EVIDENCE:
  - context_compass/artifacts/failed_notch_refusal_20261018/probes/probe_failed_switch_plain.py:1-100
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_switch_plain_0_2_8260_gil0.txt:1-13
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_switch_plain_0_2_8260_gil1.txt:1-17
  - context_compass/artifacts/failed_notch_refusal_20261018/probes/probe_failed_notch_two_reasons.py:1-91
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_notch_two_reasons_0_2_8260.txt:1-76
  IMPACT: The defect is the notch's order - switch, then check, no undo - whatever the check finds, so the fix in
    the patch docs (an undo inside the window) must and does cover any failing check, not only a self-dependency.
  NEXT: Add symptom-named regression tests with TimedGreeter to the S8 integration file (red today) and run them
    with the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T10:54:06Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Two symptom-named regression tests with the no-recursion version join the S8 integration file -
    test_a_notch_refused_for_an_ambiguous_provider_leaves_the_old_version_active and
    test_a_notch_refused_for_an_ambiguous_provider_leaves_borrowers_on_the_lenders_version (Clock, UtcClock,
    LocalClock and TimedGreeter; `_world(clocks=True)` binds the two clocks), and the file's docstring names both
    broken versions. On 0.2.8260 the S8 red set is 20 failed, 1 passed, the same list with the GIL off and on:
    13 integration and 7 unit failures, each for the defect's reason (the index selects the broken version, the
    borrower's Speaker is refused, English is unclaimed and does not meld, `preface` does not exist yet); the
    pass is the standing-notch journal control. The two new tests fail where the SelfMade ones do: at the index
    selection (TimedGreeter selected) and at the borrower's Speaker meld.
  EVIDENCE:
  - tests/integration/melder/aether/conduit/test_notch_refused_at_commit_integration.py:93-134
  - tests/integration/melder/aether/conduit/test_notch_refused_at_commit_integration.py:249-295
  - tests/integration/melder/aether/conduit/test_notch_refused_at_commit_integration.py:422-459
  - context_compass/artifacts/failed_notch_refusal_20261018/scripts/add_ambiguous_provider_tests.py:1-206
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/s8_red_0_2_8260_gil0.txt:1-100
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/s8_red_0_2_8260_gil1.txt:1-108
  IMPACT: The fix's acceptance now proves the refusal for any failing check, not only a self-dependency; the red
    set is the patch mapping's validation step on today's tree.
  NEXT: Re-check the patch against 0.2.8260, after the identity landings (FACT note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T10:54:06Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S8's analysis and mechanism hold on 0.2.8260, after the new bind (0.2.8257-0.2.8258), as the owner asked
    (chat 2026-10-19: "make sure your change is true after our new bind changes because french and english should
    be seperate IDs now"). (1) English, French, SelfMade and TimedGreeter on one index at one address are four
    spell_ids (each the hash of its code) under one binding hash (one binding): a notch switches the index between
    separate spells. (2) The commit path, re-read whole, has the shape the 0.2.8255 FACT note gives: `notch_spell`
    ends the transaction outside its try and fans out to borrowers after; `_apply_notch` parks the outgoing
    version, promotes the incoming one, repoints the index and the frame claim by the incoming key and
    re-registers the index gated; the commit's structural validator resolves the staged binding key to the
    now-active member and runs phases 1-4 only for a never-compiled one, letting the error propagate. Nothing
    there takes identity from the bind call, so the undo inside the window still fits. (3) S1's defect still
    shapes the claims: staging at English's address drops its frame claim and Book lookup, and the failed notch
    leaves both on TimedGreeter. S1 and S2 land first (the owner's order) and change those steps, so the patch's
    claim and lookup restoration (the shared-address refinement) is re-derived on the tree they leave, before
    S8's code.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5650-5787
  - src/melder/aether/conduit/conduit.py:5828-5881
  - src/melder/aether/spellbook/spellbook.py:1572-1693
  - src/melder/aether/spellbook/spellbook.py:3947-4157
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:562-586
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:744-835
  - context_compass/artifacts/failed_notch_refusal_20261018/probes/probe_identity_after_new_bind.py:1-99
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_identity_after_new_bind_0_2_8260.txt:1-26
  IMPACT: S8's patch docs stand except their claim and lookup restoration step, which waits for the behaviour S1
    and S2 leave; nothing in them assumed spell_ids taken from the bind call.
  NEXT: Send M1-45 to melder_0 with the owner's order (S1, S3, S2, S8, S5, all with melder_1), then open S1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T11:07:22Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's go for the fix, now (chat 2026-10-19). Asked "are you saying notch doesn't roll back?" and told
    that today it does not - its check fails after the switch and nothing in src/melder registers a rollback or an
    abort hook for it - he answered "yes go ahead and fix this ... it should roll back properly", and asked that
    the code be explained properly. So S8 is fixed now, ahead of S1, S3, S2 and S5 (his order for those stands),
    as the patch docs give it: the check inside the notch window and, when it fails, an undo of everything the seam
    did - English active, selected, claimed and routed again, the refused version parked and unchecked, borrowers
    untouched, nothing journaled or published for the refused version - with the shared-address refinement (FACT
    note of 2026-10-18T13:11:11Z), which a proper rollback needs on today's tree; the patch docs take it first.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:242-242
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:534-560
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_session.py:445-526
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/architecture_patch.md:1-62
  IMPACT: S8's hold is lifted; the four files go to melder_1 for S8 by message (M1-45); S1 follows S8.
  NEXT: Send M1-45; add the refinement to the patch docs; implement and test in the mirror while melder_0 answers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T11:10:18Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: CONFLICT
  CLAIM: S8's files are being edited by melder_0 now: spellbook.py, conduit.py and conduit_ward.py changed at
    2026-10-19T11:07:13Z, nine seconds before M1-45, for melder_0's cleanup_releases_contracts_2026_10_19 (it takes
    0.2.8261: a conjured Book's `cleanup_and_remove_spell` goes through `Conduit.cleanup_spell`, and `_dispose_spell`
    takes a `release_contracts` hook), with two new tests untracked. Its hunks sit in `cleanup_and_remove_spell` and
    `_dispose_spell`, not in the notch path S8 edits, but one writer per file holds: melder_1 edits neither file
    until melder_0 answers M1-45. Meanwhile S8 is built and tested in the mirror on the index's versions of the
    three files (0.2.8260), and applied onto whatever melder_0 lands by anchored edits.
  EVIDENCE: src/melder/aether/spellbook/spellbook.py:4483-4680
  IMPACT: S8 lands after melder_0's change and notches above it (0.2.8262 if melder_0 lands 0.2.8261).
  NEXT: Implement the rollback in the mirror; re-read the mailbox between work units for melder_0's answer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T11:22:28Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: CONFLICT
  CLAIM: M0-209 from melder_0 (2026-10-19T10:50:30Z), consumed after the re-onboarding: the owner gave S3
    (STORY-2026-10-17-parked_cleanup_leaves_borrower_copies) its go in melder_0's chat and melder_0 takes it -
    `Conduit.cleanup_spell` removes a version from every contract that holds it before the Book disposes it, and
    the direct `Spellbook.cleanup_spell` takes the same path; melder_0 writes conduit.py, spellbook.py and, if the
    patch needs it, conduit_ward.py, notches above 0.2.8260 at landing, and asks to be told before they are
    edited. That crosses the order the owner gave melder_1 (DECISION note of 2026-10-19T10:34:26Z: S1, S3, S2, S8,
    S5, all with melder_1) and M1-45's line "S3 comes to melder_1 too". S3 is in progress with melder_0, so
    melder_1 does not take it: after S8 it goes on with S1, S2 and S5, and asks the owner about S3 only if
    melder_0 hands it back.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md:329-350
  - context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:456-475
  - context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:561-581
  IMPACT: S8's files stay with melder_0 until it answers M1-45 or lands S3; S8 lands after S3 and notches above it.
  NEXT: Add the shared-key refinement and the preface's line-break refusal to the patch docs, then build the
    rollback in the mirror.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T11:31:31Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: The patch docs now carry the owner's go, the shared-key refinement and the preface's line-break refusal
    (scripts/patch_docs_refinement_20261019.py), and every method the fix changes was re-read whole on the mirror
    (0.2.8260). Mapping, patch section -> step -> validation: the architecture invariants and the notch component's
    After -> `_notch_spell` (the before-state, the seam, `_check_notched_version`, the journal once the notch
    stands), `_apply_notch` without the journal, `_revert_refused_notch` (the seam run back with
    `mutation_rolled_back`; a differing key set back by `_restore_binding_key`; a minted index through
    `_revert_refused_activation` and `_remove_spell_record_from_nexus`) and the artifact reset -> the 14 integration
    tests (13 red, one control), GIL off and on; the preface component -> `SpellbookValidationError.__init__(...,
    preface=None)` and `_check_preface` -> the 7 unit tests plus a new line-break test; the docstrings
    (`Conduit.notch_spell`, the CCM validator, `_stage_spell_for_structural_phases`) -> the documentation ritual.
    Two of the four files are CRLF on disk (spellbook_validation_error.py, change_control_manager.py; git holds
    them LF), so their edits keep CRLF.
  EVIDENCE:
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/architecture_patch.md:1-69
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/component_patch_spellbook_notch_refusal.md:1-62
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/code_description_patch_notch_refusal.md:1-38
  - context_compass/system_docs/patches/active/failed_notch_refusal_2026_10_18/component_patch_spellbook_validation_error_preface.md:1-23
  - src/melder/aether/spellbook/spellbook.py:3947-4157
  - src/melder/utilities/custom_exceptions/spellbook_validation_error.py:147-174
  IMPACT: The code follows the patch section by section; the red set is its acceptance.
  NEXT: Write the edit script for the mirror and run the red set with the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T11:41:48Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The red set on the mirror (0.2.8260 plus the S8 edits) found one more thing the reversal must put back: the
    check's Phase 3 registers the refused version's dependencies and topology on the lineage
    (`update_dependencies`, `register_local_topology`), and the seam run back leaves them. SelfMade depends on
    itself, so after the refusal the lineage read English as depending on SelfMade, and the borrower's first meld of
    `Speaker` - whose catch-up had nothing to refresh, its topology an UNRESOLVED_INPUT socket from before the link -
    was refused by VisibilityGapStrategy: "Spell 'English' depends on spells this Spellbook cannot see (spell id
    3f1c78b54469)" [visibility_gap_dependency_filtered], GIL off and on; the TimedGreeter twin passed, an ambiguous
    socket registering no dependency. `_notch_spell` now records the lineage's direct dependencies and the outgoing
    version's topology before the switch, and the reversal restores both after the seam run back. All 25 S8 tests
    pass with the GIL off and on (14 integration, 11 unit with the four new line-break cases); the probe shows the
    lineage back on no dependencies and the borrower's meld of `Speaker` ok.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:1203-1212
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:757-817
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1789-1845
  - src/melder/aether/spellbook/spell_compiler/system/validation/visibility_gap_strategy.py:43-120
  - context_compass/artifacts/failed_notch_refusal_20261018/probes/dbg_refused_notch_lineage_dependencies.py:1-42
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/dbg_refused_notch_lineage_dependencies_fix_gil0.txt:1-7
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/s8_green_gil0.txt:1-2
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/s8_green_gil1.txt:1-10
  IMPACT: The patch's invariant "SpellSystemStates tracks the restored version" widens to its dependency registration;
    the component patch and the architecture invariants say so before the code lands.
  NEXT: Add the dependency restore to the patch docs, then run the seven whole-tree shards with the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T11:41:48Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: HYPOTHESIS
  CLAIM: The same leftover may follow an ordinary notch back, outside S8: a notch back to a version compiled before
    runs no Phase 3 (`_check_notched_version` and the commit validator both skip it), so the lineage keeps the
    dependencies the version notched away registered until the restored version's next structural rerun. If one of
    them is not visible to a borrower, the borrower's consumer melding before the lender could be refused for a
    dependency the restored version does not have. Unprobed; not changed by S8.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4002-4157
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:757-817
  - src/melder/aether/spellbook/spell_compiler/system/validation/visibility_gap_strategy.py:43-120
  IMPACT: A possible defect for EPIC-2026-10-17-correctness_defects (a borrower stuck until its lender melds).
  NEXT: Probe it after S8 lands (a version with a lender-only dependency, a notch away and back, the borrower's
    consumer melding first) and file a story under the epic if it holds.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-19T11:58:42Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-210 from melder_0 (2026-10-19T11:48:58Z, the ACK of M1-45 and M1-46), consumed after the
    re-onboarding: S8 now, then S1, S2 and S5 with melder_1; S3 stays with melder_0. melder_0 holds S3's edits in
    conduit.py (`Conduit.cleanup_spell`), spellbook.py (`Spellbook.cleanup_spell`,
    `Spellbook._dispose_spell(release_contracts=...)`) and conduit_ward.py (`ConduitWard._emit_spell_disposed`, two
    docstrings), and none in spellbook_validation_error.py or change_control_manager.py. On the owner's word S3
    notches 0.2.8261 and does not rebuild; S8's landing, applied onto S3 and notched above it, rebuilds for both.
    melder_0 hands spellbook.py and conduit.py to melder_1 by NOTICE when S3 lands. S3's hunks sit in
    `_dispose_spell`, `cleanup_spell` and the ward, not in the notch path S8 edits.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:1135-1157
  - context_compass/tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md:410-447
  - context_compass/tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md:449-466
  IMPACT: S8 applies all five of its files to the repository in one pass after the hand-over (the two free files
    wait too, so no half of S8 sits in the worktree while S3 is committed); its notch is the next free number
    above 0.2.8261, read from `__version__` at landing.
  NEXT: Finish the documentation ritual on the mirror diff (spellbook_validation_error.py), then re-run the S8
    probes on the mirror with the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T11:59:46Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The whole tree passes on the mirror with the S8 rollback, the GIL off and on: 0 failed in all seven shards,
    14,620 passed in each mode - unit 9,702, component 2,403, integration spellbook 678, aether 836 (S8's 14
    integration tests among them), conduit 353, the rest 398, experiments and misc 250 - beside the skips, xfails
    and xpasses those shards always carry. The mirror is 0.2.8260 as the git index holds spellbook.py and
    conduit.py, the worktree's spellbook_validation_error.py and change_control_manager.py, and the repository's
    tests, with the S8 edits applied by apply_s8_rollback.py. Method: Python 3.14.7t, `-X gil=0` and `-X gil=1`
    with PYTHON_GIL to match, one pytest run per shard. Caveat: melder_0's S3 tests (untracked, only in the
    repository) are not in the mirror; the tree is run again once S8 is applied onto S3.
  EVIDENCE:
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_unit_gil0.txt:1-137
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_unit_gil1.txt:1-145
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_component_gil0.txt:1-35
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_component_gil1.txt:1-43
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_integ_spellbook_gil0.txt:1-11
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_integ_spellbook_gil1.txt:1-19
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_integ_aether_gil0.txt:1-13
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_integ_aether_gil1.txt:1-21
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_integ_conduit_gil0.txt:1-6
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_integ_conduit_gil1.txt:1-14
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_integ_rest_gil0.txt:1-7
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_integ_rest_gil1.txt:1-15
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_exp_and_misc_gil0.txt:1-5
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_mirror_0_2_8260/s8_exp_and_misc_gil1.txt:1-13
  IMPACT: The rollback breaks nothing outside S8's own 25 tests; what remains before the repository is the
    documentation ritual on the error file, the probes on the mirror, and melder_0's hand-over after S3.
  NEXT: Finish the documentation ritual on the mirror diff (spellbook_validation_error.py), then re-run the S8
    probes on the mirror with the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T12:04:23Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The four S8 probes, re-run on the mirror (0.2.8260 plus the rollback), show the refusal with nothing
    moved, the same with the GIL off and on (only the GIL-mode warning differs). N2: `notch_spell` to SelfMade
    raises SpellbookValidationError whose first line is "notch_spell refused: 'SelfMade' (spell_id 83717df2...)
    failed its structural check, so the notch did not happen; 'English' (spell_id 677a47a3...) is still the active
    version of the index.", the SELF_DEPENDENCY report under it; afterwards the lender selects English, SelfMade is
    parked, the borrower holds English active and SelfMade parked, and the lender melds English by address and by
    spell_id. N1 (French, sound) moves owner and borrower as before; N3 (a notch back to English after N2) changes
    nothing. The ambiguous-provider version (TimedGreeter) is refused the same way with its AMBIGUOUS_PROVIDER
    report, and the borrower's Speaker melds "hello". The lineage probe: after the refusal the lineage reads
    English with no dependencies and the borrower's meld of Speaker is ok. The documentation ritual on the error
    file changed only its words and one annotation: the docstrings name `Spellbook._notch_spell` as the caller
    that passes a preface, and `_check_preface` takes `object` (the value it narrows), not `Any`; the edit set
    (apply_s8_rollback.py) reproduces the mirror byte for byte from the index's spellbook.py and conduit.py and
    the worktree's other files, and the custom-exception unit tests plus S8's integration file pass, 63 in each
    GIL mode.
  EVIDENCE:
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_notch_commit_s8_mirror_gil0.txt:1-34
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_notch_commit_s8_mirror_gil1.txt:1-38
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_notch_two_reasons_s8_mirror_gil0.txt:1-30
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_notch_two_reasons_s8_mirror_gil1.txt:1-38
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_switch_plain_s8_mirror_gil0.txt:1-13
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_switch_plain_s8_mirror_gil1.txt:1-17
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/dbg_refused_notch_lineage_dependencies_s8_mirror_gil0.txt:1-7
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/dbg_refused_notch_lineage_dependencies_s8_mirror_gil1.txt:1-11
  - context_compass/artifacts/failed_notch_refusal_20261018/scripts/s8_error_doc_ritual_20261019.py:1-73
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/s8_after_ritual_gil0.txt:1-2
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/s8_after_ritual_gil1.txt:1-10
  IMPACT: The exit gate's probe criteria hold on the mirror; S8 waits only for melder_0's hand-over of
    spellbook.py and conduit.py after S3 lands, then the repository edits, the tree again, docs, notch, rebuild.
  NEXT: Draft the system-document edits for S8 (src_architecture, src_components, tests docs) in the lane while
    melder_0 lands S3; re-read the mailbox between work units.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T12:08:58Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The HYPOTHESIS of 11:41:48Z holds for an ordinary notch back, outside S8, on 0.2.8260 (the git index's
    src, exported), the same with the GIL off and on. English (no dependencies) active; French, which needs Accent,
    staged; Accent bound only in the lender's Book; a borrower links, contracts the index and binds
    Speaker(greeter: Greeter). The lender notches to French and melds it (the lineage reads deps [Accent]), then
    notches back to English: the lineage still reads deps [Accent], gated. H3 - the borrower's Speaker never melded
    before: its first meld is refused, "Spell 'English' depends on spells this Spellbook cannot see (spell id
    6e9578a406c6 [Accent]) ... [visibility_gap_dependency_filtered]"; the lender's meld of English then clears the
    lineage to deps [], yet every later meld of Speaker is refused, "Broken spells: Speaker ... No validation error
    was recorded for this spell; its validity is invalid, gated or disabled.": the borrower is stuck. H1 - the
    borrower melded Speaker before the notches: its meld after the notch back is "hello" (its recorded topology
    names English, so the meld's catch-up refreshes the gated lineage first). H2 - the lender melds English first:
    "hello". Not yet read whole: why the catch-up skips English in H3 and why nothing re-gates Speaker's verdict.
  EVIDENCE:
  - context_compass/artifacts/failed_notch_refusal_20261018/probes/probe_notch_back_lineage_dependencies.py:1-105
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_notch_back_lineage_dependencies_0_2_8260_gil0.txt:1-42
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_notch_back_lineage_dependencies_0_2_8260_gil1.txt:1-54
  IMPACT: A defect for EPIC-2026-10-17-correctness_defects, independent of S8 (S8's reversal restores the
    dependencies for a refused notch only): a notch back can leave a borrower's consumer refused for good.
  NEXT: Read the paths whole (the notch's lineage re-registration, the meld gate and its catch-up, the visibility
    strategy, the verdict that stays invalid), then file a story under the epic and tell melder_0.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T12:13:37Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The HYPOTHESIS of 11:41:48Z, measured at 12:08:58Z and read whole on 0.2.8260, is filed as
    STORY-2026-10-19-notch_back_keeps_outgoing_dependencies (ready, unassigned, p2) under
    EPIC-2026-10-17-correctness_defects: `_apply_notch` never writes the lineage's dependencies and a notch to a
    compiled version runs no Phase 3, so the outgoing version's dependencies stay; a borrower's consumer melding
    first is refused by `VisibilityGapStrategy` and its verdict stays `invalid`. A fourth case joined the probe -
    H4, a notch to French and straight back with no meld between - refused and stuck the same way. The story's
    reproducer is rowed on the artifact board; melder_0, the epic's writer, is told by M1-47.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-19_notch_back_keeps_outgoing_dependencies_story.md:1-212
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_notch_back_lineage_dependencies_0_2_8260_gil0.txt:1-55
  IMPACT: S8's own scope is unchanged (its reversal restores the dependencies for a refused notch only); the plain
    notch-back case waits for the owner's scheduling.
  NEXT: Wait for melder_0's hand-over of spellbook.py and conduit.py after S3, then apply S8 to the repository.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T12:29:12Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: S8 goes onto S3 as S3 stands in the worktree (not yet notched; `__version__` reads 0.2.8260).
    `apply_s8_rollback.py <repository> --check` finds every edit's old text once in each of the five files and
    writes nothing (spellbook.py 7945 -> 8344 lines, conduit.py 7892 -> 7907; the error file, the CCM and the unit
    test as on 0.2.8260). On the mirror, re-synced from the worktree's src/ and tests/ (S3's edits and its two
    untracked tests included) with the S8 edits applied, S8's integration file, the custom-exception unit tests
    and S3's two new test files pass, 76 in each GIL mode. Method: Python 3.14.7t, `-X gil=0` and `-X gil=1` with
    PYTHON_GIL to match, one pytest run each. Caveat: S3 can still change before its notch, so the check and the
    whole tree run again on the repository after melder_0's hand-over.
  EVIDENCE:
  - context_compass/artifacts/failed_notch_refusal_20261018/scripts/apply_s8_rollback.py:1-746
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/s3s8_smoke_mirror_gil0.txt:1-3
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/s3s8_smoke_mirror_gil1.txt:1-11
  IMPACT: S3's hunks and S8's do not overlap; the landing needs no rework of the edit set, only the re-check on
    the tree melder_0 hands over.
  NEXT: Draft S8's system-document edits against the post-S3 text (land_s8_docs.py), reading the mailbox between
    work units.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T12:37:14Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The owner's review (chat 2026-10-19): "The rollback for notch is fine but it should still put the spell in an
    invalid state just incase for revalidation". It does, in Melder's terms: `gated` is the state whose next meld
    re-runs the checks, and `invalid` refuses every meld with no re-run (`Meld._ensure_lineage_resolvable`,
    `Meld._ensure_resolution_resolvable`). Probe on the mirror (S3 as in the worktree, plus S8), the same with the GIL
    off and on apart from the GIL-mode warning: after a notch to TimedGreeter is refused, the index state reads gated
    and tracks English, English's verdict in the world conduit reads gated, and TimedGreeter's reads gated with its
    check result cleared; one meld of English returns "hello" and leaves the index state and English's verdict valid.
    The marks are the seam's own (`register_index`, `mark_dependents_for_revalidation`, the verdicts set gated), from
    its run back toward English and its forward run to TimedGreeter; S8 adds no mark. Shown to the owner.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4002-4157
  - src/melder/aether/conduit/meld/meld.py:944-1021
  - src/melder/aether/conduit/meld/meld.py:1290-1351
  - context_compass/artifacts/failed_notch_refusal_20261018/probes/probe_refused_notch_marks.py:1-77
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_refused_notch_marks_s3s8_mirror_gil0.txt:1-21
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_refused_notch_marks_s3s8_mirror_gil1.txt:1-25
  IMPACT: The owner's ask is met by the patch as built; S8's edit set is unchanged.
  NEXT: Act on the owner's answer on the turn-in (DECISION_REQUEST note).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T12:37:14Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: The owner asked (chat 2026-10-19), after the notch-back discussion: "... however just turn in your tickets".
    S8 is not in the repository: its edits wait for melder_0's hand-over of spellbook.py and conduit.py after S3.
    Asked twice, the second time in one line because he is reading on his phone: land S8 first (apply, the whole
    tree, docs, the notch, the release note, the rebuild for S3 and S8) and then turn it in, or turn it in now
    unlanded - parked in the backlog with the ready edit set and its tests, nothing in src/. Either way melder_1 stops
    after it: S1, S2 and S5 stay with the epic, not started. No answer yet.
  EVIDENCE: context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:921-937
  IMPACT: The answer decides whether S8 lands at the next free notch with the rebuild for both stories, or parks;
    until then S8 waits for S3's hand-over as before.
  NEXT: Act on the owner's answer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T12:39:07Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-211 from melder_0 (2026-10-19T12:35:35Z), consumed: on the owner's word ("After you finish your change
    hand all your tickets to melder1 your competing for the same resources and document them") S3 landed at
    0.2.8261 with no rebuild - src, 13 tests, docs, indexes, graph, the release-note section "Cleaning up a spell
    takes it out of every contract first", the notch - and conduit.py, spellbook.py and conduit_ward.py are
    melder_1's. Every ticket melder_0 held is melder_1's: EPIC-2026-10-17-correctness_defects,
    STORY-2026-10-17-parked_cleanup_leaves_borrower_copies (its turn-in on the owner's word) and, parked,
    STORY-2026-09-29-atomic-frame-retirement-and-creation-attribution, STORY-2026-10-18-explicit_duplicate_binding,
    STORY-2026-10-18-one_registration_per_object, STORY-2026-10-18-revalidate_on_binding_change,
    STORY-2026-10-18-spell_id_migration and TASK-2026-10-17-spell_id_wording_in_held_files; melder_0 has checked
    out. S8 lands above 0.2.8261 and its rebuild sets the release note's rebuild line, which still reads 0.2.8260.
    `__version__` reads 0.2.8261; the board's epic and S3 rows already name melder_1.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md:577-609
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:1195-1219
  - src/melder/__version__.py:12-12
  IMPACT: S8 is unblocked: its edit set applies to the landed S3 tree, the whole tree runs with S3's 13 tests, and
    S8's turn-in carries the rebuild for both; S3's turn-in is melder_1's.
  NEXT: Re-sync the mirror with the landed S3 tree, apply S8 and run the whole tree with the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T12:46:57Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner answered the turn-in question (chat 2026-10-19): "Yes do s8" - S8 lands first, then it is turned
    in, with S3's turn-in and the rebuild for both; he also confirmed "M0 is passing all info to you on his tickets".
    So: the edit set on the repository (check, then apply), the whole tree with S3's 13 tests, the probes, the
    system documents, indexes and graph, the next free notch above 0.2.8261, the release note, the closures of S3 and
    S8, and the rebuild last; then melder_1 stops - S1, S2 and S5 stay with the epic, not started.
  EVIDENCE: context_compass/tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md:961-977
  IMPACT: The DECISION_REQUEST note is answered; S8 proceeds to landing.
  NEXT: Finish the whole tree on the mirror (S3 landed plus S8) with the GIL off and on, then apply to the repository.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-19T12:55:50Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: S8 is in the repository, on S3's landed tree (0.2.8261). `apply_s8_rollback.py <repository> --check`, then
    `--apply`, edited the five files (spellbook.py 7945 -> 8344 lines, conduit.py 7892 -> 7907, the error file 541
    CRLF, the CCM 1683 CRLF, the unit test 97), byte-identical to the mirror the whole tree ran on (its src/ and
    tests/ equal to the repository's, S3's 13 tests included). The whole tree there, GIL off and on, one pytest run
    per shard: unit 9,701 passed and 1 failed, component 2,406, integration spellbook 678, aether 846 (S3's 10 and
    S8's 14 among them), conduit 353, the rest 398, experiments and misc 250 - 14,632 passed in each mode. The one
    failure, `test_generated_build_assets_are_stamped_for_the_live_version`, reads build assets stamped 0.2.8260
    against package 0.2.8261: S3 notched without a rebuild, and this landing's rebuild clears it. On the repository
    itself: S8's and S3's test files with the custom-exception unit tests, 76 passed in each GIL mode, and the
    probes - N1-N3, the plain proof, the marks - print the refusal with nothing moved; only the GIL-mode warning
    differs between the modes.
  EVIDENCE:
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/apply_s8_repo_check_0_2_8261.txt:1-5
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/apply_s8_repo_apply_0_2_8261.txt:1-6
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_unit_gil0.txt:1-143
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_unit_gil1.txt:1-151
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_component_gil0.txt:1-35
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_component_gil1.txt:1-43
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_integ_spellbook_gil0.txt:1-11
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_integ_spellbook_gil1.txt:1-19
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_integ_aether_gil0.txt:1-13
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_integ_aether_gil1.txt:1-21
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_integ_conduit_gil0.txt:1-6
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_integ_conduit_gil1.txt:1-14
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_integ_rest_gil0.txt:1-7
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_integ_rest_gil1.txt:1-15
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_exp_and_misc_gil0.txt:1-5
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/full_tree_s8_on_s3_0_2_8261/s8s3_exp_and_misc_gil1.txt:1-13
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/s8_s3_tests_repo_0_2_8261_gil0.txt:1-3
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/s8_s3_tests_repo_0_2_8261_gil1.txt:1-11
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_notch_commit_0_2_8255_repo_0_2_8261_gil0.txt:1-34
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_notch_commit_0_2_8255_repo_0_2_8261_gil1.txt:1-38
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_switch_plain_repo_0_2_8261_gil0.txt:1-13
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_failed_switch_plain_repo_0_2_8261_gil1.txt:1-17
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_refused_notch_marks_repo_0_2_8261_gil0.txt:1-21
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/probe_refused_notch_marks_repo_0_2_8261_gil1.txt:1-25
  IMPACT: S8's code is landed and validated on S3's tree; documents, the notch, the release note, the closures and
    the rebuild remain.
  NEXT: The system documents (land_s8_docs.py), the citation remap and the four indexes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T13:22:14Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: S8's documents, graph, notch and release note are in. land_s8_docs.py (41 edits) carries the refusal into
    src_architecture (the boundary list, the summary, a new step 6 of the SpellIndex Mutation Entry sequence, an
    operational invariant, a fixed failure mode, four code-map entries remeasured), src_components (Spellbook Core,
    Conduit Runtime, the error's contract, the SpellIndex Mutation Surface, the notch flow, the code map),
    tests_components (both test modules catalogued with key files and code-map records; the aether integration
    tree recounted to 50, the core union 278) and tests_architecture (a handoff entry); the three citations
    remap_s8_citations.py widened cite 4022-4024 again. The four indexes are regenerated and --check OK; the
    bounds recipe flags the same 2 of 1419 citations as at S3's landing (bare file names in an older handoff
    entry). Graph: extracted with --strict (593 descriptors, none skipped); Spellbook gains one responsibility and
    its MutationResearch edge's why, SpellbookValidationError one responsibility (graph_prose_s8.py); both accepted
    after their source was read (Spellbook: S3's accepted text plus S8's whole diff; the error file whole);
    assembled and --check OK (593 sections). Conduit and ChangeControlManager stay SEMANTICS_STALE, as before this
    landing. Notch: `__version__` read 0.2.8261, set 0.2.8262. Release note: the section "A notch whose new version
    fails its check is refused, and nothing moves" and one packaging bullet, the header 0.2.8262 and the rebuild
    line for 0.2.8262; its example, run as written, prints the refusal line and "release-note example: OK" with the
    GIL off and on.
  EVIDENCE:
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/land_s8_docs_apply.txt:1-6
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/index_check_src_architecture_s8.txt:1-1
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/index_check_src_components_s8.txt:1-1
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/index_check_tests_components_s8.txt:1-1
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/index_check_tests_architecture_s8.txt:1-1
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/citation_bounds_s8.txt:1-3
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/graph_extract_0_2_8262.txt:1-46
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/graph_prose_0_2_8262.txt:1-3
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/graph_accept_0_2_8262.txt:1-6
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/graph_assemble_check_0_2_8262.txt:1-4
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/notch_0_2_8262.txt:1-1
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/release_note_s8_apply.txt:1-2
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/release_note_probe_s8_0_2_8262_gil0.txt:1-2
  - context_compass/artifacts/failed_notch_refusal_20261018/runs/release_note_probe_s8_0_2_8262_gil1.txt:1-6
  - context_compass/system_docs/src_architecture.md:1176-1215
  - context_compass/system_docs/src_architecture.md:2500-2513
  - release_docs/next_version_release.md:1145-1217
  - src/melder/__version__.py:12-12
  IMPACT: S8 is landed but for the rebuild, which comes last - after the closures and any small fixes this pass
    takes on the owner's word.
  NEXT: Turn S8 in (close_s8.py), then S3.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [x] Work walkthrough shared with user (the landing report, chat 2026-10-19, sent with this turn-in)
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
- Scope: a notch whose incoming version fails its commit check is refused with nothing moved - the lender and its
  borrowers stay on the outgoing version (Requirements; the owner's answer (a)). Defect proven on 0.2.8252
  (Notes); probe and runs in Artifact Links.
- State: done (melder_1; turned in 2026-10-19T13:24:30Z). Landed at 0.2.8262 on S3's tree: the check inside the notch
  window and the reversal in spellbook.py, the error's `preface`, docstrings in conduit.py and the change-control
  validator; 25 tests green with the GIL off and on and the whole tree as the MEASURE note records; the system
  documents with their indexes, the graph, the notch and the release-note section (FACT note); the rebuild comes
  last in this pass, after S3's turn-in and any small fixes.
- Open elsewhere: S11 (STORY-2026-10-19-notch_back_keeps_outgoing_dependencies), the owner's call; the seam's own
  refusal inside the window (TASK-2026-10-16-notch_seam_checks_incoming_before_parking); melds in flight during
  a notch's fan-out (TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout).
- Next: none here.

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
