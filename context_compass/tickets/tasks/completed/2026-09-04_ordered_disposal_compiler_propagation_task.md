# Task: Carry the Spell disposal list through compiler families

## Metadata
- Task ID: TASK-2026-09-04-ordered-disposal-compiler-propagation
- Story: STORY-2026-09-04-ordered-disposal-runtime
- Story Ticket: `tickets/stories/completed/2026-09-04_ordered_disposal_runtime_story.md`
- Epic Ticket: `tickets/epics/completed/2026-09-02_ordered_live_spell_disposal_epic.md`
- Status: done
- Completed: 2026-09-05T14:22:02Z
- Summary: Preserved established list references through compiler families, namespaces, and cache hydration.
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-04T21:17:27Z
- Updated: 2026-09-05T14:22:02Z

## Objective
Carry each Spell's resolved ordered list through runtime records, plans, and emitted
executor bindings without redundant live-list copies or changes to execution algorithms.

## Ticket Contract
- ENTRY_GATE: Binding task verified; runtime patch contract read and mapped; board routes here.
- EXECUTION_BOUNDARY: Disposal metadata propagation in the compiler families and focused tests.
- DEPENDENCIES:
  `tickets/tasks/completed/2026-09-04_ordered_disposal_bind_and_spell_task.md`
  `tickets/tasks/completed/2026-09-04_ordered_disposal_patch_contract_task.md`
- EXIT_GATE: Solo, generalized, and many-only paths preserve order through cold and cached
  execution, including override variants; direct live-list ownership is established.
- FAILURE_ESCALATION: Classify a real cache/schema dependency before changing a conversion;
  no blanket tuple-to-list codemod or unrelated compiler redesign.

## Scope Boundaries
- In scope: names, related presence/register flags, metadata carriers, and runtime namespace bindings.
- Out of scope: method matching, override API redesign, arbitrary post-creation list mutation.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner accepted delivery and requested this closure; completed at 2026-09-05T14:22:02Z.

## Required Reading and Evidence
Read Component: SpellCompiler and Validation Pipeline and Component: Meld Resolution Runtime
through the component index. Use graph index rows for the files below, then read the source.
Earlier discovery inspected contact functions, not every complete compiler file.

Runtime record and planning entry anchors:
- `src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_runtime_analysis.py:31-91`
- `src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_runtime_processor_strategy.py:38-100`
- `src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1091-1302`
- `src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1460-1590`
- `src/melder/aether/spellbook/spell_compiler/codegen_planner/data/many_only_codegen_plan.py:1057-1115`

Also read the disposal-bearing functions in these known contact files under `spell_compiler/`:
- `phases/shared_compiler_executions.py`
- `codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py`
- `codegen_creation_system/strategies/many_only/many_only_codegen_creation_helpers.py`
- `codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py`
- `codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py`
- `codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py`
- `codegen_creation_system/strategies/generalized/compilers/generalized_manifest_overrides_runtime.py`
- `codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py`
- `codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py`
- `codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py`
- `codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py`
The source prefix for those relative entries is `src/melder/aether/spellbook/spell_compiler/`.
Open complete implementations before editing; the list is a shortlist, not an edit-all instruction.

## Steps / Checklist
- [x] Classify each contact as a live reference, copied inner method list, or serialized/hash values.
- [x] Carry the resolved list directly in SpellRuntimeRecord and generalized plan steps.
- [x] Adjust solo normalization and many-only metadata only where they detach live method values.
- [x] Preserve outer containers that already hold the same inner list references.
- [x] Keep genuine IR/hash projections deterministic and order-preserving, documenting why
      they are value boundaries. Check cache hydration rebinding to live Spell metadata.
- [x] Preserve existing has_disposal_methods/must_register and lifetime-store routing.
- [x] Test family and override variants, cold and cached; append results before Creations work.

## Deliverables
Minimal compiler metadata/type/docstring changes and focused family/cache regression coverage.

## Files / Paths Impacted
- Only evidenced metadata contacts from the inventory above and their paired tests.
- `tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_compilers_core.py`
- `tests/unit/melder/spellbook/spell_compiler/test_spell_artifact_processor_data_migrations.py`
- `tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_cache_rehydration_exec.py`
- `tests/unit/melder/spellbook/spell_compiler/codegen_planner/test_generalized_dual_build_differential.py`
- Relevant component pipeline tests; read test docs and implementations first.

## Validation
- Passed: 81 focused cases, then 792 compiler unit/Spellbook component tests on Windows 3.14t.
- No full-suite, cross-platform, or whole-world persistence/replay claim. Assets remain deferred.
- Assert exact names at registration, not merely tuple/list type or attribute existence.
- Check the explicit sharing contract for live metadata; it is not a mutation feature.
- Confirm cached value projections retain order and hydrated executors use current bound Spells.
- Subsequent Creations task verifies the actual cleanup result with these executors.

## Risks / Rollback Notes
An outer `tuple(spell.disposal_method_names for spell in spells)` retains list references;
it is different from `tuple(spell.disposal_method_names)`, which projects the names themselves.
Do not remove useful cache value normalization or make a key unhashable accidentally.

## Applicable Anti-Patterns
- [x] No indiscriminate snapshot/tuple removal or compiler performance claims without measurements.
- [x] No invented mutation invalidation system or extra hot-path guards.

## Done Checklist
- [x] Minimal changes and family/cache tests complete with evidence.
- [x] Live ownership versus serialized values documented in touched contracts.
- [x] Creations task unblocked; closure requires owner acceptance.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false (closed)
- ARTIFACT_PATHS: none active
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: owner-accepted closure 2026-09-05T14:22:02Z
- Durable contracts: source architecture/components, source docstrings, README, configuration guide,
  and committed regression tests. Temporary patches/probes/validation scratch are removed at closure.
- Historical artifact citations in Notes are retained; tracked patches are recoverable from Git history.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: compiler carriers, emitted bindings, cache hydration
- IF_UNKNOWN: none

## Noting Behavior
Record the classification and evidence before changing each compiler family. One NEXT per note.

## Notes
- DATETIME: 2026-09-04T21:17:27Z
  TYPE: PLAN
  CLAIM: Runtime processor/plan conversions and solo normalization need classification;
    some namespace arrays already retain the Spell's collection by reference.
  EVIDENCE:
  - `src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_runtime_processor_strategy.py:79-94`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:965-1030`
  IMPACT: The narrow fix must preserve compiler algorithms and required cache schemas.
  NEXT: Trace processor -> plan -> one solo executor with the Phase 1 list contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:57:25Z
  TYPE: FACT
  CLAIM: Holistic source trace separates three compiler contact classes. Live-value copies:
    processor tuple conversion, both generalized builder list conversions, many-only plan
    inner tuples, and both solo normalization helpers. Existing direct-reference carriers:
    SpellRuntimeRecord/PlanStep stores and generalized/many-only executor namespace arrays,
    including the manifest runtime paths. Real value boundaries: phase-11 schema rows and
    spell/many-only signature rows encode ordered tuples for serialization and hashing.
  EVIDENCE:
  - `src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_runtime_analysis.py:31-91`
  - `src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_runtime_processor_strategy.py:38-100`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1091-1302`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1460-1728`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/data/many_only_codegen_plan.py:1057-1310`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:8-248`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:8-318`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:302-443`
  - `src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1011-1198`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/many_only_codegen_creation_helpers.py:163-270`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:965-1030`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_overrides_runtime.py:448-521`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1146-1201`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:448-545`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:935-994`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:443-541`
  IMPACT: Update only the live metadata copies/types. Keep outer arrays that already hold
    the same inner collection, and keep ordered schema/hash encoding. The six executor
    namespace contacts are verification targets, not an edit-all list. Preserve register
    flags: many without disposal is untracked; other lifetimes use their selected store.
    This was source inspection, not cold/cache execution proof. Large files were read by
    relevant complete methods/blocks; do not claim whole-file review of every compiler.
  NEXT: At implementation, consume the patch and verify cold/cache hydration uses the same
    established list through each family; no blanket conversion rewrite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:46:41Z
  TYPE: PLAN
  CLAIM: Owner requested continuation to compiler/Creations propagation. Producer changes
    are verified by 753 selected tests. Begin with compiler contacts; preserve algorithms,
    lifetime routing, ordered hash/IR projections, and existing synchronization.
    codex_2 reports regenerated tracked LLM corpora but excluded our untracked test module;
    final corpus refresh remains required when the epic reaches its assets task.
  EVIDENCE:
  - `context_compass/tickets/tasks/completed/2026-09-04_ordered_disposal_bind_and_spell_task.md`
  - Incoming codex_2 notice, 2026-09-05T09:41:40Z, citing artifacts/2026-09-05_rtd_local_build_validation.md:49-59.
  IMPACT: Do not change other agents' documentation, CI, or corpus work. No commits/pushes.
  NEXT: Read the compiler component/graph slices and classify the known live-copy contacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:49:29Z
  TYPE: FACT
  CLAIM: Complete reads of runtime record/processor and both solo compiler modules confirm
    the first live copies. The record stores its supplied names directly; the processor creates
    a tuple first. Both solo namespace binders pass names through a tuple-normalizing helper.
    Their emitted source contains only the presence flag and lifetime route, not method names.
    Runtime-analysis cleanup clears the outer record map and does not clear inner names.
  EVIDENCE:
  - `src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_runtime_analysis.py:31-140`
  - `src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_runtime_processor_strategy.py:38-116`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:8-248`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:8-318`
  IMPACT: Retain the list at these compile-time boundaries; do not rewrite emitted lifetime
    routing, override application, or code-object cache semantics.
  NEXT: Read both complete plan implementations and classify their disposal-bearing fields/builders.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:51:21Z
  TYPE: FACT
  CLAIM: Both plan files are now fully read (generalized 2,752 lines; many-only 1,381).
    Generalized single/dual builders each copy runtime_record names into a list; the step
    retains it directly. Many-only builds inner tuples for the no-overrides metadata array.
    Plan cleanup clears outer arrays/maps only, leaving borrowed inner lists intact.
    Register/store decisions are independent of collection type and remain unchanged.
  EVIDENCE:
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:127-251`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:683-910`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1091-1302`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1460-1728`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/data/many_only_codegen_plan.py:300-542`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/data/many_only_codegen_plan.py:1057-1310`
  IMPACT: Six compiler source files need small propagation/type/doc changes; do not rewrite
    fast-call arrays, overrides, cache schema rows, or cleanup algorithms.
  NEXT: Verify emitted namespace and serialized row boundaries, then prepare tests/contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:55:21Z
  TYPE: FACT
  CLAIM: Namespace reads confirm the six generalized/many-only binders already retain inner
    Spell-list references. Canonical/legacy phase-11 rows and many-only signatures intentionally
    project ordered values. Complete cache-helper read confirms hydration resolves the live
    Spell lookup before namespace creation. The selected existing compiler baseline passes
    56 tests in 0.33s. Compiler contracts are now authored for the six-file correction.
  EVIDENCE:
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:302-443`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py:316-484`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1146-1205`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:935-1008`
  - Command: .venv_new/Scripts/python.exe -m pytest tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_compilers_core.py tests/unit/melder/spellbook/spell_compiler/test_spell_artifact_processor_data_migrations.py tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_cache_rehydration_exec.py tests/unit/melder/spellbook/spell_compiler/codegen_planner/test_generalized_dual_build_differential.py -q -p no:cacheprovider --tb=short
  IMPACT: Only live copies/types change; hash/IR, six existing namespace functions, and cache
    helper source stay untouched. Tests must exercise behavior as well as explicit sharing.
  NEXT: Index/consume the compiler contracts, add red regressions, then apply the six-file edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:59:50Z
  TYPE: PLAN
  CLAIM: Compiler architecture/component/control-flow contracts were indexed, linked, and
    consumed. Mapping: processor/record -> record identity/order; generalized single/dual and
    many-only plans -> step/array identity plus cleanup; solo normalization -> actual emitted
    registration and reused code-object binding; preserved IR/cache boundaries -> ordered
    marshal roundtrip and stored-code hydration against fresh Spell references.
  EVIDENCE:
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/architecture_patch.md:20-73`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/component_patch_compiler_disposal.md:7-39`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/code_description_patch_compiler_disposal.md:7-30`
  IMPACT: Compiler entry gate is satisfied. Six source files are fully read; other namespace,
    row, and cache helper paths are verification boundaries, not new implementation scope.
  NEXT: Add/run focused compiler regressions before applying the propagation edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:04:13Z
  TYPE: MEASURE
  CLAIM: New compiler regressions run: 22 failed, 3 passed in 0.35s. Twenty failures expose
    the intended processor/solo list-copy mismatch. Two override cases need fixture review:
    the recording store lacks its lock, and direct many-only plan steps lack the hydrated
    runtime shape expected by the override namespace. No runtime workaround is authorized.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe -m pytest tests/unit/melder/spellbook/spell_compiler/test_ordered_disposal_compiler.py -q -p no:cacheprovider --tb=line
  - `tests/unit/melder/spellbook/spell_compiler/test_ordered_disposal_compiler.py`
  IMPACT: Source correction remains the six-file metadata patch. Trace the real many-only
    override caller before repairing the test setup, not the production contracts.
  NEXT: Verify the override setup boundary, apply the six-file patch, and rerun the focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:08:16Z
  TYPE: FACT
  CLAIM: Six compiler files now retain the established list: runtime record/processor,
    generalized single/dual builders, many-only metadata, and both solo helpers. Updated
    the existing record fixture to list inputs. Override test setup now supplies the store
    lock and uses many-only row hydration, matching the actual many-only phase-11 caller.
    No production locks, namespaces, hash/IR encoding, or cache formats were changed.
  EVIDENCE:
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_overrides_codegen_creation_step.py:113-180`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:2180-2220`
  - `tests/unit/melder/spellbook/spell_compiler/test_ordered_disposal_compiler.py`
  IMPACT: Test-double failures are repaired at the test boundary; compiler runtime behavior
    remains unchanged apart from list ownership. Verification is next, not yet claimed.
  NEXT: Run focused compiler tests and then the wider existing compiler suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:08:16Z
  TYPE: MEASURE
  CLAIM: Focused compiler verification passes 81 tests in 0.43s: 56 existing plus 25 new.
    Actual emitted registrations retain the supplied lists. Processor and all tested plan
    variants retain identity/order; serialized cache rows preserve order and stored-code
    hydration binds fresh Spell lists. Source diff is exactly six compiler files.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe -m pytest tests/unit/melder/spellbook/spell_compiler/test_ordered_disposal_compiler.py tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_compilers_core.py tests/unit/melder/spellbook/spell_compiler/test_spell_artifact_processor_data_migrations.py tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_cache_rehydration_exec.py tests/unit/melder/spellbook/spell_compiler/codegen_planner/test_generalized_dual_build_differential.py -q -p no:cacheprovider --tb=short
  - Result: 81 passed in 0.43s, exit 0.
  IMPACT: Focused contract is green. Wider compiler and real component regression checks
    precede switching to Creations ownership changes.
  NEXT: Run the wider compiler unit/component boundary and inspect the six-file diff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:10:55Z
  TYPE: MEASURE
  CLAIM: Wider compiler/Spellbook verification passes 792 tests in 3.43s. The six-file source
    diff is reviewed and scoped whitespace checking passes. No emitted algorithms, locks,
    cache helpers, or schema-value transforms were changed.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe -m pytest tests/unit/melder/spellbook/spell_compiler tests/component/melder/spellbook -q -p no:cacheprovider --tb=short
  - Result: 792 passed in 3.43s, exit 0.
  IMPACT: Compiler slice is in review; its verification prerequisite unblocks Creations work.
  NEXT: Execute the separately routed Creations metadata-ownership task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:33:58Z
  TYPE: MEASURE
  CLAIM: Real Creations integration found two additional copies inside generalized manifest
    emitted registration, beyond the correctly shared namespace. The Creations caller clause
    owns the correction, and the updated compiler contract includes this seventh source file.
    Final combined runtime verification passes 2,797 tests; no source synchronization changed.
  EVIDENCE:
  - `context_compass/tickets/tasks/completed/2026-09-04_ordered_disposal_creations_task.md`
  IMPACT: The initial six-file/792-test result was not complete end-to-end evidence; the real
    stored-list assertion closed that gap without weakening the contract.
  NEXT: Verify configuration transport, then proceed with crystal/replay order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T14:22:02Z
  TYPE: DECISION
  CLAIM: Owner accepted this deliverable and requested closure of the ordered-disposal program.
    Preserved established list references through compiler families, namespaces, and cache hydration.
  EVIDENCE: tickets/tasks/completed/2026-09-04_ordered_disposal_end_to_end_validation_task.md
  IMPACT: Ticket history is retained under completed. Registered temporary artifacts are disposed
    at accepted closure; durable behavior is in canonical docs, examples, source, and regression tests.
    Linux/hosted checks and unrelated recording/name-lookup findings retain their documented scope.
  NEXT: none; this work item is closed.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
CLOSED: 2026-09-05T14:22:02Z. Preserved established list references through compiler families, namespaces, and cache hydration.
Program record: tickets/epics/completed/2026-09-02_ordered_live_spell_disposal_epic.md
No active work remains in this ticket. Prior handoff text below is historical.

### Historical handoff at closure
Seven compiler source files and focused tests are implemented/in review. All seven edited files
were read fully; other namespace/cache contacts were read through their relevant functions.
Twenty-five new tests cover list identity/order, plan cleanup, six solo routes with overrides
and code-cache reuse, generalized/many-only registration, and marshal/stored-code hydration.
81 focused tests and the wider 792-test compiler/Spellbook boundary pass on Windows 3.14t.
Creations and generalized inline storage now retain names, verified by the combined 2,797-test run.
This agent did not commit/push or regenerate final assets; separate commits occurred during work.
Next: `tickets/tasks/completed/2026-09-04_ordered_disposal_creations_task.md`.
