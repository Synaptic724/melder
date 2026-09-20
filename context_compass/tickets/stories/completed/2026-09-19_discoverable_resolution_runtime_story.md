# Story: Enforce non-resolution and caller-supplied inputs across runtime execution

## Completion
- Completed: 2026-09-20T00:25:59Z
- Summary: Delivered direct non-resolution admission and verified existing supplied-value and cached execution semantics.
- Acceptance: Owner requested turn-in, then required two repairs first; both are verified.

## Metadata
- Story ID: STORY-2026-09-19-discoverable-resolution-runtime
- Epic: EPIC-2026-09-19-discoverable-non-resolvable-registrations
- Sequence: S4
- Status: done
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-19T17:25:45Z
- Updated: 2026-09-20T00:25:59Z

## User Narrative
As a user, I receive clear errors when melding a discovery-only target or constructing a consumer
without its required supplied input, and valid overrides work through all supported execution paths.

## Value / MRP Alignment
Make the declaration enforceable at actual execution, including paths that skip normal validation.

## Ticket Contract
- ENTRY_GATE: S1/S2/S3 contracts are available; a runtime task and concurrency/control-flow patch exist.
- EXECUTION_BOUNDARY: Conduit/SpellSpace meld and reuse, creation-context execution, override targeting,
  emitted executors, fast doors and compiled-cache hydration.
- DEPENDENCIES: S2 per-Spell policy and S3 resolved input schema. Expose cache schema needs to S6.
- EXIT_GATE: Direct and nested execution enforce mode/input contracts with cold/warm parity.
- FAILURE_ESCALATION: Reproduce bypasses and contract mismatches; do not add blanket defensive guards.

## Requirements (Functional)
- Direct meld and reuse-only meld refuse a selected non-resolvable registration before invocation.
- Preserve registration lookup/introspection so Nexus can still discover the target.
- Enforce capability independently of _spellbook_validation_required and risk-based validation skipping.
- Preserve Python's normal errors for missing ordinary required constructor arguments and existing
  error wrappers. Owner removed the proposed custom early-input preflight from scope.
- Accept actual override payloads through existing named/positional/deep/broadcast semantics as supported.
- Keep ordinary defaults and normal consumer reuse semantics intact.
- Prevent nested compiled execution from constructing a non-resolvable dependency without relying on
  a top-level Meld callback that those executors may not use.
- Qualify solo/generalized/many-only, hooks/no-hooks, dynamic/automatic, cache cold/warm and SpellSpace doors.
- Preserve existing invalidation/epoch protocols; mode must not survive selection changes incorrectly.
- Supplying an object does not create a new ownership/disposal policy for that reference.

## Requirements (Non-Functional)
- Use the existing cache/version/epoch machinery; no new global invalidation framework.
- Add only contract-required checks and measure any claimed performance effect.
- Preserve existing construction/reuse ordering; no additional per-call argument preflight.

## Scope Boundaries
- In scope: actual input supply and resolution refusal, execution IR/hydration and focused runtime tests.
- Out of scope: new lifetime modes, broad instance transfer/disposal redesign, Nexus graph authoring.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner-authorized turn-in after delivered scope and reported failure repairs passed.

## Dependencies / Related Work
- Parent: `tickets/epics/completed/2026-09-19_discoverable_non_resolvable_registrations_epic.md`
- S2: `tickets/stories/completed/2026-09-19_discoverable_registration_modifier_story.md`
- S3: `tickets/stories/completed/2026-09-19_caller_supplied_socket_compiler_story.md`
- Next: `tickets/stories/completed/2026-09-19_discoverable_nexus_graph_and_history_story.md`
- Cache/replay partner: `tickets/stories/completed/2026-09-19_discoverable_registration_persistence_story.md`

## Required Reading Before Work
1. Parent epic and accepted S1-S3 contracts, especially requiredness and resolved target metadata.
   Read the proposed input schema, solo executor finding and First Regression Design in:
   `tickets/tasks/completed/2026-09-19_define_caller_supplied_socket_contract_task.md`.
   The proposal is not a claim that any execution path already supports this feature.
   The chosen name is OVERRIDE_REQUIRED. Read
   `tickets/tasks/completed/2026-09-19_define_discoverable_registration_selection_task.md` for exact root
   refusal and the rule against falling back from a failed True provider to required overrides.
2. Verify `system_docs/src_components_index.md`; read Meld Resolution Runtime, Creations and SpellSpace,
   and SpellCompiler and Validation Pipeline. Use verified graph-index slices for touched nodes.
3. Trace complete entry/dispatch paths:
   - `src/melder/aether/conduit/conduit.py` — public meld/reuse facade and payload forwarding.
   - `src/melder/aether/conduit/meld/meld.py` — shared lookup, validation and override normalization.
   - `src/melder/aether/conduit/meld/conduit_meld.py` — meld, reuse-only and fast-door paths.
   - `src/melder/aether/conduit/meld/spellspace_meld.py` — scoped equivalents.
   - `src/melder/aether/conduit/meld/overrides/spell_overrider.py`
   - `src/melder/aether/conduit/meld/creation_context/creation_context.py`
   - `src/melder/aether/conduit/meld/creation_context/creation_context_factory.py`
   - `src/melder/aether/conduit/meld/creation_context/creation_context_builder.py`
   - `src/melder/aether/spellbook/spell.py` — context publication and door epochs.
4. Trace resolved-input data into emitted/runtime code before editing each family:
   - `src/melder/aether/spellbook/spell_compiler/artifact_processor/data/spell_injection_analysis.py`
   - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py`
   - `src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_override_targeting_processor_strategy.py`
   - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py`
   - Solo, generalized and many-only strategy compiler/step/hydration directories under
     `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/`.
   Read the selected complete files, their manifests and runtime helpers; no blanket whole-tree preload.
   - `src/melder/aether/spellbook/spellbook_creation_system.py` — cache load and context installation.
5. Before test edits, use test architecture/component indexes and read the relevant fixtures:
   - `tests/component/melder/aether/conduit/test_conduit_component_meld_overrides.py`
   - `tests/component/melder/aether/conduit/test_conduit_component_meld_overrides_deep.py`
   - `tests/integration/melder/spellbook/test_spellbook_integration_overrides.py`
   - `tests/integration/melder/spellbook/test_spellbook_integration_default_precedence.py`
   - `tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_cache_rehydration_exec.py`
   - `tests/experimentation/test_creation_context_override_cache_asset_experiment.py`

## S3 Delivered Compiler Contract
Read `tickets/tasks/completed/2026-09-19_implement_override_required_compiler_task.md` and its validation artifact.
S3 passes 2098 focused tests; it does not enforce actual supplied values or every resolution door.

- Local topology records SocketKind.OVERRIDE_REQUIRED, empty executable target_spell_ids, descriptive
  referenced_spell_ids, the actual parameter position and parameter_kind, plus the selector key.
- Injection sources use kind="override_required". Injection specs and both planner families/variants
  retain immutable required_override_params tuples of (name, position, parameter-kind name, reference IDs).
- Required input rows are independent of optional override-targeting metadata. Generalized steps retain
  inject_spec in both variants; standalone many-only steps do not have inject_spec.
- Injection IR/signature rows carry the extra values for this source kind. The live Phase11 step-row
  exporter is CodegenCreationSchemaHelpers, not the legacy SharedCompilerExecutions step-row twin.
  S4 must read and wire the real exporter, family compilers and cache-hydration consumers.
- False roots are excluded from executable Phase5 snapshots and Phase8-11 scheduling/cache admission.
  This does not replace direct/reuse/fast/nested runtime capability checks.
- Selector changes reuse the existing frame-key watcher. Successful structural reruns now gate the
  prior conduit-local verdict through Meld._force_resolution_revalidation(reason=structure_changed).
  Direct-consumer notch/new-provider transitions pass; deeper transition matrices remain unqualified.

First runtime proof: a False Base and a resolvable Consumer with a required Base argument. Refuse
direct Base meld, report an omitted Consumer input, and return the exact supplied object on success.
Then cover fast/scoped/reuse/nested/hook/cache variants without adding another invalidation framework.

## Tasks (Implementation Checklist)
- [x] Direct/runtime admission (implemented; review pending):
  `tickets/tasks/completed/2026-09-19_enforce_non_resolvable_runtime_admission_task.md`.
- [x] Required supplied-input compatibility (implemented/tested; no custom preflight):
  `tickets/tasks/completed/2026-09-19_enforce_required_override_execution_task.md`.
- [x] Create scoped runtime tasks and consume the S3 contract.
- [x] Add direct-refusal and ordinary required-input compatibility regressions.
- [x] Verify existing caller supply through nested targeting and all three executor families.
- [x] Verify reuse and preserve existing hook/construction ordering without custom preflight.
- [x] Qualify memoized executors, manifest hydration and version/selection behavior.

## Acceptance Criteria
- Discovery-only targets never produce or return an instance through prohibited execution doors.
- Ordinary required arguments retain Python omission errors; supplied values reach consumers by identity.
- Defaults, unrelated providers and normal reuse continue working.
- Nested/cached/scoped paths agree with ordinary paths; no validation-disabled bypass remains.
- No newly assigned lifecycle ownership arises merely from supplying an override.

## Validation / Test Plan
- Direct admission: 58 new cases; supplied-value/executor/cache compatibility: 32 cases. They are
  included in the final 8055-distinct-test qualification; do not add overlapping counts.
- Use the minimum real runtime slice; mock only external boundaries.
- Exercise malformed, omitted, falsey and explicit-None inputs according to S1 policy.
- Keep failures as regressions to fix; do not weaken assertions to accept partial behavior.

## UX / API / Data Notes
Errors distinguish unresolvable registration from unavailable provider and missing caller input.

## Risks / Mitigations
The fast door precedes normal checks and nested executors can bypass public meld; test both explicitly.

## Applicable Anti-Patterns
- [x] No restriction solely inside an optional validation gate.
- [x] No dependence on every nested call re-entering Meld.
- [x] No silent argument defaults, cache bypasses or new reference ownership.

## Open Questions
Use S1's required/type/descriptor policy; performance and failure-side-effect claims require measurements.

## Decision Log
- Runtime enforcement follows resolved socket policy; it does not reinterpret annotations independently.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: accepted story closure with per-artifact disposition.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: caller supply, nested overrides, meld doors, reuse and cache parity.
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-19T17:25:45Z
  TYPE: PLAN
  CLAIM: Runtime behavior is a separate proof obligation from storing a bool or producing a socket.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:143-609
  - src/melder/aether/conduit/meld/spellspace_meld.py:168-620
  IMPACT: Validation skipping and nested/cache execution must not bypass the capability contract.
  NEXT: Consume S3's resolved category and start the smallest direct/required-input regression task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T18:36:34Z
  TYPE: PLAN
  CLAIM: S1 traced the solo executors: they compile from Spell and invoke the call target directly,
    without enforcing a required-input plan. S4 must deliver the input contract into emitted code
    and hydrated namespaces, preserve presence versus falsey values, check only constructed
    consumers, and prove branch replacement/reuse/hook ordering before claiming early failure.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-19_define_caller_supplied_socket_contract_task.md:115-215
  IMPACT: A plan-only change cannot close S4. First regression groups and untraced families are explicit.
  NEXT: Use S1's accepted contract for the first real Base/Consumer runtime regression.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T21:38:40Z
  TYPE: FACT
  CLAIM: S3 now supplies an implemented required-input/reference schema, both planner variants and
    existing revalidation integration. Runtime enforcement is still absent from this story; live
    Phase11 row export, emitted family executors and cache hydration must consume the new rows.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-19_implement_override_required_compiler_task.md
  - artifacts/override_required_compiler_20260919/validation.md:1-72
  IMPACT: S4 is ready for a scoped runtime task with real red regressions. Compiler test success
    cannot be used as direct/fast/cached execution proof.
  NEXT: Create the first runtime task and trace the common lookup/refusal and solo required-input path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T22:13:16Z
  TYPE: FACT
  CLAIM: Direct admission is implemented and in review: 665 passed, one existing owner-deferred
    shared-context skip. The shared error and four native checks preserve observational lookup and
    success-only warm entries. Docs/assets pass checks. Required supplied-input execution is the
    next active task; no full S4 completion or cache-input safety claim follows from admission tests.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-19_enforce_non_resolvable_runtime_admission_task.md
  - artifacts/non_resolvable_runtime_admission_20260919/validation.md:1-55
  IMPACT: Continue from the delivered compiler rows into actual emitted/hydrated input checks.
  NEXT: Execute tickets/tasks/completed/2026-09-19_enforce_required_override_execution_task.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T00:25:59Z
  TYPE: DECISION
  CLAIM: Owner-authorized feature turn-in is complete for this record. Both later reported failures
    are repaired: crystal test-double capability and current-run local cancellation forwarding.
    This acceptance retains ordinary Python errors, existing version rules and documented limits.
  EVIDENCE:
  - artifacts/non_resolvable_graph_replay_20260919/validation.md:1-78
  - artifacts/non_resolvable_followup_20260919/validation.md:1-50
  IMPACT: Record is done; validation evidence is retained and promoted patch contracts are archived.
  NEXT: none; reopen only for a new owner-requested change or new failure evidence.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Owner accepts runtime behavior and evidence.
- [x] Child tasks, artifacts and boards synchronized.

## Noting Behavior
Record cross-family policy here; preserve exact reproductions and results in the owning task.

## Context / Handoff Summary
CLOSED at 2026-09-20T00:25:59Z. Delivered direct non-resolution admission and verified existing supplied-value and cached execution semantics.
Final evidence and limits are in the graph/replay and follow-up validation artifacts.
No next implementation step remains in this accepted record.

### Historical pre-closure handoff
S4 is review-ready. Direct False selection refuses before optional validation/hooks/retrieval;
observational lookup and warm guards remain unchanged. Owner removed custom missing-input preflight.
32 real supplied-value/omission/reuse/cache cases pass using existing runtime execution; eager whole-child
construction remains existing behavior. Final graph/replay task records 8055 distinct selected passes.
