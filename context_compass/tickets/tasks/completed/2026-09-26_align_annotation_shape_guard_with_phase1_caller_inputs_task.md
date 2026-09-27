

# Task: Stop the Phase-4 annotation-shape guard from breaking caller-supplied container parameters

- Completed: 2026-09-26T14:47:09Z
- Summary: Dict, set and tuple constructor parameters (and typing.Any) no longer break conjure: the guard's
  container branch is removed, Any matches Phase 1, and REQUIRED_HOLE carries the list-only hint. Committed by
  the owner in a67cd3b49; docs and graph current. Turned in by the owner; assets and installs are the owner's.

## Metadata
- Task ID: TASK-2026-09-26-align-annotation-shape-guard-with-phase1-caller-inputs
- Story: none (owner-relayed defect from the CommandOps lane)
- Status: done
- Owner: user
- Agent Name: melder_1
- Priority: p1
- Created: 2026-09-26T11:56:47Z
- Updated: 2026-09-26T14:47:09Z

## Objective
Owner relayed a CommandOps agent's report (2026-09-26): Phase 1 classifies some dict/set/tuple constructor
parameters as caller-supplied (PLAIN, reported as REQUIRED_HOLE warnings), but the Phase-4
AnnotationShapeGuardStrategy errors on any dict/set/tuple parameter whose inner types look injectable,
ignoring Phase 1's verdict, and treats typing.Any as injectable (Any is a class since 3.11) where Phase 1
excludes it. The error marks spells broken (Operations, CodecPacket, ClassProfile in CommandOps
AgentsBootstrap), failing conjure. Verify every claim from source, reproduce minimally, propose a fix.

## Ticket Contract
- ENTRY_GATE: Owner direction 2026-09-26 ("We got a problem you can handle here") with the relayed report.
- EXECUTION_BOUNDARY: Investigation reads src/ and runs probes on VM copies. src edits after owner
  confirmation of a DECISION_REQUEST (the report suggests warning-vs-skip; owner picks).
- DEPENDENCIES: Phase 1 ParameterDIShape classification, Phase-4 validation strategies.
- EXIT_GATE: Claims verified or refuted with evidence; fix approved, implemented with regression tests;
  suites green; docs/graph updated.
- FAILURE_ESCALATION: CONFLICT if Phase 1 and Phase 4 intents cannot be reconciled; DECISION_REQUEST for
  the severity choice.

## Scope Boundaries
- In scope: AnnotationShapeGuardStrategy and its agreement with Phase 1 (PLAIN parameters, typing.Any).
- Out of scope: CommandOps code; whether plain data classes should be spells (design question under their
  epic); the paused class-annotation lane.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner redirected to this defect (2026-09-26T11:56:47Z).
- from_state: in_progress
- to_state: blocked
- transition_reason: Claims verified and reproduced; DECISION_REQUEST A/B open (2026-09-26T12:04:39Z).
- from_state: blocked
- to_state: in_progress
- transition_reason: Owner decided the four-part change (2026-09-26T12:09:47Z).
- from_state: in_progress
- to_state: review
- transition_reason: Fix on the device tree; VM-copy suites green; docs, patch docs and graph current (2026-09-26T12:23:14Z).
- from_state: review
- to_state: done
- transition_reason: Owner turned in melder_1's tickets (2026-09-26T14:47:09Z); the fix is in HEAD (a67cd3b49).

## Steps / Checklist
- [x] Read AnnotationShapeGuardStrategy and the Phase 1 classification it should agree with.
- [x] Reproduce minimally (dict/set/tuple of injectable types, dict[str, Any]) before and after.
- [x] DECISION_REQUEST (warning for PLAIN vs skip; Any exclusion).
- [x] Implement with regression tests after approval; validate; docs and graph.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Evidence under artifacts/annotation_shape_guard_20260926/; a fix proposal; after approval the fix, tests, docs.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/validation/strategies/annotation_shape_guard_strategy.py
- src/melder/aether/spellbook/spell_compiler/validation/strategies/required_holes_strategy.py
- tests: guard unit tests, component validation strategies, three integration files (see DECISION)

## Validation
- Agent runs (VM copy synced from the device tree, 3.14.7t, -X gil=0): unit 8595 passed; component 2109
  passed; integration 1926 passed. The 9 new/changed tests fail on the original source.
- Owner machine: Not run.
- Known pre-existing flake: tests/integration/melder/conduit/test_conduit_integration_concurrency.py (RISK note).

## Risks / Rollback Notes
- Weakening a validation guard can let a real mis-declared injection through; the fix must keep the hint.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS` (the relayed report is UNKNOWN until verified).
- [ ] No behavior claim cited only to a document or a one-line search hit.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/annotation_shape_guard_20260926/
  - system_docs/patches/completed/caller_supplied_container_params_2026_09_26/ (archived at closure)
- DISPOSITION: retain_as_reference (evidence); promote_to_documentation (patch lane)
- CLEANUP_TRIGGER: ticket closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Phase 1 vs Phase 4 agreement on caller-supplied container parameters.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.

## Notes
- DATETIME: 2026-09-26T11:57:39Z
  TYPE: FACT
  CLAIM: Relayed report verified from source (not yet run). AnnotationShapeGuardStrategy.validate skips only
    SPELLMAP_DEFAULT and SPELL_CONTRACT parameters; for any other parameter whose origin is set, frozenset,
    dict or tuple it emits UNSUPPORTED_COLLECTION_SHAPE with severity "error" when an argument "looks like a DI
    target", and its _looks_like_di_target returns True for every non-builtins class, so typing.Any (a class
    since 3.11, module "typing") counts. Phase 1 (SpellRequirementsFinder._classify_parameter) never makes such
    a parameter DI: defaults make it PLAIN, and without a default only list[T] (COLLECTION_BY_ANNOTATION) or a
    class-like base annotation (SINGLE_BY_ANNOTATION) is DI, so dict/set/tuple fall to PLAIN; Phase 1's
    _looks_like_di_target returns False for typing.Any explicitly. RequiredHolesStrategy reports the same
    default-less PLAIN parameters as REQUIRED_HOLE warnings (caller must supply). So the guard's error branch
    can only fire on a parameter Phase 1 has already made a caller input - Phase 4 contradicts Phase 1.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/annotation_shape_guard_strategy.py:73-128
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/annotation_shape_guard_strategy.py:186-226
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:1100-1210
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/required_holes_strategy.py:70-115
  IMPACT: Any resolvable spell with a dict/set/tuple parameter of user classes or Any is broken at Phase 4
    (pending measurement: conjure refusal), although Melder would never inject that parameter anyway.
  NEXT: Reproduce minimally (dict/set/tuple of a user class, dict[str, Any], with/without default) and check
    whether an error-severity issue refuses conjure; then measure the warning variant in a VM copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T12:04:31Z
  TYPE: MEASURE
  CLAIM: Reproduced (VM copy of the device tree, 3.14.7t, one fresh process per case). Conjure raises
    SpellbookValidationError for dict[str, Operation], dict[str, Any], set[Operation], tuple[Operation, ...]
    and even dict[str, Operation] with an ordinary default; the conjure report lists REQUIRED_HOLE (warning)
    and UNSUPPORTED_COLLECTION_SHAPE (error) on the same parameter. Control dict[str, int] conjures and
    melds. Prototype (PLAIN -> severity "warning"; typing.Any is not a DI target, matching Phase 1): all six
    cases conjure and the override-supplied container reaches the constructor by identity. Suites with the
    prototype: unit 8594 passed; component 1 failed (test pins severity "error"); integration 3 failed = the
    test that asserts set[IPlugin] "must block conjure" plus 2 concurrency tests.
  EVIDENCE:
  - context_compass/artifacts/annotation_shape_guard_20260926/results/container_guard_before_after.txt:1-21
  - context_compass/artifacts/annotation_shape_guard_20260926/probes/probe_container_params.py:1-95
  - tests/component/melder/spellbook/spell_crafter/validation/test_spellbook_component_validation_strategies.py:138-200
  - tests/integration/melder/spellbook/test_spellbook_integration_resolution_error_matrix.py:384-392
  IMPACT: The fix works; two tests encode the old intent ("unsupported collection DI blocks conjure") and
    change with it, which makes this a behaviour decision for the owner.
  NEXT: Record the concurrency RISK, then the DECISION_REQUEST.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T12:04:31Z
  TYPE: RISK
  CLAIM: Pre-existing and out of scope: tests/integration/melder/conduit/test_conduit_integration_concurrency.py
    fails intermittently on the UNMODIFIED source in this VM copy - 5 of 6 file runs failed 3-5 tests each
    (many_across_borrowers, unique_across_multiple_borrowers, shared_unique_contract, cluster_unique), all with
    RuntimeError "Cannot build CreationContext before spell_codegen_creation exists". Earlier lanes saw only the
    cluster test fail occasionally; the same race now reaches more tests of the file (2-core VM).
  EVIDENCE:
  - context_compass/artifacts/annotation_shape_guard_20260926/results/container_guard_before_after.txt:18-21
  IMPACT: Owner-machine integration runs may fail in this file independent of any lane; a real concurrent
    first-meld race likely exists. Needs its own lane.
  NEXT: Report to the owner as a separate follow-up.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T12:04:31Z
  TYPE: DECISION_REQUEST
  CLAIM: Fix options for AnnotationShapeGuardStrategy (file only; Phase 1 unchanged). A (recommended, and the
    relaying agent's recommendation): UNSUPPORTED_COLLECTION_SHAPE becomes a warning for PLAIN parameters
    (every dict/set/tuple parameter today, since Phase 1 never injects them) and stays an error for any other
    shape; _looks_like_di_target returns False for typing.Any like Phase 1 (list[Any] then gets the existing
    LIST_ELEMENT_NOT_DI_TARGET warning). Keeps the "only list[T] is collection DI" hint visible; conjure
    proceeds; the caller supplies the value (a missing value fails as a normal missing argument). B: skip PLAIN
    containers entirely (no issue) plus the Any change; loses the hint. Either way the two tests that pin the
    old intent change to assert the warning / a successful conjure, the message is reworded for the warning
    case, and a regression covers dict[str, Any] and a supplied container. No cache or fingerprint impact.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/annotation_shape_guard_strategy.py:110-128
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:1197-1227
  IMPACT: Implementation waits for the owner's choice.
  NEXT: Ask the owner A or B.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T12:09:47Z
  TYPE: DECISION
  CLAIM: Owner decision after discussion (supersedes options A/B): (1) remove the guard's dict/set/tuple
    UNSUPPORTED_COLLECTION_SHAPE branch - Phase 1 is the single decider of injection and never injects those
    shapes; (2) typing.Any is not a DI target in the guard's list checks, matching Phase 1; (3) the container
    hint moves into the REQUIRED_HOLE message ("Melder injects collections only as list[T]"); (4) tests that
    assert the old behaviour change to assert a successful conjure and the hint. Owner on the CommandOps data
    classes: registering them and supplying fields through override is reasonable (no Melder change). Test
    inventory for (4), wider than the two first named because removing the branch retires its unit tests and
    helper: unit guard tests (flags_unsupported_collection, collection_args helper, looks_like heuristics),
    component guard test, integration di_validation_faults control, resolution_error_matrix conjure test,
    di_shape_compiler_matrix set/dict tests.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/annotation_shape_guard_strategy.py:110-128
  - tests/integration/melder/spellbook/test_spellbook_integration_di_shape_compiler_matrix.py:600-622
  IMPACT: Scope approved; patch framework applies (validation gate behaviour; src_components entry).
  NEXT: Author the patch lane, then implement in the VM copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T12:15:01Z
  TYPE: PLAN
  CLAIM: Patch lane caller_supplied_container_params_2026_09_26 authored and linked (architecture + validation
    component patch; no code description needed: no control-flow or concurrency change). Mapping (patch ->
    implementation -> validation): guard contract -> remove the set/frozenset/dict/tuple branch and the
    _collection_args_have_di_targets helper, Any excluded in _looks_like_di_target, docstrings/AGENT_PURPOSE/
    description updated -> unit: containers emit nothing, list[Any] warns. REQUIRED_HOLE hint ->
    RequiredHolesStrategy._container_hint appended for set/frozenset/dict/tuple origins -> unit: hint for the four
    containers, none for int. Behaviour -> component guard test, fault-B control, compiler-matrix set/dict tests
    and resolution-matrix conjure test flip to "conjure succeeds / REQUIRED_HOLE"; new integration regressions:
    set[IPlugin] and dict[str, Any] conjure and meld the supplied value by identity. Implementation in the VM copy
    by one script (artifacts/annotation_shape_guard_20260926/apply_fix.py), device patched only after it is green.
  EVIDENCE:
  - system_docs/patches/active/caller_supplied_container_params_2026_09_26/architecture_patch.md:1-67
  - system_docs/patches/active/caller_supplied_container_params_2026_09_26/component_patch_spell_compiler_validation.md:1-49
  IMPACT: Patch-framework entry gate satisfied.
  NEXT: Write apply_fix.py, run it on the VM copy, run the affected tests then the suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T12:20:24Z
  TYPE: MEASURE
  CLAIM: Implemented in the VM copy by apply_fix.py (guard: container branch and _collection_args_have_di_targets
    removed, unused Tuple import dropped, Any excluded, docstrings/AGENT_PURPOSE/description updated;
    RequiredHolesStrategy: _container_hint appended to REQUIRED_HOLE for set/frozenset/dict/tuple origins) and
    apply_tests.py (9 new or changed tests; the removed helper's unit test deleted). The 9 tests fail on the
    original source and pass with the fix. All six probe shapes conjure and meld the supplied value by identity.
    Suites on the VM copy (3.14.7t, -X gil=0): unit 8595 passed; component 2109 passed; integration 1926
    passed, 3 skipped, 7 xfailed, 1 xpassed (existing non-strict Fault-B xfail); the concurrency file passed in
    this run. All 8 device target files equal HEAD (no concurrent edits).
  EVIDENCE:
  - context_compass/artifacts/annotation_shape_guard_20260926/results/container_guard_before_after.txt:1-30
  - context_compass/artifacts/annotation_shape_guard_20260926/apply_fix.py:1-184
  - context_compass/artifacts/annotation_shape_guard_20260926/apply_tests.py:1-302
  IMPACT: Ready to patch the device tree with the same scripts.
  NEXT: Apply both scripts to the device tree and hash-compare with the VM copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T12:20:36Z
  TYPE: FACT
  CLAIM: Device tree patched in place with the same two scripts (CRLF kept): 2 src files and 6 test files, all
    8 hash-equal to the validated VM copy (commit_manifest.txt).
  EVIDENCE:
  - context_compass/artifacts/annotation_shape_guard_20260926/results/commit_manifest.txt:1-8
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/annotation_shape_guard_strategy.py:22-60
  IMPACT: Code done; docs, graph and release note remain (assets deferred to the owner).
  NEXT: Promote to src_components/src_architecture, update the release note, refresh the two graph descriptors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T12:21:43Z
  TYPE: FACT
  CLAIM: Docs promoted. src_components: "Caller-supplied container parameters" block in the SpellCompiler and
    Validation Pipeline entry, a failure-mode bullet, the guard's Key Files description, a Spell Validation
    Strategies contract line and a handoff entry. src_architecture: Operational Invariant "Phase 1 decides
    injection" plus a handoff entry. Both indexes regenerated, --check OK (9363 and 2835 lines). Release note:
    section "Dict, set and tuple constructor parameters no longer break conjure" before the spell-id section,
    packaging bullet extended (no line over 110). tests_components unchanged (same test files, names only).
  EVIDENCE:
  - system_docs/src_components.md:3143-3153
  - system_docs/src_architecture.md:849-854
  - release_docs/next_version_release.md:92-117
  IMPACT: Documentation current apart from the graph descriptors.
  NEXT: Refresh the two strategy descriptors in a scratch graph copy, accept sole-delta nodes, assemble.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T12:23:14Z
  TYPE: MEASURE
  CLAIM: Graph refreshed for the two strategy files only (3.14.7t --strict extraction into a scratch copy, no
    skips). The old descriptors' source_sha256 equal the pre-fix file hashes, so the source delta is this lane's.
    Both class nodes were already SEMANTICS_STALE before this lane (stamps older than their previous spans);
    both classes were read in full, their prose rewritten/extended to the current source (guard: list-element
    and forward-ref warnings only, containers left to RequiredHolesStrategy, Any not a DI target; holes: the
    list-only collection hint) and accepted, with the guard module node. Only the two descriptors were copied
    back; assemble --check: 597 sections, all ranges verified, 28124 lines. Packaged assets and LLM bundles
    NOT rebuilt (owner deferred); the agent-documentation manifest carries the old AGENT_PURPOSE text until then.
  EVIDENCE:
  - system_docs/src_graph.md:15145-15191
  - system_docs/src_graph.md:15553-15599
  IMPACT: Exit gate met apart from owner review and the deferred asset rebuild.
  NEXT: Move the task to review and report to the owner.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T12:23:30Z
  TYPE: FACT
  CLAIM: Consumed melder_0 M0-23 (re M1-12): melder_0 takes creation-cache generation 13
    "collection_member_paths" in caching_system.py and adds 13 to test_cache_schema_version_integration.py by
    anchored edits, leaving melder_1's generation-12 entry intact; override S2/S3 move to 14. No overlap with
    this lane's files (two Phase-4 strategies and their tests). Both caching_system.py and the history test are
    also in the closed function_spell_ids commit list, so an uncommitted working tree will carry both lanes'
    entries - expected.
  EVIDENCE:
  - tickets/tasks/2026-09-26_fix_collection_member_many_sharing_task.md:1-20
  - artifacts/function_spell_ids_20260926/results/commit_files.txt:1-46
  IMPACT: None for this lane; relevant to how the owner groups commits.
  NEXT: Report to the owner.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7
- DATETIME: 2026-09-26T14:47:09Z
  TYPE: DECISION
  CLAIM: Owner turned in melder_1's tickets ("turn in your tickets"). The fix is committed: HEAD a67cd3b49
    (2026-09-26T12:24:16Z) carries the guard without the container branch and with typing.Any excluded; the worktree
    equals HEAD for both strategy files apart from line endings. The CommandOps failure the owner pasted at the same
    time (CodecPacket, ClassProfile broken by UNSUPPORTED_COLLECTION_SHAPE) comes from an installed melder 0.2.54:
    every Melder frame in that trace matches dist/melder-0.2.54-py3-none-any.whl line for line and that wheel still
    has the removed branch. Closure: moved to tasks/completed/, patch lane archived, artifacts retained.
  EVIDENCE:
  - context_compass/artifacts/annotation_shape_guard_20260926/results/owner_trace_vs_wheel.txt:1-14
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/annotation_shape_guard_strategy.py:178-191
  IMPACT: CommandOps needs a melder build from current source; no further Melder change for this defect.
  NEXT: none (the owner's review of Phase-4 error reporting is a new lane).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
DONE 2026-09-26T14:47:09Z: turned in by the owner; patch lane archived; artifacts retained.
IN REVIEW 2026-09-26T12:23:14Z: guard container branch removed, Any aligned with Phase 1, REQUIRED_HOLE hint; 2 src + 6 test
files (commit_manifest.txt), docs, graph and release note updated; assets deferred to the owner.
Opened 2026-09-26T11:56:47Z on owner redirect. Investigation first; no src edits until the owner approves a plan.
Resume from the latest Notes NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
