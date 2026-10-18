# Story: failed_notch_keeps_switch_without_borrowers - a notch that fails its commit leaves no half-made switch

## Metadata
- Story ID: STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers
- Epic: EPIC-2026-10-17-correctness_defects
- Status: blocked
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-17T21:32:09Z
- Updated: 2026-10-18T13:38:59Z

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
- to_state: blocked
- transition_reason: the owner put the fix on hold (chat 2026-10-18: "Hold" on the edit list and its refinement;
  DECISION note); it resumes on his word. Before that: ready -> in_progress when he scheduled the story and
  assigned melder_1 (DECISION note of 12:30:17Z).

## Dependencies / Related Work
- TASK-2026-10-16-notch_seam_checks_incoming_before_parking (backlog): the same seam; a check moved ahead of the park
  there and a structural check ahead of the switch here would sit side by side.
- STORY-2026-10-17-notch_moves_signature_by_incoming_key_only: the seam's frame-claim step, which an undo reverses.

## Tasks (Implementation Checklist)
- [x] Task: the owner's answer on the open question (2026-10-17: refuse with nothing moved; DECISION note).
- [x] Task: patch docs for the notch's commit path; the owner's approval (2026-10-18; DECISION note).
- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- With English active, a borrower index-linked to its index and a staged version whose structure is broken (a
  constructor that takes its own class): `notch_spell` to it raises, and afterwards the lender's index and the
  borrower both select English, the broken version is still parked, and the lender melds English by address and by
  its spell_id.
- A notch to a sound version (N1) behaves as today; after the refused notch a notch to English (N3) changes nothing.

## Validation / Test Plan
- Regression tests named for the symptom, e.g. `test_a_notch_refused_at_commit_leaves_the_old_version_active` and
  `test_a_notch_refused_at_commit_leaves_borrowers_on_the_lenders_version`; GIL off and on; the probe re-run. Not
  run: no fix exists yet.

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
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

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
  - system_docs/patches/active/failed_notch_refusal_2026_10_18/ (architecture, 2 component, code-description)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's reproducer

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
  failed_notch_refusal_2026_10_18, the red tests and their runs (2026-10-18; Notes).
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

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

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: a notch whose incoming version fails its commit check is refused with nothing moved - the lender and its
  borrowers stay on the outgoing version (Requirements; the owner's answer (a)). Defect proven on 0.2.8252 (Notes);
  probe and runs in Artifact Links.
- State: blocked (melder_1): on hold by the owner since 2026-10-18T13:38:59Z (DECISION note). Filed by melder_0
  under EPIC-2026-10-17-correctness_defects; the owner answered its question (refuse, nothing moved), scheduled it
  on 2026-10-18 in parallel with EPIC-2026-10-18-spell_identity_is_the_code, and approved the patch docs, asking
  to go over the edits first (DECISION notes). Re-verified on 0.2.8255 (MEASURE note); the mechanism - an undo
  inside the window - follows from the commit path (FACT note). Red tests written and red with the GIL off and on
  (MEASURE note, 13:11Z); melder_0 released spellbook.py, conduit.py, the error and the CCM file for S8 (FACT
  note, M0-194), now claimable back while S8 waits. One refinement to the reversal (a shared address is left to
  the reversal's promotion; FACT note, 13:11Z) was put to the owner with the edit list; he chose to hold.
- Next: (1) the owner's word to resume, with or without the refinement; (2) the fix, green with the GIL off and
  on, the probe re-run; (3) docs, the release note, the next free notch, closure, the rebuild last. No src edit
  was made, so nothing is owed meanwhile.

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
