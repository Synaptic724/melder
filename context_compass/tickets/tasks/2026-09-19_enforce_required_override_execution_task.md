# Task: Enforce required supplied inputs in generated and hydrated execution

## Metadata
- Task ID: TASK-2026-09-19-enforce-required-override-execution
- Story: STORY-2026-09-19-discoverable-resolution-runtime
- Status: in_progress
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-19T22:12:13Z
- Updated: 2026-09-19T22:12:13Z

## Objective
Qualify supplied-value behavior across solo, generalized and many-only execution using ordinary
Python missing-argument errors. Fix actual override/cache failures without a new runtime preflight.

## Ticket Contract
- ENTRY_GATE: Owner authorized S4 continuation; board routes here. S3 input rows and the direct
  admission task are implemented. Read the exact emitted/hydrated owners before creating patch contracts.
- EXECUTION_BOUNDARY: Phase11 live schema/export, generated family compilers/runtime helpers,
  override addressing/preflight, cache hydration/signature compatibility and focused regressions/docs.
- DEPENDENCIES: S3 required_override_params and S4 direct refusal; S5/S6 consume the completed contract.
- EXIT_GATE: Supplied values reach consumers, omission retains ordinary constructor failure,
  reuse/branch replacement work, and emitted/hydrated paths agree without new success-path preflight.
- FAILURE_ESCALATION: Prove ordering and ownership from source. Do not add implicit external providers,
  reinterpret default/Optional policy, mutate supplied values or introduce an alternate cache framework.

## Scope Boundaries
- In scope: required-input runtime semantics and direct codegen/override/cache consumers.
- Out of scope: graph/history tools, crystal restore/graft, new ownership/lifetime policy, releases,
  source-body identity or unrelated executor refactors.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: Owner resumed and directed completion using the simpler ordinary-constructor-error approach.

## Required Reading
- S4 story's complete read map and S1 required/default/presence versus type policy.
- S3 implementation handoff and admission validation result; do not repeat their completed discovery.
- Verified component/graph slices before actual emission/hydration/override source call paths.
- CodegenCreationSchemaHelpers is the live Phase11 step exporter; the SharedCompilerExecutions twin
  is not a substitute. Read injection analysis, generalized/many-only plan steps, all affected compiler
  families and namespace/cache hydration consumers before changing them.
- Existing override and cache test fixtures before new tests. Reuse unchanged reads in this session.

## Working Contract
- required_override_params rows: (name, position, parameter-kind name, referenced-ID tuple).
- Carry rows independently of optional targeting metadata in both no-overrides/overrides variants.
- Normalize effective addressing/arguments before presence checks. None and falsey values are present;
  do not introduce a new annotation-type validation policy in a presence check.
- A reused consumer or supplied whole branch skips that constructor's input requirements.
- Preserve current shared-instance override restrictions and selector/default/collection semantics.
- Preserve ordinary Python missing-argument errors and existing wrappers; no new early-input preflight.
- Qualify actual cold/warm executor behavior using existing mismatch/invalidation machinery.

## Steps / Checklist
- [ ] Trace live row export, solo emission/hydration and required metadata transport.
- [ ] Verify generalized/many-only overrides, reuse and branch replacement with focused runtime tests.
- [ ] Create/read patch contracts only for an actual implementation failure requiring a fix.
- [ ] Qualify public Base/Consumer and nested/reuse behavior using normal constructor errors.
- [ ] Fix any demonstrated supplied-value or hydration failures; do not add custom missing-input preflight.
- [ ] Qualify supported override shapes, hooks, reuse, scopes, selected-version changes and cache parity.
- [ ] Refresh docs/assets, record limits and route S5/S6 handoffs.

## Deliverables
- Executable required-input contract, meaningful regressions and cache parity evidence.
- Concrete schema/ordering handoff to the remaining graph and persistence stories.

## Files / Paths Impacted
- Spell compiler codegen_creation_system, direct override processors, runtime/plan metadata owners.
- Scoped tests and existing runtime caches/signatures only where required by source evidence.
- Source docs/descriptors/build outputs and ContextCompass tracking for this task.

## Validation
- Not run for this task. Prior admission: 665 passed, one existing deferred skip.
- Use .venv_new Python 3.14.7 free-threaded, uv --no-sync --offline, -X gil=0 and no pytest cacheprovider.

## Risks / Rollback Notes
- Solo executors may compile straight from Spell while many-only steps omit injection objects.
- A late per-node check can produce earlier dependency/hook side effects before refusal.
- A naive global preflight can reject reused or whole-branch-supplied consumers incorrectly.
- Existing cached templates/namespaces must enforce the same input contract after hydration.
- Preserve all S2/S3/admission and other agents' work; the current workspace version is 0.2.43.

## Applicable Anti-Patterns
- [ ] No truthiness-based presence test, synthetic None or lost reference identity.
- [ ] No preflight of a constructor the call will not execute.
- [ ] No missing required-input rows after optional targeting stripping or cache hydration.
- [ ] No new ownership, provider registry or invalidation framework.

## Done Checklist
- [ ] Runtime input contract and meaningful compatibility tests pass.
- [ ] Documentation/build state and S5/S6 handoff synchronized.
- [ ] Honest scope/remaining limits recorded.
- [ ] Owner acceptance before closure.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- PATCH_ID: required_override_execution_2026_09_19
- ARTIFACT_PATHS:
  - artifacts/required_override_execution_20260919/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: accepted task closure; promote/archive patch contracts normally.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: live Phase11 schemas, required input, effective overrides, reuse/pruning, hydration.
- IF_UNKNOWN: none

## Noting Behavior
Finish one complete source path, then record its evidence and next concrete step before continuing.

## Notes
- DATETIME: 2026-09-19T22:12:13Z
  TYPE: PLAN
  CLAIM: Direct refusal is delivered; continue S4 with required supplied-value execution. No source
    changes or tests for this new task have begun. Accepted presence semantics are distinct from a
    new type-validation policy, and reuse/whole-branch replacement determine which constructors run.
  EVIDENCE:
  - tickets/stories/2026-09-19_discoverable_resolution_runtime_story.md:28-47
  - tickets/tasks/2026-09-19_define_caller_supplied_socket_contract_task.md:116-164
  - tickets/tasks/2026-09-19_enforce_non_resolvable_runtime_admission_task.md
  IMPACT: Runtime input enforcement has its own bounded owner without reopening the direct admission patch.
  NEXT: Read live Phase11 export and solo emission/hydration, then follow generalized/many-only preflight.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T22:17:11Z
  TYPE: DECISION_REQUEST
  CLAIM: Owner explicitly paused required-input implementation and questioned the need/cost of
    additional checks because Python already rejects omitted required constructor arguments.
    No runtime preflight or input-enforcement source changes/tests have been added by this task.
    Read live schema helper, injection records, both solo compiler files and solo manifest; hydration
    and generalized/many-only preflight have not been traced. Keep those reads stopped for discussion.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:299-500
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:75-238
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:272-311
  IMPACT: Separate the compiler's descriptive/non-construction distinction from optional early
    missing-input diagnostics. No performance claim is measured for a proposed preflight implementation.
  NEXT: Discuss retaining ordinary Python missing-argument errors instead of adding runtime preflight.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T22:21:52Z
  TYPE: DECISION
  CLAIM: Owner resumed after the proposed simplification and explicitly requested completing the full
    feature. Drop custom early missing-input preflight; use ordinary Python constructor errors and
    existing wrappers. Verify real supplied-value/nested/reuse/cache behavior, fix only demonstrated
    gaps, then complete Nexus graph and Crystallizer replay. Preserve compiler descriptive references.
  EVIDENCE:
  - tickets/tasks/2026-09-19_enforce_non_resolvable_runtime_admission_task.md
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:272-311
  IMPACT: Early-error ordering and a custom missing-input diagnostic are removed from acceptance.
    No proposed preflight was implemented, so this is a scope correction rather than a runtime rollback.
  NEXT: Run focused supplied-value/omission/nested/reuse/cache tests, then move to Nexus and persistence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T22:25:53Z
  TYPE: MEASURE
  CLAIM: Real family/manifest tests report 27 passed, four failed. Ordinary/falsey/None values,
    positional supply, omission, unique reuse and explicit descriptor supply work without new preflight.
    Whole-child replacement fails in many-only/generalized, both cold and hydrated: the runtime still
    constructs SuppliedConsumer before replacing it, so its now-unneeded external argument raises.
  EVIDENCE:
  - artifacts/required_override_execution_20260919/runtime_initial.xml:1-1
  - tests/component/melder/aether/conduit/test_conduit_component_non_resolvable_overrides.py:95-164
  IMPACT: Investigate actual branch construction behavior; keep ordinary missing-argument errors.
  NEXT: Trace shape-specialized step execution and existing override branch pruning before fixing it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T22:29:21Z
  TYPE: FACT
  CLAIM: A control graph with only ordinary required int arguments reproduces the same whole-child
    override failure, without any False registration. Current emitters execute every plan step before
    parent replacement; branch pruning is a separate existing behavior, not a regression introduced
    by this feature. Preserve that behavior in this feature's compatibility tests rather than adding
    the broader pruning optimization the owner did not request. Record it for separate follow-up.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_non_resolvable_overrides.py:test_ordinary_branch_override_also_constructs_its_registered_child
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:769-887
  IMPACT: The earlier assumption that replacing a branch skips all its construction was false. Test
    compatibility with current eager construction; keep this limit explicit rather than silently claiming pruning.
  NEXT: Finish runtime compatibility, then complete Nexus publication and crystal replay.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
RESUMED. Finish with ordinary Python missing-argument errors; no additional early-input preflight.
No source/test edits yet in this task. Qualify real supplied-value/nested/reuse/cache behavior and fix
actual failures only, then finish S5 Nexus and S6 Crystallizer. S3 compiler and direct admission remain.
Source already read: schema helper, injection analysis, both solo compilers, solo manifest. No agents.
