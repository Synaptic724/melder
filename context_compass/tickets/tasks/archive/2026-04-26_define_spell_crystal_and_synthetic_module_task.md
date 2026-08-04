# Task: Define Spell Crystal And Synthetic Module

## Metadata
- Task ID: TASK-2026-04-26-define-spell-crystal-and-synthetic-module
- Story:
- Epic: EPIC-2026-04-26-design-crystallizer-asset-provenance-layer
- Status: in_progress
- Owner: codex
- Agent Name: codex_0
- Priority: p1
- Created: 2026-04-26T21:30:45Z
- Updated: 2026-04-26T23:12:53Z
- Updated: 2026-05-03T19:24:03Z
- Updated: 2026-05-03T21:21:27Z
- Updated: 2026-05-09T16:22:14Z
- Updated: 2026-05-09T16:24:31Z
- Updated: 2026-05-09T16:36:24Z

## Objective
Define the first two real crystallizer primitives:
- `SpellCrystal`
- `SyntheticModule`

Leave `Crystallizer` itself empty for now.

## Ticket Contract
- ENTRY_GATE: the crystallizer package scaffold is already in place and the
  user explicitly asked to begin with `spell_crystal.py` and
  `synthetic_module.py`.
- EXECUTION_BOUNDARY:
  - `src/melder/crystallizer/spell_crystal.py`
  - `src/melder/crystallizer/synthetic_module.py`
  - this task ticket
  - `attention_board.md`
- DEPENDENCIES:
  - `src/melder/utilities/general_base/cleanable.py`
  - `src/melder/utilities/interfaces/interfaces.py`
  - crystallizer artifact stack
- EXIT_GATE: both files define coherent initial contracts with docstrings,
  cleanup/lifecycle behavior, and enough fields/methods to anchor later
  crystallizer work.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if `SyntheticModule` cleanup
  semantics conflict with `ModuleType` subclassing strongly enough that a
  separate wrapper object would be cleaner.

## Scope Boundaries
- In scope:
  - `SpellCrystal` initial state model
  - `SyntheticModule` initial live module model
  - lifecycle/cleanup and state mutation methods needed for V1/V2 groundwork
- Out of scope:
  - `Crystallizer` facade logic
  - persistence adapters
  - loader/bootstrap logic
  - tests unless a tiny local syntax issue forces them

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested the first implementation
  slice for `SpellCrystal` and `SyntheticModule`.

## Steps / Checklist
- [ ] Review local cleanup and typing patterns.
- [ ] Define `SpellCrystal`.
- [ ] Define `SyntheticModule`.
- [ ] Record the resulting contracts in `## Notes`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `SpellCrystal` initial contract
- `SyntheticModule` initial contract

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-26_define_spell_crystal_and_synthetic_module_task.md
- codex/context_compass/attention_board.md
- src/melder/crystallizer/spell_crystal.py
- src/melder/crystallizer/synthetic_module.py

## Validation
- Executed:
  - `python -m py_compile src/melder/crystallizer/spell_crystal.py src/melder/crystallizer/synthetic_module.py`
  - runtime smoke instantiation through `PYTHONPATH=src` for `SpellCrystal`
    and `SyntheticModule`
  - `python -m pytest -q -s tests/experimentation/test_lock_cleanup_reference_release_experiment.py`
- Result:
  - compile check passed
  - runtime smoke check passed
  - lock-reference cleanup experiment passed (`1 passed`)

## Risks / Rollback Notes
- Risk: overbuilding these two objects too early will freeze bad assumptions
  into the subsystem.
  Rollback: keep the first slice limited to core state, lifecycle, and small
  mutation helpers only.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: task closure

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-26T21:30:45Z
  TYPE: PLAN
  CLAIM: The first real crystallizer implementation slice should define the
    stored asset unit and the live in-memory module unit before any facade or
    loader logic is added. `SpellCrystal` should anchor persisted source/module
    truth, and `SyntheticModule` should anchor the live module embodiment.
  EVIDENCE:
  - user_instruction: define `spell_crystal` and `synthetic module` first
  IMPACT: The implementation can stay small and foundational instead of
    spreading across the whole package.
  NEXT: patch `spell_crystal.py` and `synthetic_module.py` only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T21:35:50Z
  TYPE: FACT
  CLAIM: The first two crystallizer primitives now exist. `SpellCrystal` is a
    persisted source-bearing unit with source/hash, import/export/dependency,
    materialization, and active-runtime linkage state. `SyntheticModule` is a
    live `ModuleType` subclass with source/hash metadata, namespace merge
    support, explicit `sys.modules` publication control, and cleanup behavior.
  EVIDENCE:
  - src/melder/crystallizer/spell_crystal.py:1-426
  - src/melder/crystallizer/synthetic_module.py:1-317
  IMPACT: The crystallizer package now has both its first stored-unit contract
    and its first live-module contract, which is enough to start building the
    facade, analysis, and loader layers later.
  NEXT: review the object contracts and decide whether to keep their current
    field/method surface or trim/add anything before we implement surrounding
    systems.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T21:35:50Z
  TYPE: FACT
  CLAIM: The first `SyntheticModule` draft initially failed the runtime smoke
    check because `ModuleType` and `Cleanable` cannot be multiply inherited in
    this environment due to instance-layout conflict. The class was corrected
    to remain a pure `ModuleType` subclass while mirroring the repo cleaned-state
    contract directly (`_cleaned`, `cleaned`, `is_cleaned`, `check_cleaned`,
    `cleanup`).
  EVIDENCE:
  - runtime_error: `TypeError: multiple bases have instance lay-out conflict`
  - src/melder/crystallizer/synthetic_module.py:1-317
  IMPACT: The live module object keeps the cleanup semantics we need without
    forcing an invalid inheritance shape onto a builtin runtime type.
  NEXT: preserve this direct-cleanup pattern for `SyntheticModule` unless we
    later introduce a wrapper object instead of subclassing `ModuleType`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T21:35:50Z
  TYPE: MEASURE
  CLAIM: Both new crystallizer modules pass narrow compile and runtime smoke
    validation.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/crystallizer/spell_crystal.py src/melder/crystallizer/synthetic_module.py`
  - validation_result: `PYTHONPATH=src python -c "... SpellCrystal ... SyntheticModule ..."` -> `crystal-1`, `demo.module`
  IMPACT: The slice is ready for review without known syntax or constructor
    path failures.
  NEXT: return the slice for review and decide whether to move next into
    `CrystallizerConfiguration`, `asset_transaction`, or `CrystalAnalyzer`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T21:44:12Z
  TYPE: FACT
  CLAIM: The first draft is not thread-safe enough for this repo yet. The
    objects allocate an `RLock`, but most public reads and writes do not take
    that lock, and the internal fields are not typed explicitly enough for the
    repo's typing discipline.
  EVIDENCE:
  - src/melder/crystallizer/spell_crystal.py:128-153
  - src/melder/crystallizer/spell_crystal.py:177-663
  - src/melder/crystallizer/synthetic_module.py:1-317
  IMPACT: The task must return to implementation and harden both objects before
    the slice is ready for review again.
  NEXT: add explicit internal attribute typing and lock all public reads/writes
    consistently.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T22:42:58Z
  TYPE: FACT
  CLAIM: The cleanup pattern has been corrected to match the repo rule the user
    called out. Both crystallizer objects now use the simple lock pattern in
    cleanup: check `_cleaned`, enter `with self._lock:`, re-check `_cleaned`,
    perform teardown, then drop the lock reference. The bogus `if self._lock is
    None` branch is gone.
  EVIDENCE:
  - src/melder/crystallizer/spell_crystal.py:169-213
  - src/melder/crystallizer/synthetic_module.py:109-144
  - validation_result: `python -m py_compile src/melder/crystallizer/spell_crystal.py src/melder/crystallizer/synthetic_module.py`
  IMPACT: The two crystallizer primitives now follow the repo cleanup style
    more closely and no longer carry the fake defensive teardown branch.
  NEXT: continue tightening any remaining style/mechanics mismatches against the
    live runtime patterns before moving on to the next crystallizer component.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-26T23:12:53Z
  TYPE: MEASURE
  CLAIM: The lock-reference cleanup question now has a real repo-backed proof.
    The experiment file under `tests/experimentation/` shows that all three
    cases release the original `RLock` correctly:
    - nulling the reference inside the `with` block
    - nulling it after the block
    - keeping the reference
    In all three cases, another thread successfully acquires the original lock
    after cleanup completes.
  EVIDENCE:
  - tests/experimentation/test_lock_cleanup_reference_release_experiment.py:1-96
  - validation_result: `python -m pytest -q -s tests/experimentation/test_lock_cleanup_reference_release_experiment.py` -> `1 passed`
  IMPACT: The discussion about whether `self._lock = None` breaks release is
    now settled by a repo-local executable proof rather than chat-only claims.
  NEXT: use this proof as the baseline when deciding the final post-cleanup
    lock-reference policy for crystallizer objects.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T19:24:03Z
  TYPE: PLAN
  CLAIM: This task is being re-used for the first narrowed `SpellCrystal`
    implementation slice. The current goal is no longer broad persisted crystal
    state. It is to turn `SpellCrystal` into a spell-targeted module dependency
    manifest built from `ISpell`, rooted at the concrete spell SHA and the
    spell's module world. The slice should add root-module resolution,
    dependency walking, target classification, and a simple synthetic-module
    sentinel while explicitly staying out of bind replay and live runtime state
    mirroring.
  EVIDENCE:
  - tickets/epics/2026-05-03_implement_spell_crystal_loader_manifest_epic.md:1-98
  - user_instruction: "yeah start with that in this slice go ahead please"
  IMPACT: The next code patch can stay tightly bounded to `spell_crystal.py`
    and the synthetic-module sentinel instead of drifting back into broader
    crystal speculation.
  NEXT: patch `spell_crystal.py`, patch the synthetic-module sentinel, and run
    a syntax check.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T19:24:03Z
  TYPE: MEASURE
  CLAIM: The first narrowed `SpellCrystal` slice is now landed. The class now
    builds from `ISpell`, captures the concrete spell SHA, resolves the root
    target/module, recursively walks tracked module dependencies, classifies
    user-source/site-package/synthetic targets, and exposes flat loader-facing
    target lists and lookup maps instead of the older persisted-source/live
    runtime record shape. `SyntheticModule` now carries a simple explicit
    sentinel so the walker can recognize it without guesswork.
  EVIDENCE:
  - src/melder/crystallizer/spell_crystal.py:1-530
  - src/melder/crystallizer/synthetic_module.py:1-18
  - validation_result: `python -m py_compile src/melder/crystallizer/spell_crystal.py src/melder/crystallizer/synthetic_module.py`
  IMPACT: The loader-manifest direction now exists in code and can be reviewed
    before we widen the crystal into deeper asset or loader integration.
  NEXT: review the retained field set and the module-classification/dependency
    walk behavior before adding any more crystal responsibilities.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T21:21:27Z
  TYPE: FACT
  CLAIM: The next bounded cleanup in this slice is the synthetic-module type
    seam itself. The current code uses a magic
    `__melder_synthetic_module__ = True` marker on `SyntheticModule` and then
    probes that marker from `SpellCrystal` with `getattr(...)`. That is weaker
    than the repo's protocol-first direction and also collides with the
    user's explicit `getattr` rules for owned/declared contracts.
  EVIDENCE:
  - src/melder/crystallizer/synthetic_module.py:8-30
  - src/melder/crystallizer/spell_crystal.py:292-355
  - user_instruction: "what are my getattr rules"
  - user_instruction: "in synthetic_module why are we adding a variable to identify its a syntheticmodule"
  IMPACT: The next change should replace the marker with a shared
    `ISyntheticModule` protocol in `utilities/interfaces.py`, make
    `SyntheticModule` inherit it, and switch `SpellCrystal` to protocol/direct
    access instead of magic-marker introspection.
  NEXT: add `ISyntheticModule`, remove the marker flag, patch
    `SpellCrystal`, then run targeted validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T21:24:24Z
  TYPE: DECISION
  CLAIM: The synthetic-module seam is now patched toward the protocol-first
    shape. `ISyntheticModule` has been added to the shared interfaces file,
    `SyntheticModule` now inherits it alongside `ModuleType` while keeping the
    normal Melder internal sentinel, the magic
    `__melder_synthetic_module__ = True` marker is removed, and the
    `SpellCrystal` synthetic-module path now uses the protocol/direct property
    access instead of marker-based `getattr(...)`.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:49-191
  - src/melder/crystallizer/synthetic_module.py:1-31
  - src/melder/crystallizer/spell_crystal.py:9-11
  - src/melder/crystallizer/spell_crystal.py:259-265
  - src/melder/crystallizer/spell_crystal.py:292-355
  - src/melder/crystallizer/spell_crystal.py:398-402
  IMPACT: The crystallizer layer is now using a stronger shared type seam for
    synthetic modules and is cleaner against the user's owned-code `getattr`
    rules.
  NEXT: run targeted compile and runtime smoke validation for the new protocol
    seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T21:25:02Z
  TYPE: MEASURE
  CLAIM: The protocol seam is green. The targeted compile pass succeeded for
    `interfaces.py`, `synthetic_module.py`, and `spell_crystal.py`; a runtime
    smoke check confirms `SyntheticModule` instantiates, satisfies
    `ISyntheticModule` at runtime, and still cleans up correctly; and the old
    `__melder_synthetic_module__` marker path is gone from the two crystallizer
    files.
  EVIDENCE:
  - validation_result:
    `python -m py_compile "src/melder/utilities/interfaces/interfaces.py" "src/melder/crystallizer/synthetic_module.py" "src/melder/crystallizer/spell_crystal.py"`
  - validation_result:
    runtime smoke -> `SyntheticModule`, `True`, `demo.synthetic`, `True`
  - source_scan:
    `src/melder/crystallizer/synthetic_module.py:7-9`
  - source_scan:
    `src/melder/crystallizer/spell_crystal.py:12-12`
  - source_scan:
    `src/melder/crystallizer/spell_crystal.py:292-355`
  IMPACT: The synthetic-module detection seam is now stronger and cleaner
    against the user's protocol/getattr rules.
  NEXT: return this slice for review and decide whether to keep tightening the
    remaining `getattr` use in `SpellCrystal`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T21:31:41Z
  TYPE: DECISION
  CLAIM: The next small cleanup on this seam is to make `ISyntheticModule`
    inherit the cleanable protocol contract. The concrete `SyntheticModule`
    still cannot inherit the `Cleanable` base class because `ModuleType` and
    `Cleanable` have a layout conflict, but the protocol can and should carry
    that semantic relationship.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:13-48
  - src/melder/utilities/interfaces/interfaces.py:49-191
  - runtime_probe:
    `class Probe(ModuleType, Cleanable): pass` -> `TypeError: multiple bases have instance lay-out conflict`
  IMPACT: This strengthens the type contract without reintroducing the runtime
    inheritance problem.
  NEXT: patch `ISyntheticModule(ICleanable, Protocol)` and rerun the targeted
    compile/runtime smoke validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T21:32:17Z
  TYPE: MEASURE
  CLAIM: The cleanable-protocol relationship is green. `ISyntheticModule` now
    inherits `ICleanable`, the targeted compile pass still succeeds, and a
    runtime smoke check confirms `SyntheticModule` still satisfies both
    `ISyntheticModule` and `ICleanable` at runtime without inheriting the
    concrete `Cleanable` base.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:49-49
  - validation_result:
    `python -m py_compile "src/melder/utilities/interfaces/interfaces.py" "src/melder/crystallizer/synthetic_module.py" "src/melder/crystallizer/spell_crystal.py"`
  - validation_result:
    runtime smoke -> `SyntheticModule`, `True`, `True`, `True`
  IMPACT: The synthetic-module seam now carries the right cleanup semantics at
    the protocol level while avoiding the `ModuleType` layout conflict on the
    concrete runtime class.
  NEXT: return this small seam cleanup for review or continue tightening the
    remaining owned-contract introspection inside `SpellCrystal`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T21:34:50Z
  TYPE: MEASURE
  CLAIM: The remaining owned-contract `getattr(...)` path in `SpellCrystal`
    has now been tightened. The root target identity path uses explicit type
    branching instead of generic attribute probing, the root module fallback
    path now uses direct access where the contract is known, the
    synthetic-module path now uses direct protocol property access, and the
    file still compiles and instantiates cleanly as a manifest.
  EVIDENCE:
  - src/melder/crystallizer/spell_crystal.py:223-278
  - src/melder/crystallizer/spell_crystal.py:287-322
  - src/melder/crystallizer/spell_crystal.py:394-402
  - validation_result:
    `python -m py_compile "src/melder/utilities/interfaces/interfaces.py" "src/melder/crystallizer/synthetic_module.py" "src/melder/crystallizer/spell_crystal.py"`
  - validation_result:
    runtime smoke -> `spell-1`, `SpellCrystal`, `class`,
    `melder.crystallizer.spell_crystal`, `module_targets_len 236`, `True`
  - source_scan:
    `Select-String spell_crystal.py -Pattern 'getattr\\('` -> no matches
  IMPACT: The current `SpellCrystal` slice is materially cleaner against the
    user's owned-contract `getattr` rules than the earlier draft.
  NEXT: return the current `SpellCrystal` state for review and decide the next
    remaining seam to tighten.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T21:44:23Z
  TYPE: PLAN
  CLAIM: The next bounded pass is a direct `SpellCrystal` review/cleanup pass.
    The immediate goal is to reread the class end-to-end, verify what it is
    actually doing now, and then tighten the docstrings and contract wording so
    the implementation and its loader-facing responsibilities are explicit.
  EVIDENCE:
  - user_instruction: "so cool lets focus on spell crystal and what its doing lets review whats going on here add docstrings and fully understand this"
  IMPACT: The current work is no longer just seam cleanup. It is a focused
    implementation review and documentation-hardening pass on
    `spell_crystal.py`.
  NEXT: reread `spell_crystal.py` in bounded chunks, identify the real contract
    surfaces that need stronger docstrings, then patch them directly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T21:46:07Z
  TYPE: MEASURE
  CLAIM: The documentation-hardening pass is landed and green. The constructor,
    cleanup path, root-target resolution, module-path/classification helpers,
    source extraction, AST import extraction, dependency walk, and
    `describe()` now carry richer contract-first docstrings, and the file still
    compiles and instantiates cleanly as a manifest.
  EVIDENCE:
  - src/melder/crystallizer/spell_crystal.py:58-146
  - src/melder/crystallizer/spell_crystal.py:254-322
  - src/melder/crystallizer/spell_crystal.py:393-619
  - src/melder/crystallizer/spell_crystal.py:808-838
  - validation_result:
    `python -m py_compile "src/melder/crystallizer/spell_crystal.py"`
  - validation_result:
    runtime smoke -> `spell-1`, `SpellCrystal`,
    `melder.crystallizer.spell_crystal`, `True`
  IMPACT: The current `SpellCrystal` slice is now easier to reason about from
    source without relying on ticket notes or chat history.
  NEXT: return the file for review and decide whether the next issue to fix is
    dependency completeness, user-root classification, or another loader-facing
    manifest seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T21:44:23Z
  TYPE: PLAN
  CLAIM: The next `SpellCrystal` upgrade is the real correctness pass for the
    current loader manifest slice: make dependency reporting honest, replace
    the cwd-only user-source root model with explicit configurable roots, and
    keep the output boundary cleanly loader-facing. This also needs a small
    targeted test file so the behavior is executable rather than only described.
  EVIDENCE:
  - user_instruction: "So the real upgrade is: honesty configurable source roots clean loader manifest boundaries"
  - src/melder/crystallizer/spell_crystal.py:193-197
  - src/melder/crystallizer/spell_crystal.py:605-605
  IMPACT: The next patch should change both the implementation and the local
    tests, not just the docstrings.
  NEXT: patch `spell_crystal.py` for configurable roots + unknown dependency
    recording and add a focused pytest file for those two contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T22:31:52Z
  TYPE: RISK
  CLAIM: The first focused pytest run for the new `SpellCrystal` test file
    stalled long enough that the outer harness was manually aborted. The code
    patch itself was already in place, but the validation pass was too loose
    because the whole file was run at once and the only hard stop was the outer
    shell timeout.
  EVIDENCE:
  - validation_result:
    `python -m pytest -q tests/unit/melder/crystallizer/test_spell_crystal.py`
    -> outer command stalled and was manually aborted
  IMPACT: The next validation pass needs tighter discipline: one test at a
    time, hard shell timeouts, and explicit isolation of whichever test is
    sticky before claiming the file is green.
  NEXT: rerun each `SpellCrystal` test individually with a short timeout and
    isolate the exact hang point.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T22:40:10Z
  TYPE: DECISION
  CLAIM: The right fix is to stop treating the second `SpellCrystal` test as a
    hang-debugging problem and rewrite it as an actual unit test. The current
    version mutates `sys.path`, imports a temporary package through
    `importlib`, and tears down module cache plus filesystem state; that is
    integration-style behavior for a test that only needs to prove configurable
    source-root classification. The replacement should use direct module stubs
    plus real file paths under `C:\\tmp` so the same manifest seam is tested
    without import machinery.
  EVIDENCE:
  - tests/unit/melder/crystallizer/test_spell_crystal.py:53-94
  - user_instruction: "yo bro just make a normal fucken pytest that properly times out"
  IMPACT: The next patch should simplify the test rather than adding more
    timeout machinery around a bad test shape.
  NEXT: replace the importlib/sys.path-based second test with a direct
    module-stub unit test and rerun the focused file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T23:46:03Z
  TYPE: PLAN
  CLAIM: The next bounded validation tranche should stop at the actual loader
    manifest contract instead of adding shallow coverage. The honest split is:
    unit tests for pure `SpellCrystal` dependency walking on live synthetic
    module objects, component tests for real physical and mixed
    physical/synthetic module graphs, and one integration test that builds a
    real `Spellbook` spell through `bind(...)` and then crystallizes that live
    spell.
  EVIDENCE:
  - tickets/epics/2026-05-03_implement_spell_crystal_loader_manifest_epic.md:24-42
  - tickets/epics/2026-05-03_implement_spell_crystal_loader_manifest_epic.md:154-156
  - user_instruction: "the core test here is ensuring we properly walk the dependencies and map them right"
  IMPACT: The test pass stays aligned with the current loader-facing crystal
    direction instead of drifting into low-value surface assertions.
  NEXT: add one stable test-data package under `tests/`, then patch the unit,
    component, and integration test files around dependency walking and
    mapping.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T23:50:01Z
  TYPE: MEASURE
  CLAIM: The three-layer SpellCrystal test ring is now landed and green. The
    unit file covers honest unknown-import reporting, pure synthetic-module
    dependency walking, and configured user-source roots. The new component
    file covers a real physical dependency graph plus a mixed
    physical/synthetic graph. The integration file covers the real
    `Spellbook.bind(...)` path and then crystallizes that live spell into a
    dependency manifest. All six tests passed under the direct `.venv_new`
    interpreter path with `PYTHONPATH=src;.` and no PowerShell activation
    script.
  EVIDENCE:
  - tests/unit/melder/crystallizer/test_spell_crystal.py:1-175
  - tests/component/melder/crystallizer/test_spell_crystal_component.py:1-124
  - tests/integration/melder/crystallizer/test_spell_crystal_integration.py:1-98
  - tests/mocks/crystallizer/spell_crystal_demo_pkg/root.py:1-20
  - tests/mocks/crystallizer/spell_crystal_demo_pkg/root_with_synthetic.py:1-21
  - validation_result:
    `<local-workspace>\\.venv_new\\Scripts\\python.exe -m pytest -q -p no:cacheprovider tests/unit/melder/crystallizer/test_spell_crystal.py` -> `3 passed`
  - validation_result:
    `<local-workspace>\\.venv_new\\Scripts\\python.exe -m pytest -q -p no:cacheprovider tests/component/melder/crystallizer/test_spell_crystal_component.py` -> `2 passed`
  - validation_result:
    `<local-workspace>\\.venv_new\\Scripts\\python.exe -m pytest -q -p no:cacheprovider tests/integration/melder/crystallizer/test_spell_crystal_integration.py` -> `1 passed`
  IMPACT: The current loader-facing SpellCrystal slice now has executable proof
    across unit, component, and integration levels instead of only ticket
    claims and experimentation context.
  NEXT: return the test-complete slice for review and decide whether the next
    crystal seam is dependency completeness depth, loader activation, or
    persisted manifest shape.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-04T00:19:23Z
  TYPE: MEASURE
  CLAIM: The deeper dependency-walk harness is now in place and the collected
    test counts meet the requested scale for this tranche. The unit ring uses
    ten synthetic graph cases across closed linear/branch/relative/re-export/
    duplicate-import shapes for 92 collected tests. The component ring uses
    ten real physical or mixed physical/synthetic root modules under
    `tests.mocks.crystallizer.spell_crystal_demo_pkg` for 40 collected tests.
    The integration ring uses the same ten real root cases through the live
    `Spellbook.bind(...)` path for 80 collected tests. All three files are
    green under the direct `.venv_new` interpreter path with
    `PYTHONPATH=src;.`.
  EVIDENCE:
  - tests/mocks/crystallizer/spell_crystal_harness.py:1-724
  - tests/unit/melder/crystallizer/test_spell_crystal.py:1-191
  - tests/component/melder/crystallizer/test_spell_crystal_component.py:1-126
  - tests/integration/melder/crystallizer/test_spell_crystal_integration.py:1-168
  - validation_result:
    `python.exe -m pytest --collect-only -q -p no:cacheprovider tests/unit/melder/crystallizer/test_spell_crystal.py` -> `92 tests collected`
  - validation_result:
    `python.exe -m pytest --collect-only -q -p no:cacheprovider tests/component/melder/crystallizer/test_spell_crystal_component.py` -> `40 tests collected`
  - validation_result:
    `python.exe -m pytest --collect-only -q -p no:cacheprovider tests/integration/melder/crystallizer/test_spell_crystal_integration.py` -> `80 tests collected`
  - validation_result:
    `python.exe -m pytest -q -p no:cacheprovider tests/unit/melder/crystallizer/test_spell_crystal.py` -> `92 passed`
  - validation_result:
    `python.exe -m pytest -q -p no:cacheprovider tests/component/melder/crystallizer/test_spell_crystal_component.py` -> `40 passed`
  - validation_result:
    `python.exe -m pytest -q -p no:cacheprovider tests/integration/melder/crystallizer/test_spell_crystal_integration.py` -> `80 passed`
  IMPACT: The current loader-facing `SpellCrystal` slice now has deep,
    repeatable coverage around dependency walking, direct-dependency mapping,
    module-kind classification, and live bind-to-crystal handoff instead of
    relying on a tiny smoke ring.
  NEXT: use this harness as the baseline when the next crystal seam widens
    into loader activation, dependency completeness policy, or persisted
    manifest serialization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-04T00:53:09Z
  TYPE: DECISION
  CLAIM: `SyntheticModule` now owns the importlib-grade live-world mechanics
    the experiments justified. The class is no longer only a metadata-bearing
    `ModuleType` wrapper. It now carries package-shell semantics, parent-package
    binding, a class-level synthetic import registry, `MetaPathFinder` /
    `Loader` support, direct materialize/import/reload flows, and early
    publication behavior so benign circular worlds can load with importlib-style
    semantics while bad partial-init cycles still fail loudly. A focused unit
    ring for those mechanics is also green.
  EVIDENCE:
  - src/melder/crystallizer/synthetic_module.py:1-1024
  - src/melder/utilities/interfaces/interfaces.py:69-214
  - tests/unit/melder/crystallizer/test_synthetic_module.py:1-214
  - validation_result:
    `python.exe -m pytest -q -p no:cacheprovider tests/unit/melder/crystallizer/test_synthetic_module.py` -> `5 passed`
  - validation_result:
    `python.exe -m pytest -q -p no:cacheprovider tests/unit/melder/crystallizer/test_spell_crystal.py` -> `92 passed`
  - validation_result:
    `python.exe -m pytest -q -p no:cacheprovider tests/component/melder/crystallizer/test_spell_crystal_component.py` -> `40 passed`
  - validation_result:
    `python.exe -m pytest -q -p no:cacheprovider tests/integration/melder/crystallizer/test_spell_crystal_integration.py` -> `80 passed`
  IMPACT: The synthetic-module side is now much closer to the world-first
    runtime model described in the artifacts and experiments. Future loader work
    can lean on importlib-compatible activation behavior instead of ad hoc
    `exec()` blobs, while `SpellCrystal` remains the dependency-truth and
    validation owner.
  NEXT: decide whether the next loader-facing seam belongs in
    `SpellCrystal`/`CrystallizerLoader` orchestration or in expanding
    `SyntheticModule` graph-manifest support further.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-04T10:45:33Z
  TYPE: MEASURE
  CLAIM: The synthetic-module experiment lane now has a durable test pyramid.
    A large portion of the earlier synthetic-module experiments was translated
    into repeatable unit/component/integration tests under the crystallizer
    test tree. The final collected ratio for the dedicated
    `SyntheticModule` suite is:
    - unit: 80
    - component: 40
    - integration: 40
    The unit layer now covers successful synthetic world cases directly
    through the production `SyntheticModule` class instead of only through
    experiment-local loaders. The component layer reuses the deep physical to
    synthetic semantics experiments as durable checks around swap, reload,
    collision, and morph behavior. The integration layer reuses the deeper
    importlib, unittest, and Melder bind/drop-dependency experiments as
    durable same-process runtime checks.
  EVIDENCE:
  - tests/mocks/crystallizer/synthetic_module_harness.py:1-462
  - tests/unit/melder/crystallizer/test_synthetic_module.py:1-370
  - tests/component/melder/crystallizer/test_synthetic_module_component.py:1-163
  - tests/integration/melder/crystallizer/test_synthetic_module_integration.py:1-127
  - validation_result:
    `python.exe -m pytest --collect-only -q -p no:cacheprovider tests/unit/melder/crystallizer/test_synthetic_module.py` -> `80 tests collected`
  - validation_result:
    `python.exe -m pytest --collect-only -q -p no:cacheprovider tests/component/melder/crystallizer/test_synthetic_module_component.py` -> `40 tests collected`
  - validation_result:
    `python.exe -m pytest --collect-only -q -p no:cacheprovider tests/integration/melder/crystallizer/test_synthetic_module_integration.py` -> `40 tests collected`
  - validation_result:
    `python.exe -m pytest -q -p no:cacheprovider tests/unit/melder/crystallizer/test_synthetic_module.py` -> `80 passed`
  - validation_result:
    `python.exe -m pytest -q -p no:cacheprovider tests/component/melder/crystallizer/test_synthetic_module_component.py` -> `40 passed`
  - validation_result:
    `python.exe -m pytest -q -p no:cacheprovider tests/integration/melder/crystallizer/test_synthetic_module_integration.py` -> `40 passed`
  IMPACT: The synthetic-module side is no longer relying mainly on experiments
    to prove world-first behavior. The core runtime object now has a durable
    large-scale test ring covering importlib activation, circular semantics,
    cleanup, repeatability, same-process test-framework interactions, and real
    Melder integration seams.
  NEXT: use the durable suite as the baseline when widening
    `SyntheticModule` further or when moving more experiment-only edges into
    permanent tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-09T16:22:14Z
  TYPE: FACT
  CLAIM: The current `SpellCrystal` identity rename is only partially landed.
    The class now stores its concrete identity in `_id` at construction time,
    but `describe()` still emits `spell_id` and `spell_crystal_id` from the old
    `_spell_id` field name, which no longer exists on the object. The next
    bounded fix is to make `_id` the sole spell/crystal identity field and
    update the narrow SpellCrystal test surface to match.
  EVIDENCE:
  - src/melder/crystallizer/spell_crystal.py:44-69
  - src/melder/crystallizer/spell_crystal.py:134-137
  - src/melder/crystallizer/spell_crystal.py:1387-1388
  - tests/integration/melder/crystallizer/test_spell_crystal_integration.py:120-127
  - tests/integration/melder/crystallizer/test_spell_crystal_integration.py:202-204
  IMPACT: The class can currently construct but still has an internal naming
    mismatch on its identity path, so the identity rename should be finished
    before more module-version work builds on top of it.
  NEXT: patch `SpellCrystal` to use `_id` consistently and run the focused
    unit/component/integration SpellCrystal rings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-09T16:24:31Z
  TYPE: MEASURE
  CLAIM: The narrow `SpellCrystal` identity fix is now landed and green. The
    class already constructed its identity as `_id = spell.spell_id`; the
    remaining bug was `describe()` still emitting the old `_spell_id` field
    name. `describe()` now uses `_id` consistently and exposes `id`,
    `spell_id`, and `spell_crystal_id` from that same identity value, and the
    focused compile plus unit/component/integration SpellCrystal rings all
    passed.
  EVIDENCE:
  - src/melder/crystallizer/spell_crystal.py:135-137
  - src/melder/crystallizer/spell_crystal.py:1387-1389
  - tests/integration/melder/crystallizer/test_spell_crystal_integration.py:202-205
  - validation_result:
    `<local-workspace>\\.venv_new\\Scripts\\python.exe -m py_compile src\\melder\\crystallizer\\spell_crystal.py tests\\integration\\melder\\crystallizer\\test_spell_crystal_integration.py`
  - validation_result:
    `<local-workspace>\\.venv_new\\Scripts\\python.exe -m pytest -q -p no:cacheprovider tests\\unit\\melder\\crystallizer\\test_spell_crystal.py` -> `92 passed`
  - validation_result:
    `<local-workspace>\\.venv_new\\Scripts\\python.exe -m pytest -q -p no:cacheprovider tests\\component\\melder\\crystallizer\\test_spell_crystal_component.py` -> `40 passed`
  - validation_result:
    `<local-workspace>\\.venv_new\\Scripts\\python.exe -m pytest -q -p no:cacheprovider tests\\integration\\melder\\crystallizer\\test_spell_crystal_integration.py` -> `80 passed`
  IMPACT: The class now has one coherent crystal/spell identity path again, so
    later module-version work will not be building on a partially renamed
    internal id seam.
  NEXT: return to the module-version / synthetic-module design problem instead
    of spending more time on the narrow crystal identity cleanup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-09T16:36:24Z
  TYPE: FACT
  CLAIM: The compatibility aliases are now gone too. `SpellCrystal.describe()`
    no longer fakes `spell_id` or `spell_crystal_id` keys from the same value;
    it exposes only `id` for the crystal identity surface. The focused
    integration assertion was tightened accordingly, and the full
    unit/component/integration SpellCrystal rings stayed green.
  EVIDENCE:
  - src/melder/crystallizer/spell_crystal.py:1387-1388
  - tests/integration/melder/crystallizer/test_spell_crystal_integration.py:120-127
  - tests/integration/melder/crystallizer/test_spell_crystal_integration.py:202-204
  - validation_result:
    `<local-workspace>\\.venv_new\\Scripts\\python.exe -m pytest -q -p no:cacheprovider tests\\unit\\melder\\crystallizer\\test_spell_crystal.py` -> `92 passed`
  - validation_result:
    `<local-workspace>\\.venv_new\\Scripts\\python.exe -m pytest -q -p no:cacheprovider tests\\component\\melder\\crystallizer\\test_spell_crystal_component.py` -> `40 passed`
  - validation_result:
    `<local-workspace>\\.venv_new\\Scripts\\python.exe -m pytest -q -p no:cacheprovider tests\\integration\\melder\\crystallizer\\test_spell_crystal_integration.py` -> `80 passed`
  IMPACT: The crystal identity surface is now honest and singular, which makes
    later module-version and module-lineage work less confusing.
  NEXT: return to the unresolved module-version / synthetic-module integrity
    model instead of spending more time on the crystal id naming seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the first real object definitions in the crystallizer package.
