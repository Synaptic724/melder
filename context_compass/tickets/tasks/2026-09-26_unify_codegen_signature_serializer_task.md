# Task: Unify the codegen signature serializer into one leaf implementation with a determinism test

## Metadata
- Task ID: TASK-2026-09-26-unify-codegen-signature-serializer
- Story: STORY-2026-09-26-signature-determinism-phase8-digest
- Status: review
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T09:05:00Z
- Updated: 2026-09-26T10:42:09Z

## Objective
One implementation of `serialize_codegen_signature_part`, `hash_codegen_signature` and
`freeze_phase11_schema_value` in a new leaf module, with `SharedCompilerExecutions` and
`CodegenCreationSchemaHelpers` delegating to it; canonical freezing of classes, functions and enum members
and an explicit marker for other non-primitive objects; canonical handling of raw sets; a two-process
determinism test plus a byte-compatibility corpus test on the gauntlet book (C-H, the epic's I-0).

## Ticket Contract
- ENTRY_GATE: Patch docs exist and are linked (task 1 in review); the owner confirmed the Propose ->
  Confirm message naming the exact files and symbols; active board row routes here.
- EXECUTION_BOUNDARY: new `src/melder/aether/spellbook/spell_compiler/shared_assets/codegen_signature.py`
  (leaf; imports nothing from `melder.aether`), `phases/shared_compiler_executions.py` (the three
  helpers delegate; nothing else), `codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py`
  (the three helpers delegate; nothing else), tests under `tests/unit/melder/spellbook/spell_crafter/`
  and `tests/component/melder/spellbook/`. No other file.
- DEPENDENCIES: task 1 patch docs; melder_0's hunks on `shared_compiler_executions.py` landed (verify
  with `git diff -w` before the edit); the freeze rule decided in the component patch.
- EXIT_GATE: single implementation; both facades delegate; unit tests for tags, canonical freeze,
  set handling and delegation; determinism test and corpus test written; "Not run." until the owner
  reports; status review.
- FAILURE_ESCALATION: RISK if the corpus test shows any previously deterministic signature changing
  bytes (then a generation bump is needed and must be coordinated with melder_0's generation 11);
  CONFLICT on concurrent edits.

## Scope Boundaries
- In scope: the three helpers, their facades, the leaf module, tests.
- Out of scope: step-row builders, transient schema, manifests, emitters, `caching_system.py`.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Created with the story; moves to in_progress after task 1 is in review and the
  owner confirms the file/symbol proposal.
- from_state: ready
- to_state: in_progress
- transition_reason: Owner confirmed the proposal ("go ahead and start doing shit", 2026-09-26); U1 done.
- from_state: in_progress
- to_state: review
- transition_reason: U1-U4 complete on the task boundary (leaf, delegations, oracle, 11 unit + 4 component
  tests, patch docs amended, docstring ritual done); nothing executed here ("Not run."); one owner ruling
  (cache-path payloads) is open and recorded as a RISK note, outside this task's boundary.

## Steps / Checklist
- [x] U1: Propose -> Confirm (files/symbols, the freeze rule, the set rule) and owner confirmation.
- [x] U2: create the leaf module (docstrings per `docstrings.md`; no module-level constants; typing per
      `typing.md`); make both facades delegate; keep public names and signatures.
- [x] U3: tests - unit (tags, freeze cases, set handling, delegation identity) and component (two
      subprocesses with different `PYTHONHASHSEED` on the gauntlet book; corpus byte-compatibility
      against signatures captured before the change).
- [x] U4: docstring ritual on touched code; notes; task -> review with "Not run." and the exact
      commands for the owner.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The leaf module; two facades delegating; tests; a corpus fixture under
  `artifacts/codegen_signature_determinism_20260926/` (captured signatures before the change).

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/shared_assets/codegen_signature.py (new)
- src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py
- tests/mocks/spellbook/codegen_signature_reference.py (new; frozen pre-change bodies)
- tests/unit/melder/spellbook/spell_compiler/shared_assets/test_codegen_signature.py (new)
- tests/component/melder/spellbook/test_codegen_signature_determinism.py (new)

## Validation
- Not run. (VM interpreter is 3.10 against a 3.14 floor; no sandbox copy of the repository.)
- Recommended commands (owner-run, 3.14t):
  - `python -m pytest -q tests/unit/melder/spellbook/spell_compiler/shared_assets/test_codegen_signature.py`
  - `python -m pytest -q tests/component/melder/spellbook/test_codegen_signature_determinism.py`
  - `python -m pytest -q tests/unit/melder/spellbook/spell_compiler tests/component/melder/spellbook tests/integration/melder/conduit/test_conduit_integration_links_contracts.py`
  - `python benchmarks/testing_other_di/profile_bind_conjure_cycle.py` (cache hit rate across processes)

## Risks / Rollback Notes
- Rollback: delete the leaf module and restore the two facade bodies (pure functions; no state).
- The `shared_assets/` package under `spell_compiler/` may not exist yet: creating it needs an empty
  `__init__.py` only if package discovery requires it (`__init__.py` policy).

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [x] No edit under `src/` before the owner confirms the file/symbol proposal.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed) - patch docs amended; canonical map promotion at story closure
- [x] Validation status recorded ("Not run.")
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/codegen_signature_determinism_2026_09_26/
  - artifacts/codegen_signature_determinism_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Story closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: serializer; freeze; determinism test; byte-compatibility corpus.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T09:05:00Z
  TYPE: PLAN
  CLAIM: Sequence U1-U4; the corpus fixture is captured BEFORE any edit so byte-compatibility is proved
    against the shipped behaviour, not against the new code's own output.
  EVIDENCE:
  - tickets/tasks/2026-09-26_author_signature_patch_docs_task.md
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:58-137
  IMPACT: Prevents a silent stale-cache hit on the full-hit path, where no fresh signature is computed.
  NEXT: Wait for task 1 review and the owner's confirmation of U1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T09:29:36Z
  TYPE: DECISION
  CLAIM: U1 confirmed by the owner. Design fixed for U2: (1) new leaf `spell_compiler/shared_assets/
    codegen_signature.py` holding class `CodegenSignature` (slot-only staticmethods, stdlib imports only;
    the package tree uses namespace packages, no `__init__.py` needed). (2) Byte-compatibility rule
    refined from the patch draft: freeze canonicalizes ONLY values whose old `repr` carried an address
    (functions, methods, builtin callables -> ("__callable__", module, qualname); instances whose type
    uses `object.__repr__` -> ("__object__", module, qualname)); classes, enums, dataclasses and every
    other deterministic `repr` keep their bytes. Top-level `set`/`frozenset` parts are frozen (sorted)
    before pickling; `frozenset` joins the sorted freeze branch (it fell to `repr` before). Nested
    containers are NOT walked, because rebuilding containers changes pickle memo bytes for previously
    deterministic inputs; the existing contract (callers pre-freeze) stands. (3) Both facades keep
    their staticmethods and docstrings and delegate; unused `hashlib`/`pickle` imports are dropped.
    (4) Files on disk are CRLF; edits preserve CRLF. (5) The new class is absent from the bind-guard
    manifest until the owner regenerates build assets (registration only; no runtime effect).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:58-137
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:397-424
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:23-158
  - tests/component/melder/spellbook/spell_compiler_runtime_test_support.py:23-93
  IMPACT: The change is provably byte-compatible for every deterministic input, so no cache generation
    bump; the patch docs' Interface delta 2 is amended to this rule in the same pass.
  NEXT: U2: write the leaf module and the two facade delegations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T09:44:27Z
  TYPE: FACT
  CLAIM: Mailbox M0-17 (melder_0) consumed: build assets were rebuilt at 09:36Z for the conjure
    validation_warnings change, and the bind-guard manifest now lists the in-flight leaf class
    `CodegenSignature` (manifest :296, BUILT_FOR_VERSION 0.2.54). This closes item (5) of the 09:29:36Z
    DECISION note: this lane owes no separate regeneration unless the class moves or is removed, in
    which case `python src/melder/_build_assets/_build_asset_runner.py` is rerun here.
  EVIDENCE:
  - src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py:296-296
  - tickets/tasks/2026-09-26_add_conjure_validation_warnings_flag_task.md
  IMPACT: The registration guard already refuses binding the new class; no asset-side follow-up is
    pending in this lane for task 2.
  NEXT: Record U2/U3 progress (leaf, delegations, oracle, unit tests on disk), then write the component
    determinism test.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T09:58:49Z
  TYPE: FACT
  CLAIM: U2 and U3 are on disk and the owner's commit 6fc9af345 already carries them. Leaf
    `shared_assets/codegen_signature.py` (291 lines): class `CodegenSignature` :7-64, serializer
    :66-123 (typed tags; top-level set/frozenset frozen first; dict/tuple/list pickled as given),
    `_pickle_or_repr` :124-147, hash :148-180, freeze :181-264 (callables -> `("__callable__",
    module, qualname)`; default-`object.__repr__` instances -> `("__object__", module, qualname)`;
    everything else keeps its `repr` bytes), `_freeze_callable` :265-291. Both facades delegate
    (`shared_compiler_executions.py` :84, :106, :370; `codegen_creation_schema_helpers.py` :51,
    :71, :96) with `hashlib`/`pickle` imports dropped. Byte-compat oracle: verbatim pre-change
    bodies in `tests/mocks/spellbook/codegen_signature_reference.py` :22-122. Unit tests (11) in
    `tests/unit/melder/spellbook/spell_compiler/shared_assets/test_codegen_signature.py` :84-240.
    Component tests (4) in `tests/component/melder/spellbook/test_codegen_signature_determinism.py`:
    two-process equality for a plain book and for a contract-payload book (the object payload is
    the proof case), the live-parts corpus check (both facades' `hash_codegen_signature` recorded
    and compared with the reference digest), and in-process stability. Test dirs mirror the src
    layout (`spell_compiler/`), not the ticket's `spell_crafter/` wording.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/shared_assets/codegen_signature.py:7-291
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:58-107
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:344-370
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:1-96
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/manifest/generalized_manifest.py:185-215
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:160-215
  - tests/integration/melder/conduit/test_conduit_integration_links_contracts.py:596-673
  - tests/component/melder/spellbook/test_ordered_disposal_binding.py:341-364
  - tests/component/melder/spellbook/test_codegen_signature_determinism.py:1-440
  IMPACT: Rollback is now `git revert` of the leaf plus the two facade hunks, not a working-tree
    discard. The contract-payload fixture needs a contracted provider (payloads compile only from
    `_lookup_contracted_spells`), so it uses the public two-book link recipe from the integration
    suite with the system cache disabled; a local `SpellContract` default alone never reaches the
    signature row. Nothing was executed: the VM has Python 3.10 and the harness refused a sandbox
    copy of the repository, so every validation line stays "Not run.".
  NEXT: Amend both patch docs to the implemented freeze rule, run the docstring ritual over the two
    facades, then move this task to review with the exact owner-run commands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T10:01:13Z
  TYPE: RISK
  CLAIM: The patch's open UNKNOWN is resolved, and it matters: frozen payload values are not only
    hashed, they are EXECUTED on the cache path. `build_phase11_step_ir_row` stores each contract
    payload value through `freeze_phase11_schema_value` (:333-341); the cache-load path hydrates
    steps from those rows (`spell_codegen_creation_cache.py` :320-329 ->
    `_hydrate_steps_from_rows` :373-380) and the manifest compiler binds `row["contract_payload_items"]`
    values as the constructor keyword values (:824-830, :966). The hot in-process path compiles from
    the live plan (`compile_no_overrides_codegen_creation_executor_from_plan` :122-178) with the raw
    values, so the two paths disagree for every non-primitive payload value: before this task an
    object payload reached the constructor as its `repr` string after a cache hit (and its signature
    was process-local); after it, as the `("__object__", module, qualname)` tuple - deterministic,
    still not the object. Pre-existing and unchanged by this task: dict values thaw as sorted pair
    tuples, list values as tuples, enum members as `repr` strings, on the cache path only.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:296-341
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py:316-340
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:58-178
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:309-395
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:796-830
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:950-967
  IMPACT: The determinism change is correct and byte-compatible, but the marker must not be described
    as "safe": a cached executor for a book with a non-value payload constructs with the wrong value
    on the next process. Out of this task's boundary (row builders, manifests, cache emission are
    excluded), so it is a DECISION_REQUEST, not a fix: (A) keep the marker and document the cache-path
    limit; (B) refuse cache EMISSION for spells whose rows carry a non-value payload (row builder
    flags it; `build_package`/`build_manifest_package` skip) - in-process recompile stays correct,
    cross-process hits are lost only for those spells; (C) raise at plan time for non-value payloads.
    The pre-existing container/enum thaw is a separate defect on the same seam (same fix family).
  NEXT: Put the decision to the owner with (B) recommended; task 2 still goes to review on its own
    boundary, and the patch docs state the limit explicitly until the ruling lands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T10:03:08Z
  TYPE: FACT
  CLAIM: U4 done. Both facades' docstrings already state the delegation and the implemented freeze
    rule; the leaf's `freeze_phase11_schema_value` docstring now records the cache-path limit (frozen
    payload values are executed after a cache hit), which moves the leaf to 300 lines (freeze
    :181-273, `_freeze_callable` :274-300). Patch docs amended (Interface delta 2 to the implemented
    rule, delta 2a for the limit; component "After (freeze)", validation items, decision request);
    measurement plan B3/M1/M2 updated to the oracle and the two fixtures. Task -> review; "Not run.".
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/shared_assets/codegen_signature.py:181-300
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:60-107
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:8-96
  - system_docs/patches/active/codegen_signature_determinism_2026_09_26/architecture_patch.md:34-58
  - system_docs/patches/active/codegen_signature_determinism_2026_09_26/component_patch_spell_compiler.md:34-49
  - artifacts/codegen_signature_determinism_20260926/measurement_plan.md:29-50
  IMPACT: Task 2 is reviewable on its own boundary; the owner's ruling on the cache-path payload
    limit decides whether a follow-up task opens under the story.
  NEXT: Owner runs the four commands under Validation and rules on the RISK note's (A)/(B)/(C); fable_0
    proceeds to task 3 H1 in the meantime.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T10:12:00Z
  TYPE: DECISION
  CLAIM: Owner ruling on the cache-path payload limit: option B ("do the recommended send it"). A new task
    under the story refuses creation-cache emission for spells whose persisted rows would not replay
    their contract payload faithfully; task 2 itself stays in review unchanged.
  EVIDENCE:
  - tickets/tasks/2026-09-26_unify_codegen_signature_serializer_task.md
  - tickets/stories/2026-09-26_signature_determinism_and_phase8_digest_story.md
  IMPACT: The marker tuple never reaches a constructor through the cache once task 4 lands; the
    determinism change needs no further amendment.
  NEXT: Open task 4 (cache-faithful payload gate) after task 3's implementation; owner runs the suites.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T10:42:09Z
  TYPE: MEASURE
  CLAIM: Owner-run (3.14.7t, `.venv_new`): `python -m pytest -q tests/unit/melder/spellbook/spell_compiler
    tests/component/melder/spellbook tests/integration/melder/conduit/test_conduit_integration_links_contracts.py
    tests/component/melder/aether/conduit` -> 1784 passed, 1 skipped, 3 failed in 13.71s. All three failures
    are in the new `test_codegen_signature_determinism.py`: (1) the plain cross-process test asserted a
    64-char string signature, but the solo family publishes a shape tuple (`('solo','unique',0,0,0)`) as
    `_no_overrides_executor_signature`; assertion relaxed to presence plus cross-process equality. (2/3)
    the object-payload fixture asserted the constructor received the `PayloadMarker`; it did not. The
    string-payload sibling passed, so the payload reaches the plan and the row - the generalized family
    hydrates its executors from the manifest rows IN-PROCESS (lazy doors, first meld), so the constructor
    binds the frozen projection (`("__object__", ...)`; before task 2 the `repr` string). Fixture now
    proves the payload reached the plan (`_plan_contract_payload_value`) and documents why the instance
    is not asserted. The unit file (11 tests) and the corpus/stability tests passed.
  EVIDENCE:
  - tests/component/melder/spellbook/test_codegen_signature_determinism.py:271-365
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_lazy_door_step.py:15-130
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:974-1037
  IMPACT: Task 2's determinism claim stands (signatures equal across processes for both fixtures once
    the fixture reads the plan); the RISK note of 10:01:13Z understated the seam: manifest-first
    families project non-value payloads in-process too, not only on the cache path.
  NEXT: Owner re-runs `python -m pytest -q tests/component/melder/spellbook/test_codegen_signature_determinism.py`;
    the in-process projection goes to the owner as a decision (task 4 note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
STATE 2026-09-26T09:05:00Z: ready; opens after task 1 (patch docs) is in review and U1 is confirmed.
STATE 2026-09-26T09:29:36Z: U1 confirmed; U2 in progress (leaf module + facade delegations).
STATE 2026-09-26T09:58:49Z: U2, U3 done and committed (6fc9af345); U4 next: patch-doc amendment, docstring
ritual, task -> review.
STATE 2026-09-26T10:03:08Z: REVIEW. Owner-run suites pending; owner ruling pending on the cache-path payload
limit (RISK note 10:01:13Z). Successor: task 3 H1.
STATE 2026-09-26T10:42:09Z: REVIEW. Suites owner-run: 1784 passed; 3 fixture/assertion failures in the new component
file fixed (not re-run). In-process projection finding handed to task 4 / owner.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
