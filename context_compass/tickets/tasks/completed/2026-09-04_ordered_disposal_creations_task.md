# Task: Preserve the established disposal list through Creations

## Metadata
- Task ID: TASK-2026-09-04-ordered-disposal-creations
- Story: STORY-2026-09-04-ordered-disposal-runtime
- Story Ticket: `tickets/stories/completed/2026-09-04_ordered_disposal_runtime_story.md`
- Epic Ticket: `tickets/epics/completed/2026-09-02_ordered_live_spell_disposal_epic.md`
- Status: done
- Completed: 2026-09-05T14:22:02Z
- Summary: Preserved disposal order and list lifetime through registration, transfer, and actual cleanup.
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-04T21:17:27Z
- Updated: 2026-09-05T14:22:02Z

## Objective
Have Creations retain and consume the established Spell disposal list directly, including
extraction/restoration, while preserving existing lifetime and cleanup behavior.

## Ticket Contract
- ENTRY_GATE: Binding/compiler tasks verified, runtime patch consumed, and board routes here.
- EXECUTION_BOUNDARY: Creations disposal metadata registration, extraction/restoration,
  existing invocation loop, and focused real runtime checks.
- DEPENDENCIES: `tickets/tasks/completed/2026-09-04_ordered_disposal_compiler_propagation_task.md`.
- EXIT_GATE: Actual cleanup follows the exact established method order; direct metadata
  ownership survives supported extraction/restoration without changing lifetime routing.
- FAILURE_ESCALATION: Record a real ownership/teardown conflict; do not solve hypothetical
  private-field mutation or expand into unrelated scheduling/locking repairs.

## Scope Boundaries
- In scope: disposal names accompanying existing object records and their consumption.
- Out of scope: new configuration reads, new reflection probes, new disposal scopes or methods.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner accepted delivery and requested this closure; completed at 2026-09-05T14:22:02Z.

## Required Reading and Evidence
Navigate Component: Creations and SpellSpace / Subcomponent: Creations Disposal Pipeline;
read the full Creations file and the affected caller methods before editing.
- `src/melder/aether/conduit/creations/creations.py:93-354` (registration/cleanup)
- `src/melder/aether/conduit/creations/creations.py:369-500` (extract/restore)
- `src/melder/aether/conduit/conduit.py:1386-1428` (existing-object forwarding)
- `src/melder/aether/spellbook/spell.py:500-603` (metadata cleanup ownership)
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1500-1584`
- `tests/unit/melder/aether/conduit/creations/test_creations_disposal_all_methods_regression.py:1-211`
- Reopen reverse-order regressions and relevant test architecture/components.

## Steps / Checklist
- [x] Remove redundant method-list copies in add_creation/add_many_creations.
- [x] Preserve the same established list through extraction and restoration of stored objects.
- [x] Keep has_disposal_methods gating, no-disposal paths, and existing many/singleton routing.
- [x] Preserve the invocation loop and current stop-on-first-method-failure behavior.
- [x] Preserve reversed registry and many-bucket traversal; do not promise a stronger total
      chronology across interleaved keys than the existing implementation provides.
- [x] Verify list lifetime against Spell/Creations teardown: do not clear a shared list while
      another owner may still need its names for real instance cleanup.
- [x] Test real bind/meld/cleanup in both priority modes; record results and remaining gaps.

## Deliverables
Direct list ownership in Creations, accurate contracts, and meaningful cleanup regressions.

## Files / Paths Impacted
- `src/melder/aether/conduit/creations/creations.py`
- `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py`
- Direct caller changes only if the explicit list contract cannot already be forwarded.
- `tests/unit/melder/aether/conduit/creations/test_creations.py`
- `tests/unit/melder/aether/conduit/creations/test_creations_disposal_all_methods_regression.py`
- `tests/unit/melder/aether/conduit/creations/test_creations_disposal_reverse_order_regression.py`
- `tests/component/melder/aether/conduit/test_conduit_component_creations.py`
- `tests/integration/melder/conduit/test_conduit_integration_disposal_ordering.py`

## Validation
- Passed: 73 disposal checks and 2,797 combined Spellbook/compiler/Creations/conduit checks.
- Runtime: Windows, .venv_new/Scripts/python.exe, Python 3.14.0 free-threaded, GIL disabled.
- Full repository suite, other platforms, configuration transport, crystal replay, and final assets: Not run.
- Methods record actual call order, with class definition order intentionally different.
- Cover singleton and many entries, reusable clear/pool cleanup, and extract/restore.
- Preserve failure handling: later methods on one failing object stop, other entries continue.
- Verify many objects without matched names remain on their current untracked path.
- Assertions about list identity are justified only by the explicit sharing requirement.

## Risks / Rollback Notes
The current Creations loop already invokes all names in stored sequence. Avoid rewriting it
to solve a producer-order problem. No new getattr/hasattr existence check is requested.

## Applicable Anti-Patterns
- [x] No duplicate configuration enforcement during disposal.
- [x] No new snapshots or defensive owned-field guards.

## Done Checklist
- [x] Real cleanup order and transfer metadata tests verified.
- [x] Source/contracts and notes updated; runtime prerequisite for replay is satisfied.
- [x] Owner accepts closure; no unrequested ticket cleanup.

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
- CONTEXT_TOPICS: instance cleanup, reference lifetime, extraction/restoration
- IF_UNKNOWN: none

## Noting Behavior
Capture real ownership and behavioral findings before continuing; separate existing from changed behavior.

## Notes
- DATETIME: 2026-09-04T21:17:27Z
  TYPE: PLAN
  CLAIM: Creations currently copies names at registration/transfer and invokes them sequentially.
  EVIDENCE:
  - `src/melder/aether/conduit/creations/creations.py:197-354`
  - `src/melder/aether/conduit/creations/creations.py:369-500`
  IMPACT: Change metadata ownership narrowly while retaining actual cleanup semantics.
  NEXT: Consume the runtime patch and read the full Creations implementation/callers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:58:36Z
  TYPE: FACT
  CLAIM: Full Creations and ConduitCreations reads confirm six method-list copy sites:
    singleton/many registration, singleton/many extraction, and singleton/many restoration.
    ConduitCreations delegates without another conversion. The existing-object Conduit
    caller already forwards Spell metadata. The invocation loop uses the stored sequence
    directly and stops only that object's chain on its first failure; the outer loop
    continues in reversed-key/reversed-bucket order and aggregates failures.
  EVIDENCE:
  - `src/melder/aether/conduit/creations/creations.py:197-357`
  - `src/melder/aether/conduit/creations/creations.py:369-500`
  - `src/melder/aether/conduit/creations/conduit_creations.py:95-133`
  - `src/melder/aether/conduit/conduit.py:1386-1428`
  - `src/melder/aether/spellbook/spell.py:500-603`
  IMPACT: Retain the established inner list through the six contacts; preserve registry
    detachment before cleanup, which is a real lifecycle operation, not a disposable-list
    snapshot to remove. Spell cleanup deletes its name reference without clearing the
    collection, so other holders can still use it. Do not introduce list.clear() there.
    Existing registration locks, scoped-store selection, cleanup failure behavior, and
    no-disposable fast paths remain unchanged.
  NEXT: At implementation, verify real cleanup and extract/restore behavior using the
    producer/compiler list contract, including clear_all and pool reuse.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:10:55Z
  TYPE: PLAN
  CLAIM: Begin Creations ownership after verified compiler propagation. Existing method-call
    order, fail-stop-per-object behavior, and reversed registry/bucket traversal stay intact.
  EVIDENCE:
  - `context_compass/tickets/tasks/completed/2026-09-04_ordered_disposal_compiler_propagation_task.md`
  IMPACT: This task is one storage-owner correction, not a disposal-loop redesign.
  NEXT: Read the complete Creations implementation and its existing tests/caller contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T10:15:32Z
  TYPE: FACT
  CLAIM: Full Creations (614 lines) and ConduitCreations (133) rereads confirm six copies
    and no required caller changes. Existing-object Conduit registration passes names directly.
    Invocation, reverse traversal, cleanup/clear/pool, and exception behavior are unchanged targets.
    Existing method-order/failure/reverse unit tests and real disposal-order integration tests
    were read. Creations component/control-flow contracts now capture this one-file correction.
  EVIDENCE:
  - `src/melder/aether/conduit/creations/creations.py:148-614`
  - `src/melder/aether/conduit/creations/conduit_creations.py:95-133`
  - `src/melder/aether/conduit/conduit.py:1386-1428`
  - `tests/unit/melder/aether/conduit/creations/test_creations_disposal_all_methods_regression.py:1-211`
  - `tests/integration/melder/conduit/test_conduit_integration_disposal_ordering.py:1-342`
  IMPACT: Change references only. Preserve optional metadata fallback and supplied empty-list identity.
  NEXT: Index/consume the contracts, run baseline, and add direct ownership/runtime regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:19:26Z
  TYPE: PLAN
  CLAIM: Creations contracts are indexed, linked, and consumed. Mapping: registration ->
    singleton/many and empty-list identity; extraction/restoration -> identity plus actual
    calls after transfer; unchanged teardown -> existing failure/reverse regressions and
    reusable clear/pool checks; compiler-to-store -> real three-family, two-priority runtime cases.
    Baseline passes 47 existing tests in 0.29s before storage source edits.
  EVIDENCE:
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/component_patch_creations_disposal.md:7-38`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/code_description_patch_creations_disposal.md:7-27`
  - Command: .venv_new/Scripts/python.exe -m pytest tests/unit/melder/aether/conduit/creations tests/component/melder/aether/conduit/test_conduit_component_creations.py tests/integration/melder/conduit/test_conduit_integration_disposal_ordering.py -q -p no:cacheprovider --tb=short
  IMPACT: Entry gate is satisfied. New tests may inspect list identity because sharing is an
    explicit ownership contract, but must also verify observable disposal behavior.
  NEXT: Add and run the targeted reference and real-runtime regressions, then remove six copies.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:22:17Z
  TYPE: MEASURE
  CLAIM: New ownership/runtime regressions reproduce the six-copy defect: 22 failed,
    4 passed in 0.24s. All failures are list-reference mismatches, including every real
    solo/generalized/many-only graph under both priorities and actual override values.
    Disabled and omitted-metadata cases already pass. No runtime setup conflict remains.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe -m pytest tests/unit/melder/aether/conduit/creations/test_creations_disposal_references.py tests/integration/melder/conduit/test_ordered_disposal_runtime.py -q -p no:cacheprovider --tb=line
  - `tests/unit/melder/aether/conduit/creations/test_creations_disposal_references.py`
  - `tests/integration/melder/conduit/test_ordered_disposal_runtime.py`
  IMPACT: Real runtime family selection and value order are correct before the storage edit;
    Creations still detaches the list reference. The planned six substitutions address it.
  NEXT: Replace six inner-list copies and run new plus existing disposal regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:22:17Z
  TYPE: FACT
  CLAIM: Applied six reference substitutions in creations.py and documented ownership at
    registration and transfer boundaries. The invocation loop, detach operation, exception
    handling, locks, pooling, and scope routing are unchanged.
  EVIDENCE:
  - `src/melder/aether/conduit/creations/creations.py`
  IMPACT: The existing established list now survives this last runtime storage boundary.
  NEXT: Run the 26 new cases and 47 existing disposal checks together.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T10:22:17Z
  TYPE: MEASURE
  CLAIM: Storage verification now passes 71 of 73 tests. Only real generalized/no-overrides
    runtime cases still detach names; solo, many-only, overrides, transfer, pool reuse, and
    prior cleanup regressions pass. The remaining producer of a copied list is UNKNOWN
    until the actual generalized registration call path is traced.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe -m pytest tests/unit/melder/aether/conduit/creations tests/component/melder/aether/conduit/test_conduit_component_creations.py tests/integration/melder/conduit/test_conduit_integration_disposal_ordering.py tests/integration/melder/conduit/test_ordered_disposal_runtime.py -q -p no:cacheprovider --tb=short
  - Result: 2 failed, 71 passed in 0.49s.
  IMPACT: Do not weaken the reference assertion. This real runtime test exposes a compiler
    registration path not covered by the focused namespace probes.
  NEXT: Trace that generalized registration caller and update the compiler contract if needed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:26:15Z
  TYPE: FACT
  CLAIM: The remaining copies are in generated source, not Creations: generalized manifest
    _append_register_source emits list(disposal_methods_N) for both singleton and many entries.
    This bypasses the store methods. The complete 1,500-line emitter is now read. Both generic
    and warm-tail-specialized executors share this helper, so two substitutions cover both.
  EVIDENCE:
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:641-722`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:1330-1342`
  IMPACT: Earlier field-name inventory missed emitted variable names. The direct-caller clause
    covers this repair; compiler/Creations contracts now include it. No lock or loop redesign.
  NEXT: Consume updated contracts, remove two emitted copies, and verify cold/warm real calls.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:26:15Z
  TYPE: FACT
  CLAIM: Updated compiler/Creations contracts were consumed. Removed the two emitted list
    copies from generalized manifest registration; no surrounding emitted control flow changed.
    Real runtime cases now perform two melds each, covering repeated/specialized execution
    and checking every returned instance's stored metadata and actual cleanup sequence.
  EVIDENCE:
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:641-724`
  - `tests/integration/melder/conduit/test_ordered_disposal_runtime.py`
  IMPACT: The scoped caller repair covers both singleton and many inline entries.
  NEXT: Rerun disposal checks, then the combined compiler/runtime regression boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T10:29:44Z
  TYPE: MEASURE
  CLAIM: All 73 storage/runtime checks pass in 0.46s after the inline caller correction.
    This includes 26 new reference/runtime cases and 47 prior disposal checks. Real graphs
    select all three compiler families and execute repeated melds with both priorities and
    actual override values; every stored list retains Spell identity and disposal runs in order.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe -m pytest tests/unit/melder/aether/conduit/creations tests/component/melder/aether/conduit/test_conduit_component_creations.py tests/integration/melder/conduit/test_conduit_integration_disposal_ordering.py tests/integration/melder/conduit/test_ordered_disposal_runtime.py -q -p no:cacheprovider --tb=short
  - Result: 73 passed in 0.46s, exit 0.
  IMPACT: Runtime ownership correction is green; failure and reverse-order regressions remain intact.
  NEXT: Run the combined Spellbook/compiler/Creations and conduit integration boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:33:58Z
  TYPE: MEASURE
  CLAIM: Final combined verification passes 2,797 tests in 8.80s. Interpreter is Python 3.14.0
    free-threaded with GIL disabled. All five current compiler/Creations patch indexes pass.
    Creations and inline-emitter changes preserve registry detachment, invocation, exceptions,
    locks, pooling, and reverse traversal. Source/test diffs and affected contracts were reviewed.
    Separate commits landed during the work; this agent issued no commit or push commands.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe -m pytest tests/unit/melder/spellbook tests/component/melder/spellbook tests/unit/melder/aether/conduit/creations tests/component/melder/aether/conduit/test_conduit_component_creations.py tests/integration/melder/conduit -q -p no:cacheprovider --tb=short
  - Result: 2797 passed in 8.80s, exit 0.
  - `src/melder/aether/conduit/creations/creations.py:269-511`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:641-724`
  IMPACT: Compiler/Creations phase is implemented/in review with 51 new cases across three
    new test modules. Full persistence/replay, canonical promotion, and assets remain pending.
  NEXT: Verify disposal configuration round trips, then implement crystal capture/restore/graft order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T14:22:02Z
  TYPE: DECISION
  CLAIM: Owner accepted this deliverable and requested closure of the ordered-disposal program.
    Preserved disposal order and list lifetime through registration, transfer, and actual cleanup.
  EVIDENCE: tickets/tasks/completed/2026-09-04_ordered_disposal_end_to_end_validation_task.md
  IMPACT: Ticket history is retained under completed. Registered temporary artifacts are disposed
    at accepted closure; durable behavior is in canonical docs, examples, source, and regression tests.
    Linux/hosted checks and unrelated recording/name-lookup findings retain their documented scope.
  NEXT: none; this work item is closed.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
CLOSED: 2026-09-05T14:22:02Z. Preserved disposal order and list lifetime through registration, transfer, and actual cleanup.
Program record: tickets/epics/completed/2026-09-02_ordered_live_spell_disposal_epic.md
No active work remains in this ticket. Prior handoff text below is historical.

### Historical handoff at closure
Implemented/in review: Creations retains the established list at six registration/transfer contacts.
Real runtime tests found and fixed two additional copies in generalized manifest inline source.
That complete emitter was read before editing; surrounding emitted algorithms/locks are unchanged.
Twenty-six new storage/runtime cases verify reference lifetime, transfer, empty/disabled paths,
pool reuse, three real compiler families, both priorities, actual overrides, and repeated melds.
The complete phase adds 51 cases including the compiler tests. Combined verification: 2,797 pass.
Separate commits landed on codex_features2 during work; this agent did not commit or push.
Next prerequisite: disposal_configuration_roundtrip; then ordered_disposal_crystal_replay.
Final documentation/graph promotion and source/repo asset regeneration remain pending.
