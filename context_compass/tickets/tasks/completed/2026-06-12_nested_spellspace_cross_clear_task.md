

# Task: Root-cause nested-spellspace store cross-clear (A->B->C->D)

- Completed: 2026-06-12T21:06:51Z
- Summary: NOT a runtime bug. Receiver-traced clearing calls proved every
  clear was a scope's own LIFO exit-recycle; the failing test's post-D
  assertions were indented into scope B's body, reading C's storage after
  C's own legitimate exit. Test rewritten with per-level unwind assertions
  + regression note; independent regression test added; zero src changes.
  User accepted.

## Metadata
- Task ID: TASK-2026-06-12-nested-spellspace-cross-clear
- Story: none
- Status: done
- Owner: codex
- Agent Name: compiler_builder_0
- Priority: p1
- Created: 2026-06-12T20:20:41Z
- Updated: 2026-06-12T21:06:51Z

## Objective
Identify and fix the code path that empties scope C's spellspace-local
creations store when nested scope D exits, restoring the intended recursive
spellspace contract (A->B->C->D with per-level storage isolation and LIFO
unwind).

## Ticket Contract
- ENTRY_GATE: forensic repro output from the user
  (`tests/experimentation/test_repro_nested_spellspace_cross_clear.py -q -s`).
- EXECUTION_BOUNDARY: spellspace/creations/pool/meld-door lane
  (`src/melder/aether/conduit/spell_space/`, `creations/`, `meld/`); if the
  guilty stack lands in emitted-door/compiler code, hand off with evidence.
- DEPENDENCIES: none.
- EXIT_GATE: `test_component_spellspace_nested_scope_stack_isolation` green;
  repro test green; user confirms.
- FAILURE_ESCALATION: CONFLICT + handoff note if the captured stack points
  into compiler-emitted executors (compiler agents' lane).

## Scope Boundaries
- In scope: the cross-clear root cause and minimal fix + regression test.
- Out of scope: unrelated spellspace performance work.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Root cause proven (test indentation defect, runtime
  exonerated), fixes landed, both tests green on the user's machine, and
  the user confirmed acceptance.

## Steps / Checklist
- [x] Instrument component test with layer-pinpointing asserts
- [x] Static elimination: store, thread-state, pool, door templates, rebinds
- [x] Build forensic repro with tracing dicts + rebind detection
- [ ] User runs repro; capture guilty stack or aliasing trip
- [ ] Implement fix in owning lane (or hand off with stack evidence)
- [ ] Regression test named for the symptom
- [ ] Run Ticket Microcycle during execution.

## Deliverables
- Root-cause evidence (captured stack), fix, regression test.

## Files / Paths Impacted
- tests/experimentation/test_repro_nested_spellspace_cross_clear.py (new)
- tests/component/melder/aether/conduit/test_conduit_component_fast_meld_door.py
- fix target: UNKNOWN until repro runs

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/experimentation/test_repro_nested_spellspace_cross_clear.py -q -s`
  - `pytest tests/component/melder/aether/conduit/test_conduit_component_fast_meld_door.py -q`

## Risks / Rollback Notes
- The bug violates the user-stated recursive spellspace contract; risk of
  silent wrong-instance reuse in any nested-scope workload until fixed.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: none
- CLEANUP_TRIGGER: none

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
- DATETIME: 2026-06-12T20:20:41Z
  TYPE: FACT
  CLAIM: Failure is a storage cross-clear, not a meld-lane bug: at depth all
    four shells and stores are identity-distinct and marker_c is present in
    C's store; after D's exit a DIRECT store read returns None. Fast door
    exonerated (no meld in the failing read).
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_fast_meld_door.py:678-717
  IMPACT: Suspect set narrowed to D's exit path or a hidden aliasing layer.
  NEXT: user runs the forensic repro.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-12T20:20:41Z
  TYPE: FACT
  CLAIM: Static elimination complete: Creations builds fresh dicts per
    instance and get_creation is a plain dict read; reset_for_pool_unlocked
    clears in place; clear_all REBINDS the inner dict (tracer-bypass route,
    covered by identity check in the repro); thread-state pop validates LIFO;
    pool `_target_idle` starts at baseline 20 so release never destroys in
    the failing test; emitted door templates are stateless per call against
    the passed wrapper; no post-init rebinds of `_creations` anywhere in the
    conduit subtree.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:74-84
  - src/melder/aether/conduit/creations/creations.py:451-487
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:174-195
  - src/melder/utilities/general_base/abstract_elastic_pool.py:129-129
  IMPACT: No static suspect remains; only empirical capture can name the
    culprit.
  NEXT: forensic repro run on user machine.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-12T20:35:00Z
  TYPE: FACT
  CLAIM: The standalone forensic repro PASSED (user-run, 1 passed in 0.21s)
    while the component test fails inside its file run. Two surviving
    hypotheses: (a) cross-test contamination - the component failure needs
    state left by earlier tests in the same file (repro ran solo); (b)
    instrumentation-as-fix - installing the tracer rebinds C's inner dict,
    detaching an alias some layer captured earlier, so the guilty clear hits
    the orphaned dict harmlessly.
  EVIDENCE:
  - tests/experimentation/test_repro_nested_spellspace_cross_clear.py:212-271
  IMPACT: Discriminator is cheap: run the component test SOLO. Solo-pass
    implicates (a) and turns this into a bisect over the preceding tests in
    the file; solo-fail implicates (b) and the alias capture layer.
  NEXT: user runs the single component test by node id, then the full file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-12T21:40:00Z
  TYPE: FACT
  CLAIM: Discriminator resolved: the component test FAILS solo (user-run,
    1 failed in 0.26s), so cross-test contamination is dead. Combined with
    the v1 repro passing, the alias-capture hypothesis is confirmed in
    shape: rebinding C's inner dict (tracer install) detached an alias and
    the bug vanished; the guilty clear therefore travels through a captured
    non-wrapper reference to C's ORIGINAL inner dict. Every wrapper-surface
    clear is excluded (v1 tracer would have recorded it).
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_fast_meld_door.py:711-717
  IMPACT: The hunt narrows to "who holds C's inner dict"; GC referrer
    snapshots can name the holder directly.
  NEXT: user runs repro v2 (identity-preserving, gc.get_referrers at three
    points, case classification).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-12T22:05:00Z
  TYPE: FACT
  CLAIM: Repro v2 (identity-preserving referrer forensics) PASSED clean in
    its standalone file: exactly ONE holder of C's inner dict at all three
    snapshots (the owning Creations wrapper), no alias, no loss. Combined
    with the component test failing solo, the differential is now the
    component file's own environment (its conftest chain, its module state,
    or its preceding definitions), not the nested flow itself.
  EVIDENCE:
  - tests/experimentation/test_repro_nested_spellspace_cross_clear.py:147-233
  IMPACT: Flow-mirroring outside the failing file cannot reproduce; the
    forensics must run inside the failing test.
  NEXT: forensics ported into
    `test_component_spellspace_nested_scope_stack_isolation` itself
    (identity-preserving, same classification + referrer dump); user runs
    the solo component test again and the failure report names the holder.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-12T22:30:00Z
  TYPE: FACT
  CLAIM: In-place forensics ran in the failing environment (user-run):
    case = IN-PLACE CLEAR, and C's inner dict has exactly ONE holder at all
    three snapshots. Two consequences: (1) the v1 "instrumentation fixed it"
    inference was wrong - the standalone file simply never triggers the bug;
    (2) there is NO long-lived alias: the clear travels through a TRANSIENT
    reference that exists only inside D's exit window, invisible to
    before/after snapshots.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_fast_meld_door.py:780-797
  IMPACT: Snapshot-based forensics cannot catch a transient; method-level
    receiver tracing can.
  NEXT: trap installed - all four Creations clearing surfaces
    (reset_for_pool_unlocked/reset_for_pool/clear_all/cleanup) are wrapped
    for the exit window, recording receiver identity + full stack; report
    now also prints all four wrapper ids for receiver matching. User reruns
    the solo test. Zero recorded calls + loss = the clear bypasses wrapper
    methods entirely (raw dict mutation from emitted code).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-12T23:20:00Z
  TYPE: FACT
  CLAIM: ROOT CAUSE FOUND - NOT A RUNTIME BUG. The receiver trap recorded
    exactly two clearing calls in the exit window: D's own exit-recycle,
    then C's own exit-recycle (receiver = C's wrapper, stack = C's `with`
    line -> SpellSpace.__exit__ -> recycle, LIFO-clean, pop_expected
    succeeded). The test's post-D assertion block was indented one dedent
    level too shallow (scope B's body), so it read C's storage AFTER C's own
    legitimate exit had recycled it. The phantom "cross-clear" was a test
    indentation defect present since the test was authored
    (by compiler_builder_0's own earlier work). Runtime A->B->C->D nesting
    was always correct - which is also why both standalone repros (written
    with correct indentation) passed.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_fast_meld_door.py:680-700
  - src/melder/aether/conduit/spell_space/spell_space.py:167-198
  IMPACT: Runtime exonerated with receiver-traced proof; no src change
    needed or made.
  NEXT: fix landed - component test re-indented with per-level LIFO unwind
    assertions (D-exit checked in C's body, C-exit in B's, B-exit in A's),
    forensic machinery stripped, regression note in the docstring;
    experimentation file rewritten as an independent correctly-structured
    regression test. User runs both; expected green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Nested-spellspace cross-clear (component test
`test_component_spellspace_nested_scope_stack_isolation`) is reproducible on
the user's machine and static analysis is exhausted with evidence. The
forensic repro (`tests/experimentation/test_repro_nested_spellspace_cross_clear.py`)
installs tracing dicts on scopes C and D that capture full stacks on every
destructive mutation and detect inner-dict rebinds and shell aliasing.
Blocked on one user run; its output names the guilty layer.
