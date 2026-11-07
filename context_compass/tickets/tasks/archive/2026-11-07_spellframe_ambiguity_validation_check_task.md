> **Moved to GitHub Issues on 2026-11-07:** https://github.com/Synaptic724/melder/issues/245
> This file is read-only history; the Issue is the live record.



# Task: spellframe_ambiguity_validation_check - a Phase 4 or Phase 6 check for spells sharing a spellframe

## Metadata
- Task ID: TASK-2026-11-07-spellframe_ambiguity_validation_check
- Story: none - an epic-level task of EPIC-2026-11-07-spellframe_hides_the_concrete_class
- Status: in_progress
- Owner: Mark (owner)
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-11-07T10:03:26Z
- Updated: 2026-11-07T18:37:27Z

## Objective
The owner's check (chat 2026-11-07): "a phase 4 or phase 6 check to see if multiple spells are bound with a
spellframe without a binding_name and that should help the user situation". His rule (chat 2026-11-07, "lets do
3"): (a) after T2, a consumer annotated with a class that is bound only under a spellframe or only under a binding
name (T2's rule, E2/E3) is refused at conjure by a Phase 4 error that names where it is bound - frame and binding
names - and the lookup to use, and a `SpellMap(spell=X)` that misses X for the same reason names it the same way;
(b) two spells at one address stay refused on every path - two spells under one spellframe with no binding_name,
and two spells of one name with neither - with a check added wherever a path admits one. Each reports through the
readable validation report with its remedy.

## Ticket Contract
- ENTRY_GATE: the owner's rule (Notes, 2026-11-07); a board row routes here; T2 landed, for part (a).
- EXECUTION_BOUNDARY: part (a), one Phase 4 strategy reading what Phase 3 records for a class annotation that only
  framed spells match; part (b), the paths that register or expose a spell at an address (bind, bind_inactive,
  index moves, contracted copies, scan), a check added only where one admits a second spell; their tests and docs;
  the release note and notch; the rebuild last.
- DEPENDENCIES: EPIC-2026-11-07-spellframe_hides_the_concrete_class; T2 for part (a); none for part (b).
- EXIT_GATE: part (a) refuses with code, message and remedy naming the frame; part (b) pinned by regression tests on
  every path, any new check with code, message and remedy; tests pass, the GIL off and on.
- FAILURE_ESCALATION: DECISION_REQUEST when a path admits two spells at one address by design (a parked version, a
  borrowed copy), or when part (a) would refuse a world the owner wants to conjure.

## Scope Boundaries
- In scope: the check, its message and remedy, its tests and docs.
- Out of scope: changing Bind's address refusal.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: T1 and T2 done; the owner's "lets focus on the other fixes we can do" (chat 2026-11-07,
  15:4xZ) after T2; part (b) first, per the settled order.
- earlier: draft -> ready (the owner set the rule, chat 2026-11-07; part (a) waited for T2, part (b) for T1).

## Steps / Checklist
- [x] The owner confirms the situation and the severity (DECISION note, 2026-11-07T10:22:44Z).
- [ ] Part (a): the Phase 4 strategy, with a rich docstring, over what Phase 3 records for a class annotation that
      only framed or named spells match; the error names each frame and binding name and the lookup to use
      (a Protocol annotation, `SpellMap(spellframe=..., binding_name=...)`, `SpellMap(Class, binding_name=...)`).
- [ ] Part (a): the SpellMap miss (Phase 3's "could not be resolved") names where X is bound when it is bound
      under a spellframe or a binding name.
- [x] Part (b): read each path's address refusal; regression tests for both shapes on every path; a check where one
      is missing; the stale example probe `test_probe_two_visible_spells_may_not_share_a_name` (it asserts the
      pre-0.2.8206 rule) brought to the current rule. [Done 2026-11-07T16:54:46Z: 115 regression cases; the one
      admitting path, a cross-aetheric-frame transfer, refused at 0.2.8280 on the owner's ruling; docs merged.]
- [ ] Component tests for the flagged and the unflagged shapes; docs; release note; notch; rebuild last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- The validation strategy, its tests and docs, the release-note entry.

## Files / Paths Impacted
- part (a), per patch hidden_provider_2026_11_07 (Changed-Components Matrix):
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py and the `SpellSocketDescriptor` module
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/hidden_provider_strategy.py (new),
    src/melder/aether/spellbook/spell_compiler/validation/hidden_provider_report.py (new), validation_system.py,
    strategies/required_holes_strategy.py, strategies/ambiguous_provider_strategy.py
  - src/melder/aether/spellbook/spell_compiler/system/validation/empty_collection_strategy.py
  - src/melder/utilities/custom_exceptions/unresolved_input_error.py
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py,
    src/melder/utilities/caching_system/caching_system.py (generation 27)
  - change_control_manager.py (`_default_dirty_marker`), spellbook.py (`_add_contracted_spell`),
    spell_system_states.py (`_extract_collection_frame_keys`)
  - src/melder/__version__.py, release_docs/next_version_release.md, the tests the patch lists, the system docs
- part (b): done - conduit.py (`transfer_spell_ownership`) and its tests (Notes 2026-11-07T16:53:42Z)

## Validation
- Not run.
- Recommended commands:
  - `.venv_new/Scripts/python.exe -X gil=0 -m pytest tests -q` and the same with `-X gil=1`

## Risks / Rollback Notes
- An error-severity check refuses worlds that conjure today; a warning reports through `validation_warnings=True`.

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

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/duplicate_address_paths_20261107/ (part (b): the path x shape probe and its runs)
  - system_docs/patches/completed/transfer_within_one_frame_2026_11_07/ (merged; the lane's record)
  - system_docs/patches/active/hidden_provider_2026_11_07/ (part (a): the patch - architecture, six component
    patches, two code-description patches; read in that order 2026-11-07T18:23:28Z)
  - artifacts/hidden_provider_20261107/ (part (a): the design probes - hidden_class_probe.py, the emulation plugin
    modes 1-2, order_b_check.py - and their runs on 0.2.8280; the after-runs land beside them)
- DISPOSITION: retain_as_reference (the probe folders); promote_to_documentation (the patches)
- CLEANUP_TRIGGER: none - the probes are re-run whenever an address path or the class-lookup rule changes; the
  active patch moves to patches/completed/ at its docs merge

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - which spellframe situation the check flags
- IF_UNKNOWN: ask user before implementation

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; filed 2026-11-07T10:03:26Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-11-07T10:03:26Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: Which situation the check flags. Melder already refuses two spells at one address - a second spell bound
    under `Greeter` with no binding name raises at bind - so "multiple spells under a spellframe without a binding
    name" cannot be registered today. Candidates: (1) one frame holding several spells while a consumer asks by the
    frame - today AMBIGUOUS_PROVIDER at that consumer; (2) a frame whose spells all carry binding names, so
    `meld(spellframe=...)` alone finds nothing; (3) after T2, a consumer asking by class for a class bound only
    under a frame - it compiles unresolved, and the check names the frame to ask by. Severity: error or warning.
  EVIDENCE:
  - context_compass/artifacts/dependency_watchers_20261107/runs/interface_resolution_check_0_2_8277.txt:1-51
  IMPACT: The rule decides the phase, the facts the strategy reads and whether worlds that conjure today refuse.
  NEXT: The owner's answer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T10:22:44Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner set the rule (chat 2026-11-07): "sure 2 spells with the same name without differentiation, 2
    spells with the same spellframe without a binding_name, I think its called binding name, you can add these or
    extend various features for this, if we don't already have it you can place it where you need to, lets do 3".
    (a) Candidate 3 at error severity, in Phase 4 - the recommendation as put to him, not objected to: after T2 a
    consumer annotated with a class bound only under a spellframe is refused at conjure, the error naming the frame
    and binding names to ask by (today such a meld would raise UnresolvedInputError, "nothing registered provides
    it"). (b) Two spells at one address stay refused on every path: one spellframe with no binding_name (refused at
    bind, measured on 0.2.8277) and one name with no spellframe or binding_name (UNKNOWN - the architecture doc
    names bind's address claim and Phase 4's DUPLICATE_SPELL_NAME; not measured); a check goes in wherever a path
    admits one. Candidates 1 (already AMBIGUOUS_PROVIDER) and 2 (warning-only) are not taken.
  EVIDENCE:
  - context_compass/artifacts/dependency_watchers_20261107/runs/interface_resolution_check_0_2_8277.txt:1-51
  - context_compass/system_docs/src_architecture.md:2188-2192
  - context_compass/system_docs/src_architecture.md:2913-2919
  IMPACT: T3 has two parts: (a) depends on T2's strict model and needs Phase 3 to record the framed candidates of a
    class annotation it no longer matches; (b) is independent of T2 and is mostly verification plus tests.
  NEXT: T1's inventory first (it reads the matchers part (a) builds on); part (b) after T1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T11:57:30Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Part (a) widens with T2's rule, under the owner's licence for this task ("you can add these or extend various
    features for this, if we don't already have it you can place it where you need to"): since a binding name hides
    a class from class lookups too (E2/E3, chat 2026-11-07), the error covers a class bound only under a binding
    name, and Phase 3's SpellMap miss names where X is bound. Today such a consumer fails at meld with
    UnresolvedInputError "nothing registered provides it", which misleads when the class is registered under a frame
    or a name. Part (b) adds the stale example probe T1 found failing on 0.2.8277.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-11-07_inventory_class_resolution_of_framed_spells_task.md:409-426
  - context_compass/system_docs/src_architecture.md:2913-2919
  - UX_and_AIX_experiences/pytest_examples/test_expert_probes.py:992-1026
  IMPACT: Part (a) reads both kinds of hidden candidate; the SpellMap message is a Phase 3 change.
  NEXT: After T2: part (b) first (independent of T2), then part (a).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T15:06:23Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: T2 landed (0.2.8278, uncommitted), so part (a) is unblocked; part (b) stays first. Two messages part (a)
    should cover, found by T2's system-docs merge on 0.2.8278 (measured): EmptyCollectionStrategy's remedy "Bind at
    least one implementation under its frame" misleads for a required `list[Class]` left empty because the class is
    bound only under a spellframe or a binding name (automatic worlds refuse with `collection_socket_no_providers`);
    and UnresolvedInputError says "nothing registered provides it" for a class registered under a frame or a name.
    Part (a)'s error and the SpellMap miss should name where the class is bound and the lookup to use, for these
    shapes too (within the owner's licence for this task: "you can add these or extend various features").
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-11-07_class_annotation_selects_only_bare_spells_task.md:1-12
  - release_docs/next_version_release.md:27-33
  IMPACT: Part (a)'s scope names the collection refusal and the meld-time message beside the single-socket error.
  NEXT: Part (b): read each path's address refusal and pin both duplicate-address shapes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T15:45:30Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Part (b) started on the owner's "lets focus on the other fixes we can do" (chat 2026-11-07), delegated to a
    subagent with no src edits: measure both shapes - S (one spellframe, default binding) and N (one bare name,
    case-insensitive) - on every path (bind before/after conjure, two Books of a frame, bind_inactive into another
    index and its notch, remove_from_spell_index + notch, add_to_spell_index, scan, ownership transfer into a Book
    serving the address, contracted copies arriving at or bound beside a served address, conjure's Phase 4
    DUPLICATE_SPELL_NAME, upgrade_to_normal and restore/graft where cheap), the GIL off and on; pin each refusal with a
    regression test; report any ADMITTING path with a reproducer for the owner (no xfail, no src fix); bring the stale
    example probe test_probe_two_visible_spells_may_not_share_a_name to the 0.2.8206 address rule. Not by design a
    duplicate: versions of one index, a lender's spell lent to a borrower. Artifacts:
    context_compass/artifacts/duplicate_address_paths_20261107/.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:2244-2248
  - UX_and_AIX_experiences/pytest_examples/test_expert_probes.py:992-1026
  IMPACT: Part (b) ends with a measured path table, regression tests, and the owner's calls on any admitting path.
  NEXT: Review the subagent's table, tests and example-probe change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T16:19:38Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Part (b) measured (by subagent; 0.2.8279 working tree, no src edit), five shape variants (a category in
    three cases, a Protocol, two Protocols named alike, three same-named classes from different scopes, a name in
    three cases), the GIL off and on identical: every same-frame path REFUSES the second spell - bind before and after
    conjure, a second Book of the frame (three timings), bind_inactive onto another binding's index, a staged or
    split-off version's notch (0.2.8273's refusal), add_to_spell_index, Spellbook/Conduit.scan (at the second
    declaration; the first stays registered - a scan is not atomic, as documented), transfer within a frame, a
    contracted copy (never goes active; index link refused; a borrower cannot bind over it), upgrade_to_normal, a
    graft; a cross-frame link is refused; Phase 4's DUPLICATE_SPELL_NAME guards a forced pool. ONE PATH ADMITS:
    `transfer_spell_ownership` into a root of ANOTHER frame - the target Book then holds two active spells at one
    address (`meld("Report")` and `meld(spell_id=x)` raise DUPLICATE_SPELL_NAME), the source frame keeps a stale claim
    naming the moved spell (no new Book there can bind the address), and when the target frame did not serve the
    address, a later bind there registers a second active spell and then raises from the commit validator while
    staying registered. Code read: the transfer has no same-frame check (link has one, conduit_ward.py:801-812) and
    `_flip_registry_and_spellbooks` overwrites the target route without moving or checking the frame claim. Pinned:
    105 regression cases in tests/integration/melder/aether/conduit/test_one_active_spell_per_address_integration.py
    (100) and tests/integration/melder/crystallizer/test_graft_refuses_an_address_the_host_frame_serves_integration.py
    (5), support module tests/_one_active_spell_per_address_support.py - 105 passed in both GIL modes; the stale
    example probe is now `test_probe_two_spells_may_share_a_name_but_never_an_address` (test_expert_probes.py: 47
    passed both modes). Not measured: checkpoint restore (binds through bind/bind_inactive by code read), graft
    merge mode (covered by an existing test), concurrent binds, a cross-frame transfer with include_dependencies.
    Seen in passing: lesson 30 (04_expert) still states the old name rule in a comment block.
  EVIDENCE:
  - context_compass/artifacts/duplicate_address_paths_20261107/runs/duplicate_address_paths_gil0.txt:101-103
  - context_compass/artifacts/duplicate_address_paths_20261107/runs/duplicate_address_paths_gil0.txt:1-167
  - tests/integration/melder/aether/conduit/test_one_active_spell_per_address_integration.py:1-751
  IMPACT: The owner's rule holds on every same-frame path and is now pinned; the cross-frame transfer is a defect by
    the runtime model's own definition (a record naming the wrong owner, a state an agent cannot get past).
  NEXT: DECISION_REQUEST to the owner: refuse cross-frame transfers like links, or make them move and check the claim.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T16:45:35Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner (chat 2026-11-07), asked about the cross-aetheric-frame transfer: "no they shouldn't be able to
    transfer between frames thats an illegal operation" and "because you cannot link between frames either like that
    conduits cnanot lin kthat way". So `Conduit.transfer_spell_ownership` refuses a target in another aetheric frame
    before its transaction opens, with link's wording plus a remedy. Patch transfer_within_one_frame_2026_11_07 is
    written and read (architecture patch, component_patch_ownership_transfer; no code description - one guard).
    Mapping: interface delta 1 -> the check after the dynamic-mode check -> integration tests for both shapes (nothing
    moved, both frames unchanged, P08c and P08d) and the probe re-run; invariant 1 -> the release note (Breaking),
    the notch 0.2.8280, src_architecture/src_components and conduit.py's graph descriptor; the rebuild stays held on
    the owner's word.
  EVIDENCE:
  - context_compass/system_docs/patches/active/transfer_within_one_frame_2026_11_07/architecture_patch.md:1-77
  - src/melder/aether/conduit/conduit.py:4285-4396
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:801-814
  IMPACT: Closes the one admitting path of part (b); a spell's stewardship stays in one world, as links do.
  NEXT: Add the check and its docstring; then the tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T16:53:42Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The cross-frame refusal landed (working tree, uncommitted; notched 0.2.8280, release note "Spell ownership
    is never transferred across aetheric frames", Breaking): `Conduit.transfer_spell_ownership` raises RuntimeError
    "Cannot transfer spell ownership across different AethericFrames: <source> != <target>. ..." after the dynamic
    check, before the transaction. Pinned (by subagent) with 10 cases (P08c, P08d x five shapes): the refusal names the
    frame pair; frame a keeps X active, claimed and melding (a new frame-a Book is refused only because X still holds
    the address - no stale claim); frame b keeps only Y (P08c) or nothing, and a later bind there is an ordinary first
    bind (P08d). The probe at 0.2.8280: 135 rows, REFUSED 115, by design 10, unreachable 5, white-box 5, admitted 0
    (0.2.8279: admitted 10), both GIL modes. Runs, both modes: the two part (b) files 115 passed; the 20 other files
    exercising transfer_spell_ownership 415 passed and 1 failed - test_change_control_transfer_transaction_registers_
    live_registry_session, one of the 9 standing enum failures of 0.2.8277 (it asserts 'TRANSFER_OWNERSHIP' ==
    'transfer_ownership'; its Books share one frame); expert probes 47 passed. The system-docs merge is in flight.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:4385-4407
  - context_compass/artifacts/duplicate_address_paths_20261107/runs/duplicate_address_paths_0_2_8280_gil0.txt:1-1
  - context_compass/artifacts/duplicate_address_paths_20261107/runs/existing_transfer_tests_0_2_8280_gil0.txt:1-1
  IMPACT: Part (b)'s exit gate holds but for the docs merge: both shapes refused on every path, pinned, GIL off and on.
  NEXT: Review the docs merge, then close part (b) and start part (a).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T16:54:46Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Part (b) closed: the docs merge (by subagent) put the one-frame transfer rule into src_architecture (a new
    first invariant, a Breaking failure mode, the transfer sequence) and src_components (Ownership Transfer, Conduit
    Runtime, the transfer flow), both indexes current, the graph refreshed (`assemble_graph.py --check` OK; the
    Conduit node's prose updated but left unaccepted - its stamp spans the whole class, not re-read); the patch moved
    to patches/completed/. Seen, pre-existing, unchanged: a transfer to a cleaned target conduit raises AttributeError
    (the attribute it names moved from `_spellbook` to `_aetheric_frame_name`). Part (a) next: a read-only design
    investigation (by subagent) of how Phase 3 can record a class's hidden candidates (bound only under a frame or a
    name) for a Phase-4 error that names them and the lookup to use, the SpellMap miss, the empty required
    `list[Class]` remedy and UnresolvedInputError's text, with the cache and dynamic-bind consequences; the design goes
    to the owner before any src change.
  EVIDENCE:
  - context_compass/system_docs/patches/completed/transfer_within_one_frame_2026_11_07/architecture_patch.md:1-20
  - context_compass/system_docs/src_architecture_index.md:1-20
  IMPACT: Part (b) is done; part (a) starts from a design the owner approves.
  NEXT: Review the design proposal and take it to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T17:30:51Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: Part (a) design (by subagent, read-only, measured on 0.2.8280 both GIL modes): Phase 3 keeps resolving as
    today; when a class lookup finds nothing it also records the "hidden candidates" (same type key, bound under a
    spellframe or a non-default binding name; Protocol definitions excluded) on the socket descriptor
    (`hidden_spell_ids`, `hidden_frame_keys`), scan and index alike (a `by_hidden_type` bucket); a new Phase 4
    `HiddenProviderStrategy` emits error HIDDEN_PROVIDER naming each binding and the lookup to use (conjure refuses;
    a dynamic late bind and every meld refuse, as AMBIGUOUS_PROVIDER does); `SpellMap(Class)` misses of that kind join
    it instead of raising in Phase 3; the empty required `list[Class]` keeps `collection_socket_no_providers` with a
    text naming the bindings (automatic ERROR, dynamic WARNING + []); UnresolvedInputError names hidden candidates live;
    snapshot rows format 3 and cache generation 27. Emulated, it flips 30 tests in 6 files (mostly today's rewrites),
    0 of 627 examples. Owner decisions: D1 re-check a consumer compiled before its class was bound under a frame
    (announce the type key; recommended); D2 the break - override-reliant worlds (MelderOps shape) are refused at
    conjure, the ticket's FAILURE_ESCALATION; D3 keep the dynamic empty-list [] (recommended); D4 other SpellMap misses
    into the readable report (follow-up); D5 edge rules (Optional[...] without a default refused; non-resolvable
    framed definitions count for single sockets only; Protocol definitions never; same-named classes all listed).
    Side finding: AMBIGUOUS_PROVIDER's remedy "supply it at meld with override=..." cannot work (an invalid spell is
    refused with or without an override).
  EVIDENCE:
  - context_compass/artifacts/hidden_provider_20261107/runs/run_0_2_8280_gil0.txt:1-1
  - context_compass/artifacts/hidden_provider_20261107/runs/affected_diff_gil0.txt:1-1
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:1225-1290
  IMPACT: Part (a) is designed and measured; nothing changes in src before the owner's calls.
  NEXT: The owner's answers on D1-D5; then the patch docs and the implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T17:56:12Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner approved the part (a) design as put to him (chat 2026-11-07: "ok go ahead and update your tickets
    with our direction and lets fucken send it"). Settled: (1) the break - a consumer whose class lookup finds the class
    only under a spellframe or a binding name is refused at conjure (HIDDEN_PROVIDER, error) and an override no longer
    rescues it; migration: a frame SpellMap default, a Protocol annotation, binding the class bare, or an ordinary
    Python default; (2) order does not matter - framed and named binds, notches and contract grants also announce the
    type key, so a consumer compiled before its class was bound under a frame is re-checked and refused at its next
    meld (the "same answer" invariant); (3) a dynamic empty required `list[Class]` keeps injecting [] with a WARNING
    that names the bindings; automatic worlds keep refusing with `collection_socket_no_providers`, the text naming
    them; (4) AMBIGUOUS_PROVIDER's remedy loses "supply it at meld with override=..." (it cannot work); (5) edge rules:
    `Optional[Class]` without a default is refused, a Protocol's own definition never counts, non-resolvable framed
    definitions count for single sockets only, same-named classes from different modules are all listed; other
    SpellMap misses (X nowhere, frame-named) move into the readable report later, not now.
  EVIDENCE:
  - context_compass/artifacts/hidden_provider_20261107/runs/run_0_2_8280_gil0.txt:1-1
  IMPACT: Part (a) is authorized as designed; it lands as one source change (notch 0.2.8281) with cache generation 27.
  NEXT: Patch docs (hidden_provider_2026_11_07), read and mapped; then the implementation, tests, docs merge.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T18:23:28Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch hidden_provider_2026_11_07 (written by the design subagent, 9 files) read in the required order -
    architecture, the six component patches, the two code-description patches - and mapped (patch section ->
    implementation step -> validation step); no conflict between the patches or with the canonical docs beyond the
    owner-approved changes they record (D1-D5). (1) component_patch_compiler_phase_3 After 1-7 -> `_hidden_type_key`,
    the `by_hidden_type` bucket, `_hidden_class_candidates` (scan and index, one predicate), the miss branch of
    `_build_local_frame_dag` (single, required collection, SpellMap via `hidden_out`), `_resolve_spellmap_default`'s
    extended text for direct callers, `_build_local_topology(socket_hidden=)`, the two descriptor fields ->
    test_compiler_phase_3.py additions, its 5 SpellMap rewrites and 2 key-set updates. (2) phase4 patch After 1-4 and
    texts (1)-(3) -> HiddenProviderReport and HiddenProviderStrategy (new modules, registered after
    AmbiguousProviderStrategy), RequiredHoles' skip, AMBIGUOUS without the override remedy -> the new strategy and
    renderer tests, the AMBIGUOUS unit update, the 30 measured flips in 6 files. (3) empty-collection patch -> both
    severities' texts with hidden ids, byte-identical without -> a stub-topology unit test, automatic refusal and
    dynamic [] in the integration file. (4) UnresolvedInputError patch -> live candidates for the first missing
    socket, the optional `hidden_spell_ids` slot -> unit cases framed, bare-named, none, Protocol, and one
    integration or white-box case. (5) snapshot/cache patch -> 12-field rows, PAYLOAD_FORMAT 3, generation 27
    `class_lookup_hidden_providers` -> test_structural_snapshot.py, the cache-history integration test, a round trip
    with non-empty hidden fields, the hydrate/parity registry snapshots. (6) announcing patches -> the type-key union
    in `_default_dirty_marker` (one call), `_add_contracted_spell`, `hidden_frame_keys` in
    `_extract_collection_frame_keys` -> their unit tests, the 9 test_spellbook.py flips, the S1 file rewritten to one
    answer. (7) refusal code description, steps 1-8 and edges -> the probe matrix as an integration file (placements x
    consumers x postures, re-gate paths 6a-6c, ORDER cases). (8) migration steps 7-8 -> release note (Breaking) and
    notch 0.2.8281 by melder_0, the docs merge by the docs agent, the patch to completed/; the rebuild stays held.
    Implementation rule for (4) and (6): the patches' "never raises" and "resolve failures are swallowed" are met by
    the helpers' own None/[] returns (`_resolve_spellbook_for_staged`, `_resolve_spells_for_binding_keys`) and narrow,
    documented handling - no new broad `except` (banned_patterns.md). Accepted UNKNOWN: which departure paths
    announce a frame key (measured by the new integration tests; `cleanup_spell` stays on the watchers epic).
  EVIDENCE:
  - context_compass/system_docs/patches/active/hidden_provider_2026_11_07/architecture_patch.md:73-112
  - context_compass/system_docs/patches/active/hidden_provider_2026_11_07/component_patch_compiler_phase_3.md:22-96
  - context_compass/system_docs/patches/active/hidden_provider_2026_11_07/component_patch_phase4_validation_strategies.md:23-146
  - context_compass/system_docs/patches/active/hidden_provider_2026_11_07/code_description_patch_hidden_provider_refusal.md:18-86
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:694-876
  IMPACT: The gate for system-impacting src is met (patch linked, read, mapped); STEP 2 can start.
  NEXT: Notch 0.2.8281 before any test run, then STEP 2 (src and tests per the patch) to the design subagent.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-11-07T18:26:56Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Notched 0.2.8281 (from 0.2.8280) before any part (a) test run - a mid-run notch flipped a GIL-on test
    earlier today - with the running note's header and rebuild line. STEP 2 (src and tests per the patch, the GIL off
    and on, after-runs into artifacts/hidden_provider_20261107/runs/, no ticket/board/system_docs/version/asset edits,
    no new broad except, report deviations instead of fixing forward) went to the design subagent at 18:24Z. The
    release note's part (a) text is folded into its existing section "A class lookup reaches only a spell bound
    bare", the contribution guide's one-section-per-subject rule: a second Breaking paragraph (HIDDEN_PROVIDER with
    the patch's exact single-socket text; the SpellMap form; override no longer rescues; order-independent), the
    list and unresolved-input paragraph replacing T2's "keeps conjuring ... SpellMap default could not be resolved",
    upgrade path 5 (a SpellMap default at the binding, bind bare, or an ordinary Python default - evidenced by the
    PLAIN invariant, src_architecture.md:2388-2392; whether override= still supplies such a parameter is not
    claimed, unmeasured), AMBIGUOUS without the override remedy, cache generation 27. To verify against the landed
    code before closure: the exact texts, the late-bind "registered and refused", and that `Optional[English] = None`
    conjures without HIDDEN_PROVIDER.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:22-93
  IMPACT: The change set's version and user-facing note are in place; nothing claims a run yet.
  NEXT: Review the subagent's STEP 2 report, then verify the note's claims against the code and the runs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-11-07T18:28:11Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The docs merge's user-facing scope, swept read-only (README, docs/ sources outside _build, agents/,
    UX_and_AIX_experiences, examples): README.md states the old behaviour in four places - the overview (cycles and
    ambiguous providers; a typed parameter with no provider is a caller-supplied input), "conjure() prepares the
    registered graph" (the same), the Dependency Injection rule (a class bound only under a frame or a name is just
    "not reached", no refusal named) and SpellMap's AMBIGUOUS_PROVIDER fix list, which still offers "a meld
    `override`" (D4 drops it). No docs/ source page, lesson (lesson 25 states the rule only), example or the agent
    operations guide names UNRESOLVED_INPUT, AMBIGUOUS_PROVIDER, "nothing registered provides it" or "SpellMap default
    could not be resolved"; those texts live only in src (compiler_phase_3.py, unresolved_input_error.py), which
    STEP 2 changes. The system docs, their indexes and the graph (two new modules need descriptors) follow the code.
  EVIDENCE:
  - README.md:127-130
  - README.md:388-391
  - README.md:466-476
  - README.md:529-533
  IMPACT: The docs agent's brief names these four README passages beside the system docs; the release note's
    packaging section gains a README line.
  NEXT: The subagent's STEP 2 report.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-11-07T18:37:27Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: BLOCKER
  CLAIM: Ticket and board edits pause for the move to GitHub Issues: cc_1 (the Context Compass maintainer session)
    relayed the owner's instruction ("Switch to github_issues", "and switch communication to claude style") and
    asked every agent to record its state, check out and edit no ticket or board until the owner says the switch is
    done. melder_0 checked out at this time. Work in flight: STEP 2 (src and tests per patch hidden_provider_2026_11_07)
    runs on with the design subagent (a2be7b2), which writes only src/, tests/ and run files under
    artifacts/hidden_provider_20261107/runs/ - never tickets or boards. Uncommitted in the working tree: T2's
    follow-ons, 0.2.8279 (license), 0.2.8280 (part (b)), the Dependabot pins, the 0.2.8281 notch and release note, and
    STEP 2's edits as they land; commit and push stay the owner's.
  EVIDENCE:
  - context_compass/mailbox_board.md:92-99
  - release_docs/next_version_release.md:1-3
  IMPACT: The subagent's report cannot be recorded until the switch; it lives in its run files and the working tree
    meanwhile, and is recorded on this ticket's Issue first thing after the switch.
  NEXT: After the owner's word: re-onboard (github_issues, claude_internal_communication), check in with the
    "Agent: melder_0" issue, claim this ticket with a claim comment, then record STEP 2's report.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
- Scope: the owner's rule - (a) a Phase 4 error for a consumer annotated with a class bound only under a spellframe
  or a binding name, naming where it is bound and the lookup to use (and the SpellMap miss likewise); (b) two
  spells at one address refused on every path, checked where missing, the stale example probe fixed.
- State: in_progress, melder_0 (checked out 2026-11-07T18:37:27Z for the move to GitHub Issues; BLOCKER note). Part
  (b) done (0.2.8280, uncommitted). Part (a) approved as HIDDEN_PROVIDER (DECISION 2026-11-07T17:56:12Z); patch
  hidden_provider_2026_11_07 written, read and mapped (PLAN 18:23:28Z); notched 0.2.8281 and the release note folded
  into "A class lookup reaches only a spell bound bare" (PLAN 18:26:56Z); STEP 2 - src and tests per the patch, the
  GIL off and on - in flight with the design subagent since 18:24Z, nothing of it verified or recorded yet.
- Holds: ticket and board edits until the owner says the Issues switch is done; the asset and llm_support rebuild
  waits for the owner's word (so the version-stamp test fails until then); commit and push are the owner's.
- Next, after the switch: (1) re-onboard, check in, claim this ticket; (2) record and review STEP 2's report and its
  after-runs (artifacts/hidden_provider_20261107/runs/, 0_2_8281 names); (3) verify the release note's claims (exact
  texts, the late-bind refusal, `Optional[English] = None` conjuring); (4) docs merge - the system docs, indexes, graph
  and the four README passages (FACT 18:28:11Z); (5) full suite both modes; closure on the owner's acceptance.

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
