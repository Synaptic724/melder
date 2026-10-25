

# Task: Component tests that show the two rebind defects - wrong disposal methods, and a meld that fails

## Metadata
- Task ID: TASK-2026-10-25-rebind_while_old_objects_are_alive_tests
- Story: none (standalone; the owner's request in chat, 2026-10-25)
- Status: in_progress
- Owner: Mark (owner)
- Agent Name: melder_3
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-25T08:19:33Z
- Updated: 2026-10-25T09:47:47Z

## Objective
Write component tests that show, by running, the two defects TASK-2026-10-25-creations_many_disposal_docstrings
measured and reported to the owner. (1) A `many` spell cleaned up and bound again under other disposal names while
the removed definition's objects are still alive in a store: the new objects are disposed with the old methods
(`close` instead of `shutdown`), and nothing raises. (2) A `unique` or `unique_per_conduit` spell cleaned up and
bound again as `many` while its old object is held: the next meld builds the new object, then fails with
AttributeError, and that object is lost. Each defect test asserts the corrected contract under xfail(strict=True) -
the repository's form for a known gap - so the suite stays green, `-rxX` lists them as expected failures and
`--runxfail` shows each failure with the values observed; passing controls bound each defect. No source change: the
fix is S3 (STORY-2026-10-18-revalidate_on_binding_change, parked by the owner).

## Ticket Contract
- ENTRY_GATE: the owner's request in chat (2026-10-25, quoting the closure report's two defects): "prove it make
  tests to show me"; a board row routes here; no open lane holds the module or tests_components' Aether Component
  Cluster.
- EXECUTION_BOUNDARY: one new test module,
  tests/component/melder/aether/conduit/test_conduit_component_rebind_while_old_objects_are_alive.py; its entries in
  tests_components (the Aether Component Cluster, the C1 code map, the sources, a handoff entry) and that index; the
  rebuild last. Nothing under src/, no notch, no release-note entry.
- DEPENDENCIES: none blocking. S3 (STORY-2026-10-18-revalidate_on_binding_change, backlog) is the fix; whoever lands
  it deletes these markers. The docstring task's probes (artifacts/creations_many_disposal_20261025/, retained) are
  the reproducers the tests follow.
- EXIT_GATE: the module runs with the GIL off and on - each defect test XFAIL (strict), every control passes; with
  `--runxfail` each defect test fails on the observed values; tests_components and its index current (`--check` OK);
  closure; the rebuild last with both `--check`s OK; the runs shown to the owner.
- FAILURE_ESCALATION: DECISION_REQUEST when a defect does not reproduce in the test (the probe and the test
  disagree); CONFLICT when another lane holds tests_components; BLOCKER when the tests cannot run.

## Scope Boundaries
- In scope: the module (the two defect tests, parametrized, and their controls), its tests_components entries and
  index, the rebuild.
- Out of scope: fixing either defect (S3, the owner's call); src_components and src_architecture, which carry both
  defects since 0.2.8268 (citing these tests from them would be an edit the owner has not asked for).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner's request in chat (2026-10-25) for tests that prove the two reported defects.

## Steps / Checklist
- [x] Read the code the tests exercise (creations.py's `many` record, the emitter's call) and the two probes.
- [x] Write the module: the two defect tests (strict xfail, the corrected contract) and their controls.
- [x] Run it with the GIL off and on, then with `--runxfail`; record the MEASURE note.
- [ ] tests_components: the cluster entry, the code map, the sources, a handoff entry; the index `--check`.
- [ ] Closure and board sync; the rebuild last with both `--check`s; show the runs to the owner.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- The test module; its runs (GIL off and on, and `--runxfail`) in the Notes; the tests_components entries.

## Files / Paths Impacted
- tests/component/melder/aether/conduit/test_conduit_component_rebind_while_old_objects_are_alive.py (new)
- context_compass/system_docs/tests_components.md and tests_components_index.md
- the generated assets and bundles (the rebuild)

## Validation
- Not run.
- Recommended commands:
  - pytest on the module with -X gil=0 and -X gil=1 and `-rxX`; once more with `--runxfail`
  - index_document.py --check on tests_components; the asset runner and the llm_support builder, each with
    `--check` (`--include-untracked` while the module is untracked)

## Risks / Rollback Notes
- A strict xfail that starts passing for a reason other than the fix fails the suite; each assertion names its
  symptom alone (the new object's disposal calls, the meld's outcome), so a fix that handles the removed
  definition's objects another way still turns the test green. Rollback: one new file and its doc entries.
- The tests read the store through public behaviour only - each object records the disposal calls Melder makes on
  it, and the meld returns or raises - so a refactor of the store's record does not break them.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.
- [ ] No assertion on a private field (Rank F): the store is observed through the objects' disposal calls.

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
  - artifacts/rebind_live_store_tests_20261025/probes/probe_rebind_examples.py (E1-E7)
  - artifacts/rebind_live_store_tests_20261025/probes/probe_store_rebind.py (S1-S11, the store)
  - artifacts/rebind_live_store_tests_20261025/scripts/s3_stand_in_conftest.py (the stand-in fix)
  - artifacts/rebind_live_store_tests_20261025/runs/ (the module, --runxfail, the stand-in, the probe; GIL off/on)
- DISPOSITION: retain_as_reference (the folder refuses deletes; S3's fix reruns them)
- CLEANUP_TRIGGER: S3's fix lands, or the owner's word

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_3 (synaptic_python_developer); test and prose; revision 1.
- Published By: UNKNOWN before publication (local files; the owner commits).
- Independent Review: none requested.

## Notes
- DATETIME: 2026-10-25T08:19:33Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Mailbox consumed at lane open: M2-48 (melder_2, 03:22:43Z) turned in
    STORY-2026-10-25-pypi_trusted_publishing_and_provenance and rebuilt the assets and bundles; M1-66 (melder_1,
    08:08:16Z) notched 0.2.8269 for STORY-2026-10-25-probe_and_purge_reach_every_version, whose rebuild is the last
    write of that landing. Neither asks anything of this lane. `__version__` reads 0.2.8269; this task takes no
    notch, and its rebuild after its closure takes in the tree as it stands then.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - context_compass/tickets/stories/completed/2026-10-25_pypi_trusted_publishing_and_provenance_story.md:1-8
  IMPACT: the version and the other lanes' rebuilds are known before this lane's rebuild; nothing to notch above.
  NEXT: write the module.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T08:19:33Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Read again at lane open (creations.py unchanged since 0.2.8268, sha256 eb785194...): a `many` key's
    disposal record is written once, at the key's first registration in a store, with that Spell's list, and
    `register_many` appends every later object under it without comparing lists; it reads the key's live slot and
    calls `append` on it unchecked, after the object is built; the emitted plan passes its own Spell's list as
    `dmN`. The module: (1) `test_rebind_with_other_disposal_methods_disposes_new_objects_with_their_own` - bind
    `many` with ["close"], meld, cleanup_spell, bind with ["shutdown"] (the same spell_id), meld, end the scope
    (root teardown; a lesser's pool return), assert the second object's calls are ["shutdown"]; (2)
    `test_rebind_of_a_held_slotted_spell_as_many_returns_and_disposes_the_new_object` - `unique` and
    `unique_per_conduit`: meld, cleanup_spell, bind as `many`, meld, end the scope, assert the meld returned the new
    object and the scope disposed it with its list. Both under xfail(strict=True) with the S3 reason, each asserting
    its symptom alone. Controls that pass today: the same list; a first binding without disposal names; a second
    binding without them; a slotted definition never melded. Objects record their own disposal calls - no private
    reads. Runs: -X gil=0 and gil=1 with -rxX, then --runxfail.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:12-61
  - src/melder/aether/conduit/creations/creations.py:429-523
  - src/melder/aether/conduit/creations/creations.py:807-892
  - src/melder/aether/conduit/creations/creations.py:894-952
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1579-1624
  - context_compass/artifacts/creations_many_disposal_20261025/probes/probe_rebind_many_disposal.py:1-95
  - context_compass/artifacts/creations_many_disposal_20261025/probes/probe_rebind_existence_to_many.py:1-74
  - context_compass/tickets/stories/backlog/2026-10-18_revalidate_on_binding_change_story.md:34-41
  IMPACT: the tests prove both defects through behaviour a user sees - which methods run, whether the meld returns -
    and turn green exactly when S3 fixes each one.
  NEXT: write the module and run it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T08:26:49Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Written: tests/component/melder/aether/conduit/test_conduit_component_rebind_while_old_objects_are_alive.py
    (359 lines, 10 cases). Two defect tests under xfail(strict=True, raises=AssertionError) with the S3 reason:
    `test_rebind_with_other_disposal_methods_disposes_the_new_objects_with_their_own` [root-teardown,
    lesser-pool-return] asserts the second object's disposal calls are ["shutdown"];
    `test_rebind_of_a_held_slotted_spell_as_many_returns_and_disposes_the_new_object` [unique, unique-per-conduit]
    asserts the meld returned a new object and the root's teardown disposed it with ["close"]. Four controls (six
    cases). Found while writing it: `Svc` must hold no class-level state - the spell_id digest encodes every
    class-level value and a function's closure cells by their contents, so a construction list on `Svc` or in a
    closure changes between the two binds, gives the rebind another spell_id and hides both defects. The module
    keeps that list on an unbound `Journal` class that `Svc`'s code names; a global read by name is not digested.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_rebind_while_old_objects_are_alive.py:52-88
  - tests/component/melder/aether/conduit/test_conduit_component_rebind_while_old_objects_are_alive.py:166-264
  - tests/component/melder/aether/conduit/test_conduit_component_rebind_while_old_objects_are_alive.py:267-359
  - src/melder/aether/spellbook/bind/spell_code_digest.py:375-406
  - src/melder/aether/spellbook/bind/spell_code_digest.py:426-505
  IMPACT: the tests reproduce the defects only while the rebind keeps the spell_id; any later rebind test must keep
    its class free of mutable class-level and closure state, or it tests nothing.
  NEXT: run the module with the GIL off and on, then with --runxfail.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T08:26:49Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Run on 0.2.8269, CPython 3.14.8 free-threaded, the GIL off and on (identical): the module alone, 6 passed,
    4 xfailed (strict); with the Creations, many-child, purge and rebind-integration neighbours, 125 passed, 4
    xfailed. With `--runxfail` the four defect tests fail on the values observed - defect 1, both scopes: "the
    second binding declares ['shutdown'], but its object was disposed with ['close']; the first object ... was
    disposed with ['close']"; defect 2, both existences: "the next meld raised AttributeError: 'Svc' object has no
    attribute 'append'; Svc objects built: 2 ...; the meld's object was disposed with [] at the root's teardown; the
    first definition's object was disposed with ['close']". Under a scratch stand-in for S3's rule (a monkeypatched
    register_many, outside the repository, that moves an entry whose slot is not a list, or whose record holds
    another list, to a side key of the same store before registering) all four report XPASS(strict) and fail the run
    while the six controls pass, so the tests turn green exactly when the store follows the binding. py_compile left
    one git-ignored .pyc in the module's __pycache__ (the folder refuses deletes; the tests tree holds eight such
    caches).
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_rebind_while_old_objects_are_alive.py:166-264
  - tests/component/melder/aether/conduit/test_conduit_component_rebind_while_old_objects_are_alive.py:267-359
  - src/melder/aether/conduit/creations/creations.py:807-892
  IMPACT: both defects are proven by a run, the GIL off and on, and the strict markers flip under a fix, so a closed
    gap cannot keep reporting as open.
  NEXT: tests_components: read tests_components_instructions.md, then the cluster entry, code map, sources, handoff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T08:32:15Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: For the owner's follow-up (chat 2026-10-25 02:27 MDT: "explain the problems again with more examples an
    detail") a seven-case probe ran on 0.2.8269, the GIL off and on (identical). E1: `many` bound with close, then
    shutdown, then flush, each melded at the root - all three objects disposed with ['close']. E2: [flush, close]
    then [close] - the second object gets ['flush', 'close'], a method its binding never declared. E3: the old
    object in a lesser's store, the new one melded at the root - ['shutdown'], correct: the record is per store. E4:
    the lesser returned to its pool before the rebind, a new lesser (the same shell) melds - ['shutdown'], correct:
    the pool return emptied the store. E5: `unique` and `unique_per_conduit` rebound as `many`, three melds at the
    root - three AttributeErrors, four objects built, only the first disposed: every retry leaks one. E6: the same
    rebind, the meld through a lesser - a new object, disposed with ['close']: only the store holding the old object
    fails. E7: a `unique` class with its own append() rebound as `many` - no error: the meld returns a new object
    after Melder called old.append(new), and the new object is never disposed. The module's runs, the --runxfail
    failures and the S3 stand-in's XPASS(strict) runs are saved beside the probe.
  EVIDENCE:
  - context_compass/artifacts/rebind_live_store_tests_20261025/probes/probe_rebind_examples.py:1-172
  - context_compass/artifacts/rebind_live_store_tests_20261025/runs/probe_rebind_examples_gil0.txt:1-10
  - context_compass/artifacts/rebind_live_store_tests_20261025/runs/probe_rebind_examples_gil1.txt:1-10
  - context_compass/artifacts/rebind_live_store_tests_20261025/scripts/s3_stand_in_conftest.py:1-40
  - context_compass/artifacts/rebind_live_store_tests_20261025/runs/s3_stand_in_gil0.txt:1-23
  - context_compass/artifacts/rebind_live_store_tests_20261025/runs/module_runxfail_gil0.txt:1-40
  - src/melder/aether/conduit/creations/creations.py:807-892
  IMPACT: the two defects are bounded: each lives in the one store that still holds the removed definition's record
    or object, and problem 2 has a silent form (E7) that corrupts the old object instead of raising.
  NEXT: decide whether E7 joins the module (it is not one of the two cases the owner asked for), then
    tests_components.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T08:32:15Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The module keeps the two defects the owner asked to see proved (other disposal methods; a held slotted
    spell rebound as `many`), with their controls. E7, the silent `append()` form of the second defect, stays in the
    probe and is offered to the owner as a third strict xfail rather than added unasked (strict approval loop: no
    scope expansion without his word). The probe and the runs are kept as `retain_as_reference` - the folder refuses
    deletes, and S3's fix reruns them.
  EVIDENCE:
  - context_compass/artifacts/rebind_live_store_tests_20261025/probes/probe_rebind_examples.py:1-172
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/AGENTS.MD:311-317
  IMPACT: the test file's scope matches the request; the owner decides on E7.
  NEXT: tests_components: the cluster entry, code map, sources and handoff; the index --check.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T08:47:37Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Re-onboarded after a context compaction (REONBOARD attestation and the owner-sanctioned self-certification
    posted in chat; the closure script written before it, /tmp/m3c/task_close.py, was not run). Mailbox consumed:
    M0-227 (melder_0, 08:38:33Z) took 0.2.8270 for TASK-2026-10-10-deny-file-access-under-safe-codegen (D-10), its
    closure and rebuild next; M1-69 (melder_1, 08:40:52Z) holds S2
    (STORY-2026-10-17-notch_moves_signature_by_incoming_key_only) on the owner's go, with custody of spell_index.py,
    bind.py, spellbook.py, lookup_container.py, aetheric_frame.py, conduit.py (docstrings), restore_engine.py,
    graft_runner.py, README.md and about 35 test files that stage versions - not this module - and waits on
    tests_components until this lane says it is free. This lane edits none of those files and takes no notch; its
    rebuild after its closure takes in the tree as it stands then. The owner asked in chat (02:40 MDT) what 'rebind'
    means and why `cleanup_spell` 'disposes nothing' - he expects a removed spell gone 'internals and all' - and
    wants to talk it through, so the closure waits on that conversation: what he decides can change what the defect
    tests assert.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - context_compass/tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md:3-12
  IMPACT: nothing in the other lanes blocks this one; tests_components is released to melder_1 now (this lane's
    entries are in and its index checked), and the closure is held for the owner.
  NEXT: read the cleanup_spell path and the store's `many` record, then answer the owner from the code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T08:50:27Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Read again for the owner's question: `cleanup_spell` removes the spell itself, internals and all - it
    releases the version from every contract (`ConduitWard._emit_spell_disposed`), invalidates it (its creation
    context cleared, its lineage marked so dependents recheck), and `cleanup_and_remove_spell` unregisters its index
    from SpellSystemStates (its verdicts retired), takes it out of every id and lookup map and cleans the Spell and,
    as sole member, its SpellIndex. What it leaves is what the spell already built: the objects in the conduits'
    Creations stores, filed under the spell_id with their disposal record - a `many` key's ManyDisposalBucket (the
    first registration's method list) or a slotted key's object - ("Conduit Creations persist in this model and are
    left alone here."). That is the owner's ruling of 2026-10-03 (M7 (a), "it should be deliberately left alive
    thats perfect"), restated in the 2026-10-14 runtime model (Melder does not dispose an object because a
    definition was removed). It was made at 0.2.8219, when existence and disposal names were part of the spell_id,
    so a rebind under another existence or disposal list got another spell_id and never met the leftovers; since
    0.2.8257 the spell_id is the code alone, so `cleanup_spell` then `bind` of the same class - the path the
    collision error names for changing a binding - keeps the spell_id, and the new definition's objects register on
    the removed one's record: `register_many` appends under the old list, unchecked, or onto the old slotted object
    (AttributeError, or that object's own `append`).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4960-5042
  - src/melder/aether/spellbook/spellbook.py:5044-5212
  - src/melder/aether/spellbook/spellbook.py:6060-6073
  - src/melder/aether/conduit/conduit.py:6244-6321
  - src/melder/aether/conduit/creations/creations.py:12-61
  - src/melder/aether/conduit/creations/creations.py:807-892
  - context_compass/tickets/tasks/completed/2026-10-03_repair_rebind_after_first_meld_task.md:205-215
  - context_compass/system_docs/src_architecture.md:26-57
  - context_compass/system_docs/src_architecture.md:1330-1373
  - context_compass/system_docs/src_architecture.md:1908-1920
  IMPACT: the two defects are the 2026-10-03 rule (leave the objects alive in their store) meeting the 0.2.8257
    identity (the rebind keeps the spell_id): the new definition inherits the old definition's store record.
  NEXT: put the decision to the owner (next note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T08:50:27Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: The owner's call: what happens to the objects a removed spell built that a conduit store still holds, once
    the class is bound again under the same spell_id. (A) Keep the 2026-10-03 rule - they stay alive and are
    disposed when their scope ends, with their own methods - and have the store keep them apart from the new
    definition's objects: the new binding starts a fresh record (S3's store requirement; the stand-in that flips all
    four defect tests does this). (B) `cleanup_spell` disposes them: every store holding the spell_id - the root's,
    its lessers', its spellspaces', a cluster's team store - runs their disposal methods and drops them, so nothing
    of the removed definition survives; this reverses the 2026-10-03 ruling and the runtime model's rule, and closes
    objects holders may still use. (C) `cleanup_spell` forgets them without disposing - Melder lets go, the agent
    disposes them - which ends both defects but leaves nothing to close them at scope end. Recommended: A. It keeps
    both rulings, fixes both defects with one rule in the store, and the module already asserts it; under B or C the
    defect tests' expected values change before the closure.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:807-892
  - context_compass/tickets/stories/backlog/2026-10-18_revalidate_on_binding_change_story.md:34-41
  - context_compass/artifacts/rebind_live_store_tests_20261025/scripts/s3_stand_in_conftest.py:1-40
  - context_compass/tickets/tasks/completed/2026-10-03_repair_rebind_after_first_meld_task.md:205-215
  IMPACT: the closure waits on the owner; the tests' expectations follow A until he rules.
  NEXT: explain both defects to the owner from the code with the examples, and ask A, B or C.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T08:52:28Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Correction to the DECISION_REQUEST above, after reading the module's assertions again: its last sentence
    ("under B or C the defect tests' expected values change") is wrong. The two defect tests assert only the new
    object - its disposal calls, and that the meld returns it - so each turns green under A, B or C. Every control
    holds under A and B as written (B moves when the removed definition's object is closed, which no assertion
    pins). C changes two controls, `..._same_disposal_methods_disposes_both_objects_with_them` and
    `..._without_disposal_methods_leaves_the_new_objects_undisposed`, which expect that object closed when its scope
    ends; the lane that lands C would update them. So the owner's choice decides S3's fix, not this module.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_rebind_while_old_objects_are_alive.py:186-210
  - tests/component/melder/aether/conduit/test_conduit_component_rebind_while_old_objects_are_alive.py:233-264
  - tests/component/melder/aether/conduit/test_conduit_component_rebind_while_old_objects_are_alive.py:267-332
  IMPACT: this task's closure does not depend on the owner's A, B or C; it is held only because he asked to talk it
    through first.
  NEXT: tell the owner, with the examples; close on his word.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T08:59:17Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's direction in chat (2026-10-25 02:56 MDT): "cleanup spell shouldn't leave anything in any
    container it means we're removing hte reference"; he asked whether the defects come from not removing the
    reference properly. They do. `cleanup_spell` removes every reference the Book, the frame, the lineage registry
    and the contracts keep to the spell, and none of those the conduits' Creations stores keep under its spell_id -
    `_creations` (the live `many` list or the slotted object), `_disposable_creations` (the disposal record) and
    `_managed_quantities` (a managed version's pool) - in every store that recorded one (a root's, a live lesser's,
    a spellspace's, a cluster's team store). The rebind's spell_id reads that leftover: both defects have this one
    cause. The direction reverses the 2026-10-03 M7 ruling (a) ("deliberately left alive", the slot kept and
    returned to the replacement; its option (b) was eviction on removal), which
    `test_slotted_replacement_meets_the_surviving_singleton_in_its_slot` pins; it replaces S3's store requirement
    (keep an unchanged entry, retire a changed one) and ends the 0.2.8254 pool rebind (cleanup_spell then bind kept
    a managed spell's pool and its objects). This lane changes no source; the fix is a src lane on the owner's word.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:4960-5042
  - src/melder/aether/conduit/creations/creations.py:807-892
  - src/melder/aether/conduit/creations/creations.py:965-1023
  - context_compass/tickets/tasks/completed/2026-10-03_repair_rebind_after_first_meld_task.md:188-215
  - tests/integration/melder/aether/conduit/test_rebind_after_first_meld_integration.py:317-339
  - context_compass/tickets/stories/backlog/2026-10-18_revalidate_on_binding_change_story.md:34-41
  IMPACT: the fix is one rule - `cleanup_spell` clears its spell_id from every store - and it ends both defects; the
    module's defect tests still hold under it (they check only the new object).
  NEXT: ask the owner the one open point: on removal, are the objects disposed (as purge does) or only let go.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T08:59:17Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: When `cleanup_spell` removes its spell_id from every store, what happens to the objects it held? (1)
    Dispose them, as `Conduit.purge` does for one store: their disposal methods run (`close()`), a holder still
    using one keeps a closed object - pending work for that agent under the 2026-10-14 runtime model. (2) Only let
    go: nothing is closed and nothing will close them; whoever holds one owns it ("an object it lets go of is not a
    leak"), and one nobody holds is collected unclosed. Also to confirm with it: that this replaces the 2026-10-03
    ruling. Under (1) every test in this module holds as written; under (2) the two controls that expect the removed
    definition's object closed at its scope's end change.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5211-5290
  - context_compass/system_docs/src_architecture.md:26-57
  IMPACT: the fix's lane needs the answer before its patch; this task can close either way.
  NEXT: put (1) or (2) to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T09:05:35Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ALIGNMENT_CHECK
  CLAIM: The owner's model, in chat (03:04 MDT): a store "only has a reference to the derrived object" and a spell
    "has nothing to do wiht the creations it creates" - so the previous DECISION's reading of 02:56 (remove the
    stores' entries on cleanup_spell) and its DECISION_REQUEST (dispose them or let go) do not fit what he means:
    the objects stay where they are, untouched by the spell's removal. The code agrees that a store holds objects,
    not the Spell, but files them by the spell_id - `_creations[spell_id]` (the object, or the `many` list),
    `_disposable_creations[spell_id]` (the disposal record, the first registration's list) - and a meld reads them
    back by that key (`get_creation`, `register_many`); a rebind keeps the spell_id, so the new definition reads the
    old one's entries. The fix his model calls for: on `cleanup_spell` each store moves that spell_id's entries out
    of the key's way (alive, disposed at their scope's end with their own methods), so the new definition starts
    with an empty slot - S3's store rule for a changed binding, applied to every rebind; it ends the 2026-10-03
    behaviour of a rebound slotted spell getting its old object back. To confirm with him.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:659-735
  - src/melder/aether/conduit/creations/creations.py:807-892
  - src/melder/aether/conduit/creations/creations.py:954-964
  IMPACT: the open question narrows to one yes/no: retire the old entries out of the new definition's way at
    cleanup_spell, with no early disposal; the module holds under it as written.
  NEXT: show the owner the keyed store and ask that yes/no.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T09:36:16Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ALIGNMENT_CHECK
  CLAIM: The owner rejects tying `cleanup_spell` to the creations at all (chat 03:24 and 03:35 MDT: "the creations a
    spell makes has nothing to do with the object that makes it", "why are you trying to connect a cleanup_spell
    with the creations it made"). Corrected framing: `cleanup_spell` is right as it is and is in the reproduction
    only because bind refuses one class twice while its spell exists. The defect is the store's: it identifies
    objects by spell_id, so two different spells of one class - before and after the rebind - share one entry;
    `register_many` writes a key's disposal list once and appends every later object under it, and appends onto
    whatever the key holds. The earlier notes' fixes placed at `cleanup_spell` (the DECISION and ALIGNMENT_CHECK of
    this morning) are withdrawn; a fix belongs in the store (`register_many` and the key it files under), on the
    owner's word.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:807-892
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1579-1624
  - src/melder/aether/spellbook/spellbook.py:6060-6073
  IMPACT: the module's tests are unchanged by this (they check the new spell's object); the S3 stand-in already
    fixed it in the store alone.
  NEXT: explain it to the owner as two spells sharing one store key, with cleanup_spell out of it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T09:41:30Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: For the owner's question (chat 03:36 MDT: "what exactly is happening in the creations store explain all
    your problems with it"), creations.py read whole and an eleven-case probe run on 0.2.8270 at a root, the GIL off
    and on (identical but for conduit ids). The store is two dicts keyed by spell_id - `_creations` (the object, or
    the `many` list) and `_disposable_creations` (a `(object, methods)` tuple, or one ManyDisposalBucket per `many`
    key with the list of its first registration) - and every reader and writer goes by spell_id and reads the slot's
    shape from the spell that asks, not from what is stored. A class bound again under another binding keeps the
    spell_id and meets what the first spell left: S1 `many` close->shutdown, the new object closed with close; S2
    unique->many, the meld raises AttributeError and its object is never disposed; S3 many->unique, the meld returns
    the old Python list of two Svc objects, every time; S4 many->unique_per_conduit, the same, a list of one; S5
    unique close->shutdown, the meld returns the old object (the 2026-10-03 rule) and shutdown never runs; S6
    unique->many, purge(spell_id) raises TypeError "object of type 'Svc' has no len()"; S7 many x2->unique, purge
    returns 1 and disposes both; S8 the new `many` spell reads live, creation_count 1, before it built anything; S9
    unique->many reads not live, count 0, while the old object sits under its id. Separate, no rebind: teardown
    order is per key (a key's first insertion), not per object - S10 (a dependency purged, then the dependent melded
    again) and S11 (the first meld supplies the dependency by override, the second builds it) both close the newer
    User after its Dep, against the store's newest-first rule.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:68-272
  - src/melder/aether/conduit/creations/creations.py:429-471
  - src/melder/aether/conduit/creations/creations.py:472-524
  - src/melder/aether/conduit/creations/creations.py:659-735
  - src/melder/aether/conduit/creations/creations.py:807-892
  - src/melder/aether/conduit/creations/creations.py:1160-1272
  - src/melder/aether/conduit/creations/creations.py:1273-1332
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1652-1674
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1676-1754
  - context_compass/artifacts/rebind_live_store_tests_20261025/probes/probe_store_rebind.py:1-245
  - context_compass/artifacts/rebind_live_store_tests_20261025/runs/probe_store_rebind_gil0.txt:1-12
  - context_compass/artifacts/rebind_live_store_tests_20261025/runs/probe_store_rebind_gil1.txt:1-12
  IMPACT: the rebind's same spell_id breaks every store verb that reads the key, not only register_many (meld
    returns a list as the object, purge crashes or miscounts, the probes lie); the teardown-order gap is the store's
    own, rebind or not. None is fixed here (tests only).
  NEXT: lay the store and these problems out for the owner; the fix and its scope are his call.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T09:43:13Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's ruling in chat (2026-10-25 03:42 MDT): "WHY WOULD A USER TAKE A DISPOSAL METHOD BIND IT as 1
    thing then change it later you do realize that its the same spell if they do this its on them". A class bound
    again under other disposal names while its objects are alive in a store is the user's responsibility, not a
    Melder defect: the store keeping one key's first disposal list (problem 1, probe S1) is accepted. Consequence
    for this module: its first strict xfail,
    `test_rebind_with_other_disposal_methods_disposes_the_new_objects_with_their_own`, asserts the contract he
    rejects, and the docs that name it a known gap (tests_components, tests_architecture's Failure Modes entry)
    follow it; neither is changed before his go (strict approval loop).
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_rebind_while_old_objects_are_alive.py:166-210
  - context_compass/artifacts/rebind_live_store_tests_20261025/runs/probe_store_rebind_gil0.txt:1-12
  IMPACT: defect 1 leaves the defect list; the module and its doc entries need his go to change.
  NEXT: ask the owner to confirm removing that test, and whether the existence change (problems 2-4, 6, 7) is his
    users' responsibility too or should fail with a clear error.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T09:47:47Z
  AUTHOR: melder_3
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: For the owner's question (chat 03:46 MDT: why the bind signature left the SHA256, "there should be a ticket
    on this"): EPIC-2026-10-18-spell_identity_is_the_code. The old spell_id hashed a shallow outline of the class
    (names, bases, method names, constructor signature) plus the bind call (spellframe, binding name, existence,
    disposal names, resolvable); the owner ruled it a correctness bug (2026-10-18): one class could be registered
    once per binding name and staged once per existence, and an edited method body kept the old id. His design: the
    spell_id is the code (S1, 0.2.8257), the bind signature gets its own hash in a manifest (S2, 0.2.8258), and "if
    that hash changes we should revalidate the object ... maybe it changes how we build things" - S3,
    STORY-2026-10-18-revalidate_on_binding_change, whose requirement is that the store's entry follows the binding.
    S3-S5 were parked at the epic's turn-in on his word (2026-10-19, "turn in the epic and then we'll move on"), so
    the rebind defects are the parked third part of that design.
  EVIDENCE:
  - context_compass/tickets/epics/completed/2026-10-18_spell_identity_is_the_code_epic.md:26-36
  - context_compass/tickets/epics/completed/2026-10-18_spell_identity_is_the_code_epic.md:280-298
  - context_compass/tickets/epics/completed/2026-10-18_spell_identity_is_the_code_epic.md:1037-1064
  - context_compass/tickets/stories/backlog/2026-10-18_revalidate_on_binding_change_story.md:20-41
  IMPACT: the fix the owner is weighing is already specified as S3 of his own epic; it can be unparked rather than
    redesigned.
  NEXT: answer the owner with the epic, its reasons and the parked S3.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Scope: component tests proving the two rebind defects the docstring task reported (a rebind under other disposal
names disposes new objects with the old methods; a held slotted spell rebound as `many` fails its next meld and
loses the object), strict xfails asserting the corrected contract plus passing controls, run with the GIL off and on
and shown to the owner; tests_components entries; the rebuild last. No src change. State: in_progress, melder_3; the
closure is held while the owner talks it through. Done: the module written and run (6 passed, 4 xfailed, the GIL off
and on), `--runxfail` shows both defects, a stand-in fix flips all four; tests_components and tests_architecture
record it, both indexes checked, tests_components released to melder_1 (M3-16). Owner's model (03:04-03:35 MDT):
creations have nothing to do with the spell that made them, and `cleanup_spell` is not to be tied to them; the
defect is the store filing objects by a spell_id two spells share (ALIGNMENT_CHECK of 2026-10-25T09:36:16Z). Ruled
(03:42 MDT): other disposal names on a live class are the user's responsibility - defect 1 is not a defect (DECISION
of 2026-10-25T09:43:13Z). Holds: his go to remove that test and its doc entries, his call on the existence change (a
meld returning a list, AttributeError, purge TypeError), and E7. Next: close on his word, the rebuild last; the fix
is a src lane on his word.

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
