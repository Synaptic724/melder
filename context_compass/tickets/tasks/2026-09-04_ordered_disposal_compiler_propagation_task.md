# Task: Carry the Spell disposal list through compiler families

## Metadata
- Task ID: TASK-2026-09-04-ordered-disposal-compiler-propagation
- Story: STORY-2026-09-04-ordered-disposal-runtime
- Story Ticket: `tickets/stories/2026-09-04_ordered_disposal_runtime_story.md`
- Epic Ticket: `tickets/epics/2026-09-02_ordered_live_spell_disposal_epic.md`
- Status: ready
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-04T21:17:27Z
- Updated: 2026-09-04T21:17:27Z

## Objective
Carry each Spell's resolved ordered list through runtime records, plans, and emitted
executor bindings without redundant live-list copies or changes to execution algorithms.

## Ticket Contract
- ENTRY_GATE: Binding task verified; runtime patch contract read and mapped; board routes here.
- EXECUTION_BOUNDARY: Disposal metadata propagation in the compiler families and focused tests.
- DEPENDENCIES:
  `tickets/tasks/2026-09-04_ordered_disposal_bind_and_spell_task.md`
  `tickets/tasks/2026-09-04_ordered_disposal_patch_contract_task.md`
- EXIT_GATE: Solo, generalized, and many-only paths preserve order through cold and cached
  execution, including override variants; direct live-list ownership is established.
- FAILURE_ESCALATION: Classify a real cache/schema dependency before changing a conversion;
  no blanket tuple-to-list codemod or unrelated compiler redesign.

## Scope Boundaries
- In scope: names, related presence/register flags, metadata carriers, and runtime namespace bindings.
- Out of scope: method matching, override API redesign, arbitrary post-creation list mutation.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Owner requested a separate task for the runtime/compiler phase.

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
- [ ] Classify each contact as a live reference, copied inner method list, or serialized/hash values.
- [ ] Carry the resolved list directly in SpellRuntimeRecord and generalized plan steps.
- [ ] Adjust solo normalization and many-only metadata only where they detach live method values.
- [ ] Preserve outer containers that already hold the same inner list references.
- [ ] Keep genuine IR/hash projections deterministic and order-preserving, documenting why
      they are value boundaries. Check cache hydration rebinding to live Spell metadata.
- [ ] Preserve existing has_disposal_methods/must_register and lifetime-store routing.
- [ ] Test family and override variants, cold and cached; append results before Creations work.

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
- Not run; ticket only. Use supported Python 3.14.
- Assert exact names at registration, not merely tuple/list type or attribute existence.
- Check the explicit sharing contract for live metadata; it is not a mutation feature.
- Confirm cached value projections retain order and hydrated executors use current bound Spells.
- Subsequent Creations task verifies the actual cleanup result with these executors.

## Risks / Rollback Notes
An outer `tuple(spell.disposal_method_names for spell in spells)` retains list references;
it is different from `tuple(spell.disposal_method_names)`, which projects the names themselves.
Do not remove useful cache value normalization or make a key unhashable accidentally.

## Applicable Anti-Patterns
- [ ] No indiscriminate snapshot/tuple removal or compiler performance claims without measurements.
- [ ] No invented mutation invalidation system or extra hot-path guards.

## Done Checklist
- [ ] Minimal changes and family/cache tests complete with evidence.
- [ ] Live ownership versus serialized values documented in touched contracts.
- [ ] Creations task unblocked; closure requires owner acceptance.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false at ticket creation
- ARTIFACT_PATHS: none yet; consume the actual runtime/code-description patch before edits
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: final accepted program closure

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

## Context / Handoff Summary
No implementation yet. Read the actual compiler files; do not claim they were all read in full
before compaction. Preserve order and direct live references without inventing mutation support.
Next: `tickets/tasks/2026-09-04_ordered_disposal_creations_task.md`.
