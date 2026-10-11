# Task: Close the 0.2.8231 lock residuals and decide mediator admission or SafeGuard for cross-object operations

## Metadata
- Task ID: TASK-2026-10-11-close-lock-residuals-and-evaluate-mediator-admission
- Story: none (follow-up of TASK-2026-10-11-prove-and-fix-cross-object-lock-gaps, its Note 13 residuals)
- Status: review
- Owner: claude (directed by the owner 2026-10-11)
- Agent Name: melder_1
- Priority: p1
- Created: 2026-10-11T19:37:07Z
- Updated: 2026-10-11T22:03:34Z

## Objective
Fix the residuals the 0.2.8231 lane left - Conduit.find_contracted_spell's live walk under the conduit lock, the
window between cleanup_spell's locked decision and its disposal against an index move into the same index, and the
0.2.8230 read-side snapshots wherever a keyed read or the writers' lock can replace them - and look into how
cross-object operations should be ordered in general: lock ordering with SafeGuard, or admission through the frame
mediator for operations that run outside any transaction today. Propose before changing what the mediator admits.

## Owner Direction
Owner, chat 2026-10-11, after the 0.2.8231 report:
- "ok fix all the things you want to fix please, just don't fuck up my code" (interrupted), then
- "ok so yeah propose fix for that deadlock too and if you need to use safeguard do it for lock ordering don't
  remake things but really maybe we should add mediator blocks into other things? IDK or maybe we just use
  safeguard look into that"
Reading taken (ALIGNMENT, stated to the owner): fix the residuals; the listing deadlock is already removed in
0.2.8231, so "that deadlock" is answered by a lock-order audit of the cross-object paths and a proposal - SafeGuard
where one operation takes several peer locks at once, mediator admission where an operation must be ordered against
transactions - with no change to what the mediator admits until the owner decides.

## Ticket Contract
- ENTRY_GATE: owner direction (chat, 2026-10-11); this ticket and its attention_board.md row exist before the first
  investigation tranche.
- EXECUTION_BOUNDARY: read src/melder for the residuals, the lock orders and the mediator; reproduce in scratch
  copies under /tmp through public operations and the real locks and mediators only; fix in scratch; land through the
  patch lane after the new tests and the full tree pass. No commit or push. No new transaction type, admission change
  or public contract change without the owner's decision.
- DEPENDENCIES: working tree with 0.2.8231 landed, uncommitted (predecessor ticket in review).
- EXIT_GATE: each residual proven and fixed, or retracted with evidence; the audit and the proposal recorded and
  decided by the owner; the change set landed with the checks green.
- FAILURE_ESCALATION: DECISION_REQUEST for a transaction-type or admission change, a new kind of lock-order edge or a
  public contract change; BLOCKER if the VM disk stops validation.

## Scope Boundaries
- In scope: Conduit.find_contracted_spell; Conduit.cleanup_spell / Spellbook._dispose_spell against the index-move
  seams; the 0.2.8230 snapshots (SpellbookCreationSystem book-wide factories and cleanup pass, inspect_spell over
  another Book, the transfer impact walk, the fallback walk of Spellbook._find_contracted_spell_by_id); the lock-order
  edges between conduit, ward, contract, Book, spell, index, frame and Aether locks; the frame TransactionMediator and
  SafeGuard as ordering tools.
- Out of scope: the meld path; D-10, D-11, D-20; MelderOps code; (d)-(g) of the spell-map lane's Note 13.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner directed the residual fixes and the ordering proposal in chat (2026-10-11).
- from_state: in_progress
- to_state: review
- transition_reason: 0.2.8232 landed with its tests and checks (2026-10-11T20:41:33Z); acceptance, commit and push
  are the owner's.
- from_state: review
- to_state: in_progress
- transition_reason: the owner asked how E will be fixed - a direct Spell.cleanup() of a live owned spell takes
  spell -> Book against Book teardown's Book -> spell (chat, 2026-10-11); 0.2.8232 stays landed, unaccepted.
- from_state: in_progress
- to_state: review
- transition_reason: 0.2.8233 landed with its tests and checks (2026-10-11T22:03:34Z); acceptance, commit and
  push are the owner's.

## Steps / Checklist
- [x] Read the three residuals and prove or retract each through the real locks (Notes 1-3: the contracted lookup and
      the inspection walk proven; the cleanup_spell index-move window left open by the owner).
- [ ] Audit the cross-object lock-order edges for inversions - dropped by the owner ("no broad lock audit", Note 1);
      two inversions found on the way were fixed (D) or recorded (E), Note 4.
- [ ] Read the frame mediator's admission and SafeGuard; write the proposal - dropped: the owner ruled out mediator
      admission for cleanup_spell and asked for the bugs found to be fixed (Notes 1, 4).
- [x] Owner decision: no mediator; fix the bugs found without hurting performance (Notes 1, 4).
- [x] Patch docs and mapping; scratch fix; red/green; full tree (Notes 5-6).
- [x] Land as the next notch (0.2.8232, Note 7); assets and llm_support rebuilt last (Note 8).
- [x] E: read the direct Spell.cleanup() path against Book teardown, propose the fix, and on the owner's
      confirmation land it as the next notch (0.2.8233) the same way (Notes 9-16; F2 and F3 recorded, out).
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- A proof or retraction per residual; fixes with regression tests; the lock-order audit; the mediator/SafeGuard
  proposal and the owner's decision; the landed change set.

## Files / Paths Impacted
- src/melder/aether/conduit/conduit.py (find_contracted_spell, inspect_spell, cleanup_spell docstring)
- src/melder/aether/spellbook/spellbook.py (inspect_spell, cleanup_spell docstring, _dispose_spell,
  `_disposing_spell_ids` init and cleanup)
- src/melder/aether/spellbook/spell.py (cleanup, new `_direct_removal_route`, slot `_removal_lock`; 0.2.8233)
- src/melder/aether/spellbook/spellbook.py, 0.2.8233: cleanup_and_remove_spell re-check, cleanup_spell docstring,
  _dispose_spell comment
- src/melder/__version__.py (0.2.8232, then 0.2.8233)
- tests/component/melder/aether/conduit/test_conduit_component_lock_residuals.py (new, 0.2.8232)
- tests/component/melder/spellbook/test_spellbook_component_direct_spell_cleanup_lock_order.py (new, 0.2.8233)
- release_docs/next_version_release.md; context_compass/system_docs/src_architecture.md, src_components.md and
  their indexes; the graph descriptors of spellbook.py and conduit.py, src_graph.md and its index
- context_compass/system_docs/patches/completed/lock_residuals_2026_10_11/ (archived patch docs)
- context_compass/system_docs/patches/completed/direct_spell_cleanup_lock_order_2026_10_11/ (archived, 0.2.8233)
- the graph descriptors of spell.py and spellbook.py (0.2.8233)
- context_compass/artifacts/lock_residuals_20261011/ (evidence)

## Validation
- New tests: red on 0.2.8231 and green on 0.2.8232, GIL off and on; 20 repeats green (Note 6).
- Full tree on the scratch cut, GIL off: every chunk green (Note 6). Windows tiers and hosted CI: Not run (owner's).
- Post-landing suites on the working tree, GIL off: 5266 passed, 1 xfailed (Note 7).
- Assets and llm_support rebuilt and checked (Note 8).
- 0.2.8233: the hang reproduced on 0.2.8232 and gone on the cut (deadlock probe, root teardown and conjure, GIL off
  and on, Note 13); new tests red on 0.2.8232 and green on 0.2.8233, GIL off and on, 20 repeats green; full tree on
  the cut, GIL off: all 23 chunks green (Note 14); post-landing suites on the tree: 5381 passed, 2 skipped,
  1 xfailed, 2 xpassed (Note 15); assets and llm_support rebuilt and checked (Note 16). Windows tiers and hosted CI:
  Not run (owner's).

## Risks / Rollback Notes
- Owner: "don't fuck up my code". Every change is proven red/green in scratch and the full tree passes before it
  touches the working tree; no drive-by refactors; rollback is reverting the change set's files.

## Applicable Anti-Patterns
- [ ] No sleep-based reproduction presented as deterministic.
- [ ] No reproduction that skips a lock, a claim or a transaction the real operation takes.
- [ ] No behaviour claim from a search hit alone.
- [ ] No defensive guard without contract evidence.
- [ ] No read-side copy where a keyed read or the writers' lock serves (owner rule, predecessor Note 7).

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
  - artifacts/lock_residuals_20261011/
  - system_docs/patches/completed/lock_residuals_2026_10_11/
  - system_docs/patches/active/direct_spell_cleanup_lock_order_2026_10_11/
- DISPOSITION: retain_as_reference (evidence); promote_to_documentation (patch docs, archived at landing)
- CLEANUP_TRIGGER: evidence decided at turn-in.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: which lock or claim each writer and reader holds; mediator claims and windows; SafeGuard ordering
- IF_UNKNOWN: ask user before implementation

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes

- DATETIME: 2026-10-11T19:43:46Z
  TYPE: DECISION
  CLAIM: Owner, chat 2026-10-11, while the residuals were being read: "your really working hard on this very tiny
    edgecase cleanup_spell honestly if you think we should add a mediator call to cleanup spell for the odd chance a
    cleanup happens on a spell that sounds kinda absurd to be honest", "why aren't you just using cleanup_spells lock
    when you cleanup I don't get it", "I mean spells lock", "what even put you on this crusade?". Ruling taken: no
    mediator admission for cleanup_spell; `Spellbook._dispose_spell` holds the spell's own lock for the whole
    decide-and-dispose, in the order Spell.cleanup already takes (spell -> Book), so two disposals of one spell cannot
    interleave. The index-move window stays open by choice: the seams repoint `spell.spell_index` under the Book lock,
    not the spell lock, and the owner judges the remaining race not worth more machinery. Scope cut to two more small
    fixes, each proven first: `Conduit.find_contracted_spell` walks the Book's `_contracted_spells` keys under the
    CONDUIT lock while link and sever write them under the Book lock (and a conduit lock taken under a ward lock is the
    0.2.8231 deadlock pattern); `Spellbook.inspect_spell` walks `frame._conduits` with only its Book lock while root
    registration writes it under the frame lock, and swallows the error into a None. No broad lock audit unless the
    owner asks. The 0.2.8230 snapshots stay: the phase factories do O(n) phase work per spell anyway, inspect_spell
    searches by object identity (no key exists), and the transfer impact walk and the contracted-lookup fallback are
    rare paths whose keyed versions need cross-Book lookups.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4257-4372
  - src/melder/aether/spellbook/spellbook.py:4005-4016
  - src/melder/aether/spellbook/spellbook.py:4181-4192
  - src/melder/aether/spellbook/spell.py:550-654
  - src/melder/aether/conduit/conduit.py:3191-3235
  - src/melder/aether/spellbook/spellbook.py:3011-3090
  - src/melder/aether/spellbook/spellbook.py:2458-2567
  - src/melder/aether/aetheric_frame/aetheric_frame.py:357-420
  IMPACT: Three small changes in two files plus their tests; no transaction, admission or public contract change.
  NEXT: Prove the find_contracted_spell and inspect_spell races with an unforced stress on a scratch copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T20:02:07Z
  TYPE: MEASURE
  CLAIM: Both residuals reproduce on base 0.2.8231 with the GIL off, through public calls only (nothing patched or
    paused). `Conduit.find_contracted_spell` raised RuntimeError "dictionary changed size during iteration" 762 times
    and "dictionary keys changed during iteration" 93 times in 1,566,827 calls while eight peers linked to and severed
    from the owner 3,200 times. `Spellbook.inspect_spell` answered None for a registered provider 227 times in 45,090
    calls while 300 Books were conjured and torn down in the frame (its catch-all turns the walk's error into None).
    With the GIL on, the same runs hit neither: 0 of 156,177 and 0 of 2,933,818. A first, unlogged run before this
    note gave 807 + 63 and 157 of 78,226.
  EVIDENCE:
  - context_compass/artifacts/lock_residuals_20261011/residual_stress.py:1-124
  - context_compass/artifacts/lock_residuals_20261011/runs/base_contracted_gil0.log:1-4
  - context_compass/artifacts/lock_residuals_20261011/runs/base_contracted_gil1.log:1-4
  - context_compass/artifacts/lock_residuals_20261011/runs/base_inspect_gil0.log:1-4
  - context_compass/artifacts/lock_residuals_20261011/runs/base_inspect_gil1.log:1-4
  - src/melder/aether/conduit/conduit.py:3191-3235
  - src/melder/aether/spellbook/spellbook.py:2458-2567
  IMPACT: Both are real on the free-threaded build the library targets; with the GIL they are not hit in these runs.
    The regression tests must force the interleaving deterministically rather than rely on this stress.
  NEXT: Read cleanup_spell's disposal path against the Book's own cleanup before taking the spell lock across it.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-11T20:03:45Z
  TYPE: CONFLICT
  CLAIM: Holding the spell's own lock across `_dispose_spell` (Note 1's ruling) inverts two existing lock orders, so
    a root-conduit or frame teardown racing `cleanup_spell` would hang instead of raising. The disposal takes the
    Book lock (`cleanup_and_remove_spell`, the inactive branch) and the frame lock (`_remove_spells_from_aether` ->
    `AethericFrame.unregister_conduit_spells`; `_destroy_spell_index` -> `_remove_single_spell_index`). The other way
    round already exists: `Spellbook.cleanup` holds the Book lock while `_cleanup_spells` calls every `Spell.cleanup`
    (spell lock), root teardown reaches it from `_cleanup_normal_conduit`, and frame teardown runs that under the
    frame lock (frame -> Book -> spell). Today's `_dispose_spell` never holds the spell lock while it waits for the
    Book or frame lock, so the same race raises an error rather than hanging. The 0.2.8231 comment in
    `_dispose_spell` ("the spell's own lock is taken before this Book's lock ... so it is never taken under it") is
    wrong - Book cleanup takes it under the Book lock - but that code nests neither lock, so it stays safe. A direct
    `Spell.cleanup()` on a live owned spell already takes spell -> Book (pre-existing, out of scope).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:365-389
  - src/melder/aether/spellbook/spellbook.py:546-590
  - src/melder/aether/spellbook/spell.py:550-654
  - src/melder/aether/spellbook/spellbook.py:591-715
  - src/melder/aether/aether.py:2703-2725
  - src/melder/aether/aetheric_frame/aetheric_frame.py:1205-1225
  - src/melder/aether/aetheric_frame/aetheric_frame.py:230-330
  - src/melder/aether/conduit/conduit.py:1070-1080
  - src/melder/aether/spellbook/spellbook.py:4039-4084
  - src/melder/aether/spellbook/spellbook.py:4257-4372
  IMPACT: The spell-lock fix would trade a rare error for a rare hang. Options: (1) keep the code, correct the comment
    and document that disposing one spell from two threads at once is unsupported; (2) a "being disposed" mark
    checked and set under the Book lock the decision already takes, so a second simultaneous call raises "already
    been disposed" - no new lock edge, one new Book field; (3) the spell lock across the disposal - rejected here.
    Recommendation: (1). A second simultaneous call today raises or repeats steps that are idempotent where read
    (`SpellSystemStates.unregister_index`, `_unregister_owned_spell_id`); the destroy fan-out and the crystallizer
    emits on a repeat are UNKNOWN (not read).
  NEXT: Ask the owner for (1) or (2); fix find_contracted_spell and inspect_spell meanwhile.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T20:10:58Z
  TYPE: DECISION
  CLAIM: Owner, answering Note 3's question: "dude fix the bugs you found if you can I'm just saying if you found
    bugs fix them but make sure performance doesn't break". Scope taken, one notch: (A) `find_contracted_spell`
    walks a one-call copy of the Book's contracted peer ids and drops its conduit lock (link and sever by a peer
    never took it; holding it made the parked branch nest conduit -> spell); (B) `inspect_spell` walks a one-call
    copy of the frame's conduits; (D) `inspect_spell` holds its Book lock only for its own Book's spells - today it
    holds it through `Aether._check_for_spell`, which takes frame locks (`AethericFrame.has_spell`), while frame
    teardown takes frame -> Book (pre-existing since HEAD, a hang against a racing frame teardown); (C)
    `_dispose_spell` marks the spell id as being disposed under the Book lock its decision already holds and
    releases the mark when it finishes, so a second simultaneous `cleanup_spell` of one spell raises instead of
    repeating the disposal - no new lock edge; (F) the wrong 0.2.8231 comment is corrected. Left, recorded: (E) a
    direct `Spell.cleanup()` of a live owned spell holds the spell lock into `cleanup_and_remove_spell` (spell ->
    Book) against Book teardown's Book -> spell; moving that call outside the spell lock would stop it serializing
    two direct cleanups, which it does correctly today, so it needs its own design. Performance: none of the three
    is on the meld path; A takes a lock less, D holds one for less time, C adds one set probe under a held lock.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:3191-3235
  - src/melder/aether/spellbook/spellbook.py:2955-3009
  - src/melder/aether/spellbook/spellbook.py:2458-2567
  - src/melder/aether/aether.py:2533-2609
  - src/melder/aether/aetheric_frame/aetheric_frame.py:862-876
  - src/melder/aether/aetheric_frame/aetheric_frame.py:230-300
  - src/melder/aether/conduit/conduit.py:1070-1080
  - src/melder/aether/spellbook/spellbook.py:365-389
  - src/melder/aether/spellbook/spellbook.py:4257-4372
  - src/melder/aether/spellbook/spell.py:582-587
  IMPACT: Three methods in two files plus one Book field; tests force each interleaving; patch docs before code.
  NEXT: Write the patch docs (lock_residuals_2026_10_11) and the patch-to-step mapping, then edit the scratch copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T20:14:08Z
  TYPE: PLAN
  CLAIM: Patch docs written (lock_residuals_2026_10_11: architecture, Conduit Runtime and Spellbook Core component
    patches, code description) and consumed in that order. One addition while writing them: `Conduit.inspect_spell`
    holds the conduit lock across `Spellbook.inspect_spell`, and frame teardown takes frame -> conduit
    (`AethericFrame._cleanup_data_structures` -> `Conduit.permanent_cleanup` -> `cleanup` under the conduit lock), so
    D also drops that conduit lock. Mapping, patch section -> step -> validation:
    architecture invariant 1 (A) / Conduit patch -> find_contracted_spell: no conduit lock, `list(...)` of the peer ids
    -> a peer links to the owner between two peers of the walk, no RuntimeError (red on 0.2.8231);
    invariant 1 (B) / Spellbook patch -> inspect_spell stage 2 walks `list(frame._conduits.values())` -> a root
    registers while the walk reads another Book: the provider's id still answers (red);
    invariant 2 (D) / both patches -> Book lock for stage 1 only, no conduit lock in Conduit.inspect_spell -> neither
    lock held inside `Aether._check_for_spell` (red);
    invariant 3 (C) / Spellbook patch -> `_disposing_spell_ids` checked and set in the decision, discarded in finally
    -> a second cleanup_spell while the first is parked (active: in invalidate_spell; inactive: in Spell.cleanup)
    raises the new RuntimeError, the first completes, one destroy emitted (red);
    F -> comment corrected (review). Then the full tree with the GIL off and a before/after timing of the three calls.
  EVIDENCE:
  - context_compass/system_docs/patches/active/lock_residuals_2026_10_11/architecture_patch.md:1-61
  - context_compass/system_docs/patches/active/lock_residuals_2026_10_11/code_description_patch_lock_residuals.md:1-31
  - src/melder/aether/conduit/conduit.py:3340-3366
  - src/melder/aether/conduit/conduit.py:568-614
  - src/melder/aether/aetheric_frame/aetheric_frame.py:283-300
  IMPACT: Two src files, four methods and one Book field; every change has a red test; no meld-path code.
  NEXT: Copy base to /tmp/cc_res/cand and apply the edits with a reviewable script.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-11T20:27:31Z
  TYPE: MEASURE
  CLAIM: The 0.2.8232 cut (A-D and F) is applied to /tmp/cc_res/cand by apply_0_2_8232.py. The five new component
    tests fail on 0.2.8231 and pass on the cut, GIL off and on: A raises "dictionary changed size during iteration";
    B answers None; D finds the Book and conduit locks held at all three registry checks; C-active lets the second call
    run the whole disposal; C-parked raises "is not owned by this spellbook". 20 repeats on the cut pass (10 GIL off,
    10 on). The full tree passes with the GIL off (every chunk rc=0; comp_aether 1323 = 1318 + 5 new). The residual
    stress is clean on the cut with the GIL off: 0 of 2,392,566 lookups failed and 0 of 48,351 inspections were
    wrong. Cost, single thread, interleaved runs: find_contracted_spell 1.31 -> 1.28-1.29 us; inspect_spell (20 other
    Books) 7.9-8.0 -> 8.0-8.1 us; cleanup_spell about 20 us both, the run-to-run medians overlapping (base
    19.6-23.6, cut 20.1-22.2); the added work, measured alone, is 0.1 us (a set probe and add inside the decision's
    lock, one more lock section to clear the mark). The meld path is untouched (no change outside the four methods,
    the field and its cleanup).
  EVIDENCE:
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8232/apply_0_2_8232.py:1-432
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8232/runs/newtests_base_gil0.log:1-225
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8232/runs/newtests_cand_gil0.log:1-10
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8232/runs/newtests_cand_repeats.log:1-20
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8232/runs/summary_full_cand_0_2_8232_gil0.txt:1-30
  - context_compass/artifacts/lock_residuals_20261011/runs/cand_contracted_gil0.log:1-4
  - context_compass/artifacts/lock_residuals_20261011/runs/cand_inspect_gil0.log:1-4
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8232/runs/bench_0_2_8232.log:1-98
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8232/runs/claim_overhead_micro.log:1-4
  IMPACT: The cut is ready to land as 0.2.8232; no performance regression measured on the changed calls.
  NEXT: Land: copy the two src files and the new test into the working tree, notch, then docs, graph, assets, bundles.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-11T20:41:04Z
  TYPE: FACT
  CLAIM: Landed as 0.2.8232 (notched from 0.2.8231). conduit.py and spellbook.py in the working tree are byte-identical
    to the tested cut; the new component test file is in place; `__version__` is "0.2.8232". The running release note
    extends the "Index links, contract reads and binds across frames" section with three bullets and its packaging
    lines. src_architecture and src_components carry the invariant, failure mode, component rules, code-map extents
    (7533 and 7178 lines) and handoff; both indexes regenerated and checked. Citations into the two files were remapped
    so they point where they pointed before (16 and 21). Several were already stale at 0.2.8231, among them the
    SpellIndex verb-chain citations (`spellbook.py:3843` named as `_add_to_spell_index`, `conduit.py:5258-5260` as
    the link type check) and `spellbook.py:6516-6559`/`6772`; they are left for a citation pass. Graph: extract
    (206 stale = 204 pre-existing + Spellbook, Conduit), the two nodes' responsibilities authored and accepted,
    assemble and --check OK. Patch docs archived to
    system_docs/patches/completed/lock_residuals_2026_10_11/. Post-landing suites on the working tree, GIL off: 5266
    passed, 1 xfailed. A first run failed 3 test_method_inspector tests
    because pytest loaded the tree's Windows-built rewritten pycs (their co_filename is a Windows path, so the tests
    could not read their own source); with PYTHONPYCACHEPREFIX the file passes 46/46.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:70-128
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8232/src_0.2.8232.diff:1-485
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8232/runs/assemble_check_0_2_8232.log:1-4
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8232/runs/post_landing_gil0.log:1-104
  IMPACT: The change set is complete except the generated assets and bundles, which are rebuilt last.
  NEXT: Sync the boards (row, notch notice, artifacts), then rebuild and check the assets and llm_support.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-11T20:46:33Z
  TYPE: MEASURE
  CLAIM: Rebuilt last, from the repository root on 3.14t: the build assets (agent documentation 462 entries, bind
    guard 622, system documents 4, all v0.2.8232) and the whole-repository LLM bundles (src 579, tests 1079, other 404
    files; --include-untracked because the new test file and earlier lanes' files are not yet tracked). Both
    `--check` runs print only OK lines; no .git/index.lock was left. The new tests pass on the landed tree with the GIL
    off and on.
  EVIDENCE:
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8232/runs/assets_build.log:1-3
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8232/runs/assets_check.log:1-3
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8232/runs/llm_build.log:1-4
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8232/runs/llm_check.log:1-3
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8232/runs/post_landing_gil0.log:105-106
  IMPACT: 0.2.8232 is complete in the working tree; acceptance, commit and push, Windows tiers and hosted CI are the
    owner's.
  NEXT: Report to the owner and wait for acceptance or redirect.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8


- DATETIME: 2026-10-11T21:25:01Z
  TYPE: FACT
  CLAIM: E confirmed from source. `Spell.cleanup()` reaches its routing branch only from a caller outside Melder:
    every internal cleanup sets `_spellbook_cleanup = True` first (Book teardown, `cleanup_and_remove_spell` itself,
    the parked disposal in `_dispose_spell`, Bind's unpublished-spell retirement). The branch holds the spell lock
    across the whole of `cleanup_and_remove_spell`: its Book-locked section, then the risk-manager call, the frame
    (`_remove_spells_from_aether`, frame locks - Note 3), the Book lock again with the Nexus record removal
    (`_unregister_owned_spell_id`) and the frame lookup release. Two paths take the spell lock under the Book lock:
    Book teardown (`_cleanup_spells`; root and frame teardown reach it, Note 3) and conjure's ownership stamping
    (`define_conduit_into_spells` -> `Spell._add_owned_conduit`). Transfer was suspected and is not one: its
    SafeGuard section takes no spell lock and it stamps ownership after leaving it. So a direct cleanup that passes
    the Book's cleaned check just before teardown or conjure takes the Book lock hangs both threads; one that starts
    after the teardown has begun raises "Spellbook has already been cleaned.". Two side findings (not lock order),
    recorded only: (F2) `cleanup_and_remove_spell` - so a direct `Spell.cleanup()` too - of the active member of a
    multi-member index unregisters and cleans the index and never touches `_inactive_spells`, so the index's parked
    members stay registered on a cleaned index (`cleanup_spell` refuses that case). (F3) Book teardown cleans only
    active spells: `_cleanup_spells` walks `_spells`, then `_inactive_spells` is cleared without `cleanup()` on the
    parked Spells, and an index whose members are all parked is never cleaned. UNKNOWN (owner rule: no broad audit):
    meld-time reruns hold the spell lock into `_phase_run_lock`; whether any phase then takes the Book lock is unread.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:550-650
  - src/melder/aether/spellbook/spellbook.py:600-719
  - src/melder/aether/spellbook/spellbook.py:368-392
  - src/melder/aether/spellbook/spellbook.py:403-598
  - src/melder/aether/spellbook/spellbook.py:1221-1273
  - src/melder/aether/spellbook/spellbook.py:4295-4440
  - src/melder/aether/spellbook/spellbook_creation_system.py:1332-1384
  - src/melder/aether/spellbook/spell.py:1474-1524
  - src/melder/aether/spellbook/bind/bind.py:432-452
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1440-1500
  - src/melder/aether/spellbook/bind/spell_index.py:118-138
  - src/melder/aether/conduit/meld/meld.py:893-950
  - src/melder/aether/spellbook/spellbook_creation_system.py:2086-2128
  IMPACT: The routing branch is the only spell -> Book (and spell -> frame) edge found; taking it out of the spell
    lock removes the hang against both partners. F2 and F3 are separate cleanup gaps for the owner to rule on.
  NEXT: Write the E proposal as a PLAN note and ask the owner to confirm it before any patch doc or code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9


- DATETIME: 2026-10-11T21:25:01Z
  TYPE: PLAN
  CLAIM: Proposed fix for E, one notch (0.2.8233), pending the owner's confirmation. (1) `Spell.cleanup()` keeps its
    decision under the spell lock; when the spell must leave through its Book it captures the Book and a per-spell
    removal lock there (new last slot `_removal_lock`, created on first direct cleanup, None until then), releases the
    spell lock, re-checks `_cleaned` under the removal lock and calls `cleanup_and_remove_spell`. Nothing in Melder
    takes the removal lock, so it is never held under another lock; two direct cleanups of one spell still serialize
    (the second waits, then returns), which the spell lock gives today. (2) `cleanup_and_remove_spell` re-checks the
    Book inside its locked section: a Book torn down while the call waited (the window that hangs today) returns when
    that teardown cleaned the spell and otherwise raises the Book's cleaned RuntimeError, instead of an AttributeError
    on the deleted maps. (3) Docstrings: `Spell.cleanup`, `cleanup_and_remove_spell`, and the `cleanup_spell` /
    `_dispose_spell` text that states the spell -> Book order. Tests (component, new file): the Book is reached with
    the spell lock free (red today by an `_is_owned()` probe, no hang); Book teardown and conjure stamping racing a
    parked direct cleanup both finish (red today by the probe, without starting the hang); two direct cleanups run
    the removal once and both return. Cost: one slot store per Spell at bind; nothing on the meld path. Then the
    usual lane: patch docs and mapping, scratch, red/green, full tree, landing, system docs, graph, release note,
    assets and llm_support last. F2 and F3 stay out unless the owner adds them.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:550-650
  - src/melder/aether/spellbook/spell.py:243-300
  - src/melder/aether/spellbook/spellbook.py:600-719
  - src/melder/aether/spellbook/spellbook.py:4233-4440
  IMPACT: Two src files (spell.py, spellbook.py), no public signature change, no new lock under any existing lock.
  NEXT: Ask the owner to confirm E (and whether F2/F3 join 0.2.8233); on confirmation write the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9


- DATETIME: 2026-10-11T21:32:28Z
  TYPE: DECISION
  CLAIM: Owner, answering "What should 0.2.8233 include?" (chat, 2026-10-11): "E: direct cleanup lock order
    (Recommended)" only. Note 10's plan is confirmed as written: `Spell.cleanup()` routes through its Book outside the
    spell lock, serialized per spell by a removal lock created on first direct cleanup; `cleanup_and_remove_spell`
    re-checks the Book under its lock; docstrings that state the spell -> Book order are corrected. F2 (headless index
    on a direct removal) and F3 (parked spells not cleaned at Book teardown) stay recorded and out of this notch.
    Patch id: direct_spell_cleanup_lock_order_2026_10_11.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-11_close_lock_residuals_and_evaluate_mediator_admission_task.md:412-437
  IMPACT: Scope is fixed to two src files plus their tests and docs; one notch (0.2.8233).
  NEXT: Write the patch docs (architecture, Binding Pipeline and Spellbook Core components, code description) and the
    patch-section -> step -> validation mapping, then build the scratch trees.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8


- DATETIME: 2026-10-11T21:38:23Z
  TYPE: PLAN
  CLAIM: Patch docs written (direct_spell_cleanup_lock_order_2026_10_11: architecture, Binding Pipeline and Spellbook
    Core component patches, code description), linked here and on the artifact board, and consumed in that order.
    Mapping, patch section -> step -> validation: invariant 1 / Binding Pipeline patch -> `Spell.cleanup` routes
    through `_direct_removal_route()` and calls `cleanup_and_remove_spell` under `_removal_lock` with `_lock` released
    -> the spell lock is free at the Book call (`_is_owned()` probe, red on 0.2.8232), and root teardown and conjure
    stamping finish while a direct cleanup waits (probe-gated so the red run cannot hang); invariant 2 -> the removal
    lock serializes direct cleanups -> two direct cleanups run the removal once (preservation, green on both);
    invariant 3 -> Book-driven teardown unchanged -> existing Spell unit tests with the stub Book and the Book teardown
    tests; invariant 4 / Spellbook Core patch -> `cleanup_and_remove_spell` re-checks the Book under its lock -> a call
    parked after `check_cleaned()` while the Book is torn down returns for the cleaned Spell and raises the cleaned-Book
    error for an id (AttributeError on 0.2.8232); docstring corrections in `cleanup_spell` / `_dispose_spell` -> review.
    Then the full tree with the GIL off, and before/after timing of bind, Book teardown and a direct cleanup.
  EVIDENCE:
  - context_compass/system_docs/patches/active/direct_spell_cleanup_lock_order_2026_10_11/architecture_patch.md:1-59
  - context_compass/system_docs/patches/active/direct_spell_cleanup_lock_order_2026_10_11/code_description_patch_direct_spell_cleanup.md:1-30
  - src/melder/aether/spellbook/spell.py:550-650
  - src/melder/aether/spellbook/spellbook.py:600-719
  IMPACT: Two src files and one new test file; every invariant has a test; nothing on the meld path.
  NEXT: Build /tmp/cc_res/base and cand from the 0.2.8232 working tree, write apply_0_2_8233.py and the new tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8


- DATETIME: 2026-10-11T21:47:57Z
  TYPE: MEASURE
  CLAIM: E is proven, not only read, and the cut fixes it. `deadlock_probe.py` parks a direct `Spell.cleanup()` right
    after the Book's real cleaned check and releases it once a second thread holds the Book lock: on 0.2.8232 both
    threads are still alive 10 s later against a root teardown and against a conjure, GIL off and on (the parked
    thread holds the spell lock); on the 0.2.8233 cut (apply_0_2_8233.py on /tmp/cc_res/cand) all four runs complete.
    The conjure partner is wider than Note 9 said: conjure holds the Book lock across its whole creation system, and
    the structural full-hit hydration (`Spell._add_build_details`) already takes the spell lock there, before
    `define_conduit_into_spells`; the fix covers every such path because the direct cleanup no longer holds the spell
    lock while it waits. The six new component tests fail on 0.2.8232 and pass on the cut, GIL off and on: the probe
    test, root teardown and conjure fail at the spell-lock probe without starting the hang, the two Book-call tests
    raise AttributeError ("no attribute '_spells_by_id'"), and the two-cleanups preservation test passes on both.
  EVIDENCE:
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8233/deadlock_probe.py:1-103
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8233/runs/deadlock_probe_gil0.log:1-4
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8233/runs/deadlock_probe_gil1.log:1-4
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8233/runs/newtests_base_gil0.log:1-167
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8233/runs/newtests_cand_gil0.log:1-2
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8233/apply_0_2_8233.py:1-295
  - src/melder/aether/spellbook/spell.py:1525-1565
  IMPACT: The cut is correct for E on both builds; what remains is breadth (full tree), cost, then landing.
  NEXT: 20 repeats of the new tests on the cut, then the full tree with the GIL off, then timing.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9


- DATETIME: 2026-10-11T21:52:27Z
  TYPE: MEASURE
  CLAIM: The cut holds across the tree and costs nothing that matters. 20 repeats of the new tests pass (10 GIL off,
    10 on). The full tree on the cut with the GIL off passes in every one of the 23 chunks (comp_sb 819 = 813 + 6 new;
    the other counts equal the 0.2.8232 run). Cost, single thread, three interleaved base/cut pairs of 7 rounds: bind
    303-309 us both; root teardown 20.4-21.7 us per spell on both (the extra spell-lock pair per spell is inside the
    noise); warm meld by id 475-494 ns vs 473-479 ns (untouched path); a direct `Spell.cleanup()` 18.1-18.4 us ->
    19.1-22.6 us medians (minimums 16.3-17.7 -> 17.7-18.0 us), about 1 us, which is the first-use RLock, the removal
    lock and one more short spell-lock section on a call that is never on the meld path.
  EVIDENCE:
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8233/runs/newtests_cand_repeats.log:1-20
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8233/runs/summary_full_cand_0_2_8233_gil0.txt:1-25
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8233/runs/bench_0_2_8233.log:1-30
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8233/bench_0_2_8233.py:1-81
  IMPACT: Ready to land as 0.2.8233.
  NEXT: Land: copy spell.py, spellbook.py and the new test into the working tree, notch, then release note, system
    docs, graph, patch archive, boards, post-landing suites, and assets and llm_support last.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8


- DATETIME: 2026-10-11T22:00:31Z
  TYPE: FACT
  CLAIM: Landed as 0.2.8233 (notched from 0.2.8232). spell.py and spellbook.py in the working tree are byte-identical
    to the tested cut and the new component test file is in place; `__version__` is "0.2.8233". The running release
    note adds a bullet and the third changed error type to "Index links, contract reads and binds across frames" and
    a packaging line; its header and rebuild line name 0.2.8233. src_architecture and src_components carry the
    invariant (the 0.2.8232 entry's recorded residual now points at it), the failure mode, the component rules, the
    code-map extents (spell.py 1854, spellbook.py 7564) and the handoff; 12 and 15 citations into the two files were
    remapped so they point where they pointed before; both indexes regenerated and checked (58 sections / 3973 lines,
    149 / 11041); no citation is out of bounds. Graph: extract (206 stale = 204 pre-existing + Spell, Spellbook), the
    two nodes authored (Spell also owns `_removal_lock`) and accepted, assemble and --check OK (27735 lines). Patch
    docs archived to system_docs/patches/completed/direct_spell_cleanup_lock_order_2026_10_11/. Post-landing suites on
    the working tree, GIL off (spellbook unit and component, aether component, spellbook and conduit integration):
    5381 passed, 2 skipped, 1 xfailed, 2 xpassed; the new tests pass on the tree with the GIL off and on. One slip,
    recorded: a `git status` was appended by mistake to the post-landing command (it may have run as the tool cut the
    call at 120 s); no .git/index.lock exists afterwards.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:70-141
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8233/src_0.2.8233.diff:1-293
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8233/runs/remap_0_2_8233.log:1-29
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8233/runs/index_0_2_8233.log:1-6
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8233/runs/assemble_check_0_2_8233.log:1-4
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8233/runs/post_landing_gil0.log:1-78
  IMPACT: The change set is complete except the generated assets and bundles, which are rebuilt last.
  NEXT: Rebuild and check the build assets and llm_support, then sync the ticket and boards to review.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8


- DATETIME: 2026-10-11T22:03:03Z
  TYPE: MEASURE
  CLAIM: Rebuilt last, from the repository root on 3.14t: the build assets (agent documentation 462 entries, bind
    guard 622, system documents 4, all v0.2.8233) and the whole-repository LLM bundles (src 579, tests 1080, other 404
    files; --include-untracked because the new test files are not yet tracked). Both `--check` runs print only OK
    lines; no .git/index.lock was left. 0.2.8233 is complete in the working tree.
  EVIDENCE:
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8233/runs/assets_build.log:1-3
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8233/runs/assets_check.log:1-3
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8233/runs/llm_build.log:1-4
  - context_compass/artifacts/lock_residuals_20261011/scratch_0.2.8233/runs/llm_check.log:1-3
  IMPACT: Acceptance, commit and push, Windows tiers and hosted CI are the owner's; F2 and F3 stay recorded (Note 9).
  NEXT: Report to the owner and wait for acceptance or redirect.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
REVIEW (melder_1, 2026-10-11T20:41:33Z): 0.2.8232 landed. find_contracted_spell walks a one-call copy of the Book's
contracted peer ids with no lock; inspect_spell (Book and Conduit) walks a one-call copy of the frame's conduits and
holds no Book or conduit lock while it asks the frames; cleanup_spell refuses a second disposal of a spell while the
first runs, through an id mark under the Book lock (the spell lock would have hung against Book and frame teardown,
Note 3).
REVIEW (melder_1, 2026-10-11T22:03:34Z): 0.2.8233 landed on top (owner chose E only, Note 11). A direct
Spell.cleanup() decides under the spell lock and runs the Book removal outside it, under a per-spell removal lock
nothing else takes, so it
no longer hangs against Book, root or frame teardown or a conjure of its Book (proven hang on 0.2.8232, Note 13);
cleanup_and_remove_spell re-checks a Book torn down while it waits. Cost: about 1 us on a ~18 us direct cleanup;
bind, teardown and meld unchanged (Note 14).
Recorded, not changed: F2 - a direct removal of a multi-member index's active spell leaves its parked members on a
cleaned index; F3 - Book teardown never cleans parked spells (Note 9); meld-time reruns under the spell lock are
not audited (Note 9); the cleanup_spell index-move window (owner, Note 1); stale src citations from before 0.2.8231
(Note 7). Owner-owed: acceptance, git add -A (two new test files, two archived patch folders, this evidence folder),
commit and push, Windows tiers, hosted CI.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
